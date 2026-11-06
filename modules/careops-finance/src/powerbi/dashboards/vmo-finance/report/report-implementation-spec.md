# VMO Finance Report Implementation Spec

Status: concrete build package. This is not a Power BI Desktop export.

Canvas: 1280 x 720.

## Field Contract

Measures:

- `tbl_GL_Transactions[Total GL Amount]`
- `tbl_VMO_Data[Total VMO Amount]`
- `tbl_VMO_GL_Transactions[Reconciliation Variance]`
- `tbl_VMO_GL_Transactions[Reconciliation Variance %]`
- `tbl_GL_Transactions[GL Row Count]`
- `tbl_Reconciliation_GL_Data[Matched Rows]`
- `tbl_Reconciliation_GL_Data[Unmatched GL Rows]`
- `tbl_Reconciliation_VMO_Data[Unmatched VMO Rows]`
- `tbl_Reconciliation_GL_Data[Exception Rows]`
- `qry_Reconciliation_GL_Summary_Other_Subsystems[Other Subsystems Variance]`

Columns:

- `tbl_Calendar[Financial Year]`
- `tbl_Calendar[Period]`
- `tbl_Calendar[Date]`
- `tbl_GL_Transactions[Account]`
- `tbl_GL_Transactions[Cost Centre]`
- `tbl_GL_Transactions[Transaction Type]`
- `tbl_GL_Transactions[Posting Date]`
- `tbl_GL_Transactions[Source Transaction ID]`
- `tbl_Reconciliation_GL_Data[Match Status]`
- `tbl_Reconciliation_GL_Data[Exception Flag]`
- `tbl_Reconciliation_GL_Data[Subsystem]`
- `tbl_Reconciliation_GL_Data[Variance Amount]`
- `tbl_Reconciliation_GL_Data[Classification]`
- `tbl_VMO_GL_Classification[Classification]`

## Pages And Visuals

### Executive Summary (`executive_summary`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `card_total_gl` | card | 24,24,216,92 | field `tbl_GL_Transactions[Total GL Amount]` |
| `card_total_vmo` | card | 256,24,216,92 | field `tbl_VMO_Data[Total VMO Amount]` |
| `card_variance` | card | 488,24,216,92 | field `tbl_VMO_GL_Transactions[Reconciliation Variance]` |
| `card_variance_pct` | card | 720,24,216,92 | field `tbl_VMO_GL_Transactions[Reconciliation Variance %]` |
| `card_record_count` | card | 952,24,304,92 | field `tbl_GL_Transactions[GL Row Count]` |
| `trend_amount_by_period` | line | 24,136,736,272 | category `tbl_Calendar[Period]`, value `tbl_GL_Transactions[Total GL Amount]` |
| `bar_reconciliation_status` | stacked_bar | 784,136,472,272 | category `tbl_Reconciliation_GL_Data[Match Status]`, value `tbl_Reconciliation_GL_Data[Matched Rows]` |
| `slicer_financial_year` | slicer | 24,432,216,92 | field `tbl_Calendar[Financial Year]` |
| `slicer_period` | slicer | 256,432,216,92 | field `tbl_Calendar[Period]` |
| `slicer_cost_centre` | slicer | 488,432,240,92 | field `tbl_GL_Transactions[Cost Centre]` |
| `slicer_account` | slicer | 744,432,240,92 | field `tbl_GL_Transactions[Account]` |
| `slicer_classification` | slicer | 1000,432,256,92 | field `tbl_VMO_GL_Classification[Classification]` |

Filters and interactions:

- Year and period filter every visual on the page.
- Cost centre, account, and classification filter cards, trend, and status bar.
- Reconciliation status selection filters cards and should support navigation to
  `reconciliation_detail` when navigation is added.

### Reconciliation Detail (`reconciliation_detail`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `matrix_reconciliation_bridge` | matrix | 24,24,760,396 | rows `tbl_Calendar[Financial Year]`, value `tbl_VMO_GL_Transactions[Reconciliation Variance]` |
| `bar_status_variance` | bar | 808,24,448,260 | category `tbl_Reconciliation_GL_Data[Match Status]`, value `tbl_VMO_GL_Transactions[Reconciliation Variance]` |
| `table_variance_review` | table | 24,444,1232,232 | values `tbl_Reconciliation_GL_Data[Match Status]`, `tbl_Reconciliation_GL_Data[Variance Amount]`, `tbl_Reconciliation_GL_Data[Classification]` |
| `slicer_recon_status` | slicer | 808,308,216,92 | field `tbl_Reconciliation_GL_Data[Match Status]` |
| `slicer_recon_classification` | slicer | 1040,308,216,92 | field `tbl_Reconciliation_GL_Data[Classification]` |

Filters and interactions:

- Page filters: financial year, period, status, cost centre, and classification.
- `bar_status_variance` uses Top 10 by `tbl_Reconciliation_GL_Data[Variance Amount]`.
- Matrix selections filter the status bar and variance review table.

### Classification And Cost Centre (`classification_cost_centre`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `matrix_classification_cost_centre` | matrix | 24,24,760,396 | rows `tbl_VMO_GL_Classification[Classification]`, value `tbl_VMO_GL_Transactions[Reconciliation Variance]` |
| `bar_cost_centre_variance` | bar | 808,24,448,260 | category `tbl_GL_Transactions[Cost Centre]`, value `tbl_VMO_GL_Transactions[Reconciliation Variance]` |
| `table_top_cost_centre_exceptions` | table | 24,444,1232,232 | values `tbl_GL_Transactions[Cost Centre]`, `tbl_GL_Transactions[Account]`, `tbl_Reconciliation_GL_Data[Variance Amount]` |
| `slicer_classification_page` | slicer | 808,308,216,92 | field `tbl_VMO_GL_Classification[Classification]` |
| `slicer_account_page` | slicer | 1040,308,216,92 | field `tbl_GL_Transactions[Account]` |

Filters and interactions:

- Top-N cost-centre exceptions show the ten largest absolute variances.
- Classification and account selections filter all visuals on the page.

### Exceptions (`exceptions`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `card_unmatched_gl` | card | 24,24,240,96 | field `tbl_Reconciliation_GL_Data[Unmatched GL Rows]` |
| `card_unmatched_vmo` | card | 288,24,240,96 | field `tbl_Reconciliation_VMO_Data[Unmatched VMO Rows]` |
| `card_exception_rows` | card | 552,24,240,96 | field `tbl_Reconciliation_GL_Data[Exception Rows]` |
| `hist_status` | bar | 816,24,440,236 | category `tbl_Reconciliation_GL_Data[Match Status]`, value `tbl_Reconciliation_GL_Data[Exception Rows]` |
| `table_exception_detail` | table | 24,288,1232,388 | values `tbl_Reconciliation_GL_Data[Subsystem]`, `tbl_Reconciliation_GL_Data[Match Status]`, `tbl_Reconciliation_GL_Data[Variance Amount]`, `tbl_GL_Transactions[Source Transaction ID]` |
| `slicer_exception_flag` | slicer | 24,144,216,92 | field `tbl_Reconciliation_GL_Data[Exception Flag]` |
| `slicer_subsystem` | slicer | 256,144,280,92 | field `tbl_Reconciliation_GL_Data[Subsystem]` |

Filters and interactions:

- Exception flag filters all exception cards and tables.
- Subsystem filters the exception table and status histogram.
- Exception table row selection supports review on `transaction_detail`.

### Transaction Detail (`transaction_detail`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `table_transaction_detail` | table | 24,24,1232,520 | values `tbl_GL_Transactions[Source Transaction ID]`, `tbl_GL_Transactions[Posting Date]`, `tbl_GL_Transactions[Transaction Type]`, `tbl_GL_Transactions[Account]`, `tbl_GL_Transactions[Cost Centre]`, `tbl_Reconciliation_GL_Data[Classification]`, `tbl_Reconciliation_GL_Data[Variance Amount]` |
| `slicer_transaction_type` | slicer | 24,568,280,92 | field `tbl_GL_Transactions[Transaction Type]` |
| `slicer_transaction_account` | slicer | 320,568,280,92 | field `tbl_GL_Transactions[Account]` |
| `slicer_transaction_cost_centre` | slicer | 616,568,280,92 | field `tbl_GL_Transactions[Cost Centre]` |

### Validation (`validation`)

| Visual ID | Type | Position | Binding |
| --- | --- | --- | --- |
| `card_gl_tieout` | card | 24,24,240,96 | field `tbl_GL_Transactions[Total GL Amount]` |
| `card_vmo_tieout` | card | 288,24,240,96 | field `tbl_VMO_Data[Total VMO Amount]` |
| `card_other_subsystems` | card | 552,24,300,96 | field `qry_Reconciliation_GL_Summary_Other_Subsystems[Other Subsystems Variance]` |
| `table_validation_deltas` | table | 24,152,760,360 | values `tbl_Calendar[Financial Year]`, `tbl_Calendar[Period]`, `tbl_VMO_GL_Transactions[Reconciliation Variance]` |
| `matrix_validation_status` | matrix | 808,152,448,360 | rows `tbl_Reconciliation_GL_Data[Match Status]`, value `tbl_Reconciliation_GL_Data[Exception Rows]` |
| `slicer_validation_year` | slicer | 24,544,240,92 | field `tbl_Calendar[Financial Year]` |
| `slicer_validation_period` | slicer | 280,544,240,92 | field `tbl_Calendar[Period]` |

Filters and interactions:

- Validation year and period filter cards, delta table, and validation matrix.
- Matrix selection filters the delta table to unresolved statuses.

## PBIR Build

Run `Build-VmoReportPbir.ps1` only after the VMO dataset reference is available.
The script uses `--no-sync` and does not reload Desktop.
