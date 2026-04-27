# Workflow Execution Plan: `project-setup`

**Workflow**: `project-setup` Dynamic Workflow  
**Project**: `workflow-orchestration-queue` (OS-APOW — Opencode-Server Agent Workflow Orchestration)  
**Repository**: `intel-agency/workflow-orchestration-queue-romeo91`  
**Branch**: `main`  
**Date Created**: 2026-04-27  
**Plan Author**: Planner Agent  

---

## 1. Overview

### Workflow Summary

The `project-setup` workflow transforms a freshly seeded template repository into a fully initialized, planned, and structured project ready for development. It executes 6 sequential assignments, each validated independently, with progress tracking after every step.

| Attribute | Value |
|-----------|-------|
| **Total Main Assignments** | 6 |
| **Validation Checkpoints** | 6 (after each assignment) |
| **Progress Reports** | 6 (after each assignment) |
| **Working Branch** | `dynamic-workflow-project-setup` |
| **Target Merge Base** | `main` |
| **Pre-script Event** | `create-workflow-plan` (this document) |
| **Post-script Event** | Apply `orchestration:plan-approved` label to plan issue |

### Assignment Sequence

```
[pre-script] create-workflow-plan (this plan)
     │
     ▼
 1. init-existing-repository
     │── post: validate-assignment-completion + report-progress
     ▼
 2. create-app-plan
     │── post: validate-assignment-completion + report-progress
     ▼
 3. create-project-structure
     │── post: validate-assignment-completion + report-progress
     ▼
 4. create-agents-md-file
     │── post: validate-assignment-completion + report-progress
     ▼
 5. debrief-and-document
     │── post: validate-assignment-completion + report-progress
     ▼
 6. pr-approval-and-merge
     │
     ▼
[post-script] Apply orchestration:plan-approved label
```

### Existing State — Important Note

> **There is an existing PR #2** titled *"project-setup: Initialize repository"* on branch `dynamic-workflow-project-setup` from a **previous setup attempt**.  
> - The executing agent must assess whether to reuse or close this PR and start fresh.
> - If the branch is stale or contains incomplete/conflicting work, close PR #2, delete the branch, and create a new `dynamic-workflow-project-setup` branch.
> - If the branch contains valid completed work, assess which assignment steps are already satisfied and resume from the next incomplete step.

---

## 2. Project Context Summary

### Application Overview

**workflow-orchestration-queue** (OS-APOW) is a **headless agentic orchestration platform** that transforms GitHub Issues into autonomous execution orders. It shifts AI from a passive co-pilot role to a background production service capable of multi-step, specification-driven task fulfillment without human intervention.

### Architecture (4 Pillars)

| Pillar | Component | Tech Stack | Role |
|--------|-----------|------------|------|
| **The Ear** | Work Event Notifier | Python 3.12, FastAPI, Pydantic, uv | Secure webhook ingestion, HMAC validation, event triage |
| **The State** | Work Queue | GitHub Issues, Labels, Milestones | "Markdown-as-a-Database" — distributed state via GH labels |
| **The Brain** | Sentinel Orchestrator | Python Async, HTTPX, Docker CLI | Persistent polling, task claiming, worker lifecycle management |
| **The Hands** | Opencode Worker | Docker DevContainer, opencode CLI, LLM | Isolated code execution against cloned codebase |

### Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Language** | Python | 3.12+ |
| **Web Framework** | FastAPI + Uvicorn | Latest stable |
| **Data Validation** | Pydantic | v2 |
| **HTTP Client** | HTTPX | Latest (async) |
| **Package Manager** | uv | Latest |
| **Scripting** | PowerShell Core (pwsh) / Bash | Cross-platform |
| **Containers** | Docker + DevContainers | Latest |
| **AI Runtime** | opencode CLI | 1.2.24 |
| **LLM** | GLM-5 (ZhipuAI) | Latest |

### Planned Project Structure

```
workflow-orchestration-queue/
├── pyproject.toml                    # Core definition for uv dependencies
├── uv.lock                           # Deterministic lockfile
├── src/
│   ├── notifier_service.py           # FastAPI webhook ingestion & routing
│   ├── orchestrator_sentinel.py      # Background polling, locking, dispatch
│   ├── models/
│   │   ├── work_item.py              # WorkItem, Status, Type definitions
│   │   └── github_events.py          # GitHub webhook payload schemas
│   └── interfaces/
│       └── i_task_queue.py           # Abstract queue operations
├── scripts/                          # Shell Bridge execution layer
│   ├── devcontainer-opencode.sh      # Core orchestrator→worker bridge
│   ├── gh-auth.ps1                   # GitHub App auth sync
│   └── update-remote-indices.ps1     # Vector index maintenance
├── local_ai_instruction_modules/     # Decoupled Markdown LLM logic
├── docs/                             # Architecture & user documentation
├── tests/                            # Test suite
└── Dockerfile                        # Container build
```

### Development Phases

| Phase | Name | Focus | Status |
|-------|------|-------|--------|
| 0 | Seeding & Bootstrapping | Template clone, plan seeding, project setup | **Active (this workflow)** |
| 1 | The Sentinel (MVP) | Polling engine, shell-bridge dispatch, status feedback | Upcoming |
| 2 | The Ear (Webhook) | FastAPI receiver, HMAC validation, triage | Upcoming |
| 3 | Deep Orchestration | Hierarchical decomposition, self-healing, indexing | Upcoming |

### Key Plan Documents (in `plan_docs/`)

| File | Purpose |
|------|---------|
| `OS-APOW Architecture Guide v3.md` | System-level diagrams, ADRs, security boundaries, self-bootstrapping lifecycle |
| `OS-APOW Development Plan v4.md` | Phase-by-phase roadmap, user stories, acceptance criteria, risk assessment |
| `OS-APOW Implementation Specification v1.md` | Full requirements, test cases, tech stack, deliverables, project structure |
| `interactive-report.html` | React-based interactive visualization of architecture and plan |
| `notifier_service.py` | Skeleton implementation of the FastAPI webhook receiver |
| `orchestrator_sentinel.py` | Skeleton implementation of the Sentinel polling service |

---

## 3. Assignment Execution Plan

---

### Assignment 1: `init-existing-repository`

#### Goal
Initialize the repository by creating the working branch, importing branch protection, creating a GitHub Project, importing labels, renaming workspace/devcontainer files, and opening a PR.

#### Key Acceptance Criteria
1. **Branch created**: `dynamic-workflow-project-setup` — must be done first
2. **Branch protection ruleset** imported from `.github/protected-branches_ruleset.json`
3. **GitHub Project** created and linked (Board: Not Started → In Progress → In Review → Done)
4. **Labels imported** from `.github/.labels.json` via `scripts/import-labels.ps1`
5. **Devcontainer name** renamed to `workflow-orchestration-queue-devcontainer`
6. **Workspace file** renamed to `workflow-orchestration-queue.code-workspace`
7. **PR created** from working branch to `main`

#### Prerequisites
- GitHub authentication with scopes: `repo`, `project`, `read:project`, `read:user`, `user:email`
- `administration: write` scope for branch protection rulesets
- `GH_ORCHESTRATION_AGENT_TOKEN` available for ruleset import

#### Dependencies
- None (first assignment)

#### Project-Specific Notes
- **Branch protection ruleset file is missing**: `.github/protected-branches_ruleset.json` does not exist in the repository. The agent must either create it or skip this step with a documented deviation.
- **Existing PR #2**: Check if branch `dynamic-workflow-project-setup` already exists with prior work. Close and recreate if stale.
- **Workspace file**: Currently `workflow-orchestration-queue-romeo91.code-workspace` — should become `workflow-orchestration-queue.code-workspace` (dropping the random suffix `-romeo91`).
- **Devcontainer name**: Currently `workflow-orchestration-queue-romeo91` — should become `workflow-orchestration-queue-devcontainer`.
- **Label import**: The `.github/.labels.json` file exists with 15 labels. Run `scripts/import-labels.ps1`.
- **Python project**: Unlike .NET projects, there is no solution file to create here.

#### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Missing `protected-branches_ruleset.json` | **High** | Medium | Create the ruleset file or document as deviation |
| Existing PR/branch conflict | **Medium** | Medium | Assess existing PR #2; close and recreate if needed |
| `GH_ORCHESTRATION_AGENT_TOKEN` unavailable | **Medium** | High | Fallback: skip ruleset import, document as action item |
| GitHub Project creation scope missing | **Low** | Medium | Verify scopes with `scripts/test-github-permissions.ps1` |

#### Events
- **post-assignment-complete**: `validate-assignment-completion` → `report-progress`

---

### Assignment 2: `create-app-plan`

#### Goal
Analyze plan docs, create a comprehensive application plan documented as a GitHub Issue, and create milestones for phased development. **Planning only — no code.**

#### Key Acceptance Criteria
1. Application template analyzed and all requirements identified
2. `plan_docs/tech-stack.md` created with languages, frameworks, tools, packages
3. `plan_docs/architecture.md` created with high-level architecture and design decisions
4. Plan issue created using the issue template (`.github/ISSUE_TEMPLATE/application-plan.md`)
5. Milestones created for each phase (Phase 0, 1, 2, 3)
6. Issue linked to GitHub Project and assigned to "Phase 1: Foundation" milestone
7. Labels applied: `planning`, `documentation`

#### Prerequisites
- Assignment 1 complete (repository initialized, labels imported, project created)
- `plan_docs/` directory with all 6 documents available

#### Dependencies
- **Depends on**: `init-existing-repository` (labels, project, branch must exist)

#### Project-Specific Notes
- **Plan docs are comprehensive**: 3 markdown documents + 2 Python skeletons + 1 HTML visualization already exist
- **Python project**: tech-stack.md should document Python 3.12, FastAPI, Pydantic, HTTPX, uv — NOT .NET
- **No `ai-new-app-template.md` exists**: The assignment references this file but it is not present. The Implementation Specification (`OS-APOW Implementation Specification v1.md`) serves as the equivalent — the agent should use it as the primary requirements document.
- **Architecture doc already exists**: `OS-APOW Architecture Guide v3.md` should be used as the source for `plan_docs/architecture.md`
- **Phases are well-defined**: Phase 0 (Seeding), Phase 1 (Sentinel MVP), Phase 2 (Ear/Webhook), Phase 3 (Deep Orchestration)
- **Issue template**: Check if `.github/ISSUE_TEMPLATE/application-plan.md` exists; if not, use Appendix A from the assignment definition
- **Reference examples**: <https://github.com/nam20485/advanced-memory3/issues/12> and <https://github.com/nam20485/support-assistant/issues/2>

#### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Missing `ai-new-app-template.md` | **High** | Medium | Use Implementation Specification as equivalent |
| Missing issue template | **Medium** | Low | Use Appendix A from assignment definition |
| Scope creep (implementing instead of planning) | **Medium** | High | Reinforce "PLANNING ONLY" — no code creation |

#### Events
- **pre-assignment-begin**: `gather-context` assignment
- **post-assignment-complete**: `validate-assignment-completion` → `report-progress`
- **on-assignment-failure**: `recover-from-error` assignment

---

### Assignment 3: `create-project-structure`

#### Goal
Create the actual project scaffolding — solution structure, configuration files, Docker setup, CI/CD foundation, documentation structure, and repository summary.

#### Key Acceptance Criteria
1. Solution/project structure created following Python/uv conventions
2. All required project files and directories established (`pyproject.toml`, `src/`, `tests/`, etc.)
3. Initial configuration files created (Dockerfile, docker-compose.yml, .env templates)
4. Basic CI/CD pipeline structure established
5. Documentation structure created (README.md, docs/)
6. Development environment validated
7. All GitHub Actions workflow actions pinned to commit SHAs
8. Repository summary document (`.ai-repository-summary.md`) created
9. Solution builds/validates successfully

#### Prerequisites
- Assignment 2 complete (plan issue approved, tech-stack and architecture docs exist)
- Clear understanding of Python/uv project conventions

#### Dependencies
- **Depends on**: `create-app-plan` (structure must follow the documented plan)

#### Project-Specific Notes
- **Python project using uv**: Use `pyproject.toml` + `uv` — NOT .NET solution files
- **No `global.json` needed**: The existing `global.json` in the repo root is from the template and should be removed or `.gitignore`d
- **src/ layout**: Follow the Implementation Specification's project structure exactly
- **Existing skeletons**: Move/reference `notifier_service.py` and `orchestrator_sentinel.py` from plan_docs into `src/`
- **Docker healthchecks**: Do NOT use `curl` — use Python stdlib `urllib.request`
- **Editable installs**: If using `uv pip install -e .`, ensure source is COPYed before install
- **CI/CD**: All actions must be pinned to SHA — no version tags
- **Docker Compose**: Create for local development (Notifier + potential DB)
- **Tests**: Create initial `tests/` with basic smoke tests
- **Existing scripts**: The `scripts/` directory already has shell bridge scripts — integrate, don't replace

#### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Confusion with .NET template structure | **Medium** | High | Explicitly document: Python project, ignore .NET artifacts |
| Docker healthcheck using curl | **Low** | Medium | Use Python stdlib for healthchecks |
| Actions not pinned to SHA | **Medium** | High | Verify all `uses:` in workflow files |
| Source missing before editable install | **Low** | High | Ensure COPY src/ before pip install in Dockerfile |

#### Events
- **post-assignment-complete**: `validate-assignment-completion` → `report-progress`

---

### Assignment 4: `create-agents-md-file`

#### Goal
Create a comprehensive `AGENTS.md` at the repository root providing AI coding agents with context, build commands, conventions, and project structure information.

#### Key Acceptance Criteria
1. `AGENTS.md` exists at repository root
2. Contains: project overview, setup/build/test commands, project structure, code style, testing instructions, PR/commit guidelines
3. All listed commands validated by running them
4. Written in standard Markdown with agent-focused language
5. Committed and pushed to working branch
6. Stakeholder approval obtained

#### Prerequisites
- Assignments 1-3 complete (project structure exists, build/test tooling in place)
- Working build and test commands available

#### Dependencies
- **Depends on**: `create-project-structure` (commands must exist to validate them)

#### Project-Specific Notes
- **Existing AGENTS.md**: A template `AGENTS.md` already exists at the root — this should be **replaced/updated** with project-specific content, not the template placeholders
- **Python commands**: `uv sync`, `uv run pytest`, `uv run ruff check`, etc.
- **Docker commands**: `docker build`, `docker compose up`, etc.
- **Cross-reference**: Ensure consistency with `README.md` and `.ai-repository-summary.md`
- **No monorepo**: Single project — no nested AGENTS.md needed
- **Tech stack section**: Document Python 3.12, FastAPI, Pydantic, HTTPX, uv explicitly
- **Common pitfalls**: uv sync requires pyproject.toml; devcontainer may need GHCR image

#### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Commands fail during validation | **Medium** | High | Fix build issues before documenting; document known issues |
| Template AGENTS.md conflicts | **Low** | Medium | Replace entirely with project-specific content |

#### Events
- **post-assignment-complete**: `validate-assignment-completion` → `report-progress`

---

### Assignment 5: `debrief-and-document`

#### Goal
Create a comprehensive debriefing report capturing all learnings, deviations, errors, and recommendations from the project-setup workflow execution.

#### Key Acceptance Criteria
1. Structured report with all 12 required sections complete
2. All deviations from assignments documented
3. Execution trace saved as `debrief-and-document/trace.md`
4. Report reviewed and approved by stakeholder
5. Committed and pushed to repository

#### Prerequisites
- Assignments 1-4 complete
- All validation reports and progress reports available for reference

#### Dependencies
- **Depends on**: All preceding assignments complete

#### Project-Specific Notes
- **Track all deviations**: Especially missing ruleset file, missing template files, Python vs .NET adjustments
- **Action items**: Flag any plan-impacting findings for Phase 1 development
- **Execution trace**: Capture all terminal commands, file modifications, and GitHub interactions
- **Continuous improvement**: The debrief should inform improvements to the workflow assignments themselves
- **Template deviation**: If `ai-new-app-template.md` was missing and Implementation Spec was used instead, document this

#### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Incomplete deviation documentation | **Medium** | Medium | Review all validation reports before writing debrief |
| Missing action items | **Low** | Medium | Cross-reference all progress reports for findings |

#### Events
- **post-assignment-complete**: `validate-assignment-completion` → `report-progress`

---

### Assignment 6: `pr-approval-and-merge`

#### Goal
Complete the full PR approval and merge process — resolve all review comments, obtain approval, merge, close associated issues, and clean up.

#### Key Acceptance Criteria
1. All CI/CD checks pass
2. Code review delegated to independent reviewer (not self-review)
3. All review comments resolved via `ai-pr-comment-protocol.md` workflow
4. GraphQL verification: `pr-unresolved-threads.json` is empty
5. Stakeholder approval obtained
6. PR merged to `main`
7. Source branch deleted
8. Related issues closed/updated

#### Prerequisites
- Assignments 1-5 complete
- All changes committed and pushed to `dynamic-workflow-project-setup`
- PR exists and is up to date

#### Dependencies
- **Depends on**: All preceding assignments, all changes committed

#### Project-Specific Notes
- **PR already exists (#2)**: Either reuse or close and create new PR
- **CI pipeline**: `validate` workflow should run on the PR — ensure it passes
- **Branch protection**: If ruleset was imported, PR review is required
- **Merge strategy**: Follow repository convention (likely squash merge)
- **Issue closure**: Close the planning issue after merge if applicable
- **Commit hygiene**: Ensure ALL local changes are committed and pushed BEFORE merge

#### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CI failures on PR | **Medium** | High | Remediation loop: diagnose, fix, push, re-verify (max 3 attempts) |
| Merge conflicts | **Low** | Medium | Rebase working branch on latest main |
| Branch protection blocking merge | **Medium** | High | Ensure ruleset allows merge with required checks |
| Uncommitted changes lost at merge | **Low** | **Critical** | Verify `git status` clean before merge |

#### Events
- **post-assignment-complete**: N/A (final assignment)

---

### Post-Assignment Events (recurring after each assignment)

#### `validate-assignment-completion`
- **Executor**: Independent QA agent (e.g., `qa-test-engineer`)
- **Actions**: Check files exist, run build/test/lint commands, verify acceptance criteria, create validation report
- **Output**: `docs/validation/VALIDATION_REPORT_<assignment-name>_<timestamp>.md`
- **Gate**: If FAILED, halt workflow — do NOT proceed to next assignment

#### `report-progress`
- **Executor**: Progress reporting agent
- **Actions**: Generate structured progress report, capture outputs, validate acceptance criteria, create checkpoint state, file action items as GitHub issues
- **Output**: Progress report + action item issues filed
- **Gate**: Always proceeds (informational)

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    project-setup WORKFLOW SEQUENCE                          │
└─────────────────────────────────────────────────────────────────────────────┘

[PRE-SCRIPT EVENT]
    │
    ├── create-workflow-plan ──────────────────► plan_docs/workflow-plan.md
    │
[ASSIGNMENT 1: init-existing-repository]
    │
    ├── Create branch: dynamic-workflow-project-setup
    ├── Import branch protection ruleset (⚠️ may not exist)
    ├── Create GitHub Project (Board)
    ├── Import labels from .github/.labels.json
    ├── Rename devcontainer name + workspace file
    ├── Create PR to main
    │
    ├── [POST] validate-assignment-completion ──► VALIDATION_REPORT
    ├── [POST] report-progress ─────────────────► PROGRESS REPORT
    │
[ASSIGNMENT 2: create-app-plan]  ◄── depends on #1
    │
    ├── Analyze plan_docs/ (6 files)
    ├── Create plan_docs/tech-stack.md
    ├── Create plan_docs/architecture.md
    ├── Create plan issue (application-plan template)
    ├── Create milestones (Phase 0-3)
    ├── Link issue to Project + milestone + labels
    │
    ├── [POST] validate-assignment-completion ──► VALIDATION_REPORT
    ├── [POST] report-progress ─────────────────► PROGRESS REPORT
    │
[ASSIGNMENT 3: create-project-structure]  ◄── depends on #2
    │
    ├── Create pyproject.toml, src/, tests/, docs/ structure
    ├── Create Dockerfile, docker-compose.yml
    ├── Create CI/CD workflow files (pinned SHAs)
    ├── Create README.md + documentation structure
    ├── Create .ai-repository-summary.md
    ├── Validate build succeeds
    │
    ├── [POST] validate-assignment-completion ──► VALIDATION_REPORT
    ├── [POST] report-progress ─────────────────► PROGRESS REPORT
    │
[ASSIGNMENT 4: create-agents-md-file]  ◄── depends on #3
    │
    ├── Gather project context (README, repo summary, plan docs)
    ├── Validate all build/test/lint commands
    ├── Write AGENTS.md with all required sections
    ├── Cross-reference with existing docs
    │
    ├── [POST] validate-assignment-completion ──► VALIDATION_REPORT
    ├── [POST] report-progress ─────────────────► PROGRESS REPORT
    │
[ASSIGNMENT 5: debrief-and-document]  ◄── depends on #1-4
    │
    ├── Create debrief report (12 sections)
    ├── Create execution trace (debrief-and-document/trace.md)
    ├── Review with stakeholder
    │
    ├── [POST] validate-assignment-completion ──► VALIDATION_REPORT
    ├── [POST] report-progress ─────────────────► PROGRESS REPORT
    │
[ASSIGNMENT 6: pr-approval-and-merge]  ◄── depends on #1-5
    │
    ├── Verify CI passes on PR
    ├── Delegate code review (independent agent)
    ├── Resolve all review comments (ai-pr-comment-protocol)
    ├── Obtain stakeholder approval
    ├── Merge PR to main
    ├── Delete source branch
    ├── Close related issues
    │
[POST-SCRIPT EVENT]
    │
    └── Apply label: orchestration:plan-approved to plan issue
```

---

## 5. Dependency Graph

```
init-existing-repository
    │
    ▼
create-app-plan
    │
    ▼
create-project-structure
    │
    ▼
create-agents-md-file
    │
    ▼
debrief-and-document
    │
    ▼
pr-approval-and-merge
```

All assignments are **strictly sequential** — each depends on the successful completion (and validation) of the previous one.

---

## 6. Open Questions

### Critical (Must Resolve Before Execution)

1. **Missing Branch Protection Ruleset**: The file `.github/protected-branches_ruleset.json` referenced by `init-existing-repository` does not exist in the repository.  
   - **Question**: Should the agent create this file from scratch, or should the step be skipped and documented as a deviation?
   - **Recommendation**: Create a standard ruleset file with main branch protection (require PR, linear history, no force-push).

2. **Existing PR #2**: There is a prior PR on the target branch from a previous setup attempt.  
   - **Question**: Is PR #2 still valid, or should it be closed and a fresh attempt started?
   - **Recommendation**: Close PR #2, delete the branch, and start fresh.

3. **Missing `ai-new-app-template.md`**: The `create-app-plan` assignment expects this file in `plan_docs/`, but it does not exist. The Implementation Specification appears to be the equivalent.  
   - **Question**: Should the Implementation Specification serve as the primary requirements document?
   - **Recommendation**: Yes — use `OS-APOW Implementation Specification v1.md` as the application template equivalent.

4. **Missing Issue Template**: The `create-app-plan` assignment references `.github/ISSUE_TEMPLATE/application-plan.md`.  
   - **Question**: Does this template exist? If not, should the agent use Appendix A from the assignment definition?
   - **Recommendation**: Check for template; if missing, use Appendix A from the remote assignment definition.

### Medium Priority (Should Resolve Before Affected Assignment)

5. **Template .NET Artifacts**: The repository contains `global.json` (a .NET file) and other .NET template artifacts that are irrelevant for this Python project.  
   - **Question**: Should these be removed during `create-project-structure` or left in place?
   - **Recommendation**: Remove `global.json` and any other .NET-specific template files during project structure creation.

6. **Devcontainer Image**: The current devcontainer references `ghcr.io/intel-agency/workflow-orchestration-queue-romeo91/devcontainer:main-latest` which is the .NET/Aspire devcontainer.  
   - **Question**: Should the devcontainer be adapted for Python, or kept as-is for this workflow?
   - **Recommendation**: Keep as-is for the project-setup workflow; adapt for Python as part of Phase 1 development.

7. **Label Naming for Agent States**: The Implementation Spec defines labels like `agent:queued`, `agent:in-progress`, `agent:success`, `agent:error` but the existing `.labels.json` does not include these.  
   - **Question**: Should these agent-state labels be added during `init-existing-repository`?
   - **Recommendation**: Yes — update `.labels.json` to include all agent-state labels needed by the OS-APOW system.

### Low Priority (Informational)

8. **Scope of `create-app-plan`**: Should the plan issue be comprehensive (covering all 4 phases) or focused on Phase 1 (Sentinel MVP) for immediate execution?
   - **Recommendation**: Cover all phases at a high level; detail Phase 1 for immediate development.

9. **Test Framework**: What testing framework should be used?  
   - **Recommendation**: `pytest` with `pytest-asyncio` (standard for FastAPI/async Python).

10. **Linting/Formatting**: What Python linter/formatter?  
    - **Recommendation**: `ruff` (modern, fast, replaces flake8+isort+black).

---

## 7. Risk Register

| # | Risk | Likelihood | Impact | Phase | Mitigation | Owner |
|---|------|-----------|--------|-------|------------|-------|
| R1 | Branch protection ruleset file missing | High | Medium | A1 | Create file or document deviation | Agent |
| R2 | Existing PR #2 conflicts with fresh setup | Medium | Medium | A1 | Close PR #2, recreate branch | Agent |
| R3 | `ai-new-app-template.md` not found | High | Medium | A2 | Use Implementation Spec instead | Agent |
| R4 | Agent accidentally creates .NET project structure | Medium | High | A3 | Explicit Python/uv instructions in plan | Orchestrator |
| R5 | CI pipeline fails on new project structure | Medium | High | A6 | Remediation loop (max 3 attempts) | Agent |
| R6 | GitHub token scopes insufficient | Low | High | A1 | Pre-verify with test-github-permissions.ps1 | Agent |
| R7 | Uncommitted changes lost at merge | Low | Critical | A6 | Verify clean git status before merge | Agent |
| R8 | Validation gate blocks progression | Medium | Medium | All | Provide clear remediation steps in validation report | QA Agent |

---

## 8. Capacity & Estimation

| Assignment | Estimated Duration | Complexity | Key Bottleneck |
|------------|-------------------|------------|----------------|
| init-existing-repository | 10-15 min | Low | GitHub API calls, ruleset creation |
| create-app-plan | 30-45 min | High | Analysis depth, issue/milestone creation |
| create-project-structure | 45-60 min | High | File creation, Docker config, CI/CD setup |
| create-agents-md-file | 20-30 min | Medium | Command validation, documentation |
| debrief-and-document | 20-30 min | Medium | Comprehensive trace capture |
| pr-approval-and-merge | 20-40 min | Medium | CI wait, review resolution |
| **Validation (each)** | 5-10 min | Low | Automated checks |
| **Progress (each)** | 3-5 min | Low | Automated reporting |
| **Total Estimated** | **~3.5-5 hours** | | |

---

## 9. Assumptions

1. The executing agent has full GitHub API access with all required scopes.
2. The `plan_docs/` directory contents are accurate and represent the final project requirements.
3. The executing agent is running inside the repository's devcontainer with all tools available.
4. The `GH_ORCHESTRATION_AGENT_TOKEN` secret is available for branch protection operations.
5. All work will be done on the `dynamic-workflow-project-setup` branch targeting `main`.
6. The existing template infrastructure (scripts, workflows, devcontainer) will not be removed — only extended.
7. Stakeholder approval can be obtained synchronously during the workflow execution.

---

*Plan created by Planner Agent on 2026-04-27. This document should be updated if any deviations occur during execution.*
