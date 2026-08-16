---
name: new-session
description: Start a fresh agent session by creating a new feature branch and a dedicated git worktree (one branch + worktree per session, based off the repository's default branch). Use at the start of a new session, or whenever the user asks for a new session, branch, or worktree.
argument-hint: "Optional short feature-name suffix for the branch"
---

Start each session from a dedicated branch + git worktree instead of working directly on the
integration branch. This keeps parallel sessions isolated while all changes still flow through
the repository's single integration branch.

1. Run the bundled script (it fetches, branches off the base branch, and adds a worktree):
   ```bash
   scripts/new-session.sh [feature-suffix]
   ```
   The script lives in this skill's directory; copy or call it from there if it is not already
   on `PATH`. Omit `[feature-suffix]` to auto-generate a `<adjective>-<noun>` name.

2. Switch into the newly created worktree:
   ```bash
   cd .worktrees/<branch>
   ```

3. Do the session's work inside that directory.

## Conventions

- One branch + worktree per session.
- Base branch: the repository's default branch (auto-detected; override with `SESSION_BASE`).
- Worktree root: `<repo>/.worktrees/<branch>` (override with `SESSION_ROOT`).
- Branch name: `<SESSION_PREFIX>-<adjective>-<noun>` — the prefix defaults to the sanitized
  git `user.name` (override with `SESSION_PREFIX`).
- Do not commit or push unless explicitly asked.
- Sync from the integration branch before final verification (see the repository's sync
  workflow, e.g. `scripts/sync-with-dev.sh` in VeritaxIQ).
