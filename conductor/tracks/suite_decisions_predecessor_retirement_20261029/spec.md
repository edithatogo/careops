# Decisions: private predecessor reconciliation and retirement

Status: specification approved for planning on 29 October 2026; chore/refactor. Implementation has not started.

## Overview

Review private `careops-decisions` work, carry relevant reusable changes to the already established active owner/successor or an explicitly owned CareOps work item, then retire that private predecessor as a recoverable archive. `careops-decisions-public` remains an independently maintained source repo and its existing parent gitlink is unchanged by this track.

## Requirements

1. Reuse the Decisions migration and Clinical Hub boundary records. The observed private queue has nine open PRs; refresh the exact list/head/source owner once at execution, including the confirmation-concurrency and privacy/approved-connection changes.
2. Give every human/bot PR an explicit disposition: equivalent/already carried, eligible protected merge, scoped reusable port with origin, superseded update, retained private/native implementation or named-owner deferred work. Preserve PR refs and private discussion/history; no bulk private-history/operational-context import.
3. Prefer carrying a generic approved improvement to its established active source owner. Do not unify meeting/governance models, move an authoritative register, create a second Clinical Hub writer or infer deployment approval.
4. Merge an original PR only when relevant, owned and its required current-head checks actually pass. If private CI is billing-refused, keep the result not executed; no forced merge. A documented scoped port/supersession or explicit retained private disposition may replace an unnecessary predecessor merge.
5. Verify source/work recovery and canonical links; finish any source-dependent in-flight operation at the existing owner's checkpoint. Future native work remains owned and may continue separately.
6. Archive only the private predecessor after all required dispositions/carryover and recovery are accepted. Record repo identity, original/final refs, private/archive readback and authorised recovery. Do not change public Decisions visibility, source/pin or native bindings as an incidental retirement.

## Acceptance criteria

- [ ] Every predecessor PR/issue/active branch has a recoverable parent/successor/private disposition.
- [ ] Relevant reusable changes are qualified at their exact destination revision; no required check or governance boundary is weakened.
- [ ] The active public Decisions source and Clinical Hub ownership remain intact; no new runtime dependency or public module absorption occurs.
- [ ] The original is verified private and archived with preserved refs and recoverable private operational history; no ongoing native object is moved or changed.

## Sequence

Reconciliation can proceed alongside the first Finance/Costing planning wave with an independent owner. Actual carryover/archival waits for its own gates; it does not insert a new public Decisions migration into the six-module order.

## Shared boundaries

- Current reusable source only; no import of private Git history, operational exports, private evidence, credentials or enterprise configuration, even though CareOps is now private.
- Preserve standalone package/solution boundaries, module-owned tests, exact locks and optional integrations; repository consolidation does not transfer business-record authority.
- Python execution uses the actual repo-local exact 3.15.1 pin, with isolated qualification and no replacement of environments used by live jobs. Reconcile active manifests/locks/CI for the selected module; preserve historical literals only as evidence or deliberate fixtures.
- Apache-2.0 for project-owned code; retain full upstream/third-party licences, notices and separate external-data rights. Do not relabel third-party material.
- One writing chat per actual worktree, one repository integrator, and terminal handoffs from existing source/native owners. Do not copy a shared dirty checkout, remove locks, replace indexes, or move another lane's changes.
- Keep ordinary hooks enabled. Planning does not reinstall shared hooks, promote runtime/dependencies, advance pins or mutate remote repositories.
- No native deployment, authentication renewal, permission changes, real operational processing, communications, flow activation or email sends. Existing stopped flows, bindings, mutation journals and recovery remain with their owners.
- Encryption/storage changes, history rewriting and CareOps Sim work are excluded. Existing unrelated source/pin guards remain unchanged; do not materialise Sim for this track.
