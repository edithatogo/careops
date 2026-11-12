# Medical Staff Dashboard

Standalone Power BI project for Medical Staff reporting.

## Source

`data/raw/Medical_Staff_Reporting.accdb`

## Initial Scope

- Medical staff summary by period.
- Headcount/FTE/payroll reporting where supported by available source tables.
- Staff history and workforce-calendar trends.
- Dependency review for payroll/FTE pass-through objects.

## Source-Control Folders

- `m/` - dashboard-specific Power Query templates.
- `m/*.SqlServer.m` - SQL Server refresh templates for published refresh.
- `model-tmdl/` - dashboard model TMDL export.
- `report/` - report source artifacts.
- `Dataset/` - pbi-tools dataset source placeholder.

## Current Completion Artifacts

- `model-tmdl/measure-catalogue.md` - DAX measure catalogue for the standalone model.
- `report/page-completion-checklist.md` - report page completion checklist.
- `report/validation-checklist.md` - validation checklist for Access or SQL Server sample checks.
- `report/export-instructions.md` - TMDL and report export placeholders.
