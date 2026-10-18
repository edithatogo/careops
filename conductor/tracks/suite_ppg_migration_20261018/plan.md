# PPG migration implementation plan

Status: planned. Sequence: 7. Parent owner: CareOps maintainer.
Child/native owner: Existing PPG Workbench implementation owner.
All tasks below remain unexecuted; baseline research is recorded in spec.md.
No CGov task or tenant write is authorised by this plan.

## Phase 1: Source selection

- [ ] PPG1.1 Refresh `edithatogo/careops-ppg` default head/checks and compare with observed `d47214cdef16739c5ab9b9a2680da41544e54720`; record the selected exact source revision in this plan.
- [ ] PPG1.2 Review licence/attribution, public content/history checks and source-versus-private boundary; resolve required redistribution rights before packaging, without changing a child licence here.
- [ ] PPG1.3 Inspect existing child instructions and dependency declarations; identify the smallest standalone capability and actual unresolved qualification gaps. Reuse passed unchanged evidence.
- [ ] PPG1.4 Checkpoint: record selected slice, exact inputs, owners and stop conditions in this plan; no tenant or CGov operation.

## Phase 2: Optional source composition

- [ ] PPG2.1 Add only the selected reviewed gitlink at `modules/careops-ppg`, canonical URL and source compatibility record; update PUBLIC_SOURCE_FILES.json and catalog together. Do not copy child files or import private history.
- [ ] PPG2.2 Run existing parent inventory/portfolio checks; verify a clean parent clone without optional modules and a selective initialization of this module. No sibling checkout or runtime may be required.
- [ ] PPG2.3 Run the documented Python unittest suite, both Node fixture tests, portable-content check and draft-assembler build. Resolve the existing PR/check discrepancy without assuming a functional failure or merging its branch as part of this planning work.
- [ ] PPG2.4 Checkpoint: record actual source-check results, limitations and preimage parent SHA; native setup and operational acceptance remain separate.

## Phase 3: Bounded interoperability and recovery

- [ ] PPG3.1 Exercise fictional persistent document identity, changed-source reconciliation, unknown alias, absent row, preserved human metadata and duplicate retry. Missing rows never imply retirement. Generated HTML remains a supported fallback while the preferred native document route is qualified.
- [ ] PPG3.2 Define only the optional contract needed by the selected slice; test absent provider, incompatible version, stale/missing source and duplicate retry without duplicating authoritative ownership.
- [ ] PPG3.3 Rehearse source rollback by reverting the gitlink/catalog/CI change in a disposable clone. Do not use submodule deletion as permission to remove native resources or records.
- [ ] PPG3.4 Checkpoint: close only qualified source tasks, publish exact pins and supported commands, and hand off one consolidated completed deliverable or genuine blocker to the existing implementation owner.

Preserve current owner work; select a stable handoff point before any source pin.
