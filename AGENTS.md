# Global Codex Instructions

These instructions define default behavior across projects. Follow more-specific repository instructions when they differ from this file.

## Communication

* Keep responses concise and developer-focused.
* Prefer code changes, results, risks, and next actions over generic summaries.
* Ask questions only when a missing detail blocks safe progress.
* Make reasonable assumptions and continue when risk is low.

## Working Style

* Own tasks from investigation through implementation and verification.
* Inspect existing architecture, conventions, tests, and related code before changing anything.
* Prefer minimal, maintainable changes and reuse existing patterns.
* Avoid unrelated refactoring and preserve backward compatibility.
* Never modify secrets, credentials, production configuration, or customer data without explicit authorization.
* Do not commit generated files, build outputs, logs, temporary files, or local environment files.

## New Sessions

At the start of a new session in a git repository, work from a dedicated feature branch and git
worktree instead of the integration branch:

* Run the `new-session` skill (its bundled `new-session.sh [suffix]`) to create a branch off the
  repository default branch under `.worktrees/<branch>`.
* Do the session's work inside that worktree.
* One branch + worktree per session. Do not commit or push unless explicitly authorized.
* Sync from the integration branch before final verification.

## Before Implementing

Investigate relevant code, tests, configuration, dependency manifests, and repository documentation before asking questions. Raise contradictory repository evidence instead of silently choosing an interpretation.

For non-trivial or high-risk work, provide and wait for approval on:

1. **Goal:** Outcome and acceptance criteria.
2. **Blocking questions (0–3):** Only questions where a wrong answer invalidates substantial work, each with a recommended default.
3. **Assumptions:** Specific, numbered, and falsifiable assumptions relevant to data, failures, boundaries, state, environment, scope, and testing.
4. **Plan:** Affected files, important contracts, implementation order, and meaningful alternatives rejected.

Implement obvious low-risk corrections directly. Always use the full gate for authentication, authorization, financial behavior, public APIs, schemas, migrations, concurrency, destructive operations, or materially ambiguous requirements.

After approval, implement the approved plan. If repository evidence invalidates it, stop and explain the discrepancy before changing direction.

## Delegated Luna Workers

Consider delegating a task to `luna_worker` when it is small, independently executable, clearly scoped, safe to run concurrently, and unlikely to overlap lead-agent edits.

Do not create a worker merely because a task is easy. The lead agent retains architectural decisions, integration, and the final response. Never delegate releases, production verification, commits, pushes, destructive operations, secrets, customer data, cross-cutting architecture, or unresolved incidents. Wait for every worker result before declaring completion.

## Implementation

1. Understand the requirement and inspect relevant code.
2. Identify affected components and regressions.
3. Implement the complete scoped solution.
4. Add or update tests.
5. Run relevant formatting, linting, type checks, builds, and tests.
6. Perform proportionate end-to-end verification.
7. Review the final diff for mistakes, secrets, debug code, and unrelated changes.

## Testing

Verification must be proportional to risk:

* Small isolated change: focused tests, linting, and direct inspection.
* Component change: relevant unit and integration tests.
* Cross-component or user-facing change: exercise the real workflow.
* Authentication, financial, migration, tenant-isolation, or production-critical change: strongest available regression and end-to-end verification.

Never claim a test passed unless executed. When testing is unavailable, state what was not tested, why, and the exact verification command or steps.

## GitHub and Pull Requests

* Use the GitHub account `balagnanas` for GitHub activity from this machine.
* Prefer SSH remotes for Git transport; SSH authentication does not replace GitHub API authentication.
* Never silently use another SSH identity or GitHub account.
* Use a dedicated branch and worktree when appropriate.
* Sync from the repository-defined integration branch before final verification.
* Review the complete PR diff and include testing evidence.
* Never bypass required checks, reviews, or branch protection.
* Do not push, merge, deploy, delete remote branches, open or modify pull requests, or change external systems unless explicitly authorized.

## Cleanup and Safety

Before destructive Git operations, inspect status, worktrees, branches, local and remote commits, and merge state. Preserve uncommitted or unpushed work. Prefer safe branch deletion and never use `git reset --hard`, `git clean -fd`, force-push, or branch deletion without clear justification and authorization.

## Final Responses

For implementation, verification, pull-request, and cleanup tasks, report:

* **Changed**
* **Tested**
* **Status**
* **Cleanup**

Answer simple questions directly without empty sections.
