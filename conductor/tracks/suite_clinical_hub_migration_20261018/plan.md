# Clinical Hub migration implementation plan

Status: planned. Sequence: 1. Parent owner: CareOps maintainer.
Child/native owner: Existing Clinical Hub implementation owner.
All tasks below remain unexecuted; baseline research is recorded in spec.md.
No CGov task or tenant write is authorised by this plan.

## Phase 1: Source selection

- [ ] CLINICAL_HUB1.1 Refresh `edithatogo/clinical-hub-core` default head/checks and compare with observed `05d0e1f6f5a0495f40c516b40339c56a0b3698ae`; record the selected exact source revision in this plan.
- [ ] CLINICAL_HUB1.2 Review licence/attribution, public content/history checks and source-versus-private boundary; resolve required redistribution rights before packaging, without changing a child licence here.
- [ ] CLINICAL_HUB1.3 Inspect existing child instructions and dependency declarations; identify the smallest standalone capability and actual unresolved qualification gaps. Reuse passed unchanged evidence.
- [ ] CLINICAL_HUB1.4 Checkpoint: record selected slice, exact inputs, owners and stop conditions in this plan; no tenant or CGov operation.

## Phase 2: Optional source composition

- [ ] CLINICAL_HUB2.1 Add only the selected reviewed gitlink at `modules/clinical-hub-core`, canonical URL and source compatibility record; update PUBLIC_SOURCE_FILES.json and catalog together. Do not copy child files or import private history.
- [ ] CLINICAL_HUB2.2 Run existing parent inventory/portfolio checks; verify a clean parent clone without optional modules and a selective initialization of this module. No sibling checkout or runtime may be required.
- [ ] CLINICAL_HUB2.3 Use make ci with the module's stable Python and hash-locked environment. Reuse the passed same-SHA hosted check; inspect source inventory and publication checks before materialisation. Do not install a tenant application.
- [ ] CLINICAL_HUB2.4 Checkpoint: record actual source-check results, limitations and preimage parent SHA; native setup and operational acceptance remain separate.

## Phase 3: Bounded interoperability and recovery

- [ ] CLINICAL_HUB3.1 Trace fictional open action → reviewed carry-forward → manual minutes → follow-up; cover held/closed exclusions, unresolved concern, missing/stale paper, duplicate retry and preserved human edit. Reuse existing fixtures; implement only actual gaps.
- [ ] CLINICAL_HUB3.2 Define only the optional contract needed by the selected slice; test absent provider, incompatible version, stale/missing source and duplicate retry without duplicating authoritative ownership.
- [ ] CLINICAL_HUB3.3 Rehearse source rollback by reverting the gitlink/catalog/CI change in a disposable clone. Do not use submodule deletion as permission to remove native resources or records.
- [ ] CLINICAL_HUB3.4 Checkpoint: close only qualified source tasks, publish exact pins and supported commands, and hand off one consolidated completed deliverable or genuine blocker to the existing implementation owner.
