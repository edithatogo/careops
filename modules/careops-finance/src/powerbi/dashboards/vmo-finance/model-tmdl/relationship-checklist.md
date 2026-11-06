# VMO Finance Relationship Checklist

Use this as the live semantic-model build checklist after the local Access sample queries are loaded, then reuse the same table contract when the SQL-backed queries are bound later. Table names below are the intended model names for the first live build.

## Required Tables

| Model table | Interim Access template | Later SQL query template | Load role |
| --- | --- | --- | --- |
| `Date` | `m/tbl_Calendar.m` | `m/sql/tbl_Calendar.m` | Canonical finance date dimension. |
| `GL Transactions` | `m/tbl_GL_Transactions.m` | `m/sql/tbl_GL_Transactions.m` | Primary GL fact. |
| `VMO Data` | `m/tbl_VMO_Data.m` | `m/sql/tbl_VMO_Data.m` | Primary VMO source fact. |
| `VMO GL Transactions` | `m/tbl_VMO_GL_Transactions.m` | `m/sql/tbl_VMO_GL_Transactions.m` | Mapped GL/VMO bridge fact. |
| `VMO GL Classification` | `m/tbl_VMO_GL_Classification.m` | `m/sql/tbl_VMO_GL_Classification.m` | Classification lookup. |
| `Reconciliation GL Data` | `m/tbl_Reconciliation_GL_Data.m` | `m/sql/tbl_Reconciliation_GL_Data.m` | GL-side reconciliation fact. |
| `Reconciliation VMO Data` | `m/tbl_Reconciliation_VMO_Data.m` | `m/sql/tbl_Reconciliation_VMO_Data.m` | VMO-side reconciliation fact. |

Optional SQL lookups from the shared contract:

| Model table | SQL object | Load role |
| --- | --- | --- |
| `Account` | `dbo.ca_MVRPT_ACCOUNT` | Account lookup if reachable in the publish database. |
| `Cost Centre` | `dbo.ca_MVRPT_COSTCENTRES` | Cost-centre lookup if reachable in the publish database. |

## Relationship Build

| From | To | Cardinality | Direction | Active | Notes |
| --- | --- | --- | --- | --- | --- |
| `GL Transactions[Date]` | `Date[Date]` | Many-to-one | Single | Yes | Primary GL trend and period filter path. |
| `VMO Data[Date]` | `Date[Date]` | Many-to-one | Single | Yes | Use only if `Date` is populated and typed as date. |
| `VMO GL Transactions[Date]` | `Date[Date]` | Many-to-one | Single | Yes | Bridge/mapping trend path. |
| `Reconciliation GL Data[Date]` | `Date[Date]` | Many-to-one | Single | Yes | GL reconciliation filters. |
| `Reconciliation VMO Data[Date]` | `Date[Date]` | Many-to-one | Single | Yes | VMO reconciliation filters. |
| `GL Transactions[Account Code]` | `Account[Account Code]` | Many-to-one | Single | Conditional | Create after `Account[Account Code]` uniqueness is confirmed. |
| `VMO Data[Account Code]` | `Account[Account Code]` | Many-to-one | Single | Conditional | Keep inactive if it creates ambiguous filter paths. |
| `VMO GL Transactions[Account Code]` | `Account[Account Code]` | Many-to-one | Single | Conditional | Create when the mapped table uses the same account code contract. |
| `Reconciliation GL Data[Account Code]` | `Account[Account Code]` | Many-to-one | Single | Conditional | Needed for reconciliation drill-down by account. |
| `Reconciliation VMO Data[Account Code]` | `Account[Account Code]` | Many-to-one | Single | Conditional | Needed for VMO-side drill-down by account. |
| `GL Transactions[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Single | Conditional | Create after cost-centre key uniqueness is confirmed. |
| `VMO Data[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Single | Conditional | Keep inactive if it creates ambiguous filter paths. |
| `VMO GL Transactions[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Single | Conditional | Create when the mapped table uses the same cost-centre contract. |
| `Reconciliation GL Data[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Single | Conditional | Needed for reconciliation drill-down by cost centre. |
| `Reconciliation VMO Data[Cost Centre Code]` | `Cost Centre[Cost Centre Code]` | Many-to-one | Single | Conditional | Needed for VMO-side drill-down by cost centre. |
| `VMO GL Transactions[Classification Key]` | `VMO GL Classification[Classification Key]` | Many-to-one | Single | Conditional | Use only if the live SQL contract exposes `Classification Key` on the mapped fact. |

## Date Handling

- Mark `Date[Date]` as the model date table.
- Sort period labels by a numeric period or period-start field where available.
- Use `Posted Date` for transaction detail only; keep `Date` as the default reporting relationship unless finance confirms otherwise.
- Do not create fact-to-fact relationships for GL, VMO, mapped, or reconciliation tables in the first build.

## Relationship Validation

- `Date[Date]` is unique and covers all fact-table dates.
- All active relationship columns are typed consistently across the many and one sides.
- Account and cost-centre lookup keys are unique before relationships are activated.
- No bidirectional relationship is enabled for the first build.
- Validation-only tables or Access query tie-out tables are hidden and have no active relationship paths to report facts.
