# CareOps registration assurance — source-only prototype

**Status:** initial pure-logic source slice; not production, regulator verified or tenant deployed.

The module implements a deterministic **source-only reference model**, not an operational monitoring app:

- `assurance.py`: source-evidence assessment, temporal safety, in-memory replay and engagement watch coverage.
- `qualification.py`: trusted-provider profile/purpose/vocabulary/freshness capability gate; the production adapter must authenticate the actual agreement and source identity independently.
- `review.py`: material-change idempotency, versioned human disposition and immutable review history; authorisation and storage-side compare-and-swap remain native obligations.
- `jobs.py`: retry/lease/dead-letter/ambiguous-delivery and internal outbox reference protocol; **not** a real scheduler, transactional store or mail sender.
- `evaluation.py`: synthetic-only prospective silent-pilot confusion matrix, abstention/missingness handling, rare-event Wilson intervals and conservative population-prevalence qualification.

No source transport is implemented, and all examples are fictional. It has **no network I/O, API credentials, email, scheduled job, Dataverse access, personnel store, protected credentialing write, or scope-of-practice determination**. Its source-qualified provider labels are not authentication: a production provider adapter must enforce the organisational agreement, genuine source identity, data rights, versioned native mapping, schema validation and human review.

The original uploaded AHPRA monitoring v3.1 archive is not imported. This code is independently written from the new CareOps contract and entirely synthetic test cases. The source admission decision explicitly rejects importing old autocomplete polling, Excel watch masters or competing Power Automate/Logic Apps writers.

## Focused synthetic tests

From the **CareOps repository root**, with its exact pinned Python 3.15.1 environment:

```sh
python -m pip install --require-hashes -r requirements-ci.lock
python -m unittest discover -s modules/careops-registration-assurance/tests -p 'test_*.py' -v
python -m compileall -q modules/careops-registration-assurance/src modules/careops-registration-assurance/tests
```

The PR workflow is configured to run **87 synthetic unittest methods**, including six Hypothesis property/metamorphic tests (many generated cases), under the repository's selected Python 3.15.1 and hash-locked CI dependencies. The preceding 75-method current-head source suite passed in Python 3.15.1 before the present evaluation tests were added. The current-head execution status must be checked in GitHub before claiming the expanded set passed. A green source-only workflow is not native AHPRA or tenant qualification. Required exact-head GitHub workflows and native Microsoft/AHPRA/rights/tenant checks remain separate.

## Contract boundaries

- [Integration contract](../../docs/credentialing/registration-assurance-integration-contract.md)
- [Conductor track](../../conductor/tracks/registration_assurance_20261113/index.md)
- [RegistrationObservation 1.0/1.1 schema](../../conductor/tracks/registration_assurance_20261113/registration-observation.schema.json)
- [Safety case](../../conductor/tracks/registration_assurance_20261113/clinical-safety-case.md)
- [Engagement coverage and evaluation](../../conductor/tracks/registration_assurance_20261113/engagement-coverage-and-evaluation.md)

`source_verified` is a qualified **observation classification only**, not proof of suitability or approved practice. A restricted, provisional, limited, non-practising, unknown, expired or suspended source observation requires human attention. `assess_engagement_coverage` counts enabled watch links, **not verified registration or scope of practice**. The in-memory reconciler is an algorithmic reference; a future native implementation needs durable transactional history, protected writes and replay controls.

This module is not yet a managed Power Platform solution. Microsoft tenancy, retained evidence, field permissions, credentials, production scheduling, recovery and support cannot be inferred from these source files.

## Source admission, privacy and delivery boundary

- [Source provenance](SOURCE_PROVENANCE.json) confirms only independent synthetic reference logic has been admitted; the original v3.1 archive has **no located licence**, contains nine Python scripts with author-specific absolute paths, and has not been imported.
- [Module profile](.careops/module.json) declares no live provider, no production writes, no automatic email and no installed sibling dependency.
- Do not construct `Qualification` from an untrusted request or treat the source `qualificationRef` string as proof of authorisation. A deployed adapter must obtain an independently authenticated/approved configuration, enforce allowed use and source identity, and validate the versioned envelope **before** invoking these reference functions.
- Source `ReviewCase`, `CheckJob` and `outbox` are immutable transition *examples*: a native Dataverse/approved service boundary must enforce authentication, atomic versions, durable history, retry/readback and records retention.
- Current source approval is separate from installation and clinical commissioning. PIE XML/auth/schema, source rights, native solution/tenant roles, silent pilot, staff notification policy and credentialing authorisation all remain external gates.
