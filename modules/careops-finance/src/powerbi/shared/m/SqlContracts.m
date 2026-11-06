let
    SqlContracts = [
        Version = "1.0",
        Parameters = [
            SqlServerName = "SqlServerName",
            SqlDatabaseName = "SqlDatabaseName",
            DefaultSchema = "dbo"
        ],
        GatewayAssumptions = {
            "The published refresh reaches SQL Server through an on-premises data gateway.",
            "Gateway registration, authentication, and data-source credentials are managed outside this repository.",
            "Server names, database names, usernames, passwords, and secrets stay out of source control.",
            "The published model can read the agreed dbo objects without depending on Access files."
        ],
        SharedContracts = [
            Date = [
                SourceObject = "dbo.tbl_Calendar",
                ModelTable = "Date",
                Grain = "One row per date",
                KeyColumns = {"Date"},
                MinimumColumns = {"Date", "Financial Year", "Period", "Calendar Year", "Calendar Month", "Calendar Month Name", "Quarter"},
                Notes = "Canonical finance calendar for VMO and the candidate shared date dimension."
            ],
            WorkforceDate = [
                SourceObject = "dbo.tbl_WF_Calendar",
                ModelTable = "Workforce Calendar",
                Grain = "One row per date or reporting period",
                KeyColumns = {"Date"},
                MinimumColumns = {"Date", "Financial Year", "Period", "Calendar Year", "Calendar Month", "Quarter"},
                Notes = "Workforce calendar used by Medical Staff reporting."
            ],
            CostCentre = [
                SourceObject = "dbo.ca_MVRPT_COSTCENTRES",
                ModelTable = "Cost Centre",
                Grain = "One row per cost-centre code",
                KeyColumns = {"Cost Centre Code"},
                MinimumColumns = {"Cost Centre Code", "Cost Centre Name", "Cost Centre Group", "Status"},
                Notes = "Lookup is external until the SQL location and final object name are confirmed."
            ],
            Account = [
                SourceObject = "dbo.ca_MVRPT_ACCOUNT",
                ModelTable = "Account",
                Grain = "One row per account code",
                KeyColumns = {"Account Code"},
                MinimumColumns = {"Account Code", "Account Name", "Account Group", "Status"},
                Notes = "VMO GL lookup used for reconciliation and classification."
            ]
        ],
        VMOFinance = [
            BaseObjects = {
                [
                    SourceObject = "dbo.tbl_Calendar",
                    Kind = "table",
                    ModelTable = "Date",
                    Grain = "One row per date",
                    KeyColumns = {"Date"},
                    MinimumColumns = {"Date", "Financial Year", "Period", "Calendar Year", "Quarter", "Period Start", "Period End"},
                    Notes = "Calendar dimension used by all VMO facts."
                ],
                [
                    SourceObject = "dbo.tbl_GL_Transactions",
                    Kind = "table",
                    ModelTable = "GL Transactions",
                    Grain = "One row per GL posting line",
                    KeyColumns = {"GL Transaction ID"},
                    MinimumColumns = {"GL Transaction ID", "Date", "Financial Year", "Period", "Account Code", "Cost Centre Code", "Amount", "Narrative", "Source Reference", "Posted Date"},
                    Notes = "Primary GL fact for totals, counts, and reconciliation."
                ],
                [
                    SourceObject = "dbo.tbl_VMO_Data",
                    Kind = "table",
                    ModelTable = "VMO Data",
                    Grain = "One row per VMO source record",
                    KeyColumns = {"VMO Record ID"},
                    MinimumColumns = {"VMO Record ID", "Date", "Financial Year", "Period", "Account Code", "Cost Centre Code", "Amount", "Narrative", "Source Reference"},
                    Notes = "Primary VMO fact for reporting totals and variance."
                ],
                [
                    SourceObject = "dbo.tbl_VMO_GL_Transactions",
                    Kind = "table",
                    ModelTable = "VMO GL Transactions",
                    Grain = "One row per mapped GL line",
                    KeyColumns = {"VMO GL Transaction ID"},
                    MinimumColumns = {"VMO GL Transaction ID", "GL Transaction ID", "VMO Record ID", "Date", "Account Code", "Cost Centre Code", "Amount", "Match Status", "Variance Amount"},
                    Notes = "Bridge/fact used to tie GL and VMO records together."
                ],
                [
                    SourceObject = "dbo.tbl_VMO_GL_Classification",
                    Kind = "table",
                    ModelTable = "VMO GL Classification",
                    Grain = "One row per classification rule or lookup row",
                    KeyColumns = {"Classification Key"},
                    MinimumColumns = {"Classification Key", "Account Code", "Classification", "Subclassification", "Effective From", "Effective To", "Is Active"},
                    Notes = "Classification lookup used to map GL activity to reporting buckets."
                ],
                [
                    SourceObject = "dbo.tbl_Reconciliation_GL_Data",
                    Kind = "table",
                    ModelTable = "Reconciliation GL Data",
                    Grain = "One row per GL-side reconciliation row",
                    KeyColumns = {"Reconciliation GL Row ID"},
                    MinimumColumns = {"Reconciliation GL Row ID", "Date", "Financial Year", "Period", "Account Code", "Cost Centre Code", "Amount", "Match Status", "Exception Flag", "Variance Amount"},
                    Notes = "GL-side reconciliation fact for status and variance analysis."
                ],
                [
                    SourceObject = "dbo.tbl_Reconciliation_VMO_Data",
                    Kind = "table",
                    ModelTable = "Reconciliation VMO Data",
                    Grain = "One row per VMO-side reconciliation row",
                    KeyColumns = {"Reconciliation VMO Row ID"},
                    MinimumColumns = {"Reconciliation VMO Row ID", "Date", "Financial Year", "Period", "Account Code", "Cost Centre Code", "Amount", "Match Status", "Exception Flag", "Variance Amount"},
                    Notes = "VMO-side reconciliation fact for row-level comparison."
                ]
            },
            Views = {
                [
                    SourceObject = "dbo.qry_Financial_Year_Total",
                    Kind = "view",
                    ModelTable = "Validation Financial Year Total",
                    Grain = "One row per financial-year and period bucket",
                    KeyColumns = {"Financial Year", "Period"},
                    MinimumColumns = {"Financial Year", "Period", "Total GL Amount"},
                    Notes = "Validation view, not a substitute for the base fact."
                ],
                [
                    SourceObject = "dbo.qry_Reconciliation_GL_Data",
                    Kind = "view",
                    ModelTable = "Validation Reconciliation GL Data",
                    Grain = "One row per reconciliation detail row",
                    KeyColumns = {"Reconciliation GL Row ID"},
                    MinimumColumns = {"Reconciliation GL Row ID", "Match Status", "Variance Amount"},
                    Notes = "Validation shape used by the published reconciliation checks."
                ],
                [
                    SourceObject = "dbo.qry_Reconciliation_GL_Summary",
                    Kind = "view",
                    ModelTable = "Validation Reconciliation GL Summary",
                    Grain = "One row per summary bucket",
                    KeyColumns = {"Financial Year", "Period", "Match Status"},
                    MinimumColumns = {"Financial Year", "Period", "Match Status", "Row Count", "Variance Amount"},
                    Notes = "Validation summary for exception and status tie-out."
                ],
                [
                    SourceObject = "dbo.qry_Reconciliation_GL_Summary_Other_Subsystems",
                    Kind = "view",
                    ModelTable = "Validation Other Subsystems Summary",
                    Grain = "One row per summary bucket",
                    KeyColumns = {"Financial Year", "Period", "Subsystem"},
                    MinimumColumns = {"Financial Year", "Period", "Subsystem", "Row Count", "Variance Amount"},
                    Notes = "Validation summary for non-VMO comparison rows."
                ]
            ],
            Dependencies = {
                [
                    SourceObject = "dbo.tbl_Email_Addresses",
                    Kind = "dependency",
                    Status = "unconfirmed",
                    Notes = "Operational dependency that may remain outside the published finance database."
                ],
                [
                    SourceObject = "dbo.dbo_FMIS_GL_JOURNAL",
                    Kind = "dependency",
                    Status = "unconfirmed",
                    Notes = "Pass-through GL journal source; final SQL Server object type and location need confirmation."
                ]
            ],
            OpenQuestions = {
                "Are the reconciliation objects materialized tables or views in SQL Server?",
                "Is the account and cost-centre lookup in the same database or a separate one?",
                "Which date columns are authoritative for posting date, financial date, and reporting period?",
                "What is the final primary key for each reconciliation and transaction object?",
                "Do amounts require fixed decimal precision or currency-specific rounding rules?"
            }
        ],
        MedicalStaff = [
            BaseObjects = {
                [
                    SourceObject = "dbo.tbl_WF_Calendar",
                    Kind = "table",
                    ModelTable = "Workforce Calendar",
                    Grain = "One row per date or reporting period",
                    KeyColumns = {"Date"},
                    MinimumColumns = {"Date", "Financial Year", "Period", "Calendar Year", "Calendar Month", "Quarter", "Period Start", "Period End"},
                    Notes = "Workforce calendar for the medical staffing model."
                ],
                [
                    SourceObject = "dbo.tbl_Medical_Staff_Data",
                    Kind = "table",
                    ModelTable = "Medical Staff Data",
                    Grain = "One row per current staff record or pay-period snapshot",
                    KeyColumns = {"Staff ID"},
                    MinimumColumns = {"Staff ID", "Date", "Financial Year", "Period", "Staff Status", "FTE", "Payroll Amount", "Department", "Grade", "Record State"},
                    Notes = "Primary current-state medical staff fact."
                ],
                [
                    SourceObject = "dbo.tbl_Medical_Staff_History",
                    Kind = "table",
                    ModelTable = "Medical Staff History",
                    Grain = "One row per history event or effective-dated version",
                    KeyColumns = {"History Row ID"},
                    MinimumColumns = {"History Row ID", "Staff ID", "Effective Date", "End Date", "Record State", "Event Type", "FTE", "Payroll Amount", "Department", "Grade"},
                    Notes = "History fact for changes, overlaps, and current-versus-historical comparisons."
                ]
            },
            Views = {
                [
                    SourceObject = "dbo.qry_Medical_Staff_Data",
                    Kind = "view",
                    ModelTable = "Validation Medical Staff Data",
                    Grain = "One row per staff record or snapshot row",
                    KeyColumns = {"Staff ID"},
                    MinimumColumns = {"Staff ID", "Staff Status", "FTE", "Payroll Amount"},
                    Notes = "Validation view for tie-out against the current staff source."
                ],
                [
                    SourceObject = "dbo.qry_Combo_Medical_Payroll_Data",
                    Kind = "view",
                    ModelTable = "Medical Payroll Data",
                    Grain = "One row per staff member per payroll period and pay component",
                    KeyColumns = {"Payroll Row ID"},
                    MinimumColumns = {"Payroll Row ID", "Staff ID", "Date", "Financial Year", "Period", "Pay Component", "Payroll Amount", "FTE"},
                    Notes = "Payroll/FTE source for the summary measures."
                ],
                [
                    SourceObject = "dbo.qry_Employee_Sub",
                    Kind = "view",
                    ModelTable = "Employee Sub",
                    Grain = "One row per employee-subordinate or employee-attribute mapping",
                    KeyColumns = {"Employee ID", "Subordinate ID"},
                    MinimumColumns = {"Employee ID", "Subordinate ID", "Department", "Grade", "Status"},
                    Notes = "Helper mapping used only if the source is not already flattened."
                ]
            ],
            Dependencies = {
                [
                    SourceObject = "dbo.tbl_Calendar",
                    Kind = "dependency",
                    Status = "unconfirmed",
                    Notes = "Shared finance calendar dependency if the dashboard needs a finance-period crosswalk."
                ],
                [
                    SourceObject = "dbo.tbl_Email_Addresses",
                    Kind = "dependency",
                    Status = "unconfirmed",
                    Notes = "Operational dependency used by the Access source but not yet confirmed for SQL Server."
                ],
                [
                    SourceObject = "dbo.tbl_VMO_Data",
                    Kind = "dependency",
                    Status = "unconfirmed",
                    Notes = "Cross-dashboard comparison dependency, not a default relationship."
                ]
            ],
            OpenQuestions = {
                "Are the staff data and history objects current snapshots or fully effective-dated tables?",
                "Does the payroll source expose gross pay, total pay, or another measure as the contract amount?",
                "Which staff identifier is the canonical key across current, history, and payroll rows?",
                "Is the workforce calendar aligned to finance periods or a separate calendar hierarchy?",
                "Should the employee-sub mapping be kept as a view or promoted into a dimension table later?"
            }
        ]
    ]
in
    SqlContracts
