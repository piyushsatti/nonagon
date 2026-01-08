# ⚠️ Legacy Notice: Discord Bot

> **Status:** Legacy / Pending Migration  
> **Last Updated:** January 2026

## Overview

The Discord bot (`nonagon_bot`) is currently **behind the main API migration** and requires future work to align with the new architecture.

## Current State

The bot was designed to communicate with the backend via **REST API endpoints** at `QUEST_API_BASE_URL`. These REST endpoints have been **removed** in favor of the new **GraphQL API**.

### Affected Components

| File | Issue |
|------|-------|
| `cogs/QuestCommandsCog.py` | Uses REST calls (`_signup_via_api`, `_remove_signup_via_api`, etc.) |
| `config.py` | References `QUEST_API_BASE_URL` (deprecated) |
| `database.py` | Uses direct MongoDB/PostgreSQL sync operations |

### REST Methods to Migrate

The following methods in `QuestCommandsCog.py` need to be updated:

- `_signup_via_api()` → GraphQL `addQuestSignup` mutation
- `_remove_signup_via_api()` → GraphQL `removeQuestSignup` mutation  
- `_select_signup_via_api()` → GraphQL `selectQuestSignup` mutation
- `_nudge_via_api()` → GraphQL `nudgeQuest` mutation
- `_close_signups_via_api()` → GraphQL `closeQuestSignups` mutation

## Migration Options

### Option 1: GraphQL Client (Recommended)

Use `gql` or `httpx` to call the GraphQL API:

```python
import httpx

GRAPHQL_URL = os.getenv("GRAPHQL_API_URL", "http://localhost:8000/graphql")

async def signup_via_graphql(guild_id: int, quest_id: str, user_id: str, character_id: str):
    query = """
    mutation AddSignup($guildId: Int!, $questId: String!, $input: QuestSignupInput!) {
        addQuestSignup(guildId: $guildId, questId: $questId, input: $input) {
            id
            signups { userId characterId }
        }
    }
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GRAPHQL_URL,
            json={
                "query": query,
                "variables": {
                    "guildId": guild_id,
                    "questId": quest_id,
                    "input": {"userId": user_id, "characterId": character_id}
                }
            }
        )
        return response.json()
```

### Option 2: Direct PostgreSQL Repository

Import and use the PostgreSQL repositories directly (faster, no network hop):

```python
from nonagon_core.infra.postgres.quests_repo import QuestsRepository

quests_repo = QuestsRepository()

async def signup_direct(guild_id: int, quest_id: str, signup: QuestSignup):
    quest = await quests_repo.get(guild_id, quest_id)
    quest.signups.append(signup)
    await quests_repo.upsert(quest)
```

## Future Work

1. **Remove `QUEST_API_BASE_URL`** from `config.py`
2. **Update `QuestCommandsCog.py`** to use GraphQL or direct repos
3. **Update `database.py`** to use async PostgreSQL (`asyncpg`)
4. **Add integration tests** for bot ↔ API communication
5. **Update Docker compose** bot service environment variables

## Timeline

| Task | Priority | Estimate |
|------|----------|----------|
| Migrate quest signup flows | High | 2-3 hours |
| Remove deprecated config | Medium | 30 min |
| Add GraphQL client helper | Medium | 1 hour |
| Update database layer | Low | 2-4 hours |

---

*This bot remains functional via fallback to direct database writes, but should be migrated for consistency with the GraphQL-first architecture.*
