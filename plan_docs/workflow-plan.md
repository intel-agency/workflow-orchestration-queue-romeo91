# Workflow Execution Plan: project-setup

**Repository:** `intel-agency/workflow-orchestration-queue-romeo91`
**Dynamic Workflow:** `project-setup`
**Plan Created:** 2026-04-13
**Branch:** `dynamic-workflow-project-setup`

---

## 1. Overview

### Workflow Name

**project-setup** — the initial dynamic workflow executed to bootstrap a new repository from the `workflow-orchestration-queue-romeo91` template into a fully initialized, project-tracked, and development-ready state.

### Project Description

**workflow-orchestration-queue (OS-APOW)** is a headless agentic orchestration platform that transforms GitHub Issues into autonomous development tasks. The system comprises four pillars:

1. **The Ear (Notifier)** — FastAPI webhook receiver for event ingestion
2. **The State (Queue)** — GitHub Issues as distributed state ("Markdown as a Database")
3. **The Brain (Sentinel)** — Polling orchestrator managing worker lifecycles
4. **The Hands (Worker)** — Opencode agent in isolated DevContainers

### Total Assignments

6 sequential assignments + 1 pre-script event + 2 post-assignment validation assignments per step + 1 post-script event.

| # | Assignment | Short-ID |
|---|-----------|----------|
| 0 | create-workflow-plan | `create-workflow-plan` |
| 1 | init-existing-repository | `init-existing-repository` |
| 2 | create-app-plan | `create-app-plan` |
| 3 | create-project-structure | `create-project-structure` |
| 4 | create-agents-md-file | `create-agents-md-file` |
| 5 | debrief-and-document | `debrief-and-document` |
| 6 | pr-approval-and-merge | `pr-approval-and-merge` |

### High-Level Summary

This workflow transforms a freshly cloned template repository into a production-ready development project. It starts by creating a workflow plan (this document), then systematically initializes the repository (branch, labels, project board, renamed files, PR), creates a detailed application plan from the plan documents, scaffolds the full project structure, generates an AGENTS.md for AI agent consumption, performs a comprehensive debrief, and finally merges the setup PR.

---

## 2. Project Context Summary

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.12+ |
| Web Framework | FastAPI | Latest (via uv) |
| ASGI Server | Uvicorn | Latest |
| Validation | Pydantic | v2 (via FastAPI) |
| Async HTTP | HTTPX | Latest |
| Package Manager | uv | Latest (Rust-based) |
| Containers | Docker + Docker Compose | Latest |
| Scripts | PowerShell Core (pwsh) / Bash | Cross-platform |
| LLM Runtime | opencode CLI | 1.2.24 |
| Models | ZhipuAI GLM (zai-coding-plan/glm-5) | Current |

### Repository Details

- **Owner:** `intel-agency`
- **Repo:** `workflow-orchestration-queue-romeo91`
- **Template Source:** `intel-agency/workflow-orchestration-queue-romeo91` (GitHub template repo)
- **Branch Strategy:** `main` (stable) + `develop` (integration) + feature branches
- **Devcontainer:** Prebuilt GHCR image, auto-starts `opencode serve` on port 4096

### Key Constraints

1. **No `.global.json`** — This is a Python/Shell ecosystem, not .NET; all dependency management via `pyproject.toml` and `uv.lock`
2. **Action SHA Pinning** — All GitHub Actions in workflows must be pinned to specific commit SHAs (not version tags)
3. **Shell-First Integration** — Sentinel interacts with workers exclusively via `./scripts/devcontainer-opencode.sh`; no direct Docker SDK
4. **Polling-First Resiliency** — Polling is the primary discovery mechanism; webhooks are an optimization
5. **Script-First** — Do not reimplement container management in Python
6. **Markdown as a Database** — All state lives in GitHub Issues/Labels
7. **Template Placeholders** — `workflow-orchestration-queue-romeo91` and `intel-agency` are template placeholders already replaced in this clone

### Key Plan Documents (in `plan_docs/`)

| Document | Purpose |
|----------|---------|
| OS-APOW Architecture Guide v3.md | System architecture: Sentinel, Notifier, Worker, Queue |
| OS-APOW Development Plan v4.md | 4-phase roadmap: Seeding → Sentinel MVP → Webhook Ear → Deep Planning |
| OS-APOW Implementation Specification v1.md | Detailed implementation specs, requirements, test cases |
| notifier_service.py | Skeleton FastAPI webhook receiver |
| orchestrator_sentinel.py | Skeleton Sentinel polling orchestrator |
| interactive-report.html | Interactive project report |

### Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| GitHub API Rate Limiting | High | Use GitHub App tokens (5,000 req/hr); aggressive caching; long-polling intervals |
| LLM Looping/Hallucination | High | `max_steps` timeout; cost guardrails; retry counter (3 max then `agent:stalled`) |
| Concurrency Collisions | Medium | GitHub Assignees as distributed lock semaphore |
| Container Drift | Medium | `docker-compose down -v && up --build` between major epics |
| Security Injection via Webhook | Medium | HMAC SHA256 signature validation on all webhook endpoints |
| Missing `GH_ORCHESTRATION_AGENT_TOKEN` | Medium | Branch protection import requires PAT with `administration: write`; fallback to GITHUB_TOKEN may fail |
| `protected-branches_ruleset.json` absent | Low | Template doesn't include this file; `init-existing-repository` step 2 must handle gracefully |

---

## 3. Assignment Execution Plan

---

### Assignment 0: create-workflow-plan (Pre-Script Event)

| Field | Value |
|-------|-------|
| **Short-ID** | `create-workflow-plan` |
| **Trigger** | `pre-script-begin` event |
| **Goal** | Produce this workflow execution plan document |

**Key Acceptance Criteria:**

- All plan_docs/ files read and analyzed
- All 6 workflow assignments traced and read from remote canonical repository
- Workflow plan produced with all required sections (Overview, Context, Assignments, Sequencing, Open Questions)
- Plan committed to `plan_docs/workflow-plan.md` on branch `dynamic-workflow-project-setup`

**Dependencies:** None (first action in the workflow)

**Events:** None

---

### Assignment 1: init-existing-repository

| Field | Value |
|-------|-------|
| **Short-ID** | `init-existing-repository` |
| **Trigger** | First assignment in `$assignments` array |
| **Goal** | Initialize the repository: create branch, import labels, create GitHub Project, rename files, open setup PR |

**Key Acceptance Criteria:**

1. New branch `dynamic-workflow-project-setup` created from `main` (must be first action)
2. Branch protection ruleset imported from `.github/protected-branches_ruleset.json` (if file exists; skip if absent)
3. GitHub Project created for issue tracking (named after repository)
4. GitHub Project linked to repository with columns: Not Started, In Progress, In Review, Done
5. Labels imported from `.github/.labels.json` via `scripts/import-labels.ps1`
6. `ai-new-app-template.code-workspace` renamed to `<repo-name>.code-workspace`
7. `.devcontainer/devcontainer.json` `name` property updated to `<repo-name>-devcontainer`
8. PR created from `dynamic-workflow-project-setup` to `main`

**Project-Specific Notes:**

- The repository name is `workflow-orchestration-queue-romeo91`; workspace file becomes `workflow-orchestration-queue-romeo91.code-workspace`
- `.github/protected-branches_ruleset.json` does NOT exist in this template — this step should be skipped gracefully
- Labels from `.github/.labels.json` include the OS-APOW-specific agent labels: `agent:queued`, `agent:in-progress`, `agent:success`, `agent:error`, `agent:infra-failure`, `agent:stalled-budget`, `agent:reconciling`
- The `scripts/import-labels.ps1` script requires PowerShell Core (`pwsh`)
- The PR created here will be used by `pr-approval-and-merge` in Assignment 6 — record the PR number

**Prerequisites:**

- `gh` CLI authenticated with scopes: `repo`, `project`, `read:project`, `read:user`, `user:email`
- `pwsh` available for label import script
- `GH_ORCHESTRATION_AGENT_TOKEN` or `GITHUB_TOKEN` with `administration: write` for ruleset import

**Dependencies:** None (first main assignment)

**Risks:**

- Branch protection import will fail — file doesn't exist in template. **Mitigation:** Skip step with warning.
- GitHub Project creation may fail if org-level permissions are insufficient. **Mitigation:** Verify with `scripts/test-github-permissions.ps1`.
- PR creation requires at least one commit. **Mitigation:** Ensure file renames are committed before PR creation.

**Events:**

- `post-assignment-complete`: Run `validate-assignment-completion` then `report-progress`
- Output recorded as `#initiate-new-repository.init-existing-repository`

---

### Assignment 2: create-app-plan

| Field | Value |
|-------|-------|
| **Short-ID** | `create-app-plan` |
| **Trigger** | Sequential after `init-existing-repository` completion |
| **Goal** | Analyze plan documents and create a comprehensive application plan as a GitHub Issue with milestones |

**Key Acceptance Criteria:**

1. Application template (`plan_docs/OS-APOW Implementation Specification v1.md`) thoroughly analyzed
2. All components and dependencies planned
3. Plan documented as GitHub Issue using `.github/ISSUE_TEMPLATE/application-plan.md` template
4. Milestones created for each development phase:
   - Phase 0: Seeding & Bootstrapping
   - Phase 1: The Sentinel (MVP)
   - Phase 2: The Ear (Webhook Automation)
   - Phase 3: Deep Orchestration & Self-Healing
5. Plan issue linked to GitHub Project
6. Plan issue assigned to "Phase 0: Seeding & Bootstrapping" milestone
7. Labels applied: `planning`, `documentation`
8. `plan_docs/tech-stack.md` created documenting the technology stack
9. `plan_docs/architecture.md` created documenting high-level architecture
10. Plan ready for development — no implementation code written

**Project-Specific Notes:**

- The "application template" is the `OS-APOW Implementation Specification v1.md` combined with the Architecture Guide and Development Plan
- This is a **PLANNING ONLY** assignment — no code, no project files, no directory structures
- The issue template may need to be located at `.github/ISSUE_TEMPLATE/application-plan.md` — verify it exists
- Milestones should align with the 4-phase roadmap in the Development Plan v4:
  - Phase 0: Seeding & Bootstrapping
  - Phase 1: The Sentinel (MVP) — Polling + Shell-Bridge + Status Feedback
  - Phase 2: The Ear — FastAPI Webhook Receiver + Template Triaging
  - Phase 3: Deep Orchestration — Architect Sub-Agent + Bug Correction + Indexing
- Reference example plans: [advanced-memory3 #12](https://github.com/nam20485/advanced-memory3/issues/12), [support-assistant #2](https://github.com/nam20485/support-assistant/issues/2)

**Prerequisites:**

- `init-existing-repository` completed (labels, project, milestones infrastructure in place)
- GitHub Project exists for linking the issue

**Dependencies:** `init-existing-repository` (labels and project must exist)

**Risks:**

- Issue template may not exist at expected path. **Mitigation:** Check `.github/ISSUE_TEMPLATE/`; create if absent or use Appendix A from the assignment definition.
- Plan may be too large for a single issue body. **Mitigation:** Focus on high-level phases and epics; link to plan_docs for details.

**Events:**

- `pre-assignment-begin`: Run `gather-context` assignment
- `on-assignment-failure`: Run `recover-from-error` assignment
- `post-assignment-complete`: Run `validate-assignment-completion` then `report-progress`
- Output recorded as `#initiate-new-repository.create-app-plan`

---

### Assignment 3: create-project-structure

| Field | Value |
|-------|-------|
| **Short-ID** | `create-project-structure` |
| **Trigger** | Sequential after `create-app-plan` completion and approval |
| **Goal** | Create the actual project scaffolding: solution structure, Docker, CI/CD, documentation, and repository summary |

**Key Acceptance Criteria:**

1. Solution/project structure created following the application plan's tech stack (Python/uv)
2. All required project files and directories established per the Implementation Specification:
   ```
   workflow-orchestration-queue-romeo91/
   ├── pyproject.toml
   ├── uv.lock
   ├── src/
   │   ├── notifier_service.py
   │   ├── orchestrator_sentinel.py
   │   ├── models/
   │   │   ├── work_item.py
   │   │   └── github_events.py
   │   └── interfaces/
   │       └── i_task_queue.py
   ├── scripts/
   │   ├── devcontainer-opencode.sh
   │   ├── gh-auth.ps1
   │   └── update-remote-indices.ps1
   ├── local_ai_instruction_modules/
   │   ├── create-app-plan.md
   │   ├── perform-task.md
   │   └── analyze-bug.md
   ├── tests/
   │   ├── __init__.py
   │   └── test_notifier.py
   └── docs/
   ```
3. Dockerfile created for each service component
4. `docker-compose.yml` created for local development
5. Configuration files (env templates, pyproject.toml with uv) created
6. CI/CD pipeline structure established in `.github/workflows/`
7. All workflow actions pinned to specific commit SHAs
8. Documentation structure: README.md, docs/, API docs, ADRs
9. Test project structure created
10. `.ai-repository-summary.md` created per the `create-repository-summary` spec
11. Build validation: project builds/tests successfully
12. Stakeholder approval obtained

**Project-Specific Notes:**

- Tech stack is Python 3.12+ with `uv` — NOT .NET. Use `pyproject.toml`, not `.sln`/`.csproj`
- The skeleton code already exists in `plan_docs/notifier_service.py` and `plan_docs/orchestrator_sentinel.py` — these should be moved/adapted to `src/`
- Docker healthchecks must NOT use `curl` — use Python stdlib `urllib.request` instead
- `COPY src/ ./src/` must appear before `uv pip install -e .` in Dockerfile (editable install requires source)
- Existing scripts/ directory already has some scripts — extend, don't replace
- The `local_ai_instruction_modules/` directory already exists with instruction files
- CI/CD workflow actions MUST be pinned to commit SHAs (directive from project-setup workflow)

**Prerequisites:**

- `create-app-plan` completed and approved
- Application plan issue exists with documented tech stack and architecture

**Dependencies:** `create-app-plan` (plan must exist to guide structure)

**Risks:**

- Existing repository files may conflict with planned structure. **Mitigation:** Merge carefully; don't overwrite template infrastructure (`.devcontainer/`, `.github/`, `.opencode/`).
- Docker build may fail if dependencies aren't properly specified. **Mitigation:** Start with minimal `pyproject.toml`; iterate.
- Tests may not pass initially with skeleton code. **Mitigation:** Create basic smoke tests, not comprehensive ones.

**Events:**

- `post-assignment-complete`: Run `validate-assignment-completion` then `report-progress`
- Output recorded as `#initiate-new-repository.create-project-structure`

---

### Assignment 4: create-agents-md-file

| Field | Value |
|-------|-------|
| **Short-ID** | `create-agents-md-file` |
| **Trigger** | Sequential after `create-project-structure` completion and approval |
| **Goal** | Create a comprehensive `AGENTS.md` file at the repository root for AI coding agents |

**Key Acceptance Criteria:**

1. `AGENTS.md` exists at repository root
2. Contains project overview (purpose, tech stack: Python 3.12, FastAPI, Pydantic, uv, Docker)
3. Contains validated setup/build/test commands:
   - Install: `uv sync`
   - Run tests: `uv run pytest`
   - Lint: `uv run ruff check .`
   - Docker: `docker-compose up --build`
4. Contains code style and conventions section
5. Contains project structure / directory layout
6. Contains testing instructions
7. Contains PR / commit guidelines
8. All commands have been validated by running them
9. Complements (not duplicates) README.md and `.ai-repository-summary.md`
10. Stakeholder approval obtained

**Project-Specific Notes:**

- Must reference the existing `AGENTS.md` at root (the template-level one) — this assignment will create/replace it with project-specific content
- Should document the OS-APOW-specific conventions:
  - Agent labels: `agent:queued`, `agent:in-progress`, `agent:success`, `agent:error`
  - Shell-bridge pattern: `./scripts/devcontainer-opencode.sh`
  - Pydantic models for WorkItem, TaskType, WorkItemStatus
  - Instruction modules in `local_ai_instruction_modules/`
- Commands must be verified working in the devcontainer environment
- Cross-reference with `plan_docs/` architecture and tech-stack documents

**Prerequisites:**

- `create-project-structure` completed (actual files exist to document)
- Build/test tooling is functional

**Dependencies:** `create-project-structure` (project must exist to document its commands)

**Risks:**

- Commands may not work yet if project structure is incomplete. **Mitigation:** Ensure `create-project-structure` fully validates build before this step.
- May conflict with existing template `AGENTS.md`. **Mitigation:** Replace with project-specific content.

**Events:**

- `post-assignment-complete`: Run `validate-assignment-completion` then `report-progress`
- Output recorded as `#initiate-new-repository.create-agents-md-file`

---

### Assignment 5: debrief-and-document

| Field | Value |
|-------|-------|
| **Short-ID** | `debrief-and-document` |
| **Trigger** | Sequential after `create-agents-md-file` completion and approval |
| **Goal** | Create a comprehensive debrief report capturing key learnings, deviations, and improvement recommendations |

**Key Acceptance Criteria:**

1. Detailed report created following the 12-section structured template
2. Report saved as `.md` file in the repository
3. All deviations from assignments documented
4. Execution trace saved as `debrief-and-document/trace.md`
5. Plan-impacting findings flagged as ACTION ITEMS
6. Report reviewed and approved by stakeholder
7. Report committed and pushed to working branch

**Report Sections (12 required):**

1. Executive Summary
2. Workflow Overview (table of all assignments)
3. Key Deliverables
4. Lessons Learned
5. What Worked Well
6. What Could Be Improved
7. Errors Encountered and Resolutions
8. Complex Steps and Challenges
9. Suggested Changes (Workflow, Agent, Prompt, Script)
10. Metrics and Statistics
11. Future Recommendations (Short/Medium/Long Term)
12. Conclusion

**Project-Specific Notes:**

- The `debrief-and-document/trace.md` will contain a complete execution trace of all terminal commands, file operations, and interactions
- Must flag any plan-impacting findings — particularly:
  - Missing `protected-branches_ruleset.json` (if not handled)
  - Any assignment steps that were skipped or failed
  - CI/CD pipeline issues
  - Authentication/permission challenges
- Suggested changes should reference specific assignment files in `nam20485/agent-instructions`
- The debrief triggers the `continuous-improvement` assignment after completion

**Prerequisites:**

- All previous assignments completed (`init-existing-repository` through `create-agents-md-file`)

**Dependencies:** `create-agents-md-file` (must be the last code-producing step before debrief)

**Risks:**

- Report may be superficial if agent doesn't carefully track deviations during execution. **Mitigation:** Maintain running notes during each assignment.
- ACTION ITEMS may not get follow-up. **Mitigation:** Create GitHub Issues for each ACTION ITEM.

**Events:**

- `post-assignment-complete`: Run `validate-assignment-completion` then `report-progress`
- After completion: Initiate `continuous-improvement` assignment
- Output recorded as `#initiate-new-repository.debrief-and-document`

---

### Assignment 6: pr-approval-and-merge

| Field | Value |
|-------|-------|
| **Short-ID** | `pr-approval-and-merge` |
| **Trigger** | Sequential after `debrief-and-document` completion and approval |
| **Goal** | Complete the full PR approval and merge process for the setup PR |

**Key Acceptance Criteria:**

1. All CI/CD status checks pass (CI remediation loop: up to 3 attempts)
2. Code review delegated to `code-reviewer` subagent (NOT self-review)
3. Auto-reviewer comments (Copilot, CodeQL, etc.) waited for and resolved
4. All PR review comments resolved via `ai-pr-comment-protocol.md`
5. GraphQL verification: `pr-unresolved-threads.json` is empty
6. Stakeholder/Delegating Agent approval obtained
7. PR merged to `main`
8. Source branch `dynamic-workflow-project-setup` deleted
9. Related setup issues closed
10. Output `result` set to `"merged"`, `"pending"`, or `"failed"`

**Project-Specific Notes:**

- `$pr_num` is extracted from `#initiate-new-repository.init-existing-repository` (the PR created in Assignment 1)
- This is an **automated setup PR** — self-approval by the orchestrator is acceptable per the project-setup workflow spec
- No human stakeholder approval is required (but CI remediation loop MUST still execute)
- The PR contains ALL work from Assignments 1–5: labels, project board, renamed files, app plan, project structure, AGENTS.md, debrief
- After successful merge, the `post-script-complete` event will apply `orchestration:plan-approved` label to the application plan issue

**Phases:**

| Phase | Description |
|-------|-------------|
| Phase 0 | Pre-flight: Confirm PR number, auth, GraphQL snapshot |
| Phase 0.5 | CI Verification: Poll checks, remediate up to 3 attempts |
| Phase 0.75 | Code Review Delegation: Assign `code-reviewer`, wait for auto-reviewers |
| Phase 1 | Resolve Review Comments: Execute `pr-review-comments` protocol |
| Phase 2 | Secure Approval: Address follow-ups, record approval |
| Phase 3 | Merge & Wrap-Up: Merge, delete branch, close issues, set output |

**Prerequisites:**

- All 5 previous assignments completed
- PR exists and has commits ahead of `main`
- `gh` CLI authenticated

**Dependencies:** `debrief-and-document` (all work must be committed to the PR branch before merge)

**Risks:**

- CI checks may fail repeatedly. **Mitigation:** 3-attempt remediation loop; escalate if unresolvable.
- Merge conflicts if `main` has changed since branch creation. **Mitigation:** Rebase or resolve conflicts.
- Branch protection rules may block merge. **Mitigation:** Verify ruleset configuration; ensure checks pass.

**Events:**

- `post-assignment-complete`: Run `validate-assignment-completion` then `report-progress`
- Output recorded as `#initiate-new-repository.pr-approval-and-merge`
- **Post-script:** Apply `orchestration:plan-approved` label to application plan issue

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     project-setup Dynamic Workflow                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────┐                                      │
│  │ pre-script-begin                  │                                      │
│  │  └─ create-workflow-plan  ────────┼──► plan_docs/workflow-plan.md       │
│  └───────────────────────────────────┘          (THIS DOCUMENT)            │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Assignment 1: init-existing-repository                             │    │
│  │  ├─ Create branch: dynamic-workflow-project-setup                   │    │
│  │  ├─ Import branch protection (skip if absent)                       │    │
│  │  ├─ Create GitHub Project + columns                                │    │
│  │  ├─ Import labels from .github/.labels.json                        │    │
│  │  ├─ Rename workspace + devcontainer files                           │    │
│  │  └─ Create PR (#N) ───────────────────────────────────► PR NUMBER  │    │
│  │                                                                     │    │
│  │  [post-assignment: validate + report]                               │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Assignment 2: create-app-plan                                      │    │
│  │  ├─ pre: gather-context                                            │    │
│  │  ├─ Analyze plan_docs/ (Arch Guide, Dev Plan, Impl Spec)           │    │
│  │  ├─ Create tech-stack.md + architecture.md in plan_docs/           │    │
│  │  ├─ Create application plan GitHub Issue                           │    │
│  │  ├─ Create milestones (Phase 0–3)                                  │    │
│  │  └─ Link issue to Project + milestone                              │    │
│  │                                                                     │    │
│  │  [post-assignment: validate + report]                               │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Assignment 3: create-project-structure                             │    │
│  │  ├─ Create pyproject.toml, src/, tests/, scripts/                  │    │
│  │  ├─ Create Dockerfile + docker-compose.yml                         │    │
│  │  ├─ Create CI/CD workflows (SHA-pinned)                            │    │
│  │  ├─ Create documentation (README.md, docs/, ADRs)                  │    │
│  │  ├─ Create .ai-repository-summary.md                               │    │
│  │  └─ Validate build + tests                                         │    │
│  │                                                                     │    │
│  │  [post-assignment: validate + report]                               │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Assignment 4: create-agents-md-file                                │    │
│  │  ├─ Gather project context from README, plan_docs, CI workflows    │    │
│  │  ├─ Validate build/test/lint commands                               │    │
│  │  ├─ Draft AGENTS.md (project overview, commands, structure, etc.)   │    │
│  │  └─ Cross-reference with README.md + .ai-repository-summary.md     │    │
│  │                                                                     │    │
│  │  [post-assignment: validate + report]                               │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Assignment 5: debrief-and-document                                 │    │
│  │  ├─ Create 12-section debrief report                               │    │
│  │  ├─ Create execution trace: debrief-and-document/trace.md          │    │
│  │  ├─ Flag ACTION ITEMS for plan adjustments                         │    │
│  │  └─ Commit + push to branch                                        │    │
│  │                                                                     │    │
│  │  [post-assignment: validate + report]                               │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Assignment 6: pr-approval-and-merge                                │    │
│  │  ├─ Phase 0:   Pre-flight (PR #N, auth, snapshot)                  │    │
│  │  ├─ Phase 0.5: CI verification + remediation (≤3 attempts)         │    │
│  │  ├─ Phase 0.75: Code review delegation                             │    │
│  │  ├─ Phase 1:   Resolve review comments (pr-review-comments)        │    │
│  │  ├─ Phase 2:   Secure approval (self-approval OK for setup PR)     │    │
│  │  ├─ Phase 3:   Merge PR → main                                     │    │
│  │  ├─ Delete branch, close issues                                    │    │
│  │  └─ Set result = "merged"                                          │    │
│  │                                                                     │    │
│  │  [post-assignment: validate + report]                               │    │
│  └──────────────────────────────────┬──────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │ post-script-complete                                              │      │
│  │  └─ Apply orchestration:plan-approved label to app plan issue     │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Dependency Chain:**

```
create-workflow-plan
        │
        ▼
init-existing-repository ──► (PR #N created)
        │
        ▼
create-app-plan ──► (Plan issue + milestones created)
        │
        ▼
create-project-structure ──► (Source code + Docker + CI/CD created)
        │
        ▼
create-agents-md-file ──► (AGENTS.md created)
        │
        ▼
debrief-and-document ──► (Debrief report created)
        │
        ▼
pr-approval-and-merge ──► (PR merged, branch deleted)
        │
        ▼
orchestration:plan-approved label applied
```

---

## 5. Open Questions

### Q1: Branch Protection Ruleset File Missing

The `init-existing-repository` assignment requires importing a branch protection ruleset from `.github/protected-branches_ruleset.json`, but this file does NOT exist in the current template. Should the step be skipped, or should a default ruleset be created first?

**Recommendation:** Skip the step with a documented warning. Create the ruleset file as a follow-up task if branch protection is desired.

### Q2: Application Plan Issue Template Location

The `create-app-plan` assignment references `.github/ISSUE_TEMPLATE/application-plan.md` as the plan template. Does this file exist in the template, or should the Appendix A content from the remote assignment be used directly?

**Recommendation:** Check for the file; if absent, use Appendix A from the remote assignment definition as the template.

### Q3: Existing AGENTS.md Replacement

The template repository already has an `AGENTS.md` at root (with template-level instructions). The `create-agents-md-file` assignment will replace it with project-specific content. Should the template instructions be preserved anywhere before replacement?

**Recommendation:** The template `AGENTS.md` is already in git history. Replace with project-specific content. The original can be recovered from git if needed.

### Q4: Skeleton Python Files — Move or Reference?

`plan_docs/notifier_service.py` and `plan_docs/orchestrator_sentinel.py` contain skeleton implementations. Should `create-project-structure` move these to `src/` directly, or create fresh implementations referencing them?

**Recommendation:** Adapt the skeleton code into proper `src/` modules, maintaining the existing structure and imports. These are reference implementations that need to be production-ready.

### Q5: Milestone Naming Convention

The Development Plan v4 defines 4 phases (0–3). Should milestones be named exactly as:
- "Phase 0: Seeding & Bootstrapping"
- "Phase 1: The Sentinel (MVP)"
- "Phase 2: The Ear (Webhook Automation)"
- "Phase 3: Deep Orchestration & Self-Healing"

Or should they follow a different naming pattern?

**Recommendation:** Use the phase names from the Development Plan v4 directly for consistency with the plan documents.

### Q6: Self-Approval Scope for Setup PR

The project-setup workflow specifies that self-approval by the orchestrator is acceptable for the setup PR. However, should the `code-reviewer` subagent still perform a full code review (Phase 0.75 of `pr-approval-and-merge`) before merge?

**Recommendation:** Yes — run the full code review protocol for quality assurance, but skip the human approval gate.

### Q7: CI/CD Workflows for Python Project

The template's existing CI workflows (`validate`, `publish-docker`, `prebuild-devcontainer`) are designed for the template infrastructure. The Python application will need its own CI workflows. Should these be:
- a) Added alongside existing workflows
- b) Replace existing workflows
- c) Created as separate workflow files

**Recommendation:** Add new Python-specific workflows (e.g., `python-ci.yml`, `python-test.yml`) alongside the existing template infrastructure workflows. The existing workflows manage the devcontainer/image pipeline; the new ones manage the Python application.

### Q8: `GH_ORCHESTRATION_AGENT_TOKEN` Availability

The `init-existing-repository` assignment uses `GH_ORCHESTRATION_AGENT_TOKEN` (a PAT) for ruleset import, which requires `administration: write` scope. Is this secret available in the repository?

**Recommendation:** If the secret is not available, skip the ruleset import step and document it as an ACTION ITEM in the debrief.
