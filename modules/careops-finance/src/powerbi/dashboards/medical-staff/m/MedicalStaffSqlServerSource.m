let
    // Bind these through Power BI parameters or deployment configuration when the SQL host exists.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    Source = Sql.Database(
        SqlServerName,
        SqlDatabaseName,
        [
            CreateNavigationProperties = false,
            CommandTimeout = #duration(0, 0, 10, 0)
        ]
    )
in
    Source
