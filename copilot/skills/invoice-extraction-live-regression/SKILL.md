---
name: invoice-extraction-live-regression
description: Run an authorized, end-to-end local VeritaxIQ invoice-extraction regression against a user-supplied PDF folder. Use when validating invoice extraction after a dev merge, checking extraction paths and degraded-fallback review handling, or collecting privacy-safe outcome trends from a live local Ledger stack.
---

# Invoice extraction live regression

Run this workflow only for an expressly authorized local regression corpus. It sends the selected
PDFs to the configured Document Intelligence/OpenAI services; obtain explicit approval in the
current conversation before uploading, even if the folder is user-provided.

Keep document content, filenames, customer/vendor names, invoice identifiers, paths, extracted
values, and service credentials out of the learning log and final summary unless the user asks
for those details.

## Procedure

1. Read `references/learning-log.jsonl` before acting. Use prior generic failure patterns to add
   relevant checks, but do not treat old results as proof of current behaviour.
2. Confirm the requested directory contains PDFs. Do not copy, commit, or persist the PDFs.
3. State that upload requires explicit approval and wait for the user to grant it. Do not send any
   document to external providers without that approval.
4. Resolve the exact current `origin/dev` SHA and confirm its required CI run is successful.
   Deploy that exact SHA to the local Ledger stack using the `ledger-local-dev-deployment` skill.
   Verify `/healthz`, `/readyz`, and matching healthy web/worker image digests. Leave a healthy
   stack running.
5. Submit every PDF through the normal local batch API: create a batch, upload each PDF, complete
   the batch, and poll to a terminal state. Use no shortcuts or direct blob writes.
6. Download and inspect the generated report. Verify every completed source has an outcome,
   reportable records contain an `extraction_path`, and every record with
   `extraction_degraded=true` has a blocking review reason exactly naming the reduced fallback.
   Compare the API review flags to the report sheets; distinguish blocking Manual Review routing
   from non-blocking validation statuses retained on the Invoices sheet.
7. Report only aggregate and path-level findings by default: source count, completed/failed/
   skipped count, extraction-path distribution, degraded count, review count, report availability,
   and any invariant violation. State explicitly when this corpus did not exercise a fallback.
8. Append one JSON object to `references/learning-log.jsonl` after every terminal run. It must
   contain only: UTC timestamp, exact SHA, source_count, completed_count, failed_count,
   skipped_count, extraction_path_counts, degraded_count, blocking_review_count,
   nonblocking_review_count, report_available, invariant_violations, and generic observations.
   Never include source names, paths, document text, vendors, customers, amounts, invoice IDs,
   batch IDs, service endpoints, or credentials.

## Learning policy

Treat the append-only log as diagnostic metadata, not a source of truth. On each run, look for
repeated aggregate patterns (for example a persistent path mismatch or a report/API count
distinction) and call them out. Do not alter production code, extraction routing, prompts, or
the local deployment based solely on the log. Update this skill's procedure only in a separate,
user-authorized maintenance task after corroborating a repeated pattern.

## Failure handling

* Stop before upload if provider authorization is absent.
* Stop before regression if `origin/dev` CI is not green or exact-SHA deployment health/digest
  parity cannot be established.
* Preserve failed/partial results as evidence; never retry by silently changing extraction mode.
* Do not log document details to the learning file.
