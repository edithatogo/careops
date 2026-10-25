# PPG migration implementation plan

Status: optional public source composition complete; optional document and provider interfaces remain open. Sequence: 7. Parent owner: CareOps maintainer.
Child/native owner: Existing PPG Workbench implementation owner.
Historical baseline research is retained in spec.md; current qualification follows below.
No CGov task or tenant write is authorised by this plan.

## Phase 1: Source selection

- [x] PPG1.1 Refresh `edithatogo/careops-ppg` default head/checks and compare with observed `d47214cdef16739c5ab9b9a2680da41544e54720`; record the selected exact source revision in this plan.
- [x] PPG1.2 Review licence/attribution, public content/history checks and source-versus-private boundary; resolve required redistribution rights before packaging, without changing a child licence here.
- [x] PPG1.3 Inspect existing child instructions and dependency declarations; identify the smallest standalone capability and actual unresolved qualification gaps. Reuse passed unchanged evidence.
- [x] PPG1.4 Checkpoint: record selected slice, exact inputs, owners and stop conditions in this plan; no tenant or CGov operation.

## Phase 2: Optional source composition

- [x] PPG2.1 Add only the selected reviewed gitlink at `modules/careops-ppg`, canonical URL and source compatibility record; update PUBLIC_SOURCE_FILES.json and catalog together. Do not copy child files or import private history.
- [x] PPG2.2 Run existing parent inventory/portfolio checks; verify a clean parent clone without optional modules and a selective initialization of this module. No sibling checkout or runtime may be required.
- [x] PPG2.3 Run the documented Python unittest suite, both Node fixture tests, portable-content check and draft-assembler build. Resolve the existing PR/check discrepancy without assuming a functional failure or merging its branch as part of this planning work.
- [x] PPG2.4 Checkpoint: record actual source-check results, limitations and preimage parent SHA; native setup and operational acceptance remain separate.

## Phase 3: Bounded interoperability and recovery

- [x] PPG3.1 Exercise fictional persistent document identity, changed-source reconciliation, unknown alias, absent row, preserved human metadata and duplicate retry. Missing rows never imply retirement. Generated HTML remains a supported fallback while the preferred native document route is qualified.
- [x] PPG3.2 Define only the optional contract needed by the selected slice; test absent provider, incompatible version, stale/missing source and duplicate retry without duplicating authoritative ownership.
- [x] PPG3.3 Rehearse source rollback by reverting the gitlink/catalog/CI change in a disposable clone. Do not use submodule deletion as permission to remove native resources or records.
- [x] PPG3.4 Checkpoint: close only qualified source tasks, publish exact pins and supported commands, and hand off one consolidated completed deliverable or genuine blocker to the existing implementation owner.

Preserve current owner work; select a stable handoff point before any source pin.

## Current source candidate — 24 October 2026

Selected source: `6a98821538696f1a47d96b1ed91fff789eefbdda` from the public
`edithatogo/careops-ppg` repository. PR56 resolved the historical project-licence
gap with complete Apache-2.0 terms, package declarations and retained pandas
BSD attribution. Main package workflow40096187662 and Security40096188057 passed.
The actual attested ZIP licence, notice and pandas licence bytes, SPDX file hashes
and archive digest were verified against that exact source. Its unchanged hosted
Python3.15.1, Node22/26.12.1, content, assembler and unpacked-package checks are
reused, rather than repeating a completed source qualification.

This candidate adds only an optional source reference and paired-pin guard.
It introduces no parent PPG runtime, shared register, policy-content migration or
native deployment. Workbench and policy-source owners retain their files and
objects; the ordinary Power Automate reader remains Stopped. The original
`d47214c` baseline remains historical, rather than current licence/check state.
Parent preimage: `c81696f7dc48a29a6b3b05422778aaf3ca34edbc`.
Reversal is a reviewed revert of this composition commit, restoring the parent
catalog, inventory and gitlink together; it grants no authority to delete source,
private evidence, native resources or records. Interoperability tasks remain open
until their exact fictional cases and any optional contract are qualified.

Parent candidate qualification: reviewed public inventory and real portfolio gate
passed. The paired-pin regression checks the real gate with independent incorrect
gitlinks, including PPG. A disposable clean clone passed without optional modules;
selective PPG initialization fetched the selected exact source without siblings.
An actual no-commit revert restored the full preimage tree, not merely a proposed
rollback command. Hosted parent qualification and protected merge remain pending.
No optional contract or native interoperability is asserted by these source proofs.

### Source composition closeout — 25 October 2026

CareOps PR140 merged as `2dd1abc9f079e955c70408d48fa367bb694bd87e`. The selected public source
`6a98821538696f1a47d96b1ed91fff789eefbdda` agrees across the gitlink, public inventory, catalog and
applicable ALM/CI declarations. The recorded clean-parent, selective-checkout
and source-reversal evidence applies to this selected reference. GitHub readback
found 12 successful main checks and two conditional skips on the merge commit;
its PR head had 14 successes and one conditional skip. Current parent main
`2dd1abc9f079e955c70408d48fa367bb694bd87e` retains passing
portfolio and public-source checks. The selected child source/package and attribution receipts remain the bounded proof; optional document and provider interfaces remain open.

### Selected source interface closeout — 25 October 2026

Revalidated the exact parent-selected child commit
`6a98821538696f1a47d96b1ed91fff789eefbdda`. Its package and security workflows
(`40096187662` and `40096188057`) both passed on that exact SHA, including the
Python 3.15.1 and Node 22/26.12.1 portable test jobs, package build/unpacked
exercise, content boundary, and source/artifact attestation. In a disposable
clone at the same commit, a verified repo-local Python 3.15.1 environment ran:

```text
PYTHONPATH=tests:tools/lifecycle .venv/bin/python -m unittest \
  test_ppg_source_sync test_generation_contract test_edition_history \
  test_next_review_occurrence test_edition_receipts -v
Ran 61 tests — OK
```

The synthetic fixtures cover persistent identity, source-only field ownership,
unknown/version-changed aliases, absent rows without retirement, human metadata
and edited-output preservation, changed/stale source and template, duplicate
identity/replay, failed-write retry and readback. Generation contract fixtures
require the selected `sharepoint-structured` route and reject missing/failed
invocations or unsupported schema versions. The HTML route remains a fallback;
these checks verify local bindings and receipts only. They do not prove a native
SharePoint generation run, rendered output, access or recovery.

The public child main has since advanced to `2e02816ef4a62245c1b7bc135c19eb90532e721f`.
Its newer cloud source-observation PR59 is still a draft with current-head checks
pending. The parent retains its already-qualified pin `6a988215...`; no update is
inferred from an unmerged source candidate. This closes PPG3.1 and PPG3.2 only for
the selected composed source and records the source checkpoint; native document
generation and future child-main promotion remain separate.
