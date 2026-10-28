# H2.3c — Source isolation and recovery rehearsal

Completed at **source-only scope**,28October2026. The41 fictional rehearsal cases
reuse the existing resolver, H2 compatibility adapters and F09 pure commit preview.
No persistence layer, new runtime, native H2-to-F09 bridge or action register was
introduced. H2.3c remains partial at the broader native qualification level.
H1-G01–03 and H2-U01–05 remain OPEN. No native call, change, flow invocation,
correspondence follow-up, email or publication occurred in this increment.

## Reuse and bounded correction

[`test_forum_recovery.py`](../tests/test_forum_recovery.py) uses the existing two
fictional forum profiles, adapter fixtures and commit-preview fixtures. Its
explicit forum/occurrence-to-F09 mapping is a test input, not an implemented
native binding. Approval, acceptance, source-access and recovery states remain
caller assertions, never authenticated evidence. No real governance approval is
created by the fixtures.

Five new regression cases initially failed: the pure commit preview returned
aliases to conditions, dissent, current/prior history and action particulars.
Editing one returned proposal changed its caller's inputs or a sibling result.
[`meeting_commit_preview.py`](../scripts/meeting_commit_preview.py) now deep-copies
its successful result, retaining equal values, schemas, keys, review/disposition
semantics and all existing blockers. The import audit explicitly allows the
standard-library copy helper while continuing to exclude I/O/auth/provider
imports. This source correction does not update a live flow.

Resolver, compatibility adapters, legacy preparation and F06/F07/F12 builders,
native bindings, canonical flow catalogue, connection references and manual
fallbacks are unchanged. No dependency, authority or deployment capability was
added. No source file is a native runtime proof.

## Rehearsal matrix and exact limits

| Case group | Source evidence | Qualification limit |
| --- | --- | --- |
| Overlapping operations | Nine synchronised worker calls exercise preparation, F07 candidates, full F12 validation and F09 previews for two forums plus two occurrences of one forum. Same-context results agree; contexts, shared baseline and caller data remain unchanged. | Actual source functions run concurrently; no connector, flow, shared native setting or native transaction is exercised. |
| Shared-result editing | Six synchronised previews share one input object; each result can be edited independently. Five targeted regressions cover conditions, dissent, action details and nested current/prior histories. | In-memory object isolation only; not native file locking or prevention of concurrent edits to the same document. |
| Future-effective roles | Adjacent revisions select the explicitly named chair revision at the start-inclusive/end-exclusive boundary; an out-of-period revision blocks. Prior immutable snapshot remains unchanged. | Role/source assertions remain unverified. A pinned historical snapshot is not automatically invalidated by a later catalogue or evidence change; native freshness needs requalification before use. |
| Wrong destination/context | Existing preview refuses a mismatching or unaccepted declared target. Preparation refuses another register; F07/F12 reject another forum/occurrence binding. | No actual allowed-audience lookup exists here. Mutually consistent false bindings cannot authenticate a destination, person or permission. |
| Duplicate/replayed input | Existing deterministic operation key plus supplied key history refuses exact replay, changed payload under an old key, and a prior key with a tampered destination binding. Different explicitly bound contexts have different keys. | The caller supplies history. There is no persistent replay ledger, atomic reservation, distributed lock or exactly-once native guarantee. |
| Unknown/partial outcome | Unknown, committed, conflicting, partial, missing and extra recovery declarations block. Declared absence after unknown yields only the same noncommitting preview. | No save was attempted, so no actual uncertain save or exact readback is reconciled. Supplied absent/committed values are not proof that a native record exists or is safe to retry. |
| Source drift/denial | Changed revision/hash and denied/incomplete/missing read declarations block the pinned preparation context. | No actual403, target permission, source availability or connector failure was exercised. Do not generalise the fictional declaration to native access. |
| Calendar lineage | Moved exceptions retain original start and explicit type; full F12 inputs retain current time, lineage and baseline. Cancellation blocks preparation without rewriting the source. | Single-instance F12 lineage remains unsupported as documented in H2.3a. No calendar edit, recurrence/run or attendee notification occurred. |
| Correction/history | Existing issued-wording guard refuses an unevidenced amendment; a separately declared correction produces a distinct preview/key while preserving previous source/output/history and another forum's inputs. | No historical native bytes, file-version restore, issued-record correction or recovery transaction was tested. The original preview remains unchanged in memory. |

## Residual native and policy gaps

These references track qualification still required; they are not additional
features or instructions to perform writes under the current scope.

- **H2-R01 — Authenticated routing, audience and access.** No H2 native operation
  bridge or verified audience policy is implemented. Keep source declaration checks
  separate from exact native source/destination/role permissions and authorised
  audience. Do not infer authority from an H2 profile or F09 fixture approval.
- **H2-R02 — Atomic replay/concurrency.** Identical concurrent previews intentionally
  produce the same deterministic key when no prior receipt is supplied. They do
  not reserve the operation. Any future native path must qualify existing record
  identity/concurrency controls and exact result reconciliation; never add a blind
  retry or assume an empty local history proves native absence.
- **H2-R03 — Unknown-result readback and recovery.** No native write/readback is
  authorised by this source rehearsal. Before any selected future replay, reconcile
  the exact target/key and full saved payload, identities, references and versions.
  Conflicting/partial state stays held; preserve prior source/output/human edits.
- **H2-R04 — Current bindings and immutable history.** Source snapshots and copied
  results are isolated, but native freshness, effective-role/source recheck, actual
  historical content restoration and concurrent live runs remain untested.

H2.3b's typed operator controls, bridge/save, intended-role access and rendered UI
qualification remain unpassed under H2-U01–05. H1 governance gaps are not waived.
H2.4 rehearsal/release and H3/H4 live forum use remain pending/unselected. Preserve
manual preparation; no production readiness, cutover or wider access follows.

## Tools, permissions and verification

Only local Git, the explicitly verified repo-local Python3.15.1 environment and
fictional offline tests were used. Existing standard-connector/native resources
were not contacted. No authentication/cache/permission change, new client,
Premium connector, Copilot, AI Builder or denied renderer workaround was used.
There is no new native mutation or notification surface.

Focused affected suite:189 passed, including41 new H2 source cases and unchanged
resolver/adapters/preparation plus the existing commit-preview cases. The initial
five failures and their failure-only rerun are retained privately, followed by the
complete focused result. Full offline module suite:1194 passed; parent
publication/package checks:8 passed. Privacy, secret and committed-archive results
are recorded in the private evidence receipt; do not upgrade these source checks
to native or operational acceptance.

See the [H2 contract and tasks](h2-forum-reuse-plan.md),
[H2.3b controls and gaps](h2-operator-configuration.md) and
[maintained Word/manual route](library-column-word-route.md).
