# Shared CI/CD contract

The [Conductor programme](../conductor/tracks/suite_ci_delivery_20261018/index.md)
and [rollout matrix](../portfolio/ci-rollout.json) retain the full suite scope.
Module-specific tests and independently usable source remain mandatory. Shared CI
is a source-delivery dependency, not a runtime service or native acceptance claim.

## Immutable adoption

Call `.github/workflows/reusable-source-security.yml` from this public repository
at an exact qualified commit. Supply the same commit in `policy-revision` so the
hash-locked policy tools come from that reviewed revision. The workflow scans the
caller's full Git history, requires immutable action/workflow references and runs
checksum-verified actionlint and hash-locked zizmor. It has contents-read permission,
no inherited secrets, no private submodule checkout and no deployment action.
Keep existing native/source tests; this workflow does not replace them. Qualify
the shared revision in each consumer before making its named check required.

The parent qualifies an immutable candidate commit through its own caller.
Cross-repository consumers must pin both references to the accepted policy SHA.
The new GitHub `$/` self-reference syntax is not yet accepted by actionlint 1.7.12;
use an immutable remote commit while retaining both linters, rather than suppressing
a check.
Use one dependency updater per ecosystem; keep action commits immutable as new
versions advance. Resolve annotated tags through their commit objects first.
A different tag-object ID is not a different source commit.

## Lock generation and promotion

`Regenerate CI lock candidate` automatically resolves the declared exact CI pins,
regenerates the hash lock and inventory, installs/tests it and uploads the lock,
inventory, patch and exact-version/digest receipt. It is read-only: the existing
source owner applies the generated patch to the update PR; the declared-versus-lock
regression stays required. This works on untrusted PRs without granting write
permissions or executing PR code in `pull_request_target`. Successful regeneration
is not promotion; every current-head check must pass after the generated changes
are committed, before normal protected merge. Automation of proposal application
must retain this boundary and is tracked separately in the programme.

The reproducible local equivalent uses Python 3.11+ and qualified uv 0.13.1:

```bash
python3 portfolio-scripts/ci_delivery.py lock --output requirements-ci.lock --receipt .local/ci-lock.json
python3 portfolio-scripts/inventory_dependencies.py --root . > portfolio/dependency-inventory.json
```

## Development canaries

The scheduled/manual development workflow resolves newest compatible CI tools,
allowing prereleases, into a separate hashed candidate lock and records every
resolved version. It installs that candidate, runs affected tests/lint/audit and
keeps receipts even after a failed qualification. A separate CPython development
job records the resolved runtime and exercises the current source/lock. No
working lock, native object, connection or credential is changed. An unavailable
runtime/package is a failed qualification, not a reason to mutate the baseline.
There may be no newer preview for a package: report the exact selected version,
not a blanket claim that everything is prerelease. Schedule/manual results stay
separate from required release checks. Promotion is an explicit source PR with
exact versions, affected tests and rollback to the previous qualified lock.

## Hosted outcomes

Use `ci_delivery.py classify --input <private-run-receipt.json>` with the exact
run, jobs and annotations obtained from GitHub. Retain run/head identity. Pending,
passed, executed failure, billing-blocked, cancelled, skipped and unverified states
are distinct. Mixed executed failures and billing annotations remain visible.
A billing refusal before execution is not a tested failure or a pass; a local
result cannot substitute for hosted checks. A green generic job does not prove
that a module's domain tests, native operation or operational acceptance occurred.

## Compatibility and release requirements

Cross-module tests must exercise actual selected optional interfaces: provider
absence and version incompatibility, source-qualified identity, stale/missing
input, duplicate retry and preservation of owner edits. Do not assert integration
from a catalogue row or invent a shared authoritative business table. No tenant
writes are needed for fictional contract tests.

For real independently useful release packages, build once from a qualified SHA,
record file/package digests, emit an SBOM matching those actual contents and attach
GitHub build/SBOM attestations using job-scoped federated permissions. Download and
verify the artifact and attestation against expected repository/workflow identity.
Private contents and evidence stay private. Retain existing managed Power Platform
build/check steps where applicable and qualify deployment separately. Templates
or an attestation-producing workflow alone do not close a release gate.

## Safe rollout and recovery

Keep stronger existing controls. Establish exact check names through successful
current-head runs before enforcing them. Do not weaken checks or use admin bypass
to get a green merge. Revert the adopter's shared-workflow/tooling reference and
lock as one reviewed change if an update fails. The programme records every
module's adopted revision, tests, canary, package/attestation and protection
readback; absent evidence remains incomplete. Do not change billing, consent,
licensing or tenant settings to obtain CI success.
