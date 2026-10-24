# Clinical Hub migration implementation plan

Status: in progress — 24 October 2026. CareOps is the selected source destination.
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
- [ ] CLINICAL_HUB2.4 Publish through reviewed PR/current-head hosted checks and read back merged canonical source. Local checks alone do not close this step.

## Phase 3: Synchronisation and archive

- [x] CLINICAL_HUB3.1 Retain all existing capability dispositions and fictional contract/recovery tests; index completed and remaining meeting/DDMS work through the module index and private operational registry. Do not reopen completed development or copy private records into public plans.
- [ ] CLINICAL_HUB3.2 Verify byte-level import accounting and scoped source-package contents; rehearse source rollback against the recorded CareOps preimage in a disposable clone.
- [ ] CLINICAL_HUB3.3 Recheck source/remote heads, working changes, open PRs/issues and private continuity after integration; synchronize the user's canonical CareOps checkout without disturbing other worktrees.
- [ ] CLINICAL_HUB3.4 After the above passes, archive the selected old remote and read back its archive flag. Existing private predecessor is already archived. No tenant, permission, delivery or operational cutover follows.

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
Hosted integration, clean-clone/package/rollback and remote archive remain open.
