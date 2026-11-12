# Power BI Report Build Plan

Status: implementation package only. This plan defines pages, visuals, fields,
filters, validation interactions, and a CLI/PBIR build path for the standalone
VMO Finance and Medical Staff dashboards. It does not mutate Power BI Desktop.

## Operating Rules

- Keep VMO Finance and Medical Staff as separate report projects.
- Generate PBIR only after the matching semantic model or dataset reference
  exists.
- Treat field names in the report specs as the report contract. If the exported
  model uses different physical names, update the spec before generating PBIR.
- Keep generated PBIR artifacts under each dashboard's `report/pbir/` folder.
- Use `pbi report validate`, `pbi report list-pages`, `pbi visual list`, and
  `pbi filters list` for validation.
- Do not call `pbi report reload`; Desktop is intentionally out of scope.

## Local CLI Path

`pbi` is available locally at:

```text
${PRIVATE_HOME}\.local\bin\pbi.exe
```

Primary command sequence:

```powershell
pbi report create <target.Report> --name <ReportName> --dataset-path <relative Dataset path>
pbi report --path <target.Report> --no-sync add-page --display-name <Display> --name <page_id> --width 1280 --height 720
pbi visual --path <target.Report> --no-sync add --page <page_id> --type <visual_type> --name <visual_id> --x <x> --y <y> --width <w> --height <h>
pbi visual --path <target.Report> --no-sync bind <visual_id> --page <page_id> <roles>
pbi filters --path <target.Report> --no-sync add-topn --page <page_id> <roles>
pbi report --path <target.Report> validate
```

## VMO Finance Package

Files:

- `src/powerbi/dashboards/vmo-finance/report/report-implementation-spec.md`
- `src/powerbi/dashboards/vmo-finance/report/Build-VmoReportPbir.ps1`
- `src/powerbi/dashboards/vmo-finance/report/page-completion-checklist.md`
- `src/powerbi/dashboards/vmo-finance/report/validation-checklist.md`

Pages:

| Page ID | Display name | Purpose |
| --- | --- | --- |
| `executive_summary` | Executive Summary | Executive totals, reconciliation status, and period trend. |
| `reconciliation_detail` | Reconciliation Detail | GL-to-VMO bridge matrix and variance explanation. |
| `classification_cost_centre` | Classification And Cost Centre | Classification and cost-centre comparison. |
| `exceptions` | Exceptions | Unmatched and exception review. |
| `transaction_detail` | Transaction Detail | Line-level traceability. |
| `validation` | Validation | Access or SQL sample tie-out controls. |

Required interactions:

- Financial year and period filter all summary, reconciliation, exception, and
  validation visuals.
- Reconciliation status filters variance rows, exception counts, and status
  visuals.
- Cost centre, account, and classification filter transactions and variance
  visuals.
- Exception rows support transaction-level review on `transaction_detail`.

## Medical Staff Package

Files:

- `src/powerbi/dashboards/medical-staff/report/report-implementation-spec.md`
- `src/powerbi/dashboards/medical-staff/report/Build-MedicalStaffReportPbir.ps1`
- `src/powerbi/dashboards/medical-staff/report/page-completion-checklist.md`
- `src/powerbi/dashboards/medical-staff/report/validation-checklist.md`

Pages:

| Page ID | Display name | Purpose |
| --- | --- | --- |
| `medical_staff_overview` | Medical Staff Overview | Headcount, active staff, FTE, payroll, and workforce slices. |
| `staff_history` | Staff History | Current versus historical record coverage and row-level review. |
| `source_validation` | Source Dependencies and Validation | Source dependency and validation status. |

Required interactions:

- Period selection filters staff counts, FTE, payroll, history, and validation
  visuals.
- Department and grade selections filter headcount, FTE, payroll, and matrices.
- Staff identifier selection filters history detail and history exception
  visuals.
- Load status and validation result filter dependency and validation rows.

## Validation Gates

- `pbi report --path <target.Report> validate` succeeds.
- `pbi report --path <target.Report> list-pages` returns the documented page
  IDs in order.
- Each page contains the visual IDs in the implementation spec.
- `pbi filters --path <target.Report> list --page <page_id>` matches the page
  filter contract.
- Any missing physical field name is logged in the relevant validation
  checklist before report generation is marked complete.
