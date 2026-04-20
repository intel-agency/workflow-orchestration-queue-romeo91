"""Health check endpoint.

Provides liveness/readiness probes for container orchestration and
monitoring systems.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return service health status.

    Returns:
        A JSON object with ``status`` and ``system`` keys.
    """
    return {"status": "online", "system": "OS-APOW Notifier"}
