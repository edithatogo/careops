# VMO SQL-backed M templates

These files are parallel templates for the later SQL Server-backed published
refresh path. They are not required for the current no-SQL-host interim build,
which validates the report against the local Access sample templates under
`../`.

- `VmoSqlServerSource.m` provides the parameterized SQL Server source block.
- Each table query mirrors the Access-backed query name from `m/` so the
  published dataset can swap from Access navigation to SQL Server navigation
  without changing the dashboard table contract.

Use the agreed SQL Server parameters. These are Power BI query parameters that
must be created or bound in Desktop/pbi-cli using `<sql-server-host>` for `SqlServerName` once the database/schema and credentials are available; they
are not local placeholder strings inside each table query:

- `SqlServerName`
- `SqlDatabaseName`
- `SqlSchemaName`

Set `SqlSchemaName` to `dbo` unless the final SQL contract uses a different
schema. Keeping it as a parameter makes the Access-sample validation state
separate from the later SQL Server binding state.

Before switching the report from Access validation to SQL Server refresh,
confirm the minimum columns listed in `docs/sql-server-publish-plan.md` are
present in SQL Server. The templates do not rename columns; the live model
should keep the DAX-facing names documented in
`model-tmdl/measure-catalogue.md`.
