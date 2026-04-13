# Technology Stack — workflow-orchestration-queue (OS-APOW)

> **Source:** Derived from OS-APOW Implementation Specification v1, Architecture Guide v3, and Development Plan v4.

---

## Languages

| Language | Version | Role |
|----------|---------|------|
| **Python** | 3.12+ | Primary language for Orchestrator, API Webhook receiver, models, and all system logic |
| **PowerShell Core (pwsh)** | 7.x | Shell Bridge scripts, GitHub auth synchronization, cross-platform CLI interactions |
| **Bash** | — | Supporting shell scripts for container lifecycle and devcontainer orchestration |

## Frameworks & Libraries

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | FastAPI | Latest (via uv) | High-performance async webhook receiver (The Ear); automatic OpenAPI/Swagger docs |
| **ASGI Server** | Uvicorn | Latest | Production ASGI server for FastAPI application |
| **Validation** | Pydantic | v2 | Strict data validation, settings management, WorkItem/TaskType/WorkItemStatus schemas |
| **Async HTTP Client** | HTTPX | Latest | Fully async REST API calls to GitHub; non-blocking event loop |
| **Testing** | pytest | Latest | Unit, integration, and end-to-end testing |
| **Linting** | Ruff | Latest | Fast Python linter and formatter |

## Package Management

| Tool | Version | Purpose |
|------|---------|---------|
| **uv** | 0.10.x+ | Rust-based Python package installer and dependency resolver; manages `pyproject.toml` and `uv.lock` |

## Containerization

| Technology | Purpose |
|-----------|---------|
| **Docker** | Worker container sandboxing, network isolation, resource constraints |
| **Docker Compose** | Multi-container orchestration; environment reset between tasks (`docker-compose down -v && up --build`) |
| **DevContainers** | High-fidelity development environment for Opencode Worker (bit-for-bit identical to local developer environment) |

## API & Integration

| API | Purpose |
|-----|---------|
| **GitHub REST API v3** | Primary interface for Issue/Label state machine, PR creation, comment posting, assignee locking |
| **GitHub Webhooks** | Event-driven triggers (issues, issue_comment, pull_request_review) for The Ear |
| **GitHub App Installation Tokens** | Authenticated API access (5,000 requests/hr); HMAC SHA256 webhook signature verification |

## AI/LLM Runtime

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent Runtime** | opencode CLI (v1.2.24) | AI agent execution inside DevContainer; reads markdown instruction modules |
| **Models** | ZhipuAI GLM (zai-coding-plan/glm-5) | Primary LLM for code generation, planning, and analysis |

## CI/CD

| Platform | Purpose |
|----------|---------|
| **GitHub Actions** | Automated workflows: build, test, lint, security scan, Docker publish, devcontainer prebuild |

## Security

| Mechanism | Purpose |
|-----------|---------|
| **HMAC SHA256** | Cryptographic verification of all incoming webhook payloads (X-Hub-Signature-256) |
| **Docker Network Isolation** | Worker containers in segregated bridge network; no host subnet access |
| **Ephemeral Credentials** | GitHub tokens injected as in-memory env vars; destroyed on container exit |
| **Credential Scrubbing** | Regex-based log sanitization for public telemetry; encrypted raw logs for forensics |

## Project Configuration

| File | Purpose |
|------|---------|
| `pyproject.toml` | Core dependency definition and project metadata (uv-managed) |
| `uv.lock` | Deterministic lockfile for exact package versions |
| `.env` | Environment configuration (tokens, secrets, polling intervals) |

---

## Not Included

- **.NET / global.json** — This is a Python/Shell ecosystem; .NET is not used
- **SQL Database** — State is managed via GitHub Issues/Labels ("Markdown as a Database")
- **Message Queue** — No RabbitMQ/Redis; GitHub Labels serve as the distributed queue
