# Costing: implementation plan

Status: plan approved and registered on 29 October 2026. Implementation has not started; all tasks remain pending.

## Phase 1: Ownership and source freeze

- [ ] Task: Refresh only changed refs/PRs against retained receipts; record current writer, worktree, exact owned paths, native owner and next operation in the existing handoff.
- [ ] Task: Reconcile pending work and select the exact source commit after relevant predecessor/child PR dispositions; retain immutable private recovery and public-safe provenance.
- [ ] Task: Confirm that the module still has the existing submodule stage; do not recreate or duplicate it.
- [ ] Task: Phase verification and checkpoint against `conductor/workflow.md`; retain commands, exact source/runtime/input identities, actual results and the next owner/action. No native acceptance is implied.

## Phase 2: Behavioural boundary and direct-source migration

- [ ] Task: Add affected negative tests for residual gitlinks, missing/mismatched provenance, private content, broken standalone module roots and stale paired declarations before executable guard changes.
- [ ] Task: Import only the reviewed current files at the declared destination; preserve attribution, lock/package boundaries and safe private-profile interfaces.
- [ ] Task: Update real inventory/catalogue/consumer/packaging references and replace obsolete pin assertions in one scoped review unit; leave unrelated modules/pins untouched.
- [ ] Task: Phase verification and checkpoint against `conductor/workflow.md`; retain commands, exact source/runtime/input identities, actual results and the next owner/action. No native acceptance is implied.

## Phase 3: Standalone package and parent delivery

- [ ] Task: Run smallest affected selectors during edits; reuse unchanged receipts. At the coherent milestone run mandatory module integration, clean-package, security and source-release gates.
- [ ] Task: Wire module tests, workflow triggers, minimal permissions, exact tools/locks and required release/provenance behaviour into working parent CI; verify no old-child credential/fetch or sibling prerequisite.
- [ ] Task: Verify an independent clean parent checkout and standalone module package with fictional inputs and existing missing/provider/refusal cases. Preserve native acceptance boundaries.
- [ ] Task: Phase verification and checkpoint against `conductor/workflow.md`; retain commands, exact source/runtime/input identities, actual results and the next owner/action. No native acceptance is implied.

## Phase 4: Protected cutover and recovery

- [ ] Task: Rehearse exact source-import reversal before repository state changes; retain recoverable ordinary-source snapshots/private all-ref backups for post-archive recovery.
- [ ] Task: Require all current-head checks and normal protected merge, then verify actual main/package identities. Stop cutover on billing/signing/required-host limitations without changing protections or purchasing anything.
- [ ] Task: Confirm canonical source/work ownership, active-owner handoffs and every old workflow/release/badge/consumer link. Retire only superseded child automation after replacement proof.
- [ ] Task: Phase verification and checkpoint against `conductor/workflow.md`; retain commands, exact source/runtime/input identities, actual results and the next owner/action. No native acceptance is implied.

## Phase 5: Private archival and final handoff

- [ ] Task: Re-read exact repo identity/visibility/ref stability and absence of an in-flight source writer or native operation dependent on the old source hub.
- [ ] Task: Perform separately journaled private/archive mutations only after the preceding source, delivery and recovery gates; never blindly retry an uncertain native write.
- [ ] Task: Read back private+archived state and preserved refs; verify clean parent build independence and authorised archive readability. Record one terminal deliverable/blocker in the existing module handoff.
- [ ] Task: Phase verification and checkpoint against `conductor/workflow.md`; retain commands, exact source/runtime/input identities, actual results and the next owner/action. No native acceptance is implied.
