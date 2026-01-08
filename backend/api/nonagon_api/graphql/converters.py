# nonagon_api/graphql/converters.py
"""
Converters between domain models and GraphQL types.
"""
from __future__ import annotations

from nonagon_bot.core.domain.models.CharacterModel import Character as DCharacter
from nonagon_bot.core.domain.models.CharacterModel import CharacterRole
from nonagon_bot.core.domain.models.LookupModel import LookupEntry as DLookupEntry
from nonagon_bot.core.domain.models.QuestModel import PlayerStatus, Quest as DQuest
from nonagon_bot.core.domain.models.QuestModel import QuestStatus as DQuestStatus
from nonagon_bot.core.domain.models.SummaryModel import QuestSummary as DSummary
from nonagon_bot.core.domain.models.SummaryModel import SummaryKind as DSummaryKind
from nonagon_bot.core.domain.models.SummaryModel import SummaryStatus as DSummaryStatus
from nonagon_bot.core.domain.models.UserModel import User as DUser

from nonagon_api.graphql.types import (
    Character,
    CharacterStatus,
    LookupEntry,
    Player,
    PlayerSignup,
    PlayerSignupStatus,
    Quest,
    QuestStatus,
    Referee,
    Summary,
    SummaryKind,
    SummaryStatus,
    User,
    UserRole,
)


def domain_user_to_gql(user: DUser) -> User:
    """Convert domain User to GraphQL User type."""
    player = None
    if user.player:
        player = Player(
            characters=[str(c) for c in user.player.characters],
            joined_on=user.player.joined_on,
            created_first_character_on=user.player.created_first_character_on,
            last_played_on=user.player.last_played_on,
            quests_applied=[str(q) for q in user.player.quests_applied],
            quests_played=[str(q) for q in user.player.quests_played],
            summaries_written=[str(s) for s in user.player.summaries_written],
        )

    referee = None
    if user.referee:
        referee = Referee(
            quests_hosted=[str(q) for q in user.referee.quests_hosted],
            summaries_written=[str(s) for s in user.referee.summaries_written],
            first_dmed_on=user.referee.first_dmed_on,
            last_dmed_on=user.referee.last_dmed_on,
        )

    return User(
        user_id=str(user.user_id),
        guild_id=user.guild_id,
        discord_id=user.discord_id,
        dm_channel_id=user.dm_channel_id,
        roles=[UserRole(r.value) for r in user.roles],
        has_server_tag=user.has_server_tag,
        dm_opt_in=user.dm_opt_in,
        joined_at=user.joined_at,
        last_active_at=user.last_active_at,
        messages_count_total=user.messages_count_total,
        reactions_given=user.reactions_given,
        reactions_received=user.reactions_received,
        voice_total_time_spent=user.voice_total_time_spent,
        player=player,
        referee=referee,
    )


def domain_character_to_gql(char: DCharacter) -> Character:
    """Convert domain Character to GraphQL Character type."""
    status = CharacterStatus.ACTIVE
    if isinstance(char.status, CharacterRole):
        status = CharacterStatus(char.status.value)
    elif isinstance(char.status, str):
        status = CharacterStatus(char.status)

    return Character(
        character_id=str(char.character_id),
        guild_id=char.guild_id,
        owner_id=str(char.owner_id),
        name=char.name,
        status=status,
        ddb_link=char.ddb_link,
        character_thread_link=char.character_thread_link,
        token_link=char.token_link,
        art_link=char.art_link,
        description=char.description,
        notes=char.notes,
        tags=char.tags or [],
        created_at=char.created_at,
        last_played_at=char.last_played_at,
        quests_played=char.quests_played,
        summaries_written=char.summaries_written,
        played_with=[str(c) for c in (char.played_with or [])],
        played_in=[str(q) for q in (char.played_in or [])],
        mentioned_in=[str(s) for s in (char.mentioned_in or [])],
    )


def domain_quest_to_gql(quest: DQuest) -> Quest:
    """Convert domain Quest to GraphQL Quest type."""
    status = QuestStatus.DRAFT
    if isinstance(quest.status, DQuestStatus):
        status = QuestStatus(quest.status.value)
    elif isinstance(quest.status, str):
        status = QuestStatus(quest.status)

    signups = []
    for s in quest.signups:
        signup_status = PlayerSignupStatus.APPLIED
        if isinstance(s.status, PlayerStatus):
            signup_status = PlayerSignupStatus(s.status.value)
        signups.append(PlayerSignup(
            user_id=str(s.user_id),
            character_id=str(s.character_id),
            status=signup_status,
        ))

    duration_hours = None
    if quest.duration:
        duration_hours = int(quest.duration.total_seconds() // 3600)

    return Quest(
        quest_id=str(quest.quest_id),
        guild_id=quest.guild_id,
        referee_id=str(quest.referee_id),
        channel_id=quest.channel_id,
        message_id=quest.message_id,
        raw=quest.raw,
        title=quest.title,
        description=quest.description,
        starting_at=quest.starting_at,
        duration_hours=duration_hours,
        image_url=quest.image_url,
        status=status,
        announce_at=quest.announce_at,
        started_at=quest.started_at,
        ended_at=quest.ended_at,
        last_nudged_at=quest.last_nudged_at,
        signups=signups,
        linked_quests=[str(q) for q in (quest.linked_quests or [])],
        linked_summaries=[str(s) for s in (quest.linked_summaries or [])],
    )


def domain_summary_to_gql(summary: DSummary) -> Summary:
    """Convert domain QuestSummary to GraphQL Summary type."""
    kind = SummaryKind.PLAYER
    if isinstance(summary.kind, DSummaryKind):
        kind = SummaryKind(summary.kind.value)

    status = SummaryStatus.POSTED
    if isinstance(summary.status, DSummaryStatus):
        status = SummaryStatus(summary.status.value)

    return Summary(
        summary_id=str(summary.summary_id),
        guild_id=summary.guild_id,
        kind=kind,
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
        status=status,
    )


def domain_lookup_to_gql(entry: DLookupEntry) -> LookupEntry:
    """Convert domain LookupEntry to GraphQL LookupEntry type."""
    return LookupEntry(
        guild_id=entry.guild_id,
        name=entry.name,
        url=entry.url,
        created_by=entry.created_by,
        created_at=entry.created_at,
        updated_by=entry.updated_by,
        updated_at=entry.updated_at,
        description=entry.description,
    )
