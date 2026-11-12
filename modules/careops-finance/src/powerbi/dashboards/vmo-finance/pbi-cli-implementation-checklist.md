# VMO Finance pbi-cli Implementation Checklist

This is the concise build handoff for the main thread. It assumes Power BI Desktop is already open on the target PBIP/model. In the no-SQL-host interim state, load the local Access templates from `m/` and run sample validation first; import `m/sql/` only when the SQL Server host and credentials are ready. Do not run Desktop mutation from this worker.

## 1. Connect And Inspect

```powershell
pbi connect
pbi table list
pbi relationship list
pbi measure list
```

For Access-sample validation, confirm the source path parameter or literal points to:

- `data/raw/VMO Reporting.accdb`

For later SQL Server binding, confirm these parameters exist before refresh:

- `SqlServerName`
- `SqlDatabaseName`
- `SqlSchemaName` with default `dbo`

## 2. Load/Rename Tables

Create or confirm the model table names:

| Source query | Target model table |
| --- | --- |
| `tbl_Calendar` | `Date` |
| `tbl_GL_Transactions` | `GL Transactions` |
| `tbl_VMO_Data` | `VMO Data` |
| `tbl_VMO_GL_Transactions` | `VMO GL Transactions` |
| `tbl_VMO_GL_Classification` | `VMO GL Classification` |
| `tbl_Reconciliation_GL_Data` | `Reconciliation GL Data` |
| `tbl_Reconciliation_VMO_Data` | `Reconciliation VMO Data` |

In the interim Access build, verify field names and row counts against the Access sample exports. After SQL Server is available, verify schema parity with the SQL contract in `docs/sql-server-publish-plan.md` before rebinding the same model table contract.

## 3. Build Model

```powershell
pbi table mark-date Date --date-column Date
```

Create only the active date relationships and confirmed lookup relationships listed in `model-tmdl/relationship-checklist.md`. Keep GL, VMO, mapped, and reconciliation tables as separate facts.

## 4. Create Measures

Create a `VMO Measures` table if the model does not already have a measure table. Add measures from `model-tmdl/measure-catalogue.md`, using display folders and format strings from the catalogue.

For multi-line DAX, pipe the expression through stdin:

```powershell
@'
[Total GL Amount] - [Total VMO Amount]
'@ | pbi measure create "Reconciliation Variance" -t "VMO Measures" -e - --format-string "$#,##0;($#,##0);-"
```

## 5. Build Report Pages

Use `report/page-completion-checklist.md` for the page-level visual and filter list:

- Executive Summary
- Reconciliation Detail
- Classification And Cost Centre
- Exceptions
- Transaction Detail
- Validation

## 6. Validate And Export

Run the Access-sample checks in `report/validation-checklist.md`, then export or revalidate the model/report source:

```powershell
pbi table list
pbi relationship list
pbi measure list
pbi report validate
```

After Access validation, keep the generated TMDL/PBIR folders current. Repeat the refresh and validation checks after SQL Server binding before treating the published refresh path as production-ready.
