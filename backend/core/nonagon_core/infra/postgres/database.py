# nonagon_core/infra/postgres/database.py
"""
Async SQLAlchemy database connection for Supabase PostgreSQL.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Load database URL from environment
# Supabase connection string format: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv("SUPABASE_DB_URL", "postgresql+asyncpg://localhost:5432/nonagon")
)

# Ensure we're using asyncpg driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
# Using NullPool for serverless environments like Supabase
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    poolclass=NullPool,  # Better for serverless/Supabase
    connect_args={
        "server_settings": {
            "application_name": "nonagon"
        }
    }
)

# Async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    Use with `async with get_session() as session:`.
    """
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    In production, use Alembic migrations instead.
    """
    from nonagon_core.infra.postgres.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the database engine."""
    await engine.dispose()


async def ping() -> bool:
    """Health check for the database connection."""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except (OSError, ConnectionError) as e:
        print(f"[PostgreSQL Ping Failed] {e}")
        return False
