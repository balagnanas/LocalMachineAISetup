---
name: opencode-zen-models
description: List the models available from the OpenCode Zen provider (provider ID `opencode`, API base https://opencode.ai/zen/v1). Uses `opencode models opencode` for a plain id list or `--verbose` for per-model metadata (display name, cost, context window, capabilities). Use when the user asks what models are available in OpenCode Zen, wants to browse `opencode/...` model ids, or needs model cost, context-size, or capability details.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: general
---

## What I do

- List every model served by the OpenCode Zen provider.
- Show plain model ids (`opencode/big-pickle`, `opencode/gpt-5.6-luna`, ...).
- Optionally dump per-model metadata: display name, input/output/cache cost, context/input/output limits, and capabilities (reasoning, tool calls, attachments, input/output modalities).
- Refresh the local model cache from models.dev when the list looks stale.

## Key fact: "OpenCode Zen" is provider id `opencode`

`opencode providers list` labels the credential **"OpenCode Zen api"**, but that label is *not* the provider id. The provider id is **`opencode`** (API base `https://opencode.ai/zen/v1`). So:

- `opencode models zen` → `Error: Provider not found: zen`
- `opencode models opencode` → the OpenCode Zen model list

The sibling provider **"OpenCode Go api"** uses id `opencode-go` and serves a *different* model set. Never conflate the two.

## When to use me

Use this skill when the user asks:

- "What models are available in OpenCode Zen?"
- "List the opencode models."
- "Which OpenCode Zen models support reasoning / tool calls / image input?"
- "How much does `opencode/gpt-5.6-luna` cost?"

## Process

1. **Plain id list** (default):
   ```bash
   opencode models opencode
   ```

2. **Verbose metadata** (name, cost, limits, capabilities):
   ```bash
   opencode models opencode --verbose
   ```

3. **Refresh the cache** if the list looks incomplete or outdated:
   ```bash
   opencode models opencode --refresh
   ```

4. **All providers** (for comparison; note `opencode-go`, `lmstudio`, `ollama`, `codex-router`, ...):
   ```bash
   opencode models
   ```

## Output format

For a plain list, group the ids by model family (illustrative — always regenerate from the command):

| Family | Examples |
| --- | --- |
| claude | `opencode/claude-sonnet-4-6`, `opencode/claude-opus-4-8` |
| deepseek | `opencode/deepseek-v4-flash`, `opencode/deepseek-v4-pro` |
| gemini | `opencode/gemini-3.7-flash`, `opencode/gemini-3.1-pro` |
| glm | `opencode/glm-5.2` |
| gpt | `opencode/gpt-5.6-luna`, `opencode/gpt-5.6-sol`, `opencode/gpt-5.6-terra` |
| grok | `opencode/grok-4.6` |
| kimi | `opencode/kimi-k3` |
| minimax | `opencode/minimax-m3` |
| muse-spark | `opencode/muse-spark-1.2` |
| nemotron | `opencode/nemotron-3.5-lightning-free` |
| qwen | `opencode/qwen3.6-plus` |

For `--verbose` output, surface only the fields relevant to the user's question: `name`, `cost` (input/output/cache), `limit` (context/input/output), and `capabilities` (reasoning, toolcall, attachment, input/output modalities).

## Rules

- Never attribute a model to the wrong provider: `opencode/` is OpenCode Zen, `opencode-go/` is OpenCode Go.
- Prefer the plain list; use `--verbose` only when the user asks about cost, context size, or capabilities.
- Always run `opencode models opencode` (with `--refresh` if stale) — never report a model catalog from memory, since it changes.
