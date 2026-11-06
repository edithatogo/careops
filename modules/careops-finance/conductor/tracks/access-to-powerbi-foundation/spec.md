# Access to Power BI Foundation

## Objective

Create a private-repo-ready project foundation that can inventory Microsoft Access finance databases, extract local tables through CLI tooling, and host Power BI source-control artifacts for later ALM deployment.

## Requirements

- Initialize git and Conductor context.
- Keep raw `.accdb` files and extracted data outside source control.
- Provide CLI scripts for database inventory and table export.
- Provide a source registry for the known Access databases.
- Provide Power BI folders for M templates, TMDL exports, report source, and deployment manifests.
- Provide validation that can run without publishing or deploying anything.

## Acceptance Criteria

- `git status` shows a source-only repo with raw data ignored.
- `scripts/Get-AccessInventory.ps1` can inventory at least the smaller Access database through ACE OLEDB.
- `scripts/Invoke-Validation.ps1` validates PowerShell syntax, git ignore behavior, and local Power BI CLI readiness.
- Documentation explains the local workflow and ALM path.
