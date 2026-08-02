# Observed release learnings

Append only confirmed, reusable operational evidence here. Future release sessions must read this file before acting.

Do not include secrets, customer data, tokens, connection strings, or raw logs.

## 2026-07-21T20:30:56+00:00 — verification (succeeded)

<!-- event:deploy-29788789735 -->

- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/29788789735
- Learning: Follow canonical-host redirects during readiness checks; otherwise a successful HTTP redirect can yield an empty body and a misleading verification failure.
## 2026-07-29T13:11:58+00:00 — deployment (succeeded)
<!-- event:30454194532 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30454194532
- Learning: Atomic Ledger verification confirmed healthy 100 percent traffic, shared web and worker digest, ready endpoints, fresh heartbeat, and an empty queue.
## 2026-07-29T13:11:59+00:00 — deployment (succeeded)
<!-- event:30454569420 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30454569420
- Learning: Poll Container Apps revision health after workflow success because the new Admin Console revision briefly reported no health state before becoming Healthy at 100 percent traffic.
## 2026-07-29T16:05:40+00:00 — verification (succeeded)
<!-- event:deploy-30468102691 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30468102691
- Learning: For Ledger parser releases, verify the active web revision, worker template, and readiness heartbeat all report the same immutable digest before declaring the rollout complete.
## 2026-07-29T16:05:45+00:00 — verification (succeeded)
<!-- event:deploy-30468541265 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30468541265
- Learning: After the core Admin Console rollout, poll the new Container Apps revision until HealthState is Healthy and confirm both public health and readiness endpoints independently.
## 2026-08-01T18:47:53+00:00 — integration (succeeded)
<!-- event:30713160365 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30713160365
- Learning: Core veritax-web deployment must explicitly set EXTRACTION_MODE=di_first; image-only updates retain the prior runtime mode and can preserve LLM-first timeout behavior.
## 2026-08-01T22:52:36+00:00 — verification (succeeded)
<!-- event:30722013107 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30722013107
- Learning: Ledger release c11993a6 restored the long-document worker profile; post-release verification confirmed shared digest f3eb523e, profile enabled, 600-second deadline, one-page windows, and a fresh worker heartbeat.
