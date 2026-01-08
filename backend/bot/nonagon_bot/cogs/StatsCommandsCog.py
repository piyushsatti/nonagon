from __future__ import annotations

from nonagon_bot.utils.logging import get_logger
from datetime import timezone
from typing import Optional, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from nonagon_bot.core.domain.models.UserModel import User
from nonagon_bot.services import graphql_client


logger = get_logger(__name__)


class StatsCommandsCog(commands.Cog):
    """Slash commands for engagement statistics."""

    LEADERBOARD_FIELDS: dict[str, Tuple[str, str]] = {
        "messages": ("messagesCountTotal", "Messages Sent"),
        "reactions_given": ("reactionsGiven", "Reactions Given"),
        "reactions_received": ("reactionsReceived", "Reactions Received"),
        "voice": ("voiceTotalTimeSpent", "Voice Time (hrs)"),
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _fetch_user_stats(self, guild_id: int, discord_id: int) -> Optional[dict]:
        return await graphql_client.get_user_by_discord(guild_id, str(discord_id))

    async def _get_cached_user(self, member: discord.Member) -> User:
        """Get user from database via UserRegistry."""
        from nonagon_bot.services.user_registry import UserRegistry

        registry = UserRegistry()
        user = await registry.ensure_member(member, member.guild.id)
        user.guild_id = member.guild.id
        return user

    @app_commands.command(name="stats", description="View your engagement stats.")
    async def stats(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used inside a guild.", ephemeral=True
            )
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "Only guild members can view stats.", ephemeral=True
            )
            return

        user = await self._fetch_user_stats(member.guild.id, member.id)
        if user is None:
            await interaction.response.send_message(
                "No profile found yet; try again after interacting in this server.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"Stats for {member.display_name}",
            colour=discord.Color.gold(),
        )
        embed.add_field(
            name="Messages", value=str(user.get("messagesCountTotal", 0)), inline=True
        )
        embed.add_field(
            name="Reactions Given",
            value=str(user.get("reactionsGiven", 0)),
            inline=True,
        )
        embed.add_field(
            name="Reactions Received",
            value=str(user.get("reactionsReceived", 0)),
            inline=True,
        )
        voice_total = float(user.get("voiceTotalTimeSpent", 0.0) or 0.0)
        embed.add_field(
            name="Voice Time (hrs)",
            value=f"{voice_total:.2f}",
            inline=True,
        )
        last_active_iso = user.get("lastActiveAt")
        if last_active_iso:
            try:
                # Discord embeds accept epoch seconds; parse ISO if present.
                last_active_dt = discord.utils.parse_time(last_active_iso)
                if last_active_dt is not None:
                    epoch = int(last_active_dt.replace(tzinfo=timezone.utc).timestamp())
                    embed.set_footer(text=f"Last active: <t:{epoch}:R>")
            except Exception:
                pass

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="leaderboard", description="View engagement leaderboards."
    )
    @app_commands.describe(metric="Metric to rank users by")
    @app_commands.choices(
        metric=[
            app_commands.Choice(name="Messages", value="messages"),
            app_commands.Choice(name="Reactions Given", value="reactions_given"),
            app_commands.Choice(name="Reactions Received", value="reactions_received"),
            app_commands.Choice(name="Voice Time", value="voice"),
        ]
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        metric: app_commands.Choice[str],
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used inside a guild.", ephemeral=True
            )
            return

        field, label = self.LEADERBOARD_FIELDS[metric.value]
        users = await graphql_client.list_users_by_guild(interaction.guild.id)
        rows = [u for u in users if (u.get(field) or 0) > 0]
        rows = sorted(rows, key=lambda u: u.get(field, 0), reverse=True)[:10]

        if not rows:
            await interaction.response.send_message(
                f"No data available for {metric.name} yet.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"{interaction.guild.name} — {label} Leaderboard",
            colour=discord.Color.purple(),
        )

        for idx, row in enumerate(rows, start=1):
            discord_id = row.get("discordId")
            member = (
                interaction.guild.get_member(int(discord_id)) if discord_id else None
            )
            display = (
                member.display_name if member else f"User {discord_id}" or "Unknown"
            )
            value = row.get(field, 0)
            if field == "voiceTotalTimeSpent":
                value = f"{float(value):.2f} hrs"
            embed.add_field(name=f"#{idx} {display}", value=str(value), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nudges", description="Enable or disable DM reminders.")
    @app_commands.describe(state="Choose whether to receive DM reminders from the bot")
    @app_commands.choices(
        state=[
            app_commands.Choice(name="Enable", value="enable"),
            app_commands.Choice(name="Disable", value="disable"),
        ]
    )
    async def nudges(
        self,
        interaction: discord.Interaction,
        state: app_commands.Choice[str],
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used inside a guild.", ephemeral=True
            )
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "Only guild members can update reminders.", ephemeral=True
            )
            return

        try:
            user = await self._get_cached_user(member)
        except RuntimeError as exc:
            logger.exception("Failed to resolve user for nudges: %s", exc)
            await interaction.response.send_message(
                "Internal error resolving your profile; please try again later.",
                ephemeral=True,
            )
            return

        enable = state.value == "enable"
        user.dm_opt_in = enable

        await interaction.response.send_message(
            f"DM reminders {'enabled' if enable else 'disabled'}.", ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCommandsCog(bot))
