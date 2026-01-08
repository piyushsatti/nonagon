# Nonagon

Nonagon is a multi-guild Discord automation platform that streamlines quest scheduling, player sign-ups, summaries, and engagement analytics. It bundles a Discord bot with a FastAPI/GraphQL service so community teams can monitor activity and keep adventures moving.

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | Python 3.11+, FastAPI, Strawberry GraphQL, SQLAlchemy |
| Bot | Python 3.11+, discord.py, psycopg2 |
| Frontend | React 18, Parcel, graphql-request |
| Database | PostgreSQL 16+ (via Docker or Supabase) |
| Schemas | JSON Schema (source of truth) |
| Dev Tools | pip, Ruff, pytest, Docker (for database) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for PostgreSQL database)

### 1. Clone & Install

```bash
git clone https://github.com/your-org/nonagon.git
cd nonagon

# Install Python dependencies
pip install -e ".[dev]"

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### 2. Start Database

```bash
make db-up  # Starts PostgreSQL in Docker
```

### 3. Environment Variables

Copy `.env.example` to `.env` and configure:

```dotenv
# Database (local Docker PostgreSQL)
DATABASE_URL=postgresql+asyncpg://nonagon:nonagon@localhost:5432/nonagon

# Discord Bot
BOT_TOKEN=your-discord-bot-token
BOT_CLIENT_ID=your-discord-client-id

# API URL (for frontend)
API_URL=http://localhost:8000
```

### 4. Run Services

```bash
# Terminal 1: API server
make api

# Terminal 2: Discord bot (requires BOT_TOKEN)
make bot

# Terminal 3: Frontend
make frontend
```

Or run all in parallel:
```bash
make dev
```

### 5. Verify Installation

- GraphQL Playground: [http://localhost:8000/graphql](http://localhost:8000/graphql)
- Frontend: [http://localhost:1234](http://localhost:1234)
- Health check: `curl http://localhost:8000/healthz`

## Project Structure

```
nonagon/
├── backend/
│   ├── core/                # Shared domain & infrastructure
│   │   └── nonagon_core/
│   │       ├── domain/      # Models, entities, use cases
│   │       └── infra/       # PostgreSQL repos, serialization
│   ├── api/                 # FastAPI + GraphQL service
│   │   └── nonagon_api/
│   │       ├── graphql/     # Strawberry schema, resolvers
│   │       └── generated/   # Generated Pydantic models
│   └── bot/                 # Discord bot
│       └── nonagon_bot/
│           ├── cogs/        # Command groups
│           ├── services/    # Business logic, GraphQL client
│           └── utils/       # Helpers, embeds
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api/             # GraphQL client
│       ├── components/      # React components
│       ├── pages/           # Page components
│       └── types/           # (no JSON Schema codegen)
├── shared/
│   └── schemas/             # JSON Schema (source of truth)
├── scripts/
│   ├── (removed)            # JSON Schema generation scripts removed
│   └── migrations/          # Database migrations
├── tests/                   # All tests
├── docs/                    # Documentation
├── docker-compose.yml       # PostgreSQL database only
├── pyproject.toml           # Python project config
└── Makefile
```

## Make Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies (backend + frontend) |
| `make api` | Start FastAPI/GraphQL server with hot reload |
| `make bot` | Start Discord bot |
| `make frontend` | Start Parcel development server |
| `make dev` | Start all services in parallel |
| `make db-up` | Start PostgreSQL database (Docker) |
| `make db-down` | Stop PostgreSQL database |
| `make db-reset` | Reset database (destroys all data) |
| `make test` | Run all tests |
| `make lint` | Run Ruff linter |
| `make format` | Format code with Ruff |
| `make generate` | Generate types from JSON Schema |
| `make clean` | Remove build artifacts and caches |

## Development Workflow

### Type Generation

JSON Schema code generation has been removed. GraphQL is the source of truth for API contracts.

```bash
make generate
```

This generates:
- Python Pydantic models → `backend/api/nonagon_api/generated/`
- TypeScript types → consider GraphQL codegen or handwritten types under `frontend/src/types/`

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

Interactive GraphQL playground is available at:
- GraphQL Playground: [http://localhost:8000/graphql](http://localhost:8000/graphql)

All GraphQL queries/mutations are guild-scoped via the `guildId` parameter.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code style, and PR process.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
