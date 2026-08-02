# Observed release learnings

Append only confirmed, reusable operational evidence here. Future release sessions must read this file before acting.

Do not include secrets, customer data, tokens, connection strings, or raw logs.
## 2026-07-21T20:30:56+00:00 — verification (succeeded)
<!-- event:deploy-29788789735 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/29788789735
- Learning: Follow canonical-host redirects during readiness checks; otherwise a successful HTTP redirect can yield an empty body and a misleading verification failure.
## 2026-07-21T21:18:34+00:00 — verification (failed-rolled-back)
<!-- event:deploy-29868959087 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/29868959087
- Learning: Ledger worker healthcheck succeeded, but the new web revision did not meet the paired healthy-revision and 100-percent-traffic verifier before timeout; the workflow restored the prior web and worker digest and confirmed rollback.
## 2026-07-27T10:46:23+00:00 — deployment (succeeded)
<!-- event:30259120080 -->
- Evidence: https://github.com/balagnanas/VeritaxIQ/actions/runs/30259120080
- Learning: Green master dd7aefce deployed veritax-web-dd7aefc to Healthy revision 0000026 with 100 percent traffic; public health and readiness passed, including Graph assignment permissions.
