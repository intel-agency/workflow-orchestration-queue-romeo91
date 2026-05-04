# OS-APOW Multi-stage Docker Build
# Stage 1: Build — install dependencies with uv
# Stage 2: Runtime — minimal production image

# ---- Build Stage ----
FROM python:3.12-slim AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

# Copy dependency manifest first for layer caching
COPY pyproject.toml ./

# Copy source code before editable install
COPY src/ src/

# Install project and dependencies
RUN uv pip install --system -e ".[dev]"

# ---- Runtime Stage ----
FROM python:3.12-slim AS runtime

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Copy source code
COPY src/ src/
COPY pyproject.toml ./

# Expose FastAPI port
EXPOSE 8000

# Health check using Python stdlib (no curl dependency)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

# Run the notifier service
CMD ["uvicorn", "workflow_orchestration_queue.notifier_service:app", "--host", "0.0.0.0", "--port", "8000"]
