# RIMS migration implementation plan

Status: planned. Sequence: 3. Parent owner: CareOps maintainer.
Child/native owner: Existing RIMS publications implementation owner.
All tasks below remain unexecuted; baseline research is recorded in spec.md.
No CGov task or tenant write is authorised by this plan.

## Phase 1: Source selection

- [ ] RIMS1.1 Refresh `edithatogo/careops-rims` default head/checks and compare with observed `f9031869f4f5dda723d548c5ed821a748154cef6`; record the selected exact source revision in this plan.
- [ ] RIMS1.2 Review licence/attribution, public content/history checks and source-versus-private boundary; resolve required redistribution rights before packaging, without changing a child licence here.
- [ ] RIMS1.3 Inspect existing child instructions and dependency declarations; identify the smallest standalone capability and actual unresolved qualification gaps. Reuse passed unchanged evidence.
- [ ] RIMS1.4 Checkpoint: record selected slice, exact inputs, owners and stop conditions in this plan; no tenant or CGov operation.

## Phase 2: Optional source composition

- [ ] RIMS2.1 Add only the selected reviewed gitlink at `modules/careops-rims`, canonical URL and source compatibility record; update PUBLIC_SOURCE_FILES.json and catalog together. Do not copy child files or import private history.
- [ ] RIMS2.2 Run existing parent inventory/portfolio checks; verify a clean parent clone without optional modules and a selective initialization of this module. No sibling checkout or runtime may be required.
- [ ] RIMS2.3 Select one publications-only source-to-output slice using START_HERE.md and current completion scope. Run its existing focused contract/fixture checks plus public-source checks. Inventory report/model/flow dependencies before any managed-package or report migration.
- [ ] RIMS2.4 Checkpoint: record actual source-check results, limitations and preimage parent SHA; native setup and operational acceptance remain separate.

## Phase 3: Bounded interoperability and recovery

- [ ] RIMS3.1 Exercise fictional source-qualified publication IDs, conservative cross-source deduplication, attribution lineage, period identity, duplicate replay and one selected output. Preserve human attribution corrections, unresolved affiliation concerns and issued report revisions.
- [ ] RIMS3.2 Define only the optional contract needed by the selected slice; test absent provider, incompatible version, stale/missing source and duplicate retry without duplicating authoritative ownership.
- [ ] RIMS3.3 Rehearse source rollback by reverting the gitlink/catalog/CI change in a disposable clone. Do not use submodule deletion as permission to remove native resources or records.
- [ ] RIMS3.4 Checkpoint: close only qualified source tasks, publish exact pins and supported commands, and hand off one consolidated completed deliverable or genuine blocker to the existing implementation owner.
