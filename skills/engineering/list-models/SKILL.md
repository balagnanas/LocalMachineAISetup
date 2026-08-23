---
name: list-models
description: List the models available from the OpenCode Zen (provider ID `opencode`, API base https://opencode.ai/zen/v1) and OpenCode Go (provider ID `opencode-go`, API base https://opencode.ai/zen/go/v1) providers. Runs `opencode models opencode` / `opencode models opencode-go` for plain id lists or `--verbose` for per-model metadata (display name, cost, context window, capabilities). Use when the user asks what models are available in OpenCode Zen or OpenCode Go, wants to browse `opencode/...` or `opencode-go/...` model ids, or needs model cost, context-size, or capability details.
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: general
---

## What I do

- List every model served by the OpenCode Zen and OpenCode Go providers.
- Show plain model ids (`opencode/gpt-5.6-luna`, `opencode-go/deepseek-v4-pro`, ...).
- Optionally dump per-model metadata: display name, input/output/cache cost, context/input/output limits, and capabilities (reasoning, tool calls, attachments, input/output modalities).
- Refresh the local model cache from models.dev when the list looks stale.

## Key facts: provider labels vs ids

`opencode providers list` labels the credentials **"OpenCode Zen api"** and **"OpenCode Go api"**, but those labels are *not* the provider ids. The real provider ids are:

| Friendly label | Provider id | API base |
| --- | --- | --- |
| OpenCode Zen api | `opencode` | `https://opencode.ai/zen/v1` |
| OpenCode Go api | `opencode-go` | `https://opencode.ai/zen/go/v1` |

So:

- `opencode models zen` → `Error: Provider not found: zen`
- `opencode models opencode` → the OpenCode Zen model list
- `opencode models go` → `Error: Provider not found: go`
- `opencode models opencode-go` → the OpenCode Go model list

The two providers serve *different* model sets (Zen is the larger catalog). Never conflate them.

## When to use me

Use this skill when the user asks:

- "What models are available in OpenCode Zen / OpenCode Go?"
- "List the opencode / opencode-go models."
- "Which OpenCode Zen or Go models support reasoning / tool calls / image input?"
- "How much does `opencode/gpt-5.6-luna` or `opencode-go/deepseek-v4-pro` cost?"

## Process

Determine which provider the user means (Zen, Go, or both), then run the matching command(s).

1. **Zen — plain id list** (default):
   ```bash
   opencode models opencode
   ```

2. **Go — plain id list**:
   ```bash
   opencode models opencode-go
   ```

3. **Verbose metadata** (name, cost, limits, capabilities) — add `--verbose` to either:
   ```bash
   opencode models opencode --verbose
   opencode models opencode-go --verbose
   ```

4. **Refresh the cache** if the list looks incomplete or outdated:
   ```bash
   opencode models opencode --refresh
   opencode models opencode-go --refresh
   ```

5. **All providers** (for comparison; note `lmstudio`, `ollama`, `codex-router`, ...):
   ```bash
   opencode models
   ```

## Output format

For a plain list, group the ids by provider and model family (illustrative — always regenerate from the command).

**OpenCode Zen (`opencode/`):**

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

**OpenCode Go (`opencode-go/`):**

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

- Never attribute a model to the wrong provider: `opencode/` is OpenCode Zen, `opencode-go/` is OpenCode Go.
- Prefer the plain list; use `--verbose` only when the user asks about cost, context size, or capabilities.
- Always run `opencode models opencode` / `opencode models opencode-go` (with `--refresh` if stale) — never report a model catalog from memory, since it changes.
