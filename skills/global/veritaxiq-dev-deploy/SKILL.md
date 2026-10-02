---
name: veritaxiq-dev-deploy
description: One-step dev deployment of the full Veritax IQ surface to localhost for testing — Ledger, Admin console, and Client Portal on the shared stack at localhost:8000, plus an optional local preview of the veritaxiq.com marketing website. Use when asked to deploy, refresh, redeploy, or verify the local dev environment or local website preview.
---

# Veritax IQ dev deployment (localhost)

Deploys everything to **this machine only**:

| Surface | Where locally | How it ships |
|---|---|---|
| Ledger | `http://localhost:8000` | Ledger stack (`deploy-ledger-local.sh`) |
| Admin console | `http://localhost:8000/admin` | Same Ledger image — no separate deploy |
| Client Portal | `http://localhost:8000/portal` (staff: `/admin/client-portal`) | Same Ledger image — no separate deploy |
| veritaxiq.com website | static preview on a scratch port | Local build of `website-src`, never deployed to Cloudflare |

The Admin console and Client Portal are routes inside the FastAPI monolith
(`webapp/app/admin.py`, `webapp/app/client_portal_routes.py`). One image, one
pipeline: never build a portal- or admin-specific image, compose project, or
state directory. `8001` stays reserved for the isolated feature stack.

The repository's `compose.codex.yaml` and `scripts/codex-env.sh` are tool-check
helpers only. They cannot deploy the Ledger runtime or prove runtime parity;
use the guarded local deployment script below.

## Preconditions

1. Never deploy from a dirty working tree.
2. Fetch `origin/dev` and deploy its exact 40-character SHA, not a branch name.
3. Verify the SHA: a successful `ci.yml` push run, or — while GitHub Actions is
   billing-blocked — a passing local `./scripts/codex-env.sh python-ci`.
   Deploy nothing unverified.
4. Require Docker Compose v2, Azure CLI login, and the host-only
   `~/.config/veritaxiq/ledger-local.env`. Never print that file's contents.

## Deploy Ledger (+ Admin + Portal)

```bash
git fetch origin
SHA="$(git rev-parse origin/dev)"
WORKTREE="/private/tmp/ledgeriq-local-${SHA:0:12}"
git worktree add --detach "$WORKTREE" "$SHA"
cd "$WORKTREE"

az account show >/dev/null
scripts/deploy-ledger-local.sh "$SHA"
```

The script is the single deployment entry point; it maintains web/worker image
parity and performs paired rollback when verification fails. It uses local
filesystem storage and Azurite Queue; Azure access is limited to Document
Intelligence and Azure OpenAI via short-lived CLI tokens.

## Verify

```bash
docker ps --filter name=ledgeriq-dev \
  --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}'
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
docker inspect ledgeriq-dev-web-1 ledgeriq-dev-worker-1 \
  --format '{{.Name}} {{.Config.Image}}'
curl --fail -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/portal
curl --fail -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/admin/client-portal
```

Require: web and worker healthy on the same image, `/readyz` = `ready`, and
`200` from both portal routes (`/portal` must identify as
`Veritax IQ — Client Portal`).

Then seed idempotent demo clients inside the web container (a fresh state dir
leaves the portal registry empty, which looks like a failed deploy; the image
has no `scripts/` directory):

```bash
docker exec ledgeriq-dev-web-1 python -c "
from veritax.config import Settings
from app import clients
s = Settings.from_env()
for name, email in (('Northwind Books', 'books@northwind.example'), ('Acme LLP', 'boss@acme.com')):
    try:
        m = clients.create_client(s, name, email=email)
        print('created', m['id'], m['name'])
    except clients.DuplicateClientNameError:
        print('exists ', name)
print('portal clients:', [c['name'] for c in clients.list_clients(s)])
"
```

Done when `/portal` lists both demo clients in the `admin-client-select`
options and `/readyz` still reports ready. Never upload real client documents
locally; uploads run production AI services and consume quota. The staff Admin
view needs a login — the local stack runs `DEV_AUTH=true`, so
`/dev/login?as_user=dev@example.test` signs in as owner/admin (route is 404
wherever DEV_AUTH is off).

## Optional: local website preview

Only when testing veritaxiq.com site changes. `website/` is generated output;
the editable source is `website-src/` (Next.js static export):

```bash
cd website-src && npm ci && npx next build   # writes website-src/out/
python3 -m http.server 8088 --directory out   # pick any free scratch port
```

Verify `http://127.0.0.1:8088` renders the landing page. **Never** deploy to
Cloudflare Pages from this skill — that is production and belongs to the
`veritaxiq-prod-deploy` skill.

## Safety

- Do not use `docker compose down -v`; it destroys local Blob/Queue volumes.
- Do not deploy to Azure or modify production resources, including Cloudflare.
- Do not add Storage, Queue, Key Vault, Graph, Entra, or customer settings to
  the host-only AI configuration file.
- Leave the successful local stack running. Remove the temporary worktree only
  after confirming it has no unique changes.
