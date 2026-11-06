let
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    Navigation = Source{[Schema = SqlSchemaName, Item = "tbl_Reconciliation_GL_Data"]}[Data]
in
    Navigation
