"""FastAPI application for PromptVault REST API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from promptvault.api.routes import router
from promptvault.db.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="PromptVault API",
        description="Open-source prompt versioning, evaluation, and management.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(router, prefix="/api")

    return app


app = create_app()
