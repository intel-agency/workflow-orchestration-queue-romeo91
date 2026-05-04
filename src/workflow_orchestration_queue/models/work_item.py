"""WorkItem domain model and associated enums.

Defines the core data structures used throughout the OS-APOW system
for representing tasks, their types, statuses, and lifecycle states.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkItemType(StrEnum):
    """Classification of work item granularity."""

    APPLICATION_PLAN = "APPLICATION_PLAN"
    EPIC = "EPIC"
    STORY = "STORY"
    TASK = "TASK"


class WorkItemStatus(StrEnum):
    """Lifecycle states for a work item in the queue.

    Maps to GitHub label names used by the state machine.
    """

    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    RECONCILING = "agent:reconciling"
    STALLED_BUDGET = "agent:stalled-budget"


class TaskType(StrEnum):
    """Task execution type — determines which workflow module the worker uses."""

    PLAN = "PLAN"
    IMPLEMENT = "IMPLEMENT"
    BUGFIX = "BUGFIX"


class WorkItem(BaseModel):
    """Unified domain object representing a task in the orchestration queue.

    Mapped from GitHub Issues (or any future queue provider) into a
    provider-agnostic structure consumed by the Sentinel Orchestrator.
    """

    provider_id: str = Field(description="Unique identifier from the provider (e.g., issue number)")
    issue_number: int = Field(description="GitHub issue number")
    source_url: str = Field(description="URL to the original issue")
    context_body: str = Field(default="", description="Issue body with requirements")
    target_repo: str = Field(description="Target repository in org/repo format")
    target_repo_slug: str = Field(default="", description="Alternative slug for the target repo")
    item_type: WorkItemType = Field(
        default=WorkItemType.TASK, description="Granularity classification"
    )
    task_type: TaskType = Field(default=TaskType.IMPLEMENT, description="Execution type")
    status: WorkItemStatus = Field(default=WorkItemStatus.QUEUED, description="Current queue state")
    raw_payload: dict[str, Any] = Field(
        default_factory=dict, description="Raw provider event payload"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Provider-specific metadata")
