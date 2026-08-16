# Portable skill manifest

This inventory preserves the custom skills installed on the source machine as of
2026-08-02. It intentionally excludes OpenAI-bundled and third-party plugin skills.

| Source scope | Skill | Notes |
| --- | --- | --- |
| Global | `bank-statement-local-regression` | Local Ledger regression; requires its separately authorized sample corpus. |
| Global | `chronicle` | Screen/history-aware workflow; available only where Chronicle is enabled. |
| Global | `incident-rca` | Evidence-backed incident reporting. |
| Global | `invoice-extraction-live-regression` | Requires explicit approval before sending PDFs to configured services. |
| Global | `veritaxiq-release-promotion` | Guarded production-promotion workflow. |
| VeritaxIQ | `ledger-local-dev-deployment` | Localhost Ledger deployment workflow. |
| VeritaxIQ | `veritaxiq-release-promotion` | Repository-local release workflow variant. |
| Productivity | `new-session` | One branch + git worktree per session; portable session-start helper (`new-session.sh`). |

## Installation

Copy the intended skill directory into the matching Codex skill root. Do not
blindly overwrite a local skill with the same name; compare the `SKILL.md` files
first. The two `veritaxiq-release-promotion` variants are intentionally retained
under separate source scopes because their contents differ.

```bash
# Example: install one global skill
mkdir -p ~/.codex/skills
cp -R skills/global/incident-rca ~/.codex/skills/

# Example: install a repository-local skill from the VeritaxIQ checkout
cp -R skills/veritaxiq/ledger-local-dev-deployment /path/to/VeritaxIQ/.codex/skills/
```

Do not copy bundled or plugin-cache skills from another machine. Install those via
their owning runtime or plugin instead.
