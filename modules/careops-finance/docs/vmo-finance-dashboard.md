# VMO Finance Dashboard

## Scope

Standalone Power BI dashboard for VMO finance reporting against `VMO Reporting.accdb`.

This track stays inside the VMO dashboard folder and documents the design before any shared-model promotion:

- `conductor/tracks/vmo-finance-dashboard/`
- `src/powerbi/dashboards/vmo-finance/`
- `docs/vmo-finance-dashboard.md`

## Completion Track Notes

This document records the design, draft artifacts, current generated exports,
and validation gates for the VMO dashboard completion track. The interim state
uses the local Access sample for validation; SQL Server binding is a later
published-refresh step. The PBIR report package is already exported; the
remaining dashboard-completion work is to verify that package and keep the
acceptance evidence aligned with the checked-in source.

### Created Artifacts

- SQL-backed parallel M templates: `src/powerbi/dashboards/vmo-finance/m/sql/`
- DAX measure catalogue draft: `src/powerbi/dashboards/vmo-finance/model-tmdl/measure-catalogue.md`
- Relationship build checklist: `src/powerbi/dashboards/vmo-finance/model-tmdl/relationship-checklist.md`
- VMO acceptance pack: `conductor/tracks/vmo-dashboard-completion/acceptance-pack.md`
- pbi-cli implementation checklist: `src/powerbi/dashboards/vmo-finance/pbi-cli-implementation-checklist.md`
- Export instructions: `src/powerbi/dashboards/vmo-finance/model-tmdl/export-instructions.md`
- Generated TMDL export folder: `src/powerbi/dashboards/vmo-finance/model-tmdl/live-export/`
- Generated PBIR folder: `src/powerbi/dashboards/vmo-finance/report/pbir/`
- Report page completion checklist: `src/powerbi/dashboards/vmo-finance/report/page-completion-checklist.md`
- Validation checklist: `src/powerbi/dashboards/vmo-finance/report/validation-checklist.md`

### Blocked Items

- SQL Server credentialed refresh validation.
- Production SQL Server parameter binding.

## Source Inventory

### Local Tables

- `tbl_Calendar`
- `tbl_GL_Transactions`
- `tbl_Reconciliation_GL_Data`
- `tbl_Reconciliation_VMO_Data`
- `tbl_VMO_Data`
- `tbl_VMO_GL_Classification`
- `tbl_VMO_GL_Transactions`

### Views

- `qry_Financial_Year_Total`
- `qry_Reconciliation_GL_Data`
- `qry_Reconciliation_GL_Summary`
- `qry_Reconciliation_GL_Summary_Other_Subsystems`

### External Dependencies

- `tbl_Email_Addresses`
- `tbl_Excel_VMO_Data`
- `ca_MVRPT_ACCOUNT`
- `ca_MVRPT_COSTCENTRES`
- `dbo_FMIS_GL_JOURNAL`

## Dashboard Page Spec

| Page | Purpose | Primary visuals | Default filters |
| --- | --- | --- | --- |
| Executive Summary | Show VMO totals and the reconciliation headline. | KPI cards for GL total, VMO total, variance, variance %, and record count; trend line by financial year/period; stacked bar by reconciliation status. | Financial year, period, cost centre, account, classification. |
| Reconciliation Detail | Explain the GL-to-VMO bridge at a summary level. | Matrix by financial year, period, cost centre, account, and classification; bar chart by status; variance table. | Financial year, period, status, cost centre, classification. |
| Classification And Cost Centre | Show where VMO activity and exceptions concentrate by classification and organisational slice. | Classification/cost-centre matrix, variance bar chart, top-N exception visual. | Financial year, period, classification, account, cost centre. |
| Exceptions | Surface rows needing finance review. | Exception table with drillthrough fields; unmatched GL / unmatched VMO counts; status histogram. | Financial year, period, exception flag, subsystem, cost centre. |
| Transaction Detail | Provide line-level traceability back to Access. | Transaction table with row-level identifiers, source amounts, posting dates, and classification fields. | Financial year, period, transaction type, cost centre, account. |
| Validation | Compare Power BI results to Access exports and saved query outputs. | Reconciliation control cards, delta tables, and pass/fail indicators. | Validation set, financial year, period. |

## Model Grain Proposal

### Fact / Bridge Tables

| Table | Proposed grain | Notes |
| --- | --- | --- |
| `tbl_GL_Transactions` | One GL posting line. | Primary GL fact. Keep one row per source transaction line. |
| `tbl_VMO_Data` | One VMO source line or loaded extract row. | Primary VMO fact for reporting totals. |
| `tbl_VMO_GL_Transactions` | One mapped GL line after VMO classification. | Bridge/fact for VMO classification and reconciliation. |
| `tbl_VMO_GL_Classification` | One classification mapping row. | Use as mapping/lookup if the source has multiple classification rules. |
| `tbl_Reconciliation_GL_Data` | One GL reconciliation row. | Use for exceptions and variance explanation. |
| `tbl_Reconciliation_VMO_Data` | One VMO reconciliation row. | Use for VMO-side validation and mismatch analysis. |

### Dimensions

| Table | Proposed grain | Notes |
| --- | --- | --- |
| `tbl_Calendar` | One row per date. | Mark as the date table. |
| `ca_MVRPT_ACCOUNT` | One row per account code. | Keep external until availability is confirmed. |
| `ca_MVRPT_COSTCENTRES` | One row per cost centre code. | Keep external until availability is confirmed. |
| `tbl_Email_Addresses` | One row per contact. | Operational dependency only; not a reporting dimension. |

### Relationship Proposal

| From | To | Cardinality | Direction | Status |
| --- | --- | --- | --- | --- |
| `tbl_Calendar[Date]` | `tbl_GL_Transactions[Date]` | 1:* | Single | Active |
| `tbl_Calendar[Date]` | `tbl_VMO_Data[Date]` | 1:* | Single | Active if the loaded source has a true date column. |
| `tbl_Calendar[Date]` | `tbl_Reconciliation_GL_Data[Date]` | 1:* | Single | Active |
| `tbl_Calendar[Date]` | `tbl_Reconciliation_VMO_Data[Date]` | 1:* | Single | Active |
| `tbl_Calendar[Date]` | `tbl_VMO_GL_Transactions[Date]` | 1:* | Single | Active |
| `ca_MVRPT_ACCOUNT[Account Code]` | transaction and reconciliation fact account fields | 1:* | Single | Proposed |
| `ca_MVRPT_COSTCENTRES[Cost Centre Code]` | transaction and reconciliation fact cost-centre fields | 1:* | Single | Proposed |

Notes:

- Keep fact-to-fact relationships out of the model.
- Use account and cost-centre dimensions only after the imported field names are confirmed against the Access export.
- Use `qry_Reconciliation_GL_Summary` and `qry_Reconciliation_GL_Summary_Other_Subsystems` for validation and design review, not as a substitute for the core model grain.

## Measures Catalogue

The expressions below are DAX skeletons. Replace field names only if the Access export uses a different label.

| Measure | Table | DAX skeleton | Purpose |
| --- | --- | --- | --- |
| `Total GL Amount` | `tbl_GL_Transactions` | `SUM ( tbl_GL_Transactions[Amount] )` | Baseline GL total. |
| `Total VMO Amount` | `tbl_VMO_Data` | `SUM ( tbl_VMO_Data[Amount] )` | Baseline VMO total. |
| `GL Row Count` | `tbl_GL_Transactions` | `COUNTROWS ( tbl_GL_Transactions )` | Record volume. |
| `VMO Row Count` | `tbl_VMO_Data` | `COUNTROWS ( tbl_VMO_Data )` | Record volume. |
| `Reconciliation Variance` | `tbl_VMO_GL_Transactions` | `[Total GL Amount] - [Total VMO Amount]` | Headline delta. |
| `Reconciliation Variance %` | `tbl_VMO_GL_Transactions` | `DIVIDE ( [Reconciliation Variance], [Total GL Amount] )` | Normalized delta. |
| `Matched Rows` | `tbl_Reconciliation_GL_Data` | `CALCULATE ( COUNTROWS ( tbl_Reconciliation_GL_Data ), tbl_Reconciliation_GL_Data[Match Status] = "Matched" )` | Matched reconciliation rows. |
| `Unmatched GL Rows` | `tbl_Reconciliation_GL_Data` | `CALCULATE ( COUNTROWS ( tbl_Reconciliation_GL_Data ), tbl_Reconciliation_GL_Data[Match Status] <> "Matched" )` | GL rows needing review. |
| `Unmatched VMO Rows` | `tbl_Reconciliation_VMO_Data` | `CALCULATE ( COUNTROWS ( tbl_Reconciliation_VMO_Data ), tbl_Reconciliation_VMO_Data[Match Status] <> "Matched" )` | VMO rows needing review. |
| `Exception Rows` | `tbl_Reconciliation_GL_Data` | `CALCULATE ( COUNTROWS ( tbl_Reconciliation_GL_Data ), tbl_Reconciliation_GL_Data[Exception Flag] = TRUE () )` | Exception summary. |
| `Other Subsystems Variance` | `qry_Reconciliation_GL_Summary_Other_Subsystems` | `SUM ( qry_Reconciliation_GL_Summary_Other_Subsystems[Variance Amount] )` | Non-VMO variance check. |
| `Financial Year Total` | `tbl_Calendar` | `CALCULATE ( [Total GL Amount], ALLEXCEPT ( tbl_Calendar, tbl_Calendar[Financial Year] ) )` | Year-level control total. |
| `Period Total` | `tbl_Calendar` | `CALCULATE ( [Total GL Amount], ALLEXCEPT ( tbl_Calendar, tbl_Calendar[Financial Year], tbl_Calendar[Period] ) )` | Period-level control total. |

Recommended measure folders:

- `Totals`
- `Reconciliation`
- `Exceptions`
- `Validation`

## Validation Checks Against Access Exports

Use exported Access query results or saved table extracts under ignored `data/profile/` or `data/extracts/` paths for the current interim validation pass. After the SQL host is available, rerun the same checks against SQL Server sample extracts before enabling published refresh.

The concrete acceptance pack for the no-SQL-host phase is
`conductor/tracks/vmo-dashboard-completion/acceptance-pack.md`. It defines the
sample-result checks, measure-by-measure verification, reconciliation
acceptance table, and SQL-host-dependent checks that remain open.

| Check | Source comparison | Expected result |
| --- | --- | --- |
| GL total by financial year | `qry_Financial_Year_Total` vs `Total GL Amount` | Exact match by year and period bucket. |
| Reconciliation summary by status | `qry_Reconciliation_GL_Summary` vs Power BI reconciliation matrix | Exact match for counts and variance. |
| Other subsystem variance | `qry_Reconciliation_GL_Summary_Other_Subsystems` vs validation measure | Exact match or explained difference. |
| Local Access table row counts | Access table export vs Power BI import count | Exact match for each local table before SQL binding. |
| Null key check | Exported data vs Power BI data model | No unexpected nulls in date, account, cost-centre, or classification keys. |
| Duplicate key check | Exported data vs Power BI data model | No unexpected duplicates at the proposed grain. |
| Unmatched classification rows | `tbl_VMO_GL_Classification` and reconciliation rows | Count equals Access-side exception count. |
| Dependency readiness | `tbl_Excel_VMO_Data`, `ca_MVRPT_ACCOUNT`, `ca_MVRPT_COSTCENTRES`, `dbo_FMIS_GL_JOURNAL` | Each dependency is either reachable or explicitly documented as blocked. |

## M Query Templates For Local Tables

Use the same Access source path for every local table query. The current checked-in templates use `data/raw/VMO Reporting.accdb`; Desktop can promote this to an `AccessDatabasePath` parameter during the interim validation build.

### Shared Source Pattern

```powerquery
let
    AccessDatabasePath = "data/raw/VMO Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true])
in
    Source
```

### Table Template Pattern

```powerquery
let
    AccessDatabasePath = "data/raw/VMO Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true]),
    Navigation = Source{[Item = "tbl_Calendar", Kind = "Table"]}[Data]
in
    Navigation
```

### Local Table Template Set

- `tbl_Calendar`
- `tbl_GL_Transactions`
- `tbl_Reconciliation_GL_Data`
- `tbl_Reconciliation_VMO_Data`
- `tbl_VMO_Data`
- `tbl_VMO_GL_Classification`
- `tbl_VMO_GL_Transactions`

The same pattern applies to each local table; only the navigation name changes. Keep view logic and pass-through dependency handling separate from these local-table templates.

## SQL Server Parallel Templates

The published-refresh templates live under `src/powerbi/dashboards/vmo-finance/m/sql/`.
They mirror the Access-backed query names so the SQL-bound model can swap source
blocks without changing the table contract.

The templates assume the agreed SQL Server parameters:

- `SqlServerName`
- `SqlDatabaseName`
- `SqlSchemaName`

Set `SqlSchemaName` to `dbo` unless the final SQL contract uses a different
owner.

The table templates now reference `SqlServerName`, `SqlDatabaseName`, and
`SqlSchemaName` as Power BI query parameters. They do not assign local
placeholder strings, so the live model must create or bind those parameters
before SQL Server refresh.

## Live Build Handoff

The main implementation thread can use
`src/powerbi/dashboards/vmo-finance/pbi-cli-implementation-checklist.md` as the
short pbi-cli runbook. The expected sequence is:

1. Connect pbi-cli to the live Desktop model.
2. In the no-SQL-host interim state, load the Access templates and confirm Access row-count/schema parity.
3. Rename loaded query tables to the model names in the measure catalogue.
4. Mark `Date[Date]` as the date table.
5. Create only the confirmed relationships from `model-tmdl/relationship-checklist.md`.
6. Create measures from `model-tmdl/measure-catalogue.md`.
7. Build report pages from `report/page-completion-checklist.md`.
8. Run the Access validation checks and keep generated TMDL/PBIR source artifacts current.
9. When SQL Server is available, bind SQL parameters, confirm schema parity against `docs/sql-server-publish-plan.md`, and rerun the validation checks.

## Validation Notes

Validation is still pending against source extracts. The checklist at
`src/powerbi/dashboards/vmo-finance/report/validation-checklist.md` captures the
exact comparisons to run first against the Access sample and later against SQL
Server once credentials and host details are available.

The current track does not claim SQL Server refresh readiness until the later
binding and validation pass is complete.

Acceptance can be recorded for the interim Access-sample build when the
acceptance table in
`conductor/tracks/vmo-dashboard-completion/acceptance-pack.md` has no failed
checks and every non-zero delta has a documented finance-approved explanation.
