# Agent, Security, and Contribution Context

## Operating model

- This public repository is maintained by a single owner and contains reusable source; private operational deployments retain their own owners and authority.
- No mandatory review, CODEOWNERS, or team-approval gates are required for merge.
- Recovery remains possible via repository owner override and branch protection exceptions.

## Current automation posture

- Continuous checks:
  - `validate` workflow (`validate (RepositoryHygiene)`, `validate (SourceControlReady)`)
  - `workflow-lint`
  - `secret scan`
  - `codeql` (`analyze`)
  - `coverage` (Codecov upload + OIDC)
- Bot workflow:
  - Renovate inherits from `github>edithatogo/renovate-config`
  - Dependabot is intentionally removed once Renovate is active.

## Required review of changes

- Keep raw data, credentials, and environment secrets out of git.
- Use the one-command quality gate before merge.
- Keep changes minimal and reproducible across Windows and GitHub-hosted runners.

## Qualified suite CI rollout

The shared CareOps security job replaces duplicate tool installation while retaining
the existing lint workflows and secret scan gate names until hosted protection
migration is verified. All current-head checks must pass before normal merge;
owner bypass is not the suite delivery route. Renovate remains the sole updater,
with immutable action digests and no automatic promotion. Runtime development
candidates require source validation and exact artifact integrity evidence.
Billing refusals are not executed test failures or successful qualification.

## Portable suite delivery

Read README.md and .careops/module.json for the existing source/native queue and
shared standards. Retain exact pins, current-head CI gates and publication
boundaries. Use only fictional inputs in portable source; private bindings,
records and native exports remain outside Git. Preserve existing component IDs
and publisher/logical names. Source packaging never establishes native operation.
Evaluate the shared preferred structured-document route before a new generator.

## Python execution

Prefer the latest suitable qualified Python, currently repo-local 3.15.1, for
helpers, tests and CI. Verify the actual interpreter and prefix; retain exact
source/tool pins and existing security/functionality gates. The user's 24 October
clarification permits a necessary compatible/provider version without additional
permission when its concrete reason, scope and actual execution are recorded.
Do not replace a working environment underneath an active operation.

## Targeted test execution

Follow the [shared targeted-testing policy](https://github.com/edithatogo/careops/blob/main/docs/targeted-testing.md).
During edits, select exact affected files/nodes or native runner checks and reuse
unchanged evidence. Use an explicitly selected repo-local Python3.15.1 via
REPO_PYTHON where applicable. Do not rerun unchanged whole suites during each edit.
Run broader tests for shared fixtures, schemas, dependencies or uncertain impact;
retain full coverage/security/integration and release gates at coherent milestones.

For pytest, preserve cacheprovider per worktree/environment: --lf together with
--last-failed-no-failures=none never silently runs all tests; empty means no tests
verified. --ff still runs all selected tests; --sw is local debugging only. Do not
set selection flags globally or present partial coverage as full coverage.
Default to no automatic retries. skip/skipif requires a real capability condition
and reason; xfail needs a known issue/reason and strict=True. Neither is for speed.
Never retry native mutations, sends or real external effects through test plugins.
Difftest0.3.0 failed actual3.15.1 qualification (PyO3 maximum3.14); do not install
it with a compatibility override or downgrade Python. Rerunfailures16.7 is opt-in
for bounded, diagnosed fictional/read-only transient cases with first failure
visible; it must not turn flaky outcomes into clean acceptance.

Existing runner example (select the actual changed case, not this example blindly):

```sh
pwsh -NoProfile -File scripts/Invoke-Validation.ps1
```

This module uses its existing PowerShell validation; pytest flags do not select
PowerShell tests. Choose an affected existing validation script where available.

## Project-owned code licensing

Use Apache-2.0 for project-owned source and active package metadata. Include the
licence and notice in source distributions. Preserve third-party terms, notices
and attribution, historical evidence and private/external source rights. This
standard changes no publication, native, access or email authority.
