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

# Legacy MongoDB configuration (deprecated, kept for migration)
MONGODB_URI = os.getenv("MONGODB_URI", "")

MONGO_OP_TIMEOUT_MS = int(os.getenv("MONGO_OP_TIMEOUT_MS", "5000"))
MONGO_SERVER_SELECTION_TIMEOUT_MS = int(
    os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000")
)
MONGO_APPNAME = os.getenv("MONGO_APPNAME", "nonagon")
