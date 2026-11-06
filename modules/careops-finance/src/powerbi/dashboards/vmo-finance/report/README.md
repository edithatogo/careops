# VMO report implementation package

This folder contains the implementation package for the standalone VMO Finance
report.

Current status:

- Generated PBIR source now exists under `report/pbir/`; keep it generated-only
  and validate it before treating it as the report source of truth.
- `report-implementation-spec.md` defines pages, visuals, fields, filters, and
  validation interactions.
- [`docs/synthetic-vmo-period-slice.md`](../../../../../docs/synthetic-vmo-period-slice.md)
  describes a separate fictional source-to-measure reconciliation slice. It
  does not add a period field to the production VMO source contract or claim
  Power BI rendering.
- `Build-VmoReportPbir.ps1` provides a CLI/PBIR build path once a compatible
  semantic model or dataset reference exists.
- Keep generated PBIR artifacts under `report/pbir/` and validate them with
  `pbi report validate`.
- The current interim data binding is the local Access sample. SQL Server
  binding remains a later step once `SqlServerName`, `SqlDatabaseName`, and
  `SqlSchemaName` are available.
- Do not call `pbi report reload` from this package; Desktop mutation is out of
  scope.
