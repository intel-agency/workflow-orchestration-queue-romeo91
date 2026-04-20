# OS-APOW Architecture

> **Project:** workflow-orchestration-queue (OS-APOW — Opencode-Server Agent Workflow Orchestration Queue)
> **Last Updated:** 2026-04-20
> **Source:** Derived from OS-APOW Architecture Guide v3, Implementation Specification v1, Development Plan v4

---

## 1. Executive Summary

OS-APOW is a **headless agentic orchestration platform** that transforms the paradigm from "Interactive AI Coding" to "Autonomous Background Production Service." It translates standard project management artifacts (GitHub Issues, Epics, Kanban board movements) into automated Execution Orders, dispatching specialized AI agents running in isolated DevContainers to autonomously clone repositories, generate code, run tests, and submit Pull Requests.

The system is **self-bootstrapping**: the initial deployment is seeded from a template clone, and once the Sentinel service is active, the system uses its own orchestration capabilities to build subsequent phases.

---

## 2. Architectural Pillars

The system is decomposed into four conceptual pillars, each handling a distinct domain:

### 2.1 The Ear (Work Event Notifier)

| Aspect | Detail |
|---|---|
| **Technology** | Python 3.12, FastAPI, Uvicorn, Pydantic |
| **Role** | Primary gateway for external stimuli and asynchronous triggers |
| **Responsibilities** | Secure webhook ingestion, cryptographic HMAC SHA256 verification, intelligent event triage, WorkItem manifest generation, queue initialization |

**Key Design:**
- Exposes a hardened endpoint (`POST /webhooks/github`) that strictly requires `X-Hub-Signature-256` validation
- Parses diverse GitHub payloads into a unified `WorkItem` object using Pydantic models
- Applies `agent:queued` label to valid tasks via GitHub REST API
- Automatic OpenAPI/Swagger documentation at `/docs`

### 2.2 The State (Work Queue)

| Aspect | Detail |
|---|---|
| **Technology** | GitHub Issues, Labels, Milestones, Assignees |
| **Philosophy** | "Markdown as a Database" — all state lives in GitHub for world-class transparency |
| **Role** | Distributed state management and task persistence |

**State Machine (Label Logic):**

```
                  ┌─────────────────┐
                  │  agent:queued   │ ◄── Validated and awaiting Sentinel
                  └────────┬────────┘
                           │ Sentinel claims task
                           ▼
                  ┌─────────────────────┐
         ┌───────│  agent:in-progress  │───────┐
         │       └─────────────────────┘       │
         │ Timeout                              │ Success
         ▼                                      ▼
┌──────────────────┐               ┌──────────────────┐
│ agent:reconciling│               │  agent:success   │
└──────────────────┘               └──────────────────┘
         │                              
         ▼                              
┌──────────────────┐     ┌──────────────────────────┐
│  agent:error     │     │ agent:infra-failure      │
│ (logic/impl)     │     │ (container/build crash)  │
└──────────────────┘     └──────────────────────────┘
```

**Concurrency Control:** GitHub Assignees serve as a distributed lock semaphore. A Sentinel must successfully assign itself to an issue before transitioning to `agent:in-progress`.

### 2.3 The Brain (Sentinel Orchestrator)

| Aspect | Detail |
|---|---|
| **Technology** | Python (Async Background Service), HTTPX, PowerShell Core (pwsh), Docker CLI |
| **Role** | Persistent supervisor managing worker lifecycle and mapping intent to shell commands |
| **Runtime** | Persistent daemon (e.g., systemd), 60-second configurable polling interval |

**Lifecycle Management:**

1. **Polling Discovery** — Every 60s, scan for `agent:queued` issues via GitHub REST API with jittered exponential backoff
2. **Auth Synchronization** — Run `scripts/gh-auth.ps1` and `scripts/common-auth.ps1` for scoped installation tokens
3. **Shell-Bridge Protocol** — Three-phase dispatch:
   - `devcontainer-opencode.sh up` — Provision Docker network and volumes
   - `devcontainer-opencode.sh start` — Launch opencode-server inside DevContainer
   - `devcontainer-opencode.sh prompt "{workflow_instruction}"` — Execute the AI workflow
4. **Workflow Mapping** — Translate issue type → prompt string (e.g., `epic` label → `implement-epic` workflow)
5. **Telemetry** — Capture stdout to local JSONL logs; post sanitized "Heartbeat" comments to GitHub Issues

**Exit Code Protocol:**
- `Exit 0` = Success → label `agent:success`
- `Exit 1-10` = Infrastructure Error → label `agent:infra-failure`
- `Exit 11+` = Logic/Agent Error → label `agent:error`

### 2.4 The Hands (Opencode Worker)

| Aspect | Detail |
|---|---|
| **Technology** | opencode CLI, LLM Core (GLM-5 via ZhipuAI), MCP Servers |
| **Environment** | High-fidelity DevContainer (bit-for-bit identical to human developer environments) |
| **Role** | Isolated execution environment where actual code generation occurs |

**Worker Capabilities:**
- Contextual awareness via `./scripts/update-remote-indices.ps1` for vector-indexed codebase view
- Instructional logic from markdown modules in `local_ai_instruction_modules/`
- Pre-commit verification: run local test suites to ensure zero-regression code generation

---

## 3. Data Flow (The "Happy Path")

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. User opens GitHub Issue with [Application Plan] template                     │
│ 2. GitHub Webhook → hits The Ear (FastAPI)                                      │
│ 3. Ear verifies HMAC signature, confirms title pattern, adds agent:queued label │
│ 4. Sentinel poller detects agent:queued label                                   │
│ 5. Sentinel assigns issue to itself, updates to agent:in-progress               │
│ 6. Sentinel runs git clone/pull on target repo                                  │
│ 7. Sentinel executes: devcontainer-opencode.sh up                               │
│ 8. Sentinel dispatches: devcontainer-opencode.sh prompt "Run workflow: ..."     │
│ 9. Worker (Opencode) reads issue, analyzes codebase, generates code, runs tests │
│10. Worker creates Pull Request with changes                                     │
│11. Sentinel detects exit code 0, labels issue agent:success                     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Architectural Decisions (ADRs)

### ADR-01: Standardized Shell-Bridge Execution

- **Decision:** The Orchestrator interacts with worker environments exclusively via `./scripts/devcontainer-opencode.sh`
- **Rationale:** Existing shell infrastructure handles complex Docker logic (volume mounting, SSH-agent forwarding, port mapping). Re-implementing in Python Docker SDK would cause "Configuration Drift"
- **Consequence:** Python code stays lightweight (logic/state), while Shell scripts handle "Heavy Lifting" (container orchestration)

### ADR-02: Polling-First Resiliency Model

- **Decision:** Sentinel uses polling as primary discovery mechanism; webhooks are treated as optimization
- **Rationale:** Webhooks are "fire and forget" — if the server is down during an event, it's lost forever. Polling ensures self-healing via state reconciliation on restart
- **Consequence:** Slight latency increase (up to 60s), but guarantees zero dropped workloads

### ADR-03: Provider-Agnostic Interface Layer

- **Decision:** All queue interactions abstracted behind `ITaskQueue` interface (Strategy Pattern)
- **Methods:** `fetch_queued()`, `claim_task(id, sentinel_id)`, `update_progress(id, log_line)`, `finish_task(id, artifacts)`
- **Rationale:** Phase 1 is GitHub-specific, but the interface enables future support for Linear, Notion, or SQL queues without rewriting the Sentinel's core dispatch logic

### ADR-04: Markdown as a Database

- **Decision:** GitHub Issues, Labels, and Comments serve as the primary state store
- **Rationale:** Provides world-class audit trails, transparent versioning, out-of-the-box UI for human supervision, and enables real-time "intervention-via-commenting"

### ADR-05: Logic-as-Markdown

- **Decision:** AI behavior is defined by markdown instruction modules in `local_ai_instruction_modules/`, not hardcoded into Python
- **Rationale:** Prompt Engineers can update AI behavior via standard Pull Requests without touching or redeploying core Python infrastructure

---

## 5. Security Architecture

### 5.1 Network Isolation

- Worker DevContainers operate in a **segregated Docker bridge network**
- Explicitly blocked from: host machine internal subnets, local metadata endpoints (AWS IMDS), peer containers
- Prevents lateral movement and privilege escalation

### 5.2 Credential Management

- GitHub Installation Tokens are **dynamically generated** by the Sentinel
- Injected into DevContainers exclusively as **temporary in-memory environment variables**
- **Never written to disk** within the container
- **Instantly destroyed** on container exit (principle of least privilege)

### 5.3 Credential Scrubbing & Audit Trail

- All worker output piped through regex-based "Scrubber" utility
- Produces: (1) sanitized log for GitHub visibility, (2) raw encrypted log for local forensic audit ("Black Box")
- Patterns stripped: authentication tokens, private IPs, secrets, API keys

### 5.4 Resource Constraints

- Worker containers: **2 CPUs, 4GB RAM** hard caps via cgroup limits
- Prevents rogue agent Denial-of-Service on host infrastructure

### 5.5 Webhook Authentication

- HMAC SHA256 verification against `WEBHOOK_SECRET` for all incoming payloads
- Rejects requests with invalid/missing `X-Hub-Signature-256` with `401 Unauthorized`
- Prevents "Prompt Injection via Webhook" attacks

---

## 6. Self-Bootstrapping Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Bootstrap   │───▶│    Seed     │───▶│    Init     │───▶│   Orchestrate    │───▶│   Autonomous    │
│             │    │             │    │             │    │                  │    │                 │
│ Clone romeo │    │ Add plan    │    │ Run dc up   │    │ project-setup    │    │ Sentinel runs   │
│ template    │    │ docs to /   │    │ first time  │    │ workflow          │    │ continuously    │
└─────────────┘    └─────────────┘    └─────────────┘    └──────────────────┘    └─────────────────┘
     Manual              Manual             Manual            Agent-driven          Self-sustaining
```

---

## 7. Component Interaction Diagram

```
                    ┌─────────────────────────────────┐
                    │         GitHub Platform          │
                    │  ┌─────┐  ┌───────┐  ┌────────┐ │
                    │  │Issues│  │Labels │  │Webhooks│ │
                    │  └──┬──┘  └───┬───┘  └───┬────┘ │
                    └─────┼─────────┼──────────┼──────┘
                          │         │          │
            ┌─────────────┼─────────┼──────────┼──────────────┐
            │             │         │          │              │
            │    ┌────────▼─────────▼──┐  ┌───▼───────────┐  │
            │    │  The Brain          │  │  The Ear      │  │
            │    │  (Sentinel)         │  │  (Notifier)   │  │
            │    │                     │  │               │  │
            │    │ • Poll Issues API   │  │ • Receive     │  │
            │    │ • Claim via Assign  │  │   Webhooks    │  │
            │    │ • Dispatch Worker   │  │ • Verify HMAC │  │
            │    │ • Track Lifecycle   │  │ • Triage      │  │
            │    └────────┬────────────┘  └───────────────┘  │
            │             │                                  │
            │             │ Shell Bridge                     │
            │             │ (devcontainer-opencode.sh)       │
            │             ▼                                  │
            │    ┌────────────────────┐                      │
            │    │  The Hands         │                      │
            │    │  (Opencode Worker) │                      │
            │    │                    │                      │
            │    │ • Isolated Docker  │                      │
            │    │ • LLM Agent (GLM-5)│                      │
            │    │ • Code Generation  │                      │
            │    │ • Test Execution   │                      │
            │    │ • PR Creation      │                      │
            │    └────────────────────┘                      │
            │                                                  │
            │           Host Server / DevContainer            │
            └──────────────────────────────────────────────────┘
```

---

## 8. Deployment Topology

### Production Deployment

```
Host Server (Linux)
├── Sentinel Service (systemd daemon)
│   ├── Python 3.12 + uv
│   ├── HTTPX (GitHub API client)
│   └── Sentiel logs (sentinel.log, worker_run_*.jsonl)
├── Notifier Service (systemd daemon or Docker container)
│   ├── FastAPI + Uvicorn (port 8000)
│   └── Webhook endpoint: /webhooks/github
├── Docker Engine
│   ├── Worker DevContainer (ephemeral)
│   │   ├── opencode CLI + MCP Servers
│   │   ├── Cloned target repository
│   │   └── LLM API access (ZHIPU_API_KEY)
│   └── Isolated Docker Network (bridge)
└── Shared Volumes
    ├── Workspace (cloned repos)
    └── Logs (encrypted worker output)
```

### Development Mode

- Sentinel and Notifier run locally via `uv run`
- Worker DevContainer uses same configuration as production
- Local tunneling (ngrok/tailscale) for webhook testing
- `start_dev_notifier.sh` launches FastAPI + tunnel

---

## 9. Scalability Considerations

### Horizontal Scaling (Multiple Sentinels)

- Multiple Sentinel instances can run concurrently
- GitHub Assignees provide distributed locking (no two Sentinels claim the same task)
- Each Sentinel generates a unique `SENTINEL_ID` for attribution
- Sequential task processing in Phase 1 to prevent resource exhaustion

### Future Extensions (Post-Phase 3)

- Support for non-GitHub providers (Linear, Notion) via `ITaskQueue` interface swapping
- Real-time websocket log streaming
- Production deployment automation
- Multi-repository orchestration
