# Medical Staff Acceptance Pack

Status: concrete acceptance pack for work possible before the SQL Server host is known.

This pack covers the Access-sample build, source-controlled model/report artifacts, documented DAX, and reviewer-facing evidence tables. It does not close SQL refresh acceptance.

## Acceptance Boundary

| Area | Accepted before SQL host is known | Deferred until SQL host is known |
| --- | --- | --- |
| Source extracts | Access sample row counts and tie-outs from `data/raw/Medical_Staff_Reporting.accdb`. | SQL object row counts and source snapshots. |
| Model | Documented table grains, relationships, and DAX catalogue. | Live SQL-loaded semantic model with confirmed data types and keys. |
| Report | Page/visual contract and generated PBIR structure checks. | Service refresh and production workspace publish readiness. |
| Refresh | Local Access-sample refresh evidence only. | Gateway, credentials, SQL host/database/schema, and scheduled refresh. |

## Sample-result Checks

| Check ID | Source object | Model/report target | Check to perform | Acceptance result |
| --- | --- | --- | --- | --- |
| MS-SAMPLE-01 | `tbl_Medical_Staff_Data` | `FactMedicalStaffCurrent` | Compare source row count to imported model row count. | Must match exactly. |
| MS-SAMPLE-02 | `tbl_Medical_Staff_Data`, `qry_Medical_Staff_Data` | `[Medical Staff Count]` | Compare distinct `Staff ID` for the same period/status filters. | Must match, or variance is documented with owner. |
| MS-SAMPLE-03 | `tbl_Medical_Staff_Data` | `[Active Staff Count]` | Compare distinct active staff count. | Must match, or non-standard statuses are documented. |
| MS-SAMPLE-04 | `tbl_Medical_Staff_Data` | `[Medical Staff FTE]` | Compare total `FTE`. | Must match after accepted numeric rounding. |
| MS-SAMPLE-05 | `qry_Combo_Medical_Payroll_Data` | `[Medical Payroll Amount]` | Compare payroll totals by financial year, period, and pay component. | Must match after accepted currency rounding. |
| MS-SAMPLE-06 | `tbl_Medical_Staff_History` | `[History Row Count]` | Compare history row count. | Must match exactly. |
| MS-SAMPLE-07 | `tbl_Medical_Staff_History` | `[Missing Effective Date Count]` | Count blank effective dates. | Must match and exceptions must be explainable. |
| MS-SAMPLE-08 | `tbl_Medical_Staff_History` | `[Duplicate Staff Record Count]` | Count duplicate `Staff ID` plus `Effective Date` combinations. | Must match and duplicates must be listed as exceptions. |
| MS-SAMPLE-09 | `tbl_WF_Calendar` | `DimWorkforceCalendar` | Check min/max date, duplicate dates, and unexpected gaps. | Calendar range supports all accepted reporting periods. |
| MS-SAMPLE-10 | `report/pbir/MedicalStaff` | Report pages and visuals | Compare generated pages/visual IDs to `report-implementation-spec.md`. | Page and visual inventory matches the spec. |

## DAX Measures To Verify

| Group | Measures | Acceptance evidence |
| --- | --- | --- |
| Headcount | `Medical Staff Count`, `Active Staff Count`, `Inactive Staff Count`, `Medical Staff Row Count` | Current-staff source counts and status-filtered counts. |
| FTE | `Medical Staff FTE`, `FTE per Staff` | Current-staff FTE total and derived FTE per staff. |
| Payroll | `Medical Payroll Amount`, `Payroll per Staff` | Payroll amount by financial year, period, and pay component. |
| Trends | Staff, FTE, and payroll prior-period/delta/delta-percent measures | Workforce-calendar period order and accepted period selections. |
| History | `History Row Count`, `Current Record Count`, `Historical Record Count`, `History Coverage %`, `Open History Records` | History row counts, current/historical state counts, blank end-date counts. |
| Data quality | `Duplicate Staff Record Count`, `Missing Effective Date Count` | Duplicate grain and blank effective-date checks. |
| Validation | `Source Object Count`, `Missing Source Count`, `Validation Pass Count`, `Validation Fail Count` | Source inventory and validation-check rows. |

## Headcount/FTE/Payroll/History Acceptance Table

| Period scope | Headcount source | Headcount DAX | FTE source | FTE DAX | Payroll source | Payroll DAX | History source rows | History DAX rows | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| All sample periods | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |
| Earliest complete period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |
| Latest complete period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |
| Highest payroll period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |

## SQL-host-dependent Checks Left Open

| Check ID | Check | Dependency |
| --- | --- | --- |
| MS-SQL-01 | Confirm `SqlServerName`, `SqlDatabaseName`, and final schema. | SQL host/database/schema. |
| MS-SQL-02 | Confirm contract object existence. | Live SQL metadata. |
| MS-SQL-03 | Confirm required columns, data types, precision, and nullability. | Live SQL metadata and sample snapshots. |
| MS-SQL-04 | Confirm staff, history, payroll, and calendar keys at documented grains. | Production-like SQL rows. |
| MS-SQL-05 | Confirm payroll amount definition and rounding. | Source-owner approval. |
| MS-SQL-06 | Confirm workforce-calendar alignment with finance periods or separate workforce hierarchy. | SQL calendar source and business approval. |
| MS-SQL-07 | Confirm gateway and credentials. | Power BI Service/gateway configuration. |
| MS-SQL-08 | Confirm published refresh and scheduled refresh readiness. | Live SQL binding and gateway success. |

## Focused Validation Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Invoke-Validation.ps1 -Mode RepositoryHygiene -SkipPowerBiCli
git diff -- docs/medical-staff-dashboard.md src/powerbi/dashboards/medical-staff/report/validation-checklist.md src/powerbi/dashboards/medical-staff/model-tmdl/measure-catalogue.md conductor/tracks/medical-staff-dashboard-completion/acceptance-pack.md
git diff --name-only -- src/powerbi/dashboards/medical-staff/m src/powerbi/dashboards/medical-staff/report/pbir src/powerbi/dashboards/medical-staff/model-tmdl/live-export
```

The final command should show no edited M templates, generated PBIR, or generated TMDL live-export files for this worker.
