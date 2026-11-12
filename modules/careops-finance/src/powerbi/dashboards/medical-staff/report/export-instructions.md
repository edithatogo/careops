# Medical Staff Export Instructions

## Desktop Export

- Use the current generated exports as Access-sample validation artifacts for the interim no-SQL-host build.
- After SQL Server binding is completed and validated, regenerate the semantic model export under `src/powerbi/dashboards/medical-staff/model-tmdl/live-export/`.
- Keep generated report source artifacts under `src/powerbi/dashboards/medical-staff/report/pbir/`.

## Placeholder Rule

- Do not create fake TMDL or report export files that imply SQL Server refresh binding has already happened.
- Keep Access-sample exports and SQL-bound exports clearly labelled by folder or handoff notes.

## Source Parameters

- Published refresh should bind `SqlServerName` and `SqlDatabaseName`.
- Published refresh should bind `SqlSchemaName`; default to `dbo` only while the SQL contract still uses that schema.
- Keep secrets, gateway settings, and credentials out of git.
- Keep source-controlled M placeholders as `SET_BY_PARAMETER` for host/database values until environment-specific deployment supplies them.

## pbi-cli Handoff

Use this sequence after the live model has been created from the SQL-backed M templates and the SQL parameters have been bound:

```powershell
pbi connect
pbi table list
pbi relationship list
pbi measure list
pbi report validate
pbi database export-tmdl .\src\powerbi\dashboards\medical-staff\model-tmdl
pbi report validate --path .\src\powerbi\dashboards\medical-staff\report
```

Do not run `pbi report reload` as part of this worker handoff; Desktop mutation is out of scope for this task.
