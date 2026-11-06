let
    // Keep server and database values parameterised; the SQL object contracts live in docs and SqlContracts.m.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false])
in
    Source
