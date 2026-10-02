---
name: update-9router-catalog
description: Refresh 9router's model catalog (~/.9router/model-catalog.json and model-catalog-raw.json) from models.dev, the same source 9router's built-in sync uses. Use when the user wants to refresh/update 9router's model catalog, pull the latest models.dev data into 9router, or fix a stale 9router catalog without waiting for the automatic 24h sync or entering the admin password.
---

Refresh **9router's** model catalog files from `https://models.dev/api.json` — the exact source and transform 9router's own sync job uses (verified against `chunks/7716.js` in the installed bundle).

## Why
9router auto-syncs 60s after boot, then every 24h (30min retry on failure). The manual API (`POST /api/models/catalog-sync`) requires the admin password. This skill writes the catalog files directly — 9router re-stats file mtime on every access, so changes take effect **immediately, no restart**.

## What it does
1. Fetches `https://models.dev/api.json`.
2. Backs up both catalog files (`*.bak-<timestamp>`).
3. Rebuilds `model-catalog-raw.json` — per provider, per model: `{i: [non-text input modalities], c: context limit, o: output limit, r: reasoning}` (exact server transform).
4. Rebuilds `model-catalog.json` — `{v:2, etag, syncedAt, models, providers}`:
   - `models`: `"<provider>:<model>"` keys with modality flags (`vision`, `pdf`, `audioInput`, `videoInput`), including alias groups (glm→zai, claude→anthropic, gemini→google, kimi→moonshotai, qwen→alibaba, ...).
   - `providers`: **carried forward** from the existing file for providers still present in the new data (these are server-computed limit overrides; regenerating them needs 9router's internal registry).
5. Writes both files atomically (tmp + rename). If the transformed data is unchanged, exits without writing (unless `--force`).

## How to run
```sh
python3 ~/.copilot/skills/update-9router-catalog/scripts/sync_9router_catalog.py --dry-run
python3 ~/.copilot/skills/update-9router-catalog/scripts/sync_9router_catalog.py           # apply
python3 ~/.copilot/skills/update-9router-catalog/scripts/sync_9router_catalog.py --force   # rewrite even if unchanged
```

## Notes
- Works while 9router is running (WAL-safe, atomic writes).
- If 9router's own sync later runs, it overwrites these files with identical logic — no conflict.
- To roll back: `cp ~/.9router/model-catalog.json.bak-<ts> ~/.9router/model-catalog.json` (same for `-raw`).
- Adding a *specific model* so it's routable/listed in 9router + Copilot is a different task — use the `add-model-9router-copilot` skill.
