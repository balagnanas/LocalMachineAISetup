---
name: update-copilot-opencode-models
description: Refresh the Copilot App's model catalog in ~/.copilot/data.db with the latest OpenCode Go, OpenCode Zen, and OpenRouter models. Use when the user wants to sync/add the newest models into the Copilot App, pull live OpenCode/OpenRouter model lists, or update the model_providers/provider_models tables.
---

Sync the newest OpenCode Go / OpenCode Zen / OpenRouter models into the **Copilot App** SQLite database (`~/.copilot/data.db`).

## What it does
1. Fetches live catalogs (the app caches models in memory, so this is the only way to refresh without manual UI entry):
   - **OpenCode Go** `https://opencode.ai/zen/go/v1/models` — *all* live models
   - **OpenCode Zen** `https://opencode.ai/zen/v1/models` — *free* models only (`-free` suffix, plus `big-pickle`)
   - **OpenRouter** `https://openrouter.ai/api/v1/models` — *free* models only (prompt + completion price = 0)
2. Backs up `~/.copilot/data.db` to `data.db.bak-<timestamp>`.
3. Upserts rows into `provider_models` (matched by normalized provider name). Providers are **not** recreated; existing models not in the catalog are **kept** (this is an upsert, never a wipe).
4. Reports inserted/updated counts per provider.

## OpenCode context-window caveat
OpenCode's API does **not** publish `context`/`max_prompt_tokens`. For Zen/Go, that value is proxied from the **live OpenRouter** `context_length` whenever a matching model exists (`context_source: openrouter-proxy`). `max_output_tokens` is left `NULL` (OpenRouter doesn't reliably expose it). Treat proxied values as approximate.

## How to run
The skill ships a self-contained script. Run it (no args) to apply, or `--dry-run` to preview:

```sh
python3 ~/.copilot/skills/update-copilot-opencode-models/scripts/update_copilot_models.py --dry-run
python3 ~/.copilot/skills/update-copilot-opencode-models/scripts/update_copilot_models.py
```

## After running
Tell the user to **quit and reopen the Copilot App** — it caches the model list, so new/updated models won't appear in *Settings → Models* until restarted.

## Safety
- Always makes a timestamped backup before writing. To roll back: `cp ~/.copilot/data.db.bak-<ts> ~/.copilot/data.db`.
- Does not touch `model_providers` settings (auth/keys), so API keys stay as the user configured them.
- Network only; no external system changes.

## Notes
- To also write a portable JSON export (e.g. for OneDrive), the script returns the in-memory `providers` structure — extend `main()` to dump it.
- If you want *all* Zen models (not just free), change `scope: "free"` to `"all"` in the script's `PROVIDERS` map.
