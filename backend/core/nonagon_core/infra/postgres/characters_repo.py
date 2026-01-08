# nonagon_core/infra/postgres/characters_repo.py
"""
PostgreSQL repository for Character entities using SQLAlchemy.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import and_, select

from nonagon_core.domain.models.CharacterModel import Character
from nonagon_core.domain.models.EntityIDModel import CharacterID
from nonagon_core.infra.postgres.database import get_session
from nonagon_core.infra.postgres.mappers import character_from_orm, character_to_orm
from nonagon_core.infra.postgres.models import CharacterModel


class CharactersRepoPostgres:
    """Async PostgreSQL repository for Character entities."""

    async def upsert(self, guild_id: int, character: Character) -> bool:
        """
        Insert or update a character.
        Returns True on success.
        """
        async with get_session() as session:
            # Check if character exists
            stmt = select(CharacterModel).where(
                and_(
                    CharacterModel.guild_id == int(guild_id),
                    CharacterModel.character_id == str(character.character_id),
                )
            )
            
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing character
                existing.owner_id = str(character.owner_id)
                existing.name = character.name
                existing.status = character.status.value if hasattr(character.status, 'value') else character.status
                existing.ddb_link = character.ddb_link
                existing.character_thread_link = character.character_thread_link
                existing.token_link = character.token_link
                existing.art_link = character.art_link
                existing.announcement_channel_id = character.announcement_channel_id
                existing.announcement_message_id = character.announcement_message_id
                existing.onboarding_thread_id = character.onboarding_thread_id
                existing.created_at = character.created_at
                existing.last_played_at = character.last_played_at
                existing.quests_played = character.quests_played
                existing.summaries_written = character.summaries_written
                existing.description = character.description
                existing.notes = character.notes
                existing.tags = character.tags or []
                existing.played_with = [str(c) for c in (character.played_with or [])]
                existing.played_in = [str(q) for q in (character.played_in or [])]
                existing.mentioned_in = [str(s) for s in (character.mentioned_in or [])]
            else:
                # Create new character
                character.guild_id = int(guild_id)
                new_char = character_to_orm(character)
                session.add(new_char)

            return True

    async def get(self, guild_id: int, character_id: str) -> Optional[Character]:
        """Get a character by guild_id and character_id."""
        async with get_session() as session:
            stmt = select(CharacterModel).where(
                and_(
                    CharacterModel.guild_id == int(guild_id),
                    CharacterModel.character_id == str(character_id),
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return character_from_orm(model) if model else None

    async def delete(self, guild_id: int, character_id: str) -> bool:
        """Delete a character. Returns True if deleted, False if not found."""
        async with get_session() as session:
            stmt = select(CharacterModel).where(
                and_(
                    CharacterModel.guild_id == int(guild_id),
                    CharacterModel.character_id == str(character_id),
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                await session.delete(model)
                return True
            return False

    async def exists(self, guild_id: int, character_id: str) -> bool:
        """Check if a character exists."""
        async with get_session() as session:
            stmt = select(CharacterModel.id).where(
                and_(
                    CharacterModel.guild_id == int(guild_id),
                    CharacterModel.character_id == str(character_id),
                )
            ).limit(1)
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def next_id(self, guild_id: int) -> str:
        """
        Generate a new unique CharacterID.
        Uses collision checking with generated postal IDs.
        """
        async with get_session() as session:
            while True:
                candidate = CharacterID.generate()
                
                stmt = select(CharacterModel.id).where(
                    and_(
                        CharacterModel.guild_id == int(guild_id),
                        CharacterModel.character_id == candidate.value,
                    )
                ).limit(1)
                
                result = await session.execute(stmt)
                if result.scalar_one_or_none() is None:
                    return str(candidate)
