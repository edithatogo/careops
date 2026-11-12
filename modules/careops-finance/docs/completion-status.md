# Completion Status

This document summarizes the completion-track sequence for the finance DBs project and the blockers that still prevent the dashboards from being published.

## Current State

- The foundation track is complete.
- Access extracts and exposed Access DSNs remain the only confirmed source-discovery inputs.
- Live Power BI Desktop sample models have now been built and refreshed from the available sample/source surface.
- Live TMDL model exports and PBIR report exports now exist for both dashboard streams; PBIR completion is now a checked-in report-package verification problem for each dashboard, not an export-creation problem.
- The checked-in PBIP report packages now include sibling `Dataset` semantic-model folders with tiny embedded sample partitions, so the `.pbip` files can be opened directly from source control without committing or opening the Access databases.
- Generated PBIR visuals have a reproducible local-proof binding pass that maps planned SQL contract fields to the local Access-backed model fields exposed in the current TMDL exports.
- Future report changes should use the CLI-first surface (`pbi report`, `pbi visual`, PBIR/TMDL source, and `pbi-tools`) before falling back to Power BI Desktop UI inspection.
- Source-control readiness is the current executable validation baseline. `./scripts/Invoke-Validation.ps1 -Mode SourceControlReady` is expected to cover repository hygiene plus PBIR/TMDL export presence and structural checks, with CLI-dependent checks documented when they cannot run locally.
- Acceptance evidence scaffolding is in progress for both dashboards so sample-result checks, PBIR/TMDL structural evidence, and SQL-dependent open checks are captured in that order.
- Published refresh remains blocked because the SQL Server host/listener is now known as `<sql-server-host>`, but the database/schema and gateway path have not been validated.

## Track Order

| Order | Track | State | Blocker |
| --- | --- | --- | --- |
| 1 | `sql-server-source-contracts` | In progress | Contract mappings are documented and host/listener `<sql-server-host>` is supplied; live database/schema and gateway validation remain open. |
| 2 | `vmo-dashboard-completion` | In progress | Embedded local sample Dataset package, PBIR export, and `pbi report validate` now pass; live SQL Server validation remains. |
| 3 | `medical-staff-dashboard-completion` | In progress | Embedded local sample Dataset package, PBIR export, and `pbi report validate` now pass; live SQL Server validation remains. |
| 4 | `dashboard-acceptance-and-publish-readiness` | In progress | Source-control readiness is established; acceptance evidence scaffolding is in progress, while publish readiness waits on SQL Server host/gateway validation. |
| 5 | `shared-model-merge-readiness` | Pending | Only meaningful after both dashboards are validated against live refresh sources. |

## Blockers

- SQL Server source contracts are documented at the expected table/view and column level, with host/listener `<sql-server-host>` supplied but database/schema still not confirmed live.
- Access exposed DSNs only, so the database name, schema/object mapping, credential mode, and gateway binding remain unvalidated. The supplied SQL Server host/listener is `<sql-server-host>`.
- Access data should still be treated as local profiling/sample evidence, not as the final published-refresh source.
- Business-result validation for VMO totals, reconciliation, exceptions, Medical Staff headcount/FTE/payroll, and staff history remains open until the live SQL Server path is available.
- Deployment dry-run and published-refresh readiness remain blocked until the SQL database/schema and gateway binding are confirmed; workspace and authentication details still need to be supplied before any dry-run.

## Notes

- Keep the dashboards separate until both source contracts are stable and validated against the live refresh path.
- Only consider a shared semantic layer after both standalone dashboards are validated and the merge trade-offs are clear.
- Run PBIR/TMDL structural checks against exported artifacts only; do not use validation to reload or mutate Power BI Desktop.
- Treat pbi-cli and pbi-tools output as acceptance evidence when available, and record skipped checks explicitly when local tooling is missing.
