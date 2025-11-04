from __future__ import annotations

from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from app.bot.cogs.admin.staff import is_allowed_staff
from app.bot.services import guild_settings_store
from app.bot.core.cache import ensure_guild_entry
from app.domain.models.EntityIDModel import UserID
from app.domain.models.UserModel import Role, User
from app.bot.utils.logging import get_logger


logger = get_logger(__name__)


class AssignRolesCog(commands.Cog):
    """Staff-only commands to assign domain roles to members."""

    assign = app_commands.Group(
        name="assign", description="Grant Nonagon roles to members (staff only)."
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    async def _resolve_or_create_user(self, member: discord.Member) -> User:
        listener: Optional[commands.Cog] = self.bot.get_cog("GuildListenersCog")
        if listener is not None:
            ensure_method = getattr(listener, "_ensure_cached_user", None)
            if ensure_method is not None:
                try:
                    return await ensure_method(member)  # type: ignore[misc]
                except Exception as exc:
                    logger.debug(
                        "Falling back to manual user creation for %s: %s",
                        member.id,
                        exc,
                    )

        ensure_guild_entry(self.bot, member.guild.id)
        guild_entry = self.bot.guild_data[member.guild.id]
        users = guild_entry.setdefault("users", {})
        user = users.get(member.id)
        if user is None:
            user = User(
                user_id=UserID.from_body(str(member.id)),
                guild_id=member.guild.id,
                roles=[Role.MEMBER],
            )
            users[member.id] = user
        return user

    @assign.command(name="referee", description="Grant referee role to a member (staff only).")
    @app_commands.describe(user="Member to grant the referee role to")
    @app_commands.guild_only()
    async def assign_referee(self, interaction: discord.Interaction, user: discord.Member) -> None:
        invoker = interaction.user
        if not isinstance(invoker, discord.Member) or not is_allowed_staff(self.bot, invoker):
            await interaction.response.send_message(
                "Only staff can use this command.", ephemeral=True
            )
            return

        if interaction.guild is None or user.guild != interaction.guild:
            await interaction.response.send_message(
                "Select a member from this server.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # Update domain role
        domain_user = await self._resolve_or_create_user(user)
        domain_user.enable_referee()
        await self.bot.dirty_data.put((interaction.guild.id, user.id))

        # Optionally add Discord role
        settings = guild_settings_store.fetch_settings(interaction.guild.id) or {}
        role_id_raw = settings.get("referee_role_id")
        referee_role = None
        try:
            referee_role = interaction.guild.get_role(int(role_id_raw)) if role_id_raw is not None else None
        except (TypeError, ValueError):
            referee_role = None

        discord_role_status = "not configured"
        if referee_role is not None:
            try:
                if referee_role not in user.roles:
                    await user.add_roles(referee_role, reason=f"Granted by {invoker} via /assign referee")
                discord_role_status = f"added {referee_role.mention}"
            except Exception as exc:
                logger.debug("Unable to grant referee Discord role: %s", exc)
                discord_role_status = "could not add (insufficient permissions)"

        await interaction.followup.send(
            f"Granted REFEREE to {user.mention} (domain). Discord role: {discord_role_status}.",
            ephemeral=True,
        )

    @assign.command(name="player", description="Grant player role to a member (staff only).")
    @app_commands.describe(user="Member to grant the player role to")
    @app_commands.guild_only()
    async def assign_player(self, interaction: discord.Interaction, user: discord.Member) -> None:
        invoker = interaction.user
        if not isinstance(invoker, discord.Member) or not is_allowed_staff(self.bot, invoker):
            await interaction.response.send_message(
                "Only staff can use this command.", ephemeral=True
            )
            return

        if interaction.guild is None or user.guild != interaction.guild:
            await interaction.response.send_message(
                "Select a member from this server.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # Update domain role
        domain_user = await self._resolve_or_create_user(user)
        domain_user.enable_player()
        await self.bot.dirty_data.put((interaction.guild.id, user.id))

        # Optionally add Discord role
        settings = guild_settings_store.fetch_settings(interaction.guild.id) or {}
        role_id_raw = settings.get("player_role_id")
        player_role = None
        try:
            player_role = interaction.guild.get_role(int(role_id_raw)) if role_id_raw is not None else None
        except (TypeError, ValueError):
            player_role = None

        discord_role_status = "not configured"
        if player_role is not None:
            try:
                if player_role not in user.roles:
                    await user.add_roles(player_role, reason=f"Granted by {invoker} via /assign player")
                discord_role_status = f"added {player_role.mention}"
            except Exception as exc:
                logger.debug("Unable to grant player Discord role: %s", exc)
                discord_role_status = "could not add (insufficient permissions)"

        await interaction.followup.send(
            f"Granted PLAYER to {user.mention} (domain). Discord role: {discord_role_status}.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AssignRolesCog(bot))
