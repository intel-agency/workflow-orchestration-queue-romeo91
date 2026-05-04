"""OS-APOW Sentinel Orchestrator (The Brain).

Background polling service that discovers queued WorkItems from the task queue,
claims them for execution, manages the worker lifecycle via shell-bridge scripts,
and reports results back to the queue.

Phase 1 uses a polling-first approach for resilience against server downtime.
"""

import asyncio
import logging
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime

from workflow_orchestration_queue.interfaces.i_task_queue import ITaskQueue
from workflow_orchestration_queue.models.work_item import TaskType, WorkItem, WorkItemStatus

# Unique instance identification for concurrency safety
SENTINEL_ID = os.getenv("SENTINEL_ID", f"sentinel-{uuid.uuid4().hex[:8]}")
POLL_INTERVAL = int(os.getenv("SENTINEL_POLL_INTERVAL", "60"))
SHELL_BRIDGE_PATH = os.getenv("SHELL_BRIDGE_PATH", "./scripts/devcontainer-opencode.sh")

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s [%(levelname)s] {SENTINEL_ID} - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("OS-APOW.Sentinel")


async def run_shell_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Invoke the local shell bridge (devcontainer-opencode.sh).

    Executes commands in a subprocess and captures stdout/stderr.
    """
    logger.info("Executing Bridge: %s", " ".join(args))
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    return subprocess.CompletedProcess(
        args=args,
        returncode=process.returncode or 0,
        stdout=stdout.decode().strip() if stdout else "",
        stderr=stderr.decode().strip() if stderr else "",
    )


class Sentinel:
    """Orchestrator that manages the full lifecycle of work item execution.

    Polls for queued tasks, claims them, dispatches to worker containers,
    monitors execution, and finalizes the task status.
    """

    def __init__(self, queue: ITaskQueue) -> None:
        self.queue = queue

    async def process_task(self, item: WorkItem) -> None:
        """Execute a single work item through the shell-bridge pipeline."""
        logger.info("Processing Task #%s...", item.issue_number)

        try:
            # Step 1: Initialize infrastructure
            res_up = await run_shell_command([SHELL_BRIDGE_PATH, "up"])
            if res_up.returncode != 0:
                await self.queue.update_status(
                    item.provider_id,
                    WorkItemStatus.INFRA_FAILURE,
                    f"Infrastructure Failure during 'up' stage:\n{res_up.stderr}",
                )
                return

            # Step 2: Start opencode server
            res_start = await run_shell_command([SHELL_BRIDGE_PATH, "start"])
            if res_start.returncode != 0:
                await self.queue.update_status(
                    item.provider_id,
                    WorkItemStatus.INFRA_FAILURE,
                    f"Infrastructure Failure starting opencode-server:\n{res_start.stderr}",
                )
                return

            # Step 3: Dispatch workflow instruction
            workflow_map: dict[TaskType, str] = {
                TaskType.PLAN: "create-app-plan.md",
                TaskType.IMPLEMENT: "perform-task.md",
                TaskType.BUGFIX: "recover-from-error.md",
            }
            workflow = workflow_map.get(item.task_type, "perform-task.md")
            instruction = f"Execute workflow {workflow} for context: {item.source_url}"

            res_prompt = await run_shell_command([SHELL_BRIDGE_PATH, "prompt", instruction])

            # Step 4: Handle completion
            if res_prompt.returncode == 0:
                await self.queue.update_status(
                    item.provider_id,
                    WorkItemStatus.SUCCESS,
                    f"Workflow '{workflow}' completed successfully.",
                )
            else:
                log_tail = (
                    res_prompt.stderr[-1500:] if res_prompt.stderr else "No error output captured."
                )
                await self.queue.update_status(
                    item.provider_id,
                    WorkItemStatus.ERROR,
                    f"Execution Error during '{workflow}':\n{log_tail}",
                )

        except Exception as e:
            logger.exception("Internal Sentinel Error on Task #%s", item.issue_number)
            await self.queue.update_status(
                item.provider_id,
                WorkItemStatus.INFRA_FAILURE,
                f"Sentinel encountered an unhandled exception: {e}",
            )

    async def run_forever(self) -> None:
        """Main polling loop. Discovers and processes queued tasks."""
        logger.info(
            "Sentinel %s entering polling loop (Interval: %ds)",
            SENTINEL_ID,
            POLL_INTERVAL,
        )

        while True:
            try:
                tasks = await self.queue.fetch_queued_items()
                if tasks:
                    logger.info("Found %d queued task(s).", len(tasks))
                    for task in tasks:
                        if await self.queue.claim_task(task.provider_id, SENTINEL_ID):
                            await self.process_task(task)
                            break  # Sequential processing for Phase 1
            except Exception as e:
                logger.error("Polling cycle error: %s", e)

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    env_vars = ["GITHUB_TOKEN", "GITHUB_REPOSITORY"]
    missing = [v for v in env_vars if not os.getenv(v)]
    if missing:
        logger.error("Critical Error: Missing environment variables: %s", ", ".join(missing))
        sys.exit(1)

    logger.info("Sentinel %s starting at %s", SENTINEL_ID, datetime.now(UTC).isoformat())
