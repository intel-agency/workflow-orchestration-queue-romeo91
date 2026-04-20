"""OS-APOW FastAPI application entry point.

Provides the web API for webhook ingestion and health monitoring.
Run with: uv run uvicorn osapow.main:app --reload
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from osapow.api.health import router as health_router
from osapow.api.webhooks import router as webhooks_router
from osapow.core.config import settings
from osapow.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown hooks."""
    setup_logging()
    yield


app = FastAPI(
    title="OS-APOW",
    description=(
        "Operational Status and Automated Processing of Workflows — "
        "a headless agentic orchestration platform."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── Routers ─────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])


def run_api() -> None:
    """Entry point for the `osapow-api` console script."""
    import uvicorn

    uvicorn.run(
        "osapow.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
