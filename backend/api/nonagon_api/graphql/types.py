# nonagon_api/graphql/types.py
"""
Strawberry GraphQL type definitions.
These types mirror the domain models and API schemas.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

import strawberry


# =============================================================================
# Enums
# =============================================================================

@strawberry.enum
class UserRole(Enum):
    MEMBER = "MEMBER"
    PLAYER = "PLAYER"
    REFEREE = "REFEREE"


@strawberry.enum
class CharacterStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@strawberry.enum
class QuestStatus(Enum):
    DRAFT = "DRAFT"
    ANNOUNCED = "ANNOUNCED"
    SIGNUP_CLOSED = "SIGNUP_CLOSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@strawberry.enum
class PlayerSignupStatus(Enum):
    APPLIED = "APPLIED"
    SELECTED = "SELECTED"


@strawberry.enum
class SummaryKind(Enum):
    PLAYER = "PLAYER"
    REFEREE = "REFEREE"


@strawberry.enum
class SummaryStatus(Enum):
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


@strawberry.enum
class LeaderboardMetric(Enum):
    MESSAGES = "messages"
    REACTIONS_GIVEN = "reactions_given"
    REACTIONS_RECEIVED = "reactions_received"
    VOICE = "voice"


# =============================================================================
# Player & Referee Types (embedded in User)
# =============================================================================

@strawberry.type
class Player:
    """Player role profile for a user."""
    characters: List[str]
    joined_on: Optional[datetime] = None
    created_first_character_on: Optional[datetime] = None
    last_played_on: Optional[datetime] = None
    quests_applied: List[str] = strawberry.field(default_factory=list)
    quests_played: List[str] = strawberry.field(default_factory=list)
    summaries_written: List[str] = strawberry.field(default_factory=list)


@strawberry.type
class Referee:
    """Referee role profile for a user."""
    quests_hosted: List[str] = strawberry.field(default_factory=list)
    summaries_written: List[str] = strawberry.field(default_factory=list)
    first_dmed_on: Optional[datetime] = None
    last_dmed_on: Optional[datetime] = None


# =============================================================================
# User Types
# =============================================================================

@strawberry.type
class User:
    """A guild member who can be a player and/or referee."""
    user_id: str
    guild_id: int
    discord_id: Optional[str] = None
    dm_channel_id: Optional[str] = None
    roles: List[UserRole]
    has_server_tag: bool = False
    dm_opt_in: bool = True
    joined_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    messages_count_total: int = 0
    reactions_given: int = 0
    reactions_received: int = 0
    voice_total_time_spent: float = 0.0
    player: Optional[Player] = None
    referee: Optional[Referee] = None


@strawberry.input
class CreateUserInput:
    """Input for creating a new user."""
    discord_id: Optional[str] = None
    dm_channel_id: Optional[str] = None
    dm_opt_in: bool = True
    roles: List[UserRole] = strawberry.field(default_factory=lambda: [UserRole.MEMBER])


@strawberry.input
class UpdateUserInput:
    """Input for updating a user."""
    discord_id: Optional[str] = strawberry.UNSET
    dm_channel_id: Optional[str] = strawberry.UNSET
    dm_opt_in: Optional[bool] = strawberry.UNSET
    roles: Optional[List[UserRole]] = strawberry.UNSET


# =============================================================================
# Character Types
# =============================================================================

@strawberry.type
class Character:
    """A player's character in the game."""
    character_id: str
    guild_id: int
    owner_id: str
    name: str
    status: CharacterStatus = CharacterStatus.ACTIVE
    ddb_link: Optional[str] = None
    character_thread_link: Optional[str] = None
    token_link: Optional[str] = None
    art_link: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = strawberry.field(default_factory=list)
    created_at: Optional[datetime] = None
    last_played_at: Optional[datetime] = None
    quests_played: int = 0
    summaries_written: int = 0
    played_with: List[str] = strawberry.field(default_factory=list)
    played_in: List[str] = strawberry.field(default_factory=list)
    mentioned_in: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class CreateCharacterInput:
    """Input for creating a new character."""
    name: str
    owner_id: str
    ddb_link: Optional[str] = None
    character_thread_link: Optional[str] = None
    token_link: Optional[str] = None
    art_link: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateCharacterInput:
    """Input for updating a character."""
    name: Optional[str] = strawberry.UNSET
    ddb_link: Optional[str] = strawberry.UNSET
    character_thread_link: Optional[str] = strawberry.UNSET
    token_link: Optional[str] = strawberry.UNSET
    art_link: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    notes: Optional[str] = strawberry.UNSET
    tags: Optional[List[str]] = strawberry.UNSET
    status: Optional[CharacterStatus] = strawberry.UNSET


# =============================================================================
# Quest Types
# =============================================================================

@strawberry.type
class PlayerSignup:
    """A player's signup for a quest."""
    user_id: str
    character_id: str
    status: PlayerSignupStatus = PlayerSignupStatus.APPLIED


@strawberry.type
class Quest:
    """A quest that players can sign up for."""
    quest_id: str
    guild_id: int
    referee_id: str
    channel_id: Optional[str] = None
    message_id: Optional[str] = None
    raw: str
    title: Optional[str] = None
    description: Optional[str] = None
    starting_at: Optional[datetime] = None
    duration_hours: Optional[int] = None
    image_url: Optional[str] = None
    status: QuestStatus = QuestStatus.DRAFT
    announce_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    last_nudged_at: Optional[datetime] = None
    signups: List[PlayerSignup] = strawberry.field(default_factory=list)
    linked_quests: List[str] = strawberry.field(default_factory=list)
    linked_summaries: List[str] = strawberry.field(default_factory=list)
    
    @strawberry.field
    def is_signup_open(self) -> bool:
        return self.status == QuestStatus.ANNOUNCED


@strawberry.input
class CreateQuestInput:
    """Input for creating a new quest."""
    referee_id: str
    raw: str
    channel_id: str
    message_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    starting_at: Optional[datetime] = None
    duration_hours: Optional[int] = None
    image_url: Optional[str] = None
    linked_quests: List[str] = strawberry.field(default_factory=list)
    linked_summaries: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateQuestInput:
    """Input for updating a quest."""
    title: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    starting_at: Optional[datetime] = strawberry.UNSET
    duration_hours: Optional[int] = strawberry.UNSET
    image_url: Optional[str] = strawberry.UNSET
    linked_quests: Optional[List[str]] = strawberry.UNSET
    linked_summaries: Optional[List[str]] = strawberry.UNSET


@strawberry.input
class AddSignupInput:
    """Input for adding a signup to a quest."""
    user_id: str
    character_id: str


# =============================================================================
# Summary Types
# =============================================================================

@strawberry.type
class Summary:
    """A quest summary written by a player or referee."""
    summary_id: str
    guild_id: int
    kind: SummaryKind = SummaryKind.PLAYER
    author_id: Optional[str] = None
    character_id: Optional[str] = None
    quest_id: Optional[str] = None
    raw: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    created_on: Optional[datetime] = None
    last_edited_at: Optional[datetime] = None
    players: List[str] = strawberry.field(default_factory=list)
    characters: List[str] = strawberry.field(default_factory=list)
    linked_quests: List[str] = strawberry.field(default_factory=list)
    linked_summaries: List[str] = strawberry.field(default_factory=list)
    channel_id: Optional[str] = None
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    status: SummaryStatus = SummaryStatus.POSTED


@strawberry.input
class CreateSummaryInput:
    """Input for creating a new summary."""
    kind: SummaryKind = SummaryKind.PLAYER
    author_id: str
    character_id: Optional[str] = None
    quest_id: Optional[str] = None
    raw: Optional[str] = None
    title: str
    description: str
    characters: List[str] = strawberry.field(default_factory=list)
    players: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateSummaryInput:
    """Input for updating a summary."""
    title: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    raw: Optional[str] = strawberry.UNSET
    characters: Optional[List[str]] = strawberry.UNSET
    players: Optional[List[str]] = strawberry.UNSET


# =============================================================================
# Lookup Types
# =============================================================================

@strawberry.type
class LookupEntry:
    """A named URL lookup entry."""
    guild_id: int
    name: str
    url: str
    created_by: int
    created_at: datetime
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    description: Optional[str] = None


@strawberry.input
class CreateLookupInput:
    """Input for creating a lookup entry."""
    name: str
    url: str
    description: Optional[str] = None


@strawberry.input
class UpdateLookupInput:
    """Input for updating a lookup entry."""
    url: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET


# =============================================================================
# Leaderboard Types
# =============================================================================

@strawberry.type
class LeaderboardEntry:
    """A single entry in the leaderboard."""
    user_id: str
    discord_id: Optional[str]
    value: float
    rank: int


@strawberry.type
class LeaderboardResponse:
    """Response for leaderboard queries."""
    metric: LeaderboardMetric
    entries: List[LeaderboardEntry]


# =============================================================================
# Activity Stats Types
# =============================================================================

@strawberry.type
class TopContributor:
    """A top contributor in the guild."""
    user_id: str
    discord_id: Optional[str]
    username: Optional[str]
    messages: int
    reactions: int
    voice_hours: float


@strawberry.type
class ActivityStats:
    """Aggregated activity statistics for a guild."""
    total_messages: int
    total_reactions: int
    total_voice_hours: float
    active_users: int
    total_quests: int
    total_characters: int
    total_summaries: int
    top_contributors: List[TopContributor]
