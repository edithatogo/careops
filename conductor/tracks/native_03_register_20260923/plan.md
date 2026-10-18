# N03 plan: native persistent register

Owner: Decisions module maintainer, to be named. IN PROGRESS.
Updated 25 September 2026. Source qualification is not native deployment.
Detailed historical source receipts remain in the linked archives below.

- [x] N03.01 Inventory existing register invariants and native artifacts; accept a Python-to-Dataverse parity matrix and synthetic-only SQLite boundary. Evidence: native-parity-inventory.md (baseline source inventory, reviewed in CareOps#168 on 2026-09-24; not runtime parity), with dated deltas in the source archives below, including append-only-history-source-closeout-20260925.md and human-journal-recovery-source-closeout-20260925.md.
- [~] N03.02 Define practitioner/source IDs, profession, facility, scope and decision tables; accept data ownership, alternate keys and relationship/deletion rules.
- [~] N03.03 Add conditions, supervision, actual/recorded effective times and supersession history; accept no later revocation revived by an older/future approval.
- [~] N03.04 Implement reviewed Custom API/plug-in write boundary; accept exact decision/evidence/authority checks and blocked direct CRUD bypass attempts.
- [~] N03.05 Commit decision, history and durable event atomically; accept rollback on intermediate failure in an actual Dataverse sandbox.
- [~] N03.06 Enforce version checks and idempotent command keys; accept competing updates, lost responses, altered retries and repeated renewals without corruption.
- [~] N03.07 Implement authenticated profession/facility/own-record projections; accept direct API/export tests as well as UI tests with no hidden-field reliance.
- [~] N03.08 Separate last-recorded scope from source currentness; accept stale/missing/failed-source tests without invented approval or revocation.
- [ ] N03.09 Deploy/index representative synthetic volume and query views; accept measured latency, throttling and permission boundaries against N01 targets.
- [ ] N03.10 Demonstrate standalone install, native restart/recovery and migration-ready exports; accept Decisions-owned register package with no SQLite or sibling runtime requirement.

## Implemented source and preserved qualification history

| Decisions PRs | Source implementation | Detailed archive |
| --- | --- | --- |
| #18 / #19 | Native table/key definitions and original caller-scoped recorded-data read. Not installed. | [Initial source closeout](completed-source-slices.md) |
| #20 / #21 | Complete immutable decision intent, exact replay, transaction-bound staging and conditional root update. | [Journal closeout](journal-source-closeout-20260924.md) |
| #22 / #23 | Recording chronology; same-service journal/event staging; exact historical event reconciliation without resend. | [Event closeout](event-source-closeout-20260924.md) |
| #24 / #25 | Complete temporal history selection and version-guarded native read; no older/future grant revival after later revocation. | [Projection/read closeout](projection-source-closeout-20260924.md) |
| #27 | Single composed caller-bound current-scope IPlugin. Duplicate #26 closed unmerged. | [Caller-bound read closeout](caller-bound-read-closeout-20260924.md) |
| #28 / #29 | Privilege/handler-bound read API definition, read-only card and fixed synthetic visual preview. | [API/card closeout](api-card-source-closeout-20260924.md) |
| #30 / #31 | Automatic record/tab/section binding and real browser/iframe composition with synthetic native-form objects. | [Form lifecycle closeout](form-lifecycle-source-closeout-20260924.md) |
| #32 / #33 | Native root identity invariant and disabled registration with required minimal pre/post images. | [Identity invariant closeout](identity-invariant-source-closeout-20260925.md) |
| #34 / #35 | Final-history Update/Delete denial, exact disabled registration definitions and read-only inspection of all four active bindings. | [Append-only history closeout](append-only-history-source-closeout-20260925.md) |
| #36 / #37 | Explicit owner-bound confirmed intent and composed caller, root identity, human confirmation, delegation and journal checks. Trusted native-source resolution is not yet supplied. | [Confirmed writer and recovery closeout](human-journal-recovery-source-closeout-20260925.md) |
| #38 / #39 | Read-only own historical receipt and privilege-bound API metadata, with final root-access revalidation and actual reader/contract parity tests. | [Confirmed writer and recovery closeout](human-journal-recovery-source-closeout-20260925.md) |

Preserve the [historical reference-to-native inventory](native-parity-inventory.md).
Its gaps have dated source deltas, not retrospective claims of native acceptance.
The archives contain exact merge/head/run/artifact identifiers and historical test
counts. No earlier receipt was deleted by this source index.

## Latest source delivery

Existing Decisions#36 at 3978c179396bbab244e158982cb57f571a2612e3 supplied
owner-bound intent and full confirmation hashing. The existing draft #37 was then
reviewed, corrected and merged at 8034a7ce5ba62205e868ffbdbb8d48f0c5441e04.
It composes current canonical caller, exact confirmed content, native root identity,
owner-capable teams and delegation at confirmation/recording times with the existing
journal/event path, using one verified caller-scoped service. It is not a public
write endpoint or native source resolver. Its trusted HOST snapshots cannot safely
be supplied by a browser or agent. Source tests: 202/202 Identity cases, no skips,
278/278 library lines and 326/326 branches.

Decisions#38 at 82039faabf4ea2d5bc1101471d1c838cb6624a43 adds historical own
receipt recovery without repeating the decision. Current account and root/decision
access remain required, not renewed authority to approve again. Applied the review
finding with a final root access check and frozen response primitives; access loss
or malformed results clear output. An unavailable receipt does not mean a failed
save, and a historical outcome does not establish current scope. Source tests:
238/238 Identity cases, no skips, 338/338 lines and 430/430 branches.

Decisions#39 at ad5a0ccf0bd1a02f094732553e36b556c2a30c68 adds native receipt
API metadata with exact inspected handler, explicit existing privilege, required
DecisionId and nine primitive responses. Tests invoke the actual reader and compare
output names/types with the definition. No registration is executed. Final source
suite: 249/249 Identity cases, no skips, 383/383 lines and 458/458 branches.

All seven module workflows passed at each final head before merge. The source
archive records artifact hashes, review corrections and remaining gates. Existing
locked dependencies, tests and coverage thresholds remain. These are native
.NET/SDK tests with synthetic services, not native tenant or whole-app assurance.
The existing 44-test browser/card suite and its prior evidence remain unchanged.

## Next implementation and native acceptance

Finish the protected native source adapter and host: retrieve the original saved
human confirmation, approved outcome/ownership rules, current released delegation,
source evidence and verified role occupancy from protected native records. Prevent
concurrent withdrawal/rebinding between reading those sources and committing the
journal. Only then expose the composed core through an approved protected endpoint.
A constructor, account identity, caller-generated hash or metadata receipt alone is
not clinical authority. Direct Create and alternate mutation paths still need the
complete enforced boundary and native prohibited-operation tests.

The current core is the same-decision-maker recording path. Any administrative
recording-on-behalf pathway must explicitly retain the actual human decision-maker,
recorder and applicable authority rather than substitute impersonation or require
the original decision to be repeated. That separately governed source path is open.
Ownership is configured, not chosen as another technical task during clinical review.

Connect bounded receipt recovery to the existing save experience with its original
stable decision ID. Do not convert technical uncertainty into a new approval request,
automatically generate another decision, or treat a receipt as present clinical
scope. Actual API/execute privilege registration, source creation integrity, native
field/row/wire behavior, read-after-commit and access-revocation tests remain open.
The final root check is point-in-time revalidation, not an atomic permissions snapshot.

Terminal history guards intentionally block administrative in-place updates too.
Qualify ownership at creation and separate access administration. Implement auditable
corrections, records disposal/legal holds and legacy migration without assuming
indefinite retention or a generic bypass switch. Missing configuration is a technical
failure, not an adverse practitioner finding.

Qualify native null/empty/time-precision fidelity, active keys, registration/image/
bulk/Upsert/state/assignment/cascade behavior, bypass privileges and real rollback.
Read-only metadata inspection is non-atomic and cannot replace prohibited-operation
tests, signed release provenance, access control or drift monitoring. Required
guards left disabled cannot pass production acceptance.

Complete native packaging/standalone installation, actual API response and role/
record/export checks, assistive-technology/workbench tests, representative-volume
measurements and Dataverse/SharePoint recovery reconciliation. Version-guarded
reads rely on immutable history and atomic root updates, not snapshot isolation.
Temporal as well as journal/source changes must invalidate any future cache.
An as-of recorded snapshot is not continuing permission to practise.

All acceptance criteria above remain open until their named environment-specific
evidence and approvals exist. Current signed CHHHS sources are not certified by
source tests. No whole track is archived merely because source slices are complete.

## Pilot and workload boundaries

Full Dataverse remains the production target; SQLite remains synthetic-test-only.
The no-admin Lists/connector-free Flow/fixed-browser pilots remain independent
and unchanged. No new Entra app, tenant privilege, practitioner record, clinical
scope, paid service or CGov change occurred. No additional ordinary case form,
approval queue, per-case deployment check or recurring clinician task was added.
Close remaining tasks with executed native evidence, reviewer and date; archive
completed source slices only until full track criteria are met.
