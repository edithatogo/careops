# Finance: staged direct-source consolidation and private archival

Status: specification approved for planning on 29 October 2026; chore/refactor. Implementation has not started.
Proposed track ID: `suite_finance_direct_source_20261029`. Sequence: 1 of 6. Source `careops-finance-public`; destination `modules/careops-finance`.

## Overview

Use the already composed optional submodule as the first stage. Select and verify its exact qualified source revision, then replace that gitlink with ordinary module-owned source at the same intended path in CareOps. Move maintained work and required delivery here, qualify the replacement, then make the replaced repository private and archived. This specification plans that work; it does not execute migration or archival.

## Functional requirements

1. Read the existing `suite_finance_migration_20261018` records and reuse unchanged qualification/provenance rather than reopening completed work. Record exact selected commit objects, source paths and the changed range; a tag object is not a source commit.
2. Obtain the current source owner's terminal handoff, classify every selected path, account for uncommitted work without copying it, and retain private all-ref recovery plus sanitized PR/issue dispositions.
3. Reconcile every open PR in private `careops-finance` before source freeze: already carried, merge eligible with passing checks, port reusable code with provenance, supersede obsolete updates, retain private/native scope, or hand off remaining work explicitly. Never merge everything just to empty the queue.
4. Preserve report-source packaging, period/source reconciliation and the existing finance authority boundary. Reconcile all four observed private predecessor PRs; do not assume build/security drafts are already equivalent to the public successor.
5. Replace the selected gitlink with reviewed ordinary source. Update actual catalogue, inventory, provenance, CI and consumer declarations atomically; replace obsolete gitlink checks with meaningful direct-source/provenance checks. Preserve independent module installation/builds without sibling modules.
6. Move required workflows to the parent's actual workflow directory, preserve meaningful module tests, locks, package contents and provenance/attestation requirements, and remove runtime/build dependence on the soon-private child. Nested workflow files alone are not a working CI migration.
7. Retire redundant child automation only after the replacement is qualified. Record unresolved native/business work with its existing owner; those items may continue after source archival and do not become new implementation gates for optional integrations.
8. Retire both the public successor and the private predecessor only after each has its own verified source/work disposition and recovery record. Recheck repo identity, visibility, refs, active work and required consumers immediately before any state mutation; journal each visibility/archive action and independently read it back.

## Acceptance criteria

- [ ] The existing submodule stage is recorded; the selected module becomes ordinary tracked source at `modules/careops-finance`, with no duplicate source location.
- [ ] All selected paths and open work have a disposition; private material stays with its authorised private custodian and no owned changes are lost.
- [ ] Standalone source/package qualification passes on the selected exact runtime/locks; affected regression tests precede changed executable behaviour. No speed-only skips, new global retries or weakened sensors.
- [ ] Parent inventory/catalogue/consumer/provenance declarations agree; a fresh parent clone builds and tests this module without authenticating to the retired child or requiring siblings.
- [ ] All required checks for the actual parent head execute and pass before protected merge; verify merged main. Billing refusal means not executed and blocks cutover, not a software pass/failure.
- [ ] Exact-source package/provenance parity and source-only reversal are retained; post-archive recovery can use the retained ordinary source/private recovery copy without making the archive public again.
- [ ] The selected old repo is independently verified private and archived, with preserved refs/history and a canonical-development notice pointing to CareOps. Native operations/bindings are unchanged.

## Dependencies and execution order

First direct-source pilot in this sequence; establish the reusable execution/checkpoint pattern in existing project records, not a new service or framework.

## Out of scope

New business features, authority/model unification, native cutover, completing unrelated open native work, broad dependency upgrades, automatic merges/archives during planning, importing historical private material, and public Decisions module absorption.

## Shared boundaries

- Current reusable source only; no import of private Git history, operational exports, private evidence, credentials or enterprise configuration, even though CareOps is now private.
- Preserve standalone package/solution boundaries, module-owned tests, exact locks and optional integrations; repository consolidation does not transfer business-record authority.
- Python execution uses the actual repo-local exact 3.15.1 pin, with isolated qualification and no replacement of environments used by live jobs. Reconcile active manifests/locks/CI for the selected module; preserve historical literals only as evidence or deliberate fixtures.
- Apache-2.0 for project-owned code; retain full upstream/third-party licences, notices and separate external-data rights. Do not relabel third-party material.
- One writing chat per actual worktree, one repository integrator, and terminal handoffs from existing source/native owners. Do not copy a shared dirty checkout, remove locks, replace indexes, or move another lane's changes.
- Keep ordinary hooks enabled. Planning does not reinstall shared hooks, promote runtime/dependencies, advance pins or mutate remote repositories.
- No native deployment, authentication renewal, permission changes, real operational processing, communications, flow activation or email sends. Existing stopped flows, bindings, mutation journals and recovery remain with their owners.
- Encryption/storage changes, history rewriting and CareOps Sim work are excluded. Existing unrelated source/pin guards remain unchanged; do not materialise Sim for this track.
