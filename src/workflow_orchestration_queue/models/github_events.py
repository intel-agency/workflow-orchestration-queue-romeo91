"""GitHub webhook event payload schemas.

Pydantic models for parsing and validating incoming GitHub webhook events
before they are mapped to WorkItem objects by the Notifier.
"""

from pydantic import BaseModel, Field


class GitHubLabel(BaseModel):
    """GitHub label attached to an issue or PR."""

    id: int
    name: str
    color: str = ""
    description: str | None = None


class GitHubUser(BaseModel):
    """GitHub user (actor) associated with an event."""

    id: int
    login: str
    avatar_url: str = ""


class GitHubRepository(BaseModel):
    """GitHub repository referenced in a webhook event."""

    id: int
    name: str
    full_name: str
    html_url: str = ""
    private: bool = False


class GitHubIssue(BaseModel):
    """GitHub issue from a webhook payload."""

    id: int
    number: int
    title: str
    body: str | None = None
    html_url: str = ""
    state: str = "open"
    labels: list[GitHubLabel] = Field(default_factory=list)
    user: GitHubUser | None = None


class GitHubWebhookPayload(BaseModel):
    """Top-level GitHub webhook event payload.

    Supports issues, issue_comment, and pull_request events
    used by the OS-APOW Notifier for event triage.
    """

    action: str = ""
    issue: GitHubIssue | None = None
    repository: GitHubRepository | None = None
    sender: GitHubUser | None = None
    ref: str | None = None
    number: int | None = None

    model_config = {"extra": "allow"}

    @property
    def event_labels(self) -> list[str]:
        """Extract label names from the associated issue."""
        if self.issue and self.issue.labels:
            return [label.name for label in self.issue.labels]
        return []

    @property
    def is_plan_request(self) -> bool:
        """Check if this event represents a planning request."""
        if not self.issue:
            return False
        return "agent:plan" in self.event_labels or "[Application Plan]" in self.issue.title
