# VMO Finance Measure Catalogue

Status: source-control catalogue for later TMDL/pbi-cli implementation. Do not treat this file as an exported TMDL artifact.

Recommended measure table: `VMO Measures`.

## Model Naming Assumptions

The SQL M templates load from the agreed SQL contract and the live model should
rename the raw query names to these report-facing model names before measures
are created.

| Model table | Source contract |
| --- | --- |
| `Date` | `dbo.tbl_Calendar` |
| `GL Transactions` | `dbo.tbl_GL_Transactions` |
| `VMO Data` | `dbo.tbl_VMO_Data` |
| `VMO GL Transactions` | `dbo.tbl_VMO_GL_Transactions` |
| `VMO GL Classification` | `dbo.tbl_VMO_GL_Classification` |
| `Reconciliation GL Data` | `dbo.tbl_Reconciliation_GL_Data` |
| `Reconciliation VMO Data` | `dbo.tbl_Reconciliation_VMO_Data` |
| `Account` | `dbo.ca_MVRPT_ACCOUNT`, if reachable |
| `Cost Centre` | `dbo.ca_MVRPT_COSTCENTRES`, if reachable |

## Base Totals

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `Total GL Amount` | `SUM ( 'GL Transactions'[Amount] )` | `$#,##0;($#,##0);-` | `Totals` | Baseline GL amount. |
| `Total VMO Amount` | `SUM ( 'VMO Data'[Amount] )` | `$#,##0;($#,##0);-` | `Totals` | Baseline VMO amount. |
| `Total Mapped Amount` | `SUM ( 'VMO GL Transactions'[Amount] )` | `$#,##0;($#,##0);-` | `Totals` | Amount in the mapping/bridge table. |
| `GL Transaction Count` | `COUNTROWS ( 'GL Transactions' )` | `#,##0` | `Counts` | GL row volume. |
| `VMO Record Count` | `COUNTROWS ( 'VMO Data' )` | `#,##0` | `Counts` | VMO source row volume. |
| `Mapped Transaction Count` | `COUNTROWS ( 'VMO GL Transactions' )` | `#,##0` | `Counts` | Mapping row volume. |
| `Distinct GL Accounts` | `DISTINCTCOUNT ( 'GL Transactions'[Account Code] )` | `#,##0` | `Counts` | Account breadth in GL rows. |
| `Distinct Cost Centres` | `DISTINCTCOUNT ( 'GL Transactions'[Cost Centre Code] )` | `#,##0` | `Counts` | Cost-centre breadth in GL rows. |

## Reconciliation

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `Reconciliation Variance` | `[Total GL Amount] - [Total VMO Amount]` | `$#,##0;($#,##0);-` | `Reconciliation` | Headline GL minus VMO delta. |
| `Reconciliation Variance %` | `DIVIDE ( [Reconciliation Variance], [Total GL Amount] )` | `0.0%` | `Reconciliation` | Variance as a share of GL. |
| `Mapped Variance` | `[Total GL Amount] - [Total Mapped Amount]` | `$#,##0;($#,##0);-` | `Reconciliation` | GL minus mapped bridge amount. |
| `Matched GL Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation GL Data' ), 'Reconciliation GL Data'[Match Status] = "Matched" )` | `#,##0` | `Reconciliation` | Matched GL-side reconciliation rows. |
| `Unmatched GL Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation GL Data' ), 'Reconciliation GL Data'[Match Status] <> "Matched" )` | `#,##0` | `Reconciliation` | GL rows needing review. |
| `Matched VMO Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation VMO Data' ), 'Reconciliation VMO Data'[Match Status] = "Matched" )` | `#,##0` | `Reconciliation` | Matched VMO-side reconciliation rows. |
| `Unmatched VMO Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation VMO Data' ), 'Reconciliation VMO Data'[Match Status] <> "Matched" )` | `#,##0` | `Reconciliation` | VMO rows needing review. |
| `Reconciliation GL Variance Amount` | `SUM ( 'Reconciliation GL Data'[Variance Amount] )` | `$#,##0;($#,##0);-` | `Reconciliation` | GL-side variance total. |
| `Reconciliation VMO Variance Amount` | `SUM ( 'Reconciliation VMO Data'[Variance Amount] )` | `$#,##0;($#,##0);-` | `Reconciliation` | VMO-side variance total. |

## Exceptions And Validation

| Measure | DAX | Format | Display folder | Purpose |
| --- | --- | --- | --- | --- |
| `GL Exception Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation GL Data' ), 'Reconciliation GL Data'[Exception Flag] = TRUE () )` | `#,##0` | `Exceptions` | GL reconciliation exceptions. |
| `VMO Exception Rows` | `CALCULATE ( COUNTROWS ( 'Reconciliation VMO Data' ), 'Reconciliation VMO Data'[Exception Flag] = TRUE () )` | `#,##0` | `Exceptions` | VMO reconciliation exceptions. |
| `Exception Rows` | `[GL Exception Rows] + [VMO Exception Rows]` | `#,##0` | `Exceptions` | Combined exceptions. |
| `Financial Year Total` | `CALCULATE ( [Total GL Amount], ALLEXCEPT ( 'Date', 'Date'[Financial Year] ) )` | `$#,##0;($#,##0);-` | `Validation` | Year-level control total. |
| `Period Total` | `CALCULATE ( [Total GL Amount], ALLEXCEPT ( 'Date', 'Date'[Financial Year], 'Date'[Period] ) )` | `$#,##0;($#,##0);-` | `Validation` | Period-level control total. |
| `Current Period GL Amount` | `CALCULATE ( [Total GL Amount], 'Date'[Date] <= MAX ( 'Date'[Date] ) )` | `$#,##0;($#,##0);-` | `Validation` | Current filter-context GL total. |

## Implementation Notes

- Apply these to `VMO Measures` unless the final model uses table-local measures.
- Replace column names only after source schema validation, not during catalogue editing.
- Keep bridge relationships from `VMO GL Transactions` to the two base facts inactive until uniqueness is verified.
- If `Account` and `Cost Centre` dimensions are unavailable, keep distinct-count measures on fact-table codes for the first build.
- Create simple measures with `pbi measure create`; pipe multi-line DAX through stdin so PowerShell does not collapse line breaks.
- Use `model-tmdl/relationship-checklist.md` before creating measures that depend on `Date`, `Account`, or `Cost Centre` filter paths.
- Verify every measure against the acceptance pack at
  `conductor/tracks/vmo-dashboard-completion/acceptance-pack.md` before
  treating the Access-sample build as accepted.

## Acceptance Verification Summary

| Measure group | Required verification | SQL-host dependency |
| --- | --- | --- |
| Base totals and counts | Match Access table/query exports for the accepted sample window. | None for Access-sample acceptance. |
| Reconciliation | Match Access reconciliation summary counts and variance amounts by status. | SQL rerun required after host/database binding. |
| Exceptions | Match exception flags and unmatched-row counts from reconciliation exports. | SQL rerun required after host/database binding. |
| Validation/date totals | Match financial-year and period controls and confirm date filter behavior. | SQL rerun required after host/database binding. |

Example creation commands:

```powershell
pbi measure create "Total GL Amount" -t "VMO Measures" -e "SUM ( 'GL Transactions'[Amount] )" --format-string "$#,##0;($#,##0);-"
pbi measure create "Total VMO Amount" -t "VMO Measures" -e "SUM ( 'VMO Data'[Amount] )" --format-string "$#,##0;($#,##0);-"
pbi measure create "GL Transaction Count" -t "VMO Measures" -e "COUNTROWS ( 'GL Transactions' )" --format-string "#,##0"
```
