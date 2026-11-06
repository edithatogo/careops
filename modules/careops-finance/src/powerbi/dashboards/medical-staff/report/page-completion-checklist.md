# Medical Staff Report Page Completion Checklist

Use this checklist when the report is being built in PBIR or Power BI Desktop.
The concrete page contract is `report-implementation-spec.md`.

## Page 1: Medical Staff Overview

- [ ] Add page `medical_staff_overview` with display name `Medical Staff Overview`.
- [ ] Add KPI cards bound to `[Medical Staff Count]`, `[Active Staff Count]`, `[Medical Staff FTE]`, and `[Medical Payroll Amount]`.
- [ ] Add trend line by `DimWorkforceCalendar[Date]` with `[Medical Staff Count]` and `[Medical Staff FTE]`.
- [ ] Add payroll column or line chart by period with `[Medical Payroll Amount]`.
- [ ] Add matrix by department and grade using `FactMedicalStaffCurrent[Department]`, `FactMedicalStaffCurrent[Grade]`, `[Medical Staff Count]`, `[Medical Staff FTE]`, and `[Medical Payroll Amount]`.
- [ ] Add slicers for financial year, period, staff status, record state, department, and grade.
- [ ] Visual IDs match `medical_staff_overview` entries in `report-implementation-spec.md`.
- [ ] Period, department, grade, status, and record-state interactions are validated.

## Page 2: Staff History

- [ ] Add page `staff_history` with display name `Staff History`.
- [ ] Add timeline chart by `DimWorkforceCalendar[Date]` with `[History Row Count]`.
- [ ] Add current versus historical matrix by period using `[Current Record Count]`, `[Historical Record Count]`, and `[History Coverage %]`.
- [ ] Add staff-level history table with staff ID, effective date, end date, event type, record state, FTE, payroll amount, department, and grade.
- [ ] Add exception cards for `[Duplicate Staff Record Count]` and `[Missing Effective Date Count]`.
- [ ] Add slicers for staff ID, financial year, period, record state, event type, department, and grade.
- [ ] Staff identifier selection filters history detail and exception visuals.

## Page 3: Source Dependencies and Validation

- [ ] Add page `source_validation` with display name `Source Dependencies and Validation`.
- [ ] Add source status matrix for local tables, SQL objects, linked dependencies, and pass-through objects.
- [ ] Add validation summary cards bound to `[Validation Pass Count]`, `[Validation Fail Count]`, `[Source Object Count]`, and `[Missing Source Count]`.
- [ ] Add dependency gap table with object name, Access source object, SQL source object, expected load role, and load status.
- [ ] Add validation detail table with check name, source object, grain, expected result, actual result, delta, and owner note.
- [ ] Add slicers for source class, object type, load status, validation result, and dashboard page.
- [ ] `pbi report validate` passes for generated PBIR artifacts.

## pbi-cli Page Handoff

Use `--no-sync` during batch page and visual creation. The main thread should reload Desktop only after the report source has been generated and validated.

```powershell
pbi report --no-sync add-page --display-name "Medical Staff Overview" --name medical_staff_overview
pbi report --no-sync add-page --display-name "Staff History" --name staff_history
pbi report --no-sync add-page --display-name "Source Dependencies and Validation" --name source_validation
pbi report validate
```
