let
    NormalizeTextKey = (value as any) as nullable text =>
        let
            textValue = try Text.From(value) otherwise null,
            trimmedValue = if textValue = null then null else Text.Trim(textValue),
            upperValue = if trimmedValue = null then null else Text.Upper(trimmedValue)
        in
            if upperValue = null or upperValue = "" then null else upperValue,

    NormalizeDate = (value as any) as nullable date =>
        try Date.From(value) otherwise null,

    NormalizeCostCentreCode = (value as any) as nullable text =>
        NormalizeTextKey(value),

    NormalizeStaffId = (value as any) as nullable text =>
        NormalizeTextKey(value),

    SharedFinanceContracts = [
        Version = "1.0",
        Parameters = [
            RawDataRoot = "data/raw",
            ExtractRoot = "data/extracts"
        ],
        Naming = [
            ParameterPrefix = "p_",
            FunctionPrefix = "fn_",
            StagingPrefix = "stg_",
            DimensionPrefix = "dim_",
            FactPrefix = "fact_",
            BridgePrefix = "bridge_",
            LookupPrefix = "ref_"
        ],
        SharedDimensions = [
            Date = [
                CanonicalName = "Date",
                SourceTables = {"tbl_Calendar", "tbl_WF_Calendar"},
                Grain = "One row per date",
                RequiredKey = "Date",
                RequiredAttributes = {"Calendar Year", "Calendar Month", "Calendar Month Name", "Quarter", "Financial Year", "Period", "Period Start", "Period End"}
            ],
            CostCentre = [
                CanonicalName = "Cost Centre",
                SourceTables = {"GL transactions", "payroll/FTE pass-through", "lookup tables"},
                Grain = "One row per cost centre",
                RequiredKey = "Cost Centre Code",
                RequiredAttributes = {"Cost Centre Code", "Cost Centre Name"}
            ],
            Account = [
                CanonicalName = "Account",
                SourceTables = {"ca_MVRPT_ACCOUNT", "GL transactions", "VMO source data"},
                Grain = "One row per account code",
                RequiredKey = "Account Code",
                RequiredAttributes = {"Account Code", "Account Name", "Account Group", "Status"}
            ],
            MedicalStaff = [
                CanonicalName = "Medical Staff",
                SourceTables = {"tbl_Medical_Staff_Data", "tbl_Medical_Staff_History", "qry_Combo_Medical_Payroll_Data"},
                Grain = "One row per staff ID",
                RequiredKey = "Staff ID",
                RequiredAttributes = {"Staff ID", "Staff Status", "Department", "Grade"}
            ]
        ],
        ImplementationTables = [
            VMOFinance = {
                [ModelTable = "Date", SourceObject = "dbo.tbl_Calendar", Role = "dimension", Grain = "One row per date", DateTableColumn = "Date"],
                [ModelTable = "GL Transactions", SourceObject = "dbo.tbl_GL_Transactions", Role = "fact", Grain = "One row per GL posting line"],
                [ModelTable = "VMO Data", SourceObject = "dbo.tbl_VMO_Data", Role = "fact", Grain = "One row per VMO source record"],
                [ModelTable = "VMO GL Transactions", SourceObject = "dbo.tbl_VMO_GL_Transactions", Role = "bridge/fact", Grain = "One row per mapped GL/VMO transaction"],
                [ModelTable = "VMO GL Classification", SourceObject = "dbo.tbl_VMO_GL_Classification", Role = "lookup", Grain = "One row per classification rule/key"],
                [ModelTable = "Reconciliation GL Data", SourceObject = "dbo.tbl_Reconciliation_GL_Data", Role = "fact", Grain = "One row per GL-side reconciliation row"],
                [ModelTable = "Reconciliation VMO Data", SourceObject = "dbo.tbl_Reconciliation_VMO_Data", Role = "fact", Grain = "One row per VMO-side reconciliation row"],
                [ModelTable = "Account", SourceObject = "dbo.ca_MVRPT_ACCOUNT", Role = "dimension", Grain = "One row per account code"],
                [ModelTable = "Cost Centre", SourceObject = "dbo.ca_MVRPT_COSTCENTRES", Role = "dimension", Grain = "One row per cost-centre code"]
            },
            MedicalStaff = {
                [ModelTable = "Workforce Calendar", SourceObject = "dbo.tbl_WF_Calendar", Role = "dimension", Grain = "One row per date or reporting period", DateTableColumn = "Date"],
                [ModelTable = "Medical Staff Data", SourceObject = "dbo.tbl_Medical_Staff_Data", Role = "fact", Grain = "One row per staff record or staff-period row"],
                [ModelTable = "Medical Staff History", SourceObject = "dbo.tbl_Medical_Staff_History", Role = "history fact", Grain = "One row per staff history event/version"],
                [ModelTable = "Medical Payroll Data", SourceObject = "dbo.qry_Combo_Medical_Payroll_Data", Role = "fact", Grain = "One row per staff/pay-period/pay-component row"],
                [ModelTable = "Medical Staff", SourceObject = "derived", Role = "dimension", Grain = "One row per staff ID"],
                [ModelTable = "Department", SourceObject = "derived", Role = "dimension", Grain = "One row per department/cost-centre"]
            }
        ],
        ImplementationRelationships = [
            VMOFinance = {
                [From = "GL Transactions[Date]", To = "Date[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "VMO Data[Date]", To = "Date[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "VMO GL Transactions[Date]", To = "Date[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Reconciliation GL Data[Date]", To = "Date[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Reconciliation VMO Data[Date]", To = "Date[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "GL Transactions[Account Code]", To = "Account[Account Code]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "VMO Data[Account Code]", To = "Account[Account Code]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "GL Transactions[Cost Centre Code]", To = "Cost Centre[Cost Centre Code]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "VMO Data[Cost Centre Code]", To = "Cost Centre[Cost Centre Code]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "VMO GL Transactions[GL Transaction ID]", To = "GL Transactions[GL Transaction ID]", Cardinality = "many-to-one", Active = false, Direction = "single"],
                [From = "VMO GL Transactions[VMO Record ID]", To = "VMO Data[VMO Record ID]", Cardinality = "many-to-one", Active = false, Direction = "single"]
            },
            MedicalStaff = {
                [From = "Medical Staff Data[Date]", To = "Workforce Calendar[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Medical Staff History[Effective Date]", To = "Workforce Calendar[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Medical Staff History[End Date]", To = "Workforce Calendar[Date]", Cardinality = "many-to-one", Active = false, Direction = "single"],
                [From = "Medical Payroll Data[Date]", To = "Workforce Calendar[Date]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Medical Staff Data[Staff ID]", To = "Medical Staff[Staff ID]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Medical Staff History[Staff ID]", To = "Medical Staff[Staff ID]", Cardinality = "many-to-one", Active = true, Direction = "single"],
                [From = "Medical Payroll Data[Staff ID]", To = "Medical Staff[Staff ID]", Cardinality = "many-to-one", Active = true, Direction = "single"]
            }
        ],
        SourceTables = [
            VMO = {
                [Name = "tbl_Calendar", Role = "date calendar", Classification = "shared-dimension candidate"],
                [Name = "tbl_GL_Transactions", Role = "fact", Classification = "GL fact"],
                [Name = "tbl_Reconciliation_GL_Data", Role = "fact", Classification = "reconciliation fact"],
                [Name = "tbl_Reconciliation_VMO_Data", Role = "fact", Classification = "reconciliation fact"],
                [Name = "tbl_VMO_Data", Role = "fact", Classification = "VMO activity fact"],
                [Name = "tbl_VMO_GL_Classification", Role = "lookup/bridge", Classification = "classification map"],
                [Name = "tbl_VMO_GL_Transactions", Role = "fact/bridge", Classification = "transaction bridge"]
            ],
            MedicalStaff = {
                [Name = "tbl_WF_Calendar", Role = "date calendar", Classification = "shared-dimension candidate"],
                [Name = "tbl_Medical_Staff_Data", Role = "fact", Classification = "staff fact"],
                [Name = "tbl_Medical_Staff_History", Role = "fact/history", Classification = "history fact"]
            }
        ],
        MergePath = [
            Step1 = "Keep the standalone VMO and Medical Staff models separate.",
            Step2 = "Reuse this contract in both models for source-normalisation and naming.",
            Step3 = "Promote the shared Date and Cost Centre tables into `src/powerbi/shared/`.",
            Step4 = "Promote common measures only after both models agree on the same semantics.",
            Step5 = "Move to a shared semantic model only once independent refresh and shared definitions are stable."
        ],
        Helpers = [
            NormalizeTextKey = NormalizeTextKey,
            NormalizeDate = NormalizeDate,
            NormalizeCostCentreCode = NormalizeCostCentreCode,
            NormalizeStaffId = NormalizeStaffId
        ]
    ]
in
    SharedFinanceContracts
