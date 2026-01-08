# Contributing to Nonagon

Thank you for your interest in contributing to Nonagon! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## Getting Started

### Development Environment Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/nonagon.git
   cd nonagon
   ```

2. **Install dependencies**

   ```bash
   # Backend
   cd backend
   uv sync --all-extras
   source .venv/bin/activate
   cd ..

   # Frontend
   cd frontend
   npm install
   cd ..

   # Pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

3. **Set up environment variables**

   Copy `.env.example` to `.env` and fill in the required values (see README.md).

4. **Start services**

   ```bash
   make api       # Terminal 1
   make bot       # Terminal 2
   make frontend  # Terminal 3
   ```

## Code Style

### Python

- **Indentation**: Tabs (not spaces) for Python files
- **Linting**: Ruff (configured in `pyproject.toml`)
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for modules, classes, and public functions

```python
def calculate_xp(base_xp: int, multiplier: float = 1.0) -> int:
	"""Calculate experience points with optional multiplier.

	Args:
		base_xp: The base experience points to award.
		multiplier: Optional multiplier for bonus XP.

	Returns:
		The calculated experience points.

	Raises:
		ValueError: If base_xp is negative.
	"""
	if base_xp < 0:
		raise ValueError("base_xp cannot be negative")
	return int(base_xp * multiplier)
```

### TypeScript

- **Indentation**: Tabs
- **Linting**: ESLint with Prettier
- **Types**: Explicit types preferred, avoid `any`

### Configuration Files

- YAML, JSON, TOML: 2 spaces for indentation

### Pre-commit Hooks

Pre-commit hooks automatically run on commit:

```bash
pre-commit run --all-files  # Run manually
```

Hooks include:
- Ruff linting and formatting
- Trailing whitespace removal
- End-of-file fixer
- JSON/YAML validation

## Testing

### Running Tests

```bash
make test                    # All tests
pytest tests/domain/         # Domain tests
pytest tests/api/            # API tests
pytest tests/bot/            # Bot tests
pytest -k "quest"            # Pattern matching
pytest -v                    # Verbose output
pytest --cov                 # With coverage
```

### Writing Tests

- Place tests in the appropriate `tests/` subdirectory
- Use `pytest` fixtures for setup/teardown
- Mock external dependencies (Discord API, MongoDB)
- Aim for >80% coverage on new code

```python
import pytest
from nonagon_core.domain.models.quest_model import Quest

class TestQuestModel:
	def test_create_quest_with_valid_data(self):
		quest = Quest(
			guild_id="123",
			title="Test Quest",
			dm_id="456",
		)
		assert quest.title == "Test Quest"

	def test_create_quest_validates_title(self):
		with pytest.raises(ValueError):
			Quest(guild_id="123", title="", dm_id="456")
```

### Test Organization

```
tests/
├── api/           # API endpoint tests
├── bot/           # Discord bot tests
├── domain/        # Domain model & use case tests
│   ├── models/
│   └── usecases/
└── infra/         # Repository & infrastructure tests
```

## Pull Request Process

### Before Submitting

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow code style guidelines
   - Add/update tests
   - Update documentation if needed

3. **Run checks locally**

   ```bash
   make lint
   make test
   pre-commit run --all-files
   ```

4. **Commit with clear messages**

   ```bash
   git commit -m "feat: add quest completion notifications"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `style:` Code style (no logic change)
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

### Submitting

1. Push your branch and open a PR
2. Fill out the PR template
3. Link related issues
4. Request review from maintainers

### Review Process

- At least one maintainer approval required
- All CI checks must pass
- Address review feedback promptly
- Squash commits before merge (if requested)

## Project Architecture

### Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│     API     │────▶│   MongoDB   │
│  (Next.js)  │     │  (FastAPI)  │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐             │
                    │  Discord    │◀────────────┘
                    │    Bot      │
                    └─────────────┘
```

### Package Dependencies

```
nonagon_core (domain + infra)
     ▲              ▲
     │              │
nonagon_api    nonagon_bot
```

- `nonagon_core`: Shared domain models, entities, repositories
- `nonagon_api`: FastAPI service, REST endpoints
- `nonagon_bot`: Discord bot, cogs, commands

### Key Conventions

1. **Guild Scoping**: All persistent models require `guild_id`
2. **Entity IDs**: Use `EntityIDModel` subclasses (`UserID`, `QuestID`, etc.)
3. **Validation**: Call `validate_*` methods before persisting
4. **Async**: API uses Motor (async), bot uses PyMongo for sync flush

### Adding New Features

1. **Domain Model**: Add/modify in `nonagon_core/domain/models/`
2. **Repository**: Add/modify in `nonagon_core/infra/mongo/`
3. **API Endpoint**: Add router in `nonagon_api/routers/`
4. **Bot Command**: Add cog in `nonagon_bot/cogs/`
5. **Schema**: Update JSON Schema in `shared/schemas/` and run `make generate`

## JSON Schema Workflow

JSON Schema files are the source of truth for data contracts:

1. Edit schema in `shared/schemas/`
2. Validate: `make validate-schemas`
3. Generate types: `make generate`
4. Update any manual Pydantic models if needed

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community server (link in README)

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions

Thank you for contributing to Nonagon! 🎮
