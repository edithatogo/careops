# Reviewed-contribution recovery

Use the existing record store, selected contribution contract and qualified CLI
session. This is a reusable procedure, not a new runtime or permission to process
real records. Native identities, raw receipts and operational results remain in
the private track.

## Bounded fictional check

1. Read the current source and target by stable list/item identity. Preserve their
   GUIDs, ETags, versions, complete stored fields and the existing record inventory.
   Keep actual work and human narrative authoritative in the target record.
2. Create an isolated fictional linked pair through the existing guarded route.
   Reconcile a failed create before attempting another. Preserve unrelated fixtures.
3. Prepare only the existing seven contribution metadata fields. Pin the exact
   target ETag, source revision, mapping revision and expected post-save revision.
   Do not use a wildcard ETag or copy clinical narrative, names or certifications.
4. Send the conditional update once. A test-only client exception after the native
   response can exercise caller uncertainty without changing the app or connectors.
   Preserve the first failure and single-send marker; disable mutation retries and
   redirects. Do not infer failure or success from the command exit code.
5. Before any retry, independently reread both canonical records. Compare identity,
   all seven expected values, exact expected revision and every preserved field.
   A request-scoped OData response identity may vary: compare the stable item ID
   and GUID, retaining any exact presentation exclusion in the private evidence.
6. Classify the result. An exact applied result requires **no retry**. A missing,
   conflicting, partial or changed result remains held for reconciliation; zero
   matches never grants permission to create again.
7. Read the complete scoped inventory, including pagination. Require exactly one
   matching contribution and unchanged unrelated records. Repeat the read-only
   check to establish that reconciliation added no revision or duplicate.
8. Recoverably recycle only the newly created fictional pair, child before parent,
   and read back the original inventory. Preserve raw evidence and original history.

## Evidence boundaries

Record separately the actual mutation, deliberate client failure, independent
native readback, duplicate/preservation comparison and cleanup. Reuse unchanged
passed checks. A local helper test is not native verification.

A post-response client exception proves that the selected CLI route can reconcile
a committed write after caller failure. It does **not** prove an actual lost network
acknowledgement, the unpublished app's error handler, concurrent-writer isolation,
or device/Teams behaviour. Keep any specifically required app-runtime case pending
until observed in that app; do not close it using this narrower result.

Keep existing workflows disabled. No publication, people, real data, delivery,
licensing, access changes or deadline configuration follows from this procedure.

## Unpublished-app recovery review

Qualify the app separately from the CLI case, using only an isolated fictional
pair. Preserve the original handlers and independent native preimages first.

- Clear any prior receipt before reconciliation, clear review acknowledgements,
  and disable the review write while reconciliation is uncertain or in progress.
- Handle each canonical refresh failure explicitly. An error in an earlier
  chained operation must not be followed by a receipt from cached records. Gate
  the lookups and receipt decision on successful refreshes of both sources.
- Require the selected parent/child identities, eligible source and target states,
  all seven metadata values and current revision pins. An uncertain-save receipt
  additionally requires the original review preimage and preserved human work.
  Matching status and two version fields alone is insufficient.
- With a supported, tab-scoped test interface, allow one fictional write to reach
  the server, then withhold its successful response. Block any further test writes
  before transmission. Require an app error/hold and independent native readback
  before selecting reconciliation. Never inject test logic into the production
  handler or invoke internal connector endpoints directly.
- Observe reconciliation in the actual app, then reread the records independently.
  Require no extra revision, duplicate, work change or narrative change. Test a
  conflicting metadata value while keeping otherwise valid revision pins; the app
  must refuse a receipt. Persistent read failure must clear the receipt and hold
  review. Retain connector retries and the initial failure, and remove all network
  interception in a finally block.

Record inconclusive probes explicitly: a short observation interval ending before
connector retries finish does not prove an error handler failed or passed. A
deliberately withheld response proves that bounded app recovery path, not every
spontaneous outage or recovery across a new session without the review preimage.
Reuse prior entry, conditional-field, source correction and create-recovery checks
only where their affected formulas and bindings are unchanged. Native final source,
saved-state metadata and fixture cleanup are separate closeout evidence. Physical
device, embedded rollout and later source adoption remain separately scoped.
