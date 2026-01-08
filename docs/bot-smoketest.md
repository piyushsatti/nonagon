# Bot Smoke Test (Test Discord Server)

## Prerequisites

- Bot is invited to your test server with scopes `bot applications.commands` and permissions: Send Messages, Read Message History, Use Slash Commands.
- PostgreSQL reachable per `.env`: set `DATABASE_URL`.
- `BOT_TOKEN` is set in `.env` and not a placeholder.

## Run the Bot (local)

- Install deps: `pip install -e ".[dev]"`
- Start the bot: `make bot` (or `python -m nonagon_bot.main`)
- Tail logs: `tail -f logs/bot.log`

## First-Time Command Sync

- Slash commands can take up to 1–3 minutes to appear the first time.
- If they don’t appear, restart once: stop and re-run `make bot`.

## Basic Smoke Checks (in Discord)

- Use `/help` — expect quickstart/links response (HelpCommandsCog).
- Use `/extensions` — should list loaded extensions (ExtensionManagerCog).
- Try a simple flow to touch DB + logic:
  - Create something minimal (e.g., `/quest_create` with valid inputs).
  - Verify via `/quest_list` that it persists.
- Listener sanity (optional): send a normal message in a channel the bot can access and watch logs for ListnerCog events.

## Fast Dev Loop

- Edit code under `backend/bot/nonagon_bot`; restart the bot to pick up changes.
- Reinstall deps only if `pyproject.toml` changed.

## Troubleshooting

- Bot offline or commands missing:
  - Confirm the bot is in the server and online.
  - Ensure invite used `applications.commands` scope.
  - Wait up to a few minutes; then restart the bot.
- Auth failures:
  - Check `BOT_TOKEN` in `.env` is correct and non-empty.
  - Logs: `tail -n 200 logs/bot.log`.
- Database errors:
  - Verify `DATABASE_URL` is correct and reachable.
- Cog load failures:
  - Logs will include `Error loading extension ...` with a traceback; fix and restart.

## Cleanup

- Stop services: ctrl+c the bot process
- Clear logs: `rm -f logs/bot.log`
