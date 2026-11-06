# Medical Staff Validation Checklist

Use exported Access extracts for the interim no-SQL-host build. Use SQL Server sample snapshots later, after the host, database, schema, gateway, and credentials are available, to confirm the published refresh path before refresh automation is enabled.

## Acceptance Mode

Until the SQL database/schema and gateway binding are known, validation is limited to `AccessSampleAccepted`. This mode accepts the local sample result checks, documented DAX tie-outs, report page inventory, and source-control package integrity. It explicitly does not accept `SqlRefreshAccepted` or publish readiness. SQL host/listener is supplied as `<sql-server-host>`.

| Mode | Can be completed now | Required evidence | Cannot close in this mode |
| --- | --- | --- | --- |
| `AccessSampleAccepted` | Yes | Access sample row counts, DAX tie-outs, PBIR/TMDL source-control structure checks, documented exceptions. | SQL host, SQL object metadata, gateway, credentials, published refresh. |
| `SqlRefreshAccepted` | No | SQL snapshots, SQL metadata checks, gateway binding, refresh success. | Blocked until SQL database/schema and gateway are known for `<sql-server-host>`. |

| Check | Source | Expected result |
| --- | --- | --- |
| Local table row count parity | `tbl_Medical_Staff_Data`, `tbl_Medical_Staff_History`, `tbl_WF_Calendar` | Power BI import row counts match the source extract row counts |
| Access sample model parity | `data/raw/Medical_Staff_Reporting.accdb` through the Access M templates | Measures, relationships, and generated report structure validate against the local sample without implying SQL readiness |
| SQL contract column presence | SQL objects listed in `docs/sql-server-publish-plan.md` and represented by `m/*_SqlServer.m` | Later SQL binding loads every required column without `Table.SelectColumns` errors |
| Staff count tie-out | `qry_Medical_Staff_Data` | Distinct staff count matches the source query export for the same period |
| Payroll amount tie-out | `qry_Combo_Medical_Payroll_Data` | Payroll totals match by period and pay component |
| History coverage check | `tbl_Medical_Staff_History` | Every current staff record maps to a valid history path or an explicit exception |
| Calendar continuity check | `tbl_WF_Calendar` | No unexpected date gaps inside the supported reporting range |
| Dependency presence check | payroll/FTE pass-through objects, `tbl_Calendar`, `tbl_Email_Addresses`, `tbl_VMO_Data` | Each linked object is either loaded, explicitly excluded, or documented as unavailable |
| Key uniqueness check | staff key, history key, payroll key | No duplicate keys at the grain defined for each fact table |
| Null key check | all join keys | No unexpected nulls in relationship columns |
| Relationship filter check | model relationships | Workforce calendar filters current, history, and payroll facts without many-to-many or bidirectional paths |
| Hidden validation table check | validation-only views | Validation tables are hidden and not exposed as report dimensions |
| PBIR structure validation | `pbi report --path src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff.Report validate` | Generated PBIR parses and passes report validation |
| Page inventory validation | `pbi report --path src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff.Report list-pages` | Confirms pages from `report-implementation-spec.md` |
| Visual inventory validation | `pbi visual --path src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff.Report list --page <page_id>` | Confirms visual IDs from `report-implementation-spec.md` |
| Filter and interaction validation | `pbi filters --path src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff.Report list --page <page_id>` plus manual cross-filter check | Confirms slicers and selections affect expected visuals |

## Access Sample Acceptance Results

Populate this table from a single Access sample extraction run. Leave `Status` as `Open` until the source value, model value, and owner note are filled.

| Check ID | Check | Source object | Source value | Model/report value | Difference | Status | Owner note |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| MS-SAMPLE-01 | Current staff row count | `tbl_Medical_Staff_Data` | To be recorded | To be recorded | To be recorded | Open | Sample extract required. |
| MS-SAMPLE-02 | Distinct current staff | `tbl_Medical_Staff_Data`, `qry_Medical_Staff_Data` | To be recorded | To be recorded | To be recorded | Open | Tie out to `[Medical Staff Count]`. |
| MS-SAMPLE-03 | Active staff | `tbl_Medical_Staff_Data` | To be recorded | To be recorded | To be recorded | Open | Tie out to `[Active Staff Count]`. |
| MS-SAMPLE-04 | Current FTE total | `tbl_Medical_Staff_Data` | To be recorded | To be recorded | To be recorded | Open | Tie out to `[Medical Staff FTE]`. |
| MS-SAMPLE-05 | Payroll amount total | `qry_Combo_Medical_Payroll_Data` | To be recorded | To be recorded | To be recorded | Open | Tie out by financial year, period, and pay component. |
| MS-SAMPLE-06 | History row count | `tbl_Medical_Staff_History` | To be recorded | To be recorded | To be recorded | Open | Tie out to `[History Row Count]`. |
| MS-SAMPLE-07 | Missing effective dates | `tbl_Medical_Staff_History` | To be recorded | To be recorded | To be recorded | Open | Tie out to `[Missing Effective Date Count]`. |
| MS-SAMPLE-08 | Duplicate staff/effective-date records | `tbl_Medical_Staff_History` | To be recorded | To be recorded | To be recorded | Open | Tie out to `[Duplicate Staff Record Count]`. |
| MS-SAMPLE-09 | Calendar duplicates and gaps | `tbl_WF_Calendar` | To be recorded | To be recorded | To be recorded | Open | Confirm supported reporting range before accepting. |
| MS-SAMPLE-10 | Report page and visual inventory | `report/pbir/MedicalStaff` | To be recorded | To be recorded | To be recorded | Open | Match `report-implementation-spec.md`. |

## Headcount/FTE/Payroll/History Period Acceptance

Use this table for acceptance evidence. Add rows as needed for additional periods selected by Finance or Medical Workforce reviewers.

| Period scope | Headcount source | Headcount DAX | FTE source | FTE DAX | Payroll source | Payroll DAX | History source rows | History DAX rows | Acceptance status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| All sample periods | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |
| Earliest complete period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |
| Latest complete period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |
| Highest payroll period in sample | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | To be recorded | Open |

## DAX Verification Checklist

| Measure group | Measures | Required verification |
| --- | --- | --- |
| Core headcount | `Medical Staff Count`, `Active Staff Count`, `Inactive Staff Count`, `Medical Staff Row Count` | Tie out to current-staff sample counts and status-filtered counts. |
| Core FTE | `Medical Staff FTE`, `FTE per Staff` | Tie out to current-staff FTE totals and derived per-staff value. |
| Payroll | `Medical Payroll Amount`, `Payroll per Staff` | Tie out to payroll sample totals by financial year, period, and pay component. |
| Trends | prior-period, delta, and delta percent measures for staff, FTE, and payroll | Verify against the accepted workforce-calendar sort and selected period sequence. |
| History | `History Row Count`, `Current Record Count`, `Historical Record Count`, `History Coverage %`, `Open History Records` | Tie out to history source counts, current/historical state counts, and blank end-date count. |
| Data quality | `Duplicate Staff Record Count`, `Missing Effective Date Count` | Tie out to duplicate and blank effective-date source checks. |
| Validation | `Source Object Count`, `Missing Source Count`, `Validation Pass Count`, `Validation Fail Count` | Tie out to the manually reviewed source inventory and validation-check tables. |

## SQL Snapshot Inputs

When SQL Server access is available, capture these row-count and tie-out values before report layout work:

Bind `SqlServerName`, `SqlDatabaseName`, and `SqlSchemaName` through model parameters or environment-specific deployment configuration. Leave the source-controlled placeholder values in the M templates until the live SQL target is known.

| Object | Required check |
| --- | --- |
| `dbo.tbl_Medical_Staff_Data` | Row count, distinct `Staff ID`, active staff count, FTE sum, payroll amount sum. |
| `dbo.tbl_Medical_Staff_History` | Row count, distinct `History Row ID`, distinct `Staff ID`, null effective-date count. |
| `dbo.qry_Combo_Medical_Payroll_Data` | Row count, distinct `Payroll Row ID`, payroll amount by financial year and period. |
| `dbo.tbl_WF_Calendar` | Minimum date, maximum date, duplicate date count, period coverage. |

## SQL-host-dependent Open Checks

| Check ID | Check | Open dependency |
| --- | --- | --- |
| MS-SQL-01 | SQL host, database, and schema are confirmed. | Host/database/schema are not known. |
| MS-SQL-02 | SQL objects exist for the Medical Staff contract. | Requires live SQL metadata. |
| MS-SQL-03 | Required columns load without `Table.SelectColumns` errors. | Requires live SQL refresh. |
| MS-SQL-04 | SQL row counts match captured SQL snapshots. | Requires SQL sample snapshots. |
| MS-SQL-05 | Staff, history, payroll, and workforce-calendar keys are unique at their documented grain. | Requires production-like SQL rows. |
| MS-SQL-06 | Payroll amount definition and rounding are approved. | Requires source-owner confirmation. |
| MS-SQL-07 | Gateway and credential binding are confirmed. | Requires Power BI Service/gateway configuration. |
| MS-SQL-08 | Published refresh succeeds and scheduled refresh can be enabled. | Requires all previous SQL checks to pass. |
