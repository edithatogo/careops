# Cross-module qualification tests

Independent, synthetic-only adversarial qualification of the public source interfaces in:
- `careops-registration-assurance`: provider qualification, freshness, outage, schema-version and human-review fail-closed paths.
- `careops-medical-job-planning`: rule/contract evidence, issued-record projection, negotiation state and candidate CAS authority boundaries.

This directory is intentionally separate from both module-owned source and tests. It imports only their published Python interfaces; it does not patch module internals, alter module tests, shared CI, Conductor ownership or runtime configuration.

## Run

From the repository root with the repository's pinned Python 3.15.1 environment:

```sh
python -m unittest discover -s tests/cross_module_qualification -p 'test_*.py' -v
```

Inputs are fictional `test:` references only. Passing means the currently checked source interfaces preserve these tested negative boundaries; it is not provider, tenant, identity, physical ACL, policy-adoption, native deployment or operational qualification.

## Frozen interface dependency and source hashes

The test base is CareOps `main` at `11f5b224fdd0263cc9ec7f27441231eb72674a24`; the repository pin is Python `3.15.1` (`.python-version`).

Before execution, the latest available registration-assurance implementation branch for PR #326 was reconciled against `main`. The public interfaces imported here are byte-identical across those refs:

| Interface | Git blob ID |
|---|---|
| Registration `qualification.py` | `94d3194bb36a6df39aa55b4b829aae09f7f8da13` |
| Registration `assurance.py` | `98501b81749c9580969e9e6f11ab4b15bcaecf88` |
| MJP `policy_rules.py` | `1fbd08d0304b28f364ae3bd74e65573acfac45e9` |
| MJP `plan_records.py` | `018f90dfb3228d4ec8c12295e2ebfe1372dd7905` |
| MJP `negotiation.py` | `453b410400322171eff98f45d5c2431330864e3a` |
| MJP `cas_contract.py` | `e4e213d779f35893ca7a33b13b93f0628e1dbdff` |

The registration package `__init__.py` differs on the PR #326 branch, but these tests import the explicit `registration_assurance.qualification` and `registration_assurance.assurance` modules, whose blobs are unchanged. Re-run against each accepted exact head before treating these tests as integration evidence. No interface is considered authenticated merely because its source-only function accepts a caller-supplied flag or reference.
