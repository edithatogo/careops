# Deployment Dry-Run Checklist

This checklist is for the next ALM/private-GitHub handoff only. It does not approve a live publish or deployment.

## Private GitHub

- [ ] Confirm the private GitHub repository exists as `careops-finance`.
- [ ] Confirm the repo is private.
- [ ] Confirm the local remote alias is `private`.
- [ ] Confirm the local remote URL is `git@github.com:<org>/careops-finance.git`.
- [ ] Run `git status --short` and review any uncommitted changes before the operator-controlled first push.
- [ ] Run `./scripts/Invoke-Validation.ps1 -Mode RepositoryHygiene -SkipPowerBiCli`.
- [ ] Run `./scripts/Invoke-Validation.ps1 -Mode SourceControlReady -SkipPowerBiCli`.

## CI

- [ ] Confirm `.github/workflows/validate.yml` runs `RepositoryHygiene`.
- [ ] Confirm `.github/workflows/validate.yml` runs `SourceControlReady`.
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
