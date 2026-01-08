from nonagon_bot.core.infra.postgres.database import close_db, init_db, ping


async def on_startup():
    await init_db()
    await ping()


async def on_shutdown():
    await close_db()
