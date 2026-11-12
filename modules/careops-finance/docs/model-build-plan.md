# Power BI Model Build Plan

Status: implementation package for later Power BI Desktop, pbi-cli, or TMDL application. This plan does not mutate any PBIX/PBIP file.

## Operating Position

Build two standalone semantic models first:

- `vmo-finance`: VMO activity, GL transaction, classification, and reconciliation reporting.
- `medical-staff`: current staff, payroll/FTE, workforce calendar, and staff-history reporting.

Keep common implementation rules in `src/powerbi/shared/m/` so both models can later be exported to TMDL with predictable table, relationship, and measure names. Do not create a combined shared semantic model until both dashboards refresh and validate independently.

## Shared Model Rules

- Import SQL Server tables or views through parameterised M. Access is a local profiling/source-extraction input only.
- Use business-facing model table names. Keep `tbl_*` names only in source-facing M query names and comments.
- Hide surrogate/source helper columns after relationships and validation measures are working.
- Create measures in dedicated measure tables when applying in Desktop/TMDL:
  - `VMO Measures`
  - `Medical Staff Measures`
  - optional later `Shared Finance Measures`
- Use single-direction, many-to-one relationships from fact tables to dimensions unless a bridge requirement is explicitly proven.
- Mark date tables with their real date column before adding time-intelligence measures.

## VMO Finance Tables

| Model table | Source object | Role | Grain | Required implementation notes |
| --- | --- | --- | --- | --- |
| `Date` | `dbo.tbl_Calendar` | Dimension | One row per finance calendar date | Mark as date table on `Date`. Include financial year, period, calendar year, month, quarter, period start, period end. |
| `GL Transactions` | `dbo.tbl_GL_Transactions` | Fact | One row per GL posting line | Main amount fact. Normalize `Account Code` and `Cost Centre Code`. Date relationship uses reporting/posting `Date`. |
| `VMO Data` | `dbo.tbl_VMO_Data` | Fact | One row per VMO source record | Main VMO-side amount fact. Normalize account and cost-centre keys. |
| `VMO GL Transactions` | `dbo.tbl_VMO_GL_Transactions` | Bridge/fact | One row per mapped GL/VMO transaction | Use for reconciliation-level mappings and matched/unmatched status. Avoid bidirectional filters until validated. |
| `VMO GL Classification` | `dbo.tbl_VMO_GL_Classification` | Lookup | One row per classification rule/key | Relate by `Classification Key` if present; otherwise by normalized `Account Code` only after uniqueness is proven. |
| `Reconciliation GL Data` | `dbo.tbl_Reconciliation_GL_Data` | Reconciliation fact | One row per GL-side reconciliation row | Supports matched/unmatched, exception, and variance measures. |
| `Reconciliation VMO Data` | `dbo.tbl_Reconciliation_VMO_Data` | Reconciliation fact | One row per VMO-side reconciliation row | Supports VMO-side reconciliation checks. |
| `Account` | `dbo.ca_MVRPT_ACCOUNT` or confirmed replacement | Dimension | One row per account code | Optional for first build if lookup source is unavailable; required before account hierarchy pages are final. |
| `Cost Centre` | `dbo.ca_MVRPT_COSTCENTRES` or confirmed replacement | Dimension | One row per cost-centre code | Optional for first build if lookup source is unavailable; key must match shared normalisation rule. |

## VMO Finance Relationships

| From table.column | To table.column | Cardinality | Active | Filter direction | Notes |
| --- | --- | --- | --- | --- | --- |
| `GL Transactions[Date]` | `Date[Date]` | Many-to-one | Yes | Single | Primary GL reporting date. |
| `VMO Data[Date]` | `Date[Date]` | Many-to-one | Yes | Single | Primary VMO reporting date. |
| `VMO GL Transactions[Date]` | `Date[Date]` | Many-to-one | Yes | Single | Bridge/fact reporting date. |
| `Reconciliation GL Data[Date]` | `Date[Date]` | Many-to-one | Yes | Single | Reconciliation period analysis. |
| `Reconciliation VMO Data[Date]` | `Date[Date]` | Many-to-one | Yes | Single | Reconciliation period analysis. |
| `GL Transactions[Account Code]` | `Account[Account Code]` | Many-to-one | Yes when lookup exists | Single | Use normalized text keys. |
| `VMO Data[Account Code]` | `Account[Account Code]` | Many-to-one | Yes when lookup exists | Single | Use normalized text keys. |
| `VMO GL Classification[Account Code]` | `Account[Account Code]` | Many-to-one | No initially | Single | Activate only if rule uniqueness is proven. |
| `GL Transactions[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Yes when lookup exists | Single | Use normalized text keys. |
| `VMO Data[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Yes when lookup exists | Single | Use normalized text keys. |
| `VMO GL Transactions[GL Transaction ID]` | `GL Transactions[GL Transaction ID]` | Many-to-one | No initially | Single | Keep inactive until row uniqueness is verified; measures can use `TREATAS` or `USERELATIONSHIP` later if needed. |
| `VMO GL Transactions[VMO Record ID]` | `VMO Data[VMO Record ID]` | Many-to-one | No initially | Single | Keep inactive until bridge semantics are verified. |

## Medical Staff Tables

| Model table | Source object | Role | Grain | Required implementation notes |
| --- | --- | --- | --- | --- |
| `Workforce Calendar` | `dbo.tbl_WF_Calendar` | Dimension | One row per date or workforce reporting period | Mark as date table on `Date` when row grain is daily. If period-only, add a true date table before time intelligence. |
| `Medical Staff Data` | `dbo.tbl_Medical_Staff_Data` | Fact/current snapshot | One row per staff record or staff-period row | Main current staff/FTE source. Normalize staff ID, department, status, and period fields. |
| `Medical Staff History` | `dbo.tbl_Medical_Staff_History` | History fact | One row per staff history event/version | Use `Effective Date` for history trend relationship; keep `End Date` inactive if modelled. |
| `Medical Payroll Data` | `dbo.qry_Combo_Medical_Payroll_Data` or confirmed replacement | Fact | One row per staff/pay-period/pay-component row | Optional but required for payroll amount measures. Relate by staff ID and date/period. |
| `Medical Staff` | derived from staff data/history | Dimension | One row per staff ID | Build later if staff attributes are duplicated across fact rows or history needs clean slicing. |
| `Department` | derived or confirmed lookup | Dimension | One row per department/cost centre | Build later when department keys are stable. |

## Medical Staff Relationships

| From table.column | To table.column | Cardinality | Active | Filter direction | Notes |
| --- | --- | --- | --- | --- | --- |
| `Medical Staff Data[Date]` | `Workforce Calendar[Date]` | Many-to-one | Yes | Single | Current-state trend date. |
| `Medical Staff History[Effective Date]` | `Workforce Calendar[Date]` | Many-to-one | Yes | Single | History event trend date. |
| `Medical Staff History[End Date]` | `Workforce Calendar[Date]` | Many-to-one | No | Single | Use only for end-date analysis. |
| `Medical Payroll Data[Date]` | `Workforce Calendar[Date]` | Many-to-one | Yes when table exists | Single | Payroll/FTE trends. |
| `Medical Staff Data[Staff ID]` | `Medical Staff[Staff ID]` | Many-to-one | Yes when dimension exists | Single | Use normalized staff key. |
| `Medical Staff History[Staff ID]` | `Medical Staff[Staff ID]` | Many-to-one | Yes when dimension exists | Single | Use normalized staff key. |
| `Medical Payroll Data[Staff ID]` | `Medical Staff[Staff ID]` | Many-to-one | Yes when table and dimension exist | Single | Use normalized staff key. |

## Date Table Implementation

### VMO Finance

Use `Date` from `dbo.tbl_Calendar` if it has one row per date. Required output columns:

- `Date`
- `Calendar Year`
- `Calendar Month`
- `Calendar Month Name`
- `Quarter`
- `Financial Year`
- `Period`
- `Period Start`
- `Period End`
- `Month End`

Implementation steps:

1. Convert `Date`, `Period Start`, `Period End`, and `Month End` to `date` in Power Query.
2. Sort `Calendar Month Name` by `Calendar Month` if both exist.
3. Mark `Date` as the date table using `Date[Date]`.
4. Create a `Financial Period Label` calculated column only if the source does not already provide a stable label.

### Medical Staff

Use `Workforce Calendar` from `dbo.tbl_WF_Calendar` if it is daily. If it is period-grain only, create a separate calculated table named `Date` for DAX time intelligence and keep `Workforce Calendar` as a reporting-period dimension.

Required daily-calendar output columns:

- `Date`
- `Calendar Year`
- `Calendar Month`
- `Calendar Month Name`
- `Quarter`
- `Financial Year`
- `Period`
- `Period Start`
- `Period End`

Implementation steps:

1. Verify whether `tbl_WF_Calendar` is daily or period-only.
2. If daily, mark `Workforce Calendar[Date]` as the date table.
3. If period-only, create a daily `Date` table using the min/max fact dates and relate period attributes separately.
4. Use `DATEADD` measures only after a marked date table is present.

## Measure Implementation Order

### VMO Finance

1. Create base row-count and amount measures.
2. Create reconciliation variance measures from base totals.
3. Create matched/unmatched/exception status measures.
4. Create period and financial-year validation measures.
5. Add optional account/cost-centre distinct counts after dimensions exist.

### Medical Staff

1. Create staff count, FTE, payroll amount, and base row-count measures.
2. Create prior-period and delta measures after date-table marking.
3. Create history coverage and data-quality measures.
4. Create source dependency/validation measures if source-inventory tables are present.

## TMDL And pbi-cli Notes

- Store source-control catalogues in `src/powerbi/dashboards/*/model-tmdl/measure-catalogue.md` until a real TMDL export exists.
- When applying measures with pbi-cli, pipe multi-line DAX through stdin rather than passing it as a collapsed `-e` argument.
- Export finished standalone models before any shared merge:
  - `pbi database export-tmdl src/powerbi/dashboards/vmo-finance/model-tmdl`
  - `pbi database export-tmdl src/powerbi/dashboards/medical-staff/model-tmdl`
- Do not export shared TMDL into `src/powerbi/shared/model-tmdl/` until both standalone models are validated and the merge-readiness gate passes.

## Validation Gate

Before report completion, validate:

- every fact table has expected row counts against SQL/Access exports;
- every active many-to-one relationship has unique keys on the one side;
- date tables are marked and time-intelligence measures return non-error values;
- base totals tie out to source Access reports or SQL validation views;
- inactive bridge relationships are documented before use in measures;
- live-export TMDL exists for both standalone dashboards, required table TMDL
  files are present, and currently exported catalogue measures remain present in
  table TMDL;
- no local file path, server name, credential, or raw data extract is committed.
