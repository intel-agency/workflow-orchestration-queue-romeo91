"""Tests for WorkItem domain model and associated enums.

Validates construction, defaults, serialization, and enum behavior
for the core data structures used throughout the OS-APOW system.
"""

import pytest
from pydantic import ValidationError

from workflow_orchestration_queue.models.work_item import (
    TaskType,
    WorkItem,
    WorkItemStatus,
    WorkItemType,
)


class TestWorkItemEnums:
    """Tests for WorkItem enumeration types."""

    def test_work_item_status_values(self) -> None:
        """WorkItemStatus should have all required label values."""
        assert WorkItemStatus.QUEUED == "agent:queued"
        assert WorkItemStatus.IN_PROGRESS == "agent:in-progress"
        assert WorkItemStatus.SUCCESS == "agent:success"
        assert WorkItemStatus.ERROR == "agent:error"
        assert WorkItemStatus.INFRA_FAILURE == "agent:infra-failure"

    def test_task_type_values(self) -> None:
        """TaskType should have PLAN, IMPLEMENT, and BUGFIX."""
        assert TaskType.PLAN == "PLAN"
        assert TaskType.IMPLEMENT == "IMPLEMENT"
        assert TaskType.BUGFIX == "BUGFIX"

    def test_work_item_type_values(self) -> None:
        """WorkItemType should cover all granularity levels."""
        assert WorkItemType.APPLICATION_PLAN == "APPLICATION_PLAN"
        assert WorkItemType.EPIC == "EPIC"
        assert WorkItemType.STORY == "STORY"
        assert WorkItemType.TASK == "TASK"


class TestWorkItemModel:
    """Tests for the WorkItem Pydantic model."""

    def test_create_minimal_work_item(self) -> None:
        """WorkItem should be creatable with required fields only."""
        item = WorkItem(
            provider_id="1",
            issue_number=1,
            source_url="https://github.com/org/repo/issues/1",
            target_repo="org/repo",
        )
        assert item.provider_id == "1"
        assert item.issue_number == 1
        assert item.status == WorkItemStatus.QUEUED
        assert item.task_type == TaskType.IMPLEMENT
        assert item.item_type == WorkItemType.TASK

    def test_create_full_work_item(self, sample_work_item: WorkItem) -> None:
        """WorkItem should accept all fields."""
        assert sample_work_item.provider_id == "42"
        assert sample_work_item.context_body == "Implement the notification service"
        assert sample_work_item.status == WorkItemStatus.QUEUED

    def test_work_item_default_collections(self) -> None:
        """WorkItem should default raw_payload and metadata to empty dicts."""
        item = WorkItem(
            provider_id="1",
            issue_number=1,
            source_url="https://github.com/org/repo/issues/1",
            target_repo="org/repo",
        )
        assert item.raw_payload == {}
        assert item.metadata == {}

    def test_work_item_serialization(self, sample_work_item: WorkItem) -> None:
        """WorkItem should serialize to and from JSON correctly."""
        data = sample_work_item.model_dump()
        restored = WorkItem.model_validate(data)
        assert restored.provider_id == sample_work_item.provider_id
        assert restored.issue_number == sample_work_item.issue_number
        assert restored.status == sample_work_item.status

    def test_work_item_missing_required_field(self) -> None:
        """WorkItem should raise ValidationError when required fields are missing."""
        with pytest.raises(ValidationError):
            WorkItem(provider_id="1")  # type: ignore[call-arg]

    def test_plan_item_type(self, sample_plan_item: WorkItem) -> None:
        """Plan work items should have APPLICATION_PLAN type."""
        assert sample_plan_item.item_type == WorkItemType.APPLICATION_PLAN
        assert sample_plan_item.task_type == TaskType.PLAN
