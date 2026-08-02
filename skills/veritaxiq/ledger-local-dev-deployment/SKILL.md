---
name: ledger-local-dev-deployment
description: Manually deploy the exact CI-verified VeritaxIQ dev commit to the local Ledger IQ stack at localhost:8000. Use when asked to refresh, manually trigger, redeploy, or verify the local Ledger dev environment.
---

# Ledger IQ local dev deployment

Deploy Ledger IQ **only on the current machine** at `http://localhost:8000`.
This is not an Azure Container Apps or production deployment.

Read `docs/local-dev-deployment.md` before acting. Follow the instructions
below rather than running Compose directly: the deployment script maintains
web/worker image parity and performs paired rollback when verification fails.

## Preconditions

1. Preserve unrelated changes. Never deploy from a dirty working tree.
2. Fetch `origin/dev` and deploy its exact 40-character SHA, not a branch name.
3. Require a successful `ci.yml` push run for that exact SHA. If CI is absent,
   pending, or failed, stop and report it; do not deploy an unverified commit.
4. On the local host, require Docker Compose v2, Azure CLI login, a readable
   host-only `~/.config/veritaxiq/ledger-local.env`, and a local Azure CLI
   config directory. Do not print the contents of either configuration.

## Deploy

Create a clean detached worktree, then run the repository script:

```bash
git fetch origin
SHA="$(git rev-parse origin/dev)"
WORKTREE="/private/tmp/ledgeriq-local-${SHA:0:12}"
git worktree add --detach "$WORKTREE" "$SHA"
cd "$WORKTREE"

az account show >/dev/null
scripts/deploy-ledger-local.sh "$SHA"
```

The script is the single deployment entry point. It uses local filesystem
storage and Azurite Queue; production Azure access is limited to Document
Intelligence and Azure OpenAI through short-lived Azure CLI tokens.

## Verify

After the script succeeds, independently check:

```bash
docker ps --filter name=ledgeriq-dev \
  --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}'
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
docker inspect ledgeriq-dev-web-1 ledgeriq-dev-worker-1 \
  --format '{{.Name}} {{.Config.Image}}'
```

Require both web and worker to be healthy, `/readyz` to report `ready`, and
both services to use the same image. Report the exact SHA, image digest, and
health/readiness result.

## Safety

- Do not use `docker compose down -v`; it destroys local Blob/Queue volumes.
- Do not deploy to Azure or modify production resources.
- Do not add Storage, Queue, Key Vault, Graph, Entra, or customer settings to
  the host-only AI configuration file.
- Leave the successful local stack running. Remove a temporary worktree only
  after confirming it has no unique changes.
