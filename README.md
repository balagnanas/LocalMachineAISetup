# Local Machine AI Setup

Portable Codex configuration for a cost-aware engineering workflow.

## Model routing

* **Luna (`gpt-5.6-luna`, max):** small, bounded implementation and verification tasks with clear acceptance criteria.
* **Terra (`gpt-5.6-terra`):** repository exploration, research, medium-complexity debugging, and supporting reviews.
* **Sol (`gpt-5.6-sol`):** architecture, ambiguous multi-step work, high-risk changes, incident analysis, and final review.

The lead agent retains planning, integration, security-sensitive work, releases, and final review. Luna workers never commit, push, deploy, or make architectural decisions independently.

## Files

* `AGENTS.md` — global operating policy.
* `agents/luna-worker.toml` — low-cost bounded implementation worker.
* `config.example.toml` — portable configuration fragment.
* `skills/` — reviewed, user-authored skills grouped by their source scope.

## Portable skills

`skills/` intentionally contains only custom skills from this machine. It excludes
bundled and plugin-provided skills, credentials, memories, screen recordings,
caches, logs, and other machine-generated state.

The source scope is preserved so identically named skills can coexist:

* `skills/global/` — skills sourced from `~/.codex/skills`.
* `skills/veritaxiq/` — repository-local VeritaxIQ skills.

See [`skills/MANIFEST.md`](skills/MANIFEST.md) for the inventory and installation
guidance. Review every skill before installing it; some are intentionally specific
to a local Ledger/VeritaxIQ deployment.

## Install

Review the files before installing. Preserve any existing local settings that are not represented here.

```bash
mkdir -p ~/.codex/agents
cp AGENTS.md ~/.codex/AGENTS.md
cp agents/luna-worker.toml ~/.codex/agents/luna-worker.toml
```

Merge the desired values from `config.example.toml` into `~/.codex/config.toml`; do not overwrite an existing configuration wholesale.

## Excluded on purpose

Credentials, authentication files, memories, thread history, browser state, caches, logs, local paths, plugin installations, MCP environment values, and machine-generated state are not stored in this repository.
