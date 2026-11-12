# Synthetic VMO period reconciliation slice

`scripts/Build-SyntheticVmoPeriodSlice.ps1` turns the fictional fixture at
`tests/fixtures/finance/synthetic-vmo-period-reconciliation-v1.json` into a
small JSON report slice. It joins GL and VMO facts to a unique calendar by
`periodKey`, sorts by the calendar's `sortOrder`, and emits period and annual
amounts and variances.

Run it with:

```powershell
./scripts/Build-SyntheticVmoPeriodSlice.ps1 `
  -FixturePath ./tests/fixtures/finance/synthetic-vmo-period-reconciliation-v1.json `
  -OutputPath ./out/synthetic-vmo-period-slice.json `
  -AsOfDate ([datetime]"2026-10-25")
```

The selected fixture produces monthly GL totals of 41,000, 37,000 and 29,000;
VMO totals of 42,000, 36,500 and 28,500; and variances of 1,000, -500 and
-500. Both annual totals are 107,000, which demonstrates why the period rows
are required to reveal cancelling differences.

This contract is deliberately synthetic and does not alter the current Access
or parameterized SQL bindings, the PBIR dataset, the finance ledger, or the
production VMO schema. It is a reproducible source-to-measure fixture, not a
Power BI engine execution or rendered report receipt. `SourceControlReady`
runs the fixture regression through `tests/finance/Test-SyntheticVmoPeriodSlice.ps1`.
Native model relationships, report rendering, visual filtering and actual
provider behavior still require a qualified Power BI runtime and selected
interface.
