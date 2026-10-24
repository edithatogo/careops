# Clinical Hub migration implementation plan

Status: source migration, historical reconciliation and connected source integration complete — 24 October 2026. CareOps is the selected source destination.
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

## Phase 4: Historical and functional integration — user-selected extension

The earlier closeout verified source migration/preservation, not reconciliation of
every historical implementation or a connected capability journey. The user now
explicitly requests that additional integration. Preserve the earlier evidence.

- [x] CLINICAL_HUB4.1 Account for every historical source ref, private-main source/helper and unfinished track; classify absorbed, superseded, portable useful work, native/private-only work and genuine remaining prerequisites. Retain detailed private evidence and a sanitised public disposition.
- [x] CLINICAL_HUB4.2 Integrate useful missing pure helpers and explicit-binding graph builders with fictional tests; preserve exact native originals and authoritative business logic. No private history/data/bindings or new document runtime.
- [x] CLINICAL_HUB4.3 Exercise one connected source/paper/agenda/minutes/review/follow-up/recovery journey and the separate DDMS contribution boundary through actual helpers. Verify identity/version drift, held/closed exclusions, retries, human edits, absence paths and no unintended writes.
- [x] CLINICAL_HUB4.4 Run affected checks then full module integration/audit and parent privacy/security gates. Publish through protected PR/current-head checks, synchronize canonical main and record source versus native limits. Archived remotes remain private/archived.

Functional reconciliation: see [all-source dispositions and connected test scope](../../../modules/clinical-hub-core/conductor/historical-integration.md).
The portable slice passed full integration/audit and protected hosted publication.
Native/operational limitations are explicitly retained.

## Functional integration closeout — 24 October 2026

[PR126](https://github.com/edithatogo/careops/pull/126) merged normally as
`3acadc75cc676956679463e85a0e74b98a5a0e94` after all applicable current-head
checks passed with no unresolved review threads. The latest parent source pins
were merged before qualification. Canonical main and existing private links were
verified after merge; the selected repo-local interpreter reported Python 3.15.1.

Final hardened implementation passed 1,007 tests/13 subtests and a clean dependency
audit. Five private/public transformation boundaries were compared with fictional
inputs; the public native write template intentionally adds async immutable-byte
and changed-retry guards. Private governance passed 158 fictional tests separately.
The standalone initial integrated slice passed 63 focused tests without siblings;
affected tests and hosted full checks qualified the subsequent guard hardening.

[Package run 40072398921](https://github.com/edithatogo/careops/actions/runs/40072398921)
qualified implementation commit `3acadc75cc676956679463e85a0e74b98a5a0e94`.
Downloaded 149-file archive/SBOM digests and both attestations were independently
verified against the exact repository, workflow, source and signer commit. This
is immutable implementation evidence; later closeout metadata does not relabel
that artifact as another commit.

All 68 core refs, 4 linked worktrees, 1 private branch/506 tracked entries, 53 helpers,
20 plans and 387 pending/in-progress historical tasks have dispositions. Detailed
private task/source accounting remains outside public Git. Six absent historical
skill links and their exact pinned plugin were recovered privately; detached
worktree heads also have explicit recovery refs and a verified bundle. Useful
missing source was ported; redundant/obsolete tooling and unselected broader
roadmap work retain explicit dispositions rather than becoming new runtimes.

This closes source/helper integration and its connected fictional qualification.
It does not claim completion of every historical operational checkbox, a new
live cross-flow run, recording/processing authority, intended-role access, real
register cutover or distribution. Existing exact native bindings, private data
and human work remain in their authoritative store. No tenant write, recording,
authentication repair or email invocation was performed. Both replaced remotes
remain private and archived.
