#!/usr/bin/env python3
"""Upsert BYOK provider models (Groq, Google AI, Mistral, SambaNova, Cerebras)
into ~/.copilot/data.db, with provider-bracketed display names and
context-window fallbacks (OpenRouter → Luna 1.05M).

Context fallback chain:
  1. Provider's own /models endpoint (SambaNova public, others auth-gated)
  2. OpenRouter's context_length (same or similar model_id)
  3. GPT-5.6 Luna (1,050,000 tokens) -- fallback for unknown models
"""
import json, os, re, shutil, sqlite3, subprocess, uuid
from datetime import datetime

DATA_DB = os.path.expanduser("~/.copilot/data.db")
FALLBACK_CTX = 1_050_000   # Luna context
PROVIDER_IDS = {            # provider_id from data.db
    "Groq":        "01a84ec9-50ac-4b3a-992d-fdda606d7e10",
    "Google AI":   "2f9c6b1e-c67e-486a-b1b7-f256ed8286a1",
    "Mistral":     "c7159c0a-3e0c-4049-802e-1e7d080e3591",
    "SambaNova":   "fb44fb42-2599-4213-80bb-bab71ce4d088",
    "Cerebras":    "6ee28ee3-63c1-4f6e-8155-1242a1c3498c",
}

# ── Groq models (from console.groq.com/docs/models) ──────────────────────────
# (model_id, display_name_base, max_prompt_tokens, max_output_tokens, source)
GROQ_MODELS = [
    # Production Models
    ("llama-3.1-8b-instant",         "Llama 3.1 8B Instant",          131072, 131072, "groq-docs"),
    ("llama-3.3-70b-versatile",       "Llama 3.3 70B Versatile",       131072,  32768, "groq-docs"),
    ("openai/gpt-oss-120b",           "GPT-OSS 120B",                  131072,  65536, "groq-docs"),
    ("openai/gpt-oss-20b",            "GPT-OSS 20B",                   131072,  65536, "groq-docs"),
    ("whisper-large-v3",              "Whisper Large V3",                    None,    None, "groq-docs"),
    ("whisper-large-v3-turbo",        "Whisper Large V3 Turbo",              None,    None, "groq-docs"),
    # Production Systems
    ("groq/compound",                 "Groq Compound",                   131072,   8192, "groq-docs"),
    ("groq/compound-mini",            "Groq Compound Mini",              131072,   8192, "groq-docs"),
    # Preview Models
    ("canopylabs/orpheus-arabic-saudi",   "Canopy Labs Orpheus Arabic Saudi",  4000,  50000, "groq-docs"),
    ("canopylabs/orpheus-v1-english",      "Canopy Labs Orpheus V1 English",    4000,  50000, "groq-docs"),
    ("meta-llama/llama-prompt-guard-2-22m","Llama Prompt Guard 2 22M",            512,    512, "groq-docs"),
    ("meta-llama/llama-prompt-guard-2-86m","Prompt Guard 2 86M",                 512,    512, "groq-docs"),
    ("minimaxai/minimax-m2.7",       "MiniMax M2.7",                   196608, 131072, "groq-docs"),
    ("openai/gpt-oss-safeguard-20b", "Safety GPT-OSS 20B",            131072,  65536, "groq-docs"),
    ("qwen/qwen3.6-27b",             "Qwen3.6 27B",                   131072,  16384, "groq-docs"),
    ("qwen/qwen3.8-27b",             "Qwen3.8 27B",                   131042,  16384, "groq-docs"),
]

# ── Google AI / Gemini models (from ai.google.dev/gemini-api/docs/models) ─────
# Active models only; shut-down/deprecated models excluded.
# Context: Google AI docs + known specs. Unknown → fallback.
GOOGLE_MODELS = [
    # Text/ Multimodal
    ("gemini-3.8-flash",                      "Gemini 3.8 Flash",                      None, None, "google-docs"),
    ("gemini-3.7-flash",                      "Gemini 3.7 Flash",                      None, None, "google-docs"),
    ("gemini-3.6-flash",                      "Gemini 3.6 Flash",                      None, None, "google-docs"),
    ("gemini-3.5-flash",                      "Gemini 3.5 Flash",                      None, None, "google-docs"),
    ("gemini-3.5-flash-lite",                 "Gemini 3.5 Flash-Lite",                 None, None, "google-docs"),
    ("gemini-3.1-flash-lite",                 "Gemini 3.1 Flash-Lite",                 None, None, "google-docs"),
    ("gemini-3.1-pro-preview",                "Gemini 3.1 Pro Preview",                None, None, "google-docs"),
    ("gemini-3-flash-preview",                "Gemini 3 Flash Preview",                None, None, "google-docs"),
    ("gemini-3.5-live-translate-preview",     "Gemini 3.5 Live Translate Preview",     None, None, "google-docs"),
    ("gemini-3.1-flash-live-preview",         "Gemini 3.1 Flash Live Preview",         None, None, "google-docs"),
    ("gemini-3.1-flash-tts-preview",         "Gemini 3.1 Flash TTS Preview",          None, None, "google-docs"),
    ("gemini-omni-flash",                    "Gemini Omni Flash",                     None, None, "google-docs"),
    ("gemini-3.5-transcribe",                "Gemini 3.5 Transcribe",                None, None, "google-docs"),
    ("gemini-2.5-flash",                     "Gemini 2.5 Flash",                   1048576, None, "google-docs"),
    ("gemini-2.5-flash-lite",                "Gemini 2.5 Flash-Lite",             1048576, None, "google-docs"),
    ("gemini-2.5-pro",                       "Gemini 2.5 Pro",                    1048576, None, "google-docs"),
    ("gemini-2.5-flash-native-audio-preview-12-2025", "Gemini 2.5 Flash Live",        None, None, "google-docs"),
    ("gemini-2.5-flash-preview-tts",         "Gemini 2.5 Flash TTS Preview",          None, None, "google-docs"),
    ("gemini-2.5-pro-preview-tts",           "Gemini 2.5 Pro TTS Preview",            None, None, "google-docs"),
    # Image gen / editing
    ("gemini-3.1-flash-image",               "Nano Banana 2",                         None, None, "google-docs"),
    ("gemini-3.1-flash-lite-image",          "Nano Banana 2 Lite",                     None, None, "google-docs"),
    ("gemini-3-pro-image",                   "Nano Banana Pro",                        None, None, "google-docs"),
    ("gemini-2.5-flash-image",               "Nano Banana",                            None, None, "google-docs"),
    # Audio / Live
    ("gemini-3.1-flash-live-preview",        "Gemini 3.1 Flash Live",                None, None, "google-docs"),
    ("gemini-3.1-flash-tts-preview",         "Gemini 3.1 Flash TTS",                 None, None, "google-docs"),
    # Video
    ("veo-3.1-generate-preview",             "Veo 3.1",                              None, None, "google-docs"),
    ("veo-3.1-lite-generate-preview",       "Veo 3.1 Lite",                         None, None, "google-docs"),
    # Music
    ("lyria-3.5",                           "Lyria 3.5",                            None, None, "google-docs"),
    ("lyria-3-clip-preview",                 "Lyria 3 Clip Preview",                  None, None, "google-docs"),
    ("lyria-3-pro-preview",                 "Lyria 3 Pro Preview",                   None, None, "google-docs"),
    ("lyria-realtime-exp",                   "Lyria RealTime",                       None, None, "google-docs"),
    # Agents / Research
    ("gemini-2.5-computer-use-preview-10-2025", "Computer Use",                      None, None, "google-docs"),
    ("deep-research-preview-04-2026",        "Gemini Deep Research",                 None, None, "google-docs"),
    ("deep-research-max-preview-04-2026",    "Gemini Deep Research Max",             None, None, "google-docs"),
    ("antigravity-preview-05-2026",         "Antigravity Agent",                    None, None, "google-docs"),
    # Embeddings
    ("gemini-embedding-2-preview",           "Gemini Embedding 2",                   None, None, "google-docs"),
    ("gemini-embedding-001",                "Gemini Embedding",                      None, None, "google-docs"),
    # Robotics
    ("gemini-robotics-er-2-preview",         "Gemini Robotics ER 2",                  None, None, "google-docs"),
    ("gemini-robotics-er-1.6-preview",       "Gemini Robotics ER 1.6",                None, None, "google-docs"),
]

# ── Mistral models ────────────────────────────────────────────────────────────
# Cross-referenced with OpenRouter context_length.
MISTRAL_MODELS = [
    # Generalist text/multimodal
    ("mistral-medium-3.5-26-04",           "Mistral Medium 3.5",          262144, None, "openrouter"),
    ("mistral-small-4-0-26-03",             "Mistral Small 4",             262144, None, "openrouter"),
    ("mistral-large-3-25-12",               "Mistral Large 3",             262144, None, "openrouter"),
    ("mistral-medium-3-5:batch",            "Mistral Medium 3.5 Batch",     32768, None, "openrouter"),
    ("mistral-small-2603",                  "Mistral Small 2603",         262144, None, "openrouter"),
    # Ministral
    ("ministral-3-14b-25-12",               "Ministral 3 14B",            262144, None, "openrouter"),
    ("ministral-3-8b-25-12",               "Ministral 3 8B",             262144, None, "openrouter"),
    ("ministral-3-3b-25-12",               "Ministral 3 3B",             131072, None, "openrouter"),
    # OCR
    ("ocr-4-1",                             "OCR 4.1",                         None, None, "mistral-docs"),
    ("ocr-25-12",                           "OCR 3",                           None, None, "mistral-docs"),
    # Audio (TTS / transcription)
    ("voxtral-tts-26-03",                   "Voxtral TTS",                      None, None, "mistral-docs"),
    ("voxtral-mini-transcribe-26-02",       "Voxtral Mini Transcribe 2",         None, None, "mistral-docs"),
    ("voxtral-mini-transcribe-realtime-26-02","Voxtral Mini Transcribe Realtime",  None, None, "mistral-docs"),
    ("voxtral-small-25-07",                 "Voxtral Small",                    None, None, "mistral-docs"),
    ("voxtral-small-24b-2507",              "Voxtral Small 24B",             32768, None, "openrouter"),
    # Code
    ("codestral-25-08",                     "Codestral",                    256000, None, "openrouter"),
    # Embeddings
    ("codestral-embed-25-05",               "Codestral Embed",                  None, None, "mistral-docs"),
    ("mistral-embed-23-12",                 "Mistral Embed",                    None, None, "mistral-docs"),
    # Moderation
    ("shieldstral-1-0",                     "Shieldstral 1.0",                  None, None, "mistral-docs"),
    ("mistral-moderation-26-03",            "Mistral Moderation 2",              None, None, "mistral-docs"),
    # Specialist
    ("leanstral-1-5",                      "Leanstral 1.5",                    None, None, "mistral-docs"),
    # Deprecated (still active, add for completeness)
    ("mistral-medium-3-25-08",              "Mistral Medium 3.1",           131072, None, "openrouter"),
    ("mistral-small-3-2-25-06",             "Mistral Small 3.2 24B",       131072, None, "openrouter"),
    ("devstral-2512",                       "Devstral 2",                   262144, None, "openrouter"),
    ("devstral-medium-1-0-25-07",           "Devstral Medium 1.0",         131072, None, "mistral-docs"),
    ("devstral-small-1-1-25-07",            "Devstral Small 1.1",         131072, None, "mistral-docs"),
    ("magistral-medium-1-1-25-07",           "Magistral Medium 1.1",        131072, None, "mistral-docs"),
    ("magistral-small-1-2-25-09",            "Magistral Small 1.2",        131072, None, "mistral-docs"),
    ("mistral-small-3-0-25-01",             "Mistral Small 3.0",          32768, None, "openrouter"),
    ("mistral-large-2407",                  "Mistral Large 2407",          131072, None, "openrouter"),
    ("mistral-nemo",                        "Mistral Nemo",                 131072, None, "openrouter"),
    ("mixtral-8x22b-instruct",              "Mixtral 8x22B Instruct",       65536, None, "openrouter"),
    ("mistral-large",                        "Mistral Large",                128000, None, "openrouter"),
]

# ── SambaNova models (fetched from https://api.sambanova.ai/v1/models) ─────────
SAMBA_MODELS = [
    ("DeepSeek-V3.1",               "DeepSeek-V3.1",               131072,  7168, "sambanova-api"),
    ("DeepSeek-V3.2",               "DeepSeek-V3.2",               32768,   7168, "sambanova-api"),
    ("Meta-Llama-3.3-70B-Instruct", "Meta-Llama 3.3 70B Instruct", 131072,  3072, "sambanova-api"),
    ("MiniMax-M2.6",                "MiniMax M2.6",                196608, 196608, "sambanova-api"),
    ("MiniMax-M3",                  "MiniMax M3",                 1048576, 1048576, "sambanova-api"),
    ("gemma-4-31B-it",             "Gemma 4 31B It",             131072, 131072, "sambanova-api"),
    ("gpt-oss-120b",               "GPT-OSS 120B",               131072, 131072, "sambanova-api"),
]

# ── Cerebras models (from inference-docs.cerebras.ai/models) ──────────────────
CEREBRAS_MODELS = [
    ("gpt-oss-120b",    "GPT-OSS 120B",    131072, 65536, "cerebras-docs"),
    ("qwen-3.8-27b",   "Qwen 3.8 27B",   131072, 65536, "cerebras-docs"),
]

# ── OpenRouter context_length lookup (for fallback) ──────────────────────────
def _load_or_ctx():
    """Load OpenRouter context_length by model tail (last segment of id)."""
    import urllib.request
    try:
        data = json.loads(urllib.request.urlopen(
            "https://openrouter.ai/api/v1/models", timeout=30).read())
        lut = {}
        for m in data["data"]:
            tail = m["id"].rsplit("/", 1)[-1].lower()
            if m.get("context_length") and (tail not in lut or m["top_provider"].get("context_length")):
                lut[tail] = m["context_length"]
        return lut
    except Exception as e:
        print(f"Warning: could not fetch OpenRouter context lookup: {e}")
        return {}

OR_CTX = _load_or_ctx()

def ctx_for(model_id, provider_ctx, source):
    """Resolve context: provider → OR fallback → Luna."""
    if provider_ctx is not None:
        return provider_ctx, source
    # OR fallback: strip common prefixes to find a match
    tail = model_id.lower().replace("-", "").replace("_", "").replace("/", "")
    for key, val in OR_CTX.items():
        if key.replace("-","").replace("_","") in tail or tail in key.replace("-","").replace("_",""):
            return val, "openrouter-fallback"
    return FALLBACK_CTX, "fallback-luna"

def fmt(mid, base, pid, pctx, pout, src):
    ctx, _src = ctx_for(mid, pctx, src)
    return {
        "model_id": mid,
        "wire_model": mid,
        "display_name": f"{base} ({pid})",
        "max_prompt_tokens": ctx,
        "max_output_tokens": pout,
        "wire_api_override": None,
        "supported_reasoning_efforts": None,
    }

def upsert_byok():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"{DATA_DB}.bak-{ts}"
    shutil.copy2(DATA_DB, backup)
    print(f"Backup: {backup}")

    conn = sqlite3.connect(DATA_DB)
    conn.execute("PRAGMA foreign_keys=OFF")

    for prov_name, pid in PROVIDER_IDS.items():
        if prov_name == "Groq":
            rows = [fmt(m[0], m[1], prov_name, m[2], m[3], m[4]) for m in GROQ_MODELS]
        elif prov_name == "Google AI":
            rows = [fmt(m[0], m[1], prov_name, m[2], m[3], m[4]) for m in GOOGLE_MODELS]
        elif prov_name == "Mistral":
            rows = [fmt(m[0], m[1], prov_name, m[2], m[3], m[4]) for m in MISTRAL_MODELS]
        elif prov_name == "SambaNova":
            rows = [fmt(m[0], m[1], prov_name, m[2], m[3], m[4]) for m in SAMBA_MODELS]
        elif prov_name == "Cerebras":
            rows = [fmt(m[0], m[1], prov_name, m[2], m[3], m[4]) for m in CEREBRAS_MODELS]
        else:
            continue

        existing = {r[0] for r in conn.execute(
            "SELECT model_id FROM provider_models WHERE provider_id=?", (pid,))}
        new_ids = {r["model_id"] for r in rows}

        # Remove stale models
        stale = existing - new_ids
        if stale:
            placeholders = ','.join('?' for _ in stale)
            conn.execute(f"DELETE FROM provider_models WHERE provider_id=? AND model_id IN ({placeholders})",
                         (pid,) + tuple(stale))
            print(f"{prov_name}: -{len(stale)} removed")

        ins = upd = 0
        for r in rows:
            if r["model_id"] in existing:
                upd += 1
            else:
                ins += 1
            conn.execute(
                """INSERT OR REPLACE INTO provider_models
                   (id, provider_id, model_id, wire_model, display_name,
                    max_prompt_tokens, max_output_tokens, wire_api_override,
                    supported_reasoning_efforts)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), pid, r["model_id"], r["wire_model"],
                 r["display_name"], r["max_prompt_tokens"], r["max_output_tokens"],
                 r["wire_api_override"], r["supported_reasoning_efforts"]))

        conn.execute("UPDATE model_providers SET updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?", (pid,))
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM provider_models WHERE provider_id=?", (pid,)).fetchone()[0]
        print(f"{prov_name}: +{ins} new, ~{upd} updated, {total} total in DB")

    conn.close()
    print(f"\nDone. RESTART the Copilot App to load the new model list.")

if __name__ == "__main__":
    dry = "--dry-run" in __import__("sys").argv
    if dry:
        print("Dry-run: would insert models for:", list(PROVIDER_IDS.keys()))
    else:
        upsert_byok()
