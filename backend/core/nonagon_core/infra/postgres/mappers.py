# nonagon_core/infra/postgres/mappers.py
"""
Mappers between domain models (dataclasses) and SQLAlchemy ORM models.
"""
from __future__ import annotations

from datetime import timedelta

from nonagon_core.domain.models.CharacterModel import Character, CharacterRole
from nonagon_core.domain.models.EntityIDModel import (
    CharacterID,
    QuestID,
    SummaryID,
    UserID,
)
from nonagon_core.domain.models.LookupModel import LookupEntry
from nonagon_core.domain.models.QuestModel import (
    PlayerSignUp,
    PlayerStatus,
    Quest,
    QuestStatus,
)
from nonagon_core.domain.models.SummaryModel import (
    QuestSummary,
    SummaryKind,
    SummaryStatus,
)
from nonagon_core.domain.models.UserModel import Player, Referee, Role, User
from nonagon_core.infra.postgres.models import (
    CharacterModel,
    LookupModel,
    PlayerModel,
    QuestModel,
    QuestSignupModel,
    RefereeModel,
    SummaryModel,
    UserModel,
)


# =============================================================================
# User Mappers
# =============================================================================

def user_to_orm(user: User) -> UserModel:
    """Convert domain User to ORM UserModel."""
    return UserModel(
        user_id=str(user.user_id),
        guild_id=user.guild_id,
        discord_id=user.discord_id,
        dm_channel_id=user.dm_channel_id,
        roles=[r.value for r in user.roles],
        has_server_tag=user.has_server_tag,
        dm_opt_in=user.dm_opt_in,
        joined_at=user.joined_at,
        last_active_at=user.last_active_at,
        messages_count_total=user.messages_count_total,
        reactions_given=user.reactions_given,
        reactions_received=user.reactions_received,
        voice_total_time_spent=user.voice_total_time_spent,
    )


def user_from_orm(model: UserModel) -> User:
    """Convert ORM UserModel to domain User."""
    player = None
    if model.player:
        player = Player(
            characters=[CharacterID.parse(c) for c in (model.player.characters or [])],
            joined_on=model.player.joined_on,
            created_first_character_on=model.player.created_first_character_on,
            last_played_on=model.player.last_played_on,
            quests_applied=[QuestID.parse(q) for q in (model.player.quests_applied or [])],
            quests_played=[QuestID.parse(q) for q in (model.player.quests_played or [])],
            summaries_written=[SummaryID.parse(s) for s in (model.player.summaries_written or [])],
            played_with_character=model.player.played_with_character or {},
        )

    referee = None
    if model.referee:
        referee = Referee(
            quests_hosted=[QuestID.parse(q) for q in (model.referee.quests_hosted or [])],
            summaries_written=[SummaryID.parse(s) for s in (model.referee.summaries_written or [])],
            first_dmed_on=model.referee.first_dmed_on,
            last_dmed_on=model.referee.last_dmed_on,
            collabed_with=model.referee.collabed_with or {},
            hosted_for=model.referee.hosted_for or {},
        )

    return User(
        user_id=UserID.parse(model.user_id),
        guild_id=model.guild_id,
        discord_id=model.discord_id,
        dm_channel_id=model.dm_channel_id,
        roles=[Role(r) for r in (model.roles or ["MEMBER"])],
        has_server_tag=model.has_server_tag,
        dm_opt_in=model.dm_opt_in,
        joined_at=model.joined_at,
        last_active_at=model.last_active_at,
        messages_count_total=model.messages_count_total,
        reactions_given=model.reactions_given,
        reactions_received=model.reactions_received,
        voice_total_time_spent=model.voice_total_time_spent,
        player=player,
        referee=referee,
    )


def player_to_orm(player: Player, user_pk: int) -> PlayerModel:
    """Convert domain Player to ORM PlayerModel."""
    return PlayerModel(
        user_pk=user_pk,
        characters=[str(c) for c in player.characters],
        joined_on=player.joined_on,
        created_first_character_on=player.created_first_character_on,
        last_played_on=player.last_played_on,
        quests_applied=[str(q) for q in player.quests_applied],
        quests_played=[str(q) for q in player.quests_played],
        summaries_written=[str(s) for s in player.summaries_written],
        played_with_character={str(k): v for k, v in player.played_with_character.items()},
    )


def referee_to_orm(referee: Referee, user_pk: int) -> RefereeModel:
    """Convert domain Referee to ORM RefereeModel."""
    return RefereeModel(
        user_pk=user_pk,
        quests_hosted=[str(q) for q in referee.quests_hosted],
        summaries_written=[str(s) for s in referee.summaries_written],
        first_dmed_on=referee.first_dmed_on,
        last_dmed_on=referee.last_dmed_on,
        collabed_with={str(k): v for k, v in referee.collabed_with.items()},
        hosted_for={str(k): v for k, v in referee.hosted_for.items()},
    )


# =============================================================================
# Character Mappers
# =============================================================================

def character_to_orm(char: Character) -> CharacterModel:
    """Convert domain Character to ORM CharacterModel."""
    return CharacterModel(
        character_id=str(char.character_id),
        guild_id=char.guild_id,
        owner_id=str(char.owner_id),
        name=char.name,
        status=char.status.value if isinstance(char.status, CharacterRole) else char.status,
        ddb_link=char.ddb_link,
        character_thread_link=char.character_thread_link,
        token_link=char.token_link,
        art_link=char.art_link,
        announcement_channel_id=char.announcement_channel_id,
        announcement_message_id=char.announcement_message_id,
        onboarding_thread_id=char.onboarding_thread_id,
        created_at=char.created_at,
        last_played_at=char.last_played_at,
        quests_played=char.quests_played,
        summaries_written=char.summaries_written,
        description=char.description,
        notes=char.notes,
        tags=char.tags or [],
        played_with=[str(c) for c in (char.played_with or [])],
        played_in=[str(q) for q in (char.played_in or [])],
        mentioned_in=[str(s) for s in (char.mentioned_in or [])],
    )


def character_from_orm(model: CharacterModel) -> Character:
    """Convert ORM CharacterModel to domain Character."""
    return Character(
        character_id=model.character_id,
        guild_id=model.guild_id,
        owner_id=UserID.parse(model.owner_id),
        name=model.name,
        status=CharacterRole(model.status) if model.status else CharacterRole.ACTIVE,
        ddb_link=model.ddb_link,
        character_thread_link=model.character_thread_link,
        token_link=model.token_link,
        art_link=model.art_link,
        announcement_channel_id=model.announcement_channel_id,
        announcement_message_id=model.announcement_message_id,
        onboarding_thread_id=model.onboarding_thread_id,
        created_at=model.created_at,
        last_played_at=model.last_played_at,
        quests_played=model.quests_played,
        summaries_written=model.summaries_written,
        description=model.description,
        notes=model.notes,
        tags=model.tags or [],
        played_with=[CharacterID.parse(c) for c in (model.played_with or [])],
        played_in=[QuestID.parse(q) for q in (model.played_in or [])],
        mentioned_in=[SummaryID.parse(s) for s in (model.mentioned_in or [])],
    )


# =============================================================================
# Quest Mappers
# =============================================================================

def quest_to_orm(quest: Quest) -> QuestModel:
    """Convert domain Quest to ORM QuestModel."""
    return QuestModel(
        quest_id=str(quest.quest_id),
        guild_id=quest.guild_id,
        referee_id=str(quest.referee_id),
        channel_id=quest.channel_id,
        message_id=quest.message_id,
        raw=quest.raw,
        title=quest.title,
        description=quest.description,
        image_url=quest.image_url,
        starting_at=quest.starting_at,
        duration_seconds=int(quest.duration.total_seconds()) if quest.duration else None,
        announce_at=quest.announce_at,
        started_at=quest.started_at,
        ended_at=quest.ended_at,
        last_nudged_at=quest.last_nudged_at,
        status=quest.status.value if isinstance(quest.status, QuestStatus) else quest.status,
        linked_quests=[str(q) for q in (quest.linked_quests or [])],
        linked_summaries=[str(s) for s in (quest.linked_summaries or [])],
    )


def signup_to_orm(signup: PlayerSignUp, quest_pk: int) -> QuestSignupModel:
    """Convert domain PlayerSignUp to ORM QuestSignupModel."""
    return QuestSignupModel(
        quest_pk=quest_pk,
        user_id=str(signup.user_id),
        character_id=str(signup.character_id),
        status=signup.status.value if isinstance(signup.status, PlayerStatus) else signup.status,
    )


def quest_from_orm(model: QuestModel) -> Quest:
    """Convert ORM QuestModel to domain Quest."""
    signups = [
        PlayerSignUp(
            user_id=UserID.parse(s.user_id),
            character_id=CharacterID.parse(s.character_id),
            status=PlayerStatus(s.status) if s.status else PlayerStatus.APPLIED,
        )
        for s in (model.signups or [])
    ]

    return Quest(
        quest_id=QuestID.parse(model.quest_id),
        guild_id=model.guild_id,
        referee_id=UserID.parse(model.referee_id),
        channel_id=model.channel_id,
        message_id=model.message_id,
        raw=model.raw,
        title=model.title,
        description=model.description,
        image_url=model.image_url,
        starting_at=model.starting_at,
        duration=timedelta(seconds=model.duration_seconds) if model.duration_seconds else None,
        announce_at=model.announce_at,
        started_at=model.started_at,
        ended_at=model.ended_at,
        last_nudged_at=model.last_nudged_at,
        status=QuestStatus(model.status) if model.status else QuestStatus.DRAFT,
        linked_quests=[QuestID.parse(q) for q in (model.linked_quests or [])],
        linked_summaries=[SummaryID.parse(s) for s in (model.linked_summaries or [])],
        signups=signups,
    )


# =============================================================================
# Summary Mappers
# =============================================================================

def summary_to_orm(summary: QuestSummary) -> SummaryModel:
    """Convert domain QuestSummary to ORM SummaryModel."""
    return SummaryModel(
        summary_id=str(summary.summary_id),
        guild_id=summary.guild_id,
        kind=summary.kind.value if isinstance(summary.kind, SummaryKind) else summary.kind,
        author_id=str(summary.author_id) if summary.author_id else None,
        character_id=str(summary.character_id) if summary.character_id else None,
        quest_id=str(summary.quest_id) if summary.quest_id else None,
        raw=summary.raw,
        title=summary.title,
        description=summary.description,
        created_on=summary.created_on,
        last_edited_at=summary.last_edited_at,
        players=[str(p) for p in (summary.players or [])],
        characters=[str(c) for c in (summary.characters or [])],
        linked_quests=[str(q) for q in (summary.linked_quests or [])],
        linked_summaries=[str(s) for s in (summary.linked_summaries or [])],
        channel_id=summary.channel_id,
        message_id=summary.message_id,
        thread_id=summary.thread_id,
        status=summary.status.value if isinstance(summary.status, SummaryStatus) else summary.status,
    )


def summary_from_orm(model: SummaryModel) -> QuestSummary:
    """Convert ORM SummaryModel to domain QuestSummary."""
    return QuestSummary(
        summary_id=SummaryID.parse(model.summary_id),
        guild_id=model.guild_id,
        kind=SummaryKind(model.kind) if model.kind else SummaryKind.PLAYER,
        author_id=UserID.parse(model.author_id) if model.author_id else None,
        character_id=CharacterID.parse(model.character_id) if model.character_id else None,
        quest_id=QuestID.parse(model.quest_id) if model.quest_id else None,
        raw=model.raw,
        title=model.title,
        description=model.description,
        created_on=model.created_on,
        last_edited_at=model.last_edited_at,
        players=[UserID.parse(p) for p in (model.players or [])],
        characters=[CharacterID.parse(c) for c in (model.characters or [])],
        linked_quests=[QuestID.parse(q) for q in (model.linked_quests or [])],
        linked_summaries=[SummaryID.parse(s) for s in (model.linked_summaries or [])],
        channel_id=model.channel_id,
        message_id=model.message_id,
        thread_id=model.thread_id,
        status=SummaryStatus(model.status) if model.status else SummaryStatus.POSTED,
    )


# =============================================================================
# Lookup Mappers
# =============================================================================

def lookup_to_orm(entry: LookupEntry) -> LookupModel:
    """Convert domain LookupEntry to ORM LookupModel."""
    return LookupModel(
        guild_id=entry.guild_id,
        name=entry.name,
        name_normalized=LookupEntry.normalize_name(entry.name),
        url=entry.url,
        created_by=entry.created_by,
        created_at=entry.created_at,
        updated_by=entry.updated_by,
        updated_at=entry.updated_at,
        description=entry.description,
    )


def lookup_from_orm(model: LookupModel) -> LookupEntry:
    """Convert ORM LookupModel to domain LookupEntry."""
    return LookupEntry(
        guild_id=model.guild_id,
        name=model.name,
        url=model.url,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_by=model.updated_by,
        updated_at=model.updated_at,
        description=model.description,
    )
