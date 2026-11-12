let
    // Later SQL binding only; local interim validation uses the Access templates.
    SqlServerName = "SET_BY_PARAMETER",
    SqlDatabaseName = "SET_BY_PARAMETER",
    SqlSchemaName = "dbo",
    Source = Sql.Database(SqlServerName, SqlDatabaseName, [CreateNavigationProperties = false]),
    RemoteTable = Source{[Schema=SqlSchemaName, Item="tbl_WF_Calendar"]}[Data],
    RequiredColumns = {
        "Date",
        "Financial Year",
        "Period",
        "Calendar Year",
        "Calendar Month",
        "Quarter",
        "Period Start",
        "Period End"
    },
    #"Selected Contract Columns" = Table.SelectColumns(RemoteTable, RequiredColumns),
    #"Typed Columns" = Table.TransformColumnTypes(
        #"Selected Contract Columns",
        {
            {"Date", type date},
            {"Financial Year", Int64.Type},
            {"Period", Int64.Type},
            {"Calendar Year", Int64.Type},
            {"Calendar Month", Int64.Type},
            {"Quarter", type text},
            {"Period Start", type date},
            {"Period End", type date}
        }
    ),
    #"Renamed Model Columns" = Table.RenameColumns(
        #"Typed Columns",
        {
            {"Financial Year", "FinancialYear"},
            {"Calendar Year", "CalendarYear"},
            {"Calendar Month", "CalendarMonth"},
            {"Period Start", "PeriodStart"},
            {"Period End", "PeriodEnd"}
        }
    )
in
    #"Renamed Model Columns"
