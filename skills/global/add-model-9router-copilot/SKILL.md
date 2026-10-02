---
name: add-model-9router-copilot
description: Add a specific model under a specific 9router provider alias (e.g. oc, ocg, cl, glm) so 9router lists and routes it, and register the same model in the Copilot App's BYOK 9router provider (~/.copilot/data.db). Use when the user wants to add a new model to 9router and Copilot, expose an upstream model via a 9router alias, or wire a model into Copilot Sessions through the 9router BYOK provider.
---

Add one model to **9router** (custom-model pin + provider connection if missing) and to the **Copilot App** DB under the 9router BYOK provider, end to end.

## What it does
1. Checks 9router is up (`GET /v1/models`, default `http://127.0.0.1:20128`).
2. Backs up `~/.9router/db/data.sqlite` and `~/.copilot/data.db` (`*.bak-<timestamp>`) before any write.
3. **9router** (`~/.9router/db/data.sqlite`, WAL-safe, live — no restart):
   - Inserts a `providerConnections` row for the provider if none exists (authType `none`, isActive 1, minimal data — matches the row created for `opencode`; needed so the provider's models are exposed in `/v1/models`).
   - Upserts a `customModels` kv pin: key `alias|model|llm`, value `{"providerAlias":"<alias>","id":"<model>","type":"llm","name":"<display>"}`.
4. Verifies `<alias>/<model>` now appears in `GET /v1/models`.
5. **Copilot** (`~/.copilot/data.db`): upserts a `provider_models` row for the 9router BYOK provider (`4e5a4e55-0c50-4791-ab9b-9df1df31ce82`) with `model_id = <alias>/<model>`; optional context/output limits via flags.
6. `--test` sends a tiny chat completion to prove routing end to end (upstream 5xx is reported as a warning, not a failure — 9router routing is still verified).

## Known aliases
`oc` (OpenCode Free → provider `opencode`), `ocg` (OpenCode Go → `opencode-go`), `cl` (Cline → `cline`), `cx` (Codex → `codex`), `glm` (Z.ai), `gemini`, `groq`, `cerebras`, `mistral`, `nvidia`, `ollama-local` (→ `ollama`). Unknown aliases need `--provider-id <registry id>` (the `id` field in 9router's `AI_PROVIDERS` registry) and a display name.

## How to run
```sh
# preview (no writes)
python3 ~/.copilot/skills/add-model-9router-copilot/scripts/add_model.py \
  --alias oc --model jev-1.13-free --dry-run

# add + register
python3 ~/.copilot/skills/add-model-9router-copilot/scripts/add_model.py \
  --alias oc --model jev-1.13-free

# with limits and a routing smoke test
python3 ~/.copilot/skills/add-model-9router-copilot/scripts/add_model.py \
  --alias oc --model jev-1.13 --context 64000 --test
```

Options: `--display NAME`, `--context N`, `--max-output N`, `--port N` (9router port, default 20128), `--provider-id ID`, `--copilot-provider-id ID`, `--api-key KEY` (for `--test`; defaults to the single key found in the 9router DB), `--dry-run`, `--test`.

## After running
Tell the user to **quit and reopen the Copilot App** — it caches the model list; the model appears under the *9router* provider.

## Safety
- Timestamped backups before every write; idempotent upserts (safe to re-run).
- To roll back: restore the `.bak-<ts>` files.
- Does not touch API keys, settings, or existing connections/models.
- If the upstream provider rejects the model (e.g. "Model ... is not supported"), the add still succeeds locally — the model simply can't serve traffic until upstream supports it (seen with brand-new OpenCode models).
