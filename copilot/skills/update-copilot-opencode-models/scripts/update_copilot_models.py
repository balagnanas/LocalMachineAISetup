#!/usr/bin/env python3
"""Sync the latest OpenCode Go / OpenCode Zen / OpenRouter / Z.ai models into ~/.copilot/data.db.

Fetches live catalogs from:
  - https://opencode.ai/zen/go/v1/models     (OpenCode Go  -- ALL models)
  - https://opencode.ai/zen/v1/models        (OpenCode Zen -- FREE models only)
  - https://openrouter.ai/api/v1/models      (OpenRouter   -- FREE models only)
  - https://api.z.ai/api/coding/paas/v4/models (Z.ai -- ALL models; live if Z_AI_API_KEY
                                               is set, else static catalog in PROVIDERS)

Then syncs the model rows into the Copilot App SQLite DB (provider_models table).
Providers themselves are matched by name and left untouched. Models no longer in the
catalog are deleted; new or changed models are upserted. A timestamped backup of data.db is made.

OpenCode does NOT publish context windows via its API, so max_prompt_tokens for Zen/Go is
proxied from the live OpenRouter context_length when a matching model exists.
"""
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime

DATA_DB = os.path.expanduser("~/.copilot/data.db")
BIG_PICKLE = "big-pickle"  # labeled "FREE" in the app but has no -free suffix
FALLBACK_CONTEXT = 1050000  # GPT-5.6 Luna context length (1.05M tokens)

# name (as shown in Copilot App) -> (baseUrl, include_what)
PROVIDERS = {
    "Opencode Go": {
        "baseUrl": "https://opencode.ai/zen/go/v1",
        "type": "custom",
        "scope": "all",  # all live models
        # OpenCode Go rejects requests missing x-opencode-session (required as
        # of 2026-09-06). None = keep any existing value; a stable uuid is
        # generated once if the header is absent.
        "required_headers": {"x-opencode-session": None},
    },
    "OpenCode Zen": {
        "baseUrl": "https://opencode.ai/zen/v1",
        "type": "custom",
        "scope": "free",  # free models only
    },
    "Open Router": {
        "baseUrl": "https://openrouter.ai/api/v1",
        "type": "openai-compatible",
        "scope": "free",  # free models only
    },
    # DB provider is named "Z AI"; normalized lookup is "zai".
    # Z.ai's /models endpoint requires auth: set Z_AI_API_KEY to fetch live,
    # otherwise the static catalog below is used. Update it as Z.ai ships models.
    "Z AI": {
        "baseUrl": "https://api.z.ai/api/coding/paas/v4",
        "type": "openai-compatible",
        "scope": "all",
        "static_models": {  # model_id -> context_length (from docs.z.ai)
            "glm-5.3": 1048576,
            "glm-5.3-flash": 1048576,
            "glm-5.2": 1048576,
            "glm-5.1": 204800,
            "glm-5": 131072,
            "glm-4.7": 204800,
            "glm-4.6": 204800,
            "glm-4.5-air": 131072,
        },
    },
}


def fetch_json(url, timeout=60, headers=None):
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-A", "copilot-model-sync/1.0", url]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def is_free_openrouter(m):
    p = m.get("pricing", {})
    try:
        return float(p.get("prompt", "0") or 0) == 0.0 and float(p.get("completion", "0") or 0) == 0.0
    except (TypeError, ValueError):
        return False


def is_free_zen(model_id):
    return model_id.endswith("-free") or model_id == BIG_PICKLE


def apply_scope(ids, scope, kind):
    if scope == "all":
        return list(ids)
    if kind == "zen":
        return [i for i in ids if is_free_zen(i)]
    raise ValueError(f"unsupported free-scope kind: {kind}")


def pretty(s):
    out = []
    for seg in s.replace("-", " ").split(" "):
        if seg and seg[0].isalpha():
            seg = seg[0].upper() + seg[1:]
        out.append(seg)
    return " ".join(out)


def build_models():
    go_ids = [m["id"] for m in fetch_json(PROVIDERS["Opencode Go"]["baseUrl"] + "/models")["data"]]
    zen_ids = [m["id"] for m in fetch_json(PROVIDERS["OpenCode Zen"]["baseUrl"] + "/models")["data"]]
    or_all = fetch_json(PROVIDERS["Open Router"]["baseUrl"] + "/models")["data"]

    or_by_tail = {}
    for m in or_all:
        or_by_tail.setdefault(m["id"].split("/")[-1], []).append(m)

    def ctx_for(opencode_id):
        """Return (context_length, source) tuple for an OpenCode model."""
        cands = []
        for cand in [opencode_id, opencode_id.replace("-free", ""), opencode_id.replace("-free", ":free")]:
            cands += or_by_tail.get(cand, [])
        cands = [c for c in cands if c.get("context_length")]
        if cands:
            return cands[0].get("context_length"), "openrouter-proxy"
        # Fallback: use Luna's context length for OpenCode-exclusive models
        return FALLBACK_CONTEXT, "fallback-luna"

    def detail(ids, label, proxy=True):
        rows = []
        for mid in ids:
            if proxy:
                ctx, src = ctx_for(mid)
            else:
                ctx, src = None, None
            rows.append({
                "model_id": mid,
                "wire_model": mid,
                "display_name": f"{pretty(mid)} ({label})",
                "max_prompt_tokens": ctx,
                "max_output_tokens": None,
                "wire_api_override": None,
                "supported_reasoning_efforts": None,
                "context_source": src,
            })
        return rows

    zen_ids = apply_scope(zen_ids, PROVIDERS["OpenCode Zen"]["scope"], "zen")
    if PROVIDERS["Open Router"]["scope"] == "free":
        or_models = [m for m in or_all if is_free_openrouter(m)]
    else:
        or_models = list(or_all)

    return [
        {"name": "Opencode Go", "baseUrl": PROVIDERS["Opencode Go"]["baseUrl"],
         "required_headers": PROVIDERS["Opencode Go"].get("required_headers"),
         "models": detail(go_ids, "OpenCode Go")},
        {"name": "OpenCode Zen", "baseUrl": PROVIDERS["OpenCode Zen"]["baseUrl"],
         "models": detail(zen_ids, "OpenCode Zen")},
        {"name": "Open Router", "baseUrl": PROVIDERS["Open Router"]["baseUrl"],
         "models": [{
            "model_id": m["id"], "wire_model": m["id"],
            "display_name": f"{re.sub(r'\\s*\\(free\\)\\s*$', '', m.get('name') or m['id'])} (OpenRouter)",
            "max_prompt_tokens": m.get("context_length"), "max_output_tokens": None,
            "wire_api_override": None, "supported_reasoning_efforts": None,
            "context_source": "openrouter-live",
        } for m in sorted(or_models, key=lambda x: x["id"])]},
        zai_models(),
    ]


def zai_models():
    """Z.ai models: live list when Z_AI_API_KEY is set, else the static catalog."""
    api_key = os.environ.get("Z_AI_API_KEY")
    base = PROVIDERS["Z AI"]["baseUrl"]
    ctx_map = dict(PROVIDERS["Z AI"]["static_models"])
    source = "static-docs"
    if api_key:
        try:
            data = fetch_json(base + "/models", headers={"Authorization": f"Bearer {api_key}"})
            live = {m["id"]: m.get("context_length") for m in data["data"]}
            if live:
                ctx_map.update({k: v or ctx_map.get(k) for k, v in live.items()})
                ctx_map = {k: v for k, v in ctx_map.items() if k in live or k in PROVIDERS["Z AI"]["static_models"]}
                source = "zai-live"
        except Exception as e:
            print(f"Z.ai live fetch failed ({e}); using static catalog")

    return {"name": "Z AI", "baseUrl": base, "models": [{
        "model_id": mid, "wire_model": mid,
        "display_name": f"{pretty(mid)} (Z.ai)",
        "max_prompt_tokens": ctx, "max_output_tokens": None,
        "wire_api_override": None, "supported_reasoning_efforts": None,
        "context_source": source,
    } for mid, ctx in sorted(ctx_map.items(), reverse=True)]}


def upsert(providers):
    if not os.path.exists(DATA_DB):
        raise SystemExit(f"data.db not found at {DATA_DB}")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"{DATA_DB}.bak-{ts}"
    shutil.copy2(DATA_DB, backup)
    print(f"Backup: {backup}")

    conn = sqlite3.connect(DATA_DB)
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        db_prov = {name.lower().replace(" ", ""): pid
                   for pid, name in conn.execute("SELECT id, name FROM model_providers")}

        for prov in providers:
            norm = prov["name"].lower().replace(" ", "")
            pid = db_prov.get(norm)
            if not pid:
                print(f"!! Provider '{prov['name']}' not found in data.db -- SKIPPED")
                continue
            
            # Get current models in DB for this provider
            existing = {r[0] for r in conn.execute(
                "SELECT model_id FROM provider_models WHERE provider_id=?", (pid,))}
            # Get new models from catalog
            new_models = {m["model_id"] for m in prov["models"]}
            
            # Delete models no longer in catalog
            to_delete = existing - new_models
            if to_delete:
                placeholders = ','.join('?' for _ in to_delete)
                conn.execute(
                    f"DELETE FROM provider_models WHERE provider_id=? AND model_id IN ({placeholders})",
                    (pid,) + tuple(to_delete)
                )
                del_count = conn.total_changes
                print(f"{prov['name']}: -{len(to_delete)} removed")
            
            # Upsert new/updated models
            ins = upd = 0
            for m in prov["models"]:
                mid = m["model_id"]
                if mid in existing:
                    upd += 1
                else:
                    ins += 1
                conn.execute(
                    """INSERT OR REPLACE INTO provider_models
                       (id, provider_id, model_id, wire_model, display_name,
                        max_prompt_tokens, max_output_tokens, wire_api_override,
                        supported_reasoning_efforts)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (str(uuid.uuid4()), pid, mid, m["wire_model"], m["display_name"],
                     m.get("max_prompt_tokens"), m.get("max_output_tokens"),
                     m.get("wire_api_override"), m.get("supported_reasoning_efforts")))
            # Ensure required provider headers (e.g. x-opencode-session for
            # OpenCode Go). Existing values are preserved; missing ones get a
            # stable uuid so the id never churns between runs.
            if prov.get("required_headers"):
                row = conn.execute(
                    "SELECT settings_json FROM model_providers WHERE id=?", (pid,)).fetchone()
                if row:
                    settings = json.loads(row[0])
                    headers = json.loads(settings.get("headersJson") or "{}")
                    added = [h for h in prov["required_headers"] if not headers.get(h)]
                    if added:
                        for h in added:
                            headers[h] = prov["required_headers"][h] or str(uuid.uuid4())
                        settings["headersJson"] = json.dumps(headers)
                        conn.execute(
                            "UPDATE model_providers SET settings_json=?,"
                            " updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
                            (json.dumps(settings), pid))
                        print(f"{prov['name']}: + required header(s): {', '.join(added)}")
            conn.execute("UPDATE model_providers SET updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?", (pid,))
            conn.commit()
            total = conn.execute("SELECT COUNT(*) FROM provider_models WHERE provider_id=?", (pid,)).fetchone()[0]
            print(f"{prov['name']}: +{ins} new, ~{upd} updated, -{len(to_delete)} removed, {total} total in DB")
    finally:
        conn.close()


def main():
    providers = build_models()
    print(f"Fetched {sum(len(p['models']) for p in providers)} models across "
          f"{len(providers)} providers (Go=all, Zen+OpenRouter=free, Z.ai=all).")
    dry = "--dry-run" in sys.argv
    if dry:
        print(json.dumps(providers, indent=2)[:2000] + "\n... (dry-run, not writing to DB)")
        return
    upsert(providers)
    print("\nDone. RESTART the Copilot App to load the new model list (it caches in memory).")


if __name__ == "__main__":
    main()
