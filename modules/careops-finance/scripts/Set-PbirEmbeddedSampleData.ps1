param(
    [string[]]$TableRoots = @(
        "src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance/Dataset/definition/tables",
        "src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff/Dataset/definition/tables",
        "src/powerbi/dashboards/vmo-finance/model-tmdl/live-export/tables",
        "src/powerbi/dashboards/medical-staff/model-tmdl/live-export/tables"
    ),

    [string[]]$ReportRoots = @(
        "src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance/VMO Finance.Report",
        "src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff/Medical Staff.Report"
    )
)

$ErrorActionPreference = 'Stop'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$sampleSources = @{
    'Medical Staff Data' = 'let Source = Table.FromRecords({[EMPLOYEE_NUMBER="MS001", EMPLOYEE_COST_CODE="CC100", COST_CODE="Emergency", FY="2025-26", PAY_PERIOD_NUMBER=1, FTE=1.0, PAY_AMOUNT=12500.00, PAY_CLASS="Active"], [EMPLOYEE_NUMBER="MS002", EMPLOYEE_COST_CODE="CC200", COST_CODE="Surgery", FY="2025-26", PAY_PERIOD_NUMBER=1, FTE=0.8, PAY_AMOUNT=9800.00, PAY_CLASS="Active"], [EMPLOYEE_NUMBER="MS003", EMPLOYEE_COST_CODE="CC300", COST_CODE="Medicine", FY="2025-26", PAY_PERIOD_NUMBER=2, FTE=0.6, PAY_AMOUNT=7200.00, PAY_CLASS="Sessional"]}), Typed = Table.TransformColumnTypes(Source, {{"EMPLOYEE_NUMBER", type text}, {"EMPLOYEE_COST_CODE", type text}, {"COST_CODE", type text}, {"FY", type text}, {"PAY_PERIOD_NUMBER", Int64.Type}, {"FTE", type number}, {"PAY_AMOUNT", type number}, {"PAY_CLASS", type text}}) in Typed'
    'Medical Staff History' = 'let Source = Table.FromRecords({[EMPLOYEE_NUMBER="MS001", EMPLOYEE_COST_CODE="CC100", COST_CODE="Emergency", FY="2025-26", PAY_PERIOD_NUMBER=1, FTE=1.0, PAY_AMOUNT=12500.00], [EMPLOYEE_NUMBER="MS001", EMPLOYEE_COST_CODE="CC100", COST_CODE="Emergency", FY="2025-26", PAY_PERIOD_NUMBER=2, FTE=1.0, PAY_AMOUNT=12650.00], [EMPLOYEE_NUMBER="MS002", EMPLOYEE_COST_CODE="CC200", COST_CODE="Surgery", FY="2025-26", PAY_PERIOD_NUMBER=2, FTE=0.8, PAY_AMOUNT=9900.00]}), Typed = Table.TransformColumnTypes(Source, {{"EMPLOYEE_NUMBER", type text}, {"EMPLOYEE_COST_CODE", type text}, {"COST_CODE", type text}, {"FY", type text}, {"PAY_PERIOD_NUMBER", Int64.Type}, {"FTE", type number}, {"PAY_AMOUNT", type number}}) in Typed'
    'VMO Calendar' = 'let Source = Table.FromRecords({[FIN_YEAR="2025-26", FIN_MONTH="Jul"], [FIN_YEAR="2025-26", FIN_MONTH="Aug"], [FIN_YEAR="2025-26", FIN_MONTH="Sep"]}) in Source'
    'VMO Data' = 'let Source = Table.FromRecords({[#"Period Processed"="2025-26", #"Cost Centre"="CC100", #"Unique VMO Id"="VMO001", #"VMO Surname"="Nguyen", #"VMO Total Amount Paid(Excl GST)"=42000.00, #"SES Total Amount Paid"=12000.00, #"FEE Total Amount Paid"=25000.00, #"RUR Total Amount Paid"=5000.00], [#"Period Processed"="2025-26", #"Cost Centre"="CC200", #"Unique VMO Id"="VMO002", #"VMO Surname"="Patel", #"VMO Total Amount Paid(Excl GST)"=36500.00, #"SES Total Amount Paid"=9500.00, #"FEE Total Amount Paid"=22000.00, #"RUR Total Amount Paid"=5000.00], [#"Period Processed"="2025-26", #"Cost Centre"="CC300", #"Unique VMO Id"="VMO003", #"VMO Surname"="Smith", #"VMO Total Amount Paid(Excl GST)"=28500.00, #"SES Total Amount Paid"=8500.00, #"FEE Total Amount Paid"=17000.00, #"RUR Total Amount Paid"=3000.00]}), Typed = Table.TransformColumnTypes(Source, {{"Period Processed", type text}, {"Cost Centre", type text}, {"Unique VMO Id", type text}, {"VMO Surname", type text}, {"VMO Total Amount Paid(Excl GST)", type number}, {"SES Total Amount Paid", type number}, {"FEE Total Amount Paid", type number}, {"RUR Total Amount Paid", type number}}) in Typed'
    'VMO GL Bridge' = 'let Source = Table.FromRecords({[FIN_YEAR="2025-26", FIN_MONTH="Jul", COST_CENTRE="CC100", ACCOUNT="6001", TRN_AMOUNT_1=41000.00], [FIN_YEAR="2025-26", FIN_MONTH="Aug", COST_CENTRE="CC200", ACCOUNT="6002", TRN_AMOUNT_1=37000.00], [FIN_YEAR="2025-26", FIN_MONTH="Sep", COST_CENTRE="CC300", ACCOUNT="6003", TRN_AMOUNT_1=29000.00]}), Typed = Table.TransformColumnTypes(Source, {{"FIN_YEAR", type text}, {"FIN_MONTH", type text}, {"COST_CENTRE", type text}, {"ACCOUNT", type text}, {"TRN_AMOUNT_1", type number}}) in Typed'
    'VMO GL Classification' = 'let Source = Table.FromRecords({[Account_Code="6001", VMO_GL_Classification="VMO Fees"], [Account_Code="6002", VMO_GL_Classification="Sessional"], [Account_Code="6003", VMO_GL_Classification="Rural"]}), Typed = Table.TransformColumnTypes(Source, {{"Account_Code", type text}, {"VMO_GL_Classification", type text}}) in Typed'
    'VMO GL Transactions' = 'let Source = Table.FromRecords({[FIN_YEAR="2025-26", FIN_MONTH="Jul", ACCOUNT_CODE="6001", COST_CENTRE_CODE="CC100", AMOUNT=41000.00, JOURNAL_SOURCE="GL"], [FIN_YEAR="2025-26", FIN_MONTH="Aug", ACCOUNT_CODE="6002", COST_CENTRE_CODE="CC200", AMOUNT=37000.00, JOURNAL_SOURCE="GL"], [FIN_YEAR="2025-26", FIN_MONTH="Sep", ACCOUNT_CODE="6003", COST_CENTRE_CODE="CC300", AMOUNT=29000.00, JOURNAL_SOURCE="Manual"]}), Typed = Table.TransformColumnTypes(Source, {{"FIN_YEAR", type text}, {"FIN_MONTH", type text}, {"ACCOUNT_CODE", type text}, {"COST_CENTRE_CODE", type text}, {"AMOUNT", type number}, {"JOURNAL_SOURCE", type text}}) in Typed'
    'VMO Reconciliation GL' = 'let Source = Table.FromRecords({[Subsystem="GL", MatchStatus="Matched", VarianceAmount=1000.00], [Subsystem="GL", MatchStatus="Review", VarianceAmount=-500.00]}) in Source'
    'VMO Reconciliation VMO' = 'let Source = Table.FromRecords({[Subsystem="VMO", MatchStatus="Matched", VarianceAmount=1000.00], [Subsystem="VMO", MatchStatus="Review", VarianceAmount=-500.00]}) in Source'
    'Workforce Calendar' = 'let Source = Table.FromRecords({[Financial_Year=2026, Fortnight="2026-FN01", Month=7], [Financial_Year=2026, Fortnight="2026-FN02", Month=8], [Financial_Year=2026, Fortnight="2026-FN03", Month=9]}), Typed = Table.TransformColumnTypes(Source, {{"Financial_Year", Int64.Type}, {"Fortnight", type text}, {"Month", Int64.Type}}) in Typed'
}

function Get-TableNameFromPath {
    param([string]$Path)
    return [System.IO.Path]::GetFileNameWithoutExtension($Path)
}

$changedTables = 0
foreach ($tableRoot in $TableRoots) {
    if (-not (Test-Path -LiteralPath $tableRoot -PathType Container)) {
        throw "Table root not found: $tableRoot"
    }

    Get-ChildItem -LiteralPath $tableRoot -Filter '*.tmdl' | ForEach-Object {
        $tableName = Get-TableNameFromPath -Path $_.FullName
        if (-not $sampleSources.ContainsKey($tableName)) {
            return
        }

        $before = Get-Content -LiteralPath $_.FullName -Raw
        $replacement = "`t`t" + 'source = ' + $sampleSources[$tableName]
        $after = [regex]::Replace($before, '(?m)^\t\tsource = .+$', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $replacement })
        if ($after -ne $before) {
            [System.IO.File]::WriteAllText($_.FullName, $after, $utf8NoBom)
            $changedTables++
        }
    }
}

$changedVisuals = 0
foreach ($reportRoot in $ReportRoots) {
    if (-not (Test-Path -LiteralPath $reportRoot -PathType Container)) {
        throw "Report root not found: $reportRoot"
    }

    Get-ChildItem -LiteralPath $reportRoot -Recurse -Filter 'visual.json' | ForEach-Object {
        $before = Get-Content -LiteralPath $_.FullName -Raw
        $after = $before -replace '"visualType"\s*:\s*"stackedBarChart"', '"visualType":  "barChart"'
        if ($after -ne $before) {
            [System.IO.File]::WriteAllText($_.FullName, $after, $utf8NoBom)
            $changedVisuals++
        }
    }
}

Write-Host "Embedded sample data pass complete. Changed table files: $changedTables. Changed visual files: $changedVisuals."
