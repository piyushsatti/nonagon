# nonagon_core/infra/postgres/lookup_repo.py
"""
PostgreSQL repository for LookupEntry entities using SQLAlchemy.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import and_, select

from nonagon_bot.core.domain.models.LookupModel import LookupEntry
from nonagon_bot.core.infra.postgres.database import get_session
from nonagon_bot.core.infra.postgres.mappers import lookup_from_orm, lookup_to_orm
from nonagon_bot.core.infra.postgres.models import LookupModel


class LookupRepoPostgres:
    """Async PostgreSQL repository for LookupEntry entities."""

    async def upsert(self, entry: LookupEntry) -> LookupEntry:
        """
        Insert or update a lookup entry.
        Returns the persisted entry.
        """
        async with get_session() as session:
            normalized = LookupEntry.normalize_name(entry.name)
            
            # Check if entry exists
            stmt = select(LookupModel).where(
                and_(
                    LookupModel.guild_id == int(entry.guild_id),
                    LookupModel.name_normalized == normalized,
                )
            )
            
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing entry
                existing.name = entry.name
                existing.name_normalized = normalized
                existing.url = entry.url
                existing.description = entry.description
                existing.updated_by = entry.updated_by
                existing.updated_at = entry.updated_at
                return lookup_from_orm(existing)
            else:
                # Create new entry
                new_entry = lookup_to_orm(entry)
                session.add(new_entry)
                await session.flush()
                return lookup_from_orm(new_entry)

    async def get_by_name(self, guild_id: int, name: str) -> Optional[LookupEntry]:
        """Get a lookup entry by exact name (case-insensitive)."""
        normalized = LookupEntry.normalize_name(name)
        
        async with get_session() as session:
            stmt = select(LookupModel).where(
                and_(
                    LookupModel.guild_id == int(guild_id),
                    LookupModel.name_normalized == normalized,
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return lookup_from_orm(model) if model else None

    async def list_all(self, guild_id: int) -> List[LookupEntry]:
        """List all lookup entries for a guild."""
        async with get_session() as session:
            stmt = select(LookupModel).where(
                LookupModel.guild_id == int(guild_id)
            ).order_by(LookupModel.name_normalized)
            
            result = await session.execute(stmt)
            models = result.scalars().all()
            
            return [lookup_from_orm(m) for m in models]

    async def delete(self, guild_id: int, name: str) -> bool:
        """Delete a lookup entry. Returns True if deleted, False if not found."""
        normalized = LookupEntry.normalize_name(name)
        
        async with get_session() as session:
            stmt = select(LookupModel).where(
                and_(
                    LookupModel.guild_id == int(guild_id),
                    LookupModel.name_normalized == normalized,
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                await session.delete(model)
                return True
            return False

    async def find_best_match(self, guild_id: int, query: str) -> Optional[LookupEntry]:
        """
        Find the best matching lookup entry using fuzzy matching.
        Uses PostgreSQL's similarity function (requires pg_trgm extension).
        Falls back to ILIKE prefix matching if pg_trgm is not available.
        """
        normalized = LookupEntry.normalize_name(query)
        
        async with get_session() as session:
            # Try exact match first
            exact = await self.get_by_name(guild_id, query)
            if exact:
                return exact
            
            # Fall back to prefix match
            stmt = select(LookupModel).where(
                and_(
                    LookupModel.guild_id == int(guild_id),
                    LookupModel.name_normalized.ilike(f"{normalized}%"),
                )
            ).order_by(LookupModel.name_normalized).limit(1)
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return lookup_from_orm(model) if model else None
