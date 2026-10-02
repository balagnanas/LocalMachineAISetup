---
name: incident-rca
description: Produce concise, evidence-backed root-cause incident reports. Use for production incidents, regressions, failed workflows, data-quality defects, customer-impacting failures, and investigations where the user asks for an RCA, diagnosis, root cause, or incident summary.
---

# Incident RCA

Produce a decision-ready report after collecting enough evidence to distinguish confirmed facts from hypotheses. Do not treat an implementation as proof that the incident is resolved.

## Investigate

1. Establish scope: affected environment, tenant/customer only when authorized, component, time window, version/revision, and user-visible impact.
2. Collect primary evidence: reproducible inputs, test output, logs, telemetry, persisted records, source history, or authenticated platform state. Record a precise command, path, query, URL, or timestamp for each material claim.
3. Separate confirmed root cause from contributing factors and hypotheses. State when evidence is unavailable, stale, or insufficient.
4. Verify safeguards with focused tests and, when in scope, the real entrypoint. Do not claim an unrun test or deployment check passed.

## Report format

Use these headings, omitting none:

### Symptom

State observed behavior, impact, scope, and first known occurrence. Link or cite the supporting evidence inline.

### Root cause

Name the confirmed causal mechanism and evidence. Put plausible but unconfirmed factors under **Hypotheses**, not here.

### Affected statements or scope

List precisely affected documents, transactions, tenants, revisions, or workflows when authorized. Otherwise give bounded counts and selection criteria; never expose customer content unnecessarily.

### Safeguards

State the prevention or containment change, the boundary at which it acts, and verification actually run. Say whether it prevents recurrence, detects it, or limits blast radius.

### Remaining gaps

List unresolved evidence, untested paths, monitoring gaps, rollout state, and the concrete next verification. Use `Confirmed`, `Partial`, or `Blocked` status.

## Evidence standard

- Prefer immutable or reproducible evidence over screenshots and recollection.
- Keep evidence proportionate: enough to support each claim without copying sensitive logs or document content.
- Preserve tenant isolation and redact identifiers unless they are already in the approved task scope.
- Update the report after remediation or rollout so its safeguards and remaining gaps reflect current reality.
