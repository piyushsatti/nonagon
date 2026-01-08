# Nonagon

Nonagon is a multi-guild Discord automation platform that streamlines quest scheduling, player sign-ups, summaries, and engagement analytics. It bundles a Discord bot with a FastAPI service so community teams can monitor activity and keep adventures moving.

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | Python 3.11+, FastAPI, Uvicorn, Motor (async MongoDB) |
| Bot | Python 3.11+, discord.py, PyMongo |
| Frontend | Next.js 14, React, TypeScript |
| Database | MongoDB 7+ |
| Schemas | JSON Schema (source of truth) |
| Dev Tools | uv, Ruff, pytest, Docker Compose |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- MongoDB 7+ (local or Atlas)
- Docker & Docker Compose (optional, for containerized runs)

### 1. Clone & Install

```bash
git clone https://github.com/your-org/nonagon.git
cd nonagon

# Backend (creates backend/.venv automatically)
cd backend
uv sync --all-extras
source .venv/bin/activate
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 2. Environment Variables

Create a `.env` file in the repository root:

```dotenv
# MongoDB
ATLAS_URI=mongodb://localhost:27017
DB_NAME=nonagon

# Discord Bot
BOT_TOKEN=your-discord-bot-token
BOT_CLIENT_ID=your-discord-client-id

# Optional overrides
MONGO_URI=           # Bot uses this → falls back to ATLAS_URI
MONGODB_URI=         # API uses this → falls back to ATLAS_URI
```

### 3. Run Services

**Option A: Make commands (recommended for development)**

```bash
make install      # Install all dependencies
make api          # Start API server (port 8000)
make bot          # Start Discord bot (separate terminal)
make frontend     # Start Next.js dev server (port 3000)
```

**Option B: Docker Compose (production-like)**

```bash
docker compose up --build
```

### 4. Verify Installation

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:3000](http://localhost:3000)
- Health check: `curl http://localhost:8000/health`

## Project Structure

```
nonagon/
├── backend/
│   ├── pyproject.toml       # Single config for all backend packages
│   ├── .venv/               # Python virtual environment
│   ├── core/                # Shared domain & infrastructure
│   │   └── nonagon_core/
│   │       ├── domain/      # Models, entities, use cases
│   │       └── infra/       # Database, repositories, serialization
│   ├── api/                 # FastAPI service
│   │   └── nonagon_api/
│   │       ├── routers/     # REST endpoints
│   │       ├── schemas.py   # Pydantic request/response models
│   │       └── mappers.py   # Domain ↔ API transformations
│   └── bot/                 # Discord bot
│       └── nonagon_bot/
│           ├── cogs/        # Command groups
│           ├── services/    # Business logic
│           └── utils/       # Helpers, embeds
├── frontend/
│   ├── package.json
│   ├── node_modules/
│   └── src/
│       ├── app/             # Next.js App Router pages
│       ├── api/             # API client
│       └── types/generated/ # TypeScript types from JSON Schema
├── shared/
│   └── schemas/             # JSON Schema (source of truth)
│       ├── common.schema.json
│       ├── quest.schema.json
│       └── ...
├── scripts/
│   ├── generate-types.sh    # Generate Pydantic + TS types
│   └── validate-schemas.sh  # Validate JSON Schema files
├── tests/                   # All tests
├── docs/                    # Documentation
├── docker-compose.yml
└── Makefile
```

## Make Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies (backend + frontend) |
| `make api` | Start FastAPI server with hot reload |
| `make bot` | Start Discord bot |
| `make frontend` | Start Next.js development server |
| `make test` | Run all tests |
| `make lint` | Run Ruff linter |
| `make format` | Format code with Ruff |
| `make generate` | Generate types from JSON Schema |
| `make validate-schemas` | Validate JSON Schema files |
| `make docker-up` | Start all services via Docker Compose |
| `make docker-down` | Stop Docker Compose services |
| `make clean` | Remove build artifacts and caches |

## Development Workflow

### Type Generation

JSON Schema files in `shared/schemas/` are the source of truth. Generate types after schema changes:

```bash
make generate
```

This generates:
- Python Pydantic models → `backend/api/nonagon_api/generated/`
- TypeScript types → `frontend/src/types/generated/`

### Running Tests

```bash
make test                    # All tests
pytest tests/domain/         # Domain tests only
pytest tests/api/            # API tests only
pytest -k "quest"            # Tests matching "quest"
```

### Code Style

- **Python**: Ruff for linting and formatting (tabs for indentation)
- **TypeScript**: ESLint + Prettier
- Pre-commit hooks enforce style on commit

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Discord Bot Setup

After inviting the bot to a guild:

1. Run `/setup` to create default roles and channels
2. Use `/setup_status` to verify configuration
3. Use `/setup_reset` to clear settings if needed

Required bot permissions:
- Send Messages
- Embed Links
- Add Reactions
- Manage Roles (for Quest Manager role)
- Read Message History

## API Documentation

Interactive API docs are available at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

All API routes are guild-scoped: `/v1/guilds/{guild_id}/...`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code style, and PR process.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
