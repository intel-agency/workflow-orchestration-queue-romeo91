# workflow-orchestration-queue (OS-APOW)

> **Opencode-Server Agent Workflow Orchestration**

A **headless agentic orchestration platform** that transforms the paradigm of AI-assisted software development from *interactive co-piloting* to *autonomous background production service*.

OS-APOW natively integrates into existing Agile workflows, translating standard project management artifacts (GitHub Issues, Epics, Kanban board movements) into automated **Execution Orders** fulfilled by specialized AI agents operating in isolated, reproducible DevContainers.

**Key Outcome**: "Zero-Touch Construction" — open a single Specification Issue and receive a functional, test-passed branch and Pull Request within minutes.

---

## Architecture — The Four Pillars

| Pillar | Component | Tech Stack | Role |
|--------|-----------|------------|------|
| **The Ear** | Work Event Notifier | Python 3.12, FastAPI, Pydantic | Secure webhook ingestion, HMAC validation, event triage |
| **The State** | Work Queue | GitHub Issues, Labels, Milestones | "Markdown-as-a-Database" — distributed state via GitHub labels |
| **The Brain** | Sentinel Orchestrator | Python Async, HTTPX, Docker CLI | Persistent polling, task claiming, worker lifecycle management |
| **The Hands** | Opencode Worker | Docker DevContainer, opencode CLI, LLM | Isolated code execution against cloned codebase |

### System Overview

```
┌───────────┐     ┌──────────────┐     ┌───────────────────┐
│  THE EAR  │────>│  THE STATE   │────>│   THE BRAIN       │
│ (Notifier)│     │ (Work Queue) │     │ (Sentinel Orch.)  │
└───────────┘     └──────────────┘     └───────┬───────────┘
                                                │
                                                v
                                        ┌───────────────────┐
                                        │   THE HANDS       │
                                        │ (Opencode Worker) │
                                        └───────────────────┘
```

---

## Prerequisites

- **Python 3.12+**
- **uv** — Rust-based Python package manager ([install guide](https://docs.astral.sh/uv/))
- **Docker** (for containerized development and worker execution)
- **Git** with access to the target repository

---

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/your-org/workflow-orchestration-queue.git
cd workflow-orchestration-queue
uv sync --dev
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual tokens and configuration
```

### 3. Run the Notifier Service

```bash
uv run uvicorn workflow_orchestration_queue.notifier_service:app --reload
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

### 4. Run with Docker

```bash
docker compose up --build
```

---

## Development Setup

### Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync --dev

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>
```

### Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml                    # Core project definition (PEP 621)
├── Dockerfile                        # Multi-stage container build
├── docker-compose.yml                # Local development environment
├── src/
│   └── workflow_orchestration_queue/
│       ├── __init__.py               # Package metadata
│       ├── main.py                   # Application entry point
│       ├── notifier_service.py       # FastAPI webhook ingestion (The Ear)
│       ├── orchestrator_sentinel.py  # Background polling service (The Brain)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── work_item.py          # WorkItem, Status, Type definitions
│       │   └── github_events.py      # GitHub webhook payload schemas
│       └── interfaces/
│           ├── __init__.py
│           └── i_task_queue.py       # Abstract queue operations
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Shared pytest fixtures
│   ├── test_notifier_service.py      # Notifier smoke tests
│   ├── test_work_item.py             # WorkItem model tests
│   └── test_github_events.py         # GitHub event model tests
├── scripts/                          # Shell bridge execution layer
├── docs/                             # Architecture and user documentation
├── plan_docs/                        # Project planning documents
└── local_ai_instruction_modules/     # Decoupled Markdown LLM logic
```

---

## Running Tests

```bash
# Run all tests with verbose output
uv run pytest tests/ -v

# Run with coverage report
uv run pytest tests/ --cov --cov-report=term-missing

# Run a specific test file
uv run pytest tests/test_work_item.py -v

# Run only smoke tests (fast)
uv run pytest tests/ -v -m "not slow"
```

---

## Linting and Formatting

```bash
# Check for lint errors
uv run ruff check src/ tests/

# Auto-fix lint errors
uv run ruff check --fix src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Apply formatting
uv run ruff format src/ tests/

# Type checking
uv run mypy src/
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Polling-first resiliency** | Webhooks are fire-and-forget; polling ensures self-healing after restarts |
| **Markdown-as-a-Database** | GitHub Issues provide audit logs, versioning, and human intervention out-of-the-box |
| **Provider-agnostic ITaskQueue** | Prevents vendor lock-in; GitHub Issues today, Linear/Notion tomorrow |
| **Logic-as-Markdown** | AI behavioral logic in `/local_ai_instruction_modules/` — update via PR without redeploying Python |
| **Shell-bridge execution** | Complex Docker logic stays in shell scripts; Python handles state and orchestration |

---

## Documentation

- [Architecture Guide](plan_docs/OS-APOW%20Architecture%20Guide%20v3.md) — System diagrams, ADRs, security boundaries
- [Development Plan](plan_docs/OS-APOW%20Development%20Plan%20v4.md) — Phase-by-phase roadmap and user stories
- [Implementation Spec](plan_docs/OS-APOW%20Implementation%20Specification%20v1.md) — Full requirements and test cases
- [Tech Stack](plan_docs/tech-stack.md) — Complete technology stack reference
- [Architecture Summary](plan_docs/architecture.md) — Architecture document generated from plan docs

---

## Phased Evolution

| Phase | Name | Focus |
|-------|------|-------|
| **0** | Seeding & Bootstrapping | Template clone, plan seeding, project setup (current) |
| **1** | The Sentinel (MVP) | Polling engine, shell-bridge dispatch, status feedback |
| **2** | The Ear (Webhook) | FastAPI receiver, HMAC validation, triage |
| **3** | Deep Orchestration | Hierarchical decomposition, self-healing, codebase indexing |

---

## License

MIT
