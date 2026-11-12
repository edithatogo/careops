# Access Extraction

The Access databases in `data/raw/` are treated as read-only inputs. Generated inventory and extract files stay under ignored output folders so the repo only carries source and documentation.

## Inventory

Use the inventory script to profile tables, views, links, and pass-through objects:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-AccessInventory.ps1 -DatabasePath ".\data\raw\VMO Reporting.accdb"
```

The inventory output includes object category fields so you can separate:

- `local-table` objects that can be exported for profiling.
- `linked-table` objects that depend on external files, network shares, or credentials.
- `pass-through-query` objects that depend on the upstream SQL source.

## Export

Export one Access database directly with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-AccessTables.ps1 -DatabasePath ".\data\raw\VMO Reporting.accdb" -ObjectName tbl_Calendar,tbl_GL_Transactions -OutDir ".\data\extracts\vmo-finance"
```

For the dashboard-specific convenience flow, use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-DashboardSources.ps1
```

That command exports a limited sample of the known local tables for both standalone dashboards into `data/extracts/`. The default is `-MaxRows 1000` because local extracts are for profiling, not for production refresh:

- `data/extracts/vmo-finance/`
- `data/extracts/medical-staff/`

You can also target one dashboard:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-DashboardSources.ps1 -Dashboard vmo-finance
```

Use a different sample size when needed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-DashboardSources.ps1 -Dashboard vmo-finance -MaxRows 500
```

Use `-MaxRows 0` only for a full export.

## Published Source

The published Power BI dashboards should connect to SQL Server, not to these Access files. Treat Access extracts as local shape samples. Use `docs/sql-server-publish-plan.md` and `src/powerbi/shared/m/SqlServerSourceTemplate.m` for the publish-time source contract.

## Dependency Failures

Linked and pass-through objects are often the first thing to fail on a machine that does not have the original network paths, ODBC sources, or credentials.

Typical failure patterns include:

- `The Microsoft Access database engine cannot open or write to the file ...`
- `ODBC--connection to '...' failed.`
- `The parameter is incorrect.`

Treat those as dependency failures, not as a reason to block local-table profiling. The dashboard export wrapper skips those objects by design and only exports the known local tables needed for Power BI development.

If a linked or pass-through object must be profiled anyway, do it only on a machine that can reach the original source, and document the external dependency before wiring it into refresh logic.
