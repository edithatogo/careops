# Fictional event-replay qualification — 27 October 2026

The queued portable Process replay increment is locally qualified on Python
3.15.1. It uses fictional facts and existing ingestion, OCEL, pipeline and
checkpoint APIs; no connector, tenant, mailbox, meeting or native flow is run.

## Behavior

- `facts_to_ocel` orders events by UTC timestamp then existing pseudonymous event
  ID, and objects by their existing pseudonymous ID. Late-arrival permutations
  therefore produce identical serialized logs. The HMAC inputs, schema version,
  source/object identities and original input records are unchanged. Ties have
  a reproducible serialization order; that order does not establish causality.
- Empty or whitespace-only source event/object IDs fail before pseudonymization.
  Missing or blank provider names remain errors. An absent optional provider
  contributes no invented event, binding or completion assertion.
- Duplicate event IDs in one batch, including conflicting duplicates, still fail
  closed. The adapter does not silently select a winner. The existing checkpoint
  suppresses accepted or tombstoned identities before batch conversion.
- Repeated tombstones are idempotent and consume one retention slot. Removing an
  accepted identity also removes its old retention-queue entry, so that entry
  cannot later evict a new acceptance of the same identity.
- A newly observed older fact does not move the checkpoint watermark backward.
  The adapter's explicit `after` argument remains an exclusive filter: facts at
  or before it are excluded. Automatic late-event recovery beyond that filter
  is not introduced by this increment.

The checkpoint remains an in-memory count-bounded model, not a durable native
store or a time-based retention guarantee. Once an ID leaves its configured
retention window, replay admission is possible. Retention policy, authorized
source partitions, provider identity namespaces, persistence, output-before-
checkpoint commit and recovery remain the selected connector implementation's
responsibility. This work does not qualify a native SharePoint checkpoint or
change any connector binding. No retry mechanism is added.

## Evidence and recovery

`tests/test_event_replay.py` adds 12 cases covering all six arrival permutations,
unchanged existing event-ID derivation, duplicate/conflicting batches, repeated
and expired tombstones, reacceptance, empty IDs, missing providers, source input
preservation and a provider-independent minimized pipeline. The RED control
reproduced seven failures before the fixes; 31 focused tests pass afterward.

The complete offline suite passed 1,753 tests with 10 existing capability skips.
Independent coverage gates passed: 96.24% line and 92.63% branch coverage.
Network access was blocked for this run. Lint, formatting and affected strict
Python type checks pass. Existing unrelated source edits were included as an
explicit baseline, preserved separately, and not attributed to this increment.

The task's exact additive patch and baseline hashes are retained in the parent
checkout's ignored `.local/process-event-replay-20261027/` evidence directory.
Only matching preimages permit applying or reversing that patch; unrelated work
must be retained. Existing native files, bindings and F06/F08 are untouched.
This is local source/runtime qualification, not hosted CI, merge, native
acceptance, production rollout or authorization for communications.
