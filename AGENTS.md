# AGENTS.md

> **Project instructions for AI coding agents working on this repository.**
> This file is the primary reference for how to build, test, lint, and contribute to OS-APOW.

---

## Project Overview

**workflow-orchestration-queue** (OS-APOW) is a **headless agentic orchestration platform** that transforms GitHub Issues into autonomous execution orders fulfilled by AI workers in isolated containers.

OS-APOW shifts AI-assisted development from interactive co-piloting to an autonomous background production service. Users open GitHub Issues with specifications, and the system autonomously plans, implements, tests, and submits Pull Requests via isolated AI worker DevContainers.

### The Four Pillars Architecture

| Pillar | Component | Tech Stack | Role |
|--------|-----------|------------|------|
| **The Ear** | `notifier_service.py` | FastAPI, Pydantic, HMAC validation | Secure webhook ingestion, event triage |
| **The State** | GitHub Issues + Labels | Labels as status, Assignees as locks | "Markdown-as-a-Database" — distributed state machine |
| **The Brain** | `orchestrator_sentinel.py` | Python asyncio, HTTPX, Docker CLI | Persistent polling, task claiming, worker lifecycle |
| **The Hands** | Opencode Worker | Docker DevContainer, opencode CLI, LLM | Isolated code execution against cloned codebase |

### Data Flow (Happy Path)

1. **Stimulus** — User opens a GitHub Issue with a specification template
2. **Notify** — GitHub Webhook hits The Ear (FastAPI on port 8000)
3. **Triage** — Notifier verifies HMAC, applies `agent:queued` label
4. **Claim** — Sentinel detects queued issue, assigns itself, updates to `agent:in-progress`
5. **Execute** — Sentinel provisions DevContainer, dispatches AI worker
6. **Finalize** — Worker completes, Sentinel applies terminal label, creates PR

---

## Setup Commands

| Action | Command |
|--------|---------|
| Install dependencies (runtime + dev) | `uv sync --dev` or `uv pip install -e ".[dev]"` |
| Run the notifier service | `uv run uvicorn workflow_orchestration_queue.notifier_service:app --reload` |
| Run main entry point | `uv run python -m workflow_orchestration_queue.main` |
| Run all tests | `uv run pytest tests/ -v` |
| Lint | `uv run ruff check src/ tests/` |
| Auto-fix lint issues | `uv run ruff check --fix src/ tests/` |
| Format check | `uv run ruff format --check src/ tests/` |
| Apply formatting | `uv run ruff format src/ tests/` |
| Type check | `uv run mypy src/` |
| Docker build | `docker compose up --build` |

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your tokens (WEBHOOK_SECRET, GITHUB_TOKEN, etc.)
```

---

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml                    # Core project definition (PEP 621), ruff/mypy/pytest config
├── Dockerfile                        # Multi-stage container build
├── docker-compose.yml                # Local development environment
├── src/
│   └── workflow_orchestration_queue/
│       ├── __init__.py               # Package metadata (version, title)
│       ├── main.py                   # Application entry point
│       ├── notifier_service.py       # FastAPI webhook ingestion (The Ear)
│       ├── orchestrator_sentinel.py  # Background polling service (The Brain)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── work_item.py          # WorkItem, Status, Type definitions (Pydantic v2)
│       │   └── github_events.py      # GitHub webhook payload schemas (Pydantic v2)
│       └── interfaces/
│           ├── __init__.py
│           └── i_task_queue.py       # Abstract queue operations (Strategy pattern)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Shared pytest fixtures
│   ├── test_notifier_service.py      # FastAPI endpoint tests (health, webhooks)
│   ├── test_work_item.py             # WorkItem model tests
│   └── test_github_events.py         # GitHub event model tests
├── scripts/                          # Shell bridge scripts + PowerShell helpers
├── plan_docs/                        # Architecture and planning documents (seeded — do not modify)
├── local_ai_instruction_modules/     # Markdown LLM instruction modules
├── docs/                             # User documentation
├── .opencode/                        # opencode agent definitions (template infrastructure)
└── .github/workflows/                # CI/CD pipelines (template + Python)
```

---

## Code Style

- **Python 3.12+** with type hints everywhere (enforced by mypy strict mode)
- **Pydantic v2** for all data validation and serialization
- **Google-style docstrings** for all public classes and methods
- **Ruff** for linting and formatting (replaces flake8, isort, black)
  - Line length: 100 characters
  - Quote style: double quotes
  - Import sorting: first-party imports grouped
- **Async/await patterns** for all I/O operations (HTTPX, FastAPI)
- **Always add/update tests** for changed code — target 80%+ coverage
- No hardcoded secrets or tokens — use environment variables and `pydantic-settings`

### Ruff Configuration (from `pyproject.toml`)

- Enabled rules: `E`, `W`, `F`, `I`, `N`, `UP`, `B`, `SIM`, `TCH`, `RUF`
- Target: Python 3.12
- `E501` (line length) ignored — handled by formatter

---

## Testing Instructions

| Action | Command |
|--------|---------|
| Run full suite | `uv run pytest tests/ -v` |
| Run single test file | `uv run pytest tests/test_work_item.py -v` |
| Run with coverage | `uv run pytest tests/ --cov=src/workflow_orchestration_queue` |
| Run with coverage report | `uv run pytest tests/ --cov --cov-report=term-missing` |
| Skip slow tests | `uv run pytest tests/ -v -m "not slow"` |
| Run integration tests only | `uv run pytest tests/ -v -m "integration"` |

- Tests use **pytest** with **pytest-asyncio** (auto mode)
- Shared fixtures live in `tests/conftest.py`
- Coverage minimum: **80%** (configured in `pyproject.toml`)
- Test markers: `slow` (long-running), `integration` (external services)

---

## Architecture Notes

### Four Pillars

- **The Ear** (`notifier_service.py`) — FastAPI app exposing `POST /webhooks/github`, `GET /health`, `GET /docs`. HMAC SHA256 validation on all webhook requests.
- **The State** — GitHub Issues as a distributed task queue. Labels drive state transitions: `agent:queued` → `agent:in-progress` → `agent:success` / `agent:error`. GitHub Assignees serve as distributed locks.
- **The Brain** (`orchestrator_sentinel.py`) — Python asyncio background service. Polls for `agent:queued` issues every 60s, claims tasks, provisions Docker DevContainers, dispatches AI workers.
- **The Hands** — Docker DevContainer running opencode CLI with LLM. Isolated execution (2 CPU / 4GB RAM limits, segregated bridge network).

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Polling-first resiliency** | Webhooks are fire-and-forget; polling ensures self-healing after restarts |
| **Markdown-as-a-Database** | GitHub Issues provide audit logs, versioning, and human intervention out-of-the-box |
| **Provider-agnostic ITaskQueue** | Strategy pattern prevents vendor lock-in; GitHub Issues today, Linear/Notion tomorrow |
| **Logic-as-Markdown** | AI behavioral logic in `local_ai_instruction_modules/` — update via PR without redeploying Python |
| **Shell-bridge execution** | Complex Docker logic stays in shell scripts; Python handles state and orchestration |

### Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.12+ |
| Web Framework | FastAPI + Uvicorn |
| Data Validation | Pydantic v2 |
| HTTP Client | HTTPX (async) |
| Settings | pydantic-settings |
| Package Manager | uv |
| Linter/Formatter | Ruff |
| Type Checker | MyPy (strict) |
| Test Framework | pytest + pytest-asyncio |
| Containers | Docker + Docker Compose |
| AI Runtime | opencode CLI |

---

## PR and Commit Guidelines

- **Commit format**: `type: description` where type is one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- **PR titles** should include the assignment/epic prefix (e.g., `project-setup: add AGENTS.md`)
- **Ensure all tests pass** before committing: `uv run pytest tests/ -v`
- **Run linter** before committing: `uv run ruff check src/ tests/`
- **Run formatter** before committing: `uv run ruff format --check src/ tests/`
- **Branch naming**: `dynamic-workflow-<workflow-name>` for dynamic workflow work (e.g., `dynamic-workflow-project-setup`)

---

## Common Pitfalls

- **Template infrastructure**: The repository contains template files (`.opencode/`, `.github/workflows/`, `.devcontainer/`) for the AI orchestration system — **do not remove or modify** these unless specifically instructed.
- **plan_docs/ is read-only**: Contains seeded planning documents — do not modify.
- **validate-python.yml vs validate.yml**: The existing `validate.yml` references .NET artifacts. Use `validate-python.yml` for Python CI.
- **Docker healthchecks**: Must use Python stdlib (`urllib.request`), NOT `curl` (not available in slim containers).
- **Dev dependencies**: `uv sync --dev` may not always install optional `[dev]` extras. Use `uv pip install -e ".[dev]"` if `ruff`, `pytest`, or `mypy` are missing.
- **Dockerfile source copy**: When using `uv pip install -e .`, ensure source is copied before the install step.
- **Async test fixtures**: Tests use `asyncio_mode = "auto"` — async test functions are automatically handled by pytest-asyncio.
