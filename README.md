# OS-APOW — Operational Status and Automated Processing of Workflows

A headless agentic orchestration platform that transforms GitHub Issues, Epics, and Kanban board movements into automated Execution Orders, dispatching specialized AI agents running in isolated DevContainers.

## Overview

OS-APOW shifts AI from a passive assistant to an autonomous background production service. It natively integrates into existing Agile workflows by translating standard project management artifacts into automated Execution Orders. A product manager simply writes an issue description, applies a label, and the system:

1. Detects the intent via webhook or polling
2. Dispatches an AI worker in an isolated DevContainer
3. The worker clones the repository, generates code, runs tests
4. Submits a fully formatted Pull Request for human review

## Architecture

The system is decomposed into four pillars:

| Pillar | Component | Technology |
|--------|-----------|------------|
| **The Ear** | Work Event Notifier | FastAPI + Uvicorn + Pydantic |
| **The State** | Work Queue | GitHub Issues + Labels |
| **The Brain** | Sentinel Orchestrator | Python async + HTTPX |
| **The Hands** | Opencode Worker | Docker DevContainers + GLM-5 |

See [plan_docs/architecture.md](plan_docs/architecture.md) for detailed architecture documentation.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker & Docker Compose (for full stack)

### Local Development

```bash
# Install dependencies
uv sync --extra dev

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Run the API server
uv run uvicorn osapow.main:app --reload

# Run tests
uv run pytest tests/ -v

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

### Docker Compose

```bash
# Start full stack (app + PostgreSQL + Redis)
docker compose up --build

# Clean slate reset
docker compose down -v
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
├── src/osapow/              # Main application source
│   ├── api/                 # FastAPI routes (webhooks, health)
│   ├── core/                # Configuration, security, logging
│   ├── interfaces/          # Abstract base classes (ITaskQueue)
│   ├── models/              # Pydantic data models
│   ├── services/            # Business logic (notifier, sentinel, queue)
│   └── main.py              # FastAPI app entry point
├── tests/                   # Pytest test suite
├── plan_docs/               # Architecture and planning documents
├── scripts/                 # Shell bridge and helper scripts
├── docs/                    # Additional documentation
├── .github/workflows/       # CI/CD pipelines
├── pyproject.toml           # Project configuration (uv, ruff, mypy, pytest)
├── Dockerfile               # Multi-stage Docker build
└── docker-compose.yml       # Full stack local development
```

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Web Framework | FastAPI | 0.110+ |
| ASGI Server | Uvicorn | 0.29+ |
| Data Validation | Pydantic | 2.x |
| Async HTTP | HTTPX | 0.27+ |
| Package Manager | uv | 0.10+ |
| Containerization | Docker + Docker Compose | Latest |
| Agent Runtime | opencode CLI | 1.2.24+ |
| LLM | GLM-5 (ZhipuAI) | — |
| State Store | GitHub Issues + Labels | REST API v3 |
| CI/CD | GitHub Actions | SHA-pinned |
| Testing | pytest + pytest-asyncio | Latest |
| Linting | Ruff | Latest |

## Development Phases

| Phase | Name | Status |
|-------|------|--------|
| Phase 0 | Seeding & Bootstrapping | Complete |
| Phase 1 | The Sentinel (MVP) | In Progress |
| Phase 2 | The Ear (Webhook Automation) | Planned |
| Phase 3 | Deep Orchestration & Self-Healing | Planned |

## Repository Summary

See [.ai-repository-summary.md](.ai-repository-summary.md) for a comprehensive repository overview.

## License

MIT
