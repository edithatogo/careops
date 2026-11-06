let
    AccessDatabasePath = "data/raw/VMO Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true])
in
    Source
