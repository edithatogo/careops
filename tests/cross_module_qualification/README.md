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

## Frozen interface dependency

The initial evidence target is CareOps `main` at `11f5b224fdd0263cc9ec7f27441231eb72674a24`. Registration assurance PR #326 and the medical job-planning follow-on PRs may change interfaces. Re-run against each accepted exact head before treating these tests as integration evidence. No interface is considered authenticated merely because its source-only function accepts a caller-supplied flag or reference.
