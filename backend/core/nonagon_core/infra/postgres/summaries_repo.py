# nonagon_core/infra/postgres/summaries_repo.py
"""
PostgreSQL repository for QuestSummary entities using SQLAlchemy.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import and_, select

from nonagon_core.domain.models.EntityIDModel import SummaryID
from nonagon_core.domain.models.SummaryModel import QuestSummary
from nonagon_core.infra.postgres.database import get_session
from nonagon_core.infra.postgres.mappers import summary_from_orm, summary_to_orm
from nonagon_core.infra.postgres.models import SummaryModel


class SummariesRepoPostgres:
    """Async PostgreSQL repository for QuestSummary entities."""

    async def upsert(self, guild_id: int, summary: QuestSummary) -> bool:
        """
        Insert or update a summary.
        Returns True on success.
        """
        async with get_session() as session:
            # Check if summary exists
            stmt = select(SummaryModel).where(
                and_(
                    SummaryModel.guild_id == int(guild_id),
                    SummaryModel.summary_id == str(summary.summary_id),
                )
            )
            
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing summary
                existing.kind = summary.kind.value if hasattr(summary.kind, 'value') else summary.kind
                existing.author_id = str(summary.author_id) if summary.author_id else None
                existing.character_id = str(summary.character_id) if summary.character_id else None
                existing.quest_id = str(summary.quest_id) if summary.quest_id else None
                existing.raw = summary.raw
                existing.title = summary.title
                existing.description = summary.description
                existing.created_on = summary.created_on
                existing.last_edited_at = summary.last_edited_at
                existing.players = [str(p) for p in (summary.players or [])]
                existing.characters = [str(c) for c in (summary.characters or [])]
                existing.linked_quests = [str(q) for q in (summary.linked_quests or [])]
                existing.linked_summaries = [str(s) for s in (summary.linked_summaries or [])]
                existing.channel_id = summary.channel_id
                existing.message_id = summary.message_id
                existing.thread_id = summary.thread_id
                existing.status = summary.status.value if hasattr(summary.status, 'value') else summary.status
            else:
                # Create new summary
                summary.guild_id = int(guild_id)
                new_summary = summary_to_orm(summary)
                session.add(new_summary)

            return True

    async def get(self, guild_id: int, summary_id: str) -> Optional[QuestSummary]:
        """Get a summary by guild_id and summary_id."""
        sid = SummaryID.parse(summary_id)
        
        async with get_session() as session:
            stmt = select(SummaryModel).where(
                and_(
                    SummaryModel.guild_id == int(guild_id),
                    SummaryModel.summary_id == sid.value,
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return summary_from_orm(model) if model else None

    async def delete(self, guild_id: int, summary_id: str) -> bool:
        """Delete a summary. Returns True if deleted, False if not found."""
        sid = SummaryID.parse(summary_id)
        
        async with get_session() as session:
            stmt = select(SummaryModel).where(
                and_(
                    SummaryModel.guild_id == int(guild_id),
                    SummaryModel.summary_id == sid.value,
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                await session.delete(model)
                return True
            return False

    async def exists(self, guild_id: int, summary_id: str) -> bool:
        """Check if a summary exists."""
        sid = SummaryID.parse(summary_id)
        
        async with get_session() as session:
            stmt = select(SummaryModel.id).where(
                and_(
                    SummaryModel.guild_id == int(guild_id),
                    SummaryModel.summary_id == sid.value,
                )
            ).limit(1)
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def next_id(self, guild_id: int) -> str:
        """
        Generate a new unique SummaryID.
        Uses collision checking with generated postal IDs.
        """
        async with get_session() as session:
            while True:
                candidate = SummaryID.generate()
                
                stmt = select(SummaryModel.id).where(
                    and_(
                        SummaryModel.guild_id == int(guild_id),
                        SummaryModel.summary_id == candidate.value,
                    )
                ).limit(1)
                
                result = await session.execute(stmt)
                if result.scalar_one_or_none() is None:
                    return str(candidate)
