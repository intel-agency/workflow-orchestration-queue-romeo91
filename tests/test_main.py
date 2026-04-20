"""Basic application tests — import sanity and health endpoint."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from osapow.main import app


def test_import_osapow() -> None:
    """Verify the main package imports without error."""
    import osapow

    assert osapow.__version__ == "0.1.0"


def test_import_models() -> None:
    """Verify model imports work correctly."""
    from osapow.models.work_item import WorkItemStatus, WorkItemType

    assert WorkItemType.TASK.value == "TASK"
    assert WorkItemStatus.QUEUED.value == "agent:queued"


def test_import_security() -> None:
    """Verify security module imports and HMAC works."""
    import hashlib
    import hmac

    from osapow.core.security import verify_hmac_signature

    payload = b"test-payload"
    secret = "test-secret"

    sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    assert verify_hmac_signature(payload, sig, secret) is True
    assert verify_hmac_signature(payload, "sha256=invalid", secret) is False


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    """Verify the /health endpoint returns expected payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["system"] == "OS-APOW Notifier"


@pytest.mark.asyncio
async def test_webhook_rejects_missing_signature() -> None:
    """Verify webhook rejects requests without signature (TC-01)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/webhooks/github", json={"action": "opened"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_rejects_invalid_signature() -> None:
    """Verify webhook rejects requests with invalid signature (TC-01)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            json={"action": "opened"},
            headers={"X-Hub-Signature-256": "sha256=deadbeef"},
        )

    assert response.status_code == 401
