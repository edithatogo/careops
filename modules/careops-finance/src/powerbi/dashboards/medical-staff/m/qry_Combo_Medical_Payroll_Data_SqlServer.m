let
    // Later SQL binding only; local interim validation uses the Access templates.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    SqlSchemaName = "dbo",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    RemoteView = Source{[Schema=SqlSchemaName, Item="qry_Combo_Medical_Payroll_Data"]}[Data],
    RequiredColumns = {
        "Payroll Row ID",
        "Staff ID",
        "Date",
        "Financial Year",
        "Period",
        "Pay Component",
        "Payroll Amount",
        "FTE"
    },
    #"Selected Contract Columns" = Table.SelectColumns(RemoteView, RequiredColumns),
    #"Typed Columns" = Table.TransformColumnTypes(
        #"Selected Contract Columns",
        {
            {"Payroll Row ID", type text},
            {"Staff ID", type text},
            {"Date", type date},
            {"Financial Year", Int64.Type},
            {"Period", Int64.Type},
            {"Pay Component", type text},
            {"Payroll Amount", Currency.Type},
            {"FTE", type number}
        }
    ),
    #"Renamed Model Columns" = Table.RenameColumns(
        #"Typed Columns",
        {
            {"Payroll Row ID", "PayrollRowID"},
            {"Staff ID", "StaffID"},
            {"Financial Year", "FinancialYear"},
            {"Pay Component", "PayComponent"},
            {"Payroll Amount", "PayrollAmount"}
        }
    )
in
    #"Renamed Model Columns"
