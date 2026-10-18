# N03 recording chronology and event source closeout

24 September 2026. Sanitized archive of completed source slices only.
Programme careops#160; parent N03 remains IN PROGRESS. No tenant deployment.
This supplements, rather than rewrites, the #21 baseline parity inventory.

## Sequence and verified test evidence

| Slice | Final checked head | Merge commit | Executed qualification |
| --- | --- | --- | --- |
| Decisions#22: recording chronology | 6562823842e0a3da0be8a789dc09db3c45447b3f | 3cbab2f4d433339253ff4ab3e43d6f6b499a55d7 | 101/101 tests, 214/214 library lines, 204/204 branches |
| Decisions#23: native event journal | 9489bf736fd76ce1bd5e7c5779405e08f6a7d4ac | 70a091ba26232618b15ade3a33eb3d5152ec4c3d | 141/141 tests, 308/308 library lines, 246/246 branches |

#22 was based on #21 at acc135465bb0007f03256267c12da1628c515f98; #23 was
opened directly on #22's reviewed merge. Final base/head and all six applicable
PR workflows were checked before each exact-SHA squash merge. No existing test,
threshold, dependency lock or compiler/analyser gate was reduced.

For #22 the successful runs were Register35983397155, Identity35983397172,
Calendar35983397354, Authority35983397108, Reference35983397714,
Validate35983397122. Artifact10801600084 was downloaded and its TRX/Cobertura
parsed, with SHA256 verified:
8f0f104431079bac4cf133483febbf0ad50dd419bb1d3ac0daa4dee1a248f0ef.

For #23 the successful runs were Register35984542745, Identity35984542603,
Authority35984542663, Calendar35984542636, Reference35984542868,
Validate35984542870. Artifact10801936222 was downloaded and its TRX/Cobertura
parsed, with SHA256 verified:
1d653cd59a55b1226e0f61cce27cbf0c48d7be636ae5f55d30a2beecb3bf34a4.

Tests executed without skips. Coverage is for the stated register library, not
the whole credentialing application. The tests use official SDK objects and
controlled fake services; no actual Dataverse transaction or rollback is claimed.
Source review comments are recorded on the PRs, not independent clinical/cyber
or signed authority approval. No local .NET execution is claimed.

## Inventory delta: what changed

| Baseline gap | Source implementation now merged | Acceptance still open |
| --- | --- | --- |
| Predecessor recording chronology unchecked | #22 requires a present UTC predecessor instant no later than the new recording time, before any write. Equal instants use sequence ordering; legal effect stays independent. | Trusted server timestamp, native precision/range/round-trip tests and approved legal counting rules. |
| No durable event component | #23 constructs a Decisions-owned event schema and stages one minimal envelope with the same transaction-bound service as the decision and root version update. | Actual native table/key provisioning, transaction participation, forced-failure rollback and protected endpoint. |
| Replays might be misused to resend | Exact historical events reconcile without writes. Missing/altered/ambiguous events fail visibly rather than creating a new event. | Restore/backfill reconciliation and per-consumer acknowledgement/idempotency policies. |
| Downstream failure isolation | Immutable event is the native handoff boundary. No shared mutable delivery status, recipient or narrative is embedded. | Independently resumable consumers, authenticated minimum-data access, bounded retries, dead-letter recovery and cancellation of obsolete actions. |

No other row of the historical baseline matrix becomes complete by inference.
In particular, identity/role resolution, complete human approval evidence,
immutable root ownership, source/current-scope projection, direct API security,
null-versus-empty restrictions and native recovery remain explicit requirements.

## Review corrections and limits

#22 extends predecessor fixtures/allowlisted columns and adds nine chronology
cases; existing history/replay and exception assertions remain. Recording order
is not a policy that prohibits lawful backdated or future-effective decisions.

#23 adds 40 test cases. The first CI run rejected a constant-array allocation
under CA1861. The analyzer remains enabled: a private static key source is cloned
for every SDK metadata object, with a regression showing one caller cannot alter
future plans. Fresh-object isolation and original key meaning are preserved.

The event envelope contains nine fields: canonical event name/key, type/version,
origin organization, record and decision references, sequence and original
recording instant. No scope text, evidence papers, personal details, recipients
or instructions to approve/send are copied. Identifiers remain restricted data.
Native schema auditing and required flags alone do not enforce immutability or
server-side integrity; access and write controls still require implementation
and native qualification. No consumer or correspondence is installed/enabled.

Failure of the single authoritative transaction must roll back its writes.
After commit, a failed consumer must retry its own task, not the credentialing
decision or another consumer. External exactly-once effects are not guaranteed
by a Dataverse key. Recovery must reconcile retained external receipts first.

The no-admin Lists/connector-free Flow pilot remains independent, synthetic and
unchanged; no app ID, administrator role or additional module is introduced for
its operators. Full Dataverse remains the production target. No actual scope,
live register, signed CHHHS delegation, licence, privilege or CGov change occurred.
