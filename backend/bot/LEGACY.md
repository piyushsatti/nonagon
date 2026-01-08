# ✅ Migration Complete: Discord Bot

> **Status:** Migrated  
> **Last Updated:** January 2026

## Overview

The Discord bot (`nonagon_bot`) has been migrated from MongoDB/REST to PostgreSQL/GraphQL.

## Completed Changes

### Database Layer
- ✅ Replaced `UsersRepoMongo` with `UsersRepoPostgres` in all cogs
- ✅ Replaced `LookupRepoMongo` with `LookupRepoPostgres`
- ✅ Created `infra/postgres/guild_adapter.py` for sync upsert operations
- ✅ Bot uses psycopg2 for sync flush operations

### API Communication
- ✅ Added `services/graphql_client.py` with GraphQL mutations for quest operations
- ✅ Removed `QUEST_API_BASE_URL` config (REST is deprecated)
- ✅ Bot now uses `GRAPHQL_API_URL` for API calls

### Removed Legacy Code
- ✅ Removed `MONGO_URI` from config
- ✅ Removed MongoDB imports from all cogs
- ✅ Removed `to_bson`/`from_bson` serialization imports

## GraphQL Client Usage

The bot can now use the GraphQL client for quest operations:

```python
from nonagon_bot.services.graphql_client import (
    signup_quest,
    remove_signup,
    select_signup,
    nudge_quest,
    close_signups,
)

# Add a signup
await signup_quest(guild_id, quest_id, user_id, character_id)

# Remove a signup
await remove_signup(guild_id, quest_id, user_id)

# Select/accept a signup
await select_signup(guild_id, quest_id, user_id)
```

## Files Changed

| File | Change |
|------|--------|
| `cogs/QuestCommandsCog.py` | PostgreSQL repos + removed REST imports |
| `cogs/SetupCommandsCog.py` | UsersRepoPostgres |
| `cogs/CharacterCommandsCog.py` | Postgres guild_adapter |
| `cogs/SummaryCommandsCog.py` | UsersRepoPostgres |
| `cogs/LookupCommandsCog.py` | LookupRepoPostgres |
| `main.py` | Postgres guild_adapter |
| `services/user_registry.py` | UsersRepoPostgres |
| `services/graphql_client.py` | New GraphQL client |
| `config.py` | Removed MONGO_URI, QUEST_API_BASE_URL |

*This bot remains functional via fallback to direct database writes, but should be migrated for consistency with the GraphQL-first architecture.*
