# Clinical Hub Core

Current source home: `edithatogo/careops`, `modules/clinical-hub-core`.
See [migration and continuity](MIGRATION.md). This supersedes older child-repository development directions below.

Reusable meeting-management development tools for Power Platform and Microsoft 365.
This source-only repository contains fictional tests and no deployed application,
tenant bindings, meeting records or credentials. Its Git history starts fresh.

## Included capabilities

- Agenda review transitions, source/version validation and linked-paper preflight.
- Editable agenda/minutes development fixtures with overwrite protection.
- Transcript/candidate contracts and reviewed-outcome previews.
- Carry-forward source adapters and operator-input builders.
- Calendar comparison, configuration and portable flow-definition builders.
- Solution-package validation and explicit site-binding portability candidates.

Python utilities are development and verification tools. Ongoing meeting operation
belongs in Power Platform/Microsoft 365. Prefer maintained Word templates with the
selected SharePoint library-column route; local document utilities support
one-time preparation and testing, not a hosted replacement runtime.

## Setup and checks

The current qualified baseline is Python 3.15.1. Evaluate newer development
runtimes in isolation before changing `.python-version` and the hash lock:

```sh
uv python install 3.15.1
uv venv --python 3.15.1 .venv-ci
uv pip sync --python .venv-ci/bin/python --require-hashes requirements-dev.lock
make ci audit
# CareOps root CI owns publication/security checks; preserve its hooks.
# Use scripts/install_hooks.sh only for an independent standalone checkout.
```

Install Gitleaks 8.30.1 before committing or pushing. The hooks scan staged source
and history. CI repeats source validation, tests, bounded Hypothesis property
fuzzing, secret scanning and dependency auditing without tenant credentials.
`make fuzz` runs just the fuzz target. Renovate proposes dependency updates without
automerging them. No automated tenant deployment is configured.

See [the implementation plan](conductor/implementation-plan.md) and
[tool routing](conductor/tool-routing.md). Required deployment inputs must be supplied
privately and qualified for the selected operation. Tests are not proof of a native
flow deployment, licence, access permission or authority to distribute records.
For mailbox retrieval through an existing connection, see the
[CLI-managed Outlook connector route](conductor/outlook-connector-cli.md).

## Checking a downloaded source archive

The manual source-package workflow distributes committed source and an SPDX file
SBOM, without Git history or a bundled Python runtime. Before extraction, verify
the archive's provenance and SBOM attestations against this repository and the
source-release workflow. Compare the extracted files with the SBOM checksums;
`release.json` identifies the packaged commit, which may differ from current main.
Before trusting the separately downloaded `source.spdx.json`, check that it agrees
with the signed SPDX predicate returned by verification (`--format json`).

From the downloaded artifact directory, these commands verify the two signed
claims for the archive before extraction:

```sh
gh attestation verify clinical-hub-core.tar --repo edithatogo/careops \
  --signer-workflow edithatogo/careops/.github/workflows/clinical-hub-release.yml
gh attestation verify clinical-hub-core.tar --repo edithatogo/careops \
  --signer-workflow edithatogo/careops/.github/workflows/clinical-hub-release.yml \
  --predicate-type https://spdx.dev/Document
```

After extraction, run the first three setup commands above to install the selected
Python, create `.venv-ci` and sync the hash lock. Then run `make test audit` from
the extracted source root. This checks the offline
suite and declared dependencies without creating a Git repository. Fixture tests
that exercise Git create their own disposable repositories; Git must be installed.

`make ci`, `make validate`, commit hooks and `make secrets` inspect a Git index or
history and belong in a real checkout. Do not initialise an archive as a new
repository just to claim committed-source validation. An archive's own allowlist
does not replace verified provenance, checksum inspection or the checkout's
source/security gates. Keep `make ci audit` for development and PR qualification.

## Private working material

Operational records and the original repository history are intentionally absent.
Do not copy private files or historical commits into this repository. Preserve
working operational copies separately. `PUBLIC_SOURCE_FILES.json` lists the initial
reviewed source import; new files require the same source-only checks.

## Canonical development and migration

All new Clinical Hub source development uses this repository. The archived private
predecessor is retained as recovery evidence, not a second development remote.
No private history, operational evidence, real-content records or binaries were
merged. The external ignored `.private-workspace/` retains every prior work item,
uncommitted file and native receipt. The ignored `private/` link exposes the same
operational evidence without copying it into public source.

See [migration and active work](conductor/canonical-migration.md) for continuity,
qualification limits and recovery. Public helpers and Office Script fixtures are
fictional maker tools; native bindings and deployed identities remain private.

## Reconciled meeting capability

Selected-register adapters, preparation carry-forward, aggregate feedback and
source-only write-lifecycle guards are integrated with the existing meeting
helpers. See [historical dispositions and connected verification](conductor/historical-integration.md).
The domain suite includes the connected fictional meeting cycle and independent
DDMS/recovery boundaries. Private operational prerequisites retain their own scope.

## Current project-owned source licence

Project-owned source uses the parent [Apache-2.0 licence](../../LICENSE) and
[notice](../../NOTICE). Original migration/provenance records retain their dated
meaning. External documents, private evidence and third-party components retain
their own rights; this does not authorise their redistribution or native use.
