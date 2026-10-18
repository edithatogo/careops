# Suite CI/CD implementation

Implement the user's five requirements across CareOps and its owned modules:
1. Qualify current dependency/action updates; automatically regenerate locks.
2. Share reproducible security/CI checks without replacing module-specific tests.
3. Run bounded scheduled preview/development canaries; record exact candidates,
   keep working pins, and promote only through a fully green protected PR.
4. Exercise optional cross-module compatibility and attach SBOMs and build
   attestations to actual release packages.
5. Enforce usable check/update protection; classify billing-blocked execution
   separately from executed failures, pending runs, skipped and passed tests.

Scope: CareOps (including integrated Incidents), Approve, Process, Sim, Finance,
Costing, Decisions, public RIMS/Clinical Hub/PPG and their private implementation
CI definitions where owned. Conductor upstream is reviewed as a third-party
development pin; do not rewrite upstream governance. HWCC is a separate source
reconciliation dependency. CGov/native tenant work remains separate.

All remote actions/reusable workflow references use immutable commit SHAs; peel
annotated tags before comparing. Runtime and package candidates require exact
resolved versions and integrity, meaningful affected tests and source recovery.
No new credential/consent, purchase or production deployment is implied. Reuse
existing federated release routes only. Private CI that cannot start stays blocked
and unmerged; a local pass is not a hosted pass. Preserve existing writers.

Completion requires per-module evidence for all five requirements, actual green
current-head checks before each merge, and verification of adopted workflow calls,
canary results, compatibility fixtures, release SBOM/attestation verification and
protection readback. A policy document/template alone is not implementation.
