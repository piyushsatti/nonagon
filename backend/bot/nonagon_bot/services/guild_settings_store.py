from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from nonagon_bot.database import get_connection

_TABLE_NAME = "guild_settings"


def _ensure_table():
    """Ensure the guild_settings table exists."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id BIGINT PRIMARY KEY,
                settings JSONB NOT NULL DEFAULT '{}',
                configured_by BIGINT,
                configured_at TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
    conn.commit()


def fetch_settings(guild_id: int) -> Optional[Dict[str, Any]]:
    """Return the stored guild settings for the guild, if any."""
    _ensure_table()
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT settings, configured_by, configured_at, updated_at FROM guild_settings WHERE guild_id = %s",
            (int(guild_id),)
        )
        row = cur.fetchone()
    if not row:
        return None
    settings = row["settings"] if isinstance(row["settings"], dict) else json.loads(row["settings"])
    settings["configured_by"] = row.get("configured_by")
    settings["configured_at"] = row.get("configured_at")
    settings["updated_at"] = row.get("updated_at")
    return settings


def save_settings(guild_id: int, data: Dict[str, Any]) -> None:
    """Persist the guild settings document."""
    _ensure_table()
    conn = get_connection()
    now = datetime.now(timezone.utc)
    
    # Extract top-level fields
    configured_by = data.pop("configured_by", None)
    configured_at = data.pop("configured_at", None)
    data.pop("updated_at", None)  # Will be set automatically
    data.pop("guild_id", None)  # Stored separately
    
    settings_json = json.dumps(data)
    
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO guild_settings (guild_id, settings, configured_by, configured_at, updated_at)
            VALUES (%s, %s::jsonb, %s, %s, %s)
            ON CONFLICT (guild_id) DO UPDATE SET
                settings = EXCLUDED.settings,
                configured_by = COALESCE(EXCLUDED.configured_by, guild_settings.configured_by),
                configured_at = COALESCE(guild_settings.configured_at, EXCLUDED.configured_at),
                updated_at = EXCLUDED.updated_at
        """, (int(guild_id), settings_json, configured_by, configured_at, now))
    conn.commit()


def delete_settings(guild_id: int) -> bool:
    """Delete the guild settings document. Returns True if one existed."""
    result = _collection(guild_id).delete_one({"_id": _DOCUMENT_ID})
    return result.deleted_count == 1
