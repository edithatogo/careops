# Dashboard Architecture

## Recommendation

Build the VMO Finance and Medical Staff dashboards as separate Power BI projects now, then combine later only after the business definitions and source dependencies are stable.

The merge-readiness framework currently supports the same position: keep the dashboards separate until both are complete and validated, then re-run the comparison against the finished models.

This keeps the first delivery simpler:

- Smaller refresh surface for each dashboard.
- Cleaner ownership of VMO versus Medical Staff logic.
- Easier validation against the original Access reports.
- Less risk from broken linked tables or pass-through sources blocking unrelated work.
- A later merge path through shared dimensions, shared measures, or a composite model.
- A cleaner path to private GitHub readiness because each dashboard can be hardened independently.

## Project Shape

```text
src/powerbi/
|-- shared/
|   |-- m/
|   `-- model-tmdl/
`-- dashboards/
    |-- vmo-finance/
    |   |-- Dataset/
    |   |-- m/
    |   |-- model-tmdl/
    |   `-- report/
    `-- medical-staff/
        |-- Dataset/
        |-- m/
        |-- model-tmdl/
        `-- report/
```

## Separation Rules

- Dashboard-specific measures, pages, and data-shaping logic stay inside the dashboard folder.
- Shared date, organisation/cost-centre, and common finance definitions move to `src/powerbi/shared/`.
- Do not use one dashboard's private query as a dependency for the other dashboard.
- If a table is needed by both dashboards, promote the query contract to `shared/` first.
- Keep raw Access files and exported data under ignored `data/` folders only.
- Keep the source split explicit in the docs and registry until both dashboards are individually ready for ALM packaging.
- Use Access only for local profiling/sample extracts; published refresh must connect to SQL Server tables or views.

## Later Merge Options

1. Keep two reports and publish them to the same workspace with shared navigation.
2. Promote common tables and measures into one shared semantic model and connect two thin reports.
3. Build a combined executive report after both dashboard definitions are validated.
4. Use a composite model only if the separate semantic models need to remain independently refreshed.
5. Merge only after the source contracts, refresh behavior, and shared definitions have been proven stable on private GitHub.

## Merge Readiness

See `docs/shared-model-merge-readiness.md` for the decision framework, comparison matrix, prerequisites, and risk register that govern any future consolidation.

Current operating assumption:

- Separate dashboards stay the default.
- No shared-model merge should be scheduled until both dashboards have been built and checked against their source reports.
- Any merge recommendation must be based on finished models, not on partial design intent.

## Current Source Split

### VMO Finance

- Primary Access source: `VMO Reporting.accdb`
- Local tables: `tbl_Calendar`, `tbl_GL_Transactions`, `tbl_Reconciliation_GL_Data`, `tbl_Reconciliation_VMO_Data`, `tbl_VMO_Data`, `tbl_VMO_GL_Classification`, `tbl_VMO_GL_Transactions`
- External dependencies: linked Excel/email tables and pass-through GL/account/cost-centre queries
- Dashboard purpose: VMO activity, reconciliation, classification, and financial-year reporting.

### Medical Staff

- Primary Access source: `Medical_Staff_Reporting.accdb`
- Local tables: `tbl_Medical_Staff_Data`, `tbl_Medical_Staff_History`, `tbl_WF_Calendar`
- External dependencies: payroll/FTE pass-through objects plus linked VMO/calendar/email tables
- Dashboard purpose: payroll, FTE, staff history, and workforce calendar reporting.
