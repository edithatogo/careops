# Shared Semantic Model Contract

This document defines the shared finance semantic contract for the two Access-backed dashboards. The design keeps the VMO Finance and Medical Staff datasets separate for now, while standardising the parts that can be shared safely later.

## Merge Posture

Until both dashboards are complete and validated, this document remains a contract candidate rather than a merge instruction.

The current posture is:

- Keep the dashboards separate.
- Extract only definitions that can be shared without changing dashboard meaning.
- Defer any shared semantic model merge until the merge-readiness framework says the finished models justify it.
- Treat existing standalone PBIR and TMDL exports as comparison evidence, not as approval to consolidate.
- Require SQL Server validation before any shared model TMDL is exported under `src/powerbi/shared/model-tmdl/`.

## Scope

- Keep standalone Power BI models for:
  - `src/powerbi/dashboards/vmo-finance`
  - `src/powerbi/dashboards/medical-staff`
- Promote only stable common definitions into `src/powerbi/shared/`.
- Treat raw Access files, extracted data, and local machine state as out of scope for source control.

## Table Classification

### VMO Finance source

| Table | Role | Grain | Contract |
| --- | --- | --- | --- |
| `tbl_Calendar` | Shared calendar candidate | One row per date | Canonical source for VMO date attributes until merged. |
| `tbl_GL_Transactions` | Fact | One row per GL transaction line | Primary accounting fact for VMO reporting. |
| `tbl_Reconciliation_GL_Data` | Reconciliation fact | One row per reconciliation row | Supports GL tie-out and variance analysis. |
| `tbl_Reconciliation_VMO_Data` | Reconciliation fact | One row per reconciliation row | Supports VMO-to-GL comparison. |
| `tbl_VMO_Data` | Fact | One row per VMO activity record | Main VMO activity source. |
| `tbl_VMO_GL_Classification` | Lookup / bridge | One row per classification key | Maps GL activity to VMO reporting buckets. |
| `tbl_VMO_GL_Transactions` | Fact / bridge | One row per linked GL transaction | Transaction-level mapping between VMO and GL. |

### Medical Staff source

| Table | Role | Grain | Contract |
| --- | --- | --- | --- |
| `tbl_WF_Calendar` | Shared calendar candidate | One row per date | Workforce calendar source for the medical model. |
| `tbl_Medical_Staff_Data` | Fact | One row per staff record or pay-period row | Primary medical staff reporting fact. |
| `tbl_Medical_Staff_History` | Fact / history | One row per history event or versioned row | Keeps staff changes and history visible. |

### Linked and pass-through dependencies

These objects stay as dependencies rather than becoming shared model tables unless the business logic converges:

- Payroll/FTE pass-through objects
- `tbl_Calendar` when consumed from the other Access file
- `tbl_VMO_Data` when consumed from the Medical Staff file
- `tbl_Email_Addresses`
- Account and cost-centre lookup queries
- Linked Excel tables and other external pass-through objects

## Shared Definitions

### Date / calendar

The shared date table should become the canonical conformed date dimension later, with both source calendars mapped to it.

Minimum contract:

- One row per date.
- Date key stored as a real `date` value.
- Stable period attributes for year, month, quarter, fiscal year, and fiscal period.
- Derived flags for period start, period end, workday, and month end when available.
- Source-specific calendar labels can stay in the standalone models, but shared reporting should use one canonical `Date` table.
- SQL validation must prove that `dbo.tbl_Calendar` and `dbo.tbl_WF_Calendar` can be conformed without changing finance-period or workforce-period reporting.

### Cost centre

The shared cost-centre definition should be the canonical business key used by both reporting areas.

Minimum contract:

- Canonical key: trimmed, upper-cased text value.
- Required fields: cost-centre code, display name, active/status flag, and group/parent where available.
- Keep source-specific account or payroll labels separate from the canonical cost-centre key.
- Use the same normalized key in GL, VMO, payroll, and staff-history tables before any future merge.
- SQL validation must report null-key, duplicate-key, and unmatched-key counts before this becomes a shared dimension.

### Account

The shared account definition is currently a VMO-first candidate, not a general shared dimension.

Minimum contract:

- Canonical key: trimmed, upper-cased account code.
- Required fields: account code, account name, account group, and status where available.
- Classification rules stay outside the shared account dimension unless the same rule set is accepted across dashboard streams.
- Promote only if Medical Staff reporting has a confirmed account-level use case.

### Department / organisation

Department and organisational hierarchy should remain dashboard-specific until the SQL source proves a stable crosswalk to cost centre or another accepted organisational key.

Minimum contract before promotion:

- One current row per organisational reporting key, or an explicit effective-dated grain.
- Accepted mapping between department, cost centre, and staff/payroll records.
- Documented handling for inactive, renamed, merged, or unmatched units.

## Shared Measure Promotion Rules

Common measure names are not enough. A measure can move into the shared contract only when all of the following are true:

- The source fact grain is the same or the difference is explicitly handled in the DAX.
- The filter path through Date, Cost Centre, Account, and any owner-specific dimension is understood.
- The sign convention and decimal/rounding rules match the accepted source totals.
- The measure result ties out against SQL validation views or accepted source reports for agreed periods.
- The measure owner has accepted the formula and display format.

## Naming Conventions

- Parameters: `p_*`
- Functions: `fn_*`
- Staging queries: `stg_*`
- Dimension tables: `dim_*`
- Fact tables: `fact_*`
- Bridge tables: `bridge_*`
- Lookup/reference tables: `ref_*`
- Model table names should be business-first and singular when possible, for example `Date`, `Cost Centre`, `GL Transactions`, and `Medical Staff History`.
- Keep source table names as `tbl_*` only in source-facing queries or comments.

## Merge Path

1. Keep the two dashboard models separate while the source semantics are still moving.
2. Promote the shared date and cost-centre definitions into `src/powerbi/shared/`.
3. Reuse shared M helper templates so both dashboards normalise keys the same way.
4. Move common measures into the shared contract only after the measure definitions match in both dashboards.
5. Merge into a shared semantic model only after the standalone models can refresh independently and the source mapping is stable.

Do not populate `src/powerbi/shared/model-tmdl/` with shared semantic model exports until `docs/shared-model-merge-readiness.md` records a passed merge gate and a follow-up implementation track exists.

## Readiness Gate

The merge-readiness decision framework should be satisfied before any implementation work begins on a combined model:

- The finished dashboard models must exist.
- The finished dashboard outputs must be validated.
- Shared dimensions must be identifiable from the completed models, not from draft intent.
- Any remaining model differences must be explicitly understood and accepted.
- SQL Server source validation must prove the published objects, keys, row counts, and refresh bindings.
- PBIR and TMDL exports must be current enough to compare model/report binding behaviour.

## Published Source

Access is a profiling and sample-extract source. The published semantic model should use SQL Server tables or views with equivalent contracts. Keep server and database values parameterised through `SqlServerName` and `SqlDatabaseName`.

## M Query Contracts

The shared Power Query layer should follow these rules:

- Parameterise source roots and never hardcode user-specific paths.
- Load Access tables through stable query names rather than ad hoc navigation steps.
- Convert calendar fields to `date` early and keep them as `date` for model output.
- Normalize cost-centre keys with trim and upper-case logic before joins.
- Treat linked/pass-through objects as explicit dependencies, not hidden model tables.
- Keep query output schemas stable so the shared contract can be consumed later without renaming churn.

## Starter Measures

The shared model should standardise the following measure names where the underlying data exists:

- `Total Amount`
- `Transaction Count`
- `Variance Amount`
- `Variance %`
- `Distinct Cost Centres`
- `Opening Balance`
- `Closing Balance`

Domain-specific measures for VMO and Medical Staff should stay in the standalone dashboard models until the shared definitions are proven.

Initial disposition:

| Measure | Disposition before SQL validation |
| --- | --- |
| `Total Amount` | Candidate after SQL tie-out and sign convention review. |
| `Transaction Count` | Candidate after row-grain comparison. |
| `Variance Amount` | Keep VMO/reconciliation-owned until common reconciliation semantics are proven. |
| `Variance %` | Defer until `Variance Amount` is accepted. |
| `Distinct Cost Centres` | Candidate after normalized key checks. |
| `Opening Balance` | Defer; finance-specific until proven common. |
| `Closing Balance` | Defer; finance-specific until proven common. |

## Shared M Templates

- `src/powerbi/shared/m/SharedParameters.m` provides the raw and extract roots.
- `src/powerbi/shared/m/SharedFinanceContracts.m` defines the shared table and naming contract plus reusable key-normalisation helpers.

## Validation Notes

- No raw Access data needs to be committed.
- The shared contract is valid if the standalone dashboards can point at the same normalisation rules without changing source semantics.
- Later TMDL export can reuse this contract without changing the table roles above.
