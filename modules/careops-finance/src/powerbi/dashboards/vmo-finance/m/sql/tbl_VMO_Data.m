let
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    Navigation = Source{[Schema = SqlSchemaName, Item = "tbl_VMO_Data"]}[Data]
in
    Navigation
