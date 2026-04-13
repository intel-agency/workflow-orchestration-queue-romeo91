# Architecture — workflow-orchestration-queue (OS-APOW)

> **Source:** Derived from OS-APOW Architecture Guide v3, Development Plan v4, and Implementation Specification v1.

---

## System Overview

workflow-orchestration-queue (OS-APOW) is a **headless agentic orchestration platform** that transforms GitHub Issues into autonomous development tasks. The system replaces the traditional human-in-the-loop AI coding model with a persistent, event-driven infrastructure that dispatches specialized AI workers to fulfill specification-driven tasks without human intervention.

The architecture is organized around four conceptual pillars, each handling a distinct domain:

```
┌─────────────────────────────────────────────────────────────────┐
│                    OS-APOW System Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │  The Ear     │────▶│  The State   │◀────│  The Brain   │     │
│  │  (Notifier)  │     │  (Queue)     │     │  (Sentinel)  │     │
│  └──────────────┘     └──────────────┘     └──────┬───────┘     │
│                                                    │             │
│                                            ┌──────▼───────┐     │
│                                            │  The Hands   │     │
│                                            │  (Worker)    │     │
│                                            └──────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Sentinel Orchestrator (The Brain)

**Technology:** Python 3.12 (async), PowerShell Core, Docker CLI

**Role:** Persistent supervisor managing the lifecycle of Worker environments. Maps high-level intent (GitHub Issues) to low-level shell commands.

**Responsibilities:**

- **Polling Discovery** — Scans the GitHub organization for issues with `agent:queued` label every 60 seconds (configurable via `SENTINEL_POLL_INTERVAL`)
- **Auth Synchronization** — Runs `scripts/gh-auth.ps1` and `scripts/common-auth.ps1` before execution to maintain valid GitHub App installation tokens
- **Shell-Bridge Dispatch** — Manages the Worker via three primary commands with formalized return codes:
  - `./scripts/devcontainer-opencode.sh up` — Provision Docker network and base volumes (Exit 0 = Success)
  - `./scripts/devcontainer-opencode.sh start` — Launch opencode-server inside DevContainer
  - `./scripts/devcontainer-opencode.sh prompt "{instruction}"` — Core dispatch mechanism
  - Return codes: 0 = Success, 1–10 = Infrastructure Error, 11+ = Logic/Agent Error
- **Workflow Mapping** — Translates issue type (via labels/title patterns) into specific prompt strings selecting the correct agent-instruction module
- **Telemetry** — Captures Worker stdout/stderr, streams to local JSONL log files, posts heartbeat comments to GitHub Issues every 5 minutes for long-running tasks

**Key Design Decisions:**

- **ADR 07: Shell-Bridge Execution** — Orchestrator interacts with the agentic environment *exclusively* via shell scripts (no Docker SDK), ensuring environment parity with local developers
- **ADR 08: Polling-First Resiliency** — Polling as primary discovery; webhooks are an optimization. Ensures self-healing after crashes/restarts via state reconciliation

### 2. Work Event Notifier (The Ear)

**Technology:** Python 3.12, FastAPI, Uvicorn, Pydantic

**Role:** The system's sensory input — a high-performance webhook receiver for external stimuli.

**Responsibilities:**

- **Secure Webhook Ingestion** — Hardened endpoint (`POST /webhooks/github`) receiving issues, `issue_comment`, and `pull_request` events
- **Cryptographic Verification** — HMAC SHA256 validation of `X-Hub-Signature-256` against `WEBHOOK_SECRET`; rejects unauthorized payloads with 401
- **Event Triage & Manifest Generation** — Parses issue body/labels into unified `WorkItem` objects via Pydantic models; generates structured WorkItem Manifest (JSON)
- **Queue Initialization** — Applies `agent:queued` label to valid triggers via GitHub REST API
- **Automatic API Docs** — Swagger/OpenAPI documentation at `/docs` (built into FastAPI)

### 3. Opencode Worker (The Hands)

**Technology:** opencode-server CLI (v1.2.24), LLM Core (GLM-5)

**Role:** The execution layer where actual coding happens inside an isolated DevContainer.

**Capabilities:**

- **Contextual Awareness** — Accesses local project structure; maintains vector-indexed codebase view via `./scripts/update-remote-indices.ps1`
- **Instructional Logic** — Reads and executes markdown instruction modules from `local_ai_instruction_modules/` (Logic-as-Markdown principle)
- **Verification** — Runs local test suites before PR submission to ensure zero-regression code generation

**Constraints:**

- Network isolation (segregated Docker bridge network)
- Resource limits (2 CPUs, 4GB RAM)
- Ephemeral credentials (in-memory env vars only, destroyed on exit)

### 4. Work Queue (The State)

**Implementation:** GitHub Issues, Labels, and Milestones

**Philosophy: "Markdown as a Database"** — All distributed state lives in GitHub, providing:

- World-class audit trail
- Transparent versioning
- Out-of-the-box UI for human supervision
- Real-time intervention via commenting

**State Machine (Label Logic):**

```
                    ┌───────────────┐
                    │ agent:queued  │ ◀─── Notifier applies on valid trigger
                    └───────┬───────┘
                            │ Sentinel claims (assigns itself)
                            ▼
                    ┌───────────────┐
                    │agent:in-progress│  Issue assigned to Agent account (distributed lock)
                    └───────┬───────┘
                            │
                 ┌──────────┼──────────┐
                 ▼          ▼          ▼
          ┌──────────┐ ┌──────────┐ ┌──────────────────┐
          │agent:    │ │agent:    │ │agent:reconciling  │
          │success   │ │error     │ │(stale task recovery)│
          └──────────┘ └──────────┘ └──────────────────┘
```

**Special labels:**
- `agent:infra-failure` — Container/build failures (exit codes 1–10)
- `agent:impl-error` — Agent logic failures (exit codes 11+)
- `agent:stalled-budget` — Daily LLM cost threshold exceeded
- `agent:stalled` — Retry counter > 3

**Concurrency Control:** GitHub "Assignees" serve as a distributed lock semaphore — a Sentinel must successfully assign the issue before transitioning to `in-progress`.

---

## Data Flow (Happy Path)

```
 1. User opens Issue (e.g., [Application Plan] template)
         │
 2. GitHub Webhook ──▶ Notifier (FastAPI /webhooks/github)
         │
 3. Notifier verifies HMAC signature, confirms title pattern
    Applies `agent:queued` label via GitHub API
         │
 4. Sentinel poller detects `agent:queued` label (60s interval)
    Assigns issue to Agent account (distributed lock)
    Updates label to `agent:in-progress`
         │
 5. Sentinel runs `git clone` / `git pull` on target repo
         │
 6. Sentinel executes `devcontainer-opencode.sh up`
    (provisions Docker network and volumes)
         │
 7. Sentinel dispatches: `devcontainer-opencode.sh prompt "Execute workflow X..."`
         │
 8. Worker (opencode) reads issue, analyzes codebase,
    generates code, runs tests, creates PR
         │
 9. Worker posts "Execution Complete" comment
    Sentinel detects exit code 0
    Removes `in-progress`, adds `agent:success`
```

---

## Security Architecture

| Layer | Mechanism |
|-------|-----------|
| **Network Isolation** | Worker containers in dedicated Docker bridge network; no host subnet or metadata endpoint access |
| **Credential Scoping** | GitHub App Installation Token scoped to minimum necessary permissions |
| **Credential Lifecycle** | Tokens injected as temporary in-memory env vars; destroyed on container exit |
| **Log Sanitization** | Dual-stream logging: encrypted raw logs (forensic "Black Box") + regex-scrubbed public telemetry |
| **Resource Constraints** | Worker containers hard-capped at 2 CPUs / 4GB RAM to prevent rogue agent DoS |
| **Webhook Security** | HMAC SHA256 signature validation on all incoming requests; 401 rejection before JSON parsing |

---

## Provider-Agnostic Interface Layer

**ADR 09: Strategy Pattern for Queue Operations**

All queue interactions are abstracted behind a strictly defined `ITaskQueue` interface:

```python
class ITaskQueue(ABC):
    async def add_to_queue(self, item: WorkItem) -> bool: ...
    async def update_status(self, provider_id: str, status: WorkItemStatus, comment: str): ...
    async def fetch_queued_items(self) -> List[WorkItem]: ...
    async def claim_task(self, item: WorkItem) -> bool: ...
```

Phase 1 implements `GitHubIssueQueue`; the interface supports future providers (Linear, Notion, internal SQL queues) without rewriting orchestrator logic.

---

## Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml               # uv dependencies and metadata
├── uv.lock                      # Deterministic lockfile
├── src/
│   ├── notifier_service.py      # FastAPI webhook ingestion and event routing
│   ├── orchestrator_sentinel.py # Background polling, locking, and dispatch
│   ├── models/
│   │   ├── work_item.py         # WorkItem, Status, Type definitions (Pydantic)
│   │   └── github_events.py     # GitHub webhook payload schemas
│   └── interfaces/
│       └── i_task_queue.py      # Abstract base class for queue operations
├── tests/
│   ├── test_notifier.py
│   ├── test_sentinel.py
│   └── test_models.py
├── scripts/
│   ├── devcontainer-opencode.sh # Core shell bridge to worker Docker context
│   ├── gh-auth.ps1              # GitHub App auth synchronization
│   └── update-remote-indices.ps1# Vector index maintenance
├── local_ai_instruction_modules/ # Markdown logic workflows for LLM
│   ├── create-app-plan.md
│   ├── perform-task.md
│   └── analyze-bug.md
└── docs/                        # Architecture and user documentation
```

---

## Self-Bootstrapping Lifecycle

1. **Bootstrap** — Developer manually clones the template repository
2. **Seed** — Plan documents added; `create-repo-from-plan-docs` script executed
3. **Init** — `devcontainer-opencode.sh up` provisions the first worker environment
4. **Orchestrate** — `orchestrate-dynamic-workflow` configures env vars and indexes codebase
5. **Autonomous** — Sentinel service started; from this point, AI manages all further development
