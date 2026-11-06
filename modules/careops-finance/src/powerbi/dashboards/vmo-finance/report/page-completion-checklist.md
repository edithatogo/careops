# VMO report page completion checklist

Use this checklist when the report is being built in PBIR or Power BI Desktop.
The concrete page contract is `report-implementation-spec.md`.

## Executive Summary

- [ ] KPI cards for GL total, VMO total, variance, variance %, and record count.
- [ ] Trend line by financial year and period.
- [ ] Stacked bar by reconciliation status.
- [ ] Slicers for financial year, period, cost centre, account, and classification.
- [ ] Visual IDs match the `executive_summary` entries in `report-implementation-spec.md`.
- [ ] Year and period selections cross-filter all summary visuals.

## Reconciliation Detail

- [ ] Matrix by financial year, period, cost centre, account, and classification.
- [ ] Bar chart by reconciliation status.
- [ ] Variance table for drill-down review.
- [ ] Filters for financial year, period, status, cost centre, and classification.
- [ ] Matrix, status bar, and variance review interactions are validated.

## Classification And Cost Centre

- [ ] Matrix by classification, subclassification, account, and cost centre.
- [ ] Bar chart for `Total GL Amount`, `Total VMO Amount`, and `Reconciliation Variance`.
- [ ] Top-N cost-centre exceptions visual.
- [ ] Filters for financial year, period, classification, account, and cost centre.
- [ ] Visual IDs match the `classification_cost_centre` entries in `report-implementation-spec.md`.

## Exceptions

- [ ] Exception table with drillthrough fields.
- [ ] Unmatched GL and unmatched VMO counts.
- [ ] Status histogram.
- [ ] Filters for financial year, period, exception flag, subsystem, and cost centre.
- [ ] Exception table supports transaction-level review on the detail page.

## Transaction Detail

- [ ] Line-level transaction table.
- [ ] Source amount, posting date, and classification fields.
- [ ] Drillthrough from exception and reconciliation pages.
- [ ] Filters for financial year, period, transaction type, cost centre, and account.

## Validation

- [ ] Reconciliation control cards.
- [ ] Delta tables and pass/fail indicators.
- [ ] Validation set, financial year, and period filters.
- [ ] Notes or evidence table for any unresolved differences.
- [ ] `pbi report validate` passes for generated PBIR artifacts.
