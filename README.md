# Local Machine AI Setup

Portable Codex and OpenCode configuration for a cost-aware engineering workflow.

## Model routing

* **Orchestrator — Terra medium:** routine coordination, integration, and final responses.
* **Worker — Luna high:** small, bounded implementation with settled acceptance criteria.
* **Tester — Luna high:** independent verification and regression evidence.
* **Planner — Sol medium:** non-trivial, ambiguous, cross-component, or high-risk plans.
* **Reviewer — Terra high:** independent correctness, security, and regression review.

The orchestrator retains product and architecture decisions, sensitive work, releases, integration,
and the final response. Delegation is selective so routine tasks do not duplicate context or usage.

## Files

* `AGENTS.md` — global operating policy.
* `agents/` — worker, tester, planner, and reviewer role definitions.
* `config.example.toml` — portable configuration fragment.
* `opencode/AGENTS.md` — global OpenCode configuration-sync policy.
* `scripts/sync-local-ai-setup.sh` — allowlisted local-to-repository synchronization.
* `skills/` — reviewed, user-authored skills grouped by their source scope.
* `opencode/skill/` and `.codex/skills/` — tool-specific mirrors of the same skills.

## Portable skills

`skills/` intentionally contains only custom skills from this machine. It excludes
bundled and plugin-provided skills, credentials, memories, screen recordings,
caches, logs, and other machine-generated state.

The source scope is preserved so identically named skills can coexist:

* `skills/global/` — skills sourced from `~/.codex/skills`.
* `skills/veritaxiq/` — repository-local VeritaxIQ skills.
* `skills/productivity/` and `skills/engineering/` — general workflow skills, including
  `new-session` (one branch + git worktree per session).

See [`skills/MANIFEST.md`](skills/MANIFEST.md) for the inventory and installation
guidance. Review every skill before installing it; some are intentionally specific
to a local Ledger/VeritaxIQ deployment.

## Install

Review the files before installing. Preserve any existing local settings that are not represented here.

```bash
mkdir -p ~/.codex/agents
cp AGENTS.md ~/.codex/AGENTS.md
cp agents/worker.toml agents/tester.toml agents/planner.toml agents/reviewer.toml ~/.codex/agents/
cp opencode/AGENTS.md ~/.config/opencode/AGENTS.md
```

Merge the desired values from `config.example.toml` into `~/.codex/config.toml`; do not overwrite an existing configuration wholesale.

## Synchronize local configuration

Run the allowlisted sync after changing Codex or OpenCode configuration:

```bash
./scripts/sync-local-ai-setup.sh
```

The script copies only the global instruction files, the four custom Codex roles, the portable Codex
model-routing fragment, and the reviewed OpenCode JSON configuration. It validates required fields
and JSON and stops if the OpenCode file contains credential-like keys or values. Review the resulting
diff before committing.

## Excluded on purpose

Credentials, authentication files, memories, thread history, browser state, caches, logs, local paths, plugin installations, MCP environment values, and machine-generated state are not stored in this repository.
