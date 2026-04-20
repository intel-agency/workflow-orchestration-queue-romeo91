"""Task queue interface — abstract base class for queue backends.

Defines the standard operations that all queue implementations must
provide (Strategy Pattern). Phase 1 uses GitHub Issues; future phases
may add Linear, Notion, or SQL-based backends without modifying the
Sentinel's core dispatch logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osapow.models.work_item import WorkItem, WorkItemStatus


class ITaskQueue(ABC):
    """Abstract interface for the Work Queue backend.

    Implementations map these operations to a specific provider
    (e.g., GitHub Issues + Labels, Redis, Linear, etc.).
    """

    @abstractmethod
    async def add_to_queue(self, item: WorkItem) -> bool:
        """Enqueue a work item for processing.

        Args:
            item: The validated work item to add to the queue.

        Returns:
            ``True`` if the item was successfully queued.
        """

    @abstractmethod
    async def fetch_queued(self) -> list[WorkItem]:
        """Retrieve all work items awaiting processing.

        Returns:
            A list of ``WorkItem`` instances with ``QUEUED`` status.
        """

    @abstractmethod
    async def claim_task(self, item: WorkItem, sentinel_id: str) -> bool:
        """Atomically claim a task for execution.

        Uses the provider's concurrency mechanism (e.g., GitHub Assignees)
        to prevent race conditions in multi-Sentinel deployments.

        Args:
            item: The work item to claim.
            sentinel_id: Unique identifier of the claiming Sentinel instance.

        Returns:
            ``True`` if the claim succeeded (no concurrent conflict).
        """

    @abstractmethod
    async def update_status(
        self,
        item: WorkItem,
        status: WorkItemStatus,
        comment: str | None = None,
    ) -> None:
        """Transition a work item to a new status.

        Args:
            item: The work item to update.
            status: The target lifecycle state.
            comment: Optional comment to post (e.g., heartbeat, error log).
        """
