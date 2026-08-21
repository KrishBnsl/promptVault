"""FastAPI application for PromptVault REST API."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from api.routes import router
from db.engine import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    if app.state.initialize_database:
        init_db()
    yield


def create_app(initialize_database: bool = True) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="PromptVault API",
        description="Open-source prompt versioning, evaluation, and management.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.initialize_database = initialize_database

    app.include_router(router, prefix="/api")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "request_error", "detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "detail": jsonable_encoder(exc.errors())},
        )

    @app.get("/", include_in_schema=False)
    def web_index() -> FileResponse:
        return FileResponse(Path(__file__).resolve().parents[1] / "web" / "index.html")

    return app


app = create_app()
