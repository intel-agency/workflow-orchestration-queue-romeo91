# Technology Stack — workflow-orchestration-queue (OS-APOW)

> **Document Version**: 1.0  
> **Last Updated**: 2026-04-27  
> **Source**: OS-APOW Implementation Specification v1, Architecture Guide v3, Development Plan v4

---

## 1. Primary Language

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12+ | Primary language for Orchestrator, API Webhook receiver, and all system logic. Chosen for optimal blend of asynchronous capabilities and robust text processing. |

### Secondary Languages

| Technology | Version | Purpose |
|-----------|---------|---------|
| **PowerShell Core (pwsh)** | 7.x | Shell Bridge scripts, auth synchronization, GitHub App token management |
| **Bash** | 5.x | Shell Bridge scripts (`devcontainer-opencode.sh`), cross-platform CLI interactions |

---

## 2. Web Framework & Server

| Package | Version | Purpose |
|---------|---------|---------|
| **FastAPI** | Latest stable | High-performance async web framework for the Webhook Notifier ("The Ear"). Chosen for native Pydantic integration, automatic OpenAPI generation, and speed. |
| **Uvicorn** | Latest stable | Lightning-fast ASGI web server to serve the FastAPI application in production. |
| **Pydantic** | v2 | Strict data validation, settings management, and complex data schemas for cross-component communication (`WorkItem`, `TaskType`, `WorkItemStatus`). |

---

## 3. HTTP & API Client

| Package | Version | Purpose |
|---------|---------|---------|
| **HTTPX** | Latest stable | Fully asynchronous HTTP client for GitHub REST API calls. Selected over `requests` for non-blocking event loop compatibility, significantly improving throughput. |

---

## 4. Package Management & Build

| Tool | Version | Purpose |
|------|---------|---------|
| **uv** | 0.10.9+ | Rust-based Python package installer and dependency resolver. Orders of magnitude faster than pip/poetry. Manages `pyproject.toml` and `uv.lock` for deterministic builds. |
| **pyproject.toml** | — | Core project definition file for dependencies and metadata (PEP 621 compliant). |
| **uv.lock** | — | Deterministic lockfile for exact package versions. |

---

## 5. Containerization & Infrastructure

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Docker** | Latest | Core worker execution engine providing sandboxing, environment consistency, and lifecycle hooks for LLM agents. |
| **DevContainers** | Latest | High-fidelity reproducible environments. The AI worker operates in a DevContainer bit-for-bit identical to a human developer's environment. |
| **Docker Compose** | Latest | Multi-container orchestration for complex tasks (e.g., web app + database testing). Issues `docker-compose down -v && up --build` between Epic tasks to enforce clean slate. |

### Container Constraints

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| CPU Limit | 2 CPUs | Prevent rogue agents from causing host DoS |
| RAM Limit | 4 GB | Ensure orchestrator stability |
| Network | Isolated bridge | Workers cannot access host subnets or metadata endpoints |

---

## 6. AI & LLM Runtime

| Technology | Version | Purpose |
|-----------|---------|---------|
| **opencode CLI** | 1.2.24 | AI agent runtime. Runs agents defined in `.opencode/agents/` with MCP server support. |
| **LLM Provider** | GLM-5 (ZhipuAI) | Primary language model driving the agentic worker. Configurable for alternative providers. |
| **MCP Servers** | Sequential Thinking, Memory | Model Context Protocol servers for structured reasoning and knowledge persistence. |

---

## 7. Shell Bridge Scripts

| Script | Language | Purpose |
|--------|----------|---------|
| `devcontainer-opencode.sh` | Bash | Core orchestrator→worker bridge. Commands: `up`, `start`, `prompt`. Manages Docker network, volumes, SSH-agent forwarding. |
| `gh-auth.ps1` | PowerShell | GitHub App authentication synchronization. Maintains scoped installation tokens. |
| `common-auth.ps1` | PowerShell | Shared authentication initialization (`Initialize-GitHubAuth`). |
| `update-remote-indices.ps1` | PowerShell | Vector index maintenance for proactive codebase indexing. |

---

## 8. Testing & Quality

| Tool | Purpose |
|------|---------|
| **pytest** | Primary test framework for Python |
| **pytest-asyncio** | Async test support for FastAPI and async Sentinel code |
| **pytest-cov** | Code coverage measurement |
| **ruff** | Modern Python linter and formatter (replaces flake8 + isort + black) |

### Test Coverage Target

- **Unit tests**: 80%+ coverage
- **Integration tests**: API endpoint testing, webhook signature validation
- **End-to-end tests**: Full workflow from issue creation to PR submission
- **Security tests**: HMAC validation, credential scrubbing, network isolation

---

## 9. Logging & Observability

| Technology | Purpose |
|-----------|---------|
| **Python `logging` module** | Structured logging with `StreamHandler` (console) and rotating `FileHandler` (disk) |
| **JSONL log format** | Machine-readable structured log files (`worker_run_ID_TIMESTAMP.jsonl`) |
| **SENTINEL_ID** | Unique instance identifier stamped on every log line for multi-node traceability |
| **GitHub Issue Comments** | Public telemetry via sanitized "Heartbeat" comments |

### Log Outputs

| Output | Audience | Content |
|--------|----------|---------|
| Worker stdout/stderr JSONL | System Administrators | Full execution context, sensitive dumps (encrypted at rest) |
| Sanitized GitHub Comments | Users/Developers | Regex-scrubbed progress updates with no secrets/tokens |
| Service Logs | Administrators | Sentinel/Notifier structured logs with SENTINEL_ID prefix |

---

## 10. Documentation & API

| Technology | Purpose |
|-----------|---------|
| **FastAPI Swagger/OpenAPI** | Auto-generated interactive API documentation at `/docs` endpoint |
| **Sphinx/Google-style docstrings** | Inline code documentation for all classes and methods |
| **Markdown instruction modules** | Decoupled LLM behavior logic in `/local_ai_instruction_modules/` |

---

## 11. Version Control & CI/CD

| Technology | Purpose |
|-----------|---------|
| **Git** | Version control |
| **GitHub Issues + Labels** | Primary database ("Markdown-as-a-Database") — state machine via labels |
| **GitHub Actions** | CI/CD pipeline (build, test, scan, publish) |
| **GitHub App** | Webhook integration, scoped installation tokens |

### Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready release |
| `develop` | Integration branch for CI, feature testing, and staging |

---

## 12. Security Stack

| Component | Mechanism |
|-----------|-----------|
| **Webhook Validation** | HMAC SHA256 (`X-Hub-Signature-256`) against `WEBHOOK_SECRET` |
| **Credential Scoping** | GitHub App Installation Tokens — temporary, in-memory only |
| **Credential Scrubbing** | Regex-based log sanitizer stripping tokens, private IPs, secrets |
| **Network Isolation** | Dedicated Docker bridge network for worker containers |
| **Resource Constraints** | cgroup limits (2 CPU, 4GB RAM) per worker container |

---

## 13. Development Tools

| Tool | Purpose |
|------|---------|
| **GitHub CLI (`gh`)** | API interaction (issues, PRs, repos, actions) |
| **ngrok / Tailscale** | Local-to-cloud tunneling for webhook development (Phase 2) |
| **MCP Sequential Thinking** | Structured step-by-step reasoning for planning agents |
| **MCP Memory** | Knowledge graph persistence across sessions |

---

## 14. Not Included (Out of Scope)

| Technology | Reason |
|-----------|--------|
| .NET / C# / global.json | This is a Python ecosystem project; .NET artifacts are template residuals |
| SQL Database | State lives in GitHub Issues (Markdown-as-a-Database) |
| Vector Database (Phase 1-2) | Deferred to Phase 3 (workspace vector indexing) |
| LangChain / LlamaIndex | Not used in Phase 1-2; Phase 3 may introduce LangChain for Architect Sub-Agent |
| Kubernetes | Docker and Docker Compose are sufficient for current scale |

---

*Generated from OS-APOW plan documents on 2026-04-27 as part of the `project-setup` workflow.*
