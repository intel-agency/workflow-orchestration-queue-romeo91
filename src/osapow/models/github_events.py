"""GitHub webhook event payload schemas.

Pydantic models for parsing GitHub webhook JSON payloads. These schemas
support HMAC verification and event triage in the Notifier service.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GitHubLabel(BaseModel):
    """Represents a GitHub label attached to an issue."""

    id: int
    name: str
    color: str = ""


class GitHubUser(BaseModel):
    """Represents a GitHub user/actor."""

    id: int
    login: str
    avatar_url: str = ""


class GitHubRepository(BaseModel):
    """Represents a GitHub repository reference."""

    id: int
    full_name: str
    html_url: str = ""


class GitHubIssue(BaseModel):
    """Represents a GitHub issue from a webhook payload."""

    id: int
    number: int
    title: str
    body: str | None = None
    html_url: str = ""
    labels: list[GitHubLabel] = Field(default_factory=list)
    assignee: GitHubUser | None = None
    node_id: str = ""


class GitHubWebhookPayload(BaseModel):
    """Top-level GitHub webhook event payload.

    Supports ``issues``, ``issue_comment``, and ``pull_request_review``
    event types. Fields are optional to gracefully handle varied payloads.
    """

    action: str = ""
    issue: GitHubIssue | None = None
    repository: GitHubRepository | None = None
    sender: GitHubUser | None = None
    comment: dict[str, Any] | None = None
    pull_request: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
