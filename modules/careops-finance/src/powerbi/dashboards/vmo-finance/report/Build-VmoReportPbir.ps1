param(
    [string]$ReportPath = (Join-Path $PSScriptRoot 'pbir/VmoFinance'),
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
    & $pbi.Source report create $ReportPath --name 'VMO Finance' --dataset-path $DatasetPath
}

function Invoke-Pbi {
    param([string[]]$Arguments)
    & $pbi.Source @Arguments
}

$reportArgs = @('report', '--path', $ReportPath, '--no-sync')
$visualArgs = @('visual', '--path', $ReportPath, '--no-sync')
$filterArgs = @('filters', '--path', $ReportPath, '--no-sync')

Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Executive Summary', '--name', 'executive_summary', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Reconciliation Detail', '--name', 'reconciliation_detail', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Classification And Cost Centre', '--name', 'classification_cost_centre', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Exceptions', '--name', 'exceptions', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Transaction Detail', '--name', 'transaction_detail', '--width', '1280', '--height', '720'))
Invoke-Pbi ($reportArgs + @('add-page', '--display-name', 'Validation', '--name', 'validation', '--width', '1280', '--height', '720'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'card', '--name', 'card_total_gl', '--x', '24', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_total_gl', '--page', 'executive_summary', '--field', 'tbl_GL_Transactions[Total GL Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'card', '--name', 'card_total_vmo', '--x', '256', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_total_vmo', '--page', 'executive_summary', '--field', 'tbl_VMO_Data[Total VMO Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'card', '--name', 'card_variance', '--x', '488', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_variance', '--page', 'executive_summary', '--field', 'tbl_VMO_GL_Transactions[Reconciliation Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'card', '--name', 'card_variance_pct', '--x', '720', '--y', '24', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_variance_pct', '--page', 'executive_summary', '--field', 'tbl_VMO_GL_Transactions[Reconciliation Variance %]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'card', '--name', 'card_record_count', '--x', '952', '--y', '24', '--width', '304', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'card_record_count', '--page', 'executive_summary', '--field', 'tbl_GL_Transactions[GL Row Count]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'line', '--name', 'trend_amount_by_period', '--x', '24', '--y', '136', '--width', '736', '--height', '272'))
Invoke-Pbi ($visualArgs + @('bind', 'trend_amount_by_period', '--page', 'executive_summary', '--category', 'tbl_Calendar[Period]', '--value', 'tbl_GL_Transactions[Total GL Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'stacked_bar', '--name', 'bar_reconciliation_status', '--x', '784', '--y', '136', '--width', '472', '--height', '272'))
Invoke-Pbi ($visualArgs + @('bind', 'bar_reconciliation_status', '--page', 'executive_summary', '--category', 'tbl_Reconciliation_GL_Data[Match Status]', '--value', 'tbl_Reconciliation_GL_Data[Matched Rows]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'slicer', '--name', 'slicer_financial_year', '--x', '24', '--y', '432', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_financial_year', '--page', 'executive_summary', '--field', 'tbl_Calendar[Financial Year]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'slicer', '--name', 'slicer_period', '--x', '256', '--y', '432', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_period', '--page', 'executive_summary', '--field', 'tbl_Calendar[Period]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'slicer', '--name', 'slicer_cost_centre', '--x', '488', '--y', '432', '--width', '240', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_cost_centre', '--page', 'executive_summary', '--field', 'tbl_GL_Transactions[Cost Centre]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'slicer', '--name', 'slicer_account', '--x', '744', '--y', '432', '--width', '240', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_account', '--page', 'executive_summary', '--field', 'tbl_GL_Transactions[Account]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'executive_summary', '--type', 'slicer', '--name', 'slicer_classification', '--x', '1000', '--y', '432', '--width', '256', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_classification', '--page', 'executive_summary', '--field', 'tbl_VMO_GL_Classification[Classification]'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'reconciliation_detail', '--type', 'matrix', '--name', 'matrix_reconciliation_bridge', '--x', '24', '--y', '24', '--width', '760', '--height', '396'))
Invoke-Pbi ($visualArgs + @('bind', 'matrix_reconciliation_bridge', '--page', 'reconciliation_detail', '--row', 'tbl_Calendar[Financial Year]', '--value', 'tbl_VMO_GL_Transactions[Reconciliation Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'reconciliation_detail', '--type', 'bar', '--name', 'bar_status_variance', '--x', '808', '--y', '24', '--width', '448', '--height', '260'))
Invoke-Pbi ($visualArgs + @('bind', 'bar_status_variance', '--page', 'reconciliation_detail', '--category', 'tbl_Reconciliation_GL_Data[Match Status]', '--value', 'tbl_VMO_GL_Transactions[Reconciliation Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'reconciliation_detail', '--type', 'table', '--name', 'table_variance_review', '--x', '24', '--y', '444', '--width', '1232', '--height', '232'))
Invoke-Pbi ($visualArgs + @('bind', 'table_variance_review', '--page', 'reconciliation_detail', '--value', 'tbl_Reconciliation_GL_Data[Match Status]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_variance_review', '--page', 'reconciliation_detail', '--value', 'tbl_Reconciliation_GL_Data[Variance Amount]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_variance_review', '--page', 'reconciliation_detail', '--value', 'tbl_Reconciliation_GL_Data[Classification]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'reconciliation_detail', '--type', 'slicer', '--name', 'slicer_recon_status', '--x', '808', '--y', '308', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_recon_status', '--page', 'reconciliation_detail', '--field', 'tbl_Reconciliation_GL_Data[Match Status]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'reconciliation_detail', '--type', 'slicer', '--name', 'slicer_recon_classification', '--x', '1040', '--y', '308', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_recon_classification', '--page', 'reconciliation_detail', '--field', 'tbl_Reconciliation_GL_Data[Classification]'))
Invoke-Pbi ($filterArgs + @('add-topn', '--page', 'reconciliation_detail', '--table', 'tbl_Reconciliation_GL_Data', '--column', 'Match Status', '--n', '10', '--order-by-table', 'tbl_Reconciliation_GL_Data', '--order-by-column', 'Variance Amount', '--visual', 'bar_status_variance'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'classification_cost_centre', '--type', 'matrix', '--name', 'matrix_classification_cost_centre', '--x', '24', '--y', '24', '--width', '760', '--height', '396'))
Invoke-Pbi ($visualArgs + @('bind', 'matrix_classification_cost_centre', '--page', 'classification_cost_centre', '--row', 'tbl_VMO_GL_Classification[Classification]', '--value', 'tbl_VMO_GL_Transactions[Reconciliation Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'classification_cost_centre', '--type', 'bar', '--name', 'bar_cost_centre_variance', '--x', '808', '--y', '24', '--width', '448', '--height', '260'))
Invoke-Pbi ($visualArgs + @('bind', 'bar_cost_centre_variance', '--page', 'classification_cost_centre', '--category', 'tbl_GL_Transactions[Cost Centre]', '--value', 'tbl_VMO_GL_Transactions[Reconciliation Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'classification_cost_centre', '--type', 'table', '--name', 'table_top_cost_centre_exceptions', '--x', '24', '--y', '444', '--width', '1232', '--height', '232'))
Invoke-Pbi ($visualArgs + @('bind', 'table_top_cost_centre_exceptions', '--page', 'classification_cost_centre', '--value', 'tbl_GL_Transactions[Cost Centre]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_top_cost_centre_exceptions', '--page', 'classification_cost_centre', '--value', 'tbl_GL_Transactions[Account]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_top_cost_centre_exceptions', '--page', 'classification_cost_centre', '--value', 'tbl_Reconciliation_GL_Data[Variance Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'classification_cost_centre', '--type', 'slicer', '--name', 'slicer_classification_page', '--x', '808', '--y', '308', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_classification_page', '--page', 'classification_cost_centre', '--field', 'tbl_VMO_GL_Classification[Classification]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'classification_cost_centre', '--type', 'slicer', '--name', 'slicer_account_page', '--x', '1040', '--y', '308', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_account_page', '--page', 'classification_cost_centre', '--field', 'tbl_GL_Transactions[Account]'))
Invoke-Pbi ($filterArgs + @('add-topn', '--page', 'classification_cost_centre', '--table', 'tbl_GL_Transactions', '--column', 'Cost Centre', '--n', '10', '--order-by-table', 'tbl_Reconciliation_GL_Data', '--order-by-column', 'Variance Amount', '--visual', 'bar_cost_centre_variance'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'card', '--name', 'card_unmatched_gl', '--x', '24', '--y', '24', '--width', '240', '--height', '96'))
Invoke-Pbi ($visualArgs + @('bind', 'card_unmatched_gl', '--page', 'exceptions', '--field', 'tbl_Reconciliation_GL_Data[Unmatched GL Rows]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'card', '--name', 'card_unmatched_vmo', '--x', '288', '--y', '24', '--width', '240', '--height', '96'))
Invoke-Pbi ($visualArgs + @('bind', 'card_unmatched_vmo', '--page', 'exceptions', '--field', 'tbl_Reconciliation_VMO_Data[Unmatched VMO Rows]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'card', '--name', 'card_exception_rows', '--x', '552', '--y', '24', '--width', '240', '--height', '96'))
Invoke-Pbi ($visualArgs + @('bind', 'card_exception_rows', '--page', 'exceptions', '--field', 'tbl_Reconciliation_GL_Data[Exception Rows]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'bar', '--name', 'hist_status', '--x', '816', '--y', '24', '--width', '440', '--height', '236'))
Invoke-Pbi ($visualArgs + @('bind', 'hist_status', '--page', 'exceptions', '--category', 'tbl_Reconciliation_GL_Data[Match Status]', '--value', 'tbl_Reconciliation_GL_Data[Exception Rows]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'table', '--name', 'table_exception_detail', '--x', '24', '--y', '288', '--width', '1232', '--height', '388'))
Invoke-Pbi ($visualArgs + @('bind', 'table_exception_detail', '--page', 'exceptions', '--value', 'tbl_Reconciliation_GL_Data[Subsystem]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_exception_detail', '--page', 'exceptions', '--value', 'tbl_Reconciliation_GL_Data[Match Status]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_exception_detail', '--page', 'exceptions', '--value', 'tbl_Reconciliation_GL_Data[Variance Amount]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_exception_detail', '--page', 'exceptions', '--value', 'tbl_GL_Transactions[Source Transaction ID]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'slicer', '--name', 'slicer_exception_flag', '--x', '24', '--y', '144', '--width', '216', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_exception_flag', '--page', 'exceptions', '--field', 'tbl_Reconciliation_GL_Data[Exception Flag]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'exceptions', '--type', 'slicer', '--name', 'slicer_subsystem', '--x', '256', '--y', '144', '--width', '280', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_subsystem', '--page', 'exceptions', '--field', 'tbl_Reconciliation_GL_Data[Subsystem]'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'transaction_detail', '--type', 'table', '--name', 'table_transaction_detail', '--x', '24', '--y', '24', '--width', '1232', '--height', '520'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_GL_Transactions[Source Transaction ID]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_GL_Transactions[Posting Date]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_GL_Transactions[Transaction Type]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_GL_Transactions[Account]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_GL_Transactions[Cost Centre]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_Reconciliation_GL_Data[Classification]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_transaction_detail', '--page', 'transaction_detail', '--value', 'tbl_Reconciliation_GL_Data[Variance Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'transaction_detail', '--type', 'slicer', '--name', 'slicer_transaction_type', '--x', '24', '--y', '568', '--width', '280', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_transaction_type', '--page', 'transaction_detail', '--field', 'tbl_GL_Transactions[Transaction Type]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'transaction_detail', '--type', 'slicer', '--name', 'slicer_transaction_account', '--x', '320', '--y', '568', '--width', '280', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_transaction_account', '--page', 'transaction_detail', '--field', 'tbl_GL_Transactions[Account]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'transaction_detail', '--type', 'slicer', '--name', 'slicer_transaction_cost_centre', '--x', '616', '--y', '568', '--width', '280', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_transaction_cost_centre', '--page', 'transaction_detail', '--field', 'tbl_GL_Transactions[Cost Centre]'))

Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'card', '--name', 'card_gl_tieout', '--x', '24', '--y', '24', '--width', '240', '--height', '96'))
Invoke-Pbi ($visualArgs + @('bind', 'card_gl_tieout', '--page', 'validation', '--field', 'tbl_GL_Transactions[Total GL Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'card', '--name', 'card_vmo_tieout', '--x', '288', '--y', '24', '--width', '240', '--height', '96'))
Invoke-Pbi ($visualArgs + @('bind', 'card_vmo_tieout', '--page', 'validation', '--field', 'tbl_VMO_Data[Total VMO Amount]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'card', '--name', 'card_other_subsystems', '--x', '552', '--y', '24', '--width', '300', '--height', '96'))
Invoke-Pbi ($visualArgs + @('bind', 'card_other_subsystems', '--page', 'validation', '--field', 'qry_Reconciliation_GL_Summary_Other_Subsystems[Other Subsystems Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'table', '--name', 'table_validation_deltas', '--x', '24', '--y', '152', '--width', '760', '--height', '360'))
Invoke-Pbi ($visualArgs + @('bind', 'table_validation_deltas', '--page', 'validation', '--value', 'tbl_Calendar[Financial Year]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_validation_deltas', '--page', 'validation', '--value', 'tbl_Calendar[Period]'))
Invoke-Pbi ($visualArgs + @('bind', 'table_validation_deltas', '--page', 'validation', '--value', 'tbl_VMO_GL_Transactions[Reconciliation Variance]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'matrix', '--name', 'matrix_validation_status', '--x', '808', '--y', '152', '--width', '448', '--height', '360'))
Invoke-Pbi ($visualArgs + @('bind', 'matrix_validation_status', '--page', 'validation', '--row', 'tbl_Reconciliation_GL_Data[Match Status]', '--value', 'tbl_Reconciliation_GL_Data[Exception Rows]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'slicer', '--name', 'slicer_validation_year', '--x', '24', '--y', '544', '--width', '240', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_validation_year', '--page', 'validation', '--field', 'tbl_Calendar[Financial Year]'))
Invoke-Pbi ($visualArgs + @('add', '--page', 'validation', '--type', 'slicer', '--name', 'slicer_validation_period', '--x', '280', '--y', '544', '--width', '240', '--height', '92'))
Invoke-Pbi ($visualArgs + @('bind', 'slicer_validation_period', '--page', 'validation', '--field', 'tbl_Calendar[Period]'))

if (-not $SkipLocalProofBindings) {
    $repoRoot = (& git -C $PSScriptRoot rev-parse --show-toplevel 2>$null)
    $localProofBindingScript = Join-Path $repoRoot 'scripts/Set-PbirLocalProofBindings.ps1'
    if (Test-Path -LiteralPath $localProofBindingScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $localProofBindingScript -ReportPaths @($ReportPath)
    }
    $embeddedSampleDataScript = Join-Path $repoRoot 'scripts/Set-PbirEmbeddedSampleData.ps1'
    if (Test-Path -LiteralPath $embeddedSampleDataScript) {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $embeddedSampleDataScript -ReportRoots @((Join-Path $ReportPath 'VMO Finance.Report')) -TableRoots @((Join-Path $ReportPath 'Dataset/definition/tables'))
    }
}

& $pbi.Source report --path $ReportPath validate
