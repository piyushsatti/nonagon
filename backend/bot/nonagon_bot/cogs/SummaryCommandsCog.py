from __future__ import annotations

import re
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

import discord
from discord import app_commands
from discord.ext import commands

from nonagon_bot.services import guild_settings_store
from nonagon_bot.utils.logging import get_logger
from nonagon_bot.core.domain.models.EntityIDModel import (
    CharacterID,
    QuestID,
    SummaryID,
    UserID,
)
from nonagon_bot.core.domain.models.SummaryModel import (
    QuestSummary,
    SummaryKind,
    SummaryStatus,
)
from nonagon_bot.core.domain.models.UserModel import User
from nonagon_bot.core.infra.postgres.users_repo import UsersRepoPostgres
from nonagon_bot.core.infra.postgres.summaries_repo import SummariesRepoPostgres
from nonagon_bot.core.infra.postgres.characters_repo import CharactersRepoPostgres
from nonagon_bot.core.infra.postgres.guild_adapter import upsert_summary_sync


logger = get_logger(__name__)


class SummaryCommandsCog(commands.Cog):
    """Slash commands for creating and updating quest summaries via DM."""

    summary = app_commands.Group(
        name="summary", description="Share quest summaries and open discussion threads."
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._users_repo = UsersRepoPostgres()
        self._summaries_repo = SummariesRepoPostgres()
        self._characters_repo = CharactersRepoPostgres()
        self._active_summary_sessions: Set[int] = set()
        self._demo_log = logger.audit

    # ---------- Core helpers ----------

    async def _lookup_user_display(
        self, guild_id: int, user_id: Optional[UserID]
    ) -> str:
        """Look up user display name from database."""
        if user_id is None:
            return "Unknown"
        try:
            user = await self._users_repo.get(guild_id, str(user_id))
            if user and user.discord_id:
                return f"<@{user.discord_id}>"
        except Exception:
            pass
        return str(user_id)

    async def _get_cached_user(self, member: discord.Member) -> User:
        """Get user from database via UserRegistry."""
        from nonagon_bot.services.user_registry import UserRegistry

        registry = UserRegistry()
        user = await registry.ensure_member(member, member.guild.id)
        user.guild_id = member.guild.id
        return user

    def _parse_entity_id(self, cls, payload: object) -> Optional[object]:
        if payload is None:
            return None
        if isinstance(payload, cls):
            return payload
        if isinstance(payload, dict):
            value = payload.get("value")
            if isinstance(value, str) and value:
                return cls.parse(value)
            number = payload.get("number")
            if number is not None:
                prefix = payload.get("prefix", cls.prefix)
                return cls.parse(f"{prefix}{number}")
        if isinstance(payload, str) and payload:
            return cls.parse(payload)
        if isinstance(payload, int):
            return cls.parse(f"{cls.prefix}{payload}")
        return None

    def _persist_summary(self, guild_id: int, summary: QuestSummary) -> None:
        """Persist a summary using the sync adapter."""
        summary.guild_id = guild_id
        upsert_summary_sync(guild_id, summary)

    async def _fetch_summary(
        self, guild_id: int, summary_id: SummaryID
    ) -> Optional[QuestSummary]:
        """Fetch a summary from the PostgreSQL database."""
        return await self._summaries_repo.get(guild_id, str(summary_id))

    async def _next_summary_id(self, guild_id: int) -> SummaryID:
        """Generate a new unique SummaryID using the PostgreSQL repo."""
        summary_id_str = await self._summaries_repo.next_id(guild_id)
        parsed_id: SummaryID = SummaryID.parse(summary_id_str)  # type: ignore[assignment]
        return parsed_id

    def _build_summary_embed(
        self,
        summary: QuestSummary,
        guild: discord.Guild,
        *,
        updated_at: Optional[datetime] = None,
    ) -> discord.Embed:
        title = summary.title or f"Summary {summary.summary_id}"
        description = summary.description or "Summary details to follow in the thread."
        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Colour.teal(),
            timestamp=updated_at or datetime.now(timezone.utc),
        )

        author_display = self._lookup_user_display(guild.id, summary.author_id)
        embed.add_field(name="Author", value=author_display, inline=False)

        if summary.characters:
            char_lines = [f"`{str(char_id)}`" for char_id in summary.characters]
            embed.add_field(
                name="Characters",
                value="\n".join(char_lines),
                inline=False,
            )

        if summary.linked_quests:
            quest_lines = [f"`{str(quest_id)}`" for quest_id in summary.linked_quests]
            embed.add_field(
                name="Linked Quests",
                value="\n".join(quest_lines),
                inline=False,
            )

        status_label = summary.status.value.title()
        embed.set_footer(
            text=f"Summary ID: {summary.summary_id} • Status: {status_label}"
        )
        return embed

    async def _sync_summary_announcement(
        self,
        guild: discord.Guild,
        summary: QuestSummary,
        *,
        updated_at: Optional[datetime] = None,
    ) -> None:
        if not summary.channel_id or not summary.message_id:
            return

        channel = guild.get_channel(int(summary.channel_id))
        if channel is None:
            try:
                channel = await guild.fetch_channel(int(summary.channel_id))
            except Exception as exc:  # pragma: no cover - defensive
                logger.debug(
                    "Unable to resolve summary channel %s in guild %s: %s",
                    summary.channel_id,
                    guild.id,
                    exc,
                )
                return

        if not isinstance(channel, discord.TextChannel):
            logger.debug(
                "Summary channel %s in guild %s is not a text channel",
                summary.channel_id,
                guild.id,
            )
            return

        try:
            message = await channel.fetch_message(int(summary.message_id))
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug(
                "Unable to fetch summary message %s in guild %s: %s",
                summary.message_id,
                guild.id,
                exc,
            )
            return

        embed = self._build_summary_embed(summary, guild, updated_at=updated_at)

        try:
            await message.edit(embed=embed)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug(
                "Unable to update summary announcement %s in guild %s: %s",
                summary.summary_id,
                guild.id,
                exc,
            )

    async def _post_summary_announcement(
        self,
        interaction: discord.Interaction,
        summary: QuestSummary,
    ) -> tuple[discord.Message, Optional[discord.Thread]]:
        assert interaction.guild is not None, "Guild must not be None"
        settings = guild_settings_store.fetch_settings(interaction.guild.id) or {}
        channel_id = settings.get("summary_channel_id")
        if channel_id is None:
            raise ValueError(
                "No summary channel configured. Run `/setup summary` before posting summaries."
            )

        channel: Optional[discord.TextChannel] = None
        try:
            fetched = interaction.guild.get_channel(int(channel_id))  # type: ignore[arg-type]
            if isinstance(fetched, discord.TextChannel):
                channel = fetched
        except (TypeError, ValueError):
            channel = None
        if channel is None:
            try:
                fetched = await interaction.guild.fetch_channel(int(channel_id))
                if isinstance(fetched, discord.TextChannel):
                    channel = fetched
            except Exception:
                channel = None
        if channel is None or not isinstance(channel, discord.TextChannel):
            raise ValueError("The configured summary channel is not accessible.")

        me = interaction.guild.me
        if me is None:
            raise ValueError("Unable to resolve bot member for permission checks.")
        perms = channel.permissions_for(me)
        if not perms.send_messages:
            raise ValueError(
                f"I need Send Messages permission in {channel.mention} to share summaries."
            )
        if not perms.create_public_threads and not perms.create_private_threads:
            raise ValueError(
                f"I need permission to create threads in {channel.mention} to open summary discussions."
            )

        embed = self._build_summary_embed(summary, interaction.guild)
        message = await channel.send(embed=embed)

        thread: Optional[discord.Thread] = None
        thread_name = f"Summary: {summary.title or summary.summary_id}"[:90]
        try:
            thread = await message.create_thread(
                name=thread_name,
                auto_archive_duration=1440,
            )
            await thread.send(
                "Thanks for sharing your summary! Post the full write-up, images, or links in this thread."
            )
        except Exception:
            thread = None

        return message, thread

    def _parse_character_ids(
        self,
        raw: str,
        allowed: Dict[str, CharacterID],
    ) -> List[CharacterID]:
        tokens = [
            token.strip().upper()
            for token in re.split(r"[,\s]+", raw.strip())
            if token.strip()
        ]
        if not tokens:
            return []

        characters: List[CharacterID] = []
        for token in tokens:
            if token not in allowed:
                raise ValueError(f"{token} is not one of your characters.")
            characters.append(allowed[token])
        return characters

    def _parse_quest_ids(self, raw: str) -> List[QuestID]:
        tokens = [
            token.strip().upper()
            for token in re.split(r"[,\s]+", raw.strip())
            if token.strip()
        ]
        quests: List[QuestID] = []
        for token in tokens:
            try:
                quest_id: QuestID = QuestID.parse(token)  # type: ignore[assignment]
                quests.append(quest_id)
            except ValueError:
                raise ValueError(f"Unable to parse quest ID `{token}`.")
        return quests

    async def _list_owned_characters(
        self, guild: discord.Guild, member: discord.Member
    ) -> Dict[str, CharacterID]:
        """Get all characters owned by a member as a dict mapping ID string to CharacterID."""
        owner_id: UserID = UserID.from_body(str(member.id))  # type: ignore[assignment]
        characters = await self._characters_repo.list_by_owner(guild.id, owner_id)
        owned: Dict[str, CharacterID] = {}
        for char in characters:
            char_id = char.character_id
            if isinstance(char_id, CharacterID):
                owned[str(char_id)] = char_id
            elif isinstance(char_id, str):
                try:
                    parsed: CharacterID = CharacterID.parse(char_id)  # type: ignore[assignment]
                    owned[str(parsed)] = parsed
                except ValueError:
                    pass
        return owned

    # ---------- Commands ----------

    @summary.command(
        name="create", description="Guide a DM flow to publish a quest summary."
    )
    @app_commands.guild_only()
    async def summary_create(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used inside a guild.", ephemeral=True
            )
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "Only guild members can create summaries.", ephemeral=True
            )
            return

        if member.id in self._active_summary_sessions:
            await interaction.response.send_message(
                "You already have an active summary session. Complete or cancel it before starting a new one.",
                ephemeral=True,
            )
            return

        try:
            user = await self._get_cached_user(member)
        except RuntimeError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        owned_characters = await self._list_owned_characters(interaction.guild, member)
        if not owned_characters:
            await interaction.response.send_message(
                "You need at least one character before sharing a summary. Use `/character create` first.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        self._active_summary_sessions.add(member.id)
        try:
            try:
                dm_channel = await member.create_dm()
            except discord.Forbidden:
                await interaction.followup.send(
                    "I can't send you direct messages. Enable DMs from server members and run `/summary create` again.",
                    ephemeral=True,
                )
                return

            session = SummaryCreationSession(
                self,
                interaction.guild,
                member,
                user,
                dm_channel,
                owned_characters,
            )
            try:
                result = await session.run()
            except RuntimeError as exc:
                await interaction.followup.send(str(exc), ephemeral=True)
                return

            if not result.success or result.summary is None:
                await interaction.followup.send(
                    result.error or "Summary creation cancelled.",
                    ephemeral=True,
                )
                return

            summary = result.summary
            summary.guild_id = interaction.guild.id
            summary.author_id = user.user_id
            summary.players = [user.user_id]
            summary.kind = SummaryKind.PLAYER
            summary.created_on = datetime.now(timezone.utc)
            summary.status = SummaryStatus.POSTED
            summary.validate_summary()

            try:
                message, thread = await self._post_summary_announcement(
                    interaction, summary
                )
            except ValueError as exc:
                await interaction.followup.send(str(exc), ephemeral=True)
                return
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Summary announce failed: %s", exc)
                await interaction.followup.send(
                    "Unable to post the summary right now. Please try again shortly.",
                    ephemeral=True,
                )
                return

            summary.channel_id = str(message.channel.id)
            summary.message_id = str(message.id)
            summary.thread_id = str(thread.id) if thread else None

            self._persist_summary(interaction.guild.id, summary)

            thread_notice = (
                f"[discussion thread]({thread.jump_url})"
                if thread
                else "discussion thread"
            )

            # Use message.channel which is guaranteed to be TextChannel from _post_summary_announcement
            channel_mention = (
                message.channel.mention
                if isinstance(message.channel, discord.TextChannel)
                else str(message.channel)
            )

            await interaction.followup.send(
                f"Summary `{summary.summary_id}` posted in {channel_mention}. "
                f"Continue the story in the {thread_notice}.",
                ephemeral=True,
            )

            try:
                await self._demo_log(
                    self.bot,
                    interaction.guild,
                    f"{member.mention} published summary `{summary.summary_id}`",
                )
            except Exception:
                pass
        finally:
            self._active_summary_sessions.discard(member.id)

    @summary.command(name="edit", description="Update an existing summary via DM.")
    @app_commands.describe(summary="Summary ID (e.g. SUMMA1B2C3)")
    @app_commands.guild_only()
    async def summary_edit(
        self, interaction: discord.Interaction, summary: str
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used inside a guild.", ephemeral=True
            )
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "Only guild members can edit summaries.", ephemeral=True
            )
            return

        try:
            summary_id: SummaryID = SummaryID.parse(summary.upper())  # type: ignore[assignment]
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        existing = await self._fetch_summary(interaction.guild.id, summary_id)
        if existing is None:
            await interaction.response.send_message(
                "Summary not found.", ephemeral=True
            )
            return

        try:
            user = await self._get_cached_user(member)
        except RuntimeError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        if existing.author_id != user.user_id:
            await interaction.response.send_message(
                "Only the summary author can edit it.", ephemeral=True
            )
            return

        if member.id in self._active_summary_sessions:
            await interaction.response.send_message(
                "You already have an active summary session. Complete or cancel it before starting a new one.",
                ephemeral=True,
            )
            return

        owned_characters = await self._list_owned_characters(interaction.guild, member)
        if not owned_characters:
            await interaction.response.send_message(
                "You need at least one character before editing summaries.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        self._active_summary_sessions.add(member.id)
        try:
            try:
                dm_channel = await member.create_dm()
            except discord.Forbidden:
                await interaction.followup.send(
                    "I can't send you direct messages. Enable DMs from server members and run `/summary edit` again.",
                    ephemeral=True,
                )
                return

            session = SummaryUpdateSession(
                self,
                interaction.guild,
                member,
                user,
                dm_channel,
                existing,
                owned_characters,
            )
            try:
                result = await session.run()
            except RuntimeError as exc:
                await interaction.followup.send(str(exc), ephemeral=True)
                return

            if not result.success or result.summary is None:
                await interaction.followup.send(
                    result.error or "Summary update cancelled.",
                    ephemeral=True,
                )
                return

            result.summary.last_edited_at = datetime.now(timezone.utc)
            result.summary.validate_summary()
            self._persist_summary(interaction.guild.id, result.summary)

            if result.summary.channel_id and result.summary.message_id:
                await self._sync_summary_announcement(
                    interaction.guild,
                    result.summary,
                    updated_at=result.summary.last_edited_at,
                )

            await interaction.followup.send(
                f"Summary `{result.summary.summary_id}` updated.",
                ephemeral=True,
            )
        finally:
            self._active_summary_sessions.discard(member.id)


# ---------- DM session helpers ----------


@dataclass
class SummaryCreationResult:
    success: bool
    summary: Optional[QuestSummary] = None
    error: Optional[str] = None


@dataclass
class SummaryUpdateResult:
    success: bool
    summary: Optional[QuestSummary] = None
    error: Optional[str] = None


class SummarySessionBase:
    def __init__(
        self,
        cog: "SummaryCommandsCog",
        guild: discord.Guild,
        member: discord.Member,
        user: User,
        dm_channel: discord.DMChannel,
        owned_characters: Dict[str, CharacterID],
    ) -> None:
        self.cog = cog
        self.guild = guild
        self.member = member
        self.user = user
        self.dm = dm_channel
        self.owned_characters = owned_characters
        self.timeout = 300
        self._preview_message: Optional[discord.Message] = None

    async def _safe_send(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[discord.Embed] = None,
    ) -> discord.Message:
        try:
            if content is not None and embed is not None:
                return await self.dm.send(content=content, embed=embed)
            elif embed is not None:
                return await self.dm.send(embed=embed)
            elif content is not None:
                return await self.dm.send(content=content)
            else:
                return await self.dm.send(content="")
        except discord.Forbidden as exc:
            raise RuntimeError(
                "I can't send you direct messages anymore. Enable DMs and run the command again."
            ) from exc
        except discord.HTTPException as exc:
            raise RuntimeError(f"Failed to send DM: {exc}") from exc

    async def _ask(
        self,
        prompt: str,
        *,
        required: bool,
        allow_skip: bool = False,
        allow_clear: bool = False,
    ) -> Optional[str]:
        instructions = ["Type `cancel` to stop."]
        if allow_skip:
            instructions.append("Type `skip` to keep the current value.")
        if allow_clear:
            instructions.append("Type `clear` to remove this value.")
        await self._safe_send(f"{prompt}\n" + " ".join(instructions))

        while True:
            try:
                message = await self.cog.bot.wait_for(
                    "message",
                    timeout=self.timeout,
                    check=lambda m: m.author.id == self.member.id
                    and m.channel.id == self.dm.id,
                )
            except asyncio.TimeoutError as exc:
                raise TimeoutError from exc

            content = message.content.strip()
            lower = content.lower()
            if lower == "cancel":
                raise RuntimeError("cancelled")
            if allow_clear and lower == "clear":
                return ""
            if allow_skip and lower == "skip":
                return None
            if not content:
                if required:
                    await self._safe_send(
                        "Please provide a response, or type `cancel`."
                    )
                    continue
                return None
            return content

    def _build_preview_embed(self, summary: QuestSummary) -> discord.Embed:
        return self.cog._build_summary_embed(summary, self.guild)

    async def _update_preview(self, summary: QuestSummary) -> None:
        embed = self._build_preview_embed(summary)
        if self._preview_message is None:
            self._preview_message = await self._safe_send(
                "**Current summary preview:**", embed=embed
            )
            return
        try:
            await self._preview_message.edit(embed=embed)
        except discord.HTTPException:
            self._preview_message = await self._safe_send(
                "**Current summary preview:**", embed=embed
            )

    def _format_owned_characters(self) -> str:
        return ", ".join(f"`{cid}`" for cid in self.owned_characters.keys())


class SummaryCreationSession(SummarySessionBase):
    async def run(self) -> SummaryCreationResult:
        summary_id = await self.cog._next_summary_id(self.guild.id)
        summary = QuestSummary(
            summary_id=summary_id,
            guild_id=self.guild.id,
            author_id=self.user.user_id,
            title=None,
            description=None,
            raw=None,
        )

        try:
            await self._safe_send(
                f"Let's share a quest summary! We'll post it automatically once the setup finishes.\n"
                f"Owned characters: {self._format_owned_characters()}"
            )

            title = await self._ask(
                "**Step 1:** What's the summary title?", required=True
            )
            if title:
                summary.title = title.strip()
            await self._update_preview(summary)

            quests_input = await self._ask(
                "**Step 2:** List quest IDs involved (comma or space separated), or `skip`.",
                required=False,
                allow_skip=True,
            )
            if quests_input:
                try:
                    summary.linked_quests = self.cog._parse_quest_ids(quests_input)
                except ValueError as exc:
                    return SummaryCreationResult(False, error=str(exc))
            await self._update_preview(summary)

            characters_input = await self._ask(
                "**Step 3:** Which of your characters were involved? Provide IDs separated by commas or spaces.",
                required=True,
            )
            if not characters_input:
                return SummaryCreationResult(
                    False, error="Character selection is required."
                )
            try:
                summary.characters = self.cog._parse_character_ids(
                    characters_input,
                    self.owned_characters,
                )
            except ValueError as exc:
                return SummaryCreationResult(False, error=str(exc))
            if summary.characters:
                summary.character_id = summary.characters[0]
            await self._update_preview(summary)

            tldr_input = await self._ask(
                "**Step 4:** Share a quick TL;DR for the announcement (or `skip`).",
                required=False,
                allow_skip=True,
            )
            if tldr_input is not None:
                summary.description = tldr_input.strip() or None
            await self._update_preview(summary)
        except TimeoutError:
            return SummaryCreationResult(
                False,
                error="Timed out waiting for a response. Run `/summary create` again when you're ready.",
            )
        except RuntimeError as exc:
            return SummaryCreationResult(False, error=str(exc))

        summary.description = summary.description or "Story continues in the thread."
        summary.raw = summary.description
        return SummaryCreationResult(True, summary=summary)


class SummaryUpdateSession(SummarySessionBase):
    def __init__(
        self,
        cog: "SummaryCommandsCog",
        guild: discord.Guild,
        member: discord.Member,
        user: User,
        dm_channel: discord.DMChannel,
        summary: QuestSummary,
        owned_characters: Dict[str, CharacterID],
    ) -> None:
        super().__init__(cog, guild, member, user, dm_channel, owned_characters)
        self.summary = summary

    async def run(self) -> SummaryUpdateResult:
        try:
            await self._safe_send(
                "Let's update your summary. Respond with new values or `skip` to keep existing."
            )
            await self._update_preview(self.summary)

            title = await self._ask(
                "**Step 1:** Update the title (or `skip`, `clear`).",
                required=False,
                allow_skip=True,
                allow_clear=True,
            )
            if title not in (None, ""):
                self.summary.title = title.strip()
            elif title == "":
                self.summary.title = None
            await self._update_preview(self.summary)

            quests_input = await self._ask(
                "**Step 2:** Update linked quests (comma/space separated, `skip`, `clear`).",
                required=False,
                allow_skip=True,
                allow_clear=True,
            )
            if quests_input is not None:
                if quests_input == "":
                    self.summary.linked_quests = []
                else:
                    try:
                        self.summary.linked_quests = self.cog._parse_quest_ids(
                            quests_input
                        )
                    except ValueError as exc:
                        return SummaryUpdateResult(False, error=str(exc))
            await self._update_preview(self.summary)

            characters_input = await self._ask(
                "**Step 3:** Update characters (comma/space separated, `skip`, `clear`).",
                required=False,
                allow_skip=True,
                allow_clear=True,
            )
            if characters_input is not None:
                if characters_input == "":
                    self.summary.characters = []
                else:
                    try:
                        characters = self.cog._parse_character_ids(
                            characters_input,
                            self.owned_characters,
                        )
                    except ValueError as exc:
                        return SummaryUpdateResult(False, error=str(exc))
                    self.summary.characters = characters
                    self.summary.character_id = characters[0] if characters else None
            await self._update_preview(self.summary)

            tldr_input = await self._ask(
                "**Step 4:** Update TL;DR (`skip`, `clear`).",
                required=False,
                allow_skip=True,
                allow_clear=True,
            )
            if tldr_input is not None:
                if tldr_input == "":
                    self.summary.description = None
                else:
                    self.summary.description = tldr_input.strip()
            await self._update_preview(self.summary)
        except TimeoutError:
            return SummaryUpdateResult(
                False,
                error="Timed out waiting for a response. Run `/summary edit` again when you're ready.",
            )
        except RuntimeError as exc:
            return SummaryUpdateResult(False, error=str(exc))

        self.summary.description = (
            self.summary.description or "Story continues in the thread."
        )
        self.summary.raw = self.summary.description
        return SummaryUpdateResult(True, summary=self.summary)


async def setup(bot: commands.Bot):
    await bot.add_cog(SummaryCommandsCog(bot))
