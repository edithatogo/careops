# VMO Acceptance Pack

Status: concrete acceptance pack for work possible before the production SQL host, database, credential mode, and gateway binding are known.

This pack accepts the interim Access-sample build only. It does not claim SQL Server publish readiness.

## Evidence To Capture

Store evidence in an ignored local folder such as `data/profile/vmo-acceptance/` or attach it to the build ticket. Do not commit source extracts.

| Evidence item | Minimum content | Acceptance use |
| --- | --- | --- |
| Access sample export manifest | Export timestamp, Access database path, exported table/query names, row counts. | Proves the sample source used for checks. |
| Power BI model snapshot | Model refresh timestamp, table row counts, measure list, relationship list. | Proves the model loaded the same sample. |
| Reconciliation workbook or CSV | One row per acceptance check with Access value, Power BI value, delta, tolerance, pass/fail, reviewer. | Finance-facing sign-off table. |
| Exception register | Unmatched GL rows, unmatched VMO rows, classification exceptions, and known causes. | Confirms unresolved differences are visible and reviewable. |
| SQL-host-open-items note | Host/database/schema/credential/gateway questions and owner. | Separates real blockers from completed sample acceptance. |

## Sample-Result Checks To Perform Before SQL Host Is Known

All checks below are run against the local Access sample or exported Access query results. Currency totals must match to cents unless the Access query rounds to whole dollars; if rounding is present, record the Access rounding rule in the evidence.

| ID | Check | Access-side source | Power BI result | Pass criteria | Evidence |
| --- | --- | --- | --- | --- | --- |
| VMO-ACC-001 | Local table row counts | `tbl_Calendar`, `tbl_GL_Transactions`, `tbl_VMO_Data`, `tbl_VMO_GL_Transactions`, `tbl_VMO_GL_Classification`, `tbl_Reconciliation_GL_Data`, `tbl_Reconciliation_VMO_Data` exports. | Table row counts after refresh. | Exact row-count match for every loaded table. | Row-count table with export timestamp and refresh timestamp. |
| VMO-ACC-002 | GL financial-year total | `qry_Financial_Year_Total`. | `Total GL Amount` grouped by `Date[Financial Year]`. | Exact amount match for each financial year. | Reconciliation workbook tab `gl_fy_total`. |
| VMO-ACC-003 | GL period total | `qry_Financial_Year_Total` or GL export grouped by year and period. | `Period Total` grouped by `Date[Financial Year]` and `Date[Period]`. | Exact amount match for each year/period bucket. | Reconciliation workbook tab `gl_period_total`. |
| VMO-ACC-004 | Reconciliation status counts | `qry_Reconciliation_GL_Summary`. | `Matched GL Rows`, `Unmatched GL Rows`, and status matrix counts. | Exact count match by match status. | Reconciliation workbook tab `status_counts`. |
| VMO-ACC-005 | Reconciliation status variance | `qry_Reconciliation_GL_Summary`. | `Reconciliation GL Variance Amount` grouped by match status. | Exact amount match by match status. | Reconciliation workbook tab `status_variance`. |
| VMO-ACC-006 | Other subsystem variance | `qry_Reconciliation_GL_Summary_Other_Subsystems`. | Validation page card or equivalent measure for other subsystem variance. | Exact amount match, or every difference is explained and signed off. | Reconciliation workbook tab `other_subsystems`. |
| VMO-ACC-007 | VMO total | `tbl_VMO_Data` export grouped to the report grain. | `Total VMO Amount` by financial year and period where date mapping exists. | Exact amount match by comparable bucket. | Reconciliation workbook tab `vmo_totals`. |
| VMO-ACC-008 | Mapped bridge total | `tbl_VMO_GL_Transactions` export grouped to the report grain. | `Total Mapped Amount` and `Mapped Transaction Count`. | Exact amount and count match. | Reconciliation workbook tab `mapped_bridge`. |
| VMO-ACC-009 | Exception counts | Reconciliation table exports and Access exception flags. | `GL Exception Rows`, `VMO Exception Rows`, `Exception Rows`. | Exact count match by side and exception flag. | Exception register. |
| VMO-ACC-010 | Null reporting keys | Access exports profiled for date, account code, cost-centre code, classification key/status fields. | Power BI table profile or DAX count of blank keys. | No unexpected blanks in required keys; expected blanks are listed with source reason. | Data-quality tab `null_keys`. |
| VMO-ACC-011 | Duplicate lookup keys | Access exports for `tbl_Calendar`, `tbl_VMO_GL_Classification`, optional account/cost-centre lookups if present. | Relationship one-side uniqueness checks. | One-side keys are unique before active relationships are enabled. | Data-quality tab `duplicate_keys`. |
| VMO-ACC-012 | Visual field contract | Report implementation spec and PBIR field bindings. | Report pages and visuals from the generated PBIR/sample Desktop report. | Required pages exist and visuals bind to expected measures/columns. | Page/visual inventory output or screenshot evidence. |

## DAX Measures To Verify

Verify the measure exists, references the intended table/column, uses the expected format string, and returns the same value as the Access-side control for the current filter context.

| Measure | Expected expression | Format | Acceptance check |
| --- | --- | --- | --- |
| `Total GL Amount` | `SUM ( 'GL Transactions'[Amount] )` | `$#,##0;($#,##0);-` | Matches `qry_Financial_Year_Total` and GL export totals. |
| `Total VMO Amount` | `SUM ( 'VMO Data'[Amount] )` | `$#,##0;($#,##0);-` | Matches `tbl_VMO_Data` export totals after applying the same date/account filters. |
| `Total Mapped Amount` | `SUM ( 'VMO GL Transactions'[Amount] )` | `$#,##0;($#,##0);-` | Matches mapped bridge export totals. |
| `GL Transaction Count` | `COUNTROWS ( 'GL Transactions' )` | `#,##0` | Matches `tbl_GL_Transactions` row count. |
| `VMO Record Count` | `COUNTROWS ( 'VMO Data' )` | `#,##0` | Matches `tbl_VMO_Data` row count. |
| `Mapped Transaction Count` | `COUNTROWS ( 'VMO GL Transactions' )` | `#,##0` | Matches `tbl_VMO_GL_Transactions` row count. |
| `Distinct GL Accounts` | `DISTINCTCOUNT ( 'GL Transactions'[Account Code] )` | `#,##0` | Matches distinct account count from GL export. |
| `Distinct Cost Centres` | `DISTINCTCOUNT ( 'GL Transactions'[Cost Centre Code] )` | `#,##0` | Matches distinct cost-centre count from GL export. |
| `Reconciliation Variance` | `[Total GL Amount] - [Total VMO Amount]` | `$#,##0;($#,##0);-` | Equals recalculated GL minus VMO delta in the reconciliation workbook. |
| `Reconciliation Variance %` | `DIVIDE ( [Reconciliation Variance], [Total GL Amount] )` | `0.0%` | Matches workbook percentage; blank/zero denominator handling is documented. |
| `Mapped Variance` | `[Total GL Amount] - [Total Mapped Amount]` | `$#,##0;($#,##0);-` | Equals recalculated GL minus mapped bridge delta. |
| `Matched GL Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation GL Data' ), 'Reconciliation GL Data'[Match Status] = "Matched" )` | `#,##0` | Matches Access GL reconciliation matched count. |
| `Unmatched GL Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation GL Data' ), 'Reconciliation GL Data'[Match Status] <> "Matched" )` | `#,##0` | Matches Access GL reconciliation unmatched count. |
| `Matched VMO Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation VMO Data' ), 'Reconciliation VMO Data'[Match Status] = "Matched" )` | `#,##0` | Matches Access VMO reconciliation matched count. |
| `Unmatched VMO Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation VMO Data' ), 'Reconciliation VMO Data'[Match Status] <> "Matched" )` | `#,##0` | Matches Access VMO reconciliation unmatched count. |
| `Reconciliation GL Variance Amount` | `SUM ( 'Reconciliation GL Data'[Variance Amount] )` | `$#,##0;($#,##0);-` | Matches Access GL reconciliation variance by status and total. |
| `Reconciliation VMO Variance Amount` | `SUM ( 'Reconciliation VMO Data'[Variance Amount] )` | `$#,##0;($#,##0);-` | Matches Access VMO reconciliation variance by status and total. |
| `GL Exception Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation GL Data' ), 'Reconciliation GL Data'[Exception Flag] = TRUE () )` | `#,##0` | Matches Access GL exception flag count. |
| `VMO Exception Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation VMO Data' ), 'Reconciliation VMO Data'[Exception Flag] = TRUE () )` | `#,##0` | Matches Access VMO exception flag count. |
| `Exception Rows` | `[GL Exception Rows] + [VMO Exception Rows]` | `#,##0` | Equals combined GL and VMO exception counts. |
| `Financial Year Total` | `CALCULATE ( [Total GL Amount], ALLEXCEPT ( 'Date', 'Date'[Financial Year] ) )` | `$#,##0;($#,##0);-` | Ignores period only as intended and matches financial-year control total. |
| `Period Total` | `CALCULATE ( [Total GL Amount], ALLEXCEPT ( 'Date', 'Date'[Financial Year], 'Date'[Period] ) )` | `$#,##0;($#,##0);-` | Matches year/period control total. |
| `Current Period GL Amount` | `CALCULATE ( [Total GL Amount], 'Date'[Date] <= MAX ( 'Date'[Date] ) )` | `$#,##0;($#,##0);-` | Produces expected cumulative amount in the current date filter context. |

## Reconciliation Acceptance Table

Copy this table into the acceptance workbook or ticket and complete one row per check and grain.

| Check ID | Grain | Access/control source | Access/control value | Power BI measure or visual | Power BI value | Delta | Tolerance | Result | Evidence path | Reviewer | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VMO-ACC-001 | Table | Access table export | TBD | Power BI row count | TBD | 0 expected | 0 rows | Pending | TBD | TBD | One row per loaded table. |
| VMO-ACC-002 | Financial year | `qry_Financial_Year_Total` | TBD | `Total GL Amount` | TBD | 0 expected | $0.00 | Pending | TBD | TBD | One row per financial year. |
| VMO-ACC-003 | Financial year/period | `qry_Financial_Year_Total` or GL grouped export | TBD | `Period Total` | TBD | 0 expected | $0.00 | Pending | TBD | TBD | Confirm Access period definition. |
| VMO-ACC-004 | Match status | `qry_Reconciliation_GL_Summary` | TBD | `Matched GL Rows` / `Unmatched GL Rows` | TBD | 0 expected | 0 rows | Pending | TBD | TBD | One row per status. |
| VMO-ACC-005 | Match status | `qry_Reconciliation_GL_Summary` | TBD | `Reconciliation GL Variance Amount` | TBD | 0 expected | $0.00 | Pending | TBD | TBD | One row per status. |
| VMO-ACC-006 | Subsystem | `qry_Reconciliation_GL_Summary_Other_Subsystems` | TBD | Other subsystem validation measure/card | TBD | 0 expected | $0.00 unless rounded | Pending | TBD | TBD | Explain any rounded Access output. |
| VMO-ACC-007 | Financial year/period | `tbl_VMO_Data` grouped export | TBD | `Total VMO Amount` | TBD | 0 expected | $0.00 | Pending | TBD | TBD | Use only comparable date buckets. |
| VMO-ACC-008 | Financial year/period | `tbl_VMO_GL_Transactions` grouped export | TBD | `Total Mapped Amount` | TBD | 0 expected | $0.00 | Pending | TBD | TBD | Include mapped row count. |
| VMO-ACC-009 | Exception side/status | Reconciliation table exports | TBD | `GL Exception Rows`, `VMO Exception Rows`, `Exception Rows` | TBD | 0 expected | 0 rows | Pending | TBD | TBD | Tie to exception register. |
| VMO-ACC-010 | Required key | Access profiled export | TBD | Power BI blank-key count | TBD | 0 expected | 0 unexpected blanks | Pending | TBD | TBD | Known blanks require source reason. |
| VMO-ACC-011 | Lookup key | Access profiled export | TBD | Power BI duplicate-key count | TBD | 0 expected | 0 duplicates | Pending | TBD | TBD | Required before active one-side relationships. |
| VMO-ACC-012 | Page/visual | `report-implementation-spec.md` | Required page/visual list | PBIR/Desktop inventory | TBD | None | All required present | Pending | TBD | TBD | Include visual field bindings. |

## SQL-Host-Dependent Checks Left Open

These are deliberately open until the SQL host and publish pathway are known.

| Open check | Needed input | Acceptance condition after SQL host is known |
| --- | --- | --- |
| SQL host/database binding | `SqlServerName`, `SqlDatabaseName`, and final `SqlSchemaName`. | SQL templates refresh from the agreed database without changing table contracts. |
| Credential mode | Service account/user credential decision and authentication method. | Desktop and Service refresh both authenticate using the approved credential mode. |
| Gateway binding | Workspace, gateway cluster, data source registration, privacy level. | Dataset binds to the gateway data source and scheduled refresh succeeds. |
| SQL object availability | Confirmed tables/views for local equivalents and external dependencies. | SQL objects match the Access/sample table contract or documented mapping. |
| SQL row-count parity | SQL extracts for the same acceptance sample window. | SQL row counts equal Access/control counts for the agreed sample window or differences are explained. |
| SQL amount parity | SQL extracts for GL, VMO, mapped, and reconciliation outputs. | SQL totals match the acceptance workbook by year/period/status. |
| Incremental refresh policy | Finance-approved refresh window and date column. | Refresh policy uses a confirmed date column and preserves reconciliation totals. |
| Data privacy/classification | NSW Health data classification and workspace access list. | Dataset/report sharing and export settings meet the approved access model. |
| Performance threshold | Expected production row volumes and Service capacity/workspace. | Refresh and report interactions meet agreed limits on the production-sized sample. |
