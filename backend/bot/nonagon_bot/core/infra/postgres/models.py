# nonagon_core/infra/postgres/models.py
"""
SQLAlchemy ORM models for PostgreSQL/Supabase.

Design decisions:
- All tables include `guild_id` for multi-tenant isolation (enables RLS)
- Embedded documents (Player, Referee, PlayerSignUp) are normalized to separate tables
- Entity IDs (UserID, QuestID, etc.) stored as strings with their full prefix
- Timestamps stored as timezone-aware UTC
- Enums stored as strings for flexibility
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# =============================================================================
# Users & Role Profiles
# =============================================================================

class UserModel(Base):
    """
    Core user entity - corresponds to domain User model.
    Player and Referee profiles are in separate tables (normalized from embedded docs).
    """
    __tablename__ = "users"

    # Primary key: composite of guild_id + user_id for efficient lookups
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identity
    user_id: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "USERA1B2C3"
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    discord_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    dm_channel_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Roles stored as array of strings: ["MEMBER", "PLAYER", "REFEREE"]
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=["MEMBER"])
    has_server_tag: Mapped[bool] = mapped_column(Boolean, default=False)

    # Preferences
    dm_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Telemetry
    messages_count_total: Mapped[int] = mapped_column(Integer, default=0)
    reactions_given: Mapped[int] = mapped_column(Integer, default=0)
    reactions_received: Mapped[int] = mapped_column(Integer, default=0)
    voice_total_time_spent: Mapped[float] = mapped_column(Float, default=0.0)  # hours

    # Relationships
    player: Mapped[Optional["PlayerModel"]] = relationship(
        "PlayerModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    referee: Mapped[Optional["RefereeModel"]] = relationship(
        "RefereeModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    characters: Mapped[list["CharacterModel"]] = relationship(
        "CharacterModel", back_populates="owner", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("guild_id", "user_id", name="uq_users_guild_user"),
        UniqueConstraint("guild_id", "discord_id", name="uq_users_guild_discord"),
        Index("ix_users_guild_id", "guild_id"),
        Index("ix_users_discord_id", "discord_id"),
    )


class PlayerModel(Base):
    """
    Player role profile - normalized from embedded Player dataclass.
    One-to-one relationship with UserModel.
    """
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_pk: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Character list stored as array of character IDs
    characters: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    
    # Timestamps
    joined_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_first_character_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_played_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Quest tracking
    quests_applied: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    quests_played: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    summaries_written: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    # Character stats stored as JSONB: {"CHAR123": [count, last_played_ts]}
    played_with_character: Mapped[dict] = mapped_column(JSONB, default={})

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="player")


class RefereeModel(Base):
    """
    Referee role profile - normalized from embedded Referee dataclass.
    One-to-one relationship with UserModel.
    """
    __tablename__ = "referees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_pk: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Quest tracking
    quests_hosted: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    summaries_written: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    # Timestamps
    first_dmed_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_dmed_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Collaboration stats stored as JSONB
    collabed_with: Mapped[dict] = mapped_column(JSONB, default={})  # {"USER123": [count, last_ts]}
    hosted_for: Mapped[dict] = mapped_column(JSONB, default={})  # {"USER123": count}

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="referee")


# =============================================================================
# Characters
# =============================================================================

class CharacterModel(Base):
    """
    Character entity - corresponds to domain Character model.
    """
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identity
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "CHAR1234"
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    owner_pk: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    owner_id: Mapped[str] = mapped_column(String(20), nullable=False)  # UserID string
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE

    # Links
    ddb_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    character_thread_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    art_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Announcement metadata
    announcement_channel_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    announcement_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    onboarding_thread_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Telemetry
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_played_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    quests_played: Mapped[int] = mapped_column(Integer, default=0)
    summaries_written: Mapped[int] = mapped_column(Integer, default=0)

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    # Links to other entities (stored as arrays of IDs)
    played_with: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    played_in: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    mentioned_in: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    # Relationship
    owner: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="characters")

    __table_args__ = (
        UniqueConstraint("guild_id", "character_id", name="uq_characters_guild_character"),
        Index("ix_characters_guild_id", "guild_id"),
        Index("ix_characters_owner_id", "owner_id"),
    )


# =============================================================================
# Quests
# =============================================================================

class QuestModel(Base):
    """
    Quest entity - corresponds to domain Quest model.
    Signups are in a separate junction table.
    """
    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identity
    quest_id: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "QUESH3X1T7"
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    referee_id: Mapped[str] = mapped_column(String(20), nullable=False)  # UserID string
    
    # Discord message reference
    channel_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    message_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    
    # Content
    raw: Mapped[str] = mapped_column(Text, nullable=False)  # Raw markdown input
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timing
    starting_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Store as seconds
    announce_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_nudged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Lifecycle
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT, ANNOUNCED, etc.

    # Links to other entities
    linked_quests: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    linked_summaries: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    # Relationships
    signups: Mapped[list["QuestSignupModel"]] = relationship(
        "QuestSignupModel", back_populates="quest", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("guild_id", "quest_id", name="uq_quests_guild_quest"),
        UniqueConstraint("guild_id", "channel_id", "message_id", name="uq_quests_guild_channel_message"),
        Index("ix_quests_guild_id", "guild_id"),
        Index("ix_quests_status", "status"),
    )


class QuestSignupModel(Base):
    """
    Quest signup - normalized from embedded PlayerSignUp list.
    """
    __tablename__ = "quest_signups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quest_pk: Mapped[int] = mapped_column(Integer, ForeignKey("quests.id", ondelete="CASCADE"))
    
    user_id: Mapped[str] = mapped_column(String(20), nullable=False)  # UserID string
    character_id: Mapped[str] = mapped_column(String(20), nullable=False)  # CharacterID string
    status: Mapped[str] = mapped_column(String(20), default="APPLIED")  # APPLIED, SELECTED

    quest: Mapped["QuestModel"] = relationship("QuestModel", back_populates="signups")

    __table_args__ = (
        UniqueConstraint("quest_pk", "user_id", name="uq_signups_quest_user"),
        Index("ix_signups_user_id", "user_id"),
    )


# =============================================================================
# Summaries
# =============================================================================

class SummaryModel(Base):
    """
    Quest summary - corresponds to domain QuestSummary model.
    """
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identity
    summary_id: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "SUMMX5Y6Z7"
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    # Type and ownership
    kind: Mapped[str] = mapped_column(String(20), default="PLAYER")  # PLAYER, REFEREE
    author_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # UserID
    character_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # CharacterID
    quest_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # QuestID

    # Content
    raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    last_edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # References (arrays of IDs)
    players: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    characters: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    linked_quests: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    linked_summaries: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])

    # Discord announcement
    channel_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    message_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="POSTED")  # POSTED, CANCELLED

    __table_args__ = (
        UniqueConstraint("guild_id", "summary_id", name="uq_summaries_guild_summary"),
        Index("ix_summaries_guild_id", "guild_id"),
        Index("ix_summaries_quest_id", "quest_id"),
    )


# =============================================================================
# Lookups
# =============================================================================

class LookupModel(Base):
    """
    Lookup entry - corresponds to domain LookupEntry model.
    """
    __tablename__ = "lookups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_normalized: Mapped[str] = mapped_column(String(100), nullable=False)  # Lowercased, whitespace-collapsed
    url: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Discord user ID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("guild_id", "name_normalized", name="uq_lookups_guild_name"),
        Index("ix_lookups_guild_id", "guild_id"),
    )


# =============================================================================
# ID Counter (for generating sequential IDs)
# =============================================================================

class IDCounterModel(Base):
    """
    Counter table for generating sequential postal IDs per entity type per guild.
    This replaces the MongoDB collision-check approach with atomic increments.
    """
    __tablename__ = "id_counters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # USER, QUES, CHAR, SUMM
    counter: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("guild_id", "entity_type", name="uq_counters_guild_entity"),
    )
