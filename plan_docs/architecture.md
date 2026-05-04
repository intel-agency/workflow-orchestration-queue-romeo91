# Architecture Document — workflow-orchestration-queue (OS-APOW)

> **Document Version**: 1.0  
> **Last Updated**: 2026-04-27  
> **Source**: OS-APOW Architecture Guide v3, Implementation Specification v1, Development Plan v4

---

## 1. Executive Summary

**workflow-orchestration-queue** (OS-APOW — Opencode-Server Agent Workflow Orchestration) is a **headless agentic orchestration platform** that transforms the paradigm of AI-assisted software development from *interactive co-piloting* to *autonomous background production service*.

Instead of requiring a human developer to continuously prompt, guide, and troubleshoot an AI coding assistant, OS-APOW natively integrates into existing Agile workflows. It translates standard project management artifacts (GitHub Issues, Epics, Kanban board movements) into automated **Execution Orders** that are fulfilled by specialized AI agents operating in isolated, reproducible DevContainers.

**Key Outcome**: "Zero-Touch Construction" — a user opens a single Specification Issue and, within minutes, receives a functional, test-passed branch and Pull Request.

---

## 2. System Architecture Overview

The system is organized as an **event-driven, strictly decoupled** architecture distributed across four conceptual pillars:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OS-APOW System Architecture                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌───────────┐     ┌──────────────┐     ┌───────────────────┐     │
│   │  THE EAR  │────▶│  THE STATE   │────▶│   THE BRAIN       │     │
│   │ (Notifier)│     │ (Work Queue) │     │ (Sentinel Orch.)  │     │
│   └───────────┘     └──────────────┘     └───────┬───────────┘     │
│                                                   │                 │
│                                                   ▼                 │
│                                           ┌───────────────────┐     │
│                                           │   THE HANDS       │     │
│                                           │ (Opencode Worker) │     │
│                                           └───────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Four Pillars

### 3.1 The Ear — Work Event Notifier

| Attribute | Detail |
|-----------|--------|
| **Technology** | Python 3.12, FastAPI, Uvicorn, Pydantic |
| **Role** | System's primary gateway for external stimuli |
| **Phase** | Phase 2 (Phase 1 uses polling-first approach) |

**Responsibilities:**

1. **Secure Webhook Ingestion** — Exposes a hardened `/webhooks/github` endpoint to receive `issues`, `issue_comment`, and `pull_request` events from the GitHub App.
2. **Cryptographic Verification** — Every incoming request is validated using HMAC SHA256 against the `WEBHOOK_SECRET`. Prevents "Prompt Injection via Webhook" by ensuring only verified GitHub events trigger agent actions.
3. **Intelligent Event Triage** — Parses issue body and labels using Pydantic models to map diverse GitHub payloads into a unified `WorkItem` object. Generates a structured **WorkItem Manifest (JSON)** for machine-readable state sharing.
4. **Queue Initialization** — On valid trigger detection, applies the `agent:queued` label via GitHub REST API, signaling the Sentinel.

**Key Endpoint:**
- `POST /webhooks/github` — Primary webhook receiver with HMAC validation
- `GET /health` — Health check endpoint
- `GET /docs` — Auto-generated Swagger/OpenAPI documentation

---

### 3.2 The State — Work Queue

| Attribute | Detail |
|-----------|--------|
| **Technology** | GitHub Issues, Labels, Milestones, Assignees |
| **Philosophy** | "Markdown-as-a-Database" |
| **Role** | Distributed state management layer |

**State Machine (Label Logic):**

```
                    ┌──────────────┐
                    │ agent:queued │ ◄── Initial state after triage
                    └──────┬───────┘
                           │ Sentinel claims task
                           ▼
                ┌─────────────────────┐
                │ agent:in-progress   │ ◄── Sentinel assigned as owner
                └──────┬──────────────┘
                       │
              ┌────────┼──────────┐
              ▼        ▼          ▼
    ┌─────────────┐ ┌────────┐ ┌───────────────────┐
    │agent:success│ │agent:  │ │agent:infra-failure│
    │             │ │error   │ │                   │
    └─────────────┘ └────────┘ └───────────────────┘
              ▲
              │
    ┌─────────────────────┐
    │ agent:reconciling   │ ◄── Stale task recovery
    └─────────────────────┘
```

**Special Labels:**
- `agent:reconciling` — Stale task recovery state for "zombie" tasks
- `agent:impl-error` — Logic/agent-level failure during prompt execution
- `agent:infra-failure` — Infrastructure failure during `up` or `start`
- `agent:stalled-budget` — Daily LLM budget threshold exceeded
- `agent:revision` — PR changes requested, task re-queued with feedback

**Concurrency Control:** GitHub "Assignees" serve as a distributed lock semaphore. A Sentinel must successfully assign itself to an issue before transitioning to `agent:in-progress`.

---

### 3.3 The Brain — Sentinel Orchestrator

| Attribute | Detail |
|-----------|--------|
| **Technology** | Python (Async Background Service), PowerShell Core, Docker CLI |
| **Role** | Persistent supervisor managing worker lifecycle |
| **Runtime** | Background daemon (e.g., systemd) |

**Lifecycle Management Pipeline:**

```
1. Polling Discovery ──▶ Every 60s, scan for agent:queued issues
2. Auth Sync ──────────▶ Run scripts/gh-auth.ps1 for valid tokens
3. Claim Task ─────────▶ Assign issue to Sentinel, update labels
4. Shell-Bridge Protocol:
   a. devcontainer-opencode.sh up ────▶ Provision Docker environment
   b. devcontainer-opencode.sh start ──▶ Start opencode-server
   c. devcontainer-opencode.sh prompt ─▶ Dispatch workflow instruction
5. Monitor ────────────▶ Stream stdout/stderr, post heartbeat comments
6. Finalize ───────────▶ Detect exit code, apply terminal label
```

**Shell-Bridge Exit Codes:**

| Code Range | Meaning | Sentinel Action |
|-----------|---------|-----------------|
| 0 | Success | Apply `agent:success` |
| 1–10 | Infrastructure Error | Apply `agent:infra-failure` |
| 11+ | Logic/Agent Error | Apply `agent:error` |

**Resilience Features:**
- **Jittered exponential backoff** on GitHub API rate limits (403 responses)
- **Self-healing reconciliation loop** — detects stale `agent:in-progress` tasks (configurable `TASK_TIMEOUT_MINUTES`, default 120)
- **Cost guardrails** — monitors LLM usage, halts on budget threshold, labels `agent:stalled-budget`
- **Heartbeat comments** — every 5 minutes for tasks exceeding that duration

---

### 3.4 The Hands — Opencode Worker

| Attribute | Detail |
|-----------|--------|
| **Technology** | opencode CLI, LLM (GLM-5), Docker DevContainer |
| **Environment** | High-fidelity DevContainer from base template |
| **Role** | Isolated code execution against cloned codebase |

**Worker Capabilities:**

1. **Contextual Awareness** — Accesses local project structure, uses `update-remote-indices.ps1` for vector-indexed codebase view
2. **Instructional Logic** — Reads and executes `.md` workflow modules from `/local_ai_instruction_modules/` — "Logic-as-Markdown"
3. **Verification** — Runs local test suites before submitting PR to ensure zero-regression
4. **PR Creation** — Pushes committed changes to a new remote branch, generates formatted PR linking to original issue

---

## 4. Key Architectural Decisions (ADRs)

### ADR-01: Standardized Shell-Bridge Execution

- **Decision**: The Orchestrator interacts with the agentic environment *exclusively* via `./scripts/devcontainer-opencode.sh`
- **Rationale**: The existing shell infrastructure handles complex Docker logic (volume mounting, SSH-agent forwarding, port mapping). Reimplementing in Python would create maintenance burden and "Configuration Drift"
- **Consequence**: Python code stays lightweight (logic/state), shell scripts handle infra (containers). Clear separation of concerns

### ADR-02: Polling-First Resiliency Model

- **Decision**: Sentinel uses polling loop as primary discovery; webhooks are an optimization layer
- **Rationale**: Webhooks are "fire and forget" — if the server is down during a GitHub event, that event is lost. Polling ensures self-healing after restarts via state reconciliation
- **Consequence**: The system is inherently resilient against server downtime and network partitions

### ADR-03: Provider-Agnostic Interface Layer

- **Decision**: All queue interactions are abstracted behind a strictly defined `ITaskQueue` interface (Strategy Pattern)
- **Rationale**: Prevents vendor lock-in. Phase 1 is GitHub, but the interface supports Linear, Notion, or internal SQL queues without rewriting the Orchestrator
- **Interface Contract**: `fetch_queued()`, `claim_task(id, sentinel_id)`, `update_progress(id, log_line)`, `finish_task(id, artifacts)`

### ADR-04: Markdown-as-a-Database

- **Decision**: GitHub Issues, Labels, and Comments serve as the sole persistence layer
- **Rationale**: Provides world-class audit logs, transparent versioning, and an out-of-the-box UI for human supervision without maintaining a separate database
- **Consequence**: Humans can perform real-time "intervention-via-commenting" if the agent goes off-course

### ADR-05: Logic-as-Markdown

- **Decision**: AI behavioral logic is stored in Markdown instruction modules (`/local_ai_instruction_modules/`), not hardcoded in Python
- **Rationale**: Prompt Engineers can update AI behavior via standard Pull Requests without touching or redeploying core Python infrastructure
- **Consequence**: Flexible, version-controlled prompt management with low deployment friction

---

## 5. Data Flow — The "Happy Path"

```
1. Stimulus    │ User opens GitHub Issue with application-plan template
2. Notify      │ GitHub Webhook hits The Ear (FastAPI)
3. Triage      │ Notifier verifies HMAC signature, confirms title pattern,
               │ applies agent:queued label via GitHub API
4. Claim       │ Sentinel poller detects new label, assigns issue to itself,
               │ updates label to agent:in-progress
5. Sync        │ Sentinel runs git clone/pull into managed workspace volume
6. Env Check   │ Sentinel executes devcontainer-opencode.sh up
7. Dispatch    │ Sentinel sends: devcontainer-opencode.sh prompt
               │   "Execute workflow create-app-plan.md for context: <issue_url>"
8. Execute     │ Worker reads issue, analyzes tech stack, creates sub-tasks
9. Finalize    │ Worker posts completion comment. Sentinel detects exit code,
               │ removes in-progress label, adds agent:success
```

---

## 6. Security Architecture

### 6.1 Network Isolation

Worker containers run in a **segregated Docker bridge network**. They can reach the internet for package fetching but **cannot** access:
- Host machine's internal subnets
- Local metadata endpoints (e.g., AWS IMDS)
- Other peer containers

This prevents lateral movement from a compromised agent.

### 6.2 Credential Lifecycle

```
Sentinel generates temporary token
        │
        ▼
Injected as environment variable into DevContainer (in-memory only)
        │
        ▼
Used by worker for git operations and API calls
        │
        ▼
Destroyed the moment container exits — never written to disk
```

### 6.3 Log Security

| Layer | Content | Security |
|-------|---------|----------|
| **Black Box** (host files) | Full stdout/stderr with potentially sensitive data | Encrypted at rest, admin-only access |
| **Public Telemetry** (GitHub) | Sanitized progress updates | Regex scrubber strips tokens, IPs, secrets |
| **Service Logs** | Sentinel/Notifier structured logs | SENTINEL_ID tagged, no raw credentials |

---

## 7. Self-Bootstrapping Lifecycle

OS-APOW is designed to build itself through a staged evolution:

```
Stage 0: SEEDING
    └── Developer manually clones template repo, seeds plan docs

Stage 1: MANUAL LAUNCH
    └── Developer runs devcontainer-opencode.sh up

Stage 2: PROJECT SETUP
    └── Agent indexes repo, configures notifier/sentinel skeletons

Stage 3: HANDOVER
    └── Developer starts sentinel.py. From here, interaction is
        ONLY via GitHub Issues. The AI builds its own Phase 2 and 3.

Stage 4: AUTONOMOUS
    └── The system self-manages: builds features, fixes bugs,
        responds to PR reviews, and evolves its own architecture.
```

---

## 8. Component Integration Map

```
┌──────────────────────────────────────────────────────────────┐
│                     EXTERNAL SYSTEMS                         │
│  ┌──────────────┐              ┌──────────────────────────┐  │
│  │ GitHub API   │              │ GitHub App Webhooks      │  │
│  │ (REST v3)    │              │ (HMAC SHA256)            │  │
│  └──────┬───────┘              └───────────┬──────────────┘  │
│         │                                  │                  │
└─────────┼──────────────────────────────────┼──────────────────┘
          │                                  │
          │  ┌───────────────────────────────┘
          │  │
          ▼  ▼
┌─────────────────────────────────────────────────────────────┐
│                    OS-APOW RUNTIME                           │
│                                                              │
│  ┌────────────────┐    ┌────────────────────────────────┐   │
│  │ The Ear        │    │ The Brain (Sentinel)            │   │
│  │ FastAPI Server │    │ Async Python Service            │   │
│  │ :8000          │    │ Background Daemon               │   │
│  │                │    │                                  │   │
│  │ /webhooks/gh   │───▶│ Polling Engine (60s interval)   │   │
│  │ /health        │    │ Auth Sync (gh-auth.ps1)         │   │
│  │ /docs (Swagger)│    │ Task Claiming (GH Assignees)    │   │
│  └────────────────┘    │ Shell-Bridge Dispatcher         │   │
│                         │ Cost Guardrails                 │   │
│  ┌────────────────┐    │ Reconciliation Loop             │   │
│  │ The State      │    └──────────────┬─────────────────┘   │
│  │ GitHub Issues  │◀─────────────────│                      │
│  │ Labels/State   │                   │                      │
│  │ Assignees/Lock │                   │ subprocess           │
│  └────────────────┘                   ▼                      │
│                         ┌────────────────────────────────┐   │
│                         │ The Hands (Worker)             │   │
│                         │ Docker DevContainer            │   │
│                         │ opencode CLI + LLM             │   │
│                         │                                │   │
│                         │ Isolated network: bridge-net   │   │
│                         │ CPU: 2 | RAM: 4GB              │   │
│                         │ Ephemeral credentials          │   │
│                         └────────────────────────────────┘   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ INSTRUCTION MODULES (Logic-as-Markdown)                │  │
│  │ local_ai_instruction_modules/                          │  │
│  │   ├── create-app-plan.md                               │  │
│  │   ├── perform-task.md                                  │  │
│  │   └── analyze-bug.md                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ SHELL BRIDGE (scripts/)                                │  │
│  │   ├── devcontainer-opencode.sh (up/start/prompt)       │  │
│  │   ├── gh-auth.ps1 (GitHub App token sync)              │  │
│  │   └── update-remote-indices.ps1 (vector indexing)      │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Interface Contracts

### ITaskQueue (Abstract Base Class)

```python
class ITaskQueue(ABC):
    async def fetch_queued_items() -> List[WorkItem]
    async def claim_task(id: str, sentinel_id: str) -> bool
    async def update_progress(id: str, log_line: str) -> None
    async def finish_task(id: str, artifacts: dict) -> None
```

### WorkItem (Pydantic Model)

```python
class WorkItem(BaseModel):
    id: str                    # Unique identifier
    issue_number: int          # GitHub issue number
    source_url: str            # GitHub issue URL
    context_body: str          # Issue body (requirements)
    target_repo_slug: str      # Target repository (org/repo)
    task_type: TaskType        # PLAN | IMPLEMENT | BUGFIX
    status: WorkItemStatus     # Current queue state
    metadata: dict             # Provider-specific data
```

### TaskType (Enum)

```python
class TaskType(str, Enum):
    PLAN = "PLAN"          # Application planning
    IMPLEMENT = "IMPLEMENT"  # Feature implementation
    BUGFIX = "BUGFIX"      # Bug analysis and fix
```

---

## 10. Phased Evolution

| Phase | Name | Components | Key Deliverables |
|-------|------|-----------|-----------------|
| **0** | Seeding & Bootstrapping | Manual setup | Cloned repo, seeded plan docs, configured environment |
| **1** | The Sentinel (MVP) | `orchestrator_sentinel.py`, `ITaskQueue`, Shell Bridge | Polling engine, task claiming, status feedback, cost guardrails |
| **2** | The Ear (Webhook) | `notifier_service.py`, FastAPI, HMAC validation | Sub-second webhook ingestion, intelligent triage, tunneling |
| **3** | Deep Orchestration | Architect Sub-Agent, PR correction, vector indexing | Hierarchical decomposition, self-healing, codebase indexing |

---

*Generated from OS-APOW plan documents on 2026-04-27 as part of the `project-setup` workflow.*
