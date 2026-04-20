"""Notifier service scaffold — FastAPI webhook receiver.

This module provides the webhook ingestion layer ("The Ear").
Reference spec: ``plan_docs/notifier_service.py``

The FastAPI application is defined in ``osapow.main``; this module
contains the notification/triage logic that will be wired into the
API routes during Phase 2 implementation.
"""

from __future__ import annotations

import logging

from osapow.models.work_item import WorkItem, WorkItemType

logger = logging.getLogger(__name__)


def triage_issue(
    title: str,
    body: str,
    labels: list[str],
    issue_number: int,
    issue_id: int,
    html_url: str,
    repo_full_name: str,
    node_id: str = "",
) -> WorkItem | None:
    """Triage a GitHub issue into a WorkItem.

    Applies pattern matching on the title, body, and labels to determine
    the appropriate ``WorkItemType`` and returns a ``WorkItem`` ready
    for queueing.

    Args:
        title: Issue title.
        body: Issue body text.
        labels: List of label names attached to the issue.
        issue_number: GitHub issue number.
        issue_id: GitHub issue node ID (numeric).
        html_url: URL to the issue.
        repo_full_name: ``owner/repo`` slug.
        node_id: GraphQL node ID.

    Returns:
        A ``WorkItem`` if the issue is actionable, or ``None`` if it
        should be ignored.
    """
    # Determine type from labels or title
    item_type = WorkItemType.TASK

    if "[Application Plan]" in title or "agent:plan" in labels:
        item_type = WorkItemType.APPLICATION_PLAN
    elif "bug" in labels or "[Bugfix]" in title:
        item_type = WorkItemType.BUGFIX
    elif "epic" in labels:
        item_type = WorkItemType.EPIC
    elif "[Story]" in title:
        item_type = WorkItemType.STORY
    else:
        # Default: treat as a general task
        logger.debug("Issue #%d has no triage pattern — defaulting to TASK", issue_number)

    return WorkItem(
        id=str(issue_id),
        issue_number=issue_number,
        source_url=html_url,
        target_repo=repo_full_name,
        item_type=item_type,
        context_body=body or "",
        metadata={"node_id": node_id},
    )
