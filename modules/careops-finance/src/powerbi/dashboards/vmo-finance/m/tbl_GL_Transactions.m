let
    AccessDatabasePath = "data/raw/VMO Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true]),
    Navigation = Source{[Item = "tbl_GL_Transactions", Kind = "Table"]}[Data]
in
    Navigation
