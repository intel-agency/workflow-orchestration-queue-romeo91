"""Pytest fixtures and shared test configuration."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from osapow.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """Provide an async HTTP test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
