# nonagon_core/infra/postgres/users_repo.py
"""
PostgreSQL repository for User entities using SQLAlchemy.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from nonagon_core.domain.models.EntityIDModel import UserID
from nonagon_core.domain.models.UserModel import User
from nonagon_core.infra.postgres.database import get_session
from nonagon_core.infra.postgres.mappers import (
    player_to_orm,
    referee_to_orm,
    user_from_orm,
    user_to_orm,
)
from nonagon_core.infra.postgres.models import UserModel


class UsersRepoPostgres:
    """Async PostgreSQL repository for User entities."""

    async def upsert(self, guild_id: int, user: User) -> bool:
        """
        Insert or update a user.
        Returns True on success.
        """
        async with get_session() as session:
            # Check if user exists
            stmt = select(UserModel).where(
                and_(
                    UserModel.guild_id == int(guild_id),
                    UserModel.user_id == str(user.user_id),
                )
            ).options(selectinload(UserModel.player), selectinload(UserModel.referee))
            
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing user
                existing.discord_id = user.discord_id
                existing.dm_channel_id = user.dm_channel_id
                existing.roles = [r.value for r in user.roles]
                existing.has_server_tag = user.has_server_tag
                existing.dm_opt_in = user.dm_opt_in
                existing.joined_at = user.joined_at
                existing.last_active_at = user.last_active_at
                existing.messages_count_total = user.messages_count_total
                existing.reactions_given = user.reactions_given
                existing.reactions_received = user.reactions_received
                existing.voice_total_time_spent = user.voice_total_time_spent

                # Handle player profile
                if user.player:
                    if existing.player:
                        # Update existing player
                        existing.player.characters = [str(c) for c in user.player.characters]
                        existing.player.joined_on = user.player.joined_on
                        existing.player.created_first_character_on = user.player.created_first_character_on
                        existing.player.last_played_on = user.player.last_played_on
                        existing.player.quests_applied = [str(q) for q in user.player.quests_applied]
                        existing.player.quests_played = [str(q) for q in user.player.quests_played]
                        existing.player.summaries_written = [str(s) for s in user.player.summaries_written]
                        existing.player.played_with_character = {
                            str(k): v for k, v in user.player.played_with_character.items()
                        }
                    else:
                        # Create new player profile
                        existing.player = player_to_orm(user.player, existing.id)
                elif existing.player:
                    # Remove player profile
                    await session.delete(existing.player)
                    existing.player = None

                # Handle referee profile
                if user.referee:
                    if existing.referee:
                        # Update existing referee
                        existing.referee.quests_hosted = [str(q) for q in user.referee.quests_hosted]
                        existing.referee.summaries_written = [str(s) for s in user.referee.summaries_written]
                        existing.referee.first_dmed_on = user.referee.first_dmed_on
                        existing.referee.last_dmed_on = user.referee.last_dmed_on
                        existing.referee.collabed_with = {
                            str(k): v for k, v in user.referee.collabed_with.items()
                        }
                        existing.referee.hosted_for = {
                            str(k): v for k, v in user.referee.hosted_for.items()
                        }
                    else:
                        # Create new referee profile
                        existing.referee = referee_to_orm(user.referee, existing.id)
                elif existing.referee:
                    # Remove referee profile
                    await session.delete(existing.referee)
                    existing.referee = None

            else:
                # Create new user
                user.guild_id = int(guild_id)
                new_user = user_to_orm(user)
                session.add(new_user)
                await session.flush()  # Get the ID

                # Add player profile if exists
                if user.player:
                    new_user.player = player_to_orm(user.player, new_user.id)

                # Add referee profile if exists
                if user.referee:
                    new_user.referee = referee_to_orm(user.referee, new_user.id)

            return True

    async def get(self, guild_id: int, user_id: str) -> Optional[User]:
        """Get a user by guild_id and user_id."""
        uid = UserID.parse(user_id)
        
        async with get_session() as session:
            stmt = select(UserModel).where(
                and_(
                    UserModel.guild_id == int(guild_id),
                    UserModel.user_id == uid.value,
                )
            ).options(selectinload(UserModel.player), selectinload(UserModel.referee))
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return user_from_orm(model) if model else None

    async def delete(self, guild_id: int, user_id: str) -> bool:
        """Delete a user. Returns True if deleted, False if not found."""
        uid = UserID.parse(user_id)
        
        async with get_session() as session:
            stmt = select(UserModel).where(
                and_(
                    UserModel.guild_id == int(guild_id),
                    UserModel.user_id == uid.value,
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                await session.delete(model)
                return True
            return False

    async def exists(self, guild_id: int, user_id: str) -> bool:
        """Check if a user exists."""
        uid = UserID.parse(user_id)
        
        async with get_session() as session:
            stmt = select(UserModel.id).where(
                and_(
                    UserModel.guild_id == int(guild_id),
                    UserModel.user_id == uid.value,
                )
            ).limit(1)
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def next_id(self, guild_id: int) -> str:
        """
        Generate a new unique UserID.
        Uses collision checking with generated postal IDs.
        """
        async with get_session() as session:
            while True:
                candidate = UserID.generate()
                
                stmt = select(UserModel.id).where(
                    and_(
                        UserModel.guild_id == int(guild_id),
                        UserModel.user_id == candidate.value,
                    )
                ).limit(1)
                
                result = await session.execute(stmt)
                if result.scalar_one_or_none() is None:
                    return str(candidate)

    async def get_by_discord_id(self, guild_id: int, discord_id: str) -> Optional[User]:
        """Get a user by their Discord ID."""
        async with get_session() as session:
            stmt = select(UserModel).where(
                and_(
                    UserModel.guild_id == int(guild_id),
                    UserModel.discord_id == discord_id,
                )
            ).options(selectinload(UserModel.player), selectinload(UserModel.referee))
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return user_from_orm(model) if model else None
