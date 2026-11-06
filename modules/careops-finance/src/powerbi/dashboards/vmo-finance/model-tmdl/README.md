# VMO Finance Model TMDL

This folder contains the curated model build notes and the current live TMDL export from the Power BI Desktop implementation session.

Current status:

- `live-export/` contains the exported TMDL from the current Desktop model.
- `measure-catalogue.md` and `relationship-checklist.md` are build guidance
  files, not exported TMDL.
- `tests/tmdl/Test-LiveExportTmdl.ps1` validates that the live export, required
  table TMDL files, and currently exported catalogue measures remain present.

Keep production SQL Server source templates under `../m/sql/`, and do not commit
raw Access databases or extracted data.
