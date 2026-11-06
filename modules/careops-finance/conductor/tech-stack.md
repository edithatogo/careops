# Technical Stack

## Runtime

- Windows PowerShell 5.1 for Microsoft ACE OLEDB compatibility.
- PowerShell 7 for general scripting where Access provider support is not required.
- Git for source control.

## Data Sources

- Microsoft Access `.accdb` files stored under `data/raw/`.
- Local exports under `data/extracts/`.
- Profiling and schema inventory under `data/profile/`.

## BI Tooling

- Power BI Desktop for local model/report development.
- `pbi-cli` for semantic-model inspection, TMDL import/export, and scripted model operations.
- `pbi-tools` for PBIX/PBIT extraction, compilation, and later deployment manifest support.
- TMDL as the preferred semantic model source-control format once a model exists.

## Repository Policy

- Source code, scripts, documentation, Conductor context, and Power BI source artifacts are committed.
- Raw Access files, extracts, profiles, credentials, logs, and generated binaries are excluded from git.
- Environment-specific paths should be parameters, not hard-coded into model source.

Project-owned code uses Apache-2.0 under the user-selected portfolio standard.
Preserve third-party terms, attribution, historical evidence and private-source
rights; qualify source/package changes without changing native authority.
