# Release evidence

Capture these facts for every Veritax IQ production release:

- exact `master` commit and successful CI URL;
- deployment workflow URL and selected target;
- immutable image digest and active revision/image;
- traffic allocation and health state;
- for Ledger: statement-worker template digest, one-off healthcheck execution, and readiness heartbeat digest;
- public `/healthz` and `/readyz` result, including any degraded optional component;
- rollback result if the deployment did not complete.

Do not claim deployment complete from a Git merge, image build, or GitHub Actions job alone.
