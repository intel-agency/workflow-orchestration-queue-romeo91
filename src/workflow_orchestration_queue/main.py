"""Application entry point for OS-APOW services.

Provides functions to launch the Notifier (FastAPI webhook receiver)
and the Sentinel Orchestrator (background polling service).
"""

import uvicorn


def run_notifier() -> None:
    """Launch the FastAPI Notifier service (The Ear)."""
    uvicorn.run(
        "workflow_orchestration_queue.notifier_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run_notifier()
