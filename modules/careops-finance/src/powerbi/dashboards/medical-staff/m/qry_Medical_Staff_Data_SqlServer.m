let
    // Later SQL binding only; local interim validation uses the Access templates.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    SqlSchemaName = "dbo",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    RemoteView = Source{[Schema=SqlSchemaName, Item="qry_Medical_Staff_Data"]}[Data],
    RequiredColumns = {
        "Staff ID",
        "Staff Status",
        "FTE",
        "Payroll Amount"
    },
    #"Selected Contract Columns" = Table.SelectColumns(RemoteView, RequiredColumns),
    #"Typed Columns" = Table.TransformColumnTypes(
        #"Selected Contract Columns",
        {
            {"Staff ID", type text},
            {"Staff Status", type text},
            {"FTE", type number},
            {"Payroll Amount", Currency.Type}
        }
    ),
    #"Renamed Model Columns" = Table.RenameColumns(
        #"Typed Columns",
        {
            {"Staff ID", "StaffID"},
            {"Staff Status", "StaffStatus"},
            {"Payroll Amount", "PayrollAmount"}
        }
    )
in
    #"Renamed Model Columns"
