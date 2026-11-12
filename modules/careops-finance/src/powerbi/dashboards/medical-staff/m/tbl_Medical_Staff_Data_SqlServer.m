let
    // Later SQL binding only; local interim validation uses the Access templates.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    SqlSchemaName = "dbo",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    RemoteTable = Source{[Schema=SqlSchemaName, Item="tbl_Medical_Staff_Data"]}[Data],
    RequiredColumns = {
        "Staff ID",
        "Date",
        "Financial Year",
        "Period",
        "Staff Status",
        "FTE",
        "Payroll Amount",
        "Department",
        "Grade",
        "Record State"
    },
    #"Selected Contract Columns" = Table.SelectColumns(RemoteTable, RequiredColumns),
    #"Typed Columns" = Table.TransformColumnTypes(
        #"Selected Contract Columns",
        {
            {"Staff ID", type text},
            {"Date", type date},
            {"Financial Year", Int64.Type},
            {"Period", Int64.Type},
            {"Staff Status", type text},
            {"FTE", type number},
            {"Payroll Amount", Currency.Type},
            {"Department", type text},
            {"Grade", type text},
            {"Record State", type text}
        }
    ),
    #"Renamed Model Columns" = Table.RenameColumns(
        #"Typed Columns",
        {
            {"Staff ID", "StaffID"},
            {"Financial Year", "FinancialYear"},
            {"Staff Status", "StaffStatus"},
            {"Payroll Amount", "PayrollAmount"},
            {"Record State", "RecordState"}
        }
    )
in
    #"Renamed Model Columns"
