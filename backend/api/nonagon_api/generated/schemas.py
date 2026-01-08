# AUTO-GENERATED - DO NOT EDIT
# Generated from shared/schemas/*.json
# Regenerate with: ./scripts/generate-types.sh
# This is a placeholder - run `make generate` to populate

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class Role(str, Enum):
    """User roles within a guild"""
    MEMBER = "MEMBER"
    PLAYER = "PLAYER"
    REFEREE = "REFEREE"


class QuestState(str, Enum):
    """Quest lifecycle states"""
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CharacterStatus(str, Enum):
    """Character availability status"""
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class SignUpStatus(str, Enum):
    """Player signup status for a quest"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"


class SummaryStatus(str, Enum):
    """Quest summary publication status"""
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class AuthorType(str, Enum):
    """Type of summary author"""
    PLAYER = "PLAYER"
    REFEREE = "REFEREE"


# ─────────────────────────────────────────────────────────────────────────────
# User Models
# ─────────────────────────────────────────────────────────────────────────────


class PlayedWithStats(BaseModel):
    """Statistics for playing with another character"""
    frequency: int = Field(..., ge=0, description="Number of times played together")
    hours: float = Field(..., ge=0, description="Total hours played together")


class CollabStats(BaseModel):
    """Collaboration statistics with another user"""
    frequency: int = Field(..., ge=0, description="Number of collaborations")
    hours: float = Field(..., ge=0, description="Total hours collaborated")


class PlayerSchema(BaseModel):
    """Player profile embedded in User"""
    characters: list[str] = Field(default_factory=list, description="List of character IDs owned by player")
    became_player_at: datetime | None = Field(None, description="When user became a player")
    first_character_at: datetime | None = Field(None, description="When first character was created")
    last_played_at: datetime | None = Field(None, description="Last play session timestamp")
    quests_applied: list[str] = Field(default_factory=list, description="Quest IDs applied to")
    quests_played: list[str] = Field(default_factory=list, description="Quest IDs completed")
    summaries_written: list[str] = Field(default_factory=list, description="Summary IDs authored as player")
    played_with_character: dict[str, PlayedWithStats] = Field(default_factory=dict, description="Map of CharacterID to play statistics")


class RefereeSchema(BaseModel):
    """Referee profile embedded in User"""
    quests_hosted: list[str] = Field(default_factory=list, description="Quest IDs hosted as referee")
    summaries_written: list[str] = Field(default_factory=list, description="Summary IDs authored as referee")
    first_dm_at: datetime | None = Field(None, description="First DM session timestamp")
    last_dm_at: datetime | None = Field(None, description="Last DM session timestamp")
    collabed_with: dict[str, CollabStats] = Field(default_factory=dict, description="Map of UserID to collaboration statistics")
    hosted_for: dict[str, int] = Field(default_factory=dict, description="Map of UserID to times hosted for")


class UserSchema(BaseModel):
    """Main user entity"""
    user_id: str = Field(..., description="Unique user identifier")
    guild_id: int = Field(..., description="Discord guild this user belongs to")
    discord_id: int | None = Field(None, description="Discord user snowflake ID")
    roles: list[Role] = Field(default_factory=list, description="User roles")
    is_tagged: bool = Field(False, description="Whether user has server tag")
    allow_dm: bool = Field(True, description="Whether user allows DM notifications")
    joined_at: datetime | None = Field(None, description="When user joined")
    last_active_at: datetime | None = Field(None, description="Last activity timestamp")
    messages_count_total: int = Field(0, ge=0, description="Total messages sent")
    messages_count_week: int = Field(0, ge=0, description="Messages sent this week")
    voice_minutes_total: int = Field(0, ge=0, description="Total voice minutes")
    reactions_count_total: int = Field(0, ge=0, description="Total reactions given")
    is_player: bool = Field(..., description="Whether user has player role")
    is_referee: bool = Field(..., description="Whether user has referee role")
    player: PlayerSchema | None = Field(None, description="Player profile if user is a player")
    referee: RefereeSchema | None = Field(None, description="Referee profile if user is a referee")


# ─────────────────────────────────────────────────────────────────────────────
# Quest Models
# ─────────────────────────────────────────────────────────────────────────────


class PlayerSignUpSchema(BaseModel):
    """Player signup for a quest"""
    user_id: str = Field(..., description="User signing up")
    character_id: str = Field(..., description="Character for the quest")
    status: SignUpStatus = Field(..., description="Signup status")


class QuestSchema(BaseModel):
    """Main quest entity"""
    quest_id: str = Field(..., description="Unique quest identifier")
    guild_id: int = Field(..., description="Discord guild this quest belongs to")
    referee_id: str = Field(..., description="User ID of the hosting referee")
    channel_id: int | None = Field(None, description="Discord channel for the quest")
    message_id: int | None = Field(None, description="Discord message ID for quest embed")
    title: str | None = Field(None, description="Quest title")
    description: str | None = Field(None, description="Quest description")
    scheduled_start: datetime | None = Field(None, description="Scheduled start time")
    duration_hours: int | None = Field(None, ge=0, description="Expected duration in hours")
    image_url: str | None = Field(None, description="Cover image URL")
    linked_quests: list[str] = Field(default_factory=list, description="Related quest IDs")
    linked_summaries: list[str] = Field(default_factory=list, description="Related summary IDs")
    state: QuestState = Field(..., description="Current lifecycle state")
    open_at: datetime | None = Field(None, description="When quest was opened for signups")
    started_at: datetime | None = Field(None, description="When quest actually started")
    ended_at: datetime | None = Field(None, description="When quest ended")
    signups: list[PlayerSignUpSchema] = Field(default_factory=list, description="List of player signups")
    signup_count: int = Field(0, ge=0, description="Total number of signups")
    accepted_count: int = Field(0, ge=0, description="Number of accepted signups")


# ─────────────────────────────────────────────────────────────────────────────
# Character Models
# ─────────────────────────────────────────────────────────────────────────────


class CharacterSchema(BaseModel):
    """Player character entity"""
    character_id: str = Field(..., description="Unique character identifier")
    owner_id: str = Field(..., description="User ID of the owning player")
    guild_id: int | None = Field(None, description="Discord guild this character belongs to")
    name: str = Field(..., min_length=1, description="Character name")
    sheet_url: str = Field(..., description="D&D Beyond character sheet URL")
    thread_url: str = Field(..., description="Character thread URL")
    token_url: str = Field(..., description="Character token image URL")
    art_url: str = Field(..., description="Character art URL")
    status: CharacterStatus = Field(..., description="Character status (ACTIVE or RETIRED)")
    channel_id: int | None = Field(None, description="Discord channel ID")
    message_id: int | None = Field(None, description="Discord message ID")
    thread_id: int | None = Field(None, description="Discord thread ID")
    created_at: datetime | None = Field(None, description="Character creation timestamp")
    last_played_at: datetime | None = Field(None, description="Last quest played timestamp")
    quests_played_count: int = Field(0, ge=0, description="Number of quests played")
    summaries_count: int = Field(0, ge=0, description="Number of summaries written")
    description: str | None = Field(None, description="Character description/backstory")
    notes: str | None = Field(None, description="Private notes (staff-only)")
    tags: list[str] = Field(default_factory=list, description="Custom tags")
    played_with: list[str] = Field(default_factory=list, description="Other characters played with")
    played_in: list[str] = Field(default_factory=list, description="Quest history")
    mentioned_in: list[str] = Field(default_factory=list, description="Summaries mentioning this character")


# ─────────────────────────────────────────────────────────────────────────────
# Summary Models
# ─────────────────────────────────────────────────────────────────────────────


class QuestSummarySchema(BaseModel):
    """Quest summary/write-up entity"""
    summary_id: str = Field(..., description="Unique summary identifier")
    guild_id: int = Field(..., description="Discord guild this summary belongs to")
    author_type: AuthorType = Field(..., description="Whether author is player or referee")
    author_id: str | None = Field(None, description="User ID of the author")
    character_id: str | None = Field(None, description="Character ID if author is a player")
    quest_id: str | None = Field(None, description="Related quest ID")
    title: str | None = Field(None, description="Summary title")
    content: str | None = Field(None, description="Summary content (markdown)")
    created_at: datetime = Field(..., description="Creation timestamp")
    edited_at: datetime | None = Field(None, description="Last edit timestamp")
    players: list[str] = Field(default_factory=list, description="Participating player user IDs")
    characters: list[str] = Field(default_factory=list, description="Participating character IDs")
    linked_quests: list[str] = Field(default_factory=list, description="Related quest IDs")
    linked_summaries: list[str] = Field(default_factory=list, description="Related summary IDs")
    channel_id: int | None = Field(None, description="Discord channel ID")
    message_id: int | None = Field(None, description="Discord message ID")
    thread_id: int | None = Field(None, description="Discord thread ID")
    status: SummaryStatus = Field(..., description="Publication status")
