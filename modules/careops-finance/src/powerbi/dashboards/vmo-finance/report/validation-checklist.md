# VMO validation checklist

Use this checklist in two phases. In the current no-SQL-host interim state,
compare Power BI output with the local Access sample and ignored Access exports.
After SQL Server is available, rerun the same checks against agreed SQL Server
sample extracts before enabling published refresh.

The acceptance source of truth is
`conductor/tracks/vmo-dashboard-completion/acceptance-pack.md`. This file is the
operational checklist for running those checks in Desktop/PBIR.

| Check | Source comparison | Status | Evidence |
| --- | --- | --- | --- |
| GL total by financial year | `qry_Financial_Year_Total` vs `Total GL Amount` | Pending | Not run. |
| Reconciliation summary by status | `qry_Reconciliation_GL_Summary` vs Power BI reconciliation matrix | Pending | Not run. |
| Other subsystem variance | `qry_Reconciliation_GL_Summary_Other_Subsystems` vs validation measure | Pending | Not run. |
| Local Access table row counts | Access export vs Power BI import count | Pending | Interim validation gate before SQL binding. |
| Null key check | Exported data vs Power BI data model | Pending | Not run. |
| Duplicate key check | Exported data vs Power BI data model | Pending | Not run. |
| Unmatched classification rows | `tbl_VMO_GL_Classification` and reconciliation rows | Pending | Not run. |
| Dependency readiness | `tbl_Excel_VMO_Data`, `ca_MVRPT_ACCOUNT`, `ca_MVRPT_COSTCENTRES`, `dbo_FMIS_GL_JOURNAL` | Pending | Not run. |
| SQL contract parameters | `SqlServerName`, `SqlDatabaseName`, and `SqlSchemaName` defaulted to `dbo` | Pending | Later SQL Server binding gate; not required for Access-sample validation. |
| Active relationship paths | `model-tmdl/relationship-checklist.md` vs `pbi relationship list` | Pending | Date relationships first; lookup relationships only after key uniqueness is proven. |
| Hidden validation objects | Validation/tie-out views vs report field list | Pending | Validation-only objects should not appear in consumer pages. |
| PBIR structure validation | `pbi report --path src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance.Report validate` | Pending | Run after PBIR generation. |
| Page inventory validation | `pbi report --path src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance.Report list-pages` | Pending | Confirm pages from `report-implementation-spec.md`. |
| Visual inventory validation | `pbi visual --path src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance.Report list --page <page_id>` | Pending | Confirm visual IDs from `report-implementation-spec.md`. |
| Filter and interaction validation | `pbi filters --path src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance.Report list --page <page_id>` plus manual cross-filter check | Pending | Confirm slicers and selections affect expected visuals. |

## Interim Access-Sample Acceptance Run

Complete this table before asking finance to accept the no-SQL-host interim build.

| Acceptance ID | Run step | Pass criteria | Status | Evidence |
| --- | --- | --- | --- | --- |
| VMO-ACC-001 | Export Access local table row counts and compare to model row counts after refresh. | Exact row-count match for all seven required local tables. | Pending | Not run. |
| VMO-ACC-002 | Compare `qry_Financial_Year_Total` to `Total GL Amount` by financial year. | $0.00 delta for every financial year. | Pending | Not run. |
| VMO-ACC-003 | Compare Access GL period grouping to `Period Total` by year and period. | $0.00 delta for every comparable period bucket. | Pending | Not run. |
| VMO-ACC-004 | Compare `qry_Reconciliation_GL_Summary` status counts to reconciliation measures/matrix. | 0-row delta for every match status. | Pending | Not run. |
| VMO-ACC-005 | Compare `qry_Reconciliation_GL_Summary` variance amounts to `Reconciliation GL Variance Amount`. | $0.00 delta for every match status. | Pending | Not run. |
| VMO-ACC-006 | Compare `qry_Reconciliation_GL_Summary_Other_Subsystems` to the validation page/card. | $0.00 delta, or a documented rounded Access output difference. | Pending | Not run. |
| VMO-ACC-007 | Compare grouped `tbl_VMO_Data` export to `Total VMO Amount`. | $0.00 delta for every comparable bucket. | Pending | Not run. |
| VMO-ACC-008 | Compare grouped `tbl_VMO_GL_Transactions` export to `Total Mapped Amount` and `Mapped Transaction Count`. | $0.00 amount delta and 0-row count delta. | Pending | Not run. |
| VMO-ACC-009 | Compare exception flags in reconciliation exports to exception measures. | 0-row delta by side/status. | Pending | Not run. |
| VMO-ACC-010 | Profile required reporting keys for blanks. | No unexpected blank date, account, cost-centre, classification, or status keys. | Pending | Not run. |
| VMO-ACC-011 | Profile one-side lookup keys for duplicates before relationships are active. | No duplicate `Date[Date]`, classification key, account key, or cost-centre key on active one sides. | Pending | Not run. |
| VMO-ACC-012 | Inventory report pages, visuals, and field bindings against `report-implementation-spec.md`. | Required pages and bindings are present. | Pending | Not run. |

## SQL-Host-Dependent Validation Not Run

Leave these checks explicitly open until the host/database and publish pathway are supplied:

- SQL Server host, database, schema, and credential binding.
- Gateway data source registration and scheduled refresh.
- SQL object availability for local tables and external dependencies.
- SQL row-count and amount parity against the accepted Access-sample window.
- Production-sized refresh performance and workspace access validation.
