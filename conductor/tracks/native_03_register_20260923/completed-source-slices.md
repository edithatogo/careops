# N03 completed native source slices

24 September 2026. Sanitized source closeout only; full N03 is IN PROGRESS.
No actual Dataverse tables, Custom API or plug-in registration were performed.

## N03-S01: SDK register schema construction

After Decisions#15 then #16, Decisions#18 merged at
a758c9f26fc465bd3dda58964df3d38d388fb4f4. Final inspected head
9507a31574193e8d3f9a09344e0294a2e485ba54 passed every applicable workflow:
Schema 35878169177, Delegation 35878169327, Calendar 35878169196,
Reference 35878169220 and Validate 35878169258. The base remained #16's merge
8bf56acbc16d2add7f27f75c94e6e66a88656479 at final review.

Actual downloaded artifact 10759845520 from run 35878169177:
13/13 native .NET Framework 4.8 tests, zero skips; 91/91 builder lines and
4/4 branches covered. SHA-256
1977a6dc119f4bca52d4843d1031ab8299a293e7eacc333464cf340a4cb66d40.
TRX and Cobertura were independently parsed, not inferred from the PR description.
Both final dependency locks match the actual initially resolved graph. Source
review was recorded, not claimed as independent clinical or cyber acceptance.

The native SDK constructs 42 ordered requests: two standard user/team-owned
tables, 34 columns, three internal non-cascading/restricted-delete relations and
three canonical/sequence keys. Published-metadata inspection requests are also
provided. The factory has no service client, execution method, credential, live
case input or sibling table dependency. SDK data-contract round trips are tested.

The existing manifest is authoritative for the source solution name and publisher:
`decisionsworkspace`, `dft`, option prefix 60217. A review corrected a folder-name
case assumption and added an actual-manifest consistency regression. Ambiguous
type and assertion-analyzer errors were fixed without disabling checks. Committed
artifact-derived dependency locks; final restore is locked and rejects drift.
Compiler/analyzer warnings and whole-builder coverage requirements remain strict.

## N03-R01: caller-scoped recorded-register read, part of N03.07

Decisions#19 merged at 12457472bbee4d916afffe35bf0b2c0fbb0a8bc5, directly
on caller-binding #17 merge 4f8f9d1505a605d0ece954f9a91bb367a5d81be0.
Final checked head fa8635aa77c9963effcecb3089a60314026cfd64 passed:
Identity/read 35884061646, Schema 35884061627, Authority 35884061593,
Calendar 35884061591, Reference 35884061602 and Validate 35884061669.

Downloaded artifact 10761562580 from the final identity/read run was independently
parsed: 94/94 tests (37 added), zero skips;109/109 combined-library lines and
150/150 branches covered. SHA-256
bad731cb80f2a6d0d8a1d9e46ccfe8f90b087e12e62fd20fda15f56a7f57e437.
Both actual locks were compared with #17's graph and are unchanged. No new NuGet
package or sibling runtime dependency was added. Tests compile actual IPlugin
and SDK code against simulated services, not Dataverse's security engine.

The handler requires its direct synchronous bound API context and one exact
record Target. It resolves the caller and retrieves only 16 projection fields
under the caller's access. It builds a fresh, typed/versioned entity rather than
passing through private attributes, related entities, keys or formatted values.
Expected access/SDK/time-out failures are non-disclosing and never trigger
privilege escalation or a retry. No writes or external communications occur.

ReadSucceeded means retrieval ONLY. A fixed disposition explicitly excludes
practice clearance. Missing/null/access-filtered conditions or supervision remain
UnavailableFields, never assumed no restrictions. Read time is separate from
source verification. Recorded revocations, unknown states and stale dates are
not converted to approvals. The complete underlying permission/validity model
still requires approved native integration; a row version is not authority.

Review added exact response-name completeness and an all-fields-unavailable case,
then fixed a strict nullable-test error by explicitly rejecting null names. No
checks or thresholds were weakened. Tests compare requested field names/types
against the current SDK schema, and response types against the source API contract.
The intended UI uses one existing register/workbench, not another review queue.

## Acceptance still outstanding

SDK construction/serialization and plug-in source are not a managed deployment.
Before provisioning, verify an approved sandbox and privileges, name collisions,
the source solution and actual plugin type/execute-privilege bindings. Use reviewed
ALM, not blind repeated creates. Read back native metadata, concurrency settings,
field security and Active key indexes; execute real permission/access tests.
IsPrivate is discovery control, not security. A user connection is not proof of
present human confirmation. No application/environment access is granted here.

The protected write API must enforce complete evidence, exact delegated authority,
server-side required fields, same-record supersession, replay/concurrency checks
and atomic event/history updates. Actual role/purpose/profession/facility/own-record
permissions and direct API/search/export tests remain open, as do SDK/Web API
response serialization, the Power Apps workbench, migration and recovery drills.
Current signed CHHHS instruments and native-user acceptance remain gates.

Only these source deliveries are closed. No-admin pilot source and full Dataverse
production target are unchanged. No signed authority, live scope, practitioner
record, tenant setting, app registration or CGov contract changed.
