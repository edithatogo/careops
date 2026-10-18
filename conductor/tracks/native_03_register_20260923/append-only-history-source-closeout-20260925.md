# N03 append-only history: reviewed source closeout

25 September 2026. Source implementation complete for the slices below.
Full N03 remains IN PROGRESS. No tenant registration or guard activation occurred.
Sequence: Decisions#33 -> #34 -> #35 -> this portfolio closeout.

## N03-H01: final decision/event mutation denial

Decisions#34 merged at b5f95396fa06356cc4473dd64d2e025d0a264a15, directly
on #33 at 2c8703ec1a6d7da07e6930c64d2453e08d2860eb. Exact tested head:
7389b823edf24afed8b621d56ab38627d5f5f7fd.

RejectHistoryMutation is actual terminal IPlugin source. It rejects Update/Delete
of final decision/event rows when registered on the exact four intended bindings.
It does not read services, identities, exemptions or private history. The companion
factory generates only disabled synchronous PreValidation registration metadata;
no Create or operational-register binding, images, filtering or impersonation.
New corrections append a separately authorised superseding decision. Consumer
checkpoints remain outside the immutable event, so retries do not rewrite history.

All seven exact-head workflows passed: Register36068394467, Identity36068394408,
Authority36068394576, Calendar36068394453, Card36068394549, Reference36068394558,
Validate36068394444. Actual artifact10837635378 was downloaded and its SHA256,
TRX and Cobertura were checked:321/321 tests,zero skips,568/568 register-library
lines and626/626 branches. Nineteen cases added. Artifact digest:
23872e2eb28ad3c7d9d21db0ef1292b6221c7497f6dc530b4c79630c0bee1824.

Review covered the deliberately unconditional handler, exact scoping metadata,
non-identifying faults, disabled state, object isolation and SDK serialization.
No unresolved inline finding returned. Old tests, locked dependencies, compiler/
analyser warnings-as-errors and full-library thresholds were not weakened.

## N03-H02: complete active-configuration inspection

Decisions#35 merged at beeb0fd1ba7062e7005c61d2bddd71e39c766558 directly
on #34. Exact tested head:698748f91afef849584ba564d460ee4c89e0c349.

HistoryProtectionInspector performs bounded read-only SDK inspection under an
existing approved connection. It checks WhoAmI, the qualified type, and four
unique active decision/event x Update/Delete bindings with exact native filters,
rank and runtime settings. Disabled/extra/broader registrations are not hidden
by query filtering. It detects forbidden configuration and images through ID-only
existence queries, without retrieving their potentially sensitive/large contents.
The return contains immutable observed step IDs, not authority or deployment approval.
No automatic configuration repair, enabling, messages or per-case calls are added.

All seven exact-head workflows passed: Register36069066115, Identity36069066112,
Authority36069066160, Calendar36069066155, Card36069066171, Reference36069066163,
Validate36069066159. Actual artifact10837740785 was downloaded and its SHA256,
TRX and Cobertura checked:361/361 tests,zero skips,628/628 register-library lines,
702/702 branches. Forty additional cases. Artifact digest:
95eb67d76f776a1af0356756c72d29ad0a71eeef2df419b148682d90164f5467.

Review checked matrix completeness, exact references, strict active/unknown values,
query bounds, missing-pair-with-four-rows regression, minimal reads, immutable
results and generic faults. No unresolved inline finding returned. No package,
prior test or test gate changed. Both PRs were reviewed at their exact heads and
merged only after their applicable workflows passed.

## Acceptance limits and follow-through

Tests execute actual .NET/SDK code with synthetic metadata/services, not a real
Dataverse tenant. Full stated-library coverage is not whole-application coverage,
clinical assurance or independent cyber review. The metadata inspector is not an
atomic snapshot, assembly-provenance verifier, future stability guarantee or
proof against privileged bypass. It must supplement actual prohibited-operation
and recovery tests, not replace them. Active guards are not evidenced here.

All in-place updates of final rows, including administrative ownership changes,
are blocked by the proposed terminal guard. Before enabling, implement approved
ownership at creation and controlled access administration; do not accidentally
create a need for credentialing staff to repair ownership case by case. The full
human/case/source/delegation-bound creation path remains open. Preserve the
existing no-write exact-retry route instead of switching to Upsert.

App-level deletion denial is not indefinite retention. Approved records disposal,
legal-hold handling and controlled migration/correction designs remain required.
No generic bypass flag or temporary disabling is supplied as their substitute.
Native single/nested/bulk/Upsert/state/assignment/cascade behavior, all four active
registrations, access/bypass permissions, null/empty/time fidelity, native rollback,
backup/restore and workbench acceptance remain separate gates. Do not archive
N03 or authorise deployment from these source slices.

The no-admin Lists/connector-free Flow/fixed-browser pilots are independent and
unchanged. Full Dataverse remains the target. No new Entra application, tenant
privilege, practitioner record, clinical scope, paid service or CGov arrangement
was changed. These controls add no ordinary clinician form or approval queue.
