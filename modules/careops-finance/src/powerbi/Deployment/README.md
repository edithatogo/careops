# Deployment Manifests

Keep `pbi-tools` deployment manifests here once Power BI workspaces, report names, and service principals are confirmed.

Short-term work should use local extraction, local Desktop development, and `pbi-tools deploy ... -whatIf` only.

The deployment handoff currently lives in `docs/Deployment/`:

- `docs/Deployment/powerbi-alm.env.sample` lists the required operator environment variables without values.
- `docs/Deployment/dry-run-checklist.md` records the no-deploy dry-run checklist.

Do not add tenant ids, client ids, secrets, gateway ids, workspace names, or SQL Server details to this folder until the values have an approved non-secret storage path. Real secrets never belong in git.
