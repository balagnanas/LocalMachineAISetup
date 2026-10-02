---
name: veritaxiq-prod-deploy
description: One-step production deployment for Veritax IQ — Ledger (with Admin console and Client Portal) to ledger.veritaxiq.com, the Platform portal to app.veritaxiq.com, and the veritaxiq.com website to Cloudflare Pages when required. Use whenever a request mentions deploying, releasing, shipping, promoting dev to master, production, PROD, Azure Container Apps, Cloudflare, Ledger, a worker/job, a rollout, rollback, release verification, or a post-deployment status.
---

# Veritax IQ production deployment

Use the repository's versioned guard and runbook. Never treat a merged PR or a
green GitHub workflow as proof of a successful production release. Read
`docs/deploy-runbook.md` before a production action; `scripts/release-guard.sh`
is the enforcement point and must not be bypassed.

## Targets — deploy what the change touched, all from the same master commit

| Target | Production host | Contents | Script |
|---|---|---|---|
| `ledger` | `ledger.veritaxiq.com` | Ledger + Admin console (`/admin`) + Client Portal (`/portal`, `client.veritaxiq.com`) — one image | `scripts/deploy-ledger-prod.sh <tag>` |
| `veritax-web` | `app.veritaxiq.com` | Platform portal | `scripts/deploy-veritax-web-prod.sh <tag>` |
| website | `veritaxiq.com` | Marketing site (Cloudflare Pages) | `deploy-website.yml` or local wrangler (below) |

- Admin console and Client Portal ship **inside** the Ledger image; deploying
  `ledger` deploys both. There is no separate admin/portal production deploy.
- Most releases touch code shared by both Container Apps — promote **both**
  `ledger` and `veritax-web` together (see runbook).
- The website is a committed static export of `website-src/`; deploy it only
  when `website-src/` or `website/` changed in the release.

## Required flow

1. Work from a dedicated branch based on `origin/dev`. Preserve unrelated changes.
2. Run applicable checks before merging to `dev`:
   - Python: `./scripts/codex-env.sh python-ci` (Ruff, mypy, pytest with coverage).
   - .NET or web-shell changes: corresponding build/type-check commands.
   - Functions changes: clean dependency-install/import smoke test.
   - Website changes: `cd website-src && npm ci && npx next build`.
3. Merge into `dev`; wait for the CI run on that exact merge commit.
4. Promote the same green `dev` commit to `master`; wait for master CI.
5. Deploy per target. Prefer `scripts/prod-release.sh --app <target> --verify`.
   While GitHub Actions is billing-blocked, `prod-release.sh` cannot deploy —
   use the local scripts instead (`deploy-ledger-prod.sh`,
   `deploy-veritax-web-prod.sh`). Both replicate the `deploy.yml` case blocks,
   run `release-guard.sh --ref master --local-gate` first, and verify revision
   health/traffic plus public healthz/readyz. Positional image tag only; no
   flags. Flag the billing-blocked CI-evidence gap to the user before deploying.
6. Website (when required): the canonical path is the `deploy-website.yml`
   workflow (`wrangler pages deploy website-src/out`). If Actions is
   billing-blocked and the user approves using Cloudflare credentials locally:
   `cd website-src && npm ci && npx next build && npx wrangler pages deploy
   out --project-name=$CF_PROJECT --branch=master`. Never deploy the website
   without an explicit user request for this release.
7. Keep each deployment open until it completes; then independently verify live
   Azure/Cloudflare state and public health/readiness.

## Target rules

- One target at a time. For a new feature, default its runtime feature flag to
  off and enable it gradually after deployment.
- `ledger` is an atomic `ledger-web` + `ledger-statement-worker` release; never
  deploy them independently.
- For Ledger, require one immutable image digest across the active web
  revision, job template, and healthcheck heartbeat; require a healthy revision
  with 100% traffic.
- If a deployment, healthcheck, readiness, or digest assertion fails, confirm
  the paired rollback completed before doing anything else.

## Mandatory evidence

Report the exact master commit, workflow URL (or local-script run), image
tag/digest, revision and traffic, worker execution (when relevant), and
`/healthz` plus `/readyz` state for every deployed target. State any optional
degraded component explicitly.

Verification examples:

```bash
curl --location -sS -o /dev/null -w "%{http_code}\n" https://ledger.veritaxiq.com/healthz
curl --location -sS -o /dev/null -w "%{http_code}\n" https://ledger.veritaxiq.com/readyz
curl --location -sS -o /dev/null -w "%{http_code}\n" https://app.veritaxiq.com/healthz
curl --location -sS -o /dev/null -w "%{http_code}\n" https://app.veritaxiq.com/readyz
curl --location -sS -o /dev/null -w "%{http_code}\n" https://veritaxiq.com
```

Follow canonical-host redirects (`curl --location`); the Client Portal serves
at `client.veritaxiq.com` via host-redirect middleware.

## Common failure handling

- Allow for Azure eventual consistency: poll images, revision health, and
  traffic rather than asserting immediately.
- Treat Blob index-tag writes as a separate Storage data-plane permission; use
  the narrow tag role, not Blob Data Owner.
- If the desktop free-port test is the only failure in the sandbox, rerun that
  test outside the sandbox and record the sandbox restriction.

## Learning loop

The skill evolves through an append-only observed-learning log. Before a
release, read `references/observed-learnings.md` for current operational
evidence. After each completed deployment, failed deployment with verified
rollback, or material integration incident, record one concise, reusable
observation with an immutable evidence URL:

```bash
python scripts/record_release_learning.py \
  --event-id <workflow-run-or-incident-id> \
  --status succeeded|failed-rolled-back \
  --category deployment|integration|verification|permissions \
  --evidence <https-url> \
  --learning "<observable cause, prevention, or verification step>"
```

Record only confirmed, non-secret operational facts. Never include customer data, credentials, tokens, connection strings, or raw logs. The recorder is
idempotent; no duplicate event IDs or speculative conclusions. Do not automatically weaken or rewrite the required flow, target rules, guard,
workflow, or rollback rules; treat a repeated high-confidence pattern as a
candidate only and change core rules after explicit user approval and
validation.
