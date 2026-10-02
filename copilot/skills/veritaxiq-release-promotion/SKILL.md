---
name: veritaxiq-release-promotion
description: Safely promote and deploy Veritax IQ feature or bug-fix changes, while recording evidence-backed release learnings. Use whenever a request mentions deploying, releasing, shipping, promoting dev to master, production, PROD, Azure Container Apps, Ledger, a worker/job, a rollout, rollback, release verification, or a post-deployment status for this repository.
---

# Veritax IQ release promotion

Use the repository's versioned guard and runbook. Do not treat a merged pull request or a green GitHub workflow as proof of a successful production release.

## Required flow

1. Work from a dedicated branch based on `origin/dev`. Preserve unrelated local changes.
2. Run the applicable checks before merging to `dev`:
   - Python: `ruff check .`, `mypy`, and `pytest --cov --cov-report=term-missing --cov-report=xml`.
   - .NET or web-shell changes: the corresponding build/type-check commands and CI.
   - Functions changes: clean dependency-install/import smoke test.
3. Merge the tested change into `dev`; wait for the CI run on that exact merge commit.
4. Promote that same green `dev` commit to `master`; wait for master CI.
5. Use `scripts/prod-release.sh --app <target> --verify`. It deploys `master` only and the release guard rejects a commit without completed successful CI.
6. Keep the deployment run open until it completes. Then independently verify live Azure state and public health/readiness.

## Target rules

- Deploy one target at a time. For a new feature, default its runtime feature flag to off and enable it gradually after deployment.
- Use `ledger` only for Ledger. It is an atomic `ledger-web` and `ledger-statement-worker` release; never deploy them independently.
- For Ledger, require one immutable image digest across the active web revision, job template, and healthcheck heartbeat; require a healthy revision with 100% traffic.
- If a deployment, healthcheck, readiness check, or digest assertion fails, confirm the paired rollback completed before doing anything else.

## Mandatory evidence

Report the exact master commit, workflow URL, image tag/digest, revision and traffic, worker execution (when relevant), and `/healthz` plus `/readyz` state. State any optional degraded component explicitly.

## Common failure handling

- Allow for Azure eventual consistency: poll images, revision health, and traffic rather than asserting immediately.
- Follow canonical-host redirects during public readiness checks (`curl --location`).
- Treat Blob index-tag writes as a separate Storage data-plane permission; use the narrow tag role, not Blob Data Owner.
- If the desktop free-port test is the only failure in the sandbox, rerun that test outside the sandbox and record the sandbox restriction.

Read `docs/deploy-runbook.md` before a production action. The repository's `scripts/release-guard.sh` is the enforcement point; do not bypass it.

## Learning loop

Before a release, read `references/observed-learnings.md` for current operational evidence.

After each completed deployment, failed deployment with verified rollback, or material integration incident:

1. Record one concise, reusable observation with an immutable evidence URL by running:

   ```bash
   python scripts/record_release_learning.py \
     --event-id <workflow-run-or-incident-id> \
     --status succeeded|failed-rolled-back \
     --category deployment|integration|verification|permissions \
     --evidence <https-url> \
     --learning "<observable cause, prevention, or verification step>"
   ```

2. Record only confirmed, non-secret operational facts. Never include customer data, credentials, tokens, connection strings, or raw logs.
3. Do not add duplicate event IDs or speculative conclusions. The recorder is idempotent.
4. Do not automatically weaken or rewrite the required flow, target rules, guard, workflow, or rollback rules. Treat a repeated, high-confidence pattern as a candidate only; change core rules after explicit user approval and validation.

The skill evolves through the append-only observed-learning log. It retains stable safety rules while future sessions automatically use the proven lessons.
