# PPG: implementation plan

Status: Complete. CareOps maintains the reconciled module and the public predecessor is archived. The phase checklist is the historical migration proposal. The two dated receipts below record the executed scope.

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

## Direct-source implementation

CareOps imports the public PPGWorkbench revision 5d4f1111 under modules/careops-ppg, including its locks, licences and fictional tests. Parent CI builds and exercises the standalone package and retains provenance and SBOM attestation on main. The child repository remains available as migration history. Native workflow acceptance and the first genuine non-owner staff submission remain separate.

## Closeout, 3 November 2026

- **Delivered.** CareOps PR #235 imported PPGWorkbench at 5d4f1111. CareOps owns delivery of that snapshot. The [main package run](https://github.com/edithatogo/careops/actions/runs/41436758840) passed on 18e1b989.
- **Recovery verified.** In a disposable clone, reversing the import reproduced the entire tree of parent 76c72484, including the 5d4f1111 gitlink. A separate mirror of the child was bundled with all fetched refs and restored into an empty mirror. Ref comparison and full Git object verification passed, including child main at 3394f864. The bundle is held outside tracked source.
- **Consumers checked.** A GitHub account code search for the child slug returned four indexed files across the parent and child. Parent provenance and the portfolio validator intentionally identify the import source. The two package workflow copies verify the historical child signer. Only the root workflow directory runs in each repository. Older parent delivery receipts retain their contemporary URLs. No published child GitHub releases were listed. External or unindexed consumers are outside this inventory.
- **Workflow disposition.** The child still lists package, reusable security, security, privacy, development canary and external catalogue workflows plus GitHub dependency updates and graph jobs. Parent package delivery is verified. The child is still receiving changes, so its workflows remain with its current source owners.
- **Open archival dependency.** Child main contains six later merged changes, PRs #109–114, covering Registry binding protection, references, PDF inspection and publisher origins. No open child PRs were listed at inspection. Reconcile these edits and confirm writer handoff before retiring child automation or changing visibility. [Exact child range](https://github.com/edithatogo/PPGWorkbench/compare/5d4f1111...3394f864).
- **Production acceptance open.** Await the first genuine non-owner staff upload, then verify its file opens on the intended Registry record, its separate Review Queue case exists and the earlier edition is preserved.

## Final handoff and archival, 3 November 2026

CareOps owns the module and its release workflow. [PR #238](https://github.com/edithatogo/careops/pull/238) reconciled child PRs #109–114 through 3394f864, retained the parent inventory adaptation, and fixed direct CLI invocation and partial-output cleanup during review. CareOps main at 92aec042 records that child revision across its source provenance and portfolio. The [main package build and attestation](https://github.com/edithatogo/careops/actions/runs/41543016144) passed.

Before archival, the child still pointed at 3394f864 with no open PRs or pending runs. All advertised refs matched the restored recovery mirror. The child homepage now points to the maintained CareOps module. Repository Actions were disabled and verified before archival. GitHub then reported the child archived with its existing public visibility. A fresh ref listing from the archived remote matched the backup, including its main commit. The historical proposal for a visibility change was superseded by archival in the existing visibility.

The first genuine non-owner production upload remains open. After staff submit, verify the edition opens on its Registry record, its Review Queue case is distinct, and its predecessor edition is preserved.
