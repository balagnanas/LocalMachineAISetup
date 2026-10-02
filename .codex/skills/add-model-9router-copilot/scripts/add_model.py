#!/usr/bin/env python3
"""Add a model to 9router (pin + provider connection) and to the Copilot App's
BYOK 9router provider in ~/.copilot/data.db."""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import time
import urllib.request
import uuid

ROUTER_DB = os.path.expanduser("~/.9router/db/data.sqlite")
COPILOT_DB = os.path.expanduser("~/.copilot/data.db")
DEFAULT_COPILOT_PROVIDER = "4e5a4e55-0c50-4791-ab9b-9df1df31ce82"  # 9router BYOK

# 9router alias -> (registry provider id, default connection display name)
ALIAS_TO_PROVIDER = {
    "oc": ("opencode", "OpenCode Free"),
    "ocg": ("opencode-go", "OpenCode Go"),
    "cl": ("cline", "Cline"),
    "cx": ("codex", "Codex"),
    "glm": ("glm", "Z.ai GLM"),
    "gemini": ("gemini", "Gemini"),
    "groq": ("groq", "Groq"),
    "cerebras": ("cerebras", "Cerebras"),
    "mistral": ("mistral", "Mistral"),
    "nvidia": ("nvidia", "NVIDIA"),
    "ollama-local": ("ollama", "Ollama"),
}

CONNECTION_DATA = json.dumps({
    "testStatus": "active",
    "providerSpecificData": {
        "connectionProxyEnabled": False,
        "connectionProxyUrl": "",
        "connectionNoProxy": "",
    },
})


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + ".%03dZ" % (int(time.time() * 1000) % 1000)


def backup(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    bak = f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(path, bak)
    return bak


def router_models(base: str) -> list[str]:
    with urllib.request.urlopen(f"{base}/v1/models", timeout=15) as r:
        return [m["id"] for m in json.load(r)["data"]]


def first_api_key(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT key FROM apiKeys LIMIT 1").fetchone()
    return row[0] if row else None


def chat_test(base: str, api_key: str, model: str) -> int:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply with OK"}],
        "max_tokens": 16,
    }).encode()
    req = urllib.request.Request(
        f"{base}/v1/chat/completions", data=body, method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.load(r)
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        print(f"route test: HTTP 200, reply: {text!r}")
        return 0
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        print(f"route test: HTTP {e.code} (warning — 9router routed it; upstream said: {detail})")
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--alias", required=True, help="9router provider alias, e.g. oc")
    ap.add_argument("--model", required=True, help="model id at the provider, e.g. jev-1.13-free")
    ap.add_argument("--display", help="display name (default: alias/model)")
    ap.add_argument("--context", type=int, help="max prompt tokens for the Copilot row")
    ap.add_argument("--max-output", type=int, help="max output tokens for the Copilot row")
    ap.add_argument("--provider-id", help="registry provider id when alias is unknown")
    ap.add_argument("--copilot-provider-id", default=DEFAULT_COPILOT_PROVIDER)
    ap.add_argument("--port", type=int, default=20128)
    ap.add_argument("--api-key", help="9router inference key (for --test)")
    ap.add_argument("--test", action="store_true", help="send a tiny chat completion after adding")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    base = f"http://127.0.0.1:{args.port}"
    provider = args.provider_id or ALIAS_TO_PROVIDER.get(args.alias, (None, None))[0]
    conn_name = ALIAS_TO_PROVIDER.get(args.alias, (None, args.alias))[1]
    if not provider:
        sys.exit(f"unknown alias {args.alias!r}: pass --provider-id <registry id>")
    wire = f"{args.alias}/{args.model}"
    display = args.display or wire

    try:
        listed = router_models(base)
    except Exception as e:
        sys.exit(f"9router not reachable at {base}: {e}")

    rconn = sqlite3.connect(ROUTER_DB)
    has_connection = rconn.execute(
        "SELECT 1 FROM providerConnections WHERE provider=?", (provider,)
    ).fetchone() is not None
    kv_key = f"{args.alias}|{args.model}|llm"
    has_pin = rconn.execute(
        "SELECT 1 FROM kv WHERE scope='customModels' AND key=?", (kv_key,)
    ).fetchone() is not None
    pin_val = json.dumps({"providerAlias": args.alias, "id": args.model,
                          "type": "llm", "name": display})

    cconn = sqlite3.connect(COPILOT_DB)
    has_copilot_row = cconn.execute(
        "SELECT 1 FROM provider_models WHERE provider_id=? AND model_id=?",
        (args.copilot_provider_id, wire),
    ).fetchone() is not None

    print(f"plan: alias={args.alias} provider={provider} model={args.model}")
    print(f"  9router connection for {provider}: {'exists' if has_connection else 'MISSING -> will insert'}")
    print(f"  9router pin {kv_key}: {'exists' if has_pin else 'MISSING -> will upsert'}")
    print(f"  currently listed at 9router: {wire in listed}")
    print(f"  copilot row {wire}: {'exists' if has_copilot_row else 'MISSING -> will insert'}")

    if args.dry_run:
        return 0

    if not has_connection or not has_pin:
        bak = backup(ROUTER_DB)
        if bak:
            print(f"backup: {bak}")
    if not has_connection:
        rconn.execute(
            "INSERT INTO providerConnections(id, provider, authType, name, email, priority,"
            " isActive, data, createdAt, updatedAt) VALUES (?,?,?,?,NULL,1,1,?,?,?)",
            (str(uuid.uuid4()), provider, "none", conn_name, CONNECTION_DATA, now_iso(), now_iso()),
        )
        print(f"9router: inserted connection for {provider} ({conn_name})")
    if not has_pin:
        rconn.execute(
            "INSERT OR REPLACE INTO kv(scope, key, value) VALUES ('customModels', ?, ?)",
            (kv_key, pin_val),
        )
        print(f"9router: upserted pin {kv_key}")
    rconn.commit()

    listed = router_models(base)
    if wire in listed:
        print(f"9router: {wire} is listed in /v1/models")
    else:
        print(f"9router: WARNING — {wire} not in /v1/models (check the 9router UI for this provider)")

    if not has_copilot_row:
        bak = backup(COPILOT_DB)
        if bak:
            print(f"backup: {bak}")
        cconn.execute(
            "INSERT INTO provider_models(id, provider_id, model_id, display_name,"
            " max_prompt_tokens, max_output_tokens, created_at, updated_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), args.copilot_provider_id, wire, display,
             args.context, args.max_output, now_iso(), now_iso()),
        )
        cconn.commit()
        print(f"copilot: inserted provider_models row {wire}")
    cconn.close()

    if args.test:
        key = args.api_key
        if not key:
            key = first_api_key(sqlite3.connect(f"file:{ROUTER_DB}?mode=ro", uri=True))
        if not key:
            print("route test: skipped (no api key found; pass --api-key)")
        else:
            chat_test(base, key, wire)

    print("done. Restart the Copilot App to see the new model (it caches the list).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
