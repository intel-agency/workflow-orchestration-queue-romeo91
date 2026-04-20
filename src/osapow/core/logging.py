"""Structured logging configuration.

Provides consistent, timestamped log output stamped with the Sentinel ID
for attribution in multi-node deployments.
"""

from __future__ import annotations

import logging
import sys

from osapow.core.config import settings


def setup_logging() -> None:
    """Configure structured logging with console and file handlers.

    Every log line includes the ``SENTINEL_ID`` for attribution in
    multi-node deployment clusters.
    """
    sentinel_id = settings.sentinel_id or "standalone"
    log_format = f"%(asctime)s [%(levelname)s] {sentinel_id} - %(name)s - %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # File handler (rotating)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            "osapow.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)
    except Exception:
        # File logging is best-effort; don't fail startup
        pass


# Required for RotatingFileHandler (imported inside function for stdlib)
import logging.handlers  # noqa: E402
