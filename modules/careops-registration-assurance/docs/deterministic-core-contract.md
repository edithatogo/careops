# Deterministic registration-assurance core — version 0.2 (source only)

**Scope:** offline, fictional-data reference implementation in `modules/careops-registration-assurance`. **Not a production Dataverse backend, regulator data source, security boundary or authority to practise.**

## Interfaces and ownership

1. `identity.WatchBinding` is supplied from a separately authenticated, versioned credentialing owner. It binds an approved source-qualified watch ID, exact regulator and registration number, explicit profession, effective interval and revision. `reconcile_identity` never deduces identity from a name, local employment, a registration-number prefix or an autocomplete result. Missing profession, a conflicting watch, expired binding and duplicate active binding fail closed.
2. `deterministic.validate_contract` validates the bundled exact 1.1 `RegistrationObservation` JSON Schema (checked byte-for-byte against the canonical Conductor source) with a conforming Draft 2020-12 validator and explicit format checking, then checks semantic invariants. The offline ledger accepts *synthetic only* evidence; real-looking registration numbers and non-`test:` watch references are also rejected, independently of the supplied `synthetic` classification; actual data may not be ingested, even if legal/regulatory API access becomes available later.
3. `deterministic.admit_observation` requires the independently supplied `Qualification` and eligible purpose, effective source rights, exact binding and profession, approved native vocabulary, fresh source-as-of time and healthy source. It delegates status interpretation to the existing `assess_qualified` classifier. Positive registration observations never authorise scope or local employment. The qualification object is a **trusted input contract, not proof of authentication**: real source identity and rights are required at a future native boundary.
4. `durable.DeterministicLedger` is an **offline SQLite reference**. `append` accepts an admitted fictional record and expected per-watch ledger revision, with an atomic transaction containing immutable observation history, a current-observation projection and a pending **internal** outbox event. A replay with identical idempotency key/payload returns the original receipt. A changed payload with the same key is rejected. An old/equal-as-of source observation is recorded for audit but cannot replace the latest projection. Every append advances the ledger revision even if it does not change that projection. A crash before commit rolls back history, projection and outbox together.
5. `save_review` and `save_job` persist the existing deterministic reference transitions with version compare-and-swap and append-only event histories. They are *not* an authenticated user review API, a scheduler, email engine or native storage adapter. No `practiceAuthorised` or `emailEnabled` promotion is allowed.
6. `acknowledge_event` is only a local internal consumer receipt. It does not transmit or deliver email, disclose details or mutate the Decisions master. Real ambiguous delivery and external reconciliation require a separately approved adapter.
7. `verify_integrity` and `recovery_manifest` check the hash chain, current projection references and offline recovery counts. The hash chain detects accidental corruption; it is not tamper-proof, an external signature, backup or proof of authorised actor identity. Recovery quarantines external effects until native reconciliation.

## Error and isolation rules

- Invalid source/identity/purpose/mapping/permission ⇒ **held, not persisted**. A developer cannot label an ordinary HTTP result or five-result name suggestion as verified registration.
- A bad or unknown schema version cannot be silently interpreted using a more privileged version.
- A recognised *adverse* fact is a human verification candidate, never revocation of credentialing, employment, roster or scope.
- Uncertain currentness, missing professional category, conditions, a non-practising registration, provisional/limited categories and expiry are held for review.
- Source/provider health and time constraints are enforced before an assessment becomes eligible for the test ledger.
- SQLite is intentionally a local test implementation, **never a selected production dependency**; migration to native Dataverse/Power Platform must reproduce and adversarially verify these invariants against actual native permissions, retries, transactions and recovery.

## Verification

The source-only test harness checks: homonyms and exact identity; active cross-facility conflicts; source contract/version/quality rejection; historical and duplicate replay; source time conflicts; optimistic concurrency across connections; transaction rollback; append-only SQL guards and chain integrity; versioned reviewer and job persistence; internal outbox reconciliation; and recovery without automatic sends.

Use the repository's exact Python 3.15.1 environment and hash-locked dependencies:

```bash
python -m pip install --require-hashes -r requirements-ci.lock
python -m unittest discover -s modules/careops-registration-assurance/tests -p 'test_*.py' -v
```

Tests prove only fictional, offline behaviour. Native Dataverse integration, real source connectivity, AHPRA PIE contract/auth/XML mapping, staff data classification, licensing/retention, operational identity, security/restore exercises and silent pilot remain outside the completion claim.

**Track linkage:** [REGASSURE-20261113](../../../conductor/tracks/registration_assurance_20261113/plan.md), specifically RA-T04–13. G2 and G3 remain open.
