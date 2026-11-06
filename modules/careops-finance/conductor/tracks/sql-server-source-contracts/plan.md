# Plan

- [x] Review current dashboard docs and M templates for required fields.
- [x] Identify minimum VMO Finance SQL Server tables/views and columns.
- [x] Identify minimum Medical Staff SQL Server tables/views and columns.
- [x] Define shared SQL Server date and cost-centre contracts.
- [x] Document source object names, schema, grain, keys, and data types.
- [x] Update `docs/sql-server-publish-plan.md` with mappings and gaps.
- [x] Confirm gateway/authentication assumptions without storing secrets.
- [x] Extract redacted Access linked-table and saved-query source metadata.
- [x] Add read-only ODBC DSN handoff script for source-computer CA/Magiq inspection.
- [x] Document DSN-to-server/database/schema/object mapping rules.
- [x] Add local DSN source-contract validation: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\dsn\Test-OdbcDsnSourceContract.ps1`.
- [x] Add optional redacted DSN evidence export for source-machine operators: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\dsn\Test-OdbcDsnSourceContract.ps1 -WriteEvidence`.
- [ ] Run live SQL Server confirmation and validation. Host/listener is supplied as `<sql-server-host>`; database/schema, reachable endpoint, credential mode, and gateway binding are not yet confirmed.
