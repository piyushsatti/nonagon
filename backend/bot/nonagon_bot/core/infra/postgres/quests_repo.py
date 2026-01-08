# nonagon_core/infra/postgres/quests_repo.py
"""
PostgreSQL repository for Quest entities using SQLAlchemy.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from nonagon_bot.core.domain.models.EntityIDModel import QuestID
from nonagon_bot.core.domain.models.QuestModel import Quest
from nonagon_bot.core.infra.postgres.database import get_session
from nonagon_bot.core.infra.postgres.mappers import quest_from_orm, quest_to_orm, signup_to_orm
from nonagon_bot.core.infra.postgres.models import QuestModel


class QuestsRepoPostgres:
    """Async PostgreSQL repository for Quest entities."""

    async def upsert(self, guild_id: int, quest: Quest) -> bool:
        """
        Insert or update a quest.
        Returns True on success.
        """
        async with get_session() as session:
            # Check if quest exists
            stmt = select(QuestModel).where(
                and_(
                    QuestModel.guild_id == int(guild_id),
                    QuestModel.quest_id == str(quest.quest_id),
                )
            ).options(selectinload(QuestModel.signups))
            
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing quest
                existing.referee_id = str(quest.referee_id)
                existing.channel_id = quest.channel_id
                existing.message_id = quest.message_id
                existing.raw = quest.raw
                existing.title = quest.title
                existing.description = quest.description
                existing.image_url = quest.image_url
                existing.starting_at = quest.starting_at
                existing.duration_seconds = int(quest.duration.total_seconds()) if quest.duration else None
                existing.announce_at = quest.announce_at
                existing.started_at = quest.started_at
                existing.ended_at = quest.ended_at
                existing.last_nudged_at = quest.last_nudged_at
                existing.status = quest.status.value if hasattr(quest.status, 'value') else quest.status
                existing.linked_quests = [str(q) for q in (quest.linked_quests or [])]
                existing.linked_summaries = [str(s) for s in (quest.linked_summaries or [])]

                # Handle signups - replace all
                # First, delete existing signups
                for signup in existing.signups:
                    await session.delete(signup)
                existing.signups = []
                
                await session.flush()

                # Add new signups
                for signup in quest.signups:
                    new_signup = signup_to_orm(signup, existing.id)
                    session.add(new_signup)
                    existing.signups.append(new_signup)

            else:
                # Create new quest
                quest.guild_id = int(guild_id)
                new_quest = quest_to_orm(quest)
                session.add(new_quest)
                await session.flush()  # Get the ID

                # Add signups
                for signup in quest.signups:
                    new_signup = signup_to_orm(signup, new_quest.id)
                    session.add(new_signup)

            return True

    async def get(self, guild_id: int, quest_id: str) -> Optional[Quest]:
        """Get a quest by guild_id and quest_id."""
        qid = QuestID.parse(quest_id)
        
        async with get_session() as session:
            stmt = select(QuestModel).where(
                and_(
                    QuestModel.guild_id == int(guild_id),
                    QuestModel.quest_id == qid.value,
                )
            ).options(selectinload(QuestModel.signups))
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            return quest_from_orm(model) if model else None

    async def delete(self, guild_id: int, quest_id: str) -> bool:
        """Delete a quest. Returns True if deleted, False if not found."""
        qid = QuestID.parse(quest_id)
        
        async with get_session() as session:
            stmt = select(QuestModel).where(
                and_(
                    QuestModel.guild_id == int(guild_id),
                    QuestModel.quest_id == qid.value,
                )
            )
            
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                await session.delete(model)
                return True
            return False

    async def exists(self, guild_id: int, quest_id: str) -> bool:
        """Check if a quest exists."""
        qid = QuestID.parse(quest_id)
        
        async with get_session() as session:
            stmt = select(QuestModel.id).where(
                and_(
                    QuestModel.guild_id == int(guild_id),
                    QuestModel.quest_id == qid.value,
                )
            ).limit(1)
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

    async def next_id(self, guild_id: int) -> str:
        """
        Generate a new unique QuestID.
        Uses collision checking with generated postal IDs.
        """
        async with get_session() as session:
            while True:
                candidate = QuestID.generate()
                
                stmt = select(QuestModel.id).where(
                    and_(
                        QuestModel.guild_id == int(guild_id),
                        QuestModel.quest_id == candidate.value,
                    )
                ).limit(1)
                
                result = await session.execute(stmt)
                if result.scalar_one_or_none() is None:
                    return str(candidate)

    async def list_pending_announce(self, guild_id: int, before: datetime) -> List[Quest]:
        """Get quests that need to be announced (announce_at <= before and no channel_id)."""
        async with get_session() as session:
            stmt = select(QuestModel).where(
                and_(
                    QuestModel.guild_id == int(guild_id),
                    QuestModel.announce_at <= before,
                    # Quest has no channel_id (not yet posted)
                    or_(QuestModel.channel_id == None, QuestModel.channel_id == ""),
                )
            ).options(selectinload(QuestModel.signups))
            
            result = await session.execute(stmt)
            models = result.scalars().all()
            
            return [quest_from_orm(m) for m in models]

    async def list_recent(self, guild_id: int, limit: int = 20) -> List[Quest]:
        """Get recent quests for a guild, ordered by starting_at desc."""
        async with get_session() as session:
            stmt = (
                select(QuestModel)
                .where(QuestModel.guild_id == int(guild_id))
                .options(selectinload(QuestModel.signups))
                .order_by(QuestModel.starting_at.desc())
                .limit(limit)
            )
            
            result = await session.execute(stmt)
            models = result.scalars().all()
            
            return [quest_from_orm(m) for m in models]
