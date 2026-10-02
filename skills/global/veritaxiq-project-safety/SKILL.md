---
name: veritaxiq-project-safety
description: Apply VeritaxIQ/Ledger financial-safety, privacy, provenance, and evidence rules. Use when working on invoice extraction, bank statements, reconciliation, Statement Review, corrections, local document diagnostics, or extraction regressions.
---

# VeritaxIQ project safety

Use this skill for product and document-processing work. It contains durable contracts only; historical commit, PR, deployment, and customer-document details belong in the machine memory store.

## Before acting

1. Inspect the current source path, tests, configuration, and active runtime. Do not infer current behavior from an old rollout.
2. For a customer PDF or live provider call, require explicit authorization for the exact destination and scope. Report only privacy-safe aggregates, basenames when necessary, and workbook/API status evidence.
3. Keep web and worker behavior aligned. A healthy web container, merged commit, or unit test is not proof of the requested extraction or review workflow.

## Financial contracts

- Preserve `needs_review`, `unknown`, `Unverifiable`, balance mismatches, Extraction Exceptions, degraded flags, and provenance when evidence is incomplete.
- Never turn a review-required result into a pass from confidence, a heuristic signature, or a plausible guess.
- Never auto-apply a correction. Any proposal must identify the exact transaction and be replay-tested; ambiguity returns `FixSuggestion(kind="unknown", correction=None)`.
- A completed job is not necessarily complete or financially verified. Inspect persisted status, extraction path, source-page span, workbook sheets, and reconciliation evidence.

## Bank statements

- Prefer native exports, then deterministic layout/table parsing and bounded recovery. Keep visual/LLM repair shadow or review-only unless evidence improves or preserves reconciliation.
- Unsigned amounts must not default to credit. Do not borrow dates across pages/sections without matching evidence and printed checkpoint reconciliation.
- A non-empty statement producing zero transactions is a visible failure.
- Inspect `Balance Check`, `Review Queue`, `Extraction Provenance`, `Field Evidence`, `Extraction Exceptions`, and source-page evidence before declaring a result verified.
- Group balance diagnosis by source and currency. Never propose a cross-currency correction.

## Invoices

- Keep DI-first routing, bounded escalation, extraction path, page attribution, degraded state, review reasons, and report invariants visible.
- A `done` result may contain partial timeout output. Check the persisted records and deployed worker configuration before retrying.
- Supplier Examples are human-verified, redacted, tenant-scoped, disabled by default, and must be enabled consistently on web and worker. They do not reprocess existing invoices.
- Totals verification is bounded and review-preserving; retain original totals and evidence for any second-pass adjustment.

## Statement Review

- Corrections are append-only, ETag-protected, replayable, and auditable. Do not silently drop edits after conflicts.
- Source viewing resolves only manifest-authorized `sourceId` documents; reject traversal and do not guess page or bounding box.
- Test the real browser path: insert → type → click away → save/reload → publish/download. A visible row is not persistence proof.
- Keep incomplete inserted rows local until they contain a positive Debit or Credit.

## Evidence and related skills

- For local dev deployment, use `veritaxiq-dev-deploy`; keep `localhost:8000` and `localhost:8001` isolated and prove paired web/worker digest, health, readiness, heartbeat, and the requested workflow.
- For production, use `veritaxiq-prod-deploy`; never bypass `docs/deploy-runbook.md` or `scripts/release-guard.sh`.
- Offline corpus tests protect deterministic contracts, not live provider quality or production readiness.
- Never claim a test, deployment, browser flow, or customer outcome that was not actually executed and observed.
