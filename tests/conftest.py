"""OS-APOW test suite.

Shared pytest configuration and fixtures for the
workflow-orchestration-queue test suite.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from workflow_orchestration_queue.interfaces.i_task_queue import ITaskQueue
from workflow_orchestration_queue.models.work_item import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    WorkItemType,
)


@pytest.fixture
def sample_work_item() -> WorkItem:
    """Create a sample WorkItem for testing."""
    return WorkItem(
        provider_id="42",
        issue_number=42,
        source_url="https://github.com/org/repo/issues/42",
        context_body="Implement the notification service",
        target_repo="org/repo",
        item_type=WorkItemType.TASK,
        task_type=TaskType.IMPLEMENT,
        status=WorkItemStatus.QUEUED,
    )


@pytest.fixture
def sample_plan_item() -> WorkItem:
    """Create a sample planning WorkItem for testing."""
    return WorkItem(
        provider_id="7",
        issue_number=7,
        source_url="https://github.com/org/repo/issues/7",
        context_body="[Application Plan] Build the auth module",
        target_repo="org/repo",
        item_type=WorkItemType.APPLICATION_PLAN,
        task_type=TaskType.PLAN,
        status=WorkItemStatus.QUEUED,
    )


@pytest.fixture
def mock_queue() -> AsyncMock:
    """Create a mock ITaskQueue for testing."""
    queue = AsyncMock(spec=ITaskQueue)
    queue.fetch_queued_items.return_value = []
    queue.add_to_queue.return_value = True
    queue.claim_task.return_value = True
    queue.update_status.return_value = None
    return queue
