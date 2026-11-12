# Dashboard Acceptance and Publish Readiness

## Objective

Prepare both standalone dashboards for controlled publishing after the VMO and Medical Staff builds are complete.

## Requirements

- Confirm both dashboards pass repository validation.
- Confirm source-control exports exist and contain no data or secrets.
- Confirm live TMDL, PBIR, and pbi-tools Dataset exports validate from the source-controlled exports.
- Confirm SQL Server parameters, gateway assumptions, and deployment placeholders are documented.
- Prepare business acceptance checklists for VMO Finance and Medical Staff.
- Run pbi-cli source validation without reloading or changing Power BI Desktop.
- Run `pbi-tools deploy <dashboard-folder> <profile> Development . true` only when workspace/authentication details are explicitly provided.
- Keep deployment profiles disabled until publishing is approved.

## Acceptance Criteria

- Both dashboards have validation notes and unresolved issue lists.
- Git status contains no raw data, extracts, lock files, credentials, `.pbix`, or `.pbit`.
- Deployment manifests remain secret-free and disabled unless explicitly approved.
- Private GitHub push instructions are current.
- Publish-readiness checklist identifies blockers, owners, and next action.
- `./scripts/Invoke-Validation.ps1 -RequirePowerBiExports` passes against the exported live artifacts.
- The acceptance notes record the pbi-cli and pbi-tools commands used for final verification.
