import asyncio
import logging
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands

from nonagon_bot.utils.logging import get_logger


logger = get_logger(__name__)


class Nonagon(commands.Bot):
    """Main bot class that initializes the Discord bot and loads cogs.
    This class is responsible for setting up the bot, registering events,
    and loading the necessary cogs for functionality.
    """

    def __init__(self, intents: discord.Intents):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"), intents=intents
        )

    # Called before the bot logins to discord
    async def setup_hook(self):

        # Load every .py file under the bot/cogs directory as an extension
        cogs_path = Path(__file__).parent / "cogs"
        loaded: list[str] = []
        failed: dict[str, str] = {}
        for file in cogs_path.glob("*.py"):
            if file.name.startswith("_"):
                continue  # skip __init__.py and private modules
            ext = f"app.bot.cogs.{file.stem}"  # e.g. bot.cogs.my_cog
            try:
                await self.load_extension(ext)
                loaded.append(ext)
                logger.info("Loaded extension %s", ext)
            except Exception:
                import traceback as _tb

                failed[ext] = _tb.format_exc()
                logger.error("Error loading extension %s:\n%s", ext, failed[ext])

        diagnostics_ext = "app.bot.commands.diagnostics"
        if diagnostics_ext not in self.extensions:
            try:
                await self.load_extension(diagnostics_ext)
                loaded.append(diagnostics_ext)
                logger.info("Loaded extension %s", diagnostics_ext)
            except Exception:
                import traceback as _tb

                failed[diagnostics_ext] = _tb.format_exc()
                logger.error(
                    "Error loading extension %s:\n%s",
                    diagnostics_ext,
                    failed[diagnostics_ext],
                )

        # Cog loader audit summary
        logger.info("Cog loader audit: %d loaded, %d failed", len(loaded), len(failed))
        if loaded:
            logger.info("Loaded cogs: %s", ", ".join(sorted(loaded)))
        if failed:
            for ext, tb in failed.items():
                logger.debug("Failed cog %s trace:\n%s", ext, tb)

        # Call the parent setup_hook to ensure all cogs are loaded
        await super().setup_hook()

    # Called to login and connect the bot to Discord
    async def start(self, bot_token: str):
        async def _idle_forever(reason_template: str, *args: Any) -> None:
            reason = reason_template % args if args else reason_template
            logger.error(
                "%s. Bot will remain idle until restarted with valid credentials.",
                reason,
            )
            while True:
                await asyncio.sleep(30)

        normalized = (bot_token or "").strip()
        placeholders = {"", "replace_me"}

        if normalized.lower() in placeholders:
            logging.error("BOT_TOKEN is missing or still set to the placeholder value.")
            raise SystemExit(1)

        try:
            await super().start(normalized)
        except discord.LoginFailure as exc:
            await _idle_forever("Discord login failed: %s", exc)
        except discord.HTTPException as exc:
            await _idle_forever("Discord HTTP error during startup: %s", exc)
        except Exception as exc:  # pragma: no cover - defensive fallback
            await _idle_forever("Unexpected error during startup: %s", exc)

    # Called when the bot is ready
    async def on_ready(self):
        tree_commands = [cmd.qualified_name for cmd in self.tree.get_commands()]
        assert self.user is not None, "Bot user should be set when ready"
        logger.info("Logged in as %s (ID: %s)", self.user, self.user.id)
        logger.info("Loaded cogs: %s", ", ".join(sorted(self.cogs.keys())))
        logger.info("Slash commands: %s", ", ".join(sorted(tree_commands)))

    async def on_error(self, event_method, /, *args, **kwargs):
        await super().on_error(event_method, *args, **kwargs)

    async def _sync_application_commands(self) -> None:
        await self.wait_until_ready()

        try:
            # Strategy: Per-guild sync only. Copy globals to each guild and sync.
            # This ensures rapid updates without waiting for global propagation.
            target_guild_ids = {guild.id for guild in self.guilds}
            for guild_id in target_guild_ids:
                try:
                    guild_obj = discord.Object(id=guild_id)
                    self.tree.copy_global_to(guild=guild_obj)
                    scoped_commands = await self.tree.sync(guild=guild_obj)
                    logger.info(
                        "Synced %d slash commands to guild %s",
                        len(scoped_commands),
                        guild_id,
                    )
                except Exception:
                    logger.exception(
                        "Failed to sync application commands for guild %s", guild_id
                    )
        except Exception:
            logger.exception("Failed to sync application commands")
