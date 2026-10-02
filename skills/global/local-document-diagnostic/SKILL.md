---
name: local-document-diagnostic
description: Run one explicitly authorized user-supplied document through the local VeritaxIQ app on approved localhost:8000 or localhost:8001, using either /statements or /invoices, and capture the terminal API response, review/report workbook, and privacy-safe evidence. Use for the final localhost verification step after an extraction change or for a targeted customer-document diagnosis.
---

# Local Document Diagnostic

Run one supplied document through the current local stack and capture evidence from the real
browser workflow. This is targeted evidence, not the four-PDF bank-statement regression corpus
and not a production verification.

## Destination contract

Use exactly one of these user-specified local endpoints. The port must be explicitly named by the
user or by the deployment task: `8000` is the dev stack and `8001` is the isolated feature stack.

| Document | UI endpoint | Primary API/report contract |
| --- | --- | --- |
| Bank statement | `http://localhost:<approved-port>/statements` | `/api/statements/convert`, `/status`, `/review`, `/report` |
| Invoice | `http://localhost:<approved-port>/invoices` | The invoice page's normal batch/upload/status/report APIs |

Never substitute a hosted Ledger URL, production endpoint, or a localhost port other than `8000`
or `8001`. If the user has not named the destination, ask before uploading. Preserve the requested
port throughout upload, polling, report download, and evidence capture.

## Safety and privacy

1. Require explicit approval in the current conversation before uploading a personal or customer
   document. A path mentioned for inspection is not, by itself, permission to transmit it.
2. Accept the input path at run time. Never hardcode a customer filename, OneDrive path, document
   text, vendor/customer name, account number, invoice identifier, or extracted amount in this
   skill.
3. Upload exactly the selected document. Refuse a folder or a multi-file selection unless the user
   explicitly changes the scope.
4. Use the normal browser UI and app API flow. Do not bypass the UI with direct blob writes,
   synthetic API payloads, or a second extraction mode.
5. Do not edit source code, prompts, extraction flags, corrections, or production configuration as
   part of this diagnostic. Do not publish or commit the input document or generated workbook.
6. Keep any full response capture local, outside the repository, with restrictive permissions. The
   final report is redacted by default and contains hashes, counts, statuses, sheet evidence, and
   review reasons only.

## Preconditions

1. Confirm the selected endpoint is reachable and the local stack is healthy. Where available,
   record `/healthz`, `/readyz`, queue/worker readiness, and the active web/worker image or build
   identity. A healthy page alone is not proof of the requested build.
2. Confirm the input file exists and calculate its SHA-256. Do not print the absolute path or raw
   document content in the final report.
3. Confirm the selected endpoint supports the file type. Stop if the UI is not the requested
   document workflow.
4. Keep the current local stack unchanged. Deploy or restart only when the user separately asks
   for deployment or refresh.

## Run

1. Open the exact endpoint in the in-app browser and record the initial page state.
2. Upload only the selected input file through the visible upload control.
3. Start the normal conversion/extraction action. Capture the returned job/batch/statement ID,
   upload response, timestamps, and terminal status.
4. Poll the endpoint's normal status API until a terminal state. Record completed, failed,
   skipped, review-required, and warning counts. A timeout or failed item is a diagnostic failure;
   preserve the partial result rather than silently retrying with changed settings.
5. Download the generated report/workbook through the application. Store the local diagnostic copy
   outside the repository and record its SHA-256.
6. Capture the app-level JSON responses available to the browser: conversion/queue response,
   terminal status, review payload, and report metadata. Write a local JSON evidence file containing
   those responses plus a redacted summary. Do not expose the file contents in the final response.
7. Check whether the app exposes the raw Document Intelligence response. If it does not, record
   `raw_di_response_available=false` and state that the captured evidence is the app's normalized
   DI-derived payload. Do not claim that the raw DI response was captured.

## Bank-statement checks (`/statements`)

Inspect the workbook and API review payload together. Require, when present:

- `Combined Statement` or equivalent transaction sheet;
- `Balance Check` with stated/computed opening and closing values and first divergence;
- `Review Queue` when a mismatch or extraction exception is retained;
- `Extraction Provenance` showing the extraction method and source page;
- `Field Evidence` showing balance provenance, source region, and confidence availability.

Report transaction count, debit/credit totals, opening/closing statuses, mismatch delta, first
divergence page/row, review item count, and whether any ambiguous source cell was excluded.

Preserve every balance mismatch as reviewable. Confidence, a guessed sign, or a plausible manual
calculation must never turn a discrepancy into a pass. Do not apply corrections during this run.

## Invoice checks (`/invoices`)

Inspect the invoice report and API review/status payload together. At minimum verify:

- source count and completed/failed/skipped counts;
- report availability and the invoice/reportable-record sheet;
- `extraction_path` or equivalent provenance for every completed record;
- degraded extraction count and the exact blocking review reason for every
  `extraction_degraded=true` record;
- blocking Manual Review/review-queue count versus non-blocking validation flags;
- any API-to-workbook count or status mismatch.

Report only aggregate and path-level results by default. State explicitly when this document did
not exercise a degraded fallback. Preserve failed, partial, and review-required records.

## Evidence file

Use a local, restrictive temporary location such as `/private/tmp` for the capture. A compact
evidence object should include only:

```json
{
  "destination": "http://localhost:<approved-port>/statements",
  "input_sha256": "...",
  "document_kind": "statement",
  "job_id": "...",
  "terminal_status": "needs_review",
  "report_sha256": "...",
  "raw_di_response_available": false,
  "summary": {},
  "captured_at": "..."
}
```

The full app responses may be retained in the local evidence file for the authorized operator,
but must not be copied into the repository, learning logs, pull requests, or final chat response.

## Final report

Separate confirmed evidence from hypotheses. Include:

- destination and document kind;
- input and report hashes;
- job/batch ID and terminal status;
- endpoint-specific workbook/API checks;
- review-required or degraded-extraction safeguards;
- raw-DI availability boundary;
- remaining gaps and whether any source or code change was made.

State `diagnostic complete` only when the report was downloaded and inspected. State
`partially complete` when the app finished but a report, status response, or required evidence
sheet could not be obtained. Never report a fix or reconciliation that was not actually run.
