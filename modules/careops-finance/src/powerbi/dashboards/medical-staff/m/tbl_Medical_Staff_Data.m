let
    AccessDatabasePath = "data/raw/Medical_Staff_Reporting.accdb",
    Source = Access.Database(File.Contents(AccessDatabasePath), [CreateNavigationProperties = true]),
    LocalTable = Source{[Item="tbl_Medical_Staff_Data",Kind="Table"]}[Data],
    #"Typed Columns" = Table.TransformColumnTypes(LocalTable, {})
in
    #"Typed Columns"
