# Shared Model Merge Readiness

## Purpose

This framework decides whether the VMO Finance and Medical Staff dashboard work should remain separate, move to thin reports over a shared semantic model, or adopt another combined pattern after validation.

The current state matters: the dashboards are not yet complete, so this document sets the default operating position before the actual model comparison can be done.

## Current Recommendation

Keep the dashboards separate for now.

That remains the safest default even though separate PBIR and TMDL artifacts now exist for both dashboard streams. The exports make comparison possible, but they do not prove that a shared semantic model is safe. A merge decision still requires live SQL validation evidence, model-diff evidence, and explicit acceptance of any semantic differences.

## Actionable Decision Gates

Use these gates in order. Do not move to the next gate until the evidence for the previous gate has been captured.

| Gate | Decision question | Required evidence | Exit decision |
| --- | --- | --- | --- |
| Gate 0: Source-control export present | Do both dashboard streams have reviewable standalone PBIR and TMDL artifacts? | `scripts/Invoke-Validation.ps1 -Mode SourceControlReady` passes; each standalone model has current TMDL; each standalone report has current PBIR; export timestamp or commit reference is recorded. | Continue comparison only if both streams pass. |
| Gate 1: SQL contract validated | Do the published SQL objects match the shared source contract? | SQL host/listener `<sql-server-host>` and database names captured; required tables/views present; required columns and keys present; row-count and null-key checks run for every contract object; gateway/data-source binding is known. | Continue only if both dashboards can bind to SQL without Access-only dependencies. |
| Gate 2: Standalone refresh proven | Can each dashboard refresh independently against SQL? | Separate refresh logs for VMO Finance and Medical Staff; no shared refresh failure path except the same SQL platform; source parameters resolved through deployment configuration; no hardcoded local file paths. | Continue only if each dashboard can succeed or fail independently. |
| Gate 3: Model comparison complete | Are shared dimensions, relationships, and measures genuinely compatible? | TMDL model diff reviewed; table grains matched; relationship cardinalities and active/inactive roles documented; measure catalogues compared with formula, filter context, and rounding rules. | Mark each candidate as promote, defer, or reject. |
| Gate 4: Ownership and ALM accepted | Would a shared model improve maintainability without blurring ownership? | Named owner for each shared table/measure; dashboard-specific logic remains in the owning stream; deployment path and rollback plan documented; consumer-impact assessment completed. | Approve shared-model implementation track or close with standalone recommendation. |

## Comparison Matrix

| Decision option | Shared definitions required | Refresh coupling | Ownership complexity | Validation effort | Current fit before dashboard completion |
| --- | --- | --- | --- | --- | --- |
| Separate dashboards | Minimal, only shared naming and documentation | Low | Low | Lowest | Best fit |
| Thin reports over shared semantic model | Stable shared date, cost centre, and financial definitions | Medium | Medium | High | Not yet ready |
| Composite model | Shared definitions plus tolerated dual-source behaviour | High | High | Highest | Not recommended now |
| Combined executive report | Mature business definitions across both domains | Medium to high | Medium | High | Defer until later |

## Decision Criteria

Use the following criteria when the dashboards are complete:

- Business definition stability: the same metric means the same thing in both dashboards.
- Source contract stability: the underlying SQL Server tables or views are stable and documented.
- Shared dimension maturity: date, cost centre, organisation, and financial lookups are genuinely common.
- Refresh independence: one dashboard can refresh without breaking the other.
- Ownership clarity: dashboard-specific logic stays owned by the right reporting area.
- Deployment readiness: source control, ALM, and refresh paths are predictable enough to promote together.

## Shared Dimension Candidates

These are candidates only. Promotion requires the evidence listed in the gates above.

| Candidate | Likely source objects | Promotion test | Current disposition |
| --- | --- | --- | --- |
| Date | `dbo.tbl_Calendar`, `dbo.tbl_WF_Calendar` | Same date grain, finance period logic, fiscal-year boundaries, month/period attributes, and date-key type can be conformed without changing either report. | Defer until SQL validation proves both calendars and period rules. |
| Cost Centre | `dbo.ca_MVRPT_COSTCENTRES`, GL/staff/payroll cost-centre fields | Normalized cost-centre key joins across GL, VMO, staff, history, and payroll rows with acceptable null/unmatched rates. | Candidate for earliest promotion after SQL validation. |
| Account | `dbo.ca_MVRPT_ACCOUNT`, GL and VMO account fields | Account code, name, group, status, and classification use the same business meaning in both candidate fact paths. | VMO-first candidate; do not promote into a shared layer unless Medical Staff usage is proven. |
| Workforce / Medical Staff | `dbo.tbl_Medical_Staff_Data`, `dbo.tbl_Medical_Staff_History`, payroll views | Staff identifier, current/history grain, FTE, department, grade, and status are stable across current, history, and payroll data. | Keep Medical Staff-owned unless a combined workforce-finance use case is approved. |
| Department / organisation | Derived staff department, cost-centre hierarchy, available organisational lookups | Department-to-cost-centre mapping is current, unique enough for reporting, and accepted by both report owners. | Defer; high semantic-drift risk. |

## Shared Measure Candidates

Promote only measures whose DAX, grain, filter context, sign convention, and rounding all match.

| Candidate measure | Required proof before promotion | Current disposition |
| --- | --- | --- |
| `Total Amount` | Same amount column meaning, sign convention, currency/decimal precision, and filter context across SQL facts. | Candidate after SQL tie-out. |
| `Transaction Count` | Same row-grain definition and exclusion rules for blank/cancelled/duplicate rows. | Candidate after model diff. |
| `Variance Amount` | GL-side and source-side amounts use the same reconciliation grain and sign convention. | VMO/reconciliation-owned until proven common. |
| `Variance %` | Agreed denominator, zero/blank handling, rounding, and display format. | Defer until `Variance Amount` is accepted. |
| `Distinct Cost Centres` | Same normalized key and same treatment of inactive, blank, and unmatched cost centres. | Candidate after cost-centre key checks. |
| `Opening Balance` | Agreed opening period, carry-forward logic, and relationship to transaction fact. | Defer; finance-specific until proven shared. |
| `Closing Balance` | Agreed period-end logic and reconciliation to source totals. | Defer; finance-specific until proven shared. |

## Prerequisites

Do not make the merge decision until all of the following are true:

- Both standalone dashboards are complete.
- Both dashboards have current PBIR and TMDL exports from their standalone builds.
- Both dashboards have been validated against SQL Server objects, not only Access sample outputs.
- Dashboard tables, relationships, and measures have been compared from the finished TMDL exports, not from assumptions.
- Refresh paths, gateway bindings, credentials ownership, and deployment parameters are known.
- Shared definitions have been separated from dashboard-specific logic.

## Exact Evidence Required After SQL Validation

Capture this evidence before recommending any merge implementation:

| Evidence item | Required content | Stored or referenced where |
| --- | --- | --- |
| SQL contract inventory | Server/database identifier or environment alias, schema, object names, object type, required columns, key columns, row counts, and validation timestamp. | Link from this document or the relevant SQL validation note; keep secrets out of source control. |
| Column and key checks | For each contract object: required columns present, key null count, duplicate key count where uniqueness is required, and unexpected type coercions. | Validation output or checklist entry. |
| Source tie-out | For each dashboard: SQL totals match the accepted source report or validation view for agreed periods and tolerances. | Dashboard acceptance notes. |
| Refresh proof | Independent refresh result for each standalone model, including gateway/data-source binding, duration, failure text if any, and parameter values by environment alias. | Dashboard acceptance notes or ALM evidence. |
| TMDL comparison | Table list, relationship list, date-table designation, measure catalogue, and reviewed diff against the prior accepted export. | Model comparison note or committed review artifact. |
| PBIR compatibility check | Confirmation that visuals still bind after model refresh/export and no report page relies on removed or renamed fields. | PBIR validation output and acceptance notes. |
| Shared-candidate register | Promote/defer/reject outcome for each shared dimension and measure candidate, with owner and reason. | This document or follow-up implementation spec. |
| Risk acceptance | Explicit acceptance of any refresh, ownership, deployment, or semantic-drift risk that remains. | Conductor track note or approval record. |

## Risk Register

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Premature merge | Locks in the wrong model shape before the business definitions are stable | Keep the dashboards separate until validation is complete |
| Refresh coupling | A failure in one report can block the other | Preserve independent refresh paths unless shared behaviour is proven |
| Hidden semantic drift | The same term can mean different things in VMO and Medical Staff reporting | Compare the finished measures and table roles before any merge |
| Ownership blur | Shared logic can make it unclear who maintains what | Keep domain-specific logic in the owning dashboard until the boundary is proven |
| Deployment churn | Rework in report structure and ALM can cascade into avoidable packaging changes | Defer consolidation until the source contract and report shape settle |
| PBIR/TMDL false confidence | Source-control exports can parse while still pointing at unvalidated or Access-derived assumptions | Treat exports as comparison evidence, not SQL refresh evidence |
| Shared dimension overreach | A conformed dimension can hide source-specific period, cost-centre, or department rules | Promote only attributes that pass key, grain, and tie-out checks |
| Measure context mismatch | A shared measure can return plausible but wrong results if relationships or filters differ | Compare DAX, filter context, relationship paths, and accepted totals before promotion |
| Gateway and credential coupling | A shared model can create a single operational failure point for two reporting streams | Require independent refresh proof and an agreed rollback path |

## Follow-up Track Trigger

Create the implementation track for a shared semantic model only if the completed dashboards show all of the following:

- Stable shared dimensions with matching definitions.
- No material measure conflicts that would change report meaning.
- Independent refresh behaviour that can survive a shared model.
- A clear business case for reducing duplication or adding a combined report.
- Complete post-SQL-validation evidence for Gates 0 through 4.

If those conditions are not met, keep the standalone dashboards as the operating model and close this track without a merge implementation follow-up.
