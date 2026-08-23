---
name: opencode-go-models
description: List the models available from the OpenCode Go provider (provider ID `opencode-go`, API base https://opencode.ai/zen/go/v1). Uses `opencode models opencode-go` for a plain id list or `--verbose` for per-model metadata (display name, cost, context window, capabilities). Use when the user asks what models are available in OpenCode Go, wants to browse `opencode-go/...` model ids, or needs model cost, context-size, or capability details.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: general
---

## What I do

- List every model served by the OpenCode Go provider.
- Show plain model ids (`opencode-go/deepseek-v4-pro`, `opencode-go/qwen3.8-max`, ...).
- Optionally dump per-model metadata: display name, input/output/cache cost, context/input/output limits, and capabilities (reasoning, tool calls, attachments, input/output modalities).
- Refresh the local model cache from models.dev when the list looks stale.

## Key fact: "OpenCode Go" is provider id `opencode-go`

`opencode providers list` labels the credential **"OpenCode Go api"**, but that label is *not* the provider id. The provider id is **`opencode-go`** (API base `https://opencode.ai/zen/go/v1`). So:

- `opencode models go` → `Error: Provider not found: go`
- `opencode models opencode-go` → the OpenCode Go model list

The sibling provider **"OpenCode Zen api"** uses id `opencode` (API base `https://opencode.ai/zen/v1`) and serves a *different, larger* model set. Never conflate the two.

## When to use me

Use this skill when the user asks:

- "What models are available in OpenCode Go?"
- "List the opencode-go models."
- "Which OpenCode Go models support reasoning / tool calls / image input?"
- "How much does `opencode-go/gpt-5.6-luna` cost?"

## Process

1. **Plain id list** (default):
   ```bash
   opencode models opencode-go
   ```

2. **Verbose metadata** (name, cost, limits, capabilities):
   ```bash
   opencode models opencode-go --verbose
   ```

3. **Refresh the cache** if the list looks incomplete or outdated:
   ```bash
   opencode models opencode-go --refresh
   ```

4. **All providers** (for comparison; note `opencode`, `lmstudio`, `ollama`, `codex-router`, ...):
   ```bash
   opencode models
   ```

## Output format

For a plain list, group the ids by model family (illustrative — always regenerate from the command):

| Family | Examples |
| --- | --- |
| deepseek | `opencode-go/deepseek-v4-flash`, `opencode-go/deepseek-v4-pro`, `opencode-go/deepseek-v4-flash-vision-exp` |
| glm | `opencode-go/glm-5.1`, `opencode-go/glm-5.2`, `opencode-go/glm-5.3` |
| gpt | `opencode-go/gpt-5.6-luna` |
| grok | `opencode-go/grok-4.5` |
| hy3 | `opencode-go/hy3` |
| kimi | `opencode-go/kimi-k2.6`, `opencode-go/kimi-k2.7-code`, `opencode-go/kimi-k3` |
| mimo | `opencode-go/mimo-v2.5`, `opencode-go/mimo-v2.5-pro` |
| minimax | `opencode-go/minimax-m2.7`, `opencode-go/minimax-m3` |
| muse-spark | `opencode-go/muse-spark-1.2-contributor` |
| ox | `opencode-go/ox-alpha-free` |
| qwen | `opencode-go/qwen3.6-plus`, `opencode-go/qwen3.7-plus`, `opencode-go/qwen3.7-max`, `opencode-go/qwen3.8-max` |

For `--verbose` output, surface only the fields relevant to the user's question: `name`, `cost` (input/output/cache), `limit` (context/input/output), and `capabilities` (reasoning, toolcall, attachment, input/output modalities).

## Rules

- Never attribute a model to the wrong provider: `opencode-go/` is OpenCode Go, `opencode/` is OpenCode Zen.
- Prefer the plain list; use `--verbose` only when the user asks about cost, context size, or capabilities.
- Always run `opencode models opencode-go` (with `--refresh` if stale) — never report a model catalog from memory, since it changes.
