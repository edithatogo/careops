# Portable CI, privacy and optional syndication

## Security posture

Retain the existing private-source boundary, explicit source inventory, exact
dependency/tool hashes, SHA-pinned actions, Python 3.15.1, Gitleaks history scan,
offline Presidio controls, Bandit/OpenGrep analysis and OSV dependency review.
These open-source controls do not require Copilot or paid GitHub Code Security.
No scanner proves the absence of confidential clinical or organisational context;
source admission still includes human review of reusable material and fixtures.

CI must inspect changed content and intermediate outgoing commits, not just the
final diff. Exact false-positive reviews bind to the policy, source identity,
content hash, entity and span; no module-wide exemption or automatic approval of
new findings. Unknown formats and scanner failures remain visible blockers. Keep
the existing binary/document content-and-metadata review and bounded file limits.

Separate tool/model acquisition from analysis. Pin and verify the analyser model
as well as packages, prohibit inference-time network fallback, run synthetic
positive/negative controls, and keep raw matches/reports outside CI logs/artifacts.
On controlled runners enforce egress denial at the process/container boundary;
the existing Python socket guard is not a sandbox against native extensions.
Do not give untrusted PR jobs tenant credentials, publishing tokens or writable
shared caches. Use disposable workers and read-only tokens where possible.

The standard bootstrap and capability-contract tests are automatically included
by the existing parent security regression discovery. They protect optionality,
identity preservation and rejection behaviour; they do not replace scanners or
native permission tests. Keep module release qualification separate from this
small source change.

## Lean release evidence

Build the selected module once. Record exact source and policy revision, dependency
lock digest, tool/model identities, executed checks, artifact digest/SBOM and
verification result in one receipt. Sign/attest through a qualified available
provider when supported. A JSON provenance file or checksum alone is not a trusted
signature. Never claim GitHub attestation functionality available to a private
free-tier repository without checking that entitlement.

Reuse the same verified artifact for promotion; do not rebuild a different package
after approval. Store only necessary artifacts with short retention. Exclude raw
data, logs containing payloads, private connection settings and scanner findings.
Cross-repository source admission includes an explicit licence/privacy review;
a private destination does not authorise copying all historical content.

## Where portability should live

Keep substantive checks in the existing repository commands and locked tools;
GitHub/GitLab YAML should provide runners, scope, credentials and result handling.
Preserve full applicable integration gates at release. During development select
affected tests and cancel superseded runs; batch dependency updates and reduce
duplicate installs rather than dropping security checks. Publish a final stable
required result even when an unrelated optional module is not selected.

Priorities for the suite CI track:

1. Qualify the newly wired offline Presidio range gate in the hosted privacy job,
   including model integrity and failure/egress controls. The source now includes
   this stage in the required context; hosted execution remains unverified. Retain
   the narrow hash-verified PyYAML source-build exception on Python 3.15 Linux.
2. Deduplicate current shared security/lock setup while retaining the six protected
   contexts until an explicitly reviewed protection migration is complete.
3. Add exact-SHA portable receipts and controlled runner execution; qualify malicious
   fixtures, XML/archive boundaries and secret/PII rejection, not only happy paths.
4. Separate PR validation from release/publish identities; test that fork/untrusted
   jobs cannot obtain deployment credentials or contaminate release caches.
5. Promote new scanner/runtime candidates only after their rejection behaviour and
   real repository coverage are verified. Newer version numbers alone are not
   evidence of stronger protection.

## GitLab: useful optional route, with limits

At this review, GitLab Free has capped hosted compute (400 minutes/month), Free
push mirroring, paid pull mirroring, and paid native CI integration for external
GitHub repositories. Self-managed runners avoid that hosted-compute quota but
have their own operating/security cost. Check current terms before committing
to a hosting arrangement:

- [Compute usage](https://docs.gitlab.com/ci/pipelines/compute_minutes/)
- [Repository mirroring](https://docs.gitlab.com/user/project/repository/mirror/)
- [Push mirroring](https://docs.gitlab.com/user/project/repository/mirror/push/)
- [CI for external repositories](https://docs.gitlab.com/ci/ci_cd_for_external_repos/)
- [Runners](https://docs.gitlab.com/ci/runners/)

The immediate recommendation is to keep GitHub as the maintained source and make
checks portable. GitHub currently documents a USD 12 monthly shared compute allowance
for Free accounts. At USD 0.006 per minute this covers 2,000 minutes on a standard
two-core Linux runner if no other eligible usage consumes the allowance; actual
coverage depends on runner and workload. Self-hosted runners have no Actions usage
charge, but you still operate and pay for the machine. GitLab Free's 400 hosted
minutes is not a larger free compute pool. A controlled runner attached to GitHub is therefore
the first option to qualify before introducing another repository. See
[GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
and [runner responsibilities](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners). If GitLab provides operational value, use one explicitly approved private
secondary project and a controlled source-transfer route. GitLab Free does not
supply an automatic native pull mirror of GitHub.

An ordinary private GitLab project can receive reviewed exact commits through
normal Git push and run its own pipeline. Transfer a selected branch with explicit
refspecs after destination/privacy checks; avoid `git push --mirror`, which can
publish unwanted refs and delete remote refs. Use narrowly scoped credentials
outside URLs/source, verify the destination remains private and never synchronise
operational archives, secrets or all old private history by default.

For a GitLab-authored change, return its reviewed commit to a GitHub feature branch
and open a normal PR. A GitLab success is **not automatically** a passed GitHub
required check. Any future status bridge must authenticate the trusted pipeline,
exact commit and policy/tool versions; prevent replay and untrusted status writers.
Do not add a green status merely because a log says tests passed.

If GitLab later becomes canonical, Free push mirroring can keep GitHub as a passive
downstream. That is a separate topology decision: stop concurrent authoring on the
mirror and reconcile branch protection, issue/PR ownership and releases. Avoid
bidirectional authoring and force pushes as a conflict-resolution strategy.

No GitLab destination, credentials, mirror, runner or status bridge is configured
by this change. The existing private-destination allowlist must be deliberately
extended and qualified before any source transfer; do not bypass it with another
client. Switching hosts alone does not solve the currently blocked protected merge.
