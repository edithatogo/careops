# Medical Staff Dashboard

## Objective

Build a Power BI dashboard for Medical Staff reporting using `Medical_Staff_Reporting.accdb`.

This should be built as a standalone Power BI project under `src/powerbi/dashboards/medical-staff/`, with only stable reusable definitions promoted to `src/powerbi/shared/`.

## Known Source Objects

- Local tables: `tbl_Medical_Staff_Data`, `tbl_Medical_Staff_History`, `tbl_WF_Calendar`
- Views: `qry_Combo_Medical_Payroll_Data`, `qry_Employee_Sub`, `qry_Medical_Staff_Data`
- Linked/pass-through dependencies: payroll/FTE pass-through objects, `tbl_Calendar`, `tbl_Email_Addresses`, `tbl_VMO_Data`

## Requirements

- Show medical staff headcount/FTE/payroll reporting by period and relevant workforce dimensions.
- Track current versus historical staff records where supported by source data.
- Surface dependency gaps for linked VMO/calendar/email and payroll pass-through sources.
- Preserve traceability back to Access source objects and refresh assumptions.

## Acceptance Criteria

- Dashboard page spec lists visuals, filters, and measures.
- Payroll/FTE dependency handling is documented.
- Required model measures are identified and implemented.
- Report source is exported or documented under `src/powerbi/dashboards/medical-staff/report/`.
