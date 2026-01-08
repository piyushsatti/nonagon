# nonagon_core/infra/postgres/guild_adapter.py
"""
Synchronous PostgreSQL adapter for bot flush operations.

The bot's flush loop runs sync code with psycopg2, so these functions
provide sync database access for user/quest/character persistence.
"""
from __future__ import annotations

import json
import os
from datetime import timedelta
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from nonagon_bot.core.domain.models.CharacterModel import Character, CharacterRole
from nonagon_bot.core.domain.models.QuestModel import Quest, QuestStatus
from nonagon_bot.core.domain.models.SummaryModel import QuestSummary, SummaryKind, SummaryStatus
from nonagon_bot.core.domain.models.UserModel import User


def _get_connection_string() -> str:
    """Get the PostgreSQL connection string for sync operations."""
    url = os.getenv(
        "DATABASE_URL",
        os.getenv("SUPABASE_DB_URL", "postgresql://localhost:5432/nonagon")
    )
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Provide DATABASE_URL or SUPABASE_DB_URL in .env."
        )
    # Convert asyncpg URL to psycopg2 format if needed
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


_sync_connection: Optional[psycopg2.extensions.connection] = None


def _get_sync_connection():
    """Get or create a psycopg2 connection for sync operations."""
    global _sync_connection
    if _sync_connection is None or _sync_connection.closed:
        _sync_connection = psycopg2.connect(
            _get_connection_string(),
            cursor_factory=RealDictCursor
        )
    return _sync_connection


def upsert_user_sync(guild_id: int, user: User) -> None:
    """
    Upsert a user record synchronously using PostgreSQL.
    """
    conn = _get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (
                    guild_id, user_id, discord_id, dm_channel_id, roles,
                    has_server_tag, dm_opt_in, joined_at, last_active_at,
                    messages_count_total, reactions_given, reactions_received,
                    voice_total_time_spent
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (guild_id, user_id) DO UPDATE SET
                    discord_id = EXCLUDED.discord_id,
                    dm_channel_id = EXCLUDED.dm_channel_id,
                    roles = EXCLUDED.roles,
                    has_server_tag = EXCLUDED.has_server_tag,
                    dm_opt_in = EXCLUDED.dm_opt_in,
                    joined_at = EXCLUDED.joined_at,
                    last_active_at = EXCLUDED.last_active_at,
                    messages_count_total = EXCLUDED.messages_count_total,
                    reactions_given = EXCLUDED.reactions_given,
                    reactions_received = EXCLUDED.reactions_received,
                    voice_total_time_spent = EXCLUDED.voice_total_time_spent
                """,
                (
                    int(guild_id),
                    str(user.user_id),
                    user.discord_id,
                    user.dm_channel_id,
                    [r.value for r in user.roles],
                    user.has_server_tag,
                    user.dm_opt_in,
                    user.joined_at,
                    user.last_active_at,
                    user.messages_count_total,
                    user.reactions_given,
                    user.reactions_received,
                    int(user.voice_total_time_spent.total_seconds()) if isinstance(user.voice_total_time_spent, timedelta) else user.voice_total_time_spent,
                )
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def upsert_quest_sync(guild_id: int, quest: Quest) -> None:
    """
    Upsert a quest record synchronously using PostgreSQL.
    """
    conn = _get_sync_connection()
    try:
        with conn.cursor() as cur:
            # Serialize signups to JSON
            signups_json = json.dumps([
                {
                    "user_id": str(s.user_id),
                    "character_id": str(s.character_id),
                    "status": s.status.value if hasattr(s.status, 'value') else str(s.status),
                }
                for s in (quest.signups or [])
            ])
            
            cur.execute(
                """
                INSERT INTO quests (
                    guild_id, quest_id, referee_id, channel_id, message_id,
                    title, description, starting_at, duration_hours, image_url,
                    status, announce_at, started_at, ended_at, is_signup_open,
                    signups
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s::jsonb
                )
                ON CONFLICT (guild_id, quest_id) DO UPDATE SET
                    referee_id = EXCLUDED.referee_id,
                    channel_id = EXCLUDED.channel_id,
                    message_id = EXCLUDED.message_id,
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    starting_at = EXCLUDED.starting_at,
                    duration_hours = EXCLUDED.duration_hours,
                    image_url = EXCLUDED.image_url,
                    status = EXCLUDED.status,
                    announce_at = EXCLUDED.announce_at,
                    started_at = EXCLUDED.started_at,
                    ended_at = EXCLUDED.ended_at,
                    is_signup_open = EXCLUDED.is_signup_open,
                    signups = EXCLUDED.signups
                """,
                (
                    int(guild_id),
                    str(quest.quest_id),
                    str(quest.referee_id) if quest.referee_id else None,
                    quest.channel_id,
                    quest.message_id,
                    quest.title,
                    quest.description,
                    quest.starting_at,
                    quest.duration.total_seconds() / 3600 if isinstance(quest.duration, timedelta) else quest.duration,
                    quest.image_url,
                    quest.status.value if isinstance(quest.status, QuestStatus) else quest.status,
                    quest.announce_at,
                    quest.started_at,
                    quest.ended_at,
                    quest.is_signup_open,
                    signups_json,
                )
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def upsert_character_sync(guild_id: int, character: Character) -> None:
    """
    Upsert a character record synchronously using PostgreSQL.
    """
    conn = _get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO characters (
                    guild_id, character_id, owner_id, name, status,
                    ddb_link, character_thread_link, token_link, art_link,
                    description, notes, tags, created_at, last_played_at,
                    quests_played, summaries_written
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )
                ON CONFLICT (guild_id, character_id) DO UPDATE SET
                    owner_id = EXCLUDED.owner_id,
                    name = EXCLUDED.name,
                    status = EXCLUDED.status,
                    ddb_link = EXCLUDED.ddb_link,
                    character_thread_link = EXCLUDED.character_thread_link,
                    token_link = EXCLUDED.token_link,
                    art_link = EXCLUDED.art_link,
                    description = EXCLUDED.description,
                    notes = EXCLUDED.notes,
                    tags = EXCLUDED.tags,
                    last_played_at = EXCLUDED.last_played_at,
                    quests_played = EXCLUDED.quests_played,
                    summaries_written = EXCLUDED.summaries_written
                """,
                (
                    int(guild_id),
                    str(character.character_id),
                    str(character.owner_id) if character.owner_id else None,
                    character.name,
                    character.status.value if isinstance(character.status, CharacterRole) else character.status,
                    character.ddb_link,
                    character.character_thread_link,
                    character.token_link,
                    character.art_link,
                    character.description,
                    character.notes,
                    character.tags or [],
                    character.created_at,
                    character.last_played_at,
                    character.quests_played or 0,
                    character.summaries_written or 0,
                )
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def close_sync_connection() -> None:
    """Close the sync connection (for cleanup)."""
    global _sync_connection
    if _sync_connection and not _sync_connection.closed:
        _sync_connection.close()
        _sync_connection = None


def upsert_summary_sync(guild_id: int, summary: QuestSummary) -> None:
    """
    Upsert a summary record synchronously using PostgreSQL.
    """
    conn = _get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO summaries (
                    guild_id, summary_id, kind, author_id, character_id,
                    quest_id, raw, title, description, created_on,
                    last_edited_at, players, characters, linked_quests,
                    linked_summaries, channel_id, message_id, thread_id, status
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT (guild_id, summary_id) DO UPDATE SET
                    kind = EXCLUDED.kind,
                    author_id = EXCLUDED.author_id,
                    character_id = EXCLUDED.character_id,
                    quest_id = EXCLUDED.quest_id,
                    raw = EXCLUDED.raw,
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    last_edited_at = EXCLUDED.last_edited_at,
                    players = EXCLUDED.players,
                    characters = EXCLUDED.characters,
                    linked_quests = EXCLUDED.linked_quests,
                    linked_summaries = EXCLUDED.linked_summaries,
                    channel_id = EXCLUDED.channel_id,
                    message_id = EXCLUDED.message_id,
                    thread_id = EXCLUDED.thread_id,
                    status = EXCLUDED.status
                """,
                (
                    int(guild_id),
                    str(summary.summary_id),
                    summary.kind.value if isinstance(summary.kind, SummaryKind) else summary.kind,
                    str(summary.author_id) if summary.author_id else None,
                    str(summary.character_id) if summary.character_id else None,
                    str(summary.quest_id) if summary.quest_id else None,
                    summary.raw,
                    summary.title,
                    summary.description,
                    summary.created_on,
                    summary.last_edited_at,
                    [str(p) for p in (summary.players or [])],
                    [str(c) for c in (summary.characters or [])],
                    [str(q) for q in (summary.linked_quests or [])],
                    [str(s) for s in (summary.linked_summaries or [])],
                    summary.channel_id,
                    summary.message_id,
                    summary.thread_id,
                    summary.status.value if isinstance(summary.status, SummaryStatus) else summary.status,
                )
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
