# Medical Staff Dashboard Live Implementation Checklist

This is the main-thread handoff for building the live Power BI implementation with pbi-cli. It does not require this worker to mutate Power BI Desktop.

## Inputs To Confirm

- [ ] SQL Server access works for the agreed server and database.
- [ ] `dbo` is still the schema for Medical Staff objects, or the revised schema has been recorded.
- [ ] The SQL objects in `docs/sql-server-publish-plan.md` exist with the required columns.
- [ ] The target PBIP or dataset is ready for pbi-cli operations.
- [ ] Gateway and credentials are handled outside git.

## Model Build

- [ ] Load SQL M templates from `src/powerbi/dashboards/medical-staff/m/`.
- [ ] Rename loaded tables to `FactMedicalStaffCurrent`, `FactMedicalStaffHistory`, `FactMedicalPayroll`, `DimEmployeeSub`, `DimWorkforceCalendar`, and `ValidationMedicalStaffData`.
- [ ] Hide `ValidationMedicalStaffData` and any helper validation/check tables from report consumers.
- [ ] Mark `DimWorkforceCalendar[Date]` as the date table.
- [ ] Create relationships from `src/powerbi/dashboards/medical-staff/model-tmdl/relationship-checklist.md`.
- [ ] Create DAX measures from `src/powerbi/dashboards/medical-staff/model-tmdl/measure-catalogue.md`.

## Report Build

- [ ] Create pages from `src/powerbi/dashboards/medical-staff/report/page-completion-checklist.md`.
- [ ] Add KPI, trend, payroll, history, source-dependency, and validation visuals.
- [ ] Add slicers for financial year, period, staff status, record state, department, grade, source class, load status, and validation result.
- [ ] Keep validation-only fields off consumer-facing pages unless they are on the Source Dependencies and Validation page.

## pbi-cli Command Skeleton

```powershell
pbi connect
pbi table list
pbi relationship list
pbi measure list
pbi table mark-date DimWorkforceCalendar --date-column Date
pbi report --no-sync add-page --display-name "Medical Staff Overview" --name medical_staff_overview
pbi report --no-sync add-page --display-name "Staff History" --name staff_history
pbi report --no-sync add-page --display-name "Source Dependencies and Validation" --name source_validation
pbi report validate
pbi database export-tmdl .\src\powerbi\dashboards\medical-staff\model-tmdl
```

For multi-line DAX, pipe the expression into `pbi measure create "Measure Name" -e - -t "Table Name"` rather than passing the expression as one shell argument.

## Validation Gate

- [ ] SQL contract columns load without M errors.
- [ ] Row counts match SQL snapshots for `tbl_Medical_Staff_Data`, `tbl_Medical_Staff_History`, `qry_Combo_Medical_Payroll_Data`, and `tbl_WF_Calendar`.
- [ ] Staff count, active staff count, FTE, and payroll totals tie out by period.
- [ ] History duplicate and missing-date measures produce expected exception counts.
- [ ] No relationship requires bidirectional filtering for the planned visuals.
- [ ] Exported TMDL/report artifacts are real outputs from the live build, not placeholders.
