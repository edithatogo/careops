# VMO Finance Dashboard

## Objective

Build a Power BI dashboard for VMO reporting and reconciliation using `VMO Reporting.accdb`.

This should be built as a standalone Power BI project under `src/powerbi/dashboards/vmo-finance/`, with only stable reusable definitions promoted to `src/powerbi/shared/`.

## Known Source Objects

- Local tables: `tbl_Calendar`, `tbl_GL_Transactions`, `tbl_Reconciliation_GL_Data`, `tbl_Reconciliation_VMO_Data`, `tbl_VMO_Data`, `tbl_VMO_GL_Classification`, `tbl_VMO_GL_Transactions`
- Views: `qry_Financial_Year_Total`, `qry_Reconciliation_GL_Data`, `qry_Reconciliation_GL_Summary`, `qry_Reconciliation_GL_Summary_Other_Subsystems`
- Linked/pass-through dependencies: `tbl_Email_Addresses`, `tbl_Excel_VMO_Data`, `ca_MVRPT_ACCOUNT`, `ca_MVRPT_COSTCENTRES`, `dbo_FMIS_GL_JOURNAL`

## Requirements

- Show VMO totals by financial year, period, cost centre, and classification.
- Show GL versus VMO reconciliation status and variance.
- Surface unmatched or exception rows that need finance review.
- Preserve traceability back to Access source objects.
- Avoid depending on unavailable linked Excel/network paths without explicit documentation.

## Acceptance Criteria

- Dashboard page spec lists visuals, filters, and measures.
- Required model measures are identified and implemented.
- Linked/pass-through source gaps are documented before refresh automation.
- Report source is exported or documented under `src/powerbi/dashboards/vmo-finance/report/`.
