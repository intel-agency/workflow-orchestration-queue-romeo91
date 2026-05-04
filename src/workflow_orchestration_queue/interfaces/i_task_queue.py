"""Abstract task queue interface.

Defines the contract that all queue provider implementations must satisfy.
Phase 1 uses GitHub Issues; future phases may add Linear, Notion, or SQL queues.
"""

from abc import ABC, abstractmethod

from workflow_orchestration_queue.models.work_item import WorkItem, WorkItemStatus


class ITaskQueue(ABC):
    """Interface for work queue operations (Strategy Pattern).

    All queue interactions are abstracted behind this interface to prevent
    vendor lock-in. Phase 1 implements this with GitHub Issues (labels,
    comments, assignees).
    """

    @abstractmethod
    async def fetch_queued_items(self) -> list[WorkItem]:
        """Retrieve all items currently in the queued state."""

    @abstractmethod
    async def add_to_queue(self, item: WorkItem) -> bool:
        """Enqueue a new work item.

        Returns True if the item was successfully added.
        """

    @abstractmethod
    async def claim_task(self, item_id: str, sentinel_id: str) -> bool:
        """Atomically claim a task for execution.

        Uses provider-specific locking (e.g., GitHub Assignees)
        to prevent concurrent claim collisions.

        Returns True if the claim was successful.
        """

    @abstractmethod
    async def update_status(
        self,
        item_id: str,
        status: WorkItemStatus,
        comment: str = "",
    ) -> None:
        """Update the status of a work item.

        Applies the terminal or transitional label and optionally
        posts a progress/comment update.
        """
