# Power BI ALM Workflow

This repository is staying in a no-deploy state for now. The goal is to keep the Power BI projects private-GitHub-ready, with deployment manifests present but disabled until the target tenant, service principal, and workspace names are confirmed. `SourceControlReady` is the source-control gate for exported TMDL/PBIR source and does not require raw data files or SQL Server/gateway details in git.

## Acceptance Readiness

Use [docs/dashboard-acceptance.md](dashboard-acceptance.md) as the working gate for both dashboards before any publish attempt.

The readiness bar is simple:

1. Complete the VMO Finance and Medical Staff acceptance checklists.
2. Capture validation notes and unresolved issues in the template.
3. Record any blockers with an owner and next action.
4. Keep deployment profiles disabled until publish approval is explicit.
5. Keep dry-run deployment as the first and only deployment-adjacent step, and only after workspace and authentication details are confirmed.

## Historical private GitHub handoff

This section records the original private implementation handoff. The current
public repository contains reusable source only; do not push private history or
operational bindings into it. Use a dedicated private remote only for an
independently authorized private deployment, without changing this public clone.
The historical private GitHub example is:

| Setting | Expected value |
| --- | --- |
| Repository name | `careops-finance` |
| Visibility | Private |
| Remote alias | `private` |
| Remote URL | `git@github.com:<org>/careops-finance.git` |
| Default branch | `main`, unless the created repository is explicitly initialized with `master` |
| Data policy | No raw Access files, extracts, credentials, `.env`, PBIX/PBIT outputs, or local profiling artifacts |

```powershell
git remote add private git@github.com:<org>/careops-finance.git
git push -u private main
```

If the repository already has a `private` remote, update it instead of adding a second one:

```powershell
git remote set-url private git@github.com:<org>/careops-finance.git
```

Before the first push, run:

```powershell
git remote -v
git status --short
./scripts/Invoke-Validation.ps1 -Mode RepositoryHygiene -SkipPowerBiCli
./scripts/Invoke-Validation.ps1 -Mode SourceControlReady -SkipPowerBiCli
```

Do not push from this handoff pass. The push is a later operator-controlled action after the changed files are reviewed.

## Dry-Run ALM

Keep ALM promotion as a local rehearsal until the deployment targets are confirmed.

1. Run `./scripts/Invoke-Validation.ps1 -Mode SourceControlReady` before packaging.
2. Confirm the acceptance checklists and blocker register in `docs/dashboard-acceptance.md` are current.
3. Keep the dashboard `.pbixproj.json` files pointed at `./Dataset` and leave the `Development` and `Production` environments disabled.
4. Keep secrets in environment variables, not in the manifest.
5. Run the installed `pbi-tools` deployment command with `whatIf` set to `true` against the dashboard PbixProj folder and deployment profile.
6. Review the output for workspace, authentication, and parameter substitutions before any live deployment is enabled.

Use [docs/Deployment/dry-run-checklist.md](Deployment/dry-run-checklist.md) as the step-by-step handoff checklist and [docs/Deployment/powerbi-alm.env.sample](Deployment/powerbi-alm.env.sample) as the non-secret environment variable template.

## Validation Modes

Use the validator mode that matches the question being answered:

| Mode | Purpose | Expected result in the current interim state |
| --- | --- | --- |
| `RepositoryHygiene` | Fast default check for scripts, required docs, disabled deployment profiles, ignored data, and tracked-file hygiene. | Should pass locally and in CI. |
| `SourceControlReady` | Confirms the repository is ready to carry exported TMDL/PBIR source, including PBIR coverage checks, without requiring a known SQL Server host, gateway, or raw Access data files. | Should pass once both dashboards have live TMDL and PBIR exports committed. |
| `PublishRefreshReady` | Confirms the source-control gate plus publish-refresh prerequisites: real Dataset source files and externally supplied SQL Server, database, gateway, tenant, client, and secret values. | Expected to fail until the database, gateway route, and credentials are confirmed outside source control. |

`-RequirePowerBiExports` is retained as a compatibility alias for `-Mode SourceControlReady`.

The GitHub Actions workflow runs `RepositoryHygiene` and `SourceControlReady` with `-SkipPowerBiCli` because hosted runners do not have the local Power BI CLI toolchain by default. `PublishRefreshReady` is not a default CI mode. It must only run in a controlled operator environment or protected CI environment where the required secrets and gateway details are explicitly supplied.

## Environment Gates

The publish-refresh gate requires these environment variables. Store secret values in the operator shell or a protected GitHub environment, never in the repository.

| Variable | Secret? | Purpose |
| --- | --- | --- |
| `PBI_SQL_SERVER_HOST` | No, but environment-specific | SQL Server host/listener behind the Access DSN handoff. Supply the actual value through the private deployment profile. |
| `PBI_SQL_DATABASE` | No, but environment-specific | Published-refresh database name. |
| `PBI_GATEWAY_ID` | No, but environment-specific | Power BI gateway identifier for SQL Server refresh. |
| `PBI_TENANT_ID` | No, but tenant-specific | Microsoft Entra tenant used for Power BI authentication. |
| `PBI_CLIENT_ID` | No, but tenant-specific | Service principal application client id. |
| `PBI_CLIENT_SECRET` | Yes | Service principal secret. |

Optional operator notes should record the confirmed workspace names, gateway owner, credential owner, and approval reference before any dry-run command is run.

## Live Artifact Verification

After a live Desktop model/report build is exported into source control, run the repository checks without opening or changing Power BI Desktop:

```powershell
./scripts/Invoke-Validation.ps1 -Mode SourceControlReady
```

Then run the Power BI source-control checks from the exported folders:

```powershell
pbi --json database diff-tmdl .\src\powerbi\dashboards\vmo-finance\model-tmdl .\src\powerbi\dashboards\vmo-finance\model-tmdl
pbi --json database diff-tmdl .\src\powerbi\dashboards\medical-staff\model-tmdl .\src\powerbi\dashboards\medical-staff\model-tmdl
pbi report --path .\src\powerbi\dashboards\vmo-finance\report\<export>.Report validate
pbi report --path .\src\powerbi\dashboards\medical-staff\report\<export>.Report validate
pbi-tools info
```

Use the self-diff commands as a parse/readiness check for the exported TMDL folders. When a prior approved baseline exists, replace the first path with that baseline and review the JSON diff before accepting the export.

If pbi-tools project files are exported into each dashboard `Dataset/` folder, compile or dry-run them before publish approval:

```powershell
pbi-tools compile .\src\powerbi\dashboards\vmo-finance .\artifacts\validation\vmo-finance.pbit PBIT true
pbi-tools compile .\src\powerbi\dashboards\medical-staff .\artifacts\validation\medical-staff.pbit PBIT true
pbi-tools deploy .\src\powerbi\dashboards\vmo-finance vmo-finance-dashboard Development . true
pbi-tools deploy .\src\powerbi\dashboards\medical-staff medical-staff-dashboard Development . true
```

The compile output belongs under an ignored validation/artifacts folder, not under source control. The dry-run deploy command remains blocked until workspace, tenant, client, gateway, and approval details are confirmed.

When those details are available in the operator environment, use the publish-refresh gate:

```powershell
$env:PBI_SQL_SERVER_HOST = "<sql-server-host>"
$env:PBI_SQL_DATABASE = "<database-name>"
$env:PBI_GATEWAY_ID = "<gateway-id>"
$env:PBI_TENANT_ID = "<tenant-id>"
$env:PBI_CLIENT_ID = "<client-id>"
$env:PBI_CLIENT_SECRET = "<client-secret>"
./scripts/Invoke-Validation.ps1 -Mode PublishRefreshReady
```

Do not commit those values. The current committed source can be source-control ready while still publish-refresh blocked.

## Current Guardrails

- `data/raw/`, `data/profile/`, and `data/extracts/` stay out of git.
- `SourceControlReady` validates exported source control artifacts without needing those data folders committed.
- Each dashboard folder keeps its own source-control scaffold.
- Shared semantic-model work stays under `src/powerbi/shared/` until the models are stable enough to merge.
- Deployment placeholders remain disabled until the real environment details are available.
- Live deployment stays off until the approval path is documented and confirmed.
- Do not run Desktop reload, import, or write commands as part of validation; this ALM pass verifies exported source only.


## Public source and private bindings

All tracked guides, plans and environment samples use `<sql-server-host>` rather
than the operator's actual host/listener. Keep real SQL, database, schema, gateway,
workspace and account bindings in an existing private deployment profile. A
placeholder is not discovery evidence or a usable publish-refresh value. This
source cleanup changes no deployed binding and enables no refresh/deployment.
Earlier Git revisions remain historical; this is not a history-erasure claim.
