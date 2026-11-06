# Deployment Dry-Run Checklist

This checklist is for the next ALM/private-GitHub handoff only. It does not approve a live publish or deployment.

## Maintained source checkout

- [ ] Confirm the suite checkout points to `edithatogo/careops`, with Finance under `modules/careops-finance`.
- [ ] Confirm both legacy Finance repositories remain private and archived; do not configure a push to either.
- [ ] Inspect the existing suite remotes without changing another owner's configuration.
- [ ] Keep operational exports, deployment bindings, credentials and local evidence outside Git in the existing private owner scope.
- [ ] Run `git status --short` and review owned source changes before any source push through the ordinary privacy hooks.
- [ ] Run `./scripts/Invoke-Validation.ps1 -Mode RepositoryHygiene -SkipPowerBiCli` from this module.
- [ ] Run `./scripts/Invoke-Validation.ps1 -Mode SourceControlReady -SkipPowerBiCli` from this module.

## CI

- [ ] Confirm the suite-root `.github/workflows/fcd-source.yml` runs `RepositoryHygiene`.
- [ ] Confirm the suite-root `.github/workflows/fcd-source.yml` runs `SourceControlReady`.
- [ ] Confirm CI uses `-SkipPowerBiCli` unless pbi-cli and pbi-tools are explicitly installed on the runner.
- [ ] Confirm `PublishRefreshReady` is not a default pull-request or push gate.

## Environment Gates

- [ ] Populate `PBI_SQL_SERVER_HOST` outside source control.
- [ ] Populate `PBI_SQL_DATABASE` outside source control.
- [ ] Populate `PBI_GATEWAY_ID` outside source control.
- [ ] Populate `PBI_TENANT_ID` outside source control.
- [ ] Populate `PBI_CLIENT_ID` outside source control.
- [ ] Populate `PBI_CLIENT_SECRET` outside source control.
- [ ] Confirm workspace names and approval notes are recorded outside source control.
- [ ] Run `./scripts/Invoke-Validation.ps1 -Mode PublishRefreshReady` only after all required values are present.

## pbi-tools Dry Run

- [ ] Confirm deployment profiles remain disabled in dashboard manifests.
- [ ] Confirm refresh remains disabled in dashboard manifests.
- [ ] Confirm compile outputs will go under ignored validation artifacts.
- [ ] Run `pbi-tools info`.
- [ ] Run compile checks if Dataset source files exist.
- [ ] Run `pbi-tools deploy <dashboard-folder> <profile> Development . true` only as a what-if dry run after workspace, authentication, gateway, and approval details are confirmed.
- [ ] Capture dry-run command output in the acceptance notes.
- [ ] Stop before any live publish, refresh enablement, or production deployment.
