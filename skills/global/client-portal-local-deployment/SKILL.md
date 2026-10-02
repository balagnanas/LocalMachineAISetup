---
name: client-portal-local-deployment
description: Deploy and verify the Client Portal on the local Ledger IQ stack at localhost:8000/portal. Use when asked to deploy, refresh, or verify the local Client Portal; the portal ships inside the shared Ledger image and needs no separate image or port.
---

# Client Portal local deployment

The Client Portal is **not** a separate app or image. It is routes inside the
FastAPI monolith (`webapp/app/client_portal_routes.py`): the client surface at
`/portal` and the staff console at `/admin/client-portal`. Whatever image the
local Ledger stack runs already contains both.

Consequences you must respect:

- **One image, one pipeline.** Deploy the portal by deploying the local Ledger
  stack (`scripts/deploy-ledger-local.sh <sha>`). Never build a portal-specific
  Docker image, compose project, or state directory.
- **No separate port.** The portal is `http://localhost:8000/portal` on the
  persistent CI-verified dev stack (`8001` stays reserved for the isolated
  feature stack). Never run the app natively on `8002`/`8003`; if those ports
  are held by stray `gunicorn`/`uvicorn` processes, stop them with
  `kill <pid>` after `lsof -nP -iTCP:8002 -sTCP:LISTEN` (and `8003`), then
  re-check they are free.
- **Prod differs only by hostname.** In production the portal is served at
  `client.veritaxiq.com` via the host-redirect middleware in
  `webapp/app/main.py`. Locally that middleware is inert — clients use
  `/portal` directly. Do not hardcode or fake the prod hostname locally.

## Deploy

Follow the `ledger-local-dev-deployment` skill: fetch `origin/dev`, confirm a
successful `ci.yml` run for that exact SHA, then deploy from a clean detached
worktree. There is nothing portal-specific to configure; the portal deploys
with the stack.

## Verify

After the stack deploys, independently check the portal surfaces:

```bash
curl --fail http://127.0.0.1:8000/healthz
curl --fail http://127.0.0.1:8000/readyz
curl --fail -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/portal
curl --fail -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/admin/client-portal
```

Require `200` from both portal routes (the `/portal` page must identify as
`Veritax IQ — Client Portal`) alongside healthy `/healthz` and `/readyz`.
Report the deployed SHA, image digest, and portal verification result.
Optionally smoke-test the client upload flow with a synthetic file through
`/portal` under dev auth — never a real client document.

## Safety

- Same rules as the Ledger local deployment: no `docker compose down -v`, no
  Azure or production changes, no customer data on localhost.
- Do not expose the portal on an extra port or split it into its own stack;
  consistency with the shared `veritax-web` topology is the point.
