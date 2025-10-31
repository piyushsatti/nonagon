import asyncio
import os
import logging

from app.bot.core.logging import configure_logging
from app.bot.core.runtime import start_bot
from app.bot.core.settings import load_settings


logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    settings = load_settings()

    if settings.auto_load_cogs:
        logger.info("AUTO_LOAD_COGS enabled: will auto-load default cog manifest at startup")
    else:
        logger.info("AUTO_LOAD_COGS not enabled: only core admin cogs will be loaded")

    # Optionally surface the environment variable for quick debugging
    if os.getenv("AUTO_LOAD_COGS") is not None:
        logger.debug("AUTO_LOAD_COGS env value=%s", os.getenv("AUTO_LOAD_COGS"))

    asyncio.run(start_bot(settings))


if __name__ == "__main__":
    main()
