# Contributing to Nonagon

Thank you for your interest in contributing to Nonagon! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the issue, not the person
- Help others learn and grow

## Getting Started

See the [README.md Quick Start](README.md#quick-start) for environment setup, installation, and running services.

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

## Testing

Run tests with `make test` or target specific areas:

```bash
pytest tests/domain/         # Domain tests
pytest tests/bot/            # Bot tests
pytest -k "quest"            # Pattern matching
```

### Writing Tests

- Place tests in the appropriate `tests/` subdirectory
- Use `pytest` fixtures for setup/teardown
- Mock external dependencies (Discord API, PostgreSQL)
- Aim for >80% coverage on new code

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

See [docs/architecture.md](docs/architecture.md) for the full design document covering:

- Hexagonal (Ports & Adapters) structure
- Runtime components (Cogs, Use Cases, Domain, Adapters)
- Data model and ID strategy
- Key workflows (Quest lifecycle, summaries)

### Adding New Features

1. **Domain Model**: Add/modify in `nonagon_core/domain/models/`
2. **Repository**: Add/modify in `nonagon_core/infra/postgres/`
3. **API Endpoint**: Add resolver in `nonagon_api/graphql/resolvers.py`
4. **Bot Command**: Add cog in `nonagon_bot/cogs/`

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community server (link in README)

## Recognition

Contributors are recognized in:

- GitHub contributors list
- Release notes for significant contributions

Thank you for contributing to Nonagon! 🎮
