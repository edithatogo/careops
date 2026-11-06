# SQL Server Publish Plan

## Decision

The Access databases stay as profiling inputs only. Published Power BI refresh should come from SQL Server tables or views that preserve the same business contracts used by the standalone VMO Finance and Medical Staff dashboard models.

## Contract Parameters

- `SqlServerName`
- `SqlDatabaseName`
- default SQL schema: `dbo`

Supply `SqlServerName` through the private operator profile; public examples use `<sql-server-host>`.

Keep this as a Power BI parameter/deployment value rather than hard-coding it
inside M queries. The database name, schema confirmation, gateway binding, and
credential mode are still open publish-readiness inputs.

The source starter lives in [`src/powerbi/shared/m/SqlServerSourceTemplate.m`](../src/powerbi/shared/m/SqlServerSourceTemplate.m) and the structured contract lives in [`src/powerbi/shared/m/SqlContracts.m`](../src/powerbi/shared/m/SqlContracts.m).

## Gateway Assumptions

- An on-premises data gateway can reach the SQL Server host used for published refresh.
- Authentication, gateway registration, and refresh credentials are managed outside this repository.
- Database names, usernames, passwords, and secrets stay out of source control. The operator-supplied SQL host/listener stays in the private deployment profile; public handoff uses `<sql-server-host>`.
- The published model can read the agreed `dbo` objects without depending on Access files.

## Source Host Discovery Evidence

Before enabling publish-time SQL bindings, an operator should run the DSN validation on the source computer that already has working Access ODBC configuration:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\dsn\Test-OdbcDsnSourceContract.ps1 -WriteEvidence
```

The evidence file is written to ignored `data/profile/odbc-dsn-source-contract.evidence.json`. It must not be committed. Use it to confirm:

- `CA` resolves to a found ODBC DSN with a SQL Server host/listener and the expected `WORKFORCE` default database, if configured.
- `Magiq` resolves to a found ODBC DSN with a SQL Server host/listener and the expected `MAGIQ_PRD` default database for Medical Staff source objects, if configured.
- DSN host/listener evidence should agree with the operator-supplied host `<sql-server-host>`, or any difference must be recorded as an environment-specific alias/listener decision.
- The VMO GL object `dbo.FMIS_GL_JOURNAL_2026` has its database resolved from the `Magiq` DSN or a later live SQL check, because Access did not expose that database in its linked-table connection string.
- The evidence remains redacted: operator identity fields and sensitive DSN registry keys are stored as `<redacted>`.

## Local Development

Use limited Access extracts to inspect shape and validate early transformations:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-DashboardSources.ps1 -Dashboard vmo-finance -MaxRows 1000
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-DashboardSources.ps1 -Dashboard medical-staff -MaxRows 1000
```

Use `-MaxRows 0` only when a full local export is actually needed.

## SQL Server Contract Summary

### Shared contracts

| SQL object | Kind | Grain | Keys | Minimum columns | Model target |
| --- | --- | --- | --- | --- | --- |
| `dbo.tbl_Calendar` | table | One row per date | `Date` | `Date`, `Financial Year`, `Period`, `Calendar Year`, `Calendar Month`, `Quarter` | `Date` |
| `dbo.tbl_WF_Calendar` | table | One row per date or reporting period | `Date` | `Date`, `Financial Year`, `Period`, `Calendar Year`, `Calendar Month`, `Quarter` | `Workforce Calendar` |
| `dbo.ca_MVRPT_COSTCENTRES` | table or view | One row per cost-centre code | `Cost Centre Code` | `Cost Centre Code`, `Cost Centre Name`, `Cost Centre Group`, `Status` | `Cost Centre` |
| `dbo.ca_MVRPT_ACCOUNT` | table or view | One row per account code | `Account Code` | `Account Code`, `Account Name`, `Account Group`, `Status` | `Account` |

### VMO Finance contract

| SQL object | Kind | Grain | Keys | Minimum columns | Model target |
| --- | --- | --- | --- | --- | --- |
| `dbo.tbl_GL_Transactions` | table | One row per GL posting line | `GL Transaction ID` | `GL Transaction ID`, `Date`, `Financial Year`, `Period`, `Account Code`, `Cost Centre Code`, `Amount`, `Narrative`, `Source Reference`, `Posted Date` | `GL Transactions` |
| `dbo.tbl_VMO_Data` | table | One row per VMO source record | `VMO Record ID` | `VMO Record ID`, `Date`, `Financial Year`, `Period`, `Account Code`, `Cost Centre Code`, `Amount`, `Narrative` | `VMO Data` |
| `dbo.tbl_VMO_GL_Transactions` | table | One row per mapped GL line | `VMO GL Transaction ID` | `VMO GL Transaction ID`, `GL Transaction ID`, `VMO Record ID`, `Date`, `Account Code`, `Cost Centre Code`, `Amount`, `Match Status`, `Variance Amount` | `VMO GL Transactions` |
| `dbo.tbl_VMO_GL_Classification` | table | One row per classification rule or lookup row | `Classification Key` | `Classification Key`, `Account Code`, `Classification`, `Subclassification`, `Effective From`, `Effective To`, `Is Active` | `VMO GL Classification` |
| `dbo.tbl_Reconciliation_GL_Data` | table | One row per GL-side reconciliation row | `Reconciliation GL Row ID` | `Reconciliation GL Row ID`, `Date`, `Financial Year`, `Period`, `Account Code`, `Cost Centre Code`, `Amount`, `Match Status`, `Exception Flag`, `Variance Amount` | `Reconciliation GL Data` |
| `dbo.tbl_Reconciliation_VMO_Data` | table | One row per VMO-side reconciliation row | `Reconciliation VMO Row ID` | `Reconciliation VMO Row ID`, `Date`, `Financial Year`, `Period`, `Account Code`, `Cost Centre Code`, `Amount`, `Match Status`, `Exception Flag`, `Variance Amount` | `Reconciliation VMO Data` |
| `dbo.qry_Financial_Year_Total` | view | One row per financial-year and period bucket | `Financial Year`, `Period` | `Financial Year`, `Period`, `Total GL Amount` | validation only |
| `dbo.qry_Reconciliation_GL_Data` | view | One row per reconciliation detail row | `Reconciliation GL Row ID` | `Reconciliation GL Row ID`, `Match Status`, `Variance Amount` | validation only |
| `dbo.qry_Reconciliation_GL_Summary` | view | One row per summary bucket | `Financial Year`, `Period`, `Match Status` | `Financial Year`, `Period`, `Match Status`, `Row Count`, `Variance Amount` | validation only |
| `dbo.qry_Reconciliation_GL_Summary_Other_Subsystems` | view | One row per summary bucket | `Financial Year`, `Period`, `Subsystem` | `Financial Year`, `Period`, `Subsystem`, `Row Count`, `Variance Amount` | validation only |

### Medical Staff contract

| SQL object | Kind | Grain | Keys | Minimum columns | Model target |
| --- | --- | --- | --- | --- | --- |
| `dbo.tbl_Medical_Staff_Data` | table | One row per current staff record or pay-period snapshot | `Staff ID` | `Staff ID`, `Date`, `Financial Year`, `Period`, `Staff Status`, `FTE`, `Payroll Amount`, `Department`, `Grade`, `Record State` | `Medical Staff Data` |
| `dbo.tbl_Medical_Staff_History` | table | One row per history event or effective-dated version | `History Row ID` | `History Row ID`, `Staff ID`, `Effective Date`, `End Date`, `Record State`, `Event Type`, `FTE`, `Payroll Amount`, `Department`, `Grade` | `Medical Staff History` |
| `dbo.qry_Medical_Staff_Data` | view | One row per staff record or snapshot row | `Staff ID` | `Staff ID`, `Staff Status`, `FTE`, `Payroll Amount` | validation only |
| `dbo.qry_Combo_Medical_Payroll_Data` | view | One row per staff member per payroll period and pay component | `Payroll Row ID` | `Payroll Row ID`, `Staff ID`, `Date`, `Financial Year`, `Period`, `Pay Component`, `Payroll Amount`, `FTE` | `Medical Payroll Data` |
| `dbo.qry_Employee_Sub` | view | One row per employee-subordinate or employee-attribute mapping | `Employee ID`, `Subordinate ID` | `Employee ID`, `Subordinate ID`, `Department`, `Grade`, `Status` | `Employee Sub` |

## Source-To-Model Mapping

- VMO Finance keeps the current row-level facts separate: `GL Transactions`, `VMO Data`, `VMO GL Transactions`, `Reconciliation GL Data`, and `Reconciliation VMO Data`.
- `Date` comes from `dbo.tbl_Calendar` and remains the canonical finance date dimension.
- `Workforce Calendar` comes from `dbo.tbl_WF_Calendar` and stays separate until a future merge gate says it can be conformed.
- Medical Staff keeps current-state and history state separate: `Medical Staff Data` and `Medical Staff History`.
- `Medical Payroll Data` is a separate view contract because the payroll/FTE source is not yet proven to share the same grain as the staff snapshot.
- Validation views are named and documented, but they are not a replacement for the base fact tables.

## Open Source Gaps

### VMO Finance

- Confirm whether the reconciliation objects are materialized tables or views in SQL Server.
- Confirm the final key columns for the GL, VMO, and reconciliation rows.
- Confirm whether the account and cost-centre lookups live in the same database.
- Confirm the authoritative date fields for posting date, financial date, and reporting period.
- Confirm amount precision and rounding rules.

### Medical Staff

- Confirm whether the staff data and history objects are snapshots or fully effective-dated tables.
- Confirm whether payroll amount is gross pay, total pay, or another contract amount.
- Confirm the canonical staff identifier across current, history, and payroll rows.
- Confirm whether the workforce calendar is aligned to finance periods or a separate calendar hierarchy.
- Confirm whether `qry_Employee_Sub` stays as a view or later becomes a dimension table.

### Shared

- Confirm whether `dbo.tbl_Email_Addresses` and `dbo.dbo_FMIS_GL_JOURNAL` are published SQL objects or only Access-side dependencies for now.
- Confirm whether published refresh will use one SQL database for both dashboards or separate databases.
- Confirm whether the `dbo` schema is final or only the default placeholder.

## Next Build Step

The next step is not more guessing. Once SQL Server access is available, confirm the real object names, keys, and data types against these contracts, then wire the published Power BI refresh to those objects.
