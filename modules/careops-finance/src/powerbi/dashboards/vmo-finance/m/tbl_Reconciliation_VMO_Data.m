let
    AccessDatabasePath = "data/raw/VMO Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true]),
    Navigation = Source{[Item = "tbl_Reconciliation_VMO_Data", Kind = "Table"]}[Data]
in
    Navigation
