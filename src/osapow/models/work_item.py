"""Work item models — unified data structures for task representation.

These models decouple the orchestrator logic from any specific provider
(GitHub, Linear, etc.), enabling the Strategy Pattern for queue backends.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkItemType(StrEnum):
    """Categorization of work item types."""

    APPLICATION_PLAN = "APPLICATION_PLAN"
    EPIC = "EPIC"
    STORY = "STORY"
    TASK = "TASK"
    BUGFIX = "BUGFIX"


class WorkItemStatus(StrEnum):
    """Task lifecycle states — mapped to GitHub labels in Phase 1.

    State machine::

        agent:queued → agent:in-progress → agent:success
                                          → agent:error
                                          → agent:infra-failure
        agent:reconciling (stale task recovery)
        agent:stalled-budget (cost guardrail)
    """

    QUEUED = "agent:queued"
    IN_PROGRESS = "agent:in-progress"
    SUCCESS = "agent:success"
    ERROR = "agent:error"
    INFRA_FAILURE = "agent:infra-failure"
    RECONCILING = "agent:reconciling"
    STALLED_BUDGET = "agent:stalled-budget"


class WorkItem(BaseModel):
    """Unified work item representation across all providers.

    Attributes:
        id: Unique identifier (e.g., GitHub issue ID).
        issue_number: Human-readable number (e.g., GitHub issue #42).
        source_url: URL to the original issue/ticket.
        target_repo: Repository slug (e.g., ``intel-agency/my-repo``).
        item_type: Classification of the work item.
        context_body: Full text content of the issue body.
        status: Current lifecycle state.
        metadata: Provider-specific extra data (e.g., ``node_id``).
    """

    id: str
    issue_number: int
    source_url: str
    target_repo: str
    item_type: WorkItemType = WorkItemType.TASK
    context_body: str = ""
    status: WorkItemStatus = WorkItemStatus.QUEUED
    metadata: dict[str, Any] = Field(default_factory=dict)
