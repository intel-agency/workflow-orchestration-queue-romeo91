# Workflow Execution Plan: project-setup

**Workflow**: `project-setup`  
**Source File**: `ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md`  
**Repository**: `intel-agency/workflow-orchestration-queue-romeo91`  
**Branch**: `dynamic-workflow-project-setup`  
**Date**: 2026-04-20  

---

## 1. Overview

This document provides the execution plan for the **project-setup** dynamic workflow, which initializes the `workflow-orchestration-queue` repository for active development. The workflow establishes the foundational project infrastructure — including repository configuration, application planning, project scaffolding, and documentation — in a single, cohesive PR that is reviewed and merged at the end.

### Workflow Summary

| Property | Value |
|---|---|
| **Dynamic Workflow** | `project-setup` |
| **Total Main Assignments** | 6 |
| **Event Assignments** | 4 (create-workflow-plan, validate-assignment-completion ×6, report-progress ×6, plan-approved) |
| **Triggering Event** | Successful `prebuild-devcontainer` workflow_run on `main` |
| **Working Branch** | `dynamic-workflow-project-setup` |
| **Final Deliverable** | Merged setup PR with all project infrastructure in place |

### Execution Flow at a Glance

```
pre-script-begin: create-workflow-plan ← YOU ARE HERE
        │
        ▼
[1] init-existing-repository
        │  post: validate-assignment-completion, report-progress
        ▼
[2] create-app-plan
        │  pre: gather-context
        │  post: validate-assignment-completion, report-progress
        ▼
[3] create-project-structure
        │  post: validate-assignment-completion, report-progress
        ▼
[4] create-agents-md-file
        │  post: validate-assignment-completion, report-progress
        ▼
[5] debrief-and-document
        │  post: validate-assignment-completion, report-progress
        ▼
[6] pr-approval-and-merge
        │  post: validate-assignment-completion, report-progress
        ▼
post-script-complete: apply orchestration:plan-approved label
```

---

## 2. Project Context Summary

### Application: OS-APOW (workflow-orchestration-queue)

**OS-APOW** (Opencode-Server Agent Workflow Orchestration Queue) is a **headless agentic orchestration platform** that transforms GitHub Issues into autonomous execution orders fulfilled by specialized AI agents running in isolated DevContainers. It replaces interactive AI coding workflows with a persistent, event-driven background service.

### Technology Stack

| Layer | Technology |
|---|---|
| **Primary Language** | Python 3.12+ |
| **Web Framework** | FastAPI + Uvicorn |
| **Data Validation** | Pydantic |
| **Async HTTP Client** | HTTPX |
| **Package Manager** | uv (Rust-based) |
| **Containerization** | Docker, Docker Compose, DevContainers |
| **Agent Runtime** | opencode CLI (GLM-5 via ZHIPU_API_KEY) |
| **Shell Scripts** | PowerShell Core (pwsh), Bash |
| **Task Queue** | GitHub Issues + Labels ("Markdown as a Database") |
| **CI/CD** | GitHub Actions (SHA-pinned) |

### System Components

1. **The Ear (Work Event Notifier)** — FastAPI webhook receiver with HMAC signature validation and intelligent event triaging
2. **The State (Work Queue)** — Distributed state via GitHub Issues, Labels, Milestones; Assignees used as distributed locks
3. **The Brain (Sentinel Orchestrator)** — Async Python polling service (60s interval) that discovers queued tasks, claims them, and dispatches workers
4. **The Hands (Opencode Worker)** — Isolated DevContainer executing markdown-based instruction modules against cloned codebases

### Development Phases (from Plan Docs)

| Phase | Title | Status |
|---|---|---|
| Phase 0 | Seeding & Bootstrapping | Current (this workflow) |
| Phase 1 | The Sentinel (MVP) | Planned |
| Phase 2 | The Ear (Webhook Automation) | Planned |
| Phase 3 | Deep Orchestration & Self-Healing | Planned |

### Key Planning Documents in `plan_docs/`

| File | Content |
|---|---|
| `OS-APOW Architecture Guide v3.md` | System-level diagrams, component overview, ADRs, data flow, security model, self-bootstrapping lifecycle |
| `OS-APOW Development Plan v4.md` | 4-phase roadmap with user stories, acceptance criteria, risk assessment |
| `OS-APOW Implementation Specification v1.md` | Detailed app spec: features, test cases, logging, containerization, project structure, deliverables |
| `interactive-report.html` | React-based interactive visualization of the architecture and plan |
| `notifier_service.py` | Skeleton FastAPI webhook receiver with HMAC validation, WorkItem model, ITaskQueue interface |
| `orchestrator_sentinel.py` | Skeleton Sentinel orchestrator with polling, task claiming, shell-bridge dispatch |

### Repository Facts

- **Template origin**: Cloned from `intel-agency/workflow-orchestration-queue-romeo91`
- **Existing infrastructure**: DevContainer configs, GitHub Actions workflows (validate, publish-docker, prebuild-devcontainer, orchestrator-agent), shell scripts, test suite
- **Branch protection ruleset**: Located at `.github/protected branches - main - ruleset.json` (note: filename differs from the expected `protected-branches_ruleset.json`)
- **Labels**: Defined in `.github/.labels.json` (15 labels, missing some labels needed for later phases like `planning`, `orchestration:plan-approved`)
- **No `ai-new-app-template.md`**: The primary application specification is `OS-APOW Implementation Specification v1.md`

---

## 3. Assignment Execution Plan

### Assignment 1: `init-existing-repository`

| Field | Details |
|---|---|
| **Goal** | Initialize the existing repository by configuring settings, creating a GitHub Project, importing labels, renaming template files, and opening a setup PR |
| **Key Acceptance Criteria** | (1) New branch `dynamic-workflow-project-setup` created; (2) Branch protection ruleset imported; (3) GitHub Project created with Board columns; (4) Labels imported from `.github/.labels.json`; (5) Devcontainer/workspace files renamed with repo prefix; (6) PR created to `main` |
| **Project-Specific Notes** | This is a template-clone repo that already has infrastructure (workflows, scripts, devcontainer). The devcontainer name is already `workflow-orchestration-queue-romeo91` — needs `"-devcontainer"` suffix appended. The workspace file is already correctly named. The branch protection ruleset file has spaces in its name (`protected branches - main - ruleset.json`) which differs from the assignment's expected `protected-branches_ruleset.json` — the agent must locate the actual file. GitHub Project creation requires `project` scope on the token. The `GH_ORCHESTRATION_AGENT_TOKEN` may be needed for ruleset import (requires `administration: write`). |
| **Prerequisites** | GitHub auth with `repo`, `project`, `read:project`, `read:user`, `user:email` scopes; `administration: write` for rulesets |
| **Dependencies** | None (first assignment) |
| **Risks** | (1) Branch protection ruleset file name mismatch may cause import failure; (2) GitHub Project API scopes may be missing; (3) PAT token may lack `administration: write` for ruleset import; (4) PR creation may fail if no commits are pushed first |
| **Events** | post-assignment-complete: `validate-assignment-completion`, `report-progress` |

### Assignment 2: `create-app-plan`

| Field | Details |
|---|---|
| **Goal** | Analyze the application specification and planning documents to create a comprehensive application plan documented as a GitHub Issue, with milestones, labels, and project linking |
| **Key Acceptance Criteria** | (1) Application template thoroughly analyzed; (2) Plan documented in GitHub Issue using `application-plan.md` template; (3) Milestones created and linked; (4) Issue added to GitHub Project; (5) Labels applied (`planning`, `documentation`); (6) Tech stack documented in `plan_docs/tech-stack.md`; (7) Architecture documented in `plan_docs/architecture.md`; (8) No implementation code written — planning only |
| **Project-Specific Notes** | The primary app spec is `OS-APOW Implementation Specification v1.md` (not `ai-new-app-template.md`). The skeleton code files (`notifier_service.py`, `orchestrator_sentinel.py`) in `plan_docs/` provide implementation context. The architecture guide and development plan are comprehensive and should heavily inform the plan. The 4-phase development roadmap (Phase 0-3) with user stories and acceptance criteria is already defined. The plan issue will be the target for the `orchestration:plan-approved` label after workflow completion. |
| **Prerequisites** | `init-existing-repository` completed; GitHub Project exists; labels imported |
| **Dependencies** | Output from [1]: GitHub Project, labels, working branch |
| **Risks** | (1) The `planning` label may not exist in the imported label set — may need to be created; (2) The `application-plan.md` issue template may reference `.github/ISSUE_TEMPLATE/application-plan.md` which may not exist yet — may need to be created or adapted; (3) The plan docs are highly detailed which may lead to an overly verbose plan issue |
| **Events** | pre-assignment-begin: `gather-context`; on-assignment-failure: `recover-from-error`; post-assignment-complete: `validate-assignment-completion`, `report-progress` |

### Assignment 3: `create-project-structure`

| Field | Details |
|---|---|
| **Goal** | Create the actual project structure and scaffolding: solution files, project directories, Dockerfiles, docker-compose, CI/CD workflows, documentation, and development environment configuration |
| **Key Acceptance Criteria** | (1) Solution/project structure created per plan's tech stack; (2) All required project files and directories established; (3) Initial configuration files created (Docker, pyproject.toml, etc.); (4) Basic CI/CD pipeline structure established; (5) Documentation structure created (README, docs/); (6) Dev environment validated; (7) Initial commit with scaffolding; (8) Repository summary document created (`.ai-repository-summary.md`); (9) All GitHub Actions workflows SHA-pinned; (10) Stakeholder approval obtained |
| **Project-Specific Notes** | **Python/uv tech stack** — use `pyproject.toml`, `uv.lock`, `src/` layout. The Implementation Spec defines a specific project structure to follow. Existing `scripts/` directory (shell bridge, auth helpers) must be preserved. The skeleton Python files in `plan_docs/` should be moved into the proper `src/` structure. The `local_ai_instruction_modules/` directory already exists and must be preserved. Docker healthchecks must avoid `curl` (use Python stdlib instead). Existing GitHub Actions workflows must be preserved and enhanced, not overwritten. |
| **Prerequisites** | `create-app-plan` completed; application plan issue exists; tech stack documented |
| **Dependencies** | Output from [1]: working branch, PR; Output from [2]: application plan, milestones, tech-stack.md, architecture.md |
| **Risks** | (1) Existing template files (workflows, scripts, devcontainer) could be accidentally overwritten; (2) The `scripts/devcontainer-opencode.sh` referenced in plan docs may not exist in this template — needs to be created or adapted; (3) Docker Compose and Dockerfile must align with the existing DevContainer infrastructure; (4) Python `pyproject.toml` must properly reference the `src/` layout for editable installs; (5) SHA-pinning all GitHub Actions requires looking up current release SHAs |
| **Events** | post-assignment-complete: `validate-assignment-completion`, `report-progress` |

### Assignment 4: `create-agents-md-file`

| Field | Details |
|---|---|
| **Goal** | Create a comprehensive `AGENTS.md` file at the repository root providing AI coding agents with the context and instructions they need to work on the project |
| **Key Acceptance Criteria** | (1) `AGENTS.md` exists at repository root; (2) Contains project overview, setup/build/test commands, code style, project structure, testing instructions, PR/commit guidelines; (3) All commands validated by running them; (4) Written in standard Markdown with agent-focused language; (5) Committed and pushed; (6) Stakeholder approval obtained |
| **Project-Specific Notes** | The existing `AGENTS.md` from the template repo must be **updated** to reflect the actual OS-APOW project context (it currently describes the template repo's orchestration system). Build commands will be Python/uv-based (`uv run`, `uv pip install`). Test commands will be `pytest` or `bash test/...` shell scripts. The file should reference the `scripts/` directory utilities and the `.ai-repository-summary.md` created in [3]. The existing `AGENTS.md` already has a rich structure with repository map and instructions — the update should preserve the template orchestration context while adding OS-APOW project specifics. |
| **Prerequisites** | `create-project-structure` completed; project builds successfully; test infrastructure in place |
| **Dependencies** | Output from [3]: project structure, build system, README.md, `.ai-repository-summary.md` |
| **Risks** | (1) Build/test commands may not all pass yet if the project scaffolding is incomplete; (2) The existing `AGENTS.md` content must be carefully preserved for the template infrastructure while adding project-specific content; (3) Risk of information duplication between `AGENTS.md`, `README.md`, and `.ai-repository-summary.md` |
| **Events** | post-assignment-complete: `validate-assignment-completion`, `report-progress` |

### Assignment 5: `debrief-and-document`

| Field | Details |
|---|---|
| **Goal** | Perform a comprehensive debriefing that captures key learnings, insights, deviations, and areas for improvement from the entire project-setup workflow execution |
| **Key Acceptance Criteria** | (1) Detailed debrief report created following the 12-section template; (2) All deviations from assignments documented; (3) Execution trace saved as `debrief-and-document/trace.md`; (4) Report reviewed and approved; (5) Committed and pushed; (6) Action items flagged for plan adjustment |
| **Project-Specific Notes** | This is the first workflow execution for this project, so the debrief is especially valuable for capturing what worked and what didn't during the self-bootstrapping process. The execution trace should capture all commands run, files created/modified, and interactions. The "Plan Adjustment Mandate" is critical — any findings that impact Phase 1+ development must be flagged as ACTION ITEMS. |
| **Prerequisites** | All prior assignments completed |
| **Dependencies** | Outputs from [1]-[4]: full execution history, all created files, validation reports |
| **Risks** | (1) Execution trace may be incomplete if not captured incrementally; (2) Debrief may become excessively long given the multi-assignment scope; (3) Risk of missing deviations if assignment completion wasn't tracked carefully |
| **Events** | post-assignment-complete: `validate-assignment-completion`, `report-progress` |

### Assignment 6: `pr-approval-and-merge`

| Field | Details |
|---|---|
| **Goal** | Complete the full PR approval and merge process for the setup PR: resolve all review comments, obtain approval, merge, and perform post-merge hygiene |
| **Key Acceptance Criteria** | (1) All CI/CD status checks pass (CI remediation loop up to 3 attempts); (2) Code review delegated to `code-reviewer` subagent; (3) All review comments resolved with GraphQL verification; (4) Stakeholder approval obtained; (5) PR merged; (6) Source branch deleted; (7) Related issues closed; (8) Run report updated |
| **Project-Specific Notes** | This is an automated setup PR — self-approval by the orchestrator is acceptable per the dynamic workflow specification. The `$pr_num` comes from the PR opened in [1] `init-existing-repository`. The CI remediation loop (Phase 0.5) must still be executed. On successful merge, the setup branch is deleted and related setup issues are closed. The `ai-pr-comment-protocol.md` and `pr-review-comments.md` must be followed. `scripts/query.ps1` can be used for managing PR review threads. |
| **Prerequisites** | All prior assignments completed and validated; PR has commits from all assignments |
| **Dependencies** | Output from [1]: `$pr_num`; Outputs from [2]-[5]: all commits on the PR branch |
| **Risks** | (1) CI may fail due to the new project structure (lint, build, or test failures); (2) Branch protection rules may require additional checks; (3) Merge conflicts if `main` has been updated during the workflow; (4) Review comments from automated reviewers (Copilot, CodeQL) may require code changes; (5) The `code-reviewer` subagent may not be available or may require orchestrator delegation |
| **Events** | post-assignment-complete: `validate-assignment-completion`, `report-progress` |

### Post-Script Event: `orchestration:plan-approved`

After all assignments complete successfully, the `orchestration:plan-approved` label is applied to the application plan issue (created in [2]) to signal readiness for epic creation in the next orchestration phase.

---

## 4. Sequencing Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PRE-SCRIPT-BEGIN                                                            │
│  ┌──────────────────────┐                                                  │
│  │ create-workflow-plan  │ ◄── (this document)                             │
│  └──────────┬───────────┘                                                  │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [1] init-existing-repository                                                │
│  ┌─────────────────────────────────────────┐                                │
│  │ Create branch → Import ruleset →        │                                │
│  │ Create Project → Import labels →        │                                │
│  │ Rename files → Open PR                  │                                │
│  └──────────┬──────────────────────────────┘                                │
│             │ POST: validate-assignment-completion, report-progress         │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │ $pr_num
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [2] create-app-plan  (planning only — NO code)                              │
│  PRE: gather-context                                                        │
│  ┌─────────────────────────────────────────┐                                │
│  │ Analyze spec docs → Create plan issue → │                                │
│  │ Create milestones → Link to Project →   │                                │
│  │ Write tech-stack.md & architecture.md   │                                │
│  └──────────┬──────────────────────────────┘                                │
│             │ POST: validate-assignment-completion, report-progress         │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │ plan_issue_number
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [3] create-project-structure                                                │
│  ┌─────────────────────────────────────────┐                                │
│  │ Create src/ layout → pyproject.toml →   │                                │
│  │ Dockerfile + docker-compose →           │                                │
│  │ CI/CD workflows → README + docs →       │                                │
│  │ .ai-repository-summary.md → Validate    │                                │
│  └──────────┬──────────────────────────────┘                                │
│             │ POST: validate-assignment-completion, report-progress         │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [4] create-agents-md-file                                                   │
│  ┌─────────────────────────────────────────┐                                │
│  │ Gather context → Validate commands →    │                                │
│  │ Draft AGENTS.md → Cross-reference →     │                                │
│  │ Final validation → Commit               │                                │
│  └──────────┬──────────────────────────────┘                                │
│             │ POST: validate-assignment-completion, report-progress         │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [5] debrief-and-document                                                    │
│  ┌─────────────────────────────────────────┐                                │
│  │ Write 12-section debrief →              │                                │
│  │ Capture execution trace → Review →      │                                │
│  │ Flag ACTION ITEMS → Commit              │                                │
│  └──────────┬──────────────────────────────┘                                │
│             │ POST: validate-assignment-completion, report-progress         │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ [6] pr-approval-and-merge  ($pr_num from [1])                              │
│  ┌─────────────────────────────────────────┐                                │
│  │ CI verification loop → Code review →    │                                │
│  │ Resolve comments → Approval →           │                                │
│  │ Merge → Delete branch → Close issues    │                                │
│  └──────────┬──────────────────────────────┘                                │
│             │ POST: validate-assignment-completion, report-progress         │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ POST-SCRIPT-COMPLETE                                                        │
│  ┌─────────────────────────────────────────┐                                │
│  │ Apply orchestration:plan-approved       │                                │
│  │ label to plan issue from [2]            │                                │
│  └─────────────────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Open Questions

### Q1: Branch Protection Ruleset File Name
The assignment `init-existing-repository` expects the ruleset at `.github/protected-branches_ruleset.json`, but the actual file is `.github/protected branches - main - ruleset.json` (with spaces and different naming). The executing agent must locate the correct file and adapt the import command accordingly.

### Q2: Missing Labels for Planning Workflow
The imported label set (`.github/.labels.json`) does not include `planning`, `documentation`, or `orchestration:plan-approved` labels required by assignments [2] and the post-script-complete event. These labels will need to be created during execution, either by the agent or by updating the labels JSON.

### Q3: `ai-new-app-template.md` Not Present
The `create-app-plan` assignment references `plan_docs/ai-new-app-template.md` as the primary app template, but this file does not exist. The effective application specification is `OS-APOW Implementation Specification v1.md`. The executing agent should treat this as the primary spec document.

### Q4: Issue Template Availability
The `create-app-plan` assignment references `.github/ISSUE_TEMPLATE/application-plan.md` as the plan issue template. This file may not exist in the template repo. The executing agent should either create it or adapt the plan from Appendix A in the assignment.

### Q5: Token Scopes for GitHub Project Creation
The `init-existing-repository` assignment requires `project` and `read:project` OAuth scopes to create a GitHub Project. It is unclear whether the available `GITHUB_TOKEN` (or `GH_ORCHESTRATION_AGENT_TOKEN`) has these scopes. If Project creation fails, the agent should report the error and proceed with manual instructions.

### Q6: `devcontainer-opencode.sh` Script
The OS-APOW plan docs heavily reference `scripts/devcontainer-opencode.sh` as the shell bridge, but the template repo uses `scripts/run-devcontainer-orchestrator.sh` and `scripts/start-opencode-server.sh` instead. The `create-project-structure` assignment should align the actual script names with what the plan docs reference.

### Q7: Skeleton Python Files Disposition
The `notifier_service.py` and `orchestrator_sentinel.py` files currently reside in `plan_docs/`. During `create-project-structure`, these should be moved to the proper `src/` directory structure, but this must be done carefully to not break the plan_docs references.

---

## Resolution Trace

All remote assignment and workflow files were successfully read:

| # | Resource | URL | Status |
|---|---|---|---|
| 1 | Dynamic Workflow: project-setup | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/dynamic-workflows/project-setup.md` | ✅ Read |
| 2 | Assignment: init-existing-repository | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/init-existing-repository.md` | ✅ Read |
| 3 | Assignment: create-app-plan | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/create-app-plan.md` | ✅ Read |
| 4 | Assignment: create-project-structure | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/create-project-structure.md` | ✅ Read |
| 5 | Assignment: create-agents-md-file | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/create-agents-md-file.md` | ✅ Read |
| 6 | Assignment: debrief-and-document | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/debrief-and-document.md` | ✅ Read |
| 7 | Assignment: pr-approval-and-merge | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/pr-approval-and-merge.md` | ✅ Read |
| 8 | Assignment: validate-assignment-completion | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/validate-assignment-completion.md` | ✅ Read |
| 9 | Assignment: report-progress | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/report-progress.md` | ✅ Read |
| 10 | Assignment: create-workflow-plan | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/create-workflow-plan.md` | ✅ Read |
| 11 | Assignment: gather-context | `https://raw.githubusercontent.com/nam20485/agent-instructions/main/ai_instruction_modules/ai-workflow-assignments/gather-context.md` | ✅ Read |

All local plan_docs files were successfully read:

| # | File | Status |
|---|---|---|
| 1 | `plan_docs/OS-APOW Architecture Guide v3.md` | ✅ Read |
| 2 | `plan_docs/OS-APOW Development Plan v4.md` | ✅ Read |
| 3 | `plan_docs/OS-APOW Implementation Specification v1.md` | ✅ Read |
| 4 | `plan_docs/interactive-report.html` | ✅ Read |
| 5 | `plan_docs/notifier_service.py` | ✅ Read |
| 6 | `plan_docs/orchestrator_sentinel.py` | ✅ Read |
