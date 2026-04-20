"""GitHub webhook endpoint — secure ingestion and event triage.

Exposes ``POST /webhooks/github`` with mandatory HMAC SHA256 signature
verification. Valid events are parsed into ``WorkItem`` objects and
forwarded to the task queue.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from osapow.core.config import settings
from osapow.core.security import verify_hmac_signature
from osapow.models.github_events import GitHubWebhookPayload
from osapow.models.work_item import WorkItem, WorkItemType

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Signature Verification Dependency ───────────────────────────────


async def verify_github_signature(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
) -> None:
    """Validate the ``X-Hub-Signature-256`` header.

    Args:
        request: The incoming HTTP request.
        x_hub_signature_256: The HMAC signature header value.

    Raises:
        HTTPException: 401 if the header is missing or the signature is invalid.
    """
    if not x_hub_signature_256:
        raise HTTPException(
            status_code=401,
            detail="X-Hub-Signature-256 header is missing",
        )

    body = await request.body()
    try:
        if not verify_hmac_signature(body, x_hub_signature_256, settings.webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


# ── Endpoint ────────────────────────────────────────────────────────


@router.post("/github", dependencies=[Depends(verify_github_signature)])
async def handle_github_webhook(
    request: Request,
) -> dict[str, str]:
    """Receive and triage a GitHub webhook event.

    1. Validates the HMAC signature (via dependency).
    2. Parses the event type from ``X-GitHub-Event`` header.
    3. Routes to the appropriate triage logic.

    Returns:
        A JSON acknowledgement with ``status`` and optional ``item_id``.
    """
    event_type = request.headers.get("X-GitHub-Event", "")
    payload = GitHubWebhookPayload(**await request.json())

    logger.info("Received GitHub event: action=%s event=%s", payload.action, event_type)

    # ── Issue opened → check for template patterns ──────────────
    if event_type == "issues" and payload.action == "opened" and payload.issue:
        issue = payload.issue
        title = issue.title
        label_names = [lbl.name for lbl in issue.labels]

        if "[Application Plan]" in title or "agent:plan" in label_names:
            item_type = WorkItemType.APPLICATION_PLAN
        elif "bug" in label_names or "[Bugfix]" in title:
            item_type = WorkItemType.BUGFIX
        else:
            item_type = WorkItemType.TASK

        work_item = WorkItem(
            id=str(issue.id),
            issue_number=issue.number,
            source_url=issue.html_url,
            target_repo=payload.repository.full_name if payload.repository else "",
            item_type=item_type,
            context_body=issue.body or "",
            metadata={"node_id": issue.node_id},
        )
        logger.info(
            "Triaged issue #%d as %s — queued for processing",
            issue.number,
            item_type.value,
        )
        # TODO: forward to ITaskQueue.add_to_queue(work_item)
        return {"status": "accepted", "item_id": work_item.id}

    return {"status": "ignored", "reason": "No actionable OS-APOW event mapping found"}
