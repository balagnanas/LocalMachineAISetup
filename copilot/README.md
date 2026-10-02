# GitHub Copilot CLI profile

This is a public, portable baseline for GitHub Copilot CLI. It contains only generic role agents and
their shared workflow; it does not include user identity, installed plugins, MCP configuration,
permissions, trusted folders, sessions, authentication, or runtime state.

`skills/` contains the reviewed portable mirror of the shared Codex/Copilot
personal skills. Copy selected directories into `~/.copilot/skills/`, preserving
their scripts and references. Compare existing versions before overwriting them.
Customer-specific payroll instructions and recorded learning logs stay local.

## Install

Review the files first, then copy only the parts you want into your Copilot configuration directory:

```powershell
$source = Resolve-Path .\copilot
$destination = Join-Path $HOME '.copilot'

Copy-Item "$source\copilot-instructions.md" "$destination\copilot-instructions.md"
Copy-Item "$source\agents\*.agent.md" (Join-Path $destination 'agents')
```

Preserve any existing user-specific settings. Start a new Copilot session after copying the agent
profiles so they are discoverable.

## Included roles

| Agent | Model | Purpose |
| --- | --- | --- |
| Planner | GPT-5.6 Sol | Read-only, decision-ready plans for non-trivial or high-risk work. |
| Worker | GPT-5.6 Luna | Small, well-specified implementation tasks. |
| Tester | GPT-5.6 Luna | Independent acceptance-criteria and regression verification. |
| Reviewer | GPT-5.6 Terra | Read-only review for correctness, security, regressions, and missing verification. |

Run `.\scripts\Test-PublicProfile.ps1` from the repository root before publishing changes.
