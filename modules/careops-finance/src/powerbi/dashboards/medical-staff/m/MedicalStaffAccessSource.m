let
    AccessDatabasePath = "data/raw/Medical_Staff_Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true])
in
    Source
