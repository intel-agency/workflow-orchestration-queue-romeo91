"""GitHub Issues queue implementation.

Maps the abstract ``ITaskQueue`` interface to GitHub Issues, Labels,
and Comments — the "Markdown as a Database" approach for Phase 1.

Reference: ``plan_docs/notifier_service.py`` and ``plan_docs/orchestrator_sentinel.py``
"""

from __future__ import annotations

import contextlib
import logging
from datetime import UTC, datetime

import httpx

from osapow.interfaces.i_task_queue import ITaskQueue
from osapow.models.work_item import WorkItem, WorkItemStatus, WorkItemType

logger = logging.getLogger(__name__)

# Label-to-WorkItemType mapping for triage
_LABEL_TYPE_MAP: dict[str, WorkItemType] = {
    "agent:plan": WorkItemType.APPLICATION_PLAN,
    "bug": WorkItemType.BUGFIX,
    "epic": WorkItemType.EPIC,
}


class GitHubIssuesQueue(ITaskQueue):
    """Phase 1 implementation: maps WorkItems to GitHub Issue Labels/Comments.

    Args:
        token: GitHub personal access or installation token.
        org: GitHub organization or user name.
        repo: GitHub repository name.
    """

    def __init__(self, token: str, org: str, repo: str) -> None:
        self.token = token
        self.base_url = f"https://api.github.com/repos/{org}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    # ── ITaskQueue implementation ───────────────────────────────

    async def add_to_queue(self, item: WorkItem) -> bool:
        """Add the ``agent:queued`` label to a GitHub issue."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/issues/{item.issue_number}/labels"
            response = await client.post(
                url,
                json={"labels": [WorkItemStatus.QUEUED.value]},
                headers=self.headers,
            )
            if response.status_code in (200, 201):
                logger.info("Queued issue #%d", item.issue_number)
                return True
            logger.error("Failed to queue issue #%d: %s", item.issue_number, response.text)
            return False

    async def fetch_queued(self) -> list[WorkItem]:
        """Query GitHub for issues labeled ``agent:queued``."""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/issues"
            params = {
                "labels": WorkItemStatus.QUEUED.value,
                "state": "open",
            }
            response = await client.get(url, params=params, headers=self.headers)

            if response.status_code != 200:
                logger.error("GitHub API error: %d", response.status_code)
                return []

            work_items: list[WorkItem] = []
            for issue in response.json():
                labels = [lbl["name"] for lbl in issue.get("labels", [])]
                title = issue.get("title", "")

                # Determine task type from labels or title patterns
                item_type = WorkItemType.TASK
                for label, mapped_type in _LABEL_TYPE_MAP.items():
                    if label in labels:
                        item_type = mapped_type
                        break
                if item_type == WorkItemType.TASK and "[Application Plan]" in title:
                    item_type = WorkItemType.APPLICATION_PLAN

                work_items.append(
                    WorkItem(
                        id=str(issue["id"]),
                        issue_number=issue["number"],
                        source_url=issue["html_url"],
                        target_repo="",  # resolved at claim time
                        item_type=item_type,
                        context_body=issue.get("body") or "",
                        status=WorkItemStatus.QUEUED,
                        metadata={"node_id": issue.get("node_id", "")},
                    )
                )

            return work_items

    async def claim_task(self, item: WorkItem, sentinel_id: str) -> bool:
        """Lock the task via GitHub Assignees and transition to in-progress."""
        async with httpx.AsyncClient() as client:
            issue_url = f"{self.base_url}/issues/{item.issue_number}"

            # Remove queued label, add in-progress
            labels_url = f"{issue_url}/labels"
            with contextlib.suppress(httpx.HTTPStatusError):
                await client.delete(
                    f"{labels_url}/{WorkItemStatus.QUEUED.value}",
                    headers=self.headers,
                )

            await client.post(
                labels_url,
                json={"labels": [WorkItemStatus.IN_PROGRESS.value]},
                headers=self.headers,
            )

            # Post claim comment
            comment_url = f"{issue_url}/comments"
            msg = (
                f"**Sentinel {sentinel_id}** has claimed this task.\n"
                f"- **Start Time:** {datetime.now(tz=UTC).isoformat()}\n"
                f"- **Environment:** `devcontainer-opencode.sh` initializing..."
            )
            await client.post(comment_url, json={"body": msg}, headers=self.headers)

            logger.info("Claimed issue #%d as %s", item.issue_number, sentinel_id)
            return True

    async def update_status(
        self,
        item: WorkItem,
        status: WorkItemStatus,
        comment: str | None = None,
    ) -> None:
        """Transition issue labels and optionally post a comment."""
        async with httpx.AsyncClient() as client:
            labels_url = f"{self.base_url}/issues/{item.issue_number}/labels"

            # Remove previous transition label
            with contextlib.suppress(httpx.HTTPStatusError):
                await client.delete(
                    f"{labels_url}/{WorkItemStatus.IN_PROGRESS.value}",
                    headers=self.headers,
                )

            # Apply terminal status label
            await client.post(labels_url, json={"labels": [status.value]}, headers=self.headers)

            if comment:
                comment_url = f"{self.base_url}/issues/{item.issue_number}/comments"
                await client.post(comment_url, json={"body": comment}, headers=self.headers)

            logger.info("Updated issue #%d → %s", item.issue_number, status.value)
