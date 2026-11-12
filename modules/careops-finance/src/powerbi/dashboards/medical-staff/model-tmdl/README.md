# Medical Staff Model TMDL

This folder contains the curated model build notes and the current live TMDL export from the Power BI Desktop implementation session.

## Current Contents

- `measure-catalogue.md` - maintained DAX measure catalogue for the standalone model.
- `relationship-checklist.md` - relationship and date-table build checklist for the live model.
- `live-export/` - exported TMDL from the current Desktop model.
- `tests/tmdl/Test-LiveExportTmdl.ps1` validates that the live export, required
  table TMDL files, and currently exported catalogue measures remain present.

## Export Rule

- Keep `live-export/` generated from Power BI Desktop or a compatible exporter.
- Keep production SQL Server source templates under `../m/`; do not commit raw Access databases or extracted data.
