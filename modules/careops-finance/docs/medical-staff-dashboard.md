# Medical Staff Dashboard Design

## Objective

Build a standalone Power BI dashboard for Medical Staff reporting. Access extracts remain the local profiling source; published refresh is expected to move to SQL Server once the source contract is available.

The dashboard should stay isolated under `src/powerbi/dashboards/medical-staff/` until the business definitions and source dependencies are stable enough to promote shared definitions.

## Current Delivery State

- Access-backed M templates exist for local profiling.
- SQL Server Power Query templates are available for the base tables and contract views, with explicit required-column selection, data typing, and model-column renames.
- A DAX measure catalogue is documented for the standalone model, aligned to the normalized model column names from the SQL templates.
- Relationship, report page, validation, and export instructions are documented as completion artifacts.
- Local Access sample validation and generated export artifacts exist for the interim build; published SQL Server refresh binding remains pending until the database contract, host, database, schema, gateway, and credentials are available.
- The PBIR report package is already exported; the remaining completion work is verification and acceptance evidence, not new report export generation.

## Interim No-SQL-Host State

Use the Access-backed templates to validate the current sample build and business logic. These checks prove row counts, grains, relationships, measures, and report structure against `data/raw/Medical_Staff_Reporting.accdb`; they do not prove that the later SQL Server objects exist or refresh successfully.

Use the SQL Server templates as the forward contract for published refresh. Bind `SqlServerName` to the supplied host/listener `<sql-server-host>` through Power BI parameters or deployment configuration, and keep database/schema/gateway values external until confirmed:

| Placeholder | Purpose | Interim value |
| --- | --- | --- |
| `SqlServerName` | SQL Server host or listener name for published refresh | `SET_BY_PARAMETER` |
| `SqlDatabaseName` | target SQL database name | `SET_BY_PARAMETER` |
| `SqlSchemaName` | source schema for the contract tables/views | `dbo` unless revised |

Do not treat successful Access validation as SQL readiness. Before switching from Access sample validation to SQL Server refresh, run the SQL contract checks in `src/powerbi/dashboards/medical-staff/report/validation-checklist.md`.

## Source Inventory

### Local tables

- `tbl_Medical_Staff_Data`
- `tbl_Medical_Staff_History`
- `tbl_WF_Calendar`

### Views

- `qry_Combo_Medical_Payroll_Data`
- `qry_Employee_Sub`
- `qry_Medical_Staff_Data`

### Linked or pass-through dependencies

- payroll/FTE pass-through objects
- `tbl_Calendar`
- `tbl_Email_Addresses`
- `tbl_VMO_Data`

## Model Grain And Relationships Proposal

### Proposed grain

- `qry_Medical_Staff_Data` or `tbl_Medical_Staff_Data`: one row per staff member in the current medical staff snapshot.
- `tbl_Medical_Staff_History`: one row per staff member per effective-dated history record or change event.
- `qry_Combo_Medical_Payroll_Data`: one row per staff member per payroll period and pay component.
- `qry_Employee_Sub`: one row per employee-subordinate or employee-attribute mapping, used as a bridge or helper dimension if the source is not already flattened.
- `tbl_WF_Calendar`: one row per workforce calendar date or period.

### Proposed tables

- `FactMedicalStaffCurrent` from `tbl_Medical_Staff_Data`
- `FactMedicalStaffHistory` from `tbl_Medical_Staff_History`
- `FactMedicalPayroll` from `qry_Combo_Medical_Payroll_Data`
- `DimEmployeeSub` from `qry_Employee_Sub`
- `DimWorkforceCalendar` from `tbl_WF_Calendar`
- `DimCalendar` from `tbl_Calendar` if the linked calendar is required for shared period logic

### Relationship proposal

- `DimWorkforceCalendar[Date]` to each fact table date or period date column, single direction, one-to-many.
- `DimEmployeeSub[EmployeeID]` to current, history, and payroll facts on the staff key, single direction, one-to-many.
- `DimCalendar` only if the linked `tbl_Calendar` object is confirmed stable; otherwise keep it documented but not active.
- `tbl_VMO_Data` remains a documented dependency for cross-dashboard comparisons, not a default relationship unless the dashboard needs a VMO bridge.

### Modeling notes

- Keep the payroll source and the staff history source separate unless the Access export proves they are at the same grain.
- Use `tbl_WF_Calendar` for workforce-period reporting; use `tbl_Calendar` only where a linked finance calendar is required.
- Prefer explicit helper measures over calculated columns for period-based totals.
- Treat missing pass-through objects as a documented refresh dependency, not as a silent model assumption.
- Rename SQL source columns with spaces to stable model fields in Power Query, for example `Staff ID` to `StaffID` and `Payroll Amount` to `PayrollAmount`.
- Hide validation-only tables after loading them; they support tie-outs but should not drive report visuals.

## Measures Catalogue

The expressions below are planning artifacts only. Bind the table and column names to the exported Access or SQL Server schema when the final load shape is confirmed.

See `src/powerbi/dashboards/medical-staff/model-tmdl/measure-catalogue.md` for the maintained catalogue.
See `src/powerbi/dashboards/medical-staff/model-tmdl/relationship-checklist.md` for the live relationship build checklist.

## Report Page Completion Checklist

Use this list as the build gate before Power BI Desktop export.

### Page 1: Medical Staff Overview

- [ ] KPI cards for staff count, active staff, FTE, and payroll amount.
- [ ] Trend line for headcount and FTE by period.
- [ ] Payroll chart by period.
- [ ] Matrix for department, grade, or other workforce slices.
- [ ] Period, record-state, and source filters applied.

### Page 2: Staff History

- [ ] Timeline or trend chart for history row volume.
- [ ] Current versus historical record matrix by period.
- [ ] Staff-level history detail table.
- [ ] Exception view for overlapping or missing effective dates.
- [ ] Staff identifier, period, and history-state filters applied.

### Page 3: Source Dependencies and Validation

- [ ] Source status matrix for local, linked, and pass-through objects.
- [ ] Validation summary cards.
- [ ] Dependency gap table with object name, expected source, and load status.
- [ ] Source class, load status, and object type filters applied.

## Validation Checklist

Use exported Access extracts for the interim local build. Use SQL Server sample snapshots later, after the SQL host and contract objects are available, to confirm the published refresh path before refresh automation is enabled.

| Check | Source | Expected result |
| --- | --- | --- |
| Local table row count parity | `tbl_Medical_Staff_Data`, `tbl_Medical_Staff_History`, `tbl_WF_Calendar` | Power BI import row counts match the source extract row counts |
| Access sample model parity | `data/raw/Medical_Staff_Reporting.accdb` via Access M templates | Measures, relationships, and report pages validate against the local sample without implying SQL readiness |
| SQL contract column presence | SQL objects listed in `docs/sql-server-publish-plan.md` and represented by `*_SqlServer.m` templates | Later SQL binding loads every required column without `Table.SelectColumns` errors |
| Staff count tie-out | `qry_Medical_Staff_Data` | Distinct staff count matches the source query export for the same period |
| Payroll amount tie-out | `qry_Combo_Medical_Payroll_Data` | Payroll totals match by period and pay component |
| History coverage check | `tbl_Medical_Staff_History` | Every current staff record maps to a valid history path or an explicit exception |
| Calendar continuity check | `tbl_WF_Calendar` | No unexpected date gaps inside the supported reporting range |
| Dependency presence check | payroll/FTE pass-through objects, `tbl_Calendar`, `tbl_Email_Addresses`, `tbl_VMO_Data` | Each linked object is either loaded, explicitly excluded, or documented as unavailable |
| Key uniqueness check | staff key, history key, payroll key | No duplicate keys at the grain defined for each fact table |
| Null key check | all join keys | No unexpected nulls in relationship columns |

## Acceptance Pack Before SQL Host Is Known

This pack is the acceptance boundary for work that can be completed before the SQL Server host, database, gateway, and credential mode are known. It accepts the local Access-sample build, the source-control report package, and the documented model contract. It does not accept published SQL refresh.

### Sample-result checks to perform

Record each result from the Access sample extract or from an exported CSV snapshot made from `data/raw/Medical_Staff_Reporting.accdb`. Use the same extraction timestamp for all rows in the table.

| Check ID | Acceptance check | Sample source | Model object or page | Pass condition | Actual result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MS-SAMPLE-01 | Current staff row count | `tbl_Medical_Staff_Data` | `FactMedicalStaffCurrent` | Imported row count equals the Access table/export row count. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-02 | Current distinct staff count | `tbl_Medical_Staff_Data` and `qry_Medical_Staff_Data` | `[Medical Staff Count]` | Distinct `Staff ID` matches for the same period/filter context. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-03 | Active staff count | `tbl_Medical_Staff_Data` | `[Active Staff Count]` | Count of distinct staff where `Staff Status = Active` matches the source export. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-04 | FTE total | `tbl_Medical_Staff_Data` | `[Medical Staff FTE]` | Sum of `FTE` matches the source export after identical period/status filters. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-05 | Payroll total | `qry_Combo_Medical_Payroll_Data` | `[Medical Payroll Amount]` | Sum of `Payroll Amount` matches by financial year, period, and pay component. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-06 | History row count | `tbl_Medical_Staff_History` | `[History Row Count]` | Imported row count equals the Access table/export row count. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-07 | Missing effective dates | `tbl_Medical_Staff_History` | `[Missing Effective Date Count]` | Count of blank `Effective Date` rows matches source export and exceptions are explainable. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-08 | Duplicate history grain | `tbl_Medical_Staff_History` | `[Duplicate Staff Record Count]` | Duplicate `Staff ID` plus `Effective Date` count matches the source export. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-09 | Workforce calendar continuity | `tbl_WF_Calendar` | `DimWorkforceCalendar` | Date/period range has no unexpected gaps or duplicate dates inside the supported range. | To be recorded from sample extract. | Open until sample result is recorded |
| MS-SAMPLE-10 | Report page structure | Generated PBIR under `report/pbir/` | Overview, Staff History, Source Validation pages | Pages and visual IDs match `report/report-implementation-spec.md`. | To be recorded from focused validation. | Open until validation is recorded |

### DAX measures to verify

These measures must be present, evaluate without error, and tie out to the sample-result checks above before the local Access-sample pack is accepted.

| Measure | Verification source | Acceptance rule |
| --- | --- | --- |
| `Medical Staff Count` | `tbl_Medical_Staff_Data`, `qry_Medical_Staff_Data` | Matches distinct staff count at all accepted period/status filters. |
| `Active Staff Count` | `tbl_Medical_Staff_Data` | Matches distinct active staff count. |
| `Inactive Staff Count` | `tbl_Medical_Staff_Data` | Equals total staff count minus active staff count unless the source has non-standard status values that are documented. |
| `Medical Staff FTE` | `tbl_Medical_Staff_Data` | Matches source FTE total after identical filters and numeric rounding. |
| `Medical Payroll Amount` | `qry_Combo_Medical_Payroll_Data` | Matches payroll amount by financial year, period, and pay component. |
| `Payroll per Staff` | Derived from accepted payroll and staff-count checks | Equals payroll amount divided by medical staff count, with blank/zero handling through `DIVIDE`. |
| `FTE per Staff` | Derived from accepted FTE and staff-count checks | Equals FTE divided by medical staff count, with blank/zero handling through `DIVIDE`. |
| `Medical Staff Row Count` | `tbl_Medical_Staff_Data` | Matches current staff row count. |
| `Medical Staff Count Prior Period` and deltas | `DimWorkforceCalendar`, current staff sample | Prior-period value and delta follow the accepted calendar ordering. |
| `Medical Staff FTE Prior Period` and deltas | `DimWorkforceCalendar`, current staff sample | Prior-period value and delta follow the accepted calendar ordering. |
| `Medical Payroll Amount Prior Period` and deltas | `DimWorkforceCalendar`, payroll sample | Prior-period value and delta follow the accepted calendar ordering. |
| `History Row Count` | `tbl_Medical_Staff_History` | Matches history row count. |
| `Current Record Count` | `tbl_Medical_Staff_Data` | Matches rows where `Record State = Current`. |
| `Historical Record Count` | `tbl_Medical_Staff_History` | Matches rows where `Record State = Historical`. |
| `History Coverage %` | Current staff and history sample | Equals history row count divided by current distinct staff count; exceptions are documented. |
| `Duplicate Staff Record Count` | `tbl_Medical_Staff_History` | Matches duplicate staff/effective-date grain check. |
| `Missing Effective Date Count` | `tbl_Medical_Staff_History` | Matches blank effective-date count. |
| `Open History Records` | `tbl_Medical_Staff_History` | Matches blank end-date count. |
| `Source Object Count`, `Missing Source Count`, `Validation Pass Count`, `Validation Fail Count` | Source inventory and validation tables | Match manually reviewed source inventory and validation rows. |

### Headcount, FTE, payroll, and history acceptance table

Populate this table for each accepted sample period. Use one row for an all-period total and one row per period selected for regression testing.

| Period scope | Headcount source value | Headcount measure value | FTE source value | FTE measure value | Payroll source value | Payroll measure value | History source rows | History measure rows | Required outcome |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| All sample periods | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | All source and measure values match, or each variance has an owner note. |
| Earliest complete period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Period-level headcount, FTE, payroll, and history values match. |
| Latest complete period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Period-level headcount, FTE, payroll, and history values match. |
| Highest payroll period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Payroll peak is reproducible and not caused by duplicate payroll rows. |

### SQL-host-dependent checks left open

These checks cannot be closed until the SQL Server host, database, schema, gateway, and credential mode are known.

| Check ID | Open check | Why it remains open |
| --- | --- | --- |
| MS-SQL-01 | Confirm `SqlServerName`, `SqlDatabaseName`, and final schema. | Source-controlled templates intentionally keep host and database as placeholders. |
| MS-SQL-02 | Confirm SQL object existence for all Medical Staff contract tables/views. | No SQL host is available to query `INFORMATION_SCHEMA` or object metadata. |
| MS-SQL-03 | Confirm SQL column presence, data types, nullability, and precision. | The `_SqlServer.m` templates define expected columns, but the live source must prove them. |
| MS-SQL-04 | Confirm canonical staff, history, and payroll keys. | Access sample checks cannot prove production SQL key semantics. |
| MS-SQL-05 | Confirm payroll amount definition and rounding. | Gross/total/other payroll definition is still a source-contract decision. |
| MS-SQL-06 | Confirm workforce calendar alignment. | SQL must prove whether `tbl_WF_Calendar` aligns with finance periods or a separate workforce hierarchy. |
| MS-SQL-07 | Confirm gateway binding and credential mode. | Gateway and credentials are explicitly out of source control. |
| MS-SQL-08 | Confirm published refresh and scheduled refresh readiness. | Refresh cannot be validated until SQL connectivity and gateway binding exist. |

## M Query Templates

Use one query template per source shape so the final load shape stays explicit.

### Access profiling templates

- `src/powerbi/dashboards/medical-staff/m/MedicalStaffAccessSource.m`
- `src/powerbi/dashboards/medical-staff/m/tbl_Medical_Staff_Data.m`
- `src/powerbi/dashboards/medical-staff/m/tbl_Medical_Staff_History.m`
- `src/powerbi/dashboards/medical-staff/m/tbl_WF_Calendar.m`

### SQL Server refresh templates

- `src/powerbi/dashboards/medical-staff/m/MedicalStaffSqlServerSource.m`
- `src/powerbi/dashboards/medical-staff/m/tbl_Medical_Staff_Data_SqlServer.m`
- `src/powerbi/dashboards/medical-staff/m/tbl_Medical_Staff_History_SqlServer.m`
- `src/powerbi/dashboards/medical-staff/m/tbl_WF_Calendar_SqlServer.m`
- `src/powerbi/dashboards/medical-staff/m/qry_Combo_Medical_Payroll_Data_SqlServer.m`
- `src/powerbi/dashboards/medical-staff/m/qry_Employee_Sub_SqlServer.m`
- `src/powerbi/dashboards/medical-staff/m/qry_Medical_Staff_Data_SqlServer.m`

The SQL templates intentionally use `Table.SelectColumns` on the required source contract columns before typing. Missing contract columns should fail during the live build rather than producing silent blank report fields.

The `_SqlServer.m` templates are not substitutes for the current Access sample build. They carry the expected SQL contract and parameter placeholders for the later host binding.

## Live pbi-cli Implementation Checklist

Run this only after SQL Server access and a target PBIP/model are available. Do not use this checklist to imply SQL readiness from the interim Access sample build.

1. Connect to the target model with `pbi connect`.
2. Add or replace the Power Query definitions from `src/powerbi/dashboards/medical-staff/m/*_SqlServer.m`.
3. Bind `SqlServerName`, `SqlDatabaseName`, and `SqlSchemaName` through model parameters or environment-specific deployment configuration.
4. Rename loaded tables to the model names in `model-tmdl/relationship-checklist.md`.
5. Mark `DimWorkforceCalendar[Date]` as the date table.
6. Create only the active relationships listed as required in the relationship checklist; keep employee-sub relationships conditional until uniqueness is proven.
7. Create measures from `model-tmdl/measure-catalogue.md`, using display folders for Core Staff, Trends, History, and Validation.
8. Add report pages and visuals from `report/page-completion-checklist.md` using `pbi report --no-sync`.
9. Run the validation checks in `report/validation-checklist.md` and record mismatches before export.
10. Export the real TMDL/report artifacts only after the live model and report validate.

## TMDL And Report Export Instructions

- Do not create fake TMDL files that imply SQL Server refresh binding has already happened.
- Keep generated exports under the existing generated folders, including `src/powerbi/dashboards/medical-staff/model-tmdl/live-export/` and `src/powerbi/dashboards/medical-staff/report/pbir/`.
- Treat current generated exports as Access-sample validation artifacts until SQL Server binding is completed and revalidated.
- Treat PBIR completion as a report-package verification step, not a missing-export step.
- Treat the Access and SQL Server templates as source-controlled inputs, not as evidence of a completed Desktop export.

## Delivery Notes

- Keep dashboard-specific shaping in `src/powerbi/dashboards/medical-staff/`.
- Promote only stable shared definitions later, after the model grain and source dependencies are proven.
- Treat the Access or SQL Server extract schema as the source of truth for final column names and data types.
