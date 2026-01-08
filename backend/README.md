# Backend

This directory contains the FastAPI API (`api/`) and Discord bot (`bot/`).

## Documentation

| Topic                          | Location                                        |
| ------------------------------ | ----------------------------------------------- |
| Architecture & design patterns | [docs/architecture.md](../docs/architecture.md) |
| API endpoints & schemas        | [docs/api.md](../docs/api.md)                   |
| Slash commands reference       | [docs/discord.md](../docs/discord.md)           |
| Dev setup & quick start        | [README.md](../README.md)                       |
| Contributing guidelines        | [CONTRIBUTING.md](../CONTRIBUTING.md)           |

> **Note:** Moderation SOP and DM wizard guidance are documented in [docs/architecture.md](../docs/architecture.md) §3.1.1 (DM Wizard Patterns) and §8.1 (Moderation SOP).

## Quick Commands

```bash
# From project root
make api       # Start FastAPI server
make bot       # Start Discord bot
make test      # Run all tests
```
