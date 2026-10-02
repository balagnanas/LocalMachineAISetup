---
name: update-copilot-opencode-models
description: Refresh the Copilot App's model catalog in ~/.copilot/data.db with the latest OpenCode Go, OpenCode Zen, and OpenRouter models (free and paid). Use when the user wants to sync/add the newest models into the Copilot App, pull live OpenCode/OpenRouter model lists, include paid models, or update the model_providers/provider_models tables.
---

Sync the newest OpenCode Go / OpenCode Zen / OpenRouter models into the **Copilot App** SQLite database (`~/.copilot/data.db`).

## What it does
1. Fetches live catalogs (the app caches models in memory, so this is the only way to refresh without manual UI entry):
   - **OpenCode Go** `https://opencode.ai/zen/go/v1/models` — *all* live models
   - **OpenCode Zen** `https://opencode.ai/zen/v1/models` — **free only** (`-free` / `big-pickle`); paid models are excluded
   - **OpenRouter** `https://openrouter.ai/api/v1/models` — **free only** (zero prompt+completion pricing); paid models are excluded
   - **Z.ai** — **all** GLM models. Z.ai's `/models` endpoint requires auth: if `Z_AI_API_KEY` is set in the environment the script fetches live, otherwise it uses the static catalog in `PROVIDERS["Z AI"]["static_models"]` (update that dict as Z.ai ships new models).
2. Backs up `~/.copilot/data.db` to `data.db.bak-<timestamp>`.
3. Upserts rows into `provider_models` (matched by normalized provider name). Providers are **not** recreated. Models no longer in the live catalog are **removed**; new or changed models are upserted.
4. Ensures required provider headers: OpenCode Go **requires** an `x-opencode-session` header on every request (requests without it error from 2026-09-06). The script sets a stable UUID once in the provider's `settings_json.headersJson` and preserves it on later runs — do not clear this header.
5. Reports inserted/updated/removed counts per provider.

## OpenCode context-window caveat
OpenCode's API does **not** publish `context`/`max_prompt_tokens`. For Zen/Go, that value is proxied from the **live OpenRouter** `context_length` whenever a matching model exists (`context_source: openrouter-proxy`). `max_output_tokens` is left `NULL` (OpenRouter doesn't reliably expose it). Treat proxied values as approximate.

**Fallback for OpenCode-exclusive models:** Some free models (e.g. `big-pickle`, `nemotron-3-ultra-free`) exist only in OpenCode Zen and have no matching entry in OpenRouter, so their context length cannot be proxied. These models receive a **fallback context of 1,050,000 tokens** (GPT-5.6 Luna's context window) with `context_source: fallback-luna`. This is a safe conservative estimate — the actual value may be different but the Copilot App will function correctly with it.

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
- Only writes `model_providers.settings_json` to add **required headers** (currently `x-opencode-session` on Opencode Go, only when missing). API keys and other settings are never touched.
- Network only; no external system changes.

## Notes
- To also write a portable JSON export (e.g. for OneDrive), the script returns the in-memory `providers` structure — extend `main()` to dump it.
- **Scope configuration (intentional, do not revert):** `PROVIDERS` sets `scope` per provider — `"all"` for **Opencode Go** and **Z AI**, `"free"` for **OpenCode Zen** and **Open Router**. Paid Zen/OpenRouter models are deliberately excluded.
- **Z.ai**: DB provider name is `"Z AI"`. Static catalog lives in `PROVIDERS["Z AI"]["static_models"]` as `{model_id: context_length}` (sources: docs.z.ai). Optionally export `Z_AI_API_KEY` to refresh the list live from `https://api.z.ai/api/coding/paas/v4/models`.
