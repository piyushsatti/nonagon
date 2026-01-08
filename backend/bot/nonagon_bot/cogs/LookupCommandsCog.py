from __future__ import annotations

import asyncio
import contextlib
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from nonagon_bot.cogs._staff_utils import is_allowed_staff
from nonagon_bot.services import graphql_client
from nonagon_bot.utils.logging import get_logger


logger = get_logger(__name__)


class LookupCommandsCog(commands.Cog):
    """Slash commands for managing quick reference lookups."""

    lookup = app_commands.Group(name="lookup", description="Manage lookup references")

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._sync_task: Optional[asyncio.Task[None]] = None

    async def cog_load(self) -> None:
        self._sync_task = self.bot.loop.create_task(self._sync_lookup_commands())

    async def cog_unload(self) -> None:
        if self._sync_task is not None:
            self._sync_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._sync_task
            self._sync_task = None
        for guild in list(self.bot.guilds):
            target = self._guild_object(guild.id)
            self.bot.tree.remove_command(self.lookup.name, type=self.lookup.type, guild=target)
            try:
                await self.bot.tree.sync(guild=target)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Failed to sync lookup removal for guild %s", guild.id)

    async def _sync_lookup_commands(self) -> None:
        await self.bot.wait_until_ready()
        for guild in list(self.bot.guilds):
            await self._register_for_guild(guild.id)

    async def _register_for_guild(self, guild_id: int) -> None:
        target = self._guild_object(guild_id)
        try:
            self.bot.tree.add_command(self.lookup, guild=target, override=True)
            await self.bot.tree.sync(guild=target)
        except Exception:
            logger.exception("Failed to sync lookup commands for guild %s", guild_id)

    @staticmethod
    def _guild_object(guild_id: int) -> discord.Object:
        return discord.Object(id=guild_id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self._register_for_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        target = self._guild_object(guild.id)
        self.bot.tree.remove_command(self.lookup.name, type=self.lookup.type, guild=target)

    async def _fetch_user(self, guild_id: int, discord_id: int) -> Optional[Dict[str, Any]]:
        return await graphql_client.get_user_by_discord(guild_id, str(discord_id))

    async def _is_staff(self, member: discord.Member) -> bool:
        if is_allowed_staff(self.bot, member):
            return True

        try:
            user = await self._fetch_user(member.guild.id, member.id)
        except Exception:
            return False
        if not user:
            return False
        return "REFEREE" in (user.get("roles") or [])

    async def _resolve_staff_member(self, interaction: discord.Interaction) -> Optional[discord.Member]:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used inside a guild.", ephemeral=True
            )
            return None

        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "Only guild members can run lookup commands.", ephemeral=True
            )
            return None

        if not await self._is_staff(member):
            await interaction.response.send_message(
                "You need staff permissions (REFEREE or Manage Server) to use lookup commands.",
                ephemeral=True,
            )
            return None

        return member

    @lookup.command(name="add", description="Add or update a lookup entry")
    @app_commands.describe(name="Friendly identifier", url="Destination URL", description="Optional note shown in listings")
    async def lookup_add(
        self,
        interaction: discord.Interaction,
        name: str,
        url: str,
        description: Optional[str] = None,
    ) -> None:
        member = await self._resolve_staff_member(interaction)
        if member is None:
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        guild_id = interaction.guild.id  # type: ignore[union-attr]
        existing = await graphql_client.get_lookup(guild_id, name)

        saved: Optional[Dict[str, Any]]
        if existing:
            saved = await graphql_client.update_lookup(
                guild_id,
                name,
                updated_by=member.id,
                url=url.strip(),
                description=description.strip() if description else None,
            )
            action = "Updated"
        else:
            saved = await graphql_client.create_lookup(
                guild_id,
                created_by=member.id,
                name=name.strip(),
                url=url.strip(),
                description=description.strip() if description else None,
            )
            action = "Stored"

        if saved is None:
            await interaction.followup.send(
                "API request failed while saving the lookup. Please try again later.",
                ephemeral=True,
            )
            return

        logger.info(
            "Lookup entry saved (guild=%s staff=%s name=%s)",
            guild_id,
            member.id,
            saved.get("name"),
        )
        await interaction.followup.send(
            f"{action} lookup `{saved.get('name')}` → {saved.get('url')}", ephemeral=True
        )

    @lookup.command(name="get", description="Retrieve a lookup entry")
    @app_commands.describe(query="Name to search for")
    async def lookup_get(self, interaction: discord.Interaction, query: str) -> None:
        member = await self._resolve_staff_member(interaction)
        if member is None:
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        match = await graphql_client.lookup_search(interaction.guild.id, query)  # type: ignore[union-attr]
        if match is None:
            await interaction.followup.send("No lookup entry matched that query.", ephemeral=True)
            return

        embed = _build_lookup_embed(match)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @lookup.command(name="list", description="List lookup entries")
    async def lookup_list(self, interaction: discord.Interaction) -> None:
        member = await self._resolve_staff_member(interaction)
        if member is None:
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        entries = await graphql_client.list_all_lookups(interaction.guild.id)  # type: ignore[union-attr]

        if not entries:
            await interaction.followup.send("No lookup entries stored yet.", ephemeral=True)
            return

        view = LookupListView(entries, interaction.guild.name)  # type: ignore[union-attr]
        embed = view.render_embed()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @lookup.command(name="remove", description="Remove a lookup entry")
    @app_commands.describe(name="Name to delete")
    async def lookup_remove(self, interaction: discord.Interaction, name: str) -> None:
        member = await self._resolve_staff_member(interaction)
        if member is None:
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        deleted = await graphql_client.delete_lookup(interaction.guild.id, name)  # type: ignore[union-attr]

        if deleted:
            logger.info(
                "Lookup entry removed (guild=%s staff=%s name=%s)",
                interaction.guild.id,
                member.id,
                name,
            )
            await interaction.followup.send(f"Removed lookup `{name}`.", ephemeral=True)
        else:
            await interaction.followup.send(f"No lookup named `{name}` found.", ephemeral=True)


def _build_lookup_embed(entry: Dict[str, Any]) -> discord.Embed:
    embed = discord.Embed(
        title=entry.get("name", ""),
        description=entry.get("description") or "",
        colour=discord.Color.teal(),
        url=entry.get("url"),
    )
    if entry.get("url"):
        embed.add_field(name="Link", value=entry["url"], inline=False)

    timestamps = []
    stamp_iso = entry.get("updatedAt") or entry.get("createdAt")
    if stamp_iso:
        parsed = discord.utils.parse_time(stamp_iso)
        if parsed:
            epoch = int(parsed.replace(tzinfo=timezone.utc).timestamp())
            actor = entry.get("updatedBy") or entry.get("createdBy")
            actor_display = f"<@{actor}>" if actor else "Unknown"
            timestamps.append(f"Updated by {actor_display} <t:{epoch}:R>")

    if timestamps:
        embed.add_field(name="Activity", value="\n".join(timestamps), inline=False)

    return embed


class LookupListView(discord.ui.View):
    def __init__(self, entries: List[Dict[str, Any]], guild_name: str, *, per_page: int = 10):
        super().__init__(timeout=120)
        self.entries = entries
        self.guild_name = guild_name
        self.per_page = max(1, per_page)
        self.page = 0
        self._sync_button_states()

    def render_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"{self.guild_name} Lookup Entries",
            colour=discord.Color.dark_teal(),
        )
        total = len(self.entries)
        embed.description = f"{total} entr{'y' if total == 1 else 'ies'}"

        start = self.page * self.per_page
        end = start + self.per_page
        slice_entries = self.entries[start:end]
        for entry in slice_entries:
            lines: List[str] = [entry.get("url", "")] if entry.get("url") else []
            stamp_iso = entry.get("updatedAt") or entry.get("createdAt")
            parsed = discord.utils.parse_time(stamp_iso) if stamp_iso else None
            if parsed is not None:
                epoch = int(parsed.replace(tzinfo=timezone.utc).timestamp())
                actor = entry.get("updatedBy") or entry.get("createdBy")
                actor_display = f"<@{actor}>" if actor else "Unknown"
                lines.append(f"Updated by {actor_display} <t:{epoch}:R>")
            if entry.get("description"):
                lines.append(entry["description"])
            embed.add_field(name=entry.get("name", "(unnamed)"), value="\n".join(lines) or "—", inline=False)

        embed.set_footer(text=f"Page {self.page + 1} of {self._total_pages}")
        return embed

    @property
    def _total_pages(self) -> int:
        return max(1, math.ceil(len(self.entries) / self.per_page))

    def _sync_button_states(self) -> None:
        total = self._total_pages
        for child in self.children:
            if not isinstance(child, discord.ui.Button):
                continue
            if child.custom_id == "lookup:list:prev":
                child.disabled = self.page <= 0
            if child.custom_id == "lookup:list:next":
                child.disabled = self.page >= total - 1

    async def on_timeout(self) -> None:
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="lookup:list:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.page > 0:
            self.page -= 1
        self._sync_button_states()
        await interaction.response.edit_message(embed=self.render_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, custom_id="lookup:list:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.page < self._total_pages - 1:
            self.page += 1
        self._sync_button_states()
        await interaction.response.edit_message(embed=self.render_embed(), view=self)


async def setup(bot: commands.Bot) -> None:  # pragma: no cover - extension entry point
    # Use override=True to replace any previously-registered /lookup command
    # This prevents CommandAlreadyRegistered when an older registration exists.
    await bot.add_cog(LookupCommandsCog(bot), override=True)
