"""Sentinel orchestrator service — persistent polling and dispatch.

The "Brain" of OS-APOW. Polls the task queue, claims work items,
dispatches worker containers via the shell bridge, and reports results.

Reference spec: ``plan_docs/orchestrator_sentinel.py``
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import uuid
from typing import TYPE_CHECKING

from osapow.core.config import settings

if TYPE_CHECKING:
    from osapow.interfaces.i_task_queue import ITaskQueue
from osapow.models.work_item import WorkItem, WorkItemStatus, WorkItemType

logger = logging.getLogger(__name__)

# Workflow-to-instruction mapping
_WORKFLOW_MAP: dict[WorkItemType, str] = {
    WorkItemType.APPLICATION_PLAN: "create-app-plan.md",
    WorkItemType.EPIC: "perform-task.md",
    WorkItemType.STORY: "perform-task.md",
    WorkItemType.TASK: "perform-task.md",
    WorkItemType.BUGFIX: "recover-from-error.md",
}


async def _run_shell_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Invoke the shell bridge (``devcontainer-opencode.sh``).

    Args:
        args: Command and arguments to execute.

    Returns:
        A ``CompletedProcess`` with decoded stdout/stderr.
    """
    logger.info("Executing bridge: %s", " ".join(args))
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    return subprocess.CompletedProcess(
        args=args,
        returncode=process.returncode or 0,
        stdout=stdout.decode().strip() if stdout else "",
        stderr=stderr.decode().strip() if stderr else "",
    )


class Sentinel:
    """Orchestrator that polls for queued tasks and dispatches workers.

    Args:
        queue: The task queue backend (e.g., ``GitHubIssuesQueue``).
    """

    def __init__(self, queue: ITaskQueue) -> None:
        self.queue = queue
        self.sentinel_id = settings.sentinel_id or f"sentinel-{uuid.uuid4().hex[:8]}"
        self.poll_interval = settings.sentinel_poll_interval

    async def process_task(self, item: WorkItem) -> None:
        """Execute the full lifecycle for a single work item.

        1. Provision infrastructure (``devcontainer-opencode.sh up``)
        2. Start opencode server (``devcontainer-opencode.sh start``)
        3. Dispatch agent workflow (``devcontainer-opencode.sh prompt``)
        4. Report success or failure to the queue
        """
        logger.info("Processing task #%d (%s)", item.issue_number, item.item_type.value)

        try:
            # Step 1: Initialize infrastructure
            res_up = await _run_shell_command([settings.shell_bridge_path, "up"])
            if res_up.returncode != 0:
                err = f"**Infrastructure Failure** during `up` stage:\n```\n{res_up.stderr}\n```"
                await self.queue.update_status(item, WorkItemStatus.INFRA_FAILURE, err)
                return

            # Step 2: Start opencode server
            res_start = await _run_shell_command([settings.shell_bridge_path, "start"])
            if res_start.returncode != 0:
                err = (
                    f"**Infrastructure Failure** starting `opencode-server`:\n"
                    f"```\n{res_start.stderr}\n```"
                )
                await self.queue.update_status(item, WorkItemStatus.INFRA_FAILURE, err)
                return

            # Step 3: Dispatch agent workflow
            workflow = _WORKFLOW_MAP.get(item.item_type, "perform-task.md")
            instruction = f"Execute workflow {workflow} for context: {item.source_url}"

            res_prompt = await _run_shell_command(
                [settings.shell_bridge_path, "prompt", instruction]
            )

            # Step 4: Report result
            if res_prompt.returncode == 0:
                msg = (
                    f"**Workflow Complete**\n"
                    f"Sentinel `{self.sentinel_id}` successfully executed `{workflow}`. "
                    f"Please review Pull Requests."
                )
                await self.queue.update_status(item, WorkItemStatus.SUCCESS, msg)
            else:
                log_tail = res_prompt.stderr[-1500:] if res_prompt.stderr else "No error output."
                msg = f"**Execution Error** during `{workflow}`:\n```\n...{log_tail}\n```"
                await self.queue.update_status(item, WorkItemStatus.ERROR, msg)

        except Exception:
            logger.exception("Internal Sentinel error on task #%d", item.issue_number)
            await self.queue.update_status(
                item,
                WorkItemStatus.INFRA_FAILURE,
                "Sentinel encountered an unhandled exception.",
            )

    async def run_forever(self) -> None:
        """Enter the main polling loop.

        Runs indefinitely, polling at ``sentinel_poll_interval`` seconds.
        Sequential task processing in Phase 1 to prevent resource exhaustion.
        """
        logger.info(
            "Sentinel %s entering polling loop (interval: %ds)",
            self.sentinel_id,
            self.poll_interval,
        )

        while True:
            try:
                tasks = await self.queue.fetch_queued()
                if tasks:
                    logger.info("Found %d queued task(s).", len(tasks))
                    for task in tasks:
                        if await self.queue.claim_task(task, self.sentinel_id):
                            await self.process_task(task)
                            break  # one at a time in Phase 1
            except Exception:
                logger.exception("Polling cycle error")

            await asyncio.sleep(self.poll_interval)


def run_sentinel() -> None:
    """Entry point for the ``osapow-sentinel`` console script."""
    from osapow.services.queue import GitHubIssuesQueue

    # Validate required configuration
    missing = []
    if not settings.github_token:
        missing.append("GITHUB_TOKEN")
    if not settings.github_org:
        missing.append("GITHUB_ORG")
    if not settings.github_repo:
        missing.append("GITHUB_REPO")

    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        raise SystemExit(1)

    queue = GitHubIssuesQueue(
        token=settings.github_token,
        org=settings.github_org,
        repo=settings.github_repo,
    )
    sentinel = Sentinel(queue)

    try:
        asyncio.run(sentinel.run_forever())
    except KeyboardInterrupt:
        logger.info("Sentinel shutting down gracefully.")
