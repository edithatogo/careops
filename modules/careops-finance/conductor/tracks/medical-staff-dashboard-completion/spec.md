# Medical Staff Dashboard Completion

## Objective

Complete the standalone Medical Staff Power BI dashboard as a working report backed by the agreed SQL Server source contract.

## Inputs

- `docs/medical-staff-dashboard.md`
- `docs/sql-server-publish-plan.md`
- `src/powerbi/dashboards/medical-staff/`
- SQL Server source contract from `sql-server-source-contracts`

## Requirements

- Replace Access-only source assumptions with parameterised SQL Server source queries for published refresh.
- Build the semantic model with staff, history, workforce calendar, payroll/FTE, and relevant shared dimensions.
- Implement Medical Staff measures for headcount, FTE, payroll totals, period trends, and history/current-state comparisons.
- Build report pages for staff summary, period trends, staff history, and dependency/exceptions review.
- Validate report totals against agreed source checks; Access-derived sample extracts are profiling evidence only until the live SQL Server path is confirmed.
- Export model/report source artifacts to the dashboard folder.

## Acceptance Criteria

- Medical Staff dashboard opens locally and refreshes from the intended development/sample source.
- Published-refresh source is parameterised for SQL Server.
- Measures and relationships are documented or exported in source control.
- Report pages satisfy the page spec in `docs/medical-staff-dashboard.md`.
- TMDL/report source is exported under `src/powerbi/dashboards/medical-staff/`.
- Validation notes list source totals checked and unresolved exceptions.
- Live SQL Server validation records the confirmed host/database, credential mode, and gateway binding before publish readiness.
