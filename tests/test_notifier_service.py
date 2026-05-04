"""Tests for the Notifier Service (The Ear).

Validates the FastAPI webhook receiver endpoints including
health checks and webhook ingestion logic.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client."""
    from workflow_orchestration_queue.notifier_service import app

    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_online(self, client: TestClient) -> None:
        """Health check should return online status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "OS-APOW" in data["system"]

    def test_health_has_system_field(self, client: TestClient) -> None:
        """Health response should include system identifier."""
        response = client.get("/health")
        data = response.json()
        assert "system" in data


class TestWebhookEndpoint:
    """Tests for the /webhooks/github endpoint."""

    def test_webhook_missing_signature_returns_401(self, client: TestClient) -> None:
        """Requests without X-Hub-Signature-256 should be rejected."""
        response = client.post("/webhooks/github", json={"action": "opened"})
        assert response.status_code == 401

    def test_webhook_invalid_signature_returns_401(self, client: TestClient) -> None:
        """Requests with invalid signatures should be rejected."""
        response = client.post(
            "/webhooks/github",
            json={"action": "opened"},
            headers={"X-Hub-Signature-256": "sha256=badsignature"},
        )
        assert response.status_code == 401

    def test_webhook_valid_signature_accepted(self, client: TestClient) -> None:
        """Requests with valid HMAC signature should be processed."""
        import hashlib
        import hmac
        import json

        from workflow_orchestration_queue.notifier_service import (
            WEBHOOK_SECRET,
            app,
            get_queue,
        )

        mock_queue = AsyncMock()

        payload = {
            "action": "opened",
            "issue": {
                "number": 1,
                "title": "Test issue",
                "body": "test body",
                "labels": [],
            },
            "repository": {"full_name": "org/repo"},
        }

        # Use content= to control exact bytes for HMAC computation
        body = json.dumps(payload, separators=(",", ":")).encode()
        signature = "sha256=" + hmac.new(WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()

        # Override the dependency at the FastAPI app level
        app.dependency_overrides[get_queue] = lambda: mock_queue
        try:
            response = client.post(
                "/webhooks/github",
                content=body,
                headers={
                    "X-Hub-Signature-256": signature,
                    "Content-Type": "application/json",
                },
            )
            # Even with no actionable mapping, we expect 200
            assert response.status_code == 200
            assert response.json()["status"] == "ignored"
        finally:
            app.dependency_overrides.clear()
