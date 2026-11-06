# SQL Server Source Contracts

## Objective

Define the SQL Server source layer that will replace Access files for published Power BI refresh while preserving the dashboard table contracts already identified from the Access databases.

## Scope

- VMO Finance source contract.
- Medical Staff source contract.
- Shared date, cost-centre, and organisational lookup contracts.
- Power BI source parameters and gateway assumptions.
- Mapping from current Access table names to SQL Server tables or views.

## Requirements

- Identify the minimum tables/views and columns needed for each dashboard.
- Define SQL Server object names, schemas, grain, keys, and required data types.
- Decide whether each source object should be a table, view, or stored query exposed through a view.
- Keep SQL Server server/database names parameterised as `SqlServerName` and `SqlDatabaseName`.
- Document gateway, authentication, and refresh ownership assumptions without committing credentials.
- Update source templates or docs so published models do not depend on `.accdb` files.

## Acceptance Criteria

- `docs/sql-server-publish-plan.md` lists source contracts for both dashboards.
- Each dashboard has a table/column mapping from Access-derived source to SQL Server view/table.
- Shared model docs describe SQL Server-backed shared dimensions.
- Open source gaps are explicit and assigned for resolution.
- Access-exposed DSNs are recorded as discovery evidence only; SQL Server host/listener is supplied as `<sql-server-host>`, while database/schema, reachable endpoint, credential mode, and gateway binding must be confirmed separately.
- No server names, database names, credentials, or secrets are committed.
