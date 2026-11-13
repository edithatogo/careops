# CareOps registration assurance — source-only prototype

**Status:** initial pure-logic source slice; not production, regulator verified or tenant deployed.

The code in `src/registration_assurance/assurance.py` implements a deterministic **reference model** for comparing already-authorised registration observations and measuring engagement watchlist coverage. It has **no network I/O, API credentials, email, scheduled job, Dataverse access, personnel store, protected credentialing write, or scope-of-practice determination**. Its source-qualified provider labels are not authentication: a production provider adapter must enforce the organisational agreement, genuine source identity, data rights, versioned native mapping, schema validation and human review.

The original uploaded AHPRA monitoring v3.1 archive is not imported. This code is independently written from the new CareOps contract and entirely synthetic test cases. The source admission decision explicitly rejects importing old autocomplete polling, Excel watch masters or competing Power Automate/Logic Apps writers.

## Focused synthetic tests

From the **CareOps repository root**, with its exact pinned Python 3.15.1 environment:

```sh
python -m pip install --require-hashes -r requirements-ci.lock
python -m unittest discover -s modules/careops-registration-assurance/tests -p 'test_*.py' -v
python -m compileall -q modules/careops-registration-assurance/src modules/careops-registration-assurance/tests
```

The focused source-only logic tests were initially exercised on Python 3.13.5; the PR workflow runs the full synthetic and Draft202012/format-validation test set on the repository's selected Python 3.15.1 and hash-locked CI dependencies. A green workflow is still not native AHPRA or tenant qualification. Required exact-head GitHub workflows and native Microsoft/AHPRA/rights/tenant checks remain separate.

## Contract boundaries

- [Integration contract](../../docs/credentialing/registration-assurance-integration-contract.md)
- [Conductor track](../../conductor/tracks/registration_assurance_20261113/index.md)
- [RegistrationObservation 1.0/1.1 schema](../../conductor/tracks/registration_assurance_20261113/registration-observation.schema.json)
- [Safety case](../../conductor/tracks/registration_assurance_20261113/clinical-safety-case.md)
- [Engagement coverage and evaluation](../../conductor/tracks/registration_assurance_20261113/engagement-coverage-and-evaluation.md)

`source_verified` is a qualified **observation classification only**, not proof of suitability or approved practice. A restricted, provisional, limited, non-practising, unknown, expired or suspended source observation requires human attention. `assess_engagement_coverage` counts enabled watch links, **not verified registration or scope of practice**. The in-memory reconciler is an algorithmic reference; a future native implementation needs durable transactional history, protected writes and replay controls.

This module is not yet a managed Power Platform solution. Microsoft tenancy, retained evidence, field permissions, credentials, production scheduling, recovery and support cannot be inferred from these source files.
