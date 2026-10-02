---
name: orchestrate-cheap
description: Cheap Orchestrate routing on this machine. Use when the user invokes /orchestrate, asks to orchestrate work, or spawn Planner/Worker/Reviewer/Tester child sessions for non-financial coding.
---

# Cheap Orchestrate routing

Load `orchestrate` first, then apply this model map on every child session.

## Model map

Pass **both** `kickoff.agent` and `kickoff.model`. Child sessions do not inherit this chat’s model.

| Role | `kickoff.agent` | `kickoff.model` |
| --- | --- | --- |
| Planner | `Planner` | `87510620-8885-4595-8c07-aeab1c0cec16/deepseek-v4-pro` |
| Worker | `Worker` | `a0694a8f-1561-4ad0-81ed-d8f2bb5340d3/qwen3.8:27b-mlx` |
| Reviewer | `Reviewer` | `87510620-8885-4595-8c07-aeab1c0cec16/hy3` |
| Tester | `Tester` | `a0694a8f-1561-4ad0-81ed-d8f2bb5340d3/qwen3.8:27b-mlx` |

Planner fallback only if Pro is unavailable: `87510620-8885-4595-8c07-aeab1c0cec16/hy3`.

Default loop: Planner (Pro) → Worker (local Qwen) → Reviewer (Hy3) → Tester (local Qwen).

## Small-context Worker packet (mandatory)

Local Ollama `qwen3.8:27b-mlx` has a **tiny usable context** on this machine. Do **not** paste the Planner’s research, repo dumps, long diffs, `AGENTS.md`, or this chat into Worker/Tester.

1. Planner (large context) reads widely and writes a full plan **for the coordinator only**.
2. Coordinator (or Planner) then emits a **Worker Packet** per slice. Spawn one Worker session per packet.
3. Worker kickoff = **only** the packet. Tester kickoff = packet + files changed + exact commands. Reviewer may see a larger diff.

### Worker Packet (hard cap)

Keep the kickoff under **~1,200 tokens / ~80 lines**. One slice = **1–2 files**, one independently testable change.

```
Goal: <one sentence>
Files: <exact paths only>
Do: <numbered steps, 3–8 lines>
Do not: <out of scope>
Accept: <2–5 observable checks>
Snippet: <optional ≤15 lines of the exact code to change>
```

If the plan needs more files, **split into sequential Worker sessions**. Never give Qwen the whole plan.
