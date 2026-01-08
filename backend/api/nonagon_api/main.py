import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from nonagon_api.graphql.schema import graphql_router
from nonagon_core.infra.postgres.database import close_db, init_db

# Use local logs directory in development, /app/logs in Docker
log_dir = Path(os.getenv("LOG_DIR", "./logs"))
try:
    log_dir.mkdir(parents=True, exist_ok=True)
except OSError as exc:  # pragma: no cover - defensive logging
    logging.warning("Unable to create log directory %s: %s", log_dir, exc)
else:
    log_path = log_dir / "api.log"
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    root_logger = logging.getLogger()
    if not any(
        isinstance(handler, logging.FileHandler)
        and getattr(handler, "baseFilename", "") == str(log_path)
        for handler in root_logger.handlers
    ):
        root_logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup: initialize database
    try:
        await init_db()
        logging.info("Database initialized successfully")
    except (OSError, ConnectionError) as e:
        logging.warning("Database initialization failed: %s. Running without database.", e)
    yield
    # Shutdown: close database connections
    try:
        await close_db()
    except (OSError, ConnectionError):
        pass


app = FastAPI(
    title="Nonagon API",
    version="2.0.0",
    description="GraphQL API for Nonagon Discord quest management system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint (primary API)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app", host="localhost", port=8000, reload=True, log_level="debug"
    )
