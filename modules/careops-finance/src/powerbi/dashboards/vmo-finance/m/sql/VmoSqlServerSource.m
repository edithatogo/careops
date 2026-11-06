let
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false])
in
    Source
