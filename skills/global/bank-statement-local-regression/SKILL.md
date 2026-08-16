---
name: bank-statement-local-regression
description: Run the authorized four-PDF Irish bank-statement regression through Ledger IQ at localhost:8000, verify extraction, Balance Check, Review Queue, and Field Evidence workbook output, and record a concise reusable learning. Use after bank-statement extractor or review-workbook changes, or whenever local statement reliability needs proof.
---

# Bank Statement Local Regression

Run only against `http://localhost:8000`; never add customer PDFs or absolute OneDrive paths to the repository or this skill.

## Preconditions

1. Require a healthy paired local Ledger deployment: `/healthz`, `/readyz`, queue worker heartbeat, and matching web/worker image.
2. Require a host-local manifest through `BANK_STATEMENT_REGRESSION_MANIFEST`. It must name exactly the authorized PDFs: Permanent TSB, Revolut 1, AIB March 2026, and BOI with handwriting.
3. Use the same exact deployed dev SHA in the report. Do not run the corpus as CI or a PR gate.

## Run

1. Inspect the manifest without printing its absolute paths or PDF contents. Refuse any manifest that does not contain exactly four files.
2. Upload all four PDFs to `POST /api/statements/convert`; record the returned statement ID.
3. Poll `GET /api/statements/{id}/status` to a terminal state. Treat a worker timeout, skipped file, or failed item as regression failure.
4. Download `GET /api/statements/{id}/report` and inspect it with openpyxl. Require `Balance Check`, `Review Queue` when a mismatch is retained, `Extraction Provenance`, and `Field Evidence`.
5. For every source statement, report transaction count, Balance Check statuses, first divergence page (if any), Review Queue count, and five-field Field Evidence coverage. Preserve mismatches as reviewable; confidence must never turn a mismatch into pass.

## Learning loop

After a completed run, append one redacted observation to `references/observed-learnings.md`: date, deployed SHA, pass/fail, four source basenames, workbook-sheet evidence, and a verified follow-up. Never include paths, PDFs, credentials, tenant identifiers, or raw transactions. Reuse these observations on later runs, but verify deployment state and manifest afresh.
