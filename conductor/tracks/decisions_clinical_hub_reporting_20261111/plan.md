# Executable reporting programme and evidence

**Status 11 November 2026: requirements/design/track only.** No metric, dataset, PBIP, PBIR, RDL, native workspace or deployment claimed complete. Use implementation and review tracks within the existing Conductor architecture; avoid duplicate approvals or invented operational permissions.

| Task | Prerequisite | Deliverable / acceptance | Status |
|---|---|---|---|
| GRA-T01 | Existing Decisions Track 16 and PR #312 | Reconcile old Dataverse YAML and Clinical Hub RMS schema; record authoritative source/table owners, unresolved source identifiers and status dictionaries | In progress — documentary |
| GRA-T02 | T01 | Versioned canonical schemas, grains, relationships, state/authority taxonomy and effective-date contracts with JSON Schema or equivalent | Open |
| GRA-T03 | T02 | Complete metric registry: numerator/denominator, date, scope, missingness, filters, security; verify each measure on fictional two-forum cases | Open |
| GRA-T04 | T02 | Standard SharePoint/List and file-source adapter with complete pagination, ETag/version, access, watermark, read-receipt and rollback; no premium Power Automate | Open; dependent on RMS-05 native work |
| GRA-T05 | T02 | Optional Dataverse adapter with field/source parity and explicit unsupported fields; no forced migration | Open |
| GRA-T06 | T02–T05 | Synthetic star-schema fixtures and deterministic transformation tests for shared action IDs, many-to-many links, effective status, late edits, missing evidence and restricted records | Open |
| GRA-T07 | T03,T06 | PBIP project with TMDL table/relationship/measures, explicit Date table, RLS, refresh parameters and source lineage; inspect exact model files | Open |
| GRA-T08 | T07 | PBIR dashboard pages for six roles/purposes with drillthrough, coverage and as-of labels; render/accessibility tests | Open |
| GRA-T09 | T07 | RDL paginated committee/portfolio pack using same measures, parameters, source/version footer, page breaks and controlled exceptions/provenance appendix | Open |
| GRA-T10 | T07–T09 | Exact cross-output parity tests (DAX result vs PBIR visual vs RDL dataset), adversarial RLS and small-count, export suppression and source-evidence review | Open |
| GRA-T11 | T10 | Qualify standard-M365 and optional Power BI licensing, model/report source ownership, workspace settings, scheduled refresh, deployment pipeline and operator fallback | Open |
| GRA-T12 | T11 | Measured pilot for two independently configured forums, manual-versus-deterministic workload comparison, net effort including rework, benefit and safety review | Open |
| GRA-T13 | All affected | Run focused, full and protected exact-head CI/security/PAC/model/RDL tooling; package, render, review, fix and merge when checks pass | Open |

**Implementation order:** contract and schema first; reusable test fixtures; adapter qualification; TMDL/PBIR/RDL; cross-surface tests; optional licensed release. Reuse the existing CareOps Power BI projects/workflows when their patterns are proven compatible; do not copy unrelated Finance/Workforce models wholesale.

**Per-task evidence:** source SHA, test command/runtime, fixture identity, artifact hashes, observed output, security classification, blockers, recovery and review decision. Record one canonical receipt, linking existing proofs. Preserve separate statuses for planned, source implemented, offline tested, packed, native configured, operationally accepted and benefit evaluated. CI no-start/billing refusal is *not executed*, not success/failure from a test assertion.

**Native prerequisites:** RMS H2 and exact Standard SharePoint connector qualification; authoritative adopted governance records; actual Power BI workspace/read/share licensing and relevant readers; RLS access and export controls. No document publication, audience expansion or use of sensitive governance data follows from completing source tasks.
