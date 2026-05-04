"""OS-APOW Work Event Notifier (The Ear).

FastAPI-based webhook receiver that ingests GitHub webhook events,
validates HMAC signatures, performs intelligent event triage,
and enqueues actionable WorkItems for the Sentinel Orchestrator.
"""

import hashlib
import hmac
import logging
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request

from workflow_orchestration_queue.interfaces.i_task_queue import ITaskQueue
from workflow_orchestration_queue.models.work_item import WorkItem, WorkItemType

logger = logging.getLogger("OS-APOW.Notifier")

app = FastAPI(
    title="OS-APOW Event Notifier",
    description="Webhook ingestion service for the OS-APOW orchestration platform",
    version="0.1.0",
)

WEBHOOK_SECRET = b"change-me-webhook-secret"


def get_queue() -> ITaskQueue:
    """Dependency injection placeholder for the task queue implementation.

    Returns a stub queue for initial development. Will be replaced with
    GitHubIssuesQueue in production.
    """
    raise NotImplementedError("Task queue implementation not yet configured")


async def verify_signature(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
) -> None:
    """Validate the HMAC SHA256 signature on incoming webhook requests."""
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 header missing")

    body = await request.body()
    expected_signature = "sha256=" + hmac.new(WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


@app.post("/webhooks/github", dependencies=[Depends(verify_signature)])
async def handle_github_webhook(
    request: Request,
    queue: ITaskQueue = Depends(get_queue),  # noqa: B008
) -> dict[str, str]:
    """Primary webhook receiver for GitHub App events.

    Performs event triage, maps payloads to unified WorkItem objects,
    and enqueues them for the Sentinel Orchestrator.
    """
    payload: dict[str, Any] = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    action = payload.get("action", "unknown")

    logger.info("Received GitHub webhook: event=%s action=%s", event_type, action)

    if event_type == "issues" and action == "opened":
        issue = payload.get("issue", {})
        labels = [label.get("name", "") for label in issue.get("labels", [])]

        if "agent:plan" in labels or "[Application Plan]" in issue.get("title", ""):
            work_item = WorkItem(
                provider_id=str(issue.get("number", "")),
                target_repo=payload.get("repository", {}).get("full_name", ""),
                item_type=WorkItemType.APPLICATION_PLAN,
                content=issue.get("body", ""),
                raw_payload=payload,
            )
            await queue.add_to_queue(work_item)
            return {"status": "accepted", "item_id": work_item.provider_id}

    return {"status": "ignored", "reason": "No actionable OS-APOW event mapping found"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and Docker healthchecks."""
    return {"status": "online", "system": "OS-APOW Notifier"}
