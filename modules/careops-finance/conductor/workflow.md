# Workflow

## Development Flow

1. Inventory Access sources before modelling.
2. Keep extraction scripts read-only against `.accdb` files.
3. Commit only code, configuration, documentation, and Power BI source-control artifacts.
4. Export or refresh TMDL after Power BI Desktop model changes.
5. Validate scripts and manifests before pushing.
6. Use the Power BI CLI surface before Desktop UI for report work.

## Validation Gates

Run:

```powershell
.\scripts\Invoke-Validation.ps1
```

For Access-specific checks, run targeted inventory first:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Get-AccessInventory.ps1 -DatabasePath ".\data\raw\VMO Reporting.accdb"
```

## Git Hygiene

- Use feature branches when collaborating.
- Do not commit files under `data/`.
- Do not commit `.pbix`, `.pbit`, `.accdb`, `.laccdb`, `.env`, or extracted CSVs.
- Treat `config/sources.json` as the source registry, not as a credential store.

## Power BI ALM

- Keep M templates under `src/powerbi/m/`.
- Keep TMDL exports under `src/powerbi/model-tmdl/`.
- Keep deployment manifests under `src/powerbi/Deployment/`.
- Use `pbi report`, `pbi visual`, PBIR JSON, TMDL folders, validation scripts,
  and `pbi-tools` for build and validation work before falling back to Power BI
  Desktop UI.
- Use deployment dry-runs before any Power BI Service promotion.

## Targeted test cadence

Follow AGENTS.md targeted-test guidance during edits. Preserve full integration,
coverage and release gates at coherent milestones. Cached or zero-test results
are not complete acceptance evidence.
