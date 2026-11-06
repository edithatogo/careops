param(
    [string]$ReportPath = (Join-Path $PSScriptRoot 'pbir/MedicalStaff'),
    [string]$DatasetPath = '../Dataset',
    [switch]$SkipLocalProofBindings
)

$ErrorActionPreference = 'Stop'

$pbi = Get-Command pbi -ErrorAction Stop
$reportParent = Split-Path -Parent $ReportPath
if (-not (Test-Path -LiteralPath $reportParent)) {
    New-Item -ItemType Directory -Path $reportParent | Out-Null
}

if (-not (Test-Path -LiteralPath (Join-Path $ReportPath 'definition.pbir'))) {
    & $pbi.Source report create $ReportPath --name 'Medical Staff' --dataset-path $DatasetPath
}

function Invoke-Pbi {
    param([string[]]$Arguments)
    & $pbi.Source @Arguments
}

$reportArgs = @('report', '--path', $ReportPath, '--no-sync')
$visualArgs = @('visual', '--path', $ReportPath, '--no-sync')

Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Medical Staff Overview', '--name', 'medical_staff_overview', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Staff History', '--name', 'staff_history', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Source Dependencies and Validation', '--name', 'source_validation', '--width', '1280', '--height', '720'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'card', '--name', 'card_staff_count', '--x', '24', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_staff_count', '--page', 'medical_staff_overview', '--field', 'FactMedicalStaffCurrent[Medical Staff Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'card', '--name', 'card_active_staff', '--x', '256', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_active_staff', '--page', 'medical_staff_overview', '--field', 'FactMedicalStaffCurrent[Active Staff Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'card', '--name', 'card_fte', '--x', '488', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_fte', '--page', 'medical_staff_overview', '--field', 'FactMedicalStaffCurrent[Medical Staff FTE]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'card', '--name', 'card_payroll', '--x', '720', '--y', '24', '--width', '240', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_payroll', '--page', 'medical_staff_overview', '--field', 'FactMedicalPayroll[Medical Payroll Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'line', '--name', 'line_headcount_fte', '--x', '24', '--y', '140', '--width', '624', '--height', '280'))
Invoke-Pbi ($visualArgs + @('bind', 'line_headcount_fte', '--page', 'medical_staff_overview', '--category', 'DimWorkforceCalendar[Date]', '--value', 'FactMedicalStaffCurrent[Medical Staff Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'column', '--name', 'column_payroll_period', '--x', '672', '--y', '140', '--width', '584', '--height', '280'))
Invoke-Pbi ($visualArgs + @('bind', 'column_payroll_period', '--page', 'medical_staff_overview', '--category', 'DimWorkforceCalendar[Period]', '--value', 'FactMedicalPayroll[Medical Payroll Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'matrix', '--name', 'matrix_department_grade', '--x', '24', '--y', '444', '--width', '760', '--height', '232'))
Invoke-Pbi ($visualArgs + @('bind', 'matrix_department_grade', '--page', 'medical_staff_overview', '--row', 'FactMedicalStaffCurrent[Department]', '--value', 'FactMedicalStaffCurrent[Medical Staff FTE]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'slicer', '--name', 'slicer_period', '--x', '808', '--y', '444', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_period', '--page', 'medical_staff_overview', '--field', 'DimWorkforceCalendar[Period]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'slicer', '--name', 'slicer_record_state', '--x', '1040', '--y', '444', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_record_state', '--page', 'medical_staff_overview', '--field', 'FactMedicalStaffCurrent[RecordState]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'medical_staff_overview', '--type', 'slicer', '--name', 'slicer_staff_status', '--x', '808', '--y', '560', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_staff_status', '--page', 'medical_staff_overview', '--field', 'FactMedicalStaffCurrent[StaffStatus]'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'card', '--name', 'card_history_rows', '--x', '24', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_history_rows', '--page', 'staff_history', '--field', 'FactMedicalStaffHistory[History Row Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'card', '--name', 'card_current_records', '--x', '256', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_current_records', '--page', 'staff_history', '--field', 'FactMedicalStaffHistory[Current Record Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'card', '--name', 'card_historical_records', '--x', '488', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_historical_records', '--page', 'staff_history', '--field', 'FactMedicalStaffHistory[Historical Record Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'card', '--name', 'card_history_coverage', '--x', '720', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_history_coverage', '--page', 'staff_history', '--field', 'FactMedicalStaffHistory[History Coverage %]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'slicer', '--name', 'slicer_staff_id', '--x', '960', '--y', '24', '--width', '296', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_staff_id', '--page', 'staff_history', '--field', 'FactMedicalStaffCurrent[StaffID]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'line', '--name', 'line_history_volume', '--x', '24', '--y', '144', '--width', '600', '--height', '260'))
Invoke-Pbi ($visualArgs + @('bind', 'line_history_volume', '--page', 'staff_history', '--category', 'DimWorkforceCalendar[Date]', '--value', 'FactMedicalStaffHistory[History Row Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'bar', '--name', 'bar_history_exceptions', '--x', '656', '--y', '144', '--width', '600', '--height', '260'))
Invoke-Pbi ($visualArgs + @('bind', 'bar_history_exceptions', '--page', 'staff_history', '--category', 'FactMedicalStaffHistory[EventType]', '--value', 'FactMedicalStaffHistory[Duplicate Staff Record Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'staff_history', '--type', 'table', '--name', 'table_staff_history_detail', '--x', '24', '--y', '432', '--width', '1232', '--height', '244'))
Invoke-Pbi ($visualArgs + @('bind', 'table_staff_history_detail', '--page', 'staff_history', '--value', 'FactMedicalStaffCurrent[StaffID]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_staff_history_detail', '--page', 'staff_history', '--value', 'FactMedicalStaffHistory[EffectiveDate]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_staff_history_detail', '--page', 'staff_history', '--value', 'FactMedicalStaffHistory[RecordState]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_staff_history_detail', '--page', 'staff_history', '--value', 'FactMedicalStaffHistory[EventType]'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'card', '--name', 'card_source_objects', '--x', '24', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_source_objects', '--page', 'source_validation', '--field', 'Source Inventory[Source Object Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'card', '--name', 'card_missing_sources', '--x', '256', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_missing_sources', '--page', 'source_validation', '--field', 'Source Inventory[Missing Source Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'card', '--name', 'card_validation_pass', '--x', '488', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_validation_pass', '--page', 'source_validation', '--field', 'Validation Checks[Validation Pass Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'card', '--name', 'card_validation_fail', '--x', '720', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_validation_fail', '--page', 'source_validation', '--field', 'Validation Checks[Validation Fail Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'matrix', '--name', 'matrix_source_status', '--x', '24', '--y', '144', '--width', '560', '--height', '360'))
Invoke-Pbi ($visualArgs + @('bind', 'matrix_source_status', '--page', 'source_validation', '--row', 'Source Inventory[SourceClass]', '--value', 'Source Inventory[Source Object Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'table', '--name', 'table_dependency_gaps', '--x', '608', '--y', '144', '--width', '648', '--height', '360'))
Invoke-Pbi ($visualArgs + @('bind', 'table_dependency_gaps', '--page', 'source_validation', '--value', 'Source Inventory[ObjectName]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_dependency_gaps', '--page', 'source_validation', '--value', 'Source Inventory[ObjectType]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_dependency_gaps', '--page', 'source_validation', '--value', 'Source Inventory[LoadStatus]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'table', '--name', 'table_validation_checks', '--x', '24', '--y', '532', '--width', '760', '--height', '144'))
Invoke-Pbi ($visualArgs + @('bind', 'table_validation_checks', '--page', 'source_validation', '--value', 'Validation Checks[CheckName]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_validation_checks', '--page', 'source_validation', '--value', 'Validation Checks[Result]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'slicer', '--name', 'slicer_load_status', '--x', '808', '--y', '532', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_load_status', '--page', 'source_validation', '--field', 'Source Inventory[LoadStatus]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'source_validation', '--type', 'slicer', '--name', 'slicer_object_type', '--x', '1040', '--y', '532', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_object_type', '--page', 'source_validation', '--field', 'Source Inventory[ObjectType]'))

if (-not $SkipLocalProofBindings) {
    $repoRoot = (& git -C $PSScriptRoot rev-parse --show-toplevel 2>$null)
    $localProofBindingScript = Join-Path $repoRoot 'scripts/Set-PbirLocalProofBindings.ps1'
    if (Test-Path -LiteralPath $localProofBindingScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $localProofBindingScript -ReportPaths @($ReportPath)
    }
    $embeddedSampleDataScript = Join-Path $repoRoot 'scripts/Set-PbirEmbeddedSampleData.ps1'
    if (Test-Path -LiteralPath $embeddedSampleDataScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $embeddedSampleDataScript -ReportRoots @((Join-Path $ReportPath 'Medical Staff.Report')) -TableRoots @((Join-Path $ReportPath 'Dataset/definition/tables'))
    }
}

& $pbi.Source report --path $ReportPath validate
