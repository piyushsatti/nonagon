## Architecture Snapshot
- Multi-service Python 3.11 project: FastAPI API (`backend/api`) and discord.py bot (`backend/bot`) share domain models under `backend/core/nonagon_core/domain`.
- Domain entities are dataclasses (e.g. `domain/models/QuestModel.py`, `UserModel.py`) with explicit `validate_*` methods; run them before persisting or mutating caches.
- All persistent models require `guild_id`; repositories and bot caches rely on it, so set/propagate the guild on every write path.
- IDs use `EntityIDModel` subclasses (`UserID`, `QuestID`, `CharacterID`, `SummaryID`); parse with `.parse(...)` and serialize via `str(id)` to preserve readable prefixes.

## Persistence & Repos
- PostgreSQL access via SQLAlchemy async repos in `infra/postgres/*_repo.py` (e.g., `UsersRepoPostgres`, `QuestsRepoPostgres`, `CharactersRepoPostgres`, `SummariesRepoPostgres`).
- Each repo has async methods: `upsert`, `get`, `delete`, `exists`, `next_id`; use these in cogs and routers.
- Bot-side sync writes use `infra/postgres/guild_adapter.py` with `upsert_*_sync` functions (psycopg2-based for the flush loop).
- ID generation uses collision-checked postal IDs via repo `next_id()` methods—always await them as they're async.
- Tests monkeypatch module-level singletons (e.g. `api/routers/quests.py`'s `quests_repo`) to isolate datastore behavior; follow that approach for new routers.

## Discord Bot Workflow
- `bot/main.py` bootstraps cogs, manages per-guild caches in `bot.guild_data`, and flushes dirty users via `_auto_persist_loop`; enqueue `(guild_id, user_id)` whenever cached users change.
- Bot caches store `{"users": {...}}` per guild—no database handles stored in cache.
- `ListnerCog` helpers like `_ensure_cached_user` / `_resolve_cached_user` seed cache entries from gateway events—reuse them instead of duplicating Discord member lookups.
- Quest flows in `bot/cogs/QuestCommandsCog.py` use PostgreSQL repos for persistence and `QuestSignupView` infers IDs from embed footers formatted as `Quest ID: …`.
- Embed rendering is centralized in `bot/utils/quest_embeds.py`; extend `QuestEmbedData` / `QuestEmbedRoster` so footers stay parseable by signup views.

## API Patterns
- FastAPI entrypoint is `api/main.py` with Strawberry GraphQL at `/graphql`.
- GraphQL resolvers under `api/graphql/resolvers.py` transform domain instances via `api/graphql/converters.py`.
- `_persist_quest` runs `Quest.validate_quest()` prior to `quests_repo.upsert`; mirror that guardrail for new quest operations.
- All operations are guild-scoped and raise appropriate errors when invariants fail.

## Dev Workflow & Tooling
- PostgreSQL via Docker: `make db-up` starts database, `make db-down` stops it.
- Local install: `python -m pip install -e .[dev]`; run tests with `python -m pytest` (`pytest.ini` sets `asyncio_mode=auto` and session-scoped loops).
- Start the API with `uvicorn nonagon_api.main:app --reload --port 8000`.
- The bot in `bot/main.py` requires valid `BOT_TOKEN` / `BOT_CLIENT_ID` and configured Discord intents.
- Logs land under `./logs` for both services; startup code already guards against missing directories—maintain that convention on new handlers.
- Quest interactions emit telemetry through `bot/utils/logging.audit`; keep those calls when refactoring to preserve demo analytics.
- Environment variables: `DATABASE_URL` for PostgreSQL, `API_URL` for frontend GraphQL endpoint.
