"""Dockerfile for the OS-APOW application.

Multi-stage build using uv for fast dependency installation.
"""

# ── Stage 1: Build ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project definition first for layer caching
COPY pyproject.toml ./
COPY .python-version ./
COPY src/ src/

# Install dependencies (no dev deps in production image)
RUN uv pip install --system --no-cache .

# ── Stage 2: Runtime ────────────────────────────────────────────
FROM python:3.12-slim

# Non-root user for security
RUN groupadd --gid 1000 osapow && \
    useradd --uid 1000 --gid osapow --shell /bin/bash --create-home osapow

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/osapow-api /usr/local/bin/osapow-api
COPY --from=builder /usr/local/bin/osapow-sentinel /usr/local/bin/osapow-sentinel

# Copy application source
COPY src/ src/

# Switch to non-root user
USER osapow

EXPOSE 8000

# Default: run the API server
CMD ["uvicorn", "osapow.main:app", "--host", "0.0.0.0", "--port", "8000"]
