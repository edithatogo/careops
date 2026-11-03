# Private publication-readiness continuation — 3 November 2026

Status: in progress. CareOps remains PRIVATE. Public release, visibility changes,
history replacement, purchases and weakening required checks are not authorised.

## Ownership and scope

- Writing chat: `01a187b1-348d-7042-9ca8-7d309c5f4de3`.
- Isolated source branch: `codex/zip-publication-20261103`, standard Git worktree
  named `careops-zip-publication-20261103`; base `d28e1c5`.
- Owned source: the two module `powerplatform_validation.py` readers, Clinical
  Hub `validate_solution_package.py`, and the parent ZIP-boundary regressions.
- Owned records: this additive note, its existing track link and exact inventory
  entries. The dirty rollout ledger and all other chat source stay preserved.
- Native scope: read-only GitHub source/history, hosting and retained CI evidence.
  No Microsoft operation, email, artifact deletion or visibility mutation.
- Bandit source is separately owned in PR242. Its completed exact review manifest
  promotion `d28e1c5` is retained; it does not certify all Bandit findings resolved.

## Authorised work

- [~] Fix all three unbounded ZIP entrypoints without weakening CRC/format checks.
- [~] Run focused positive and malicious-package regressions on Python3.15.1.
- [~] Complete frozen history, hosting, nested-artifact and CI-log privacy checks.
- [ ] Reconcile resulting source/head evidence and public-readiness decision.
- [ ] Pass required exact-head checks before protected integration. Entitlement
  and artifact-storage refusals remain blockers; local checks do not replace them.

## Initial evidence reused

Frozen source assessment `95bf9d9` retained675commits,244refs and2,874unique text
blobs. Full-history Gitleaks22candidates were reviewed as framework identifiers,
digests and synthetic fixtures. One historical workstation path is minor metadata,
not a credential. The focused security review validated a low-severity ZIP
resource-exhaustion family at three independent locations. A16,437byte fixture
expanded16,777,216bytes before package rejection. No remote endpoint was shown.
No confirmed credential or private clinical record was established by that
assessment; its personal-data and nested/log coverage was incomplete.

## Remediation design

Bound compressed input to64MiB, entries to10,000, each expanded member to16MiB,
aggregate expansion to64MiB and compression ratio to200 before opening members.
Reject duplicate/encrypted members before decompression. Read each member through
an explicitly capped stream; preserve complete-read CRC validation, existing
structural checks and sanitised failure diagnostics. The two independently
shipped module readers remain identical; the Clinical Hub package wrapper reuses
its module reader. These limits are software guardrails, not native acceptance.

Private raw findings, downloaded content and machine paths remain outside Git.
