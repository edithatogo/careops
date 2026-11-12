# Remote Dashboard Discovery

## Purpose

The analytics share contains additional finance dashboards that should inform the shared semantic model, but the dashboards should not be bulk-copied to this workstation or committed to git.

Target share:

```text
//example.invalid/analytics
```

Current workstation status: direct enumeration returned access denied, so discovery is staged until the Windows account, VPN, or domain permissions allow read access.

## Discovery Levels

### Level 0: File Metadata

Run a metadata-only inventory over the share. This records path, extension, size, last modified time, and folder context. It does not open file contents.

Output goes under ignored `data/profile/remote-dashboard-discovery/`.

### Level 1: Source Folder Parsing

For PBIP/PBIR/TMDL folders, parse source files in place where permissions allow. Catalogue report pages, visual files, table names, measures, parameters, and source expressions. Do not copy data files.

### Level 2: Targeted Temporary Extraction

For selected PBIX/PBIT files, use approved CLI tooling to extract metadata into ignored temporary workspace storage, catalogue the result, then delete the extracted working copy. This is only for selected dashboards where file metadata is insufficient.

### Level 3: Model Mapping

Convert the catalogue into model candidates:

- Shared dimensions: date, finance period, cost centre, account, organisation, service.
- Shared facts: GL, VMO, workforce/payroll, budget/forecast, reconciliation.
- Report-specific facts and measures that should remain in thin reports.
- SQL Server source contracts and gateway requirements.

## CLI Entry Point

Use:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Export-RemoteDashboardInventory.ps1 -Root '//example.invalid/analytics'
```

The script is intentionally metadata-only. It creates CSV and JSON inventory files under ignored `data/profile/remote-dashboard-discovery/`.

## Catalogue Fields

The dashboard catalogue should retain:

- Full path.
- Relative path from the analytics root.
- File or folder name.
- Extension.
- Item type.
- Size in bytes.
- Last modified time.
- Candidate dashboard type.
- Candidate business domain.
- Discovery status.

## ALM Rules

- Do not commit PBIX, PBIT, Access databases, Excel extracts, generated inventories, credentials, or temporary extraction folders.
- Commit only source-control friendly PBIR/TMDL/model/report artifacts, scripts, docs, and validated config.
- Keep environment-specific SQL, gateway, workspace, and credential details parameterised.
