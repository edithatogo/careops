# Medical Staff Report Implementation Spec

Status: concrete build package. This is not a Power BI Desktop export.

Canvas: 1280 x 720.

## Field Contract

Measures:

- `FactMedicalStaffCurrent[Medical Staff Count]`
- `FactMedicalStaffCurrent[Active Staff Count]`
- `FactMedicalStaffCurrent[Medical Staff FTE]`
- `FactMedicalPayroll[Medical Payroll Amount]`
- `FactMedicalStaffHistory[History Row Count]`
- `FactMedicalStaffHistory[Current Record Count]`
- `FactMedicalStaffHistory[Historical Record Count]`
- `FactMedicalStaffHistory[History Coverage %]`
- `FactMedicalStaffHistory[Duplicate Staff Record Count]`
- `FactMedicalStaffHistory[Missing Effective Date Count]`
- `Source Inventory[Source Object Count]`
- `Source Inventory[Missing Source Count]`
- `Validation Checks[Validation Pass Count]`
- `Validation Checks[Validation Fail Count]`

Columns:

- `DimWorkforceCalendar[Date]`
- `DimWorkforceCalendar[Period]`
- `DimWorkforceCalendar[Financial Year]`
- `FactMedicalStaffCurrent[StaffID]`
- `FactMedicalStaffCurrent[StaffStatus]`
- `FactMedicalStaffCurrent[Department]`
- `FactMedicalStaffCurrent[Grade]`
- `FactMedicalStaffCurrent[RecordState]`
- `FactMedicalStaffHistory[EffectiveDate]`
- `FactMedicalStaffHistory[RecordState]`
- `FactMedicalStaffHistory[EventType]`
- `FactMedicalPayroll[PayComponent]`
- `Source Inventory[ObjectName]`
- `Source Inventory[SourceClass]`
- `Source Inventory[ObjectType]`
- `Source Inventory[LoadStatus]`
- `Validation Checks[CheckName]`
- `Validation Checks[Result]`

## Pages And Visuals

### Medical Staff Overview (`medical_staff_overview`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `card_staff_count` | card | 24,24,216,92 | field `FactMedicalStaffCurrent[Medical Staff Count]` |
| `card_active_staff` | card | 256,24,216,92 | field `FactMedicalStaffCurrent[Active Staff Count]` |
| `card_fte` | card | 488,24,216,92 | field `FactMedicalStaffCurrent[Medical Staff FTE]` |
| `card_payroll` | card | 720,24,240,92 | field `FactMedicalPayroll[Medical Payroll Amount]` |
| `line_headcount_fte` | line | 24,140,624,280 | category `DimWorkforceCalendar[Date]`, value `FactMedicalStaffCurrent[Medical Staff Count]` |
| `column_payroll_period` | column | 672,140,584,280 | category `DimWorkforceCalendar[Period]`, value `FactMedicalPayroll[Medical Payroll Amount]` |
| `matrix_department_grade` | matrix | 24,444,760,232 | rows `FactMedicalStaffCurrent[Department]`, value `FactMedicalStaffCurrent[Medical Staff FTE]` |
| `slicer_period` | slicer | 808,444,216,92 | field `DimWorkforceCalendar[Period]` |
| `slicer_record_state` | slicer | 1040,444,216,92 | field `FactMedicalStaffCurrent[RecordState]` |
| `slicer_staff_status` | slicer | 808,560,216,92 | field `FactMedicalStaffCurrent[StaffStatus]` |

Filters and interactions:

- Period, staff status, and record state filter all current-staff visuals.
- Department and grade selections filter trend and payroll visuals.

### Staff History (`staff_history`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `card_history_rows` | card | 24,24,216,92 | field `FactMedicalStaffHistory[History Row Count]` |
| `card_current_records` | card | 256,24,216,92 | field `FactMedicalStaffHistory[Current Record Count]` |
| `card_historical_records` | card | 488,24,216,92 | field `FactMedicalStaffHistory[Historical Record Count]` |
| `card_history_coverage` | card | 720,24,216,92 | field `FactMedicalStaffHistory[History Coverage %]` |
| `line_history_volume` | line | 24,144,600,260 | category `DimWorkforceCalendar[Date]`, value `FactMedicalStaffHistory[History Row Count]` |
| `bar_history_exceptions` | bar | 656,144,600,260 | category `FactMedicalStaffHistory[EventType]`, value `FactMedicalStaffHistory[Duplicate Staff Record Count]` |
| `table_staff_history_detail` | table | 24,432,1232,244 | values `FactMedicalStaffCurrent[StaffID]`, `FactMedicalStaffHistory[EffectiveDate]`, `FactMedicalStaffHistory[RecordState]`, `FactMedicalStaffHistory[EventType]` |
| `slicer_staff_id` | slicer | 960,24,296,92 | field `FactMedicalStaffCurrent[StaffID]` |

Filters and interactions:

- Staff ID filters cards, history trend, exception bar, and detail table.
- Event type selection filters the detail table and history cards.

### Source Dependencies and Validation (`source_validation`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `card_source_objects` | card | 24,24,216,92 | field `Source Inventory[Source Object Count]` |
| `card_missing_sources` | card | 256,24,216,92 | field `Source Inventory[Missing Source Count]` |
| `card_validation_pass` | card | 488,24,216,92 | field `Validation Checks[Validation Pass Count]` |
| `card_validation_fail` | card | 720,24,216,92 | field `Validation Checks[Validation Fail Count]` |
| `matrix_source_status` | matrix | 24,144,560,360 | row `Source Inventory[SourceClass]`, value `Source Inventory[Source Object Count]` |
| `table_dependency_gaps` | table | 608,144,648,360 | values `Source Inventory[ObjectName]`, `Source Inventory[ObjectType]`, `Source Inventory[LoadStatus]` |
| `table_validation_checks` | table | 24,532,760,144 | values `Validation Checks[CheckName]`, `Validation Checks[Result]` |
| `slicer_load_status` | slicer | 808,532,216,92 | field `Source Inventory[LoadStatus]` |
| `slicer_object_type` | slicer | 1040,532,216,92 | field `Source Inventory[ObjectType]` |

Filters and interactions:

- Load status and object type filter source matrix, dependency gap table, and
  source cards.
- Validation result selection filters pass/fail cards and validation rows.

## PBIR Build

Run `Build-MedicalStaffReportPbir.ps1` only after the Medical Staff dataset
reference is available. The script uses `--no-sync` and does not reload Desktop.
