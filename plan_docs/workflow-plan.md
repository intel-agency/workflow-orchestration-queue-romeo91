# Workflow Execution Plan: Project Setup

## 1. Overview

| Field | Value |
|-------|-------|
| **Workflow Name** | project-setup |
| **Workflow File** | `ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md` |
| **Project Name** | workflow-orchestration-queue |
| **Repository** | intel-agency/workflow-orchestration-queue-romeo91 |
| **Total Assignments** | 6 (main) + 3 (post-assignment events) + 1 (pre-script event) |
| **Execution Mode** | Sequential with event hooks |

### High-Level Summary

This workflow initializes the **workflow-orchestration-queue** repository for autonomous AI orchestration development. It transforms a template repository into a fully configured development environment ready for building a headless agentic orchestration system that converts GitHub Issues into Execution Orders fulfilled by specialized AI agents.

The workflow establishes:
- Repository configuration (branch protection, labels, project board)
- Application planning from seeded plan documents
- Project structure and scaffolding
- Agent-friendly documentation (AGENTS.md)
- Debrief and continuous improvement
- PR approval and merge to main

---

## 2. Project Context Summary

### Project Overview

**workflow-orchestration-queue** is a groundbreaking headless agentic orchestration platform that transforms interactive AI coding into autonomous background production services. The system converts GitHub Issues into "Execution Orders" fulfilled by specialized AI agents without human intervention.

### Key Architectural Components

| Component | Role | Technology |
|-----------|------|------------|
| **Work Event Notifier (The "Ear")** | Webhook ingestion and event triage | Python 3.12+, FastAPI, Pydantic, HTTPX |
| **Work Queue (The State)** | Distributed state management | GitHub Issues, Labels, Milestones |
| **Sentinel Orchestrator (The "Brain")** | Persistent polling and task dispatch | Python (async), PowerShell, Docker CLI |
| **Opencode Worker (The "Hands")** | Code execution and implementation | opencode-server CLI, LLM (GLM-5/Claude) |

### Technology Stack

| Category | Technology |
|----------|------------|
| **Language** | Python 3.12+ |
| **Web Framework** | FastAPI |
| **ASGI Server** | Uvicorn |
| **Validation** | Pydantic |
| **HTTP Client** | HTTPX (async) |
| **Package Manager** | uv (Rust-based) |
| **Containerization** | Docker, DevContainers |
| **CI/CD** | GitHub Actions |
| **Shell Scripts** | Bash, PowerShell Core (pwsh) |

### Key Constraints

- **Script-First Integration**: All container interactions via `./scripts/devcontainer-opencode.sh`
- **Markdown-as-Database**: GitHub Issues serve as the persistent state layer
- **Polling-First Resiliency**: Webhooks are optional; polling ensures self-healing
- **Self-Bootstrapping**: System builds itself using its own orchestration
- **Action SHA Pinning**: All GitHub Actions must be pinned to commit SHAs

### Repository Details

- **Template Source**: `intel-agency/workflow-orchestration-queue-romeo91`
- **Primary Branch**: `main`
- **Development Branch**: `develop`
- **Working Branch Pattern**: `dynamic-workflow-<workflow-name>`

### Seeded Plan Documents

| Document | Purpose |
|----------|---------|
| `OS-APOW Architecture Guide v3.md` | System-level diagrams, security boundaries, ADRs |
| `OS-APOW Development Plan v4.md` | Phased roadmap, user stories, risk assessment |
| `OS-APOW Implementation Specification v1.md` | Features, test cases, deliverables |
| `orchestrator_sentinel.py` | Reference implementation for Phase 1 Sentinel |
| `notifier_service.py` | Reference implementation for Phase 2 Notifier |

---

## 3. Assignment Execution Plan

### Assignment 1: init-existing-repository

| Field | Content |
|-------|---------|
| **Short ID** | `init-existing-repository` |
| **Goal** | Initialize the existing repository with configuration, labels, project board, and branch protection |
| **Key Acceptance Criteria** | - New branch created (`dynamic-workflow-project-setup`)<br>- Branch protection ruleset imported<br>- GitHub Project created and linked<br>- Labels imported from `.github/.labels.json`<br>- Workspace/devcontainer files renamed<br>- PR created (after first commit) |
| **Project-Specific Notes** | This is a template clone. The `.github/protected-branches_ruleset.json` should exist. Use `GH_ORCHESTRATION_AGENT_TOKEN` for ruleset import (requires `administration: write` scope). |
| **Prerequisites** | - GitHub CLI authenticated<br>- `repo`, `project`, `read:project`, `read:user`, `user:email` scopes<br>- `administration: write` scope for ruleset |
| **Dependencies** | None (first assignment) |
| **Risks / Challenges** | - Missing `administration: write` scope will block ruleset import<br>- Template may not have all expected files<br>- Project creation may fail if org quotas exceeded |
| **Events** | None |

### Assignment 2: create-app-plan

| Field | Content |
|-------|---------|
| **Short ID** | `create-app-plan` |
| **Goal** | Create a comprehensive application plan from seeded plan documents |
| **Key Acceptance Criteria** | - Application template analyzed<br>- Plan documented in GitHub Issue using template<br>- Milestones created and linked<br>- Issue added to GitHub Project<br>- Labels applied (`planning`, `documentation`) |
| **Project-Specific Notes** | Plan documents are in `plan_docs/` directory. Reference implementations exist for Sentinel (`orchestrator_sentinel.py`) and Notifier (`notifier_service.py`). Create `plan_docs/tech-stack.md` and `plan_docs/architecture.md`. |
| **Prerequisites** | Repository initialized, labels imported |
| **Dependencies** | Output from `init-existing-repository` (labels, project) |
| **Risks / Challenges** | - Plan documents are comprehensive; synthesis required<br>- Technology decisions already made in spec<br>- Must NOT implement code, only plan |
| **Events** | `pre-assignment-begin`: `gather-context`<br>`on-assignment-failure`: `recover-from-error`<br>`post-assignment-complete`: `report-progress` |

### Assignment 3: create-project-structure

| Field | Content |
|-------|---------|
| **Short ID** | `create-project-structure` |
| **Goal** | Create actual project structure and scaffolding based on the application plan |
| **Key Acceptance Criteria** | - Solution/project structure created<br>- Infrastructure foundation (Docker, docker-compose)<br>- Development environment configured<br>- Documentation structure created<br>- CI/CD foundation established<br>- Repository summary created (`.ai-repository-summary.md`)<br>- All GitHub Actions pinned to SHAs |
| **Project-Specific Notes** | Python project using `uv`. Structure: `src/` for main code, `tests/` for tests, `pyproject.toml` for dependencies. Reference `notifier_service.py` and `orchestrator_sentinel.py` for structure hints. |
| **Prerequisites** | Application plan completed |
| **Dependencies** | Output from `create-app-plan` (plan issue, milestones, tech-stack.md, architecture.md) |
| **Risks / Challenges** | - Dockerfile must COPY `src/` before `uv pip install -e .`<br>- Healthchecks must use Python stdlib (no curl)<br>- All workflow actions must use SHA pinning |
| **Events** | None |

### Assignment 4: create-agents-md-file

| Field | Content |
|-------|---------|
| **Short ID** | `create-agents-md-file` |
| **Goal** | Create AGENTS.md file for AI coding agent context |
| **Key Acceptance Criteria** | - AGENTS.md exists at repository root<br>- Contains project overview, setup commands, structure<br>- Commands validated by running them<br>- Complements README.md and .ai-repository-summary.md |
| **Project-Specific Notes** | Project uses Python 3.12+, FastAPI, uv. Key commands: `uv sync`, `uv run pytest`, `uv run uvicorn`. Must document shell bridge (`./scripts/devcontainer-opencode.sh`). |
| **Prerequisites** | Project structure created, build/test tooling in place |
| **Dependencies** | Output from `create-project-structure` (structure, tooling, .ai-repository-summary.md) |
| **Risks / Challenges** | - Commands must be validated before documenting<br>- Must not duplicate README.md content<br>- Must be compatible with multiple AI agents |
| **Events** | None |

### Assignment 5: debrief-and-document

| Field | Content |
|-------|---------|
| **Short ID** | `debrief-and-document` |
| **Goal** | Capture learnings, insights, and improvements from the setup process |
| **Key Acceptance Criteria** | - Detailed report created using template<br>- All deviations documented<br>- Execution trace saved (`debrief-and-document/trace.md`)<br>- Report reviewed and approved<br>- Committed to repository |
| **Project-Specific Notes** | Flag any plan-impacting findings as ACTION ITEMS. Review upcoming phases for validity. This is a self-bootstrapping system, so learnings inform Phase 2 and Phase 3 development. |
| **Prerequisites** | All prior assignments completed |
| **Dependencies** | All outputs from assignments 1-4 |
| **Risks / Challenges** | - Must capture all deviations accurately<br>- Must recommend concrete follow-up actions<br>- Execution trace must be comprehensive |
| **Events** | None |

### Assignment 6: pr-approval-and-merge

| Field | Content |
|-------|---------|
| **Short ID** | `pr-approval-and-merge` |
| **Goal** | Complete PR approval, merge, and cleanup |
| **Key Acceptance Criteria** | - CI verification and remediation loop executed<br>- Code review delegated to code-reviewer<br>- All review comments resolved<br>- Stakeholder approval obtained<br>- PR merged<br>- Source branch deleted<br>- Related issues closed |
| **Project-Specific Notes** | This is an automated setup PR - self-approval by orchestrator is acceptable. CI remediation loop (Phase 0.5) must be executed: up to 3 fix attempts before escalation. |
| **Prerequisites** | All prior assignments completed, PR exists |
| **Dependencies** | `$pr_num` from `init-existing-repository`, all committed changes |
| **Risks / Challenges** | - CI may fail on fresh repository<br>- Branch protection may require reviews<br>- Must follow `ai-pr-comment-protocol.md` exactly |
| **Events** | None |

---

## 4. Post-Assignment Events

After each main assignment completes, the following events fire:

| Event | Assignment | Purpose |
|-------|------------|---------|
| `post-assignment-complete` | `validate-assignment-completion` | Verify assignment completed correctly |
| `post-assignment-complete` | `report-progress` | Update stakeholders on progress |

---

## 5. Post-Script Complete Event

After all assignments complete successfully:

| Event | Action | Purpose |
|-------|--------|---------|
| `post-script-complete` | Apply `orchestration:plan-approved` label | Signal plan is ready for epic creation |

---

## 6. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROJECT-SETUP WORKFLOW SEQUENCE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PRE-SCRIPT EVENT ──────────────────────────────────────────────────────────┐
│  create-workflow-plan (THIS ASSIGNMENT)                                     │
│  └─► Output: plan_docs/workflow-plan.md                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ ASSIGNMENT 1 ──────────────────────────────────────────────────────────────┐
│  init-existing-repository                                                   │
│  ├─► Create branch: dynamic-workflow-project-setup                          │
│  ├─► Import branch protection ruleset                                       │
│  ├─► Create GitHub Project                                                  │
│  ├─► Import labels                                                          │
│  ├─► Rename workspace/devcontainer files                                    │
│  └─► Create PR (output: $pr_num)                                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ POST-ASSIGNMENT EVENTS ────────────────────────────────────────────────────┐
│  validate-assignment-completion → report-progress                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ ASSIGNMENT 2 ──────────────────────────────────────────────────────────────┐
│  create-app-plan                                                            │
│  ├─► [pre] gather-context                                                   │
│  ├─► Analyze plan_docs/ documents                                           │
│  ├─► Create tech-stack.md, architecture.md                                  │
│  ├─► Create plan issue from template                                        │
│  ├─► Create milestones, link to project                                     │
│  └─► [post] report-progress                                                 │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ POST-ASSIGNMENT EVENTS ────────────────────────────────────────────────────┐
│  validate-assignment-completion → report-progress                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ ASSIGNMENT 3 ──────────────────────────────────────────────────────────────┐
│  create-project-structure                                                   │
│  ├─► Create src/, tests/ directories                                        │
│  ├─► Create pyproject.toml, Dockerfile, docker-compose.yml                  │
│  ├─► Create .github/workflows/ (with SHA pinning)                           │
│  ├─► Create docs/ structure                                                 │
│  └─► Create .ai-repository-summary.md                                       │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ POST-ASSIGNMENT EVENTS ────────────────────────────────────────────────────┐
│  validate-assignment-completion → report-progress                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ ASSIGNMENT 4 ──────────────────────────────────────────────────────────────┐
│  create-agents-md-file                                                      │
│  ├─► Gather project context                                                 │
│  ├─► Validate build/test commands                                           │
│  ├─► Draft AGENTS.md                                                        │
│  └─► Cross-reference with existing docs                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ POST-ASSIGNMENT EVENTS ────────────────────────────────────────────────────┐
│  validate-assignment-completion → report-progress                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ ASSIGNMENT 5 ──────────────────────────────────────────────────────────────┐
│  debrief-and-document                                                       │
│  ├─► Create debrief report from template                                    │
│  ├─► Document all deviations                                                │
│  ├─► Save execution trace                                                   │
│  └─► Initiate continuous-improvement cycle                                  │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ POST-ASSIGNMENT EVENTS ────────────────────────────────────────────────────┐
│  validate-assignment-completion → report-progress                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ ASSIGNMENT 6 ──────────────────────────────────────────────────────────────┐
│  pr-approval-and-merge                                                      │
│  ├─► [Phase 0.5] CI verification & remediation loop                         │
│  ├─► [Phase 0.75] Code review delegation                                    │
│  ├─► [Phase 1] Resolve review comments                                      │
│  ├─► [Phase 2] Secure approval                                              │
│  ├─► [Phase 3] Merge PR                                                     │
│  ├─► Delete source branch                                                   │
│  └─► Close related issues                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─ POST-SCRIPT COMPLETE ──────────────────────────────────────────────────────┐
│  Apply orchestration:plan-approved label to plan issue                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Dependency Graph

```
init-existing-repository
         │
         ├──► [labels, project, PR created]
         │
         ▼
create-app-plan
         │
         ├──► [plan issue, milestones, tech-stack.md, architecture.md]
         │
         ▼
create-project-structure
         │
         ├──► [src/, tests/, pyproject.toml, Dockerfile, workflows, .ai-repository-summary.md]
         │
         ▼
create-agents-md-file
         │
         ├──► [AGENTS.md with validated commands]
         │
         ▼
debrief-and-document
         │
         ├──► [debrief report, execution trace]
         │
         ▼
pr-approval-and-merge
         │
         └──► [Merged PR, closed issues, orchestration:plan-approved label]
```

---

## 8. Open Questions

| # | Question | Context | Resolution Needed Before |
|---|----------|---------|--------------------------|
| 1 | **GH_ORCHESTRATION_AGENT_TOKEN availability** | Branch protection ruleset import requires `administration: write` scope. Is this token configured with the correct scopes? | `init-existing-repository` |
| 2 | **GitHub Project quota** | Creating a new project may fail if organization has reached project limits. | `init-existing-repository` |
| 3 | **Prebuilt devcontainer image** | Fresh clone may not have prebuilt GHCR image until `publish-docker` and `prebuild-devcontainer` workflows complete. Should CI fallback be expected? | `pr-approval-and-merge` (CI verification) |
| 4 | **LLM API keys** | The system requires `ZHIPU_API_KEY` and optionally `KIMI_CODE_ORCHESTRATOR_AGENT_API_KEY`. Are these configured as repository secrets? | Phase 1 implementation (post-setup) |
| 5 | **GitHub App configuration** | Phase 2 (The Ear) requires a GitHub App with webhook secret and private key. Is this already configured? | Phase 2 implementation (post-setup) |

---

## 9. Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Missing `administration: write` scope | High | Medium | Verify token scopes before starting; have fallback plan to skip ruleset import |
| CI fails on fresh repository | Medium | High | CI remediation loop handles up to 3 fix attempts; fallback build from Dockerfile expected |
| Prebuilt devcontainer image missing | Medium | High | Template designed to tolerate missing GHCR image; falls back to local build |
| Webhook secret not configured | Low | Medium | Phase 2 dependency; not blocking for project-setup |
| Project quota exceeded | Medium | Low | Check org project count before creating; can use existing project if needed |

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| All 6 assignments completed | 100% |
| PR merged to main | ✅ |
| Plan issue labeled `orchestration:plan-approved` | ✅ |
| CI checks passing | 100% |
| Setup branch deleted | ✅ |
| Related issues closed | ✅ |

---

## Approval

**Plan Status**: ⏳ Pending Approval

**Prepared By**: Planner Agent  
**Date**: 2026-03-30  
**Workflow**: project-setup  
**Repository**: intel-agency/workflow-orchestration-queue-romeo91

---

*This workflow execution plan was created as part of the `create-workflow-plan` assignment for the `project-setup` dynamic workflow.*
