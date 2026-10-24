# Clinical Hub migration implementation plan

Status: complete — 24 October 2026. CareOps is the selected source destination.
The user's full migration/archive request supersedes the earlier optional-gitlink
mechanism. Other modules and native ownership retain their existing boundaries.

## Phase 1: Source selection and preservation

- [x] CLINICAL_HUB1.1 Select hosted public main `dc7d47af62974ff768c9a715897a16f079b774b7`; its domain and source-package workflows passed. Preserve all 133 tracked source paths.
- [x] CLINICAL_HUB1.2 Review public/private boundary and attribution. No upstream licence declaration exists; migration asserts no new licence. Import source only, never old private history.
- [x] CLINICAL_HUB1.3 Include reviewed local Outlook guide/README changes. Preserve all fetched refs and every linked worktree patch/untracked source in a verified private recovery bundle/snapshots; unmerged candidates are not promoted.
- [x] CLINICAL_HUB1.4 Preserve the external operational store, full Conductor registry, native receipts, archived/completed development and open roadmap. Verified private snapshot covers 6,480 files; originals remain authoritative and writable.

## Phase 2: Integrated source and continued development

- [x] CLINICAL_HUB2.1 Integrate regular files at `modules/clinical-hub-core`, retain original file hashes/provenance and update parent catalogs/publication inventory. This replaces a gitlink.
- [x] CLINICAL_HUB2.2 Port domain tests, candidate maintenance and attested source release to root workflows; retain Python 3.15.1/hash lock and parent security controls. Scope module validation/packaging to its own files; preserve parent hooks.
- [x] CLINICAL_HUB2.3 Qualify integrated source with `make ci audit`, parent publication/portfolio checks and focused nested-release/standalone tests. Verify actual clean checkout without sibling modules.
- [x] CLINICAL_HUB2.4 Publish through reviewed PR/current-head hosted checks and read back merged canonical source. Local checks alone do not close this step.

## Phase 3: Synchronisation and archive

- [x] CLINICAL_HUB3.1 Retain all existing capability dispositions and fictional contract/recovery tests; index completed and remaining meeting/DDMS work through the module index and private operational registry. Do not reopen completed development or copy private records into public plans.
- [x] CLINICAL_HUB3.2 Verify byte-level import accounting and scoped source-package contents; rehearse source rollback against the recorded CareOps preimage in a disposable clone.
- [x] CLINICAL_HUB3.3 Recheck source/remote heads, working changes, open PRs/issues and private continuity after integration; synchronize the user's canonical CareOps checkout without disturbing other worktrees.
- [x] CLINICAL_HUB3.4 After the above passes, archive the selected old remote and read back its archive flag. Existing private predecessor is already archived. No tenant, permission, delivery or operational cutover follows.

## Work continuity

[Module migration/continuity](../../../modules/clinical-hub-core/MIGRATION.md)
and [capability index](../../../modules/clinical-hub-core/conductor/index.md)
retain source plans. Full operational plans and evidence stay in the external
private workspace, exposed locally through ignored compatibility links.
The same native objects, human edits, history and owners remain authoritative.
Optional structured generation/body refresh and real rollout remain at their
recorded scope; source consolidation does not change their acceptance status.

The migration includes all current public main source plus reviewed working
changes. Superseded branches, candidate locks, private history and operational
files are preserved as recovery evidence, not silently adopted or published.

Local qualification: Python 3.15.1; 944 domain tests and 13 subtests passed;
dependency audit found no known vulnerabilities. Focused nested module/source
checks passed 8 tests; parent publication and delivery tests passed 5 each.
Parent PowerShell portfolio validation, staged Gitleaks and workflow actionlint passed.
These local results are retained; the final hosted/package/archive verification is recorded below.

Clean-clone verification: all imported hashes matched, 136 regular module files
were packaged with no sibling modules/private links; source rollback exactly
restored the preimage tree. Standalone source was extracted only after package
completion into its own disposable checkout and selected Python environment.

## Verified closeout — 24 October 2026

[PR123](https://github.com/edithatogo/careops/pull/123) merged normally as
`3935494b8e14530eef7ff9b315cbf43f5f285ae6` after all applicable current-head
checks passed and both review findings were fixed. Main domain, publication and
security checks passed. The canonical local CareOps checkout was fast-forwarded
to that merge with its prior clean qualification branch preserved; source hashes,
private compatibility links and selected Python 3.15.1 were verified. The legacy
Clinical Hub path now resolves to the integrated module; the original checkout
remains preserved with its reviewed working changes. Use the CareOps root index
for portfolio Conductor status; the module index retains capability detail.

[Hosted package run 40068559197](https://github.com/edithatogo/careops/actions/runs/40068559197)
passed source checks, attestation and exact-repository/workflow/commit signature
verification. The downloaded archive was independently verified: 136 regular files,
all file digests, archive/SBOM digests, and equality of the downloaded SBOM with
the signed SPDX predicate. Standalone selection passed 29 tests without siblings.
The first extraction attempt began before the archive build finished; that partial
directory was discarded as evidence, and the complete archive was then extracted
into a fresh directory before the reported successful checks.

Final source recheck found unchanged child main and no open PRs. All fetched refs,
linked-worktree changes, 9 ignored local files/links, 6,480 private-workspace files
and a full mirror of the private predecessor remain in private recovery storage.
The original external operational store remains authoritative and unchanged.
The dependency-dashboard issue remains preserved with the archived remote; active
update discovery is in the parent. No unmerged candidate is silently promoted.

GitHub readback verified both `edithatogo/clinical-hub-core` and the renamed private
predecessor `edithatogo/clinical-hub` as **PRIVATE and archived**. The older
`chhhs-clinical-hub` reference resolves to that private predecessor. Source archive
is complete; native rollout, optional integrations and remaining document-route
limitations retain their existing separate dispositions. No tenant write or email
was performed. All reusable source and public planning are in CareOps; confidential
records/history are deliberately preserved outside this public repository.
