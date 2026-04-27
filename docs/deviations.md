# Project Setup Deviations

This document records deviations from the standard `init-existing-repository` assignment during the `project-setup` dynamic workflow.

---

## Deviation 001: Missing Branch Protection Ruleset

- **Step**: Step 2 — Import Branch Protection Ruleset
- **Date**: 2026-04-27
- **Status**: SKIPPED
- **Reason**: The template file `.github/protected-branches_ruleset.json` does not exist in this repository. The file was expected to contain a GitHub ruleset JSON definition that could be imported via the GitHub API to configure branch protection rules.
- **Impact**: No automated branch protection rules will be applied. Branch protection must be configured manually through the GitHub repository settings if required.
- **Action Required**: Consider creating the ruleset file in a future iteration or configuring branch protection manually via GitHub Settings → Rules → New branch ruleset.

---

## Deviation 002: GitHub Project Creation — Initially Blocked, Resolved via PAT

- **Step**: Step 3 — Create GitHub Project for Issue Tracking
- **Date**: 2026-04-27
- **Status**: RESOLVED
- **Initial Issue**: The `GITHUB_TOKEN` used by `github-actions[bot]` does not have the `project` permission scope required to create organization projects (`createProjectV2`).
- **Resolution**: Used `GH_ORCHESTRATION_AGENT_TOKEN` PAT (with `project` scope) to create the project. Project ID 80 (`workflow-orchestration-queue-romeo91`) was created, linked to the repository, and configured with columns: Not Started, In Progress, In Review, Done.
