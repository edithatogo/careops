# Medical Job Planning — source implementation receipt (13 November 2026)

**State:** first bounded source slice committed for review; **G0/W0 source admission remains incomplete** and W1 domain qualification remains partial. No industrial policy, native SharePoint app, Power Automate flow, live staff data or tenancy is established by this receipt.

## Changes on this branch

- Added `modules/careops-medical-job-planning/domain.py`: independent strict parser, overlap validation and reference-only synthetic hours arithmetic. Rejects the v0.4.2 `bool("false") is True` bug, string/float/bool coercion into interval fields and ambiguous codes.
- Added `tests/test_mjp_domain_slice.py` with focused negative, positive and non-authority cases.
- Added module documentation, provenance and a partial-source profile, and updated `portfolio/repos.json`, `portfolio/module-catalog.md`, root `README.md` and reviewed source inventory consistently.
- Existing `modules/careops-workforce/` Power BI model/source/private feed contracts are untouched.
- The original 0.4.2 archive SHA-256 is `922c29f0364c7e1a0d61e4d0ba0a87f5cb28416c1f143758577404ff615626a7`. It is not imported wholesale. New project-owned validation source is separately identified as a derivative rewrite.

## What is and is not demonstrated

In an isolated local working copy of the uploaded source, 4 strict-input regression test methods were observed to fail against the original parser, then passed after changing parser and activity validation. The local wider test discovery could not qualify because Hypothesis is not installed and the archived generated receipt is now stale. The source-package tests committed in this branch are separate and require **current-head GitHub Actions** evidence before merge. Do not recycle archived 131-pass or earlier PR #321 receipts as evidence for this new code.

**Not yet evidenced:** full v0.4.2 implementation and licence reconciliation; integration of existing workflow_runtime.py, SharePoint adapter, full suite, semantic parity across runtimes, adopted industrial-policy engine, production SharePoint/Dataverse selection, native app/flow, operational identities/ACLs, controlled document generation, activation, retention, accessibility or live deployment.

## Remaining execution priorities

1. **MJP-002–008:** classify full archive file by file; verify licences, provenance and privacy; admit useful source in reversible slices, preserve source checks and exact SHA records, extend the contract test harness and Python 3.15 qualification. Existing reference-only synthetic arithmetic is **not** an approved industrial-policy engine.
2. **MJP-101–110 / W-1:** implement approved effective-dated industrial-rule interface, record disputed or incomplete job plans without false compliance, canonical temporal identities and full state machine, plus compare SharePoint physical ACLs with Dataverse.
3. **MJP-201–309:** actual Studio-authoritative Canvas source, solution-aware cloud flows, physical rights, native CAS/reconciliation, signed issued records, recovery and operator tools. Requires explicitly approved test tenant.
4. **MJP-401–412:** each optional CareOps provider/consumer adapter separately qualified, using the existing v1 schema and contracts; do not make BI or other modules MVP prerequisites.
5. **MJP-501–509:** licence/industrial/privacy/records/native release gates and separately authorised pilot. W6 optimisation deferred.

Local ZIP with the corrected **complete offline prototype** remains a work product separate from GitHub; do not imply all those files are in this module. Source/publication validation and target-native qualification are distinct.

**Review rule:** no bypass of failing required actions and no merge on stale heads; verify exact PR-head checks, then main readback.

## Additional local source qualification

- Full source archive ZIP integrity inspected: exact SHA-256 and size for all **73** manifest-listed entries; no unlisted files, invalid hashes, or unsafe filename found; no binary payloads. Original ZIP stayed outside Git. This is source *integrity* only, not permission to publish.
- Implemented standalone `policy_rules.py` with explicit source hash, clause/edition, adopted/reference-only/withdrawn state, classification eligibility, date interval and distinct planned versus observed CST. Reference-only/default remains **non-operative**; `approval_allowed` always false.
- Implemented standalone `archive_admission.py` to fail closed on manifest mismatch, path traversal, duplicate case-colliding entries, non-UTF-8/binary content, oversized ZIP entries or unlisted files.
- Focused local tests: 9 rule-evaluator tests and 8 archive-integrity tests passed under available local Python; exact repository Python 3.15.1 CI is the authoritative source qualification. Local fully discovered patched bundle: 44 SharePoint tests passed; the broader module suite remains unqualified due to missing Hypothesis and stale generated receipt, *not* a confirmed current 131-pass state.
- These additions are a local source slice and do not supply a real, independently verified CHHHS industrial entitlement, authorised role/delegation, transactional SharePoint implementation or native workflow.
