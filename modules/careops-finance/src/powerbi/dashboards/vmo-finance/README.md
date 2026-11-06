# VMO Finance Dashboard

Standalone Power BI project for VMO finance reporting.

## Source

Interim validation source: `data/raw/VMO Reporting.accdb`.

Published refresh source: later SQL Server binding through the templates in
`m/sql/` using `SqlServerName`, `SqlDatabaseName`, and `SqlSchemaName`.

## Initial Scope

- VMO totals by financial year and period.
- GL versus VMO reconciliation.
- Classification and variance analysis.
- Exception views for rows requiring finance review.

## Source-Control Folders

- `m/` - dashboard-specific Power Query templates.
- `m/sql/` - SQL-backed parallel Power Query templates for published refresh.
- `model-tmdl/` - dashboard model notes plus generated TMDL export folder.
- `report/` - report implementation package, generated PBIR folder, completion checklist, and validation notes.
- `pbi-cli-implementation-checklist.md` - concise live-build handoff for the main thread.
- `Dataset/` - pbi-tools dataset source placeholder.
