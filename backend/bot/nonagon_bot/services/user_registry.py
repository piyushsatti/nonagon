from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Callable, Optional

from discord import Member

from nonagon_bot.core.domain.models.EntityIDModel import UserID
from nonagon_bot.core.domain.models.UserModel import Role, User
from nonagon_bot.services import graphql_client


class UserRegistry:
    """Adapter that keeps domain users in sync with Discord members.

    The registry is backed by the GraphQL API so the bot can create or fetch
    user records during gateway events without direct DB access.
    """

    def __init__(
        self,
        *,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _from_gql_user(self, payload: dict, *, joined_at: Optional[datetime] = None) -> User:
        roles = [Role(r) for r in (payload.get("roles") or []) if r]
        if not roles:
            roles = [Role.MEMBER]
        return User(
            user_id=UserID.parse(payload["userId"]),
            guild_id=int(payload["guildId"]),
            discord_id=payload.get("discordId"),
            dm_channel_id=payload.get("dmChannelId"),
            roles=roles,
            dm_opt_in=bool(payload.get("dmOptIn", True)),
            joined_at=joined_at or self._clock(),
            last_active_at=payload.get("lastActiveAt") or joined_at or self._clock(),
        )

    async def ensure_member(
        self, member: Member, guild_id: Optional[int] = None
    ) -> User:
        """Return a domain user for the Discord member, creating it if needed."""
        if member.bot:
            raise ValueError("Bots are not tracked as users")

        resolved_guild_id = guild_id or getattr(member.guild, "id", None)
        if resolved_guild_id is None:
            raise ValueError("Guild id is required to ensure a member record")

        discord_id = str(member.id)
        existing = await graphql_client.get_user_by_discord(
            int(resolved_guild_id), discord_id
        )
        if existing:
            return self._from_gql_user(existing, joined_at=member.joined_at)

        created = await graphql_client.create_user(
            int(resolved_guild_id),
            discord_id,
            dm_channel_id=None,
            dm_opt_in=True,
            roles=None,
        )
        if created:
            return self._from_gql_user(
                {
                    **created,
                    "guildId": int(resolved_guild_id),
                    "discordId": discord_id,
                },
                joined_at=member.joined_at,
            )

        # Fallback to a minimal in-memory user if API is unreachable.
        joined_at = member.joined_at or self._clock()
        user = User(
            user_id=UserID.from_body(str(member.id)),
            guild_id=resolved_guild_id,
            discord_id=discord_id,
            dm_channel_id=None,
            roles=[Role.MEMBER],
            dm_opt_in=True,
            joined_at=joined_at,
            last_active_at=joined_at,
        )
        user.validate_user()
        return user

    async def touch_last_active(
        self, guild_id: int, user: User, *, active_at: Optional[datetime] = None
    ) -> User:
        """Update the cached user's last active timestamp and persist."""
        timestamp = active_at or self._clock()
        updated = replace(user, last_active_at=timestamp)
        updated.guild_id = guild_id
        updated.validate_user()
        try:
            await graphql_client.update_user_last_active(int(guild_id), str(user.user_id))
        except Exception:
            # Log at caller; keep in-memory state regardless.
            pass
        return updated
