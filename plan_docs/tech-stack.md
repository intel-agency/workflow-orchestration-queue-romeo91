# OS-APOW Technology Stack

> **Project:** workflow-orchestration-queue (OS-APOW — Opencode-Server Agent Workflow Orchestration Queue)
> **Last Updated:** 2026-04-20
> **Source:** Derived from OS-APOW Implementation Specification v1, Architecture Guide v3, Development Plan v4

---

## 1. Languages

| Language | Version | Purpose |
|---|---|---|
| **Python** | 3.12+ | Primary language for the Orchestrator (Sentinel), the API Webhook receiver (Notifier), models, interfaces, and all system logic. Chosen for its async capabilities, rich text processing ecosystem, and AI/ML library support. |
| **PowerShell Core (pwsh)** | 7.x | Shell Bridge authentication scripts (`gh-auth.ps1`, `common-auth.ps1`), label management, and cross-platform administrative CLI interactions. |
| **Bash** | 5.x | Shell Bridge execution scripts (`devcontainer-opencode.sh`), DevContainer lifecycle management, and CI/CD glue scripts. |

## 2. Frameworks

| Framework | Version | Purpose |
|---|---|---|
| **FastAPI** | 0.110+ | High-performance async web framework for the Work Event Notifier ("The Ear"). Selected for native Pydantic integration, automatic OpenAPI/Swagger documentation generation, and ASGI performance. |
| **Uvicorn** | 0.29+ | Lightning-fast ASGI web server implementation serving the FastAPI application in production. |
| **Pydantic** | 2.x | Strict data validation, settings management, and schema definition for cross-component data structures (`WorkItem`, `WorkItemStatus`, `WorkItemType`, `TaskType`, GitHub event payload models). |

## 3. Libraries & Packages

| Package | Purpose |
|---|---|
| **HTTPX** | Fully asynchronous HTTP client for non-blocking GitHub REST API calls from the Sentinel. Selected over `requests` to avoid blocking the event loop, significantly improving throughput during polling cycles. |
| **hmac / hashlib** (stdlib) | HMAC SHA256 cryptographic signature verification for webhook payload authentication against `WEBHOOK_SECRET`. |
| **asyncio** (stdlib) | Core async runtime for the Sentinel's polling loop, shell bridge subprocess management, and concurrent task processing. |
| **subprocess** (stdlib) | Async subprocess execution for invoking the shell bridge (`devcontainer-opencode.sh up/start/prompt`). |
| **json / jsonlines** | JSON-structured log persistence (`worker_run_ID.jsonl`) and GitHub API payload parsing. |
| **logging** (stdlib) | Structured service logging with `StreamHandler` (console) and rotating `FileHandler` (disk), stamped with `SENTINEL_ID`. |
| **pytest** | Test framework for unit and integration tests. |
| **pytest-asyncio** | Async test support for testing the Sentinel's polling and task processing logic. |
| **respx** | HTTPX mocking library for testing GitHub API interactions without real network calls. |
| **httpx** (test client) | Used via `FastAPI.TestClient` / `httpx.AsyncClient` for testing webhook endpoints. |

## 4. Package Manager & Build Tools

| Tool | Version | Purpose |
|---|---|---|
| **uv** | 0.10+ | Rust-based Python package installer and dependency resolver. Orders of magnitude faster than pip/poetry. Manages `pyproject.toml` and `uv.lock` for deterministic, reproducible builds. |
| **pyproject.toml** | — | Core project definition file declaring dependencies, metadata, entry points, and tool configuration (Ruff, pytest, mypy). |
| **uv.lock** | — | Deterministic lockfile ensuring exact package version pinning across all environments. |

## 5. Infrastructure & Containerization

| Tool | Purpose |
|---|---|
| **Docker** | Core isolation and execution engine for worker DevContainers. Provides sandboxing, reproducibility, and environment parity. |
| **Docker Compose** | Multi-container orchestration for complex task environments (e.g., web app + PostgreSQL). Enforced clean-slate resets between major tasks via `docker-compose down -v && up --build`. |
| **DevContainers** | High-fidelity containerized development environment specification. Worker containers use the same DevContainer as human developers, eliminating "it works on my machine" discrepancies. |
| **GitHub Actions** | CI/CD platform for automated testing, linting, Docker image publishing, and DevContainer prebuilding. All action versions pinned by SHA for supply-chain security. |

## 6. Agent Runtime & AI

| Tool | Purpose |
|---|---|
| **opencode CLI** | AI agent runtime (v1.2.24+). Executes agents defined in `.opencode/agents/` with MCP server support. Runs inside worker DevContainers. |
| **GLM-5** (via ZHIPU_API_KEY) | Primary LLM model driving the opencode worker agents. |
| **MCP Servers** | `@modelcontextprotocol/server-sequential-thinking` (step-by-step reasoning), `@modelcontextprotocol/server-memory` (knowledge graph persistence). |

## 7. Data & State Management

| Layer | Technology | Purpose |
|---|---|---|
| **Task Queue** | GitHub Issues + Labels | "Markdown as a Database" — distributed state management via issue labels (`agent:queued`, `agent:in-progress`, `agent:success`, `agent:error`, `agent:infra-failure`, `agent:stalled-budget`). Assignees serve as distributed locks. |
| **State Machine** | GitHub Labels | State transitions: `agent:queued` → `agent:in-progress` → `agent:success` / `agent:error` / `agent:infra-failure`. Special state `agent:reconciling` for stale task recovery. |
| **Logging (Worker)** | Local JSONL files | Raw stdout/stderr captured to `worker_run_ID_TIMESTAMP.jsonl` on the host. Encrypted at rest. Retained for forensic analysis. |
| **Logging (Telemetry)** | GitHub Issue Comments | Sanitized "Heartbeat" comments posted to issue UI. Regex-based scrubber removes all tokens, secrets, and private IPs before posting. |

## 8. Security & Authentication

| Mechanism | Purpose |
|---|---|
| **HMAC SHA256** | Webhook payload signature verification (`X-Hub-Signature-256`) to prevent spoofing and prompt injection. |
| **GitHub App Installation Tokens** | Ephemeral, scoped tokens dynamically generated by the Sentinel and injected into worker containers as in-memory environment variables. Destroyed on container exit. |
| **Docker Network Isolation** | Worker containers operate in a segregated bridge network, preventing access to host subnets, metadata endpoints (AWS IMDS), and peer containers. |
| **Resource Constraints** | cgroup limits: 2 CPUs, 4GB RAM per worker container to prevent rogue agent DoS. |
| **Credential Scrubbing** | Regex-based sanitization of all log output before posting to public GitHub comments. |

## 9. Development & Code Quality

| Tool | Purpose |
|---|---|
| **Ruff** | Fast Python linter and formatter (replaces Flake8, isort, Black). Configured via `pyproject.toml`. |
| **mypy** | Static type checking for Python, ensuring type safety across models, interfaces, and implementations. |
| **pytest** | Unit, integration, and E2E test execution with coverage reporting. |
| **Sphinx / Google-style docstrings** | Inline code documentation using standard docstring format for all classes and methods. |

## 10. CI/CD Pipeline

| Workflow | Purpose |
|---|---|
| **validate** | Lint, scan, test, and DevContainer build verification. Runs on push and PR. |
| **publish-docker** | Build and push base Docker image to GHCR with branch-latest and versioned tags. |
| **prebuild-devcontainer** | Layer DevContainer Features on published Docker image (triggered by `workflow_run` on `publish-docker` completion). |
| **orchestrator-agent** | Assemble structured prompt, spin up devcontainer, and run opencode agent for task execution. |

---

## Summary Matrix

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.12+ |
| Language | PowerShell Core | 7.x |
| Language | Bash | 5.x |
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
| Testing | pytest + pytest-asyncio + respx | Latest |
| Linting | Ruff | Latest |
| Type Checking | mypy | Latest |
