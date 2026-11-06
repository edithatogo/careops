# VMO Dashboard Completion

## Objective

Complete the standalone VMO Finance Power BI dashboard as a working report backed by the agreed SQL Server source contract.

## Inputs

- `docs/vmo-finance-dashboard.md`
- `docs/sql-server-publish-plan.md`
- `src/powerbi/dashboards/vmo-finance/`
- SQL Server source contract from `sql-server-source-contracts`

## Requirements

- Replace Access-only source assumptions with parameterised SQL Server source queries for published refresh.
- Build the semantic model with relationships, date handling, VMO/GL reconciliation logic, and classification lookups.
- Implement VMO measures for totals, variance, reconciliation status, transaction counts, and exception tracking.
- Build report pages for executive summary, reconciliation, classification/cost-centre analysis, and exception review.
- Validate report totals against agreed source checks; Access-derived sample extracts are profiling evidence only until the live SQL Server path is confirmed.
- Export model/report source artifacts to the dashboard folder.

## Current Handoff Artifacts

Live Desktop sample build/refresh, TMDL export, and PBIR report export now exist. The remaining live-build handoff is SQL Server database/schema and gateway validation against host/listener `<sql-server-host>`. The main thread should use:

- `conductor/tracks/vmo-dashboard-completion/acceptance-pack.md` for the
  concrete no-SQL-host acceptance checks, DAX verification list,
  reconciliation acceptance table, and SQL-dependent open checks.
- `src/powerbi/dashboards/vmo-finance/m/sql/` for SQL-backed Power Query templates.
- `src/powerbi/dashboards/vmo-finance/model-tmdl/relationship-checklist.md` for relationship/date-table creation.
- `src/powerbi/dashboards/vmo-finance/model-tmdl/measure-catalogue.md` for DAX measures and formats.
- `src/powerbi/dashboards/vmo-finance/report/page-completion-checklist.md` for report pages.
- `src/powerbi/dashboards/vmo-finance/report/validation-checklist.md` for Access/SQL tie-out.
- `src/powerbi/dashboards/vmo-finance/pbi-cli-implementation-checklist.md` for the concise pbi-cli execution order.

## Acceptance Criteria

- VMO dashboard opens locally and refreshes from the intended development/sample source.
- Published-refresh source is parameterised for SQL Server.
- Measures and relationships are documented or exported in source control.
- Report pages satisfy the page spec in `docs/vmo-finance-dashboard.md`.
- TMDL/report source is exported under `src/powerbi/dashboards/vmo-finance/`.
- Validation notes list source totals checked and unresolved exceptions.
- The no-SQL-host acceptance pack is complete enough to run against Access
  sample exports without editing generated PBIR/TMDL or M templates.
- Live SQL Server validation records host/listener `<sql-server-host>`, the confirmed database/schema, credential mode, and gateway binding before publish readiness.
