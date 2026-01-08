import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# PostgreSQL/Supabase database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv("SUPABASE_DB_URL", "postgresql://localhost:5432/nonagon")
)
DB_NAME = os.getenv("DB_NAME", "nonagon")

# Optional: use per-guild adapter for bot flush persistence
BOT_FLUSH_VIA_ADAPTER = os.getenv("BOT_FLUSH_VIA_ADAPTER", "false").lower() in {
    "1",
    "true",
    "yes",
}

# GraphQL API endpoint
GRAPHQL_API_URL = os.getenv("GRAPHQL_API_URL", "http://localhost:8000/graphql")

board_id_raw = os.getenv("QUEST_BOARD_CHANNEL_ID")
try:
    QUEST_BOARD_CHANNEL_ID: Optional[int] = int(board_id_raw) if board_id_raw else None
except ValueError:
    QUEST_BOARD_CHANNEL_ID = None
