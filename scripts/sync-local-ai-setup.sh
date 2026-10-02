#!/usr/bin/env bash
set -euo pipefail

# Default direction: machine -> repository (portable salvage).
# With --install: repository -> machine (bootstrap a new machine from this repo).
# Use --force with --install to overwrite differing local files (backups are kept).

mode="sync"
force=0
for arg in "$@"; do
  case "$arg" in
    --install) mode="install" ;;
    --force) force=1 ;;
    --sync-skills) mode="skills" ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_root="${CODEX_HOME:-$HOME/.codex}"
opencode_root="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
copilot_mcp_config="$HOME/.copilot/mcp-config.json"
vscode_user_settings="$HOME/Library/Application Support/Code/User/settings.json"

if [[ "$mode" == "skills" ]]; then
  [[ "$#" -eq 1 ]] || { echo "Usage: $0 --sync-skills" >&2; exit 2; }
  # Reviewed personal skills only; payroll tenant/customer details stay local.
  portable_skills=(
    add-model-9router-copilot bank-statement-local-regression changelog-generate
    chronicle ci-pipeline client-portal-local-deployment code-review codebase-design
    dependency-audit diagnosing-bugs domain-modeling explain
    flowstudio-power-automate-build flowstudio-power-automate-debug
    flowstudio-power-automate-governance flowstudio-power-automate-mcp
    flowstudio-power-automate-monitoring git-release grill-me grill-with-docs grilling
    handoff implement improve-codebase-architecture incident-rca
    invoice-extraction-live-regression list-models local-document-diagnostic new-session
    orchestrate-cheap prototype research resolving-merge-conflicts setup-matt-pocock-skills
    tdd teach test-patterns to-questionnaire to-spec to-tickets triage update-9router-catalog
    update-copilot-opencode-models veritaxiq-dev-deploy veritaxiq-prod-deploy
    veritaxiq-project-safety veritaxiq-release-promotion wait-what wayfinder
    web-design-guidelines wizard writing-for-agents writing-great-skills
  )
  python3 - "$codex_root/skills" "${portable_skills[@]}" <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
sensitive = re.compile(
    r"sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"Bearer [A-Za-z0-9._-]{20,}"
)
for name in sys.argv[2:]:
    skill = root / name
    if skill.is_symlink() or not (skill / 'SKILL.md').is_file():
        raise SystemExit(f"Missing or linked skill: {name}")
    for path in skill.rglob('*'):
        if path.is_symlink():
            raise SystemExit(f"Linked skill file: {path.relative_to(root)}")
        if not path.is_file() or '__pycache__' in path.parts or '.bak.' in path.name:
            continue
        if path.suffix in {'.pyc', '.jsonl'} or path.name in {'observed-learnings.md', 'release-evidence.md'}:
            continue
        if sensitive.search(path.read_text()):
            raise SystemExit(f"Credential-like value: {path.relative_to(root)}")
print(f"Validated {len(sys.argv) - 2} portable skills.")
PY
  for skill in "${portable_skills[@]}"; do
    canonical="$repo_root/skills/global/$skill"
    for scope in engineering productivity; do
      if [[ -d "$repo_root/skills/$scope/$skill" ]]; then
        canonical="$repo_root/skills/$scope/$skill"
        break
      fi
    done
    for target in "$canonical" "$repo_root/.codex/skills/$skill" "$repo_root/copilot/skills/$skill"; do
      mkdir -p "$target"
      rsync -a --exclude='__pycache__/' --exclude='*.pyc' --exclude='*.bak.*' \
        --exclude='*.jsonl' --exclude='observed-learnings.md' --exclude='release-evidence.md' \
        "$codex_root/skills/$skill/" "$target/"
    done
  done
  echo "Synchronized ${#portable_skills[@]} skills into canonical, Codex, and Copilot mirrors."
  exit 0
fi

if [[ "$mode" == "install" ]]; then
  install_file() {
    local src="$1" dst="$2"
    if [[ -e "$dst" ]]; then
      if cmp -s "$src" "$dst"; then
        echo "  up-to-date: $dst"
        return 0
      fi
      if (( force )); then
        cp "$dst" "$dst.bak.$(date +%Y%m%d%H%M%S)"
        echo "  updated (backup kept): $dst"
      else
        echo "  SKIPPED, differs locally (rerun with --force to overwrite): $dst" >&2
        return 0
      fi
    else
      echo "  installed: $dst"
    fi
    mkdir -p "$(dirname "$dst")"
    install -m 0644 "$src" "$dst"
  }

  merge_json() {
    local src="$1" dst="$2"
    python3 - "$src" "$dst" <<'PY'
import json
import pathlib
import sys

source = json.loads(pathlib.Path(sys.argv[1]).read_text())
target_path = pathlib.Path(sys.argv[2])
indent = int(sys.argv[3]) if len(sys.argv) > 3 else 2
target = json.loads(target_path.read_text()) if target_path.exists() else {}
added = []

def merge(add, into, prefix=""):
    for key, value in add.items():
        if key not in into:
            into[key] = value
            added.append(prefix + key)
        elif isinstance(value, dict) and isinstance(into[key], dict):
            merge(value, into[key], prefix + key + ".")

merge(source, target)
if added:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(target, indent=indent) + "\n")
for key in added:
    print(f"  merged: {key} -> {sys.argv[2]}")
PY
  }

  echo "Installing Codex configuration..."
  install_file "$repo_root/AGENTS.md" "$codex_root/AGENTS.md"
  for role in worker tester planner reviewer; do
    [[ -f "$repo_root/agents/$role.toml" ]] && install_file "$repo_root/agents/$role.toml" "$codex_root/agents/$role.toml"
  done
  for toml in "$repo_root"/agents/router/*.toml; do
    [[ -e "$toml" ]] || break
    install_file "$toml" "$codex_root/agents/$(basename "$toml")"
  done
  for skill in "$repo_root"/skills/global/*/ "$repo_root"/skills/productivity/*/ "$repo_root"/skills/engineering/*/; do
    [[ -d "$skill" ]] || continue
    install_file "$skill/SKILL.md" "$codex_root/skills/$(basename "$skill")/SKILL.md"
  done

  echo "Installing OpenCode configuration..."
  install_file "$repo_root/opencode/AGENTS.md" "$opencode_root/AGENTS.md"
  install_file "$repo_root/opencode/opencode.json" "$opencode_root/opencode.json"
  for skill in "$repo_root"/opencode/skill/*/; do
    [[ -d "$skill" ]] || continue
    install_file "$skill/SKILL.md" "$opencode_root/skill/$(basename "$skill")/SKILL.md"
  done

  echo "Merging Copilot CLI MCP servers..."
  merge_json "$repo_root/copilot/mcp-config.example.json" "$copilot_mcp_config"

  echo "Merging VS Code settings..."
  merge_json "$repo_root/vscode/settings.example.json" "$vscode_user_settings" 4

  echo "Bootstrap install from $repo_root complete."
  exit 0
fi

required_files=(
  "$codex_root/AGENTS.md"
  "$codex_root/config.toml"
  "$codex_root/agents/worker.toml"
  "$codex_root/agents/tester.toml"
  "$codex_root/agents/planner.toml"
  "$codex_root/agents/reviewer.toml"
  "$opencode_root/AGENTS.md"
  "$opencode_root/opencode.json"
)

for required_file in "${required_files[@]}"; do
  if [[ ! -f "$required_file" ]]; then
    echo "Missing required configuration: $required_file" >&2
    exit 1
  fi
done

python3 - "$codex_root/config.toml" "$repo_root/config.example.toml" <<'PY'
import pathlib
import re
import sys

source_path = pathlib.Path(sys.argv[1])
target_path = pathlib.Path(sys.argv[2])
source = source_path.read_text()

def setting(name, section=None):
    current_section = None
    for raw_line in source.splitlines():
        line = raw_line.strip()
        section_match = re.fullmatch(r"\[([^]]+)\]", line)
        if section_match:
            current_section = section_match.group(1)
            continue
        if current_section != section:
            continue
        match = re.fullmatch(rf"{re.escape(name)}\s*=\s*(.+)", line)
        if not match:
            continue
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            return value[1:-1]
        if re.fullmatch(r"[0-9]+", value):
            return int(value)
        raise SystemExit(f"Unsupported value for {name}: {value}")
    return None

required = {
    "model": setting("model"),
    "model_reasoning_effort": setting("model_reasoning_effort"),
    "personality": setting("personality"),
    "max_concurrent_threads_per_session": setting("max_concurrent_threads_per_session", "agents"),
    "default_subagent_model": setting("default_subagent_model", "agents"),
    "default_subagent_reasoning_effort": setting("default_subagent_reasoning_effort", "agents"),
}
missing = [key for key, value in required.items() if value is None]
if missing:
    raise SystemExit(f"Missing portable Codex settings: {', '.join(missing)}")

target_path.write_text(
    "# Generated by scripts/sync-local-ai-setup.sh.\n"
    "# Merge these portable settings into ~/.codex/config.toml. Keep credentials, local paths,\n"
    "# MCP environment values, and machine-specific application settings only in local config.\n\n"
    f'model = "{required["model"]}"\n'
    f'model_reasoning_effort = "{required["model_reasoning_effort"]}"\n'
    f'personality = "{required["personality"]}"\n'
    'approval_policy = "on-request"\n'
    'sandbox_mode = "workspace-write"\n\n'
    "[agents]\n"
    f'max_concurrent_threads_per_session = {required["max_concurrent_threads_per_session"]}\n'
    f'default_subagent_model = "{required["default_subagent_model"]}"\n'
    f'default_subagent_reasoning_effort = "{required["default_subagent_reasoning_effort"]}"\n'
)
PY

python3 - "$opencode_root/opencode.json" <<'PY'
import json
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
config = json.loads(path.read_text())
sensitive = re.compile(r"(?:api[_-]?key|authorization|credential|password|secret|token)", re.I)
sensitive_value = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer [A-Za-z0-9._-]{20,})"
)

def walk(value, parts=()):
    if isinstance(value, dict):
        for key, child in value.items():
            next_parts = (*parts, str(key))
            if sensitive.search(str(key)):
                raise SystemExit(f"Credential-like OpenCode key found: {'.'.join(next_parts)}")
            walk(child, next_parts)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, (*parts, str(index)))
    elif isinstance(value, str) and sensitive_value.search(value):
        raise SystemExit(f"Credential-like OpenCode value found: {'.'.join(parts)}")

walk(config)
PY

install -m 0644 "$codex_root/AGENTS.md" "$repo_root/AGENTS.md"
for role in worker tester planner reviewer; do
  install -m 0644 "$codex_root/agents/$role.toml" "$repo_root/agents/$role.toml"
done
install -m 0644 "$opencode_root/AGENTS.md" "$repo_root/opencode/AGENTS.md"
install -m 0644 "$opencode_root/opencode.json" "$repo_root/opencode/opencode.json"

mkdir -p "$repo_root/agents/router"
shopt -s nullglob
router_tomls=("$codex_root/agents/router-model-"*.toml)
shopt -u nullglob
if (( ${#router_tomls[@]} )); then
  grep -riE "api[_-]?key|secret|token|password|authorization" "${router_tomls[@]}" >/dev/null && {
    echo "Credential-like string found in Codex Router agent definitions" >&2
    exit 1
  } || true
  for toml in "${router_tomls[@]}"; do
    install -m 0644 "$toml" "$repo_root/agents/router/$(basename "$toml")"
  done
  echo "Mirrored ${#router_tomls[@]} Codex Router agent definitions."
fi

python3 - "$copilot_mcp_config" "$repo_root/copilot/mcp-config.example.json" <<'PY'
import json
import pathlib
import re
import sys

source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
config = json.loads(source.read_text())
for server in config.get("mcpServers", {}).values():
    command = server.get("command")
    if isinstance(command, str):
        server["command"] = pathlib.PurePath(command).name
text = json.dumps(config, indent=2) + "\n"
if re.search(r"(?:api[_-]?key|authorization|credential|password|secret|token)", text, re.I):
    raise SystemExit("Credential-like string found in Copilot MCP configuration")
target.write_text(text)
PY

python3 - "$vscode_user_settings" "$repo_root/vscode/settings.example.json" <<'PY'
import json
import pathlib
import re
import sys

source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
config = json.loads(source.read_text())
text = json.dumps(config, indent=4) + "\n"
if re.search(r"(?:api[_-]?key|authorization|credential|password|secret|token)", text, re.I):
    raise SystemExit("Credential-like string found in VS Code settings")
target.write_text(text)
PY

third_party_skills=(
  changelog-generate ci-pipeline code-review codebase-design dependency-audit
  diagnosing-bugs domain-modeling git-release grill-with-docs implement
  improve-codebase-architecture prototype research resolving-merge-conflicts
  setup-matt-pocock-skills tdd test-patterns to-spec to-tickets triage wayfinder wizard
)
unmirrored="$(comm -23 \
  <(ls "$opencode_root/skill" | sort) \
  <(ls "$repo_root/opencode/skill" | sort))"
drift=""
while IFS= read -r skill; do
  [[ -z "$skill" ]] && continue
  is_third_party=0
  for known in "${third_party_skills[@]}"; do
    [[ "$skill" == "$known" ]] && { is_third_party=1; break; }
  done
  if (( ! is_third_party )); then
    drift+="$skill "
  fi
done <<< "$unmirrored"
if [[ -n "$drift" ]]; then
  echo "Unmirrored OpenCode skills are not third-party references: $drift" >&2
  exit 1
else
  echo "OpenCode skills drift check passed."
fi

python3 - "$repo_root" <<'PY'
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
portable_config = (root / "config.example.toml").read_text()
for required_key in (
    "model",
    "model_reasoning_effort",
    "personality",
    "max_concurrent_threads_per_session",
    "default_subagent_model",
    "default_subagent_reasoning_effort",
):
    if not re.search(rf"(?m)^{re.escape(required_key)}\s*=", portable_config):
        raise SystemExit(f"Missing portable setting: {required_key}")
for path in sorted((root / "agents").glob("*.toml")):
    agent = path.read_text()
    for required_key in ("name", "description", "model", "model_reasoning_effort", "developer_instructions"):
        if not re.search(rf"(?m)^{re.escape(required_key)}\s*=", agent):
            raise SystemExit(f"Missing {required_key} in {path}")
    if agent.count('"""') % 2:
        raise SystemExit(f"Unbalanced multiline string in {path}")
router_agents = sorted((root / "agents" / "router").glob("*.toml")) if (root / "agents" / "router").is_dir() else []
for path in router_agents:
    agent = path.read_text()
    for required_key in ("name", "description", "model_provider", "model", "developer_instructions"):
        if not re.search(rf"(?m)^{re.escape(required_key)}\s*=", agent):
            raise SystemExit(f"Missing {required_key} in {path}")
    if re.search(r"(?mi)api[_-]?key|secret|token|password|authorization", agent):
        raise SystemExit(f"Credential-like string in {path}")
    if agent.count('"""') % 2:
        raise SystemExit(f"Unbalanced multiline string in {path}")
json.loads((root / "opencode/opencode.json").read_text())
json.loads((root / "copilot/mcp-config.example.json").read_text())
json.loads((root / "vscode/settings.example.json").read_text())
print(
    f"Validated portable Codex and OpenCode configuration "
    f"({len(router_agents)} Codex Router agents, Copilot MCP, VS Code settings)."
)
PY

echo "Synchronized portable configuration into $repo_root"
echo "Review with: git -C $repo_root status --short && git -C $repo_root diff"
