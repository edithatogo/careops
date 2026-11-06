let
    // Later SQL binding only; local interim validation uses the Access templates.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    SqlSchemaName = "dbo",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    RemoteTable = Source{[Schema=SqlSchemaName, Item="tbl_Medical_Staff_History"]}[Data],
    RequiredColumns = {
        "History Row ID",
        "Staff ID",
        "Effective Date",
        "End Date",
        "Record State",
        "Event Type",
        "FTE",
        "Payroll Amount",
        "Department",
        "Grade"
    },
    #"Selected Contract Columns" = Table.SelectColumns(RemoteTable, RequiredColumns),
    #"Typed Columns" = Table.TransformColumnTypes(
        #"Selected Contract Columns",
        {
            {"History Row ID", type text},
            {"Staff ID", type text},
            {"Effective Date", type date},
            {"End Date", type date},
            {"Record State", type text},
            {"Event Type", type text},
            {"FTE", type number},
            {"Payroll Amount", Currency.Type},
            {"Department", type text},
            {"Grade", type text}
        }
    ),
    #"Renamed Model Columns" = Table.RenameColumns(
        #"Typed Columns",
        {
            {"History Row ID", "HistoryRowID"},
            {"Staff ID", "StaffID"},
            {"Effective Date", "EffectiveDate"},
            {"End Date", "EndDate"},
            {"Record State", "RecordState"},
            {"Event Type", "EventType"},
            {"Payroll Amount", "PayrollAmount"}
        }
    )
in
    #"Renamed Model Columns"
