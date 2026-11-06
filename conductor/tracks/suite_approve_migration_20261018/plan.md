# careops-approve implementation plan

Status: source composition and independent checkout qualified; optional scenario/interfaces remain open. Priority position: 10.
Existing Approve maintenance may proceed independently; this is not a second import.

## Phase 1: Selection and boundary

- [x] APPROVE1.1 Refresh exact default head/checks with the existing owner; record a stable selected commit and preserve in-flight work.
- [x] APPROVE1.2 This module is already materialised at careops-approve. Maintain its existing pin and existing release contracts; do not create modules/careops-approve or blindly update its version. Generic maintenance may proceed independently.
- [x] APPROVE1.3 Inspect licence/attribution, source/history/privacy and deployment dependencies. Record concrete gaps without inferring public safety from visibility or scanner success alone.
- [x] APPROVE1.4 Checkpoint: record selected standalone slice, exact inputs, ownership and source-only stop conditions here.

## Phase 2: Parent composition and standalone proof

- [x] APPROVE2.1 Validate the existing careops-approve gitlink; update it only for a separately qualified generic release need, preserving credentialing pins unchanged.
- [x] APPROVE2.2 Verify clean parent clone without optional modules and selective child initialization; retain child licence and actual private-access boundaries.
- [x] APPROVE2.3 Run existing focused source/fixture checks and parent publication/portfolio checks; record exact revision, commands and actual results. Do not claim native operation.
- [x] APPROVE2.4 Checkpoint: retain preimage parent SHA, source provenance and supported commands; preserve a failed/missing check rather than marking qualification complete.

## Phase 3: Interoperability and recovery

- [ ] APPROVE3.1 Synthetic intake/routing, duplicate request, human approval, cancellation, recovery and optional provider absence; no autonomous decision or credentialing integration change.
- [ ] APPROVE3.2 Test only selected optional interfaces with provider absent, incompatible version, stale/missing inputs and duplicate retry; preserve authoritative ownership and human edits.
- [ ] APPROVE3.3 Rehearse reverting only the source pin/catalog/CI change in a disposable clone. Native objects/data are not deleted or rolled back by a source-reference reversal.
- [ ] APPROVE3.4 Checkpoint: close only proved source scope; send one consolidated deliverable or genuine blocker to the existing owner, without acknowledgement polling or a new chat.

## Selected source and parent qualification — 25 October 2026

The existing source is `edithatogo/careops-approve`, selected at
`f71c494634a87a9b4145742011070325c9b39c99`, the same commit as its public
`main`. The CareOps parent gitlink, `.gitmodules`, `PUBLIC_SOURCE_FILES.json`,
catalog, and current public runtime compatibility declaration agree on this
pin. The public `credentialing-cross-module.yml` also retains a separate
credentialing release reference (`ec7d7230b0fae3293c7ed51e716074074f83b5bb`);
that explicitly selected integration reference is distinct and was preserved.
No source pin change was needed.

All eight check runs on the selected Approve main commit succeeded, including
repository validation, reference safety, package attestation and shared source
security. The source has an Apache-2.0 `LICENSE` and a `NOTICE` that preserves
third-party and external-source rights. Its README describes environment values,
connection references and identities as deployment configuration that must not
be committed. This qualifies the selected public source and its existing CI
receipt; it does not grant access to private deployment bindings or establish
native operation.

In a fresh public CareOps clone at `11520f5669cc2653d7ad3c84ec943642f48d9b0b`,
`pwsh -NoProfile -File portfolio-scripts/Test-Portfolio.ps1` passed with all
optional children uninitialized. Then
`git submodule update --init --checkout careops-approve` checked out only the
selected Approve commit; sibling optional modules stayed uninitialized. The
pre-existing parent checkout remains uninitialized at the Approve path. This
clone and the selected child were not modified. Future child/source updates
still require their own qualified source need. APPROVE3.1–3.4 remain open for
the optional synthetic scenario, interoperability and recovery slice.

### Existing root reference recheck — 25 October 2026

On CareOps main `4a10d636b9a69b525733e6f5dcc31d9c60156035`, the root
`careops-approve` gitlink is mode `160000` at
`f71c494634a87a9b4145742011070325c9b39c99`. `.gitmodules` identifies the
canonical `edithatogo/careops-approve` URL with updates disabled; the public
inventory, module catalog, repository catalog, ALM record and public runtime
compatibility record agree on the existing root path and source pin. The
separate credentialing release pin remains preserved. No
`modules/careops-approve` gitlink or duplicate directory is present, and the
existing child checkout remains uninitialized. This readback reconfirms the
already-qualified source reference without changing its pin or child state;
the optional source-only Approve/Decisions scenario remains a separate open
task under APPROVE3.1–3.4.

### Source runtime lifecycle evidence — 25 October 2026

Rechecked the existing public Approve source at its selected exact main
`f71c494634a87a9b4145742011070325c9b39c99` in a disposable clone. No source
files or parent module references were changed. Created a fresh repository-local
`.local/approve-ci` from the previously qualified Python 3.15.1 interpreter,
verified its actual version and virtual-environment prefix, then installed the
repository's hash-locked test tools. The focused source command
`.local/approve-ci/bin/python -m unittest tests.reference.test_workflow_runtime tests.reference.test_workflow_service tests.reference.test_workflow_registry -v`
passed all 39 tests.

The selected tests establish explicit route selection, human-review/approval
task creation and completion, stable source event identities, immutable
workflow-version checks, and refusal to start drafts or missing versions. They
do not establish duplicate case-request deduplication, case cancellation,
durable case persistence or recovery. `WorkflowService` delegates to the pure
in-memory `start_case`/`complete_current` reference and has no case store or
cancellation API; its module documentation reserves durability, authorization,
retries and audit persistence for a hosting adapter. No provider/API is called
by these tests. Keep APPROVE3.1–3.4 open until the selected source-only scenario
has an explicit duplicate, cancellation and recovery disposition and its
provider-absence cases are exercised; do not infer host or native behavior from
this reference suite.

## Direct-source cutover — 6 November 2026

Status: in progress. Explicit user direction supersedes the earlier submodule
retention plan: import all residual source, switch delivery to CareOps, then
label the predecessor legacy, point it here, make it private and archive it.

Owner: chat `01a1ae04-c11f-7901-b6a3-63d45f18ea93`; managed worktree
`careops-process-approve-cutover/careops`; branch
`codex/process-approve-cutover-20261106`. Scope: Process and Approve source,
paired parent CI/catalogues, backlog continuity and exact predecessor archival.
Other module/native owners retain their assignments. No tenant operations.

- [x] Freeze current main and preserve all advertised legacy refs in private recovery.
- [x] Import ordinary module source and preserve original file hashes.
- [x] Qualify local integrated tests and standalone packages; hosted delivery remains below.
- [x] Reconcile open legacy issues/PRs and local unpublished work.
- [ ] Merge with all current-head checks; verify main and independent clone.
- [ ] Verify exact private, archived, legacy-labelled predecessor state.

### Local qualification receipt — 6 November 2026

- Current legacy main: Process `ada7f03f50eb20abe384a9f3da0b76eb3a3fe2f3`;
  Approve `e0668809d50023444f173aae5bed7c0a8e661af3`. Earlier selected pins
  are historical; all subsequent main source is imported.
- Process: 1,758 tests passed, 10 capability skips; line coverage 96.24%, branch
  coverage 92.64%; strict typing zero errors/warnings. Offline PowerShell
  exporter tests pass. The exact frozen lock builds both wheel and sdist;
  an isolated wheel-only environment imports the installed implementation.
- Approve: 80 reference tests with 100% branch coverage, 10 M365 pilot tests,
  19 studio tests, strict type/lint checks and repository PowerShell checks pass.
  PAC 2.13.1 packs the unmanaged solution locally; no native import is performed.
- Parent: 127 source regression tests and six bounded fuzz tests pass;
  nine actual integrated Process/Approve compatibility cases pass. Privacy,
  reviewed-source inventory, portfolio harness and immutable-action pins pass.
- Legacy Approve's 29 substantive open issues were transferred with discussion
  history to CareOps #245–273. Process's substantive successors remain in the
  retained absorption table. Dependency dashboards move to CareOps #1.
- Every advertised legacy ref was bundled and restored in an independent mirror;
  exact ref comparison and full object checks pass. Local unpublished Process
  replay/package changes were preserved, merged and qualified here. Pending
  branches and dependency PRs retain explicit dispositions in each module's
  `conductor/legacy-cutover-ledger.json`; unqualified dependencies are not promoted.
- Native source/operational acceptance, denied connectors and email authority
  are unchanged. Protected hosted merge and predecessor archival remain open.

### Terminal checkpoint — upload and hosted prerequisites blocked, 6 November 2026

The locally qualified source import is commit
`365c712a9ef0a5fa4b94bfe85ec112299355be67` on the isolated migration branch.
Normal pre-commit guards passed. Normal pre-push refused the transfer; no source
was uploaded and no pull request was created. A bounded local reproduction using
the installed trusted scanner inspected 1,926 outgoing text identities and
returned 3,730 unreviewed spans in 659 groups. Most are PERSON detections; the
set also includes numeric and email categories. Technical examples include
programming identifiers, but that observation does not review the whole set.
Raw requests, findings and context remain private, outside tracked source.
The scanner, thresholds, model, trusted reviews and original hook chain were
not weakened or replaced. Only this worktree's dispatcher registration and
isolated qualified helper environments were added, preserving existing owners.

A separate existing hosted prerequisite also remains unresolved. Exact-target
CodeQL default-setup readback returns HTTP403: code scanning is not enabled.
The existing Security run 41639492322 records unavailable code scanning and
unsupported Dependency review on the private repository. Dependency Graph SBOM
readback itself succeeds (94 packages), so this is not a blanket API denial.
The required protected contexts remain unchanged. No purchase, entitlement,
visibility change or branch-protection bypass is authorised by this checkpoint.

CareOps #274 is the active successor for legacy dependency proposals and
historical-branch reconciliation. All 29 transferred Approve issues retain their
history. The old dependency PRs/dashboards remain open until actual cutover.
Both legacy main revisions still match the imported source. Legacy repository
visibility, archive flags, Actions and descriptions are unchanged: replacement
main delivery has not yet been established.

Next: review the exact privacy findings through the existing trusted-review
process; resolve the private-host security prerequisites through their owner;
then use normal push, current-head checks and protected merge. Verify main and
fresh-clone delivery before performing the authorised private legacy archival.

### Qualified private-repository security replacement — 6 November 2026

The user selected Python 3.15-compatible source analysis, OpenGrep where supported,
and OSV dependency scanning after the native private-repository CodeQL and
Dependency Review entitlement failures. These replacements are distinct checks;
CodeQL and native Dependency Review were not executed. All other required
contexts, strict branch protection and administrator enforcement remain required.
The required-context substitution follows successful current-head hosted checks.

Bandit 1.9.4 uses the actual repository-local Python 3.15.1 AST: 807 files scanned,
zero Python parser errors. OpenGrep native core 1.33.1 adds 251 Python, 168
JavaScript and 13 TypeScript security rules from an immutable, checksum-verified
rule revision. It scanned 807 Python, 62 JavaScript and 11 TypeScript targets.
Twenty Python parser gaps have Bandit coverage; four unchanged TypeScript parser
gaps remain explicitly unverified by OpenGrep. New or changed non-Python parser
gaps fail the gate. This does not claim CodeQL data-flow or language equivalence.

The local full-tree scan found 370 medium/high or OpenGrep findings: 284 are
unchanged baseline findings, retained as unresolved debt, and 86 received exact
source-byte/rule/line technical reviews. Changed files cannot inherit baseline
acceptance. Two actual HTML injection sinks in Approve Studio now use textContent.
Synthetic unsafe controls verify that both source scanners detect vulnerabilities;
a safe DOM control verifies the repaired construction. No source or raw findings
are uploaded. Community rule licences remain their original terms.

OSV Scanner 2.7.0 audits all 11 selected active lockfiles with zero vulnerable
packages. Immutable historical tool snapshots are excluded, active locks are not.
A known-vulnerable metadata-only fixture proves detection without installing it.
Missing locks, incomplete results and scanner errors fail closed. Native binaries,
rule bundles and Python dependencies have exact hashes. Detailed raw receipts,
source recovery bundles and privacy findings remain in private local evidence.

Privacy review removed genuine personal identifiers from imported operational
notes and retained the originals privately. Technical false positives have exact
identity/blob/span/value-digest reviews. Review-control offset and whole SHA-256
fields are recognized only after strict validation of the exact review document;
free-text reasons and other paths remain scanned. Fifteen privacy guard tests
and four source gate boundary tests passed. The original hook chain is retained.

Ownership: chat 01a1ae04-c11f-7901-b6a3-63d45f18ea93, isolated worktree
<private-home>/.codex/worktrees/careops-process-approve-cutover/careops;
Process/Approve integration and exact legacy repository cutover remain this lane.
Other worktrees, private native bindings and shared dirty checkout are untouched.
Next: final outgoing privacy scan, normal push, current-head hosted qualification,
protected merge, main delivery readback, then private/archive legacy readback.
