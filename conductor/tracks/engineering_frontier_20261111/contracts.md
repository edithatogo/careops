# Engineering acceptance contracts

These are source acceptance contracts for the proposed engineering tools, not implemented APIs. Reuse existing module contracts and source validators; add machine-readable schemas during implementation.

## EF-C01 — Task/context packet

```json
{
  "schema_version": "1.0.0",
  "source": {"repo": "edithatogo/careops", "commit": "<40-hex-sha>"},
  "task": {"id": "EF-02.02", "module": "careops", "mode": "read-test", "changed_paths": ["harness/"]},
  "context": [{"path": "AGENTS.md", "sha256": "<hex>", "purpose": "source guidance"}],
  "contracts": [{"owner": "careops", "id": "EF-R02", "version": "1"}],
  "tests": [{"command_id": "parent-targeted", "resource": "small"}],
  "tools": {"allow": ["repo:read", "runner:focused-test"], "deny": ["tenant:write", "email:send", "protected-merge"]},
  "classification": "synthetic-source-only",
  "prohibited_effects": ["email-delivery", "tenant-mutation", "unreviewed-publication"]
}
```

Schema invariants: no floating SHA; no wildcard permissions or actor-defined policy; no path outside selected source roots; module owner is selected by registry; missing classification is denied; hashes are verified before context use. The packet may point to existing full documents; it must not duplicate sensitive content or preserve secrets.

Acceptance: valid task passes offline. Wrong owner, stale commit, missing field, path traversal, injected instructions and unexpected permission each fail with a stable machine-readable code. Running an AI-free task is mandatory; a model provider is never required.

## EF-C02 — Execution and authority boundary

Tool policy resolves a request using typed `actor`, `source_sha`, `target_kind`, `target_identity`, `operation`, `allowed_paths`, `classification`, `risk_tier`, `approved_scope` and `expiry`. Enforcement is outside the agent. Read-only operations have no account setup or write side effects. Local patch writes require an isolated branch and allowed files. Tenant writes/flow enablement/email sending remain forbidden unless existing explicit native owner authorization is independently verified; Conductor task text cannot authorize it.

Acceptance: deny on missing/expired scope, implicit profile selection, environment drift, invalid actor, unrelated path, cross-tenant redirect, nested-tool privilege escalation and replay. An agent cannot approve its own scope elevation. Return only a safe denial code and a redacted reference, never tool secrets.

## EF-C03 — Test and evidence receipt

```json
{
  "schema_version": "1.0.0",
  "source_sha": "<40-hex-sha>",
  "task_id": "EF-04.03",
  "test_target": "source-contract-replay",
  "toolchain": {"python": "<exact>", "runner": "<exact>"},
  "fixture_digest": "<sha256>",
  "execution": {"status": "executed", "result": "pass", "count": 0, "skipped": 0},
  "qualification": "local-source",
  "artifact_digest": "<sha256-or-null>",
  "limitations": []
}
```

Allowed status vocabulary: `pending`, `executed`, `cancelled`, `refused-billing`, `unavailable`, `unverified`. `result` is `pass`, `fail` or `not-executed`. `pass` is impossible unless the recorded command/runner completed successfully; a CI green check with domain steps skipped cannot qualify the domain. Bind each receipt to the actual input SHA, test set and artifacts. Source acceptance is not native acceptance.

Acceptance: parse/classify synthetic GitHub outcomes, particularly no-step billing refusals, partial executed failures, changed-head results, skipped tests and stale artifacts. Never infer success from an empty/partial API response.

## EF-C04 — Non-premium module interface

Each core module declares required and optional connector capabilities, licence class, install mode, supported platform/SDK versions, data authority and an explicit `without_ai` parity test. The package linter inspects *actual authored Power Platform source* rather than narrative claims.

Acceptance: core with only standard permitted connectors packages normally; unknown, premium, custom-connector or implicit Dataverse dependencies fail the core admission gate. Optional premium packs are separately packaged and have absent-provider tests. No live tenant access needed for the source contract.

## EF-C05 — Security/privacy and supply-chain verification

The shared source guard enumerates inspected text and container/file classes, included/omitted paths, parser gaps, reviewed finding IDs, changed source identities, dependency locks and build inputs. Review exceptions bind a precise finding/fingerprint, reason and expiry. Source files, archives, notebooks and generated artifacts are evaluated where practical, with explicit declared exclusions. Detection is not equivalent to complete clinical de-identification.

Acceptance: known synthetic secrets, personally identifiable strings, split/encoded forms where supported and embedded Office/archive fixtures are either detected or explicitly reported as unsupported; no raw matches printed. Tampered build member or SBOM mismatch fails. Attestation unavailable is recorded, not asserted.

## EF-C06 — Technical benchmark

One versioned corpus of synthetic tasks includes: routing to correct module, identifying correct test, interpreting a security denial, editing with rollback, duplicate-retry handling, stale-auth source, prompt injection, optional provider absence, schema mismatch, corrupted archive and Power Platform solution source parity. A baseline current-harness run is retained next to each candidate comparison.

Report: exact revision, toolchain, task IDs, executed/skipped cases, correctness, reproducibility, false-safe/false-denied actions, total tools invoked, context tokens when available, and wall time. Critical safety acceptance requires **zero known unsafe actions accepted** in the fixed adversarial corpus, not a broad security guarantee. Do not trade safety against speed or compare model runs with different inputs without disclosure.

## EF-C07 — Release integrity

A candidate is qualified only when its package digests match the actual built bytes, dependency inventory matches the archive, tests execute on the release candidate, and applicable required checks pass on the exact source revision. Record independently downloaded verification. If private account entitlement prevents supported artifact signing, preserve checksum/SBOM provenance and mark cryptographic signature qualification false. Protected merge and native operation remain independent gates.

## EF-C08 — Continuous compatibility

Each cross-module interface gets producer/consumer fixtures and version/absence tests. Invariants: stable source-qualified IDs; same-source retry idempotent; newer incompatible schema explicitly rejected; missing optional dependency does not crash base; classification and data access never broaden; event order and timestamps remain explicable. Compare against the exact selected gitlink/revision, not an unpinned remote branch.
