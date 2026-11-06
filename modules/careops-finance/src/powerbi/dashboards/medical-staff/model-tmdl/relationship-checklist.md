# Medical Staff Relationship Checklist

Use this as the live semantic-model build checklist after the SQL-backed queries are loaded. Table names below are the intended model names, not necessarily the raw query file names.

## Required Tables

| Model table | Query template | Load role |
| --- | --- | --- |
| `FactMedicalStaffCurrent` | `tbl_Medical_Staff_Data_SqlServer.m` | Current-state staff fact. |
| `FactMedicalStaffHistory` | `tbl_Medical_Staff_History_SqlServer.m` | Effective-dated staff history fact. |
| `FactMedicalPayroll` | `qry_Combo_Medical_Payroll_Data_SqlServer.m` | Payroll and FTE fact by period/component. |
| `DimEmployeeSub` | `qry_Employee_Sub_SqlServer.m` | Optional helper dimension or bridge if the fact tables are not flattened. |
| `DimWorkforceCalendar` | `tbl_WF_Calendar_SqlServer.m` | Date and reporting-period dimension. |
| `ValidationMedicalStaffData` | `qry_Medical_Staff_Data_SqlServer.m` | Tie-out view; hide from report consumers. |

## Relationship Build

| From | To | Cardinality | Direction | Active | Notes |
| --- | --- | --- | --- | --- | --- |
| `FactMedicalStaffCurrent[Date]` | `DimWorkforceCalendar[Date]` | Many-to-one | Single | Yes | Current snapshot or pay-period date. |
| `FactMedicalStaffHistory[EffectiveDate]` | `DimWorkforceCalendar[Date]` | Many-to-one | Single | Yes | Primary history timeline. |
| `FactMedicalPayroll[Date]` | `DimWorkforceCalendar[Date]` | Many-to-one | Single | Yes | Payroll trend and period filter path. |
| `FactMedicalStaffCurrent[StaffID]` | `DimEmployeeSub[EmployeeID]` | Many-to-one | Single | Conditional | Create only if `DimEmployeeSub[EmployeeID]` is unique. |
| `FactMedicalStaffHistory[StaffID]` | `DimEmployeeSub[EmployeeID]` | Many-to-one | Single | Conditional | Keep inactive if it creates ambiguity with current-state filters. |
| `FactMedicalPayroll[StaffID]` | `DimEmployeeSub[EmployeeID]` | Many-to-one | Single | Conditional | Create only after payroll key parity is confirmed. |

## Date Handling

- Mark `DimWorkforceCalendar[Date]` as the model date table.
- Sort period labels by `DimWorkforceCalendar[Date]` or a stable period index, not alphabetically.
- Keep finance `tbl_Calendar` out of the default model unless the live source confirms the crosswalk requirement.
- Confirm whether `EffectiveDate` or `EndDate` should drive the default history page; use inactive relationships or USERELATIONSHIP measures only if both paths are needed.

## Relationship Validation

- `DimWorkforceCalendar[Date]` contains one row per date in the supported reporting range.
- `DimEmployeeSub[EmployeeID]` is unique before activating employee relationships.
- `FactMedicalStaffCurrent[StaffID]`, `FactMedicalStaffHistory[StaffID]`, and `FactMedicalPayroll[StaffID]` have no unexpected nulls.
- No bidirectional relationship is enabled unless a specific visual cannot be solved with a measure.
- Validation-only tables are hidden and have no active filter paths to report facts.
