# N03.01: reference-to-native register inventory

24 September 2026. Inventory deliverable complete; runtime parity NOT complete.
Source baseline: careops-decisions commit acc135465bb0007f03256267c12da1628c515f98
(merged #21 after #20 and #19). Source review and CI receipts are in the linked
[journal closeout](journal-source-closeout-20260924.md). This inventory records
implementation gaps rather than treating source tests as tenant acceptance.

## Inspected source boundary

All following paths are in careops-decisions at the baseline commit:

| Source | Actual role |
| --- | --- |
| reference/credentialing_register.py | Immutable reference history, explicit supersession and viewer/time/currentness projection. Not an authentication service. |
| reference/register_codec.py | Strict versioned canonical JSON; rejects missing/unknown/ambiguous fields. Decoded confirmation is an untrusted claim. |
| reference/register_store.py | SQLite transactional persistence and integrity/recovery qualification for synthetic tests ONLY. |
| powerplatform/native/RegisterSchema/RegisterSchemaPlan.cs | Official SDK metadata construction, not executed provisioning. |
| powerplatform/native/RegisterSchema/DecisionAppend.cs | Complete immutable SDK storage intent, native expected version and exact business-field replay comparison. Not authority. |
| powerplatform/native/RegisterSchema/RegisterJournalAppender.cs | Caller/transaction-consistent journal staging, conditional root update and no writes on an old exact receipt. Not an exposed handler. |
| powerplatform/native/DataverseIdentity/CallerResolver.cs | Caller-scoped canonical person resolution; current mapping/index/security still require tenant qualification. |
| powerplatform/native/DataverseIdentity/ReadCredentialingRecord.cs | Actual IPlugin source for a bounded recorded-data read. Not registered in a tenant. |
| powerplatform/native/Authority/DelegationGate.cs and ProfileChanges.cs | Exact-content authority predicates and immutable before/after review under trusted host facts. Not source approval or authentication. |

Source link root:
https://github.com/edithatogo/careops-decisions/tree/acc135465bb0007f03256267c12da1628c515f98

## Parity matrix and remaining acceptance

| Invariant | Reference behavior | Native source at baseline | Required before native acceptance |
| --- | --- | --- | --- |
| Record ownership | Practitioner/profession/facility cannot change under one record ID. | Existing record GUID and source-reference fields; journal cannot create a root implicitly. | Protected creation/identity mapping and rejection of changes to root practitioner/profession/facility; no UI-only reliance. N03.02/.04. |
| Human decision and authority | human_confirmed must be literal true, but reference documentation requires trusted verification outside the model. | Exact source/case/authority references and hashes; separate native delegation/caller components. | Protected handler must resolve and bind all facts to an actual authorised human decision. A passed constructor, account or hash is not proof. N02 and N03.04. |
| Strict complete payload | Codec requires exact versioned fields and explicit condition arrays. | Intent rejects extra/missing fields, unsupported states, malformed text/hashes and ambiguous times. | Reviewed mapping of structured conditions to native representation, including explicit-none versus unavailable. N03.03/.04/.06. |
| Exact replay | Same decision ID plus identical canonical revision is harmless; changed content rejects. | Bounded ID query; exact match returns old receipt without rewriting current root. | Actual SDK round-trip fidelity for empty/null fields and time precision; never infer missing restrictions mean none. N03.06. |
| Version conflict | Reference uses total immutable-history length; SQLite applies a transaction around that check. | Per-record native row version plus sequence, with IfRowVersionMatches. This is semantic, not byte-for-byte, parity. | Actual competing writes, lost responses, duplicate IDs and missing/inactive indexes; prove native transaction behavior. N03.05/.06. |
| Latest supersession | Each later revision explicitly supersedes latest for that same record. | Root sequence/pointer checked; predecessor row must match the same record and expected sequence. | Direct-write protection, immutable prior rows and actual native relationship/history tests. N03.03/.04. |
| Recording chronology | Reference rejects recorded_at before the preceding revision. | Journal currently checks predecessor identity/sequence, not its recorded-at chronology. | PRIORITY: trusted server-time chronology guard and regression/native tests before releasing writes. Retrospective effective dates are a different concept. N03.03/.04. |
| Future-effective changes | Reference selects only revisions whose recording and effective instants have arrived. | Schema distinguishes latest/recorded/effective/projection times; staging invalidates projection-as-of instead of replacing scope. | Implement and test native current-scope projection across future, expired, suspended and revoked decisions. A latest pointer is not current authority. N03.03/.08. |
| Currentness | Expired verification gives currentness-unverified, not a new approval/revocation. | Nullable source verification fields and explicit unavailable read fields; staging clears projection currentness. | Verify stale-data presentation and approved recovery behavior in every UI/API/export. N03.07/.08. |
| Access and minimisation | Reference accepts trusted viewer role, profession, facility and own-record limits. | Caller-scoped read allowlist; restricted evidence kept outside operational projection. | Actual row/team/column/purpose roles and cross-profession/facility/own-record API/search/export tests; no claimed role parity from SDK mocks. N03.07. |
| Atomic persistence | Synthetic SQLite transaction combines history, sequence and digest checkpoint. | Journal uses an existing native transaction, conditional update and propagates every SDK failure. No durable outbox yet. | Native transaction/rollback tests, same-transaction final projection/outbox and protected service binding; no independent ServiceClient that bypasses ambient transaction. N03.05. |
| Corruption and recovery | Synthetic store validates sequence, canonical payloads and digest chain; missing store does not appear empty. | Schema/history/read guards, but native recovery not executed. | Dataverse backup/restore and separately protected SharePoint evidence reconciliation, missing-history detection and restart tests. Lists/OneDrive is not a database substitute. N03.10 and N10. |

## Platform and trust distinctions

Full Dataverse remains the production system of record. The native code has no
SQLite production dependency. Keep the Python/SQLite tests as synthetic invariant
oracles, not production services or proof that Dataverse behaves identically.
Canonical Python JSON and native SDK entities are different representations;
never interchange their receipts or treat different hashes as equivalent without
an explicit versioned mapping. Domain validation is not legal-source validation.

The journal receives a service from the protected host. That host must resolve
IOrganizationServiceFactory from the current native execution services and create
an explicitly caller-scoped IOrganizationService. Matching WhoAmI is necessary
for caller consistency but does not prove transaction participation or a human
click. An independently constructed client is not an approved substitute.

The existing caller/read source was already merged before #20/#21. This inventory
does not claim those older components were newly implemented in this delivery.
The no-admin synthetic Lists and connector-free Flow routes remain independent;
no operator needs a new app ID or Dataverse to use those documented rehearsals.

## Inventory acceptance and follow-through

N03.01 asks for an inventory and parity matrix, not full implementation of every
row. This file supplies that deliverable, includes exact source baseline, records
the synthetic-only SQLite boundary and identifies remaining owners/tasks. Source
review occurs through the containing PR and its recorded date/checked head. A green
planning check validates structure only; it cannot certify the conclusions.

Do not close N03.03 through N03.10 or archive the parent track from this inventory.
Next native work should address the recording-chronology and storage-fidelity gaps
while composing the protected decision handler, then native projection/outbox,
security and real sandbox acceptance. No existing test or gate is relaxed.
