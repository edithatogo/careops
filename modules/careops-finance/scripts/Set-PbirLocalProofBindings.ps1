param(
    [string[]]$ReportPaths = @(
        "src/powerbi/dashboards/vmo-finance/report/pbir/VmoFinance/VMO Finance.Report",
        "src/powerbi/dashboards/medical-staff/report/pbir/MedicalStaff/Medical Staff.Report"
    )
)

$ErrorActionPreference = 'Stop'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

$fieldMap = @{
    'DimWorkforceCalendar.Date' = @{ Table = 'Workforce Calendar'; Field = 'Fortnight'; Kind = 'Column' }
    'DimWorkforceCalendar.Period' = @{ Table = 'Workforce Calendar'; Field = 'Fortnight'; Kind = 'Column' }
    'FactMedicalPayroll.Medical Payroll Amount' = @{ Table = 'Medical Staff Data'; Field = 'Medical Payroll Amount'; Kind = 'Measure' }
    'FactMedicalStaffCurrent.Active Staff Count' = @{ Table = 'Medical Staff Data'; Field = 'Medical Staff Count'; Kind = 'Measure' }
    'FactMedicalStaffCurrent.Department' = @{ Table = 'Medical Staff Data'; Field = 'COST_CODE'; Kind = 'Column' }
    'FactMedicalStaffCurrent.Grade' = @{ Table = 'Medical Staff Data'; Field = 'PAY_CLASS'; Kind = 'Column' }
    'FactMedicalStaffCurrent.Medical Staff Count' = @{ Table = 'Medical Staff Data'; Field = 'Medical Staff Count'; Kind = 'Measure' }
    'FactMedicalStaffCurrent.Medical Staff FTE' = @{ Table = 'Medical Staff Data'; Field = 'Medical Staff FTE'; Kind = 'Measure' }
    'FactMedicalStaffCurrent.RecordState' = @{ Table = 'Medical Staff Data'; Field = 'PAY_CLASS'; Kind = 'Column' }
    'FactMedicalStaffCurrent.StaffID' = @{ Table = 'Medical Staff Data'; Field = 'EMPLOYEE_NUMBER'; Kind = 'Column' }
    'FactMedicalStaffCurrent.StaffStatus' = @{ Table = 'Medical Staff Data'; Field = 'PAY_CLASS'; Kind = 'Column' }
    'FactMedicalStaffHistory.Current Record Count' = @{ Table = 'Medical Staff History'; Field = 'Medical History Row Count'; Kind = 'Measure' }
    'FactMedicalStaffHistory.Duplicate Staff Record Count' = @{ Table = 'Medical Staff History'; Field = 'Medical History Row Count'; Kind = 'Measure' }
    'FactMedicalStaffHistory.EffectiveDate' = @{ Table = 'Medical Staff History'; Field = 'PAY_PERIOD_NUMBER'; Kind = 'Column' }
    'FactMedicalStaffHistory.EventType' = @{ Table = 'Medical Staff History'; Field = 'PAY_CLASS'; Kind = 'Column' }
    'FactMedicalStaffHistory.Historical Record Count' = @{ Table = 'Medical Staff History'; Field = 'Medical History Row Count'; Kind = 'Measure' }
    'FactMedicalStaffHistory.History Coverage %' = @{ Table = 'Medical Staff History'; Field = 'Medical History Row Count'; Kind = 'Measure' }
    'FactMedicalStaffHistory.History Row Count' = @{ Table = 'Medical Staff History'; Field = 'Medical History Row Count'; Kind = 'Measure' }
    'FactMedicalStaffHistory.RecordState' = @{ Table = 'Medical Staff History'; Field = 'EMPLOYEE_NUMBER'; Kind = 'Column' }
    'Source Inventory.LoadStatus' = @{ Table = 'VMO GL Transactions'; Field = 'JOURNAL_SOURCE'; Kind = 'Column' }
    'Source Inventory.Missing Source Count' = @{ Table = 'VMO GL Transactions'; Field = 'GL Transaction Count'; Kind = 'Measure' }
    'Source Inventory.ObjectName' = @{ Table = 'VMO Data'; Field = 'Cost Centre'; Kind = 'Column' }
    'Source Inventory.ObjectType' = @{ Table = 'VMO GL Classification'; Field = 'VMO_GL_Classification'; Kind = 'Column' }
    'Source Inventory.Source Object Count' = @{ Table = 'VMO Data'; Field = 'VMO Record Count'; Kind = 'Measure' }
    'Source Inventory.SourceClass' = @{ Table = 'VMO GL Classification'; Field = 'VMO_GL_Classification'; Kind = 'Column' }
    'Validation Checks.CheckName' = @{ Table = 'VMO GL Classification'; Field = 'VMO_GL_Classification'; Kind = 'Column' }
    'Validation Checks.Result' = @{ Table = 'VMO GL Transactions'; Field = 'JOURNAL_SOURCE'; Kind = 'Column' }
    'Validation Checks.Validation Fail Count' = @{ Table = 'VMO GL Transactions'; Field = 'GL Transaction Count'; Kind = 'Measure' }
    'Validation Checks.Validation Pass Count' = @{ Table = 'VMO Data'; Field = 'VMO Record Count'; Kind = 'Measure' }
    'qry_Reconciliation_GL_Summary_Other_Subsystems.Other Subsystems Variance' = @{ Table = 'VMO Data'; Field = 'VMO Variance Amount'; Kind = 'Measure' }
    'tbl_Calendar.Financial Year' = @{ Table = 'VMO GL Transactions'; Field = 'FIN_YEAR'; Kind = 'Column' }
    'tbl_Calendar.Period' = @{ Table = 'VMO GL Transactions'; Field = 'FIN_MONTH'; Kind = 'Column' }
    'tbl_GL_Transactions.Account' = @{ Table = 'VMO GL Transactions'; Field = 'ACCOUNT_CODE'; Kind = 'Column' }
    'tbl_GL_Transactions.Cost Centre' = @{ Table = 'VMO GL Transactions'; Field = 'COST_CENTRE_CODE'; Kind = 'Column' }
    'tbl_GL_Transactions.GL Row Count' = @{ Table = 'VMO GL Transactions'; Field = 'GL Transaction Count'; Kind = 'Measure' }
    'tbl_GL_Transactions.Posting Date' = @{ Table = 'VMO GL Transactions'; Field = 'FIN_MONTH'; Kind = 'Column' }
    'tbl_GL_Transactions.Source Transaction ID' = @{ Table = 'VMO GL Transactions'; Field = 'JOURNAL_SOURCE'; Kind = 'Column' }
    'tbl_GL_Transactions.Total GL Amount' = @{ Table = 'VMO GL Transactions'; Field = 'Total GL Amount'; Kind = 'Measure' }
    'tbl_GL_Transactions.Transaction Type' = @{ Table = 'VMO GL Transactions'; Field = 'JOURNAL_SOURCE'; Kind = 'Column' }
    'tbl_Reconciliation_GL_Data.Classification' = @{ Table = 'VMO GL Classification'; Field = 'VMO_GL_Classification'; Kind = 'Column' }
    'tbl_Reconciliation_GL_Data.Exception Flag' = @{ Table = 'VMO GL Classification'; Field = 'VMO_GL_Classification'; Kind = 'Column' }
    'tbl_Reconciliation_GL_Data.Exception Rows' = @{ Table = 'VMO GL Transactions'; Field = 'GL Transaction Count'; Kind = 'Measure' }
    'tbl_Reconciliation_GL_Data.Match Status' = @{ Table = 'VMO GL Transactions'; Field = 'JOURNAL_SOURCE'; Kind = 'Column' }
    'tbl_Reconciliation_GL_Data.Matched Rows' = @{ Table = 'VMO GL Transactions'; Field = 'GL Transaction Count'; Kind = 'Measure' }
    'tbl_Reconciliation_GL_Data.Subsystem' = @{ Table = 'VMO GL Transactions'; Field = 'JOURNAL_SOURCE'; Kind = 'Column' }
    'tbl_Reconciliation_GL_Data.Unmatched GL Rows' = @{ Table = 'VMO GL Transactions'; Field = 'GL Transaction Count'; Kind = 'Measure' }
    'tbl_Reconciliation_GL_Data.Variance Amount' = @{ Table = 'VMO Data'; Field = 'VMO Variance Amount'; Kind = 'Measure' }
    'tbl_Reconciliation_VMO_Data.Unmatched VMO Rows' = @{ Table = 'VMO Data'; Field = 'VMO Record Count'; Kind = 'Measure' }
    'tbl_VMO_Data.Total VMO Amount' = @{ Table = 'VMO Data'; Field = 'Total VMO Amount'; Kind = 'Measure' }
    'tbl_VMO_GL_Classification.Classification' = @{ Table = 'VMO GL Classification'; Field = 'VMO_GL_Classification'; Kind = 'Column' }
    'tbl_VMO_GL_Transactions.Reconciliation Variance' = @{ Table = 'VMO Data'; Field = 'VMO Variance Amount'; Kind = 'Measure' }
    'tbl_VMO_GL_Transactions.Reconciliation Variance %' = @{ Table = 'VMO Data'; Field = 'VMO Variance Amount'; Kind = 'Measure' }
}

function New-FieldReference {
    param(
        [hashtable]$Target
    )

    $sourceRef = [ordered]@{
        Entity = $Target.Table
    }

    $fieldBody = [ordered]@{
        Expression = [ordered]@{
            SourceRef = $sourceRef
        }
        Property = $Target.Field
    }

    if ($Target.Kind -eq 'Measure') {
        return [pscustomobject]([ordered]@{ Measure = [pscustomobject]$fieldBody })
    }

    return [pscustomobject]([ordered]@{ Column = [pscustomobject]$fieldBody })
}

function Get-FieldKey {
    param($Field)

    foreach ($kind in @('Measure', 'Column')) {
        if ($null -ne $Field.$kind) {
            $entity = $Field.$kind.Expression.SourceRef.Entity
            $property = $Field.$kind.Property
            if (-not [string]::IsNullOrWhiteSpace($entity) -and -not [string]::IsNullOrWhiteSpace($property)) {
                return "$entity.$property"
            }
        }
    }

    return $null
}

function Update-Node {
    param($Node)

    if ($null -eq $Node) {
        return
    }

    if ($Node -is [System.Array]) {
        foreach ($item in $Node) {
            Update-Node $item
        }
        return
    }

    if ($Node -isnot [pscustomobject]) {
        return
    }

    if ($null -ne $Node.field) {
        $key = Get-FieldKey $Node.field
        if ($null -ne $key -and $fieldMap.ContainsKey($key)) {
            $target = $fieldMap[$key]
            $Node.field = New-FieldReference -Target $target
            if ($Node.PSObject.Properties.Name -contains 'queryRef') {
                $Node.queryRef = "$($target.Table).$($target.Field)"
            }
            if ($Node.PSObject.Properties.Name -contains 'nativeQueryRef') {
                $Node.nativeQueryRef = $target.Field
            }
        }
    }

    foreach ($property in $Node.PSObject.Properties) {
        Update-Node $property.Value
    }
}

function Remove-StaleTopNFilterConfig {
    param($Node)

    if ($null -eq $Node) {
        return
    }

    if ($Node -is [System.Array]) {
        foreach ($item in $Node) {
            Remove-StaleTopNFilterConfig $item
        }
        return
    }

    if ($Node -isnot [pscustomobject]) {
        return
    }

    if ($Node.PSObject.Properties.Name -contains 'filterConfig') {
        $filterJson = $Node.filterConfig | ConvertTo-Json -Depth 100
        if ($filterJson -match 'tbl_GL_Transactions|tbl_Reconciliation_GL_Data|tbl_Reconciliation_VMO_Data') {
            $Node.PSObject.Properties.Remove('filterConfig')
        }
    }

    foreach ($property in $Node.PSObject.Properties) {
        Remove-StaleTopNFilterConfig $property.Value
    }
}

$changedFiles = 0
foreach ($reportPath in $ReportPaths) {
    if (-not (Test-Path -LiteralPath $reportPath -PathType Container)) {
        throw "Report path not found: $reportPath"
    }

    Get-ChildItem -LiteralPath $reportPath -Recurse -Filter *.json | ForEach-Object {
        $path = $_.FullName
        $before = Get-Content -LiteralPath $path -Raw
        $json = $before | ConvertFrom-Json
        Update-Node $json
        Remove-StaleTopNFilterConfig $json
        $after = $json | ConvertTo-Json -Depth 100
        if ($after -ne $before) {
            [System.IO.File]::WriteAllText($path, $after, $utf8NoBom)
            $changedFiles++
        }
    }
}

Write-Host "Local proof PBIR binding pass complete. Changed files: $changedFiles"
