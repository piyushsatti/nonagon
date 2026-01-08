"""
Bot database layer - PostgreSQL/Supabase using psycopg2 for sync operations.
The bot uses synchronous database operations for its flush loop.
"""
import os
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from nonagon_bot.utils.logging import get_logger
from .config import DATABASE_URL

logger = get_logger(__name__)


def _get_connection_string() -> str:
    """Get the PostgreSQL connection string."""
    url = DATABASE_URL or ""
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Provide DATABASE_URL or SUPABASE_DB_URL in .env."
        )
    # Convert asyncpg URL to psycopg2 format if needed
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


def _make_connection():
    """Create a psycopg2 connection for synchronous operations."""
    url = _get_connection_string()
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


# Create a connection for sync operations
_db_connection: Optional[psycopg2.extensions.connection] = None


def get_connection():
    """Get or create a database connection."""
    global _db_connection
    if _db_connection is None or _db_connection.closed:
        _db_connection = _make_connection()
    return _db_connection


def ping_database() -> bool:
    """Test the database connection."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            logger.info("Pinged PostgreSQL. Connection OK.")
            return result is not None
    except Exception as exc:
        logger.error("PostgreSQL ping failed: %s", exc)
        return False


def close_connection():
    """Close the database connection."""
    global _db_connection
    if _db_connection and not _db_connection.closed:
        _db_connection.close()
        _db_connection = None


# Initialize connection on import
try:
    ping_database()
except Exception as exc:
    logger.warning("Initial database connection failed: %s", exc)

