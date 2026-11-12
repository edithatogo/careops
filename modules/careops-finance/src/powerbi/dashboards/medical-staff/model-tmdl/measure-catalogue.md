# Medical Staff Measure Catalogue

Status: source-control catalogue for later TMDL/pbi-cli implementation. Do not treat this file as an exported TMDL artifact.

Recommended measure table: `Medical Staff Measures`.

## Model Naming Assumptions

The SQL M templates select source columns from the agreed SQL contract and rename them to the field names used below. If the live SQL source differs, update the M template first and keep this catalogue stable where possible.

| Model table | Source contract |
| --- | --- |
| `FactMedicalStaffCurrent` | `dbo.tbl_Medical_Staff_Data` |
| `FactMedicalStaffHistory` | `dbo.tbl_Medical_Staff_History` |
| `FactMedicalPayroll` | `dbo.qry_Combo_Medical_Payroll_Data` |
| `DimEmployeeSub` | `dbo.qry_Employee_Sub` |
| `DimWorkforceCalendar` | `dbo.tbl_WF_Calendar` |
| `ValidationMedicalStaffData` | `dbo.qry_Medical_Staff_Data` |

## Core Staff Measures

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `Medical Staff Count` | `DISTINCTCOUNT ( FactMedicalStaffCurrent[StaffID] )` | `#,##0` | `Core` | Distinct current staff count. |
| `Active Staff Count` | `CALCULATE ( [Medical Staff Count], FactMedicalStaffCurrent[StaffStatus] = "Active" )` | `#,##0` | `Core` | Active current staff. |
| `Inactive Staff Count` | `CALCULATE ( [Medical Staff Count], FactMedicalStaffCurrent[StaffStatus] <> "Active" )` | `#,##0` | `Core` | Non-active current staff. |
| `Medical Staff FTE` | `SUM ( FactMedicalStaffCurrent[FTE] )` | `#,##0.00` | `Core` | Current FTE total. |
| `Medical Payroll Amount` | `SUM ( FactMedicalPayroll[PayrollAmount] )` | `$#,##0;($#,##0);-` | `Core` | Payroll total when payroll fact exists. |
| `Payroll per Staff` | `DIVIDE ( [Medical Payroll Amount], [Medical Staff Count] )` | `$#,##0` | `Core` | Payroll per current staff member. |
| `FTE per Staff` | `DIVIDE ( [Medical Staff FTE], [Medical Staff Count] )` | `#,##0.00` | `Core` | FTE density per staff member. |
| `Medical Staff Row Count` | `COUNTROWS ( FactMedicalStaffCurrent )` | `#,##0` | `Core` | Current source row volume. |

## Trend Measures

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `Medical Staff Count Prior Period` | `CALCULATE ( [Medical Staff Count], DATEADD ( DimWorkforceCalendar[Date], -1, MONTH ) )` | `#,##0` | `Trends` | Previous-month staff count. |
| `Medical Staff Count Delta` | `[Medical Staff Count] - [Medical Staff Count Prior Period]` | `#,##0` | `Trends` | Staff count movement. |
| `Medical Staff Count Delta %` | `DIVIDE ( [Medical Staff Count Delta], [Medical Staff Count Prior Period] )` | `0.0%` | `Trends` | Staff count movement percentage. |
| `Medical Staff FTE Prior Period` | `CALCULATE ( [Medical Staff FTE], DATEADD ( DimWorkforceCalendar[Date], -1, MONTH ) )` | `#,##0.00` | `Trends` | Previous-month FTE. |
| `Medical Staff FTE Delta` | `[Medical Staff FTE] - [Medical Staff FTE Prior Period]` | `#,##0.00` | `Trends` | FTE movement. |
| `Medical Staff FTE Delta %` | `DIVIDE ( [Medical Staff FTE Delta], [Medical Staff FTE Prior Period] )` | `0.0%` | `Trends` | FTE movement percentage. |
| `Medical Payroll Amount Prior Period` | `CALCULATE ( [Medical Payroll Amount], DATEADD ( DimWorkforceCalendar[Date], -1, MONTH ) )` | `$#,##0;($#,##0);-` | `Trends` | Previous-month payroll amount. |
| `Medical Payroll Amount Delta` | `[Medical Payroll Amount] - [Medical Payroll Amount Prior Period]` | `$#,##0;($#,##0);-` | `Trends` | Payroll movement. |
| `Medical Payroll Amount Delta %` | `DIVIDE ( [Medical Payroll Amount Delta], [Medical Payroll Amount Prior Period] )` | `0.0%` | `Trends` | Payroll movement percentage. |

## History Measures

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `History Row Count` | `COUNTROWS ( FactMedicalStaffHistory )` | `#,##0` | `History` | History source row volume. |
| `Current Record Count` | `CALCULATE ( COUNTROWS ( FactMedicalStaffCurrent ), FactMedicalStaffCurrent[RecordState] = "Current" )` | `#,##0` | `History` | Current records in current fact. |
| `Historical Record Count` | `CALCULATE ( [History Row Count], FactMedicalStaffHistory[RecordState] = "Historical" )` | `#,##0` | `History` | Historical records in history fact. |
| `History Coverage %` | `DIVIDE ( [History Row Count], [Medical Staff Count] )` | `0.0%` | `History` | History rows per current staff member. |
| `Duplicate Staff Record Count` | `COUNTROWS ( FILTER ( SUMMARIZE ( FactMedicalStaffHistory, FactMedicalStaffHistory[StaffID], FactMedicalStaffHistory[EffectiveDate], "RowCount", COUNTROWS ( FactMedicalStaffHistory ) ), [RowCount] > 1 ) )` | `#,##0` | `Data Quality` | Duplicate staff/effective-date records. |
| `Missing Effective Date Count` | `COUNTROWS ( FILTER ( FactMedicalStaffHistory, ISBLANK ( FactMedicalStaffHistory[EffectiveDate] ) ) )` | `#,##0` | `Data Quality` | History rows missing effective dates. |
| `Open History Records` | `COUNTROWS ( FILTER ( FactMedicalStaffHistory, ISBLANK ( FactMedicalStaffHistory[EndDate] ) ) )` | `#,##0` | `History` | History records without end dates. |

## Dependency And Validation Measures

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `Source Object Count` | `COUNTROWS ( 'Source Inventory' )` | `#,##0` | `Validation` | Source dependency inventory size. |
| `Missing Source Count` | `CALCULATE ( COUNTROWS ( 'Source Inventory' ), 'Source Inventory'[LoadStatus] = "Missing" )` | `#,##0` | `Validation` | Missing source dependencies. |
| `Validation Pass Count` | `CALCULATE ( COUNTROWS ( 'Validation Checks' ), 'Validation Checks'[Result] = "Pass" )` | `#,##0` | `Validation` | Passing validation checks. |
| `Validation Fail Count` | `CALCULATE ( COUNTROWS ( 'Validation Checks' ), 'Validation Checks'[Result] = "Fail" )` | `#,##0` | `Validation` | Failing validation checks. |

## Implementation Notes

- Apply these to `Medical Staff Measures` unless the final model uses table-local measures.
- Create or load `FactMedicalPayroll` before implementing payroll measures.
- Use `DATEADD` measures only after `DimWorkforceCalendar` is marked as a date table or a separate daily `Date` table is created.
- If the source only exposes period-level workforce calendar rows, keep period comparisons separate from daily DAX time intelligence.

## Acceptance Verification

Do not accept a measure only because the DAX expression exists. For the no-SQL-host acceptance pack, each measure must be evaluated against the Access sample model and tied to the source result listed below.

| Acceptance check | Measures | Source evidence | Pass condition |
| --- | --- | --- | --- |
| Headcount | `Medical Staff Count`, `Active Staff Count`, `Inactive Staff Count`, `Medical Staff Row Count` | `tbl_Medical_Staff_Data` and `qry_Medical_Staff_Data` sample exports. | Counts match source exports under the same period, status, and record-state filters. |
| FTE | `Medical Staff FTE`, `FTE per Staff` | `tbl_Medical_Staff_Data` sample export. | FTE total and derived FTE per staff match after applying the accepted rounding rule. |
| Payroll | `Medical Payroll Amount`, `Payroll per Staff` | `qry_Combo_Medical_Payroll_Data` sample export. | Payroll totals match by financial year, period, and pay component. |
| Staff trends | `Medical Staff Count Prior Period`, `Medical Staff Count Delta`, `Medical Staff Count Delta %` | Current staff sample plus `tbl_WF_Calendar`. | Prior-period and delta values follow the accepted workforce-calendar ordering. |
| FTE trends | `Medical Staff FTE Prior Period`, `Medical Staff FTE Delta`, `Medical Staff FTE Delta %` | Current staff sample plus `tbl_WF_Calendar`. | Prior-period and delta values follow the accepted workforce-calendar ordering. |
| Payroll trends | `Medical Payroll Amount Prior Period`, `Medical Payroll Amount Delta`, `Medical Payroll Amount Delta %` | Payroll sample plus `tbl_WF_Calendar`. | Prior-period and delta values follow the accepted workforce-calendar ordering. |
| History | `History Row Count`, `Current Record Count`, `Historical Record Count`, `History Coverage %`, `Open History Records` | `tbl_Medical_Staff_History` and current staff sample exports. | History counts, state counts, open rows, and coverage ratio match the exported sample. |
| Data quality | `Duplicate Staff Record Count`, `Missing Effective Date Count` | `tbl_Medical_Staff_History` sample export. | Duplicate staff/effective-date rows and blank effective-date rows match source checks. |
| Source validation | `Source Object Count`, `Missing Source Count`, `Validation Pass Count`, `Validation Fail Count` | Source inventory and validation-check rows in the report package. | Counts match the reviewed inventory/check table rows. |

SQL-host-dependent verification remains open until the SQL source can prove object existence, required columns, data types, key uniqueness, payroll semantics, and refresh behavior.

## pbi-cli Creation Notes

Create simple measures with `pbi measure create`. For multi-line measures, pass DAX through stdin so line breaks survive shell parsing.

```powershell
pbi measure create "Medical Staff Count" -t "Medical Staff Measures" -e "DISTINCTCOUNT ( FactMedicalStaffCurrent[StaffID] )" --format-string "#,##0"
pbi measure create "Medical Staff FTE" -t "Medical Staff Measures" -e "SUM ( FactMedicalStaffCurrent[FTE] )" --format-string "#,##0.00"
pbi measure create "Medical Payroll Amount" -t "Medical Staff Measures" -e "SUM ( FactMedicalPayroll[PayrollAmount] )" --format-string '$#,##0'
```
