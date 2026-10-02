#!/usr/bin/env python3
"""Refresh 9router's model catalog files from models.dev.

Replicates the transform of 9router's built-in sync (chunks/7716.js, function p()):
- model-catalog-raw.json: per provider, per model {i: non-text input modalities, c: ctx, o: out, r: reasoning}
- model-catalog.json: {v:2, etag, syncedAt, models: {"provider:model": flags}, providers}

9router re-stats the files on every access, so no restart is needed.
"""
import argparse
import json
import os
import shutil
import sys
import time
import urllib.request

DATA_DIR = os.environ.get("NINEROUTER_DATA_DIR", os.path.expanduser("~/.9router"))
CATALOG = os.path.join(DATA_DIR, "model-catalog.json")
CATALOG_RAW = os.path.join(DATA_DIR, "model-catalog-raw.json")
MODELS_DEV = "https://models.dev/api.json"

# Alias map j from chunks/7716.js (registry provider id -> canonical models.dev id)
ALIAS_MAP = {
    "glm": "zai", "glm-cn": "zhipuai", "claude": "anthropic", "gemini": "google",
    "kimi": "moonshotai", "kimi-cn": "moonshotai-cn", "qwen": "alibaba",
    "qwen-cn": "alibaba-cn", "zhipu": "zhipuai", "hunyuan": "tencent",
    "doubao": "volcengine", "cloudflare-ai": "cloudflare-workers-ai",
}
# canonical -> [registry provider ids]
CANON_TO_REGISTRY = {}
for _reg, _canon in ALIAS_MAP.items():
    CANON_TO_REGISTRY.setdefault(_canon, []).append(_reg)

# input modality -> catalog flag (map i from chunks/7716.js)
MODALITY_FLAGS = {"image": "vision", "pdf": "pdf", "audio": "audioInput", "video": "videoInput"}


def norm_model_id(mid: str) -> str:
    # m(a): strip provider prefix, lowercase, drop ":variant"
    s = mid.split("/")[-1] if "/" in mid else mid
    return s.lower().split(":")[0]


def fetch_models_dev() -> tuple[dict, str | None]:
    req = urllib.request.Request(MODELS_DEV, headers={
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) 9router-catalog-sync",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode()), resp.headers.get("etag")


def aliases_for(dev_key: str) -> list[str]:
    canon = ALIAS_MAP.get(dev_key, dev_key)
    return CANON_TO_REGISTRY.get(canon, [])


def build_raw(dev: dict) -> dict:
    raw = {}
    for provider, entry in dev.items():
        models = {}
        for mid, m in (entry.get("models") or {}).items():
            modalities = (m.get("modalities") or {}).get("input") or []
            limit = m.get("limit") or {}
            rec = {
                "i": [x for x in modalities if x != "text"],
                "c": limit.get("context"),
                "o": limit.get("output"),
            }
            if m.get("reasoning"):
                rec["r"] = m.get("reasoning")
            models[norm_model_id(mid)] = rec
        raw[provider] = models
    return raw


def build_models_map(dev: dict) -> dict:
    models = {}
    for dev_key, entry in dev.items():
        grp = aliases_for(dev_key)
        normed = {}
        seen = set()
        for mid, m in (entry.get("models") or {}).items():
            fid = norm_model_id(mid)
            normed[fid] = m  # last wins, like `g[f]=d`
            if fid in seen:
                continue
            seen.add(fid)
            flags = {}
            for a in ((m.get("modalities") or {}).get("input") or []):
                flag = MODALITY_FLAGS.get(a)
                if flag:
                    flags[flag] = True
            if flags:
                for alias in grp:
                    models[f"{alias}:{fid}"] = flags
                if dev_key not in grp:
                    models[f"{dev_key}:{fid}"] = flags
    return models


def load_json(path: str, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def write_atomic(path: str, text: str) -> None:
    tmp = f"{path}.tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w") as f:
        f.write(text)
    os.replace(tmp, path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite even if data unchanged")
    args = ap.parse_args()

    print(f"Fetching {MODELS_DEV} ...")
    dev, etag = fetch_models_dev()
    new_raw = build_raw(dev)
    new_models = build_models_map(dev)

    cur_raw = load_json(CATALOG_RAW, None)
    cur_catalog = load_json(CATALOG, None)
    unchanged = (
        cur_raw == new_raw
        and cur_catalog is not None
        and cur_catalog.get("models") == new_models
    )
    print(f"models.dev: {len(dev)} providers; catalog: {len(new_models)} model keys")
    if unchanged and not args.force:
        print("Unchanged (same content). Use --force to rewrite anyway.")
        return 0

    # providers map = server-computed limit overrides; cannot be regenerated
    # standalone (needs 9router's registry), so carry existing entries forward.
    # ponytail: stale overrides are harmless lookups; drop entries only if a
    # provider disappears from models.dev entirely.
    carried = {}
    for key, val in (cur_catalog or {}).get("providers", {}).items():
        if key in new_raw or key in ALIAS_MAP or key in CANON_TO_REGISTRY:
            carried[key] = val

    now_ms = int(time.time() * 1000)
    catalog_text = json.dumps(
        {"v": 2, "etag": etag, "syncedAt": now_ms, "models": new_models, "providers": carried},
        separators=(",", ":"),
    )
    raw_text = json.dumps(new_raw, separators=(",", ":"))

    if args.dry_run:
        print("[dry-run] would write:")
        print(f"  {CATALOG}     ({len(catalog_text) // 1024} KB)")
        print(f"  {CATALOG_RAW} ({len(raw_text) // 1024} KB)")
        return 0

    stamp = time.strftime("%Y%m%d-%H%M%S")
    for path in (CATALOG, CATALOG_RAW):
        if os.path.exists(path):
            bak = f"{path}.bak-{stamp}"
            shutil.copy2(path, bak)
            print(f"backup: {bak}")

    write_atomic(CATALOG, catalog_text)
    write_atomic(CATALOG_RAW, raw_text)
    print(f"written: {CATALOG} ({len(new_models)} model keys, {len(carried)} provider overrides)")
    print(f"written: {CATALOG_RAW} ({sum(len(v) for v in new_raw.values())} models)")
    print("9router picks this up on next request (no restart needed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
