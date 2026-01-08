import os

from dotenv import load_dotenv

load_dotenv()

# PostgreSQL/Supabase configuration (primary)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv("SUPABASE_DB_URL", "postgresql+asyncpg://localhost:5432/nonagon")
)
DB_NAME = os.getenv("DB_NAME", "nonagon")

# SQLAlchemy settings
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
SQL_POOL_SIZE = int(os.getenv("SQL_POOL_SIZE", "5"))
SQL_MAX_OVERFLOW = int(os.getenv("SQL_MAX_OVERFLOW", "10"))
