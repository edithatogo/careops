let
    // Later SQL binding only; local interim validation uses the Access templates.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    SqlSchemaName = "dbo",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    RemoteView = Source{[Schema=SqlSchemaName, Item="qry_Employee_Sub"]}[Data],
    RequiredColumns = {
        "Employee ID",
        "Subordinate ID",
        "Department",
        "Grade",
        "Status"
    },
    #"Selected Contract Columns" = Table.SelectColumns(RemoteView, RequiredColumns),
    #"Typed Columns" = Table.TransformColumnTypes(
        #"Selected Contract Columns",
        {
            {"Employee ID", type text},
            {"Subordinate ID", type text},
            {"Department", type text},
            {"Grade", type text},
            {"Status", type text}
        }
    ),
    #"Renamed Model Columns" = Table.RenameColumns(
        #"Typed Columns",
        {
            {"Employee ID", "EmployeeID"},
            {"Subordinate ID", "SubordinateID"}
        }
    )
in
    #"Renamed Model Columns"
