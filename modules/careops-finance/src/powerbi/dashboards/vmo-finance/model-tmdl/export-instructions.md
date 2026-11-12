# VMO model export instructions

Use these steps only after the model has been built in Power BI Desktop and the
export has been verified.

1. In the no-SQL-host interim state, connect the report to the local Access
   sample and complete sample validation.
2. When SQL Server is available, bind `SqlServerName`, `SqlDatabaseName`, and
   `SqlSchemaName` before the production refresh validation pass.
3. Build and save the semantic model in Desktop.
4. Export the model using the repo's approved TMDL or pbi-tools workflow.
5. Place the exported semantic model source under `src/powerbi/dashboards/vmo-finance/model-tmdl/`.
6. Keep the exported report source under `src/powerbi/dashboards/vmo-finance/report/`.
7. Remove placeholder notes only after the corresponding real export is present.

Do not create synthetic TMDL files that imply a Desktop export happened when it
did not.
