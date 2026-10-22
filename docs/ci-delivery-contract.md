# Shared CI/CD contract

The [Conductor programme](../conductor/tracks/suite_ci_delivery_20261018/index.md)
and [rollout matrix](../portfolio/ci-rollout.json) retain the full suite scope.
Module-specific tests and independently usable source remain mandatory. Shared CI
is a source-delivery dependency, not a runtime service or native acceptance claim.

## Immutable adoption

Call `.github/workflows/reusable-source-security.yml` from this public repository
at an exact qualified commit. Supply the same commit in `policy-revision` so the
hash-locked policy tools come from that reviewed revision. The job validates the
input against GitHub's called-workflow identity before checkout, refusing mismatches
or missing identity. It reads the documented job identity through JSON to remain
compatible with actionlint's older context type definitions; no audit is suppressed.
This route targets GitHub.com, not GitHub Enterprise Server. The workflow scans the
caller's full Git history, requires immutable action/workflow references and runs
checksum-verified actionlint and hash-locked zizmor. It has contents-read permission,
no inherited secrets, no private submodule checkout and no deployment action.
Callers with requirements-ci.txt must commit a matching requirements-ci.lock; the shared job rejects stale exact declarations before installing policy tools. Callers without this declaration format retain their own dependency gates.
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
keeps receipts even after a failed qualification. A separate CPython job discovers an available prerelease newer than the qualified
stable baseline for the runner platform, freezes the upstream manifest revision
and digest, and exercises the current source/lock only when a candidate exists.
Unavailable candidates produce an explicit receipt and skipped runtime test steps;
a successful discovery job is not a passed runtime qualification. Older previews
are not selected in preference to the newer stable runtime. No
working lock, native object, connection or credential is changed. An unavailable
runtime/package is a failed qualification, not a reason to mutate the baseline.
There may be no newer preview for a package: report the exact selected version,
not a blanket claim that everything is prerelease. Schedule/manual results stay
separate from required release checks. Promotion is an explicit source PR with
exact versions, affected tests and rollback to the previous qualified lock.

Runtime finalization runs even when discovery fails, is cancelled or is skipped.
Pass the actual discovery and runtime-step outcomes separately. Missing evidence
after failed discovery produces a terminal discovery-failed receipt; malformed or
contradictory evidence produces evidence-invalid, retains the original bytes and
fails the recorder. Neither state qualifies a runtime or promotes a candidate.

## Hosted outcomes

Use `ci_delivery.py classify --input <private-run-receipt.json> --output .local/run-outcome.json` with the exact
run, jobs and annotations obtained from GitHub. Retain run/head identity in the
private receipt; do not echo account-related annotations or job names into public logs. Pending,
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

Before adding private-repository attestation jobs, verify repository ownership and
service eligibility. GitHub private artifact attestations require Enterprise
Cloud; enterprise repositories are organization-owned. Private personal-account
repositories cannot qualify this route under current ownership. Actions billing
recovery is independent and does not enable private signing. Keep actual package
hashes/SBOMs and source tests useful while recording signing as unavailable; they
do not substitute for signatures. A supported alternative or organization transfer
requires separate selection. No purchase, transfer, visibility change, public
transparency submission or new signing credentials are implied by this contract.
See [attestation availability](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
and [enterprise ownership](https://docs.github.com/en/enterprise-cloud@latest/admin/concepts/enterprise-fundamentals/enterprise-accounts).

## Safe rollout and recovery

Keep stronger existing controls. Establish exact check names through successful
current-head runs before enforcing them. Do not weaken checks or use admin bypass
to get a green merge. Revert the adopter's shared-workflow/tooling reference and
lock as one reviewed change if an update fails. The programme records every
module's adopted revision, tests, canary, package/attestation and protection
readback; absent evidence remains incomplete. Do not change billing, consent,
licensing or tenant settings to obtain CI success.

## Incidents standalone source package

`Attested standalone source release` builds the integrated Incidents module once
from reviewed files in the committed public inventory, including its licence and
standalone instructions. It does not package private history, data, working-tree
edits or untracked exports. Tar/gzip metadata and SPDX timestamps derive from the
source commit so repeated builds of that commit are reproducible. Existing output
files are refused. This is a source release, not a managed deployment or native
Power BI acceptance.

The build emits a package, SPDX 2.3 SBOM with per-file SHA256/SHA1 and the package
verification code, SHA256SUMS and a source receipt. The official SPDX schema is
frozen by upstream commit and SHA256. SHA1 is used only for SPDX's specified
verification algorithm; release integrity uses SHA256. All package bytes and SBOM
content are tested together. No third-party runtime library is distributed in
this standard-library staging module; PowerShell/Power BI remain prerequisites.

Only the canonical protected main branch can attest the package. Job-scoped
GitHub OIDC produces build and SBOM attestations; there is no tenant credential,
registry push or environment deployment. Verification binds the package to the
repository, source ref and signer workflow and rejects self-hosted signing.
The candidate artifact retains package/SBOM/digests and any completed attestation
proof even when a qualification step fails. A retained candidate is verified only
when its exact workflow and verification receipts pass. Downloaded artifacts must
be independently verified again; a successful upload alone is not release proof.

The SPDX2.3 attestation predicate is `https://spdx.dev/Document/v2.3`; the
unversioned Document URI does not match the SDK's signed payload. Verification
also binds both source and signer commit digests to the exact build SHA. Preserve
bundles before verification so failed verification remains independently auditable.

Required source CI also compares exact declared tool versions with the committed
lock. Automatic regeneration retains repair artifacts but refuses uncommitted
lock/inventory changes. A generated working-tree install cannot qualify a stale
source commit. The parent security workflow now calls the common baseline once;
duplicate secret/workflow jobs and the separate caller are removed. Existing
required context `security / Shared source security` is preserved. The Security
gate still refuses any failed, skipped or cancelled required child.

## ZIP-family artifact inventories

`portfolio-scripts/artifact_sbom.py` inventories the actual managed solution ZIP,
wheel or other ZIP-family package without extracting or executing it. Supply the
qualified source commit and its recorded commit timestamp; preserve an existing
SBOM by choosing a new output revision. The SPDX 2.3 inventory includes every file's
SHA256 and SHA1, the archive SHA256 and package verification code. It refuses
duplicate identities, traversal/absolute paths, links, encryption and oversized or
empty archives. Binary content is included. Licence fields remain NOASSERTION
unless independently established. Unbundled resolved dependencies require their
own lock-derived inventory; this helper does not claim native acceptance. Sign
and independently verify the exact package/SBOM pair through the release workflow.

A historical release manifest and receipt remain an immutable pair. A newer
optional source gitlink requires its own exact reviewed publication and
compatibility pins; it does not rewrite the prior release. For Approve, the
public runtime qualification verifies all three release-facing schemas against
the historical source bytes and recorded SHA256s, then exercises the actual
Process consumer. That qualifies this source boundary, while the disabled
Approve emitter and native integration remain unqualified.


## Dependency and distribution failures

Distinguish an unavailable release from a distribution manifest that has not yet
listed its existing asset. Clinical Hub PR23 qualified uv0.13.5 through its official
Linux x86_64 release after setup-uv's default mirror manifest omitted that version.
An alternative installer must retain the selected exact version, expected platform,
reviewed archive digest, bounded selected binaries and executable-version check.
Verify the digest before extraction/execution; a matching version label alone is
insufficient. Do not turn a missing manifest entry into an unverified installer,
a floating download or a silent downgrade. Keep the normal review/check gates and
record which route actually ran. This is a source-tool distribution remedy, not
an authentication-provider fallback or a new native deployment route.

A greatest-version canary can also be blocked by an unused direct dependency's
peer constraints. Costing PR9 removed an unimported React-through-18 dependency;
its retained dependency identities did not change, both baseline builds/audits
passed, and the new candidate graphs then resolved, audited and built. Establish
actual usage and lock impact before pruning. Do not use force/legacy peer bypasses
to label an incompatible graph qualified. Preserve old failure receipts and exact
new candidate hashes. Install/audit/build qualification remains separate from
browser behaviour and promotion. The current baseline's native-config-loader
builds also verify the ESM alias change without suppressing Vite warnings.


When adding a custom updater to a repository that already uses Dependabot,
restrict Renovate's enabledManagers to the intended custom manager unless an
explicit ecosystem handover is selected. A new customManagers entry does not
disable default managers. PPG retains Dependabot for Actions and uses Renovate
only for its uv-version regex. Check actual extraction with a credential-free
local run: exactly the intended manager/dependency must remain. Release lookup
may require authenticated hosted execution; extraction alone is not a successful
lookup or update proposal. Preserve pinned digest verification and disabled
auto-merge when proposals change only the version.
