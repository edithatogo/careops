# SQL Source Discovery From Access Metadata

Generated on 2026-05-04 from read-only DAO metadata inspection of:

- `data/raw/VMO Reporting.accdb`
- `data/raw/Medical_Staff_Reporting.accdb`

The extractor is `scripts/Get-AccessSqlSources.ps1`. Generated JSON profiles were written under `data/profile/` and are intentionally ignored. Connection strings in those profiles are redacted for usernames, passwords, tokens, secrets, and keys.

## Method

The script opens each Access database through `DAO.DBEngine.OpenDatabase(..., ReadOnly=True)` and enumerates:

- `TableDefs`: linked table connection strings and `SourceTableName`.
- `QueryDefs`: saved Access SQL and pass-through connection strings where present.

No Power BI Desktop files or dashboard folders were mutated.

## SQL-Backed Linked Tables

### VMO Reporting

| Access object | DSN | Database hint | Source schema | Source object |
| --- | --- | --- | --- | --- |
| `ca_MVRPT_ACCOUNT` | `CA` | `WORKFORCE` | `ca` | `MVRPT_ACCOUNT` |
| `ca_MVRPT_COSTCENTRES` | `CA` | `WORKFORCE` | `ca` | `MVRPT_COSTCENTRES` |
| `dbo_FMIS_GL_JOURNAL` | `Magiq` | not exposed in Access connect string | `dbo` | `FMIS_GL_JOURNAL_2026` |

Access did not expose a SQL Server host name for these linked tables. The available server-level hint is the local ODBC DSN name.

### Medical Staff Reporting

| Access object | DSN | Database hint | Source schema | Source object |
| --- | --- | --- | --- | --- |
| `ca_FTE_EMPLOYEE_LAST_LHD_V` | `CA` | `WORKFORCE` | `ca` | `FTE_EMPLOYEE_LAST_LHD_V` |
| `ca_FTE_HYPERION_LHD_V` | `CA` | `WORKFORCE` | `ca` | `FTE_HYPERION_LHD_V` |
| `ca_FTE_RPT_AWARD_CODES_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_AWARD_CODES_DIM_MV` |
| `ca_FTE_RPT_COST_CENTRES_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_COST_CENTRES_DIM_MV` |
| `ca_FTE_RPT_EMP_TYPES_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_EMP_TYPES_DIM_MV` |
| `ca_FTE_RPT_PAYCLASS_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_PAYCLASS_DIM_MV` |
| `ca_MVRPT_COSTCENTRES` | `CA` | `WORKFORCE` | `ca` | `MVRPT_COSTCENTRES` |
| `dbo_FTE_IS_EMPLOYEE_INT` | `Magiq` | `MAGIQ_PRD` | `dbo` | `FTE_IS_EMPLOYEE_INT` |
| `dbo_FTE_IS_PAYROLL_INT` | `Magiq` | `MAGIQ_PRD` | `dbo` | `FTE_IS_PAYROLL_INT` |

Access did not expose SQL Server host names for these linked tables. The available server-level hints are the local ODBC DSNs `CA` and `Magiq`.

## Saved Query Findings

No SQL Server pass-through `QueryDef` objects with their own connection strings were found in either database.

The saved Access queries are local Access SQL that read from local tables and linked tables. Key query names that reference the linked SQL-backed objects include:

- VMO: `qry_Get_VMO_Data`, `qry_Reconciliation_Analysis_GL_Data`, `qry_Reconciliation_GL_Data`, `qry_Reconciliation_GL_Summary`, `qry_Reconciliation_VMO_Data`, `qry_Reconciliation_Union`.
- Medical Staff: `qry_Medical_Staff_Data`, `qry_Get_Medical_Staff_History`, `qry_Combo_Medical_Payroll_Data`, `qry_Employee_Sub`, `qry_Combo_VMO_Data`, `qry_Medical_FTE_Union`.

The full saved SQL text is available only in ignored profile JSON, not committed, because it may expose operational file paths and query internals.

## Non-SQL Linked Dependencies

The broader metadata pass also found linked file dependencies that are not SQL Server tables:

| Access database | Access object | Source hint |
| --- | --- | --- |
| VMO Reporting | `tbl_Email_Addresses` | Excel sheet `Cost_Centres$` in `Email_Addresses.xlsx` |
| VMO Reporting | `tbl_Excel_VMO_Data` | Excel sheet `ExpenditureReport$` in `VMO_Data.xlsx` |
| Medical Staff Reporting | `tbl_Calendar` | linked table from `VMO Reporting.accdb` |
| Medical Staff Reporting | `tbl_VMO_Data` | linked table from `VMO Reporting.accdb` |
| Medical Staff Reporting | `tbl_Email_Addresses` | Excel sheet `Cost_Centres$` in `Email_Addresses.xlsx` |

## Contract Implications

- The existing placeholder `dbo` SQL contract is not the same as the Access source metadata. The Access files point to `ca` schema objects in the `WORKFORCE` database through DSN `CA`, and `dbo` objects in the `Magiq` DSN, including `MAGIQ_PRD` for Medical Staff payroll/employee tables.
- VMO `dbo_FMIS_GL_JOURNAL` points at `dbo.FMIS_GL_JOURNAL_2026`; the database is not exposed in its Access connect string and must be resolved from the `Magiq` DSN or SQL Server access.
- `ca_MVRPT_COSTCENTRES` is shared between VMO and Medical Staff through the `WORKFORCE` database.
- Medical Staff FTE/reporting dimensions are already exposed as `ca` views/materialized views in `WORKFORCE`; published SQL contracts should preserve those object names or map them explicitly to curated views.
- Operator-supplied SQL Server host/listener: `<sql-server-host>`. Keep `SqlServerName` parameterised in Power BI and bind it to this value through deployment/operator configuration; database, schema, gateway, and credential details still need live validation.

## DSN Handoff Script

The repo-local handoff script is `scripts/Get-OdbcDsnSourceContract.ps1`. It is intended to be copied or run from this repo on the source computer that has the working Access ODBC DSNs. It does not need us to know the SQL Server host in advance.

Default inspection:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OdbcDsnSourceContract.ps1
```

Optional JSON export:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-OdbcDsnSourceContract.ps1 -OutPath .\data\profile\odbc-dsn-source-contract.json
```

Operator validation with redacted evidence:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\dsn\Test-OdbcDsnSourceContract.ps1 -WriteEvidence
```

This writes `data/profile/odbc-dsn-source-contract.evidence.json`. The `data/profile/` folder is ignored by git, so the evidence can stay local or be sent through the approved operational channel without committing source-machine details.

The script is read-only. It reads ODBC DSN registry configuration from:

- current-user DSNs under `HKCU\SOFTWARE\ODBC\ODBC.INI`;
- system DSNs under `HKLM\SOFTWARE\ODBC\ODBC.INI`;
- both 64-bit and 32-bit registry views.

For each requested DSN, defaulting to `CA` and `Magiq`, it captures:

- whether the DSN was found;
- DSN scope: user or system;
- registry view: 64-bit or 32-bit;
- registry path;
- driver path/name;
- configured server/address value, if present;
- configured default database/initial catalog value, if present;
- description;
- trusted/integrated authentication hint, if present.

It does not attempt a SQL Server connection, does not test credentials, and does not mutate DSNs, Access files, Power BI M templates, PBIR, or TMDL. By default it reports only the safe summary fields above. If `-IncludeAllDsnValues` is supplied, it includes all DSN registry values but redacts keys whose names look like usernames, passwords, tokens, secrets, or keys. The validation harness uses `-RedactOperatorIdentity` for evidence output so `computerName` and `currentUser` are stored as `<redacted>`.

## Local Next Steps With SQL Host Supplied

The operator has supplied the SQL Server host/listener `<sql-server-host>`. These are the remaining concrete steps that can be completed from the repo while database, schema, gateway, and credential binding remain unconfirmed:

1. Re-run `./scripts/Invoke-Validation.ps1 -Mode RepositoryHygiene -SkipPowerBiCli` and `./scripts/Invoke-Validation.ps1 -Mode SourceControlReady -SkipPowerBiCli` after any export refresh, and record the result in the acceptance notes.
2. Confirm the private GitHub remote settings and keep the first push out of this handoff pass.
3. Keep `docs/dashboard-acceptance.md` current with the blocker register, owner, and next action for each open publish item.
4. Preserve the live TMDL and PBIR exports in source control only after they pass the source-control gate, and capture the export timestamp or commit reference alongside them.
5. Keep deployment profiles disabled and leave `PublishRefreshReady` blocked until `PBI_SQL_DATABASE`, `PBI_GATEWAY_ID`, workspace, tenant/client credentials, and refresh ownership are supplied outside source control.

### Source Machine Runbook

Run these commands on the Windows source computer where the existing Access reports open successfully and where the `CA` and `Magiq` ODBC DSNs are configured:

```powershell
Set-Location '<repo path>'
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\dsn\Test-OdbcDsnSourceContract.ps1 -WriteEvidence
```

To use a different ignored evidence filename:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\dsn\Test-OdbcDsnSourceContract.ps1 -WriteEvidence -EvidenceOutPath .\data\profile\odbc-dsn-source-contract.source-machine.json
```

Verify the evidence JSON before sharing it:

- `dsnRecords` has at least one record for `CA` and one for `Magiq`.
- Each expected DSN has `found: true` on the registry view that the source machine uses.
- `server` is populated for both `CA` and `Magiq`; this is the SQL Server host/listener discovery evidence.
- `database` is populated where the DSN carries a default database. `CA` is expected to confirm `WORKFORCE`; `Magiq` is expected to confirm `MAGIQ_PRD` for the Medical Staff objects and to help resolve the VMO GL database.
- `sourceMappings` has 12 rows and still maps `CA` to the `ca` objects and `Magiq` to the `dbo` objects listed below.
- `computerName`, `currentUser`, and any DSN keys matching usernames, passwords, tokens, secrets, or keys are `<redacted>`.

### DSN To Source Object Mapping

The script embeds the Access-derived mappings from this document so the source computer output can be interpreted without opening the Access files again:

| DSN | DSN supplies | Access metadata supplies | Resulting contract row |
| --- | --- | --- | --- |
| `CA` | SQL Server host and default database, expected to confirm `WORKFORCE` | dashboard name, Access linked-table name, schema `ca`, source object name | `CA` -> server/database -> `ca.<object>` |
| `Magiq` | SQL Server host and default database, expected to confirm `MAGIQ_PRD` for Medical Staff and resolve VMO GL database | dashboard name, Access linked-table name, schema `dbo`, source object name | `Magiq` -> server/database -> `dbo.<object>` |

The mapping rule is:

1. Match the Access linked-table `DSN=` value to the inspected ODBC DSN record.
2. Take `server` and, where configured, default `database` from the DSN record.
3. Take `dashboard`, `accessObject`, `accessDatabaseHint`, `sourceSchema`, and `sourceObject` from the Access metadata.
4. Treat `accessDatabaseHint` as a hint until the DSN or live SQL Server access confirms the real database.

Current Access-derived object mappings:

| Dashboard | Access object | DSN | Database hint | Source schema | Source object |
| --- | --- | --- | --- | --- | --- |
| VMO Reporting | `ca_MVRPT_ACCOUNT` | `CA` | `WORKFORCE` | `ca` | `MVRPT_ACCOUNT` |
| VMO Reporting | `ca_MVRPT_COSTCENTRES` | `CA` | `WORKFORCE` | `ca` | `MVRPT_COSTCENTRES` |
| VMO Reporting | `dbo_FMIS_GL_JOURNAL` | `Magiq` | not exposed in Access connect string | `dbo` | `FMIS_GL_JOURNAL_2026` |
| Medical Staff Reporting | `ca_FTE_EMPLOYEE_LAST_LHD_V` | `CA` | `WORKFORCE` | `ca` | `FTE_EMPLOYEE_LAST_LHD_V` |
| Medical Staff Reporting | `ca_FTE_HYPERION_LHD_V` | `CA` | `WORKFORCE` | `ca` | `FTE_HYPERION_LHD_V` |
| Medical Staff Reporting | `ca_FTE_RPT_AWARD_CODES_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_AWARD_CODES_DIM_MV` |
| Medical Staff Reporting | `ca_FTE_RPT_COST_CENTRES_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_COST_CENTRES_DIM_MV` |
| Medical Staff Reporting | `ca_FTE_RPT_EMP_TYPES_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_EMP_TYPES_DIM_MV` |
| Medical Staff Reporting | `ca_FTE_RPT_PAYCLASS_DIM_MV` | `CA` | `WORKFORCE` | `ca` | `FTE_RPT_PAYCLASS_DIM_MV` |
| Medical Staff Reporting | `ca_MVRPT_COSTCENTRES` | `CA` | `WORKFORCE` | `ca` | `MVRPT_COSTCENTRES` |
| Medical Staff Reporting | `dbo_FTE_IS_EMPLOYEE_INT` | `Magiq` | `MAGIQ_PRD` | `dbo` | `FTE_IS_EMPLOYEE_INT` |
| Medical Staff Reporting | `dbo_FTE_IS_PAYROLL_INT` | `Magiq` | `MAGIQ_PRD` | `dbo` | `FTE_IS_PAYROLL_INT` |

## Reproduction

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-AccessSqlSources.ps1 -DatabasePath '.\data\raw\VMO Reporting.accdb'
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-AccessSqlSources.ps1 -DatabasePath '.\data\raw\Medical_Staff_Reporting.accdb'
```

To inspect all linked file dependencies and saved Access SQL locally:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-AccessSqlSources.ps1 -DatabasePath '.\data\raw\VMO Reporting.accdb' -OutDir '.\data\profile\all-source-hints' -IncludeNonSqlHints
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-AccessSqlSources.ps1 -DatabasePath '.\data\raw\Medical_Staff_Reporting.accdb' -OutDir '.\data\profile\all-source-hints' -IncludeNonSqlHints
```
