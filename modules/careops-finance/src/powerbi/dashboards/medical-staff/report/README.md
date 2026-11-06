# Medical Staff Report Implementation Package

This folder contains the implementation package for the standalone Medical Staff
report. Current generated PBIR artifacts are interim Access-sample validation
outputs, not evidence that SQL Server refresh binding has been completed.

## Current Contents

- `report-implementation-spec.md` - concrete page, visual, field, filter, and
  validation-interaction contract.
- `Build-MedicalStaffReportPbir.ps1` - CLI/PBIR build path once a compatible
  semantic model or dataset reference exists.
- `page-completion-checklist.md` - page build checklist.
- `validation-checklist.md` - model and source validation checklist.
- `export-instructions.md` - Access-sample export and later SQL-bound export guidance.

## Export Rule

- Do not add fabricated Desktop export files here.
- Keep generated PBIR artifacts under `report/pbir/`.
- Validate PBIR with `pbi report validate`.
- Do not call `pbi report reload` from this package; Desktop mutation is out of
  scope.
