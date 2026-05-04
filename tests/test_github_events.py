"""Tests for GitHub webhook event payload models.

Validates parsing and property computation for the Pydantic
schemas used by the Notifier for event triage.
"""

from workflow_orchestration_queue.models.github_events import (
    GitHubIssue,
    GitHubLabel,
    GitHubRepository,
    GitHubUser,
    GitHubWebhookPayload,
)


class TestGitHubLabel:
    """Tests for the GitHubLabel model."""

    def test_create_label(self) -> None:
        """GitHubLabel should store name and color."""
        label = GitHubLabel(id=1, name="bug", color="fc2929")
        assert label.name == "bug"
        assert label.color == "fc2929"

    def test_label_optional_description(self) -> None:
        """GitHubLabel description should be optional."""
        label = GitHubLabel(id=1, name="enhancement")
        assert label.description is None


class TestGitHubUser:
    """Tests for the GitHubUser model."""

    def test_create_user(self) -> None:
        """GitHubUser should store login and id."""
        user = GitHubUser(id=123, login="octocat")
        assert user.login == "octocat"
        assert user.id == 123


class TestGitHubRepository:
    """Tests for the GitHubRepository model."""

    def test_create_repository(self) -> None:
        """GitHubRepository should store full_name."""
        repo = GitHubRepository(id=1, name="repo", full_name="org/repo")
        assert repo.full_name == "org/repo"


class TestGitHubIssue:
    """Tests for the GitHubIssue model."""

    def test_create_issue_with_labels(self) -> None:
        """GitHubIssue should parse labels correctly."""
        issue = GitHubIssue(
            id=1,
            number=42,
            title="Test issue",
            labels=[GitHubLabel(id=1, name="agent:plan")],
        )
        assert len(issue.labels) == 1
        assert issue.labels[0].name == "agent:plan"

    def test_issue_body_can_be_none(self) -> None:
        """GitHubIssue body should allow None."""
        issue = GitHubIssue(id=1, number=1, title="Test")
        assert issue.body is None


class TestGitHubWebhookPayload:
    """Tests for the top-level GitHubWebhookPayload model."""

    def test_create_issues_event(self) -> None:
        """Payload should parse a standard issues event."""
        payload = GitHubWebhookPayload(
            action="opened",
            issue=GitHubIssue(
                id=1,
                number=42,
                title="[Application Plan] Build feature",
                labels=[GitHubLabel(id=1, name="agent:plan")],
            ),
            repository=GitHubRepository(id=1, name="repo", full_name="org/repo"),
        )
        assert payload.action == "opened"
        assert payload.issue is not None
        assert payload.issue.number == 42

    def test_event_labels_property(self) -> None:
        """event_labels should extract label names from the issue."""
        payload = GitHubWebhookPayload(
            action="opened",
            issue=GitHubIssue(
                id=1,
                number=1,
                title="Test",
                labels=[
                    GitHubLabel(id=1, name="agent:plan"),
                    GitHubLabel(id=2, name="bug"),
                ],
            ),
        )
        assert payload.event_labels == ["agent:plan", "bug"]

    def test_event_labels_empty_when_no_issue(self) -> None:
        """event_labels should return empty list when no issue is present."""
        payload = GitHubWebhookPayload(action="ping")
        assert payload.event_labels == []

    def test_is_plan_request_with_label(self) -> None:
        """is_plan_request should detect agent:plan label."""
        payload = GitHubWebhookPayload(
            action="opened",
            issue=GitHubIssue(
                id=1,
                number=1,
                title="Regular title",
                labels=[GitHubLabel(id=1, name="agent:plan")],
            ),
        )
        assert payload.is_plan_request is True

    def test_is_plan_request_with_title(self) -> None:
        """is_plan_request should detect [Application Plan] in title."""
        payload = GitHubWebhookPayload(
            action="opened",
            issue=GitHubIssue(
                id=1,
                number=1,
                title="[Application Plan] Build auth",
                labels=[],
            ),
        )
        assert payload.is_plan_request is True

    def test_is_not_plan_request(self) -> None:
        """is_plan_request should return False for regular issues."""
        payload = GitHubWebhookPayload(
            action="opened",
            issue=GitHubIssue(
                id=1,
                number=1,
                title="Fix typo in README",
                labels=[GitHubLabel(id=1, name="bug")],
            ),
        )
        assert payload.is_plan_request is False

    def test_extra_fields_allowed(self) -> None:
        """Payload should accept unknown fields (extra='allow')."""
        payload = GitHubWebhookPayload(
            action="opened",
            custom_field="allowed",
        )
        assert payload.action == "opened"
