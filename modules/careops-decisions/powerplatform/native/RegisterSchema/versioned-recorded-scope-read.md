# Version-checked recorded-scope read

24 September 2026. N03.07/N03.08 source slice, directly after Decisions#24 at
394845ecad88fc9967163da9808ad4bc2e7cfb9c. No native endpoint is registered.

RecordedScopeReader composes the complete-history reducer with actual SDK reads.
The protected host supplies an explicitly caller-scoped service from the current
platform factory, after resolving the actual person and approved access. Reserved
API context, exact bound target and WhoAmI identity/organization must agree. This
is consistency validation, not a replacement for authentication or a delegated
human decision. The code never constructs an elevated client or supplies SYSTEM.

The adapter reads only the register's latest sequence/pointer and verification
interval, freezes those values and the native row version, then requests one
bounded ordered history page. It validates every history row through the reducer,
freezes the minimum necessary result, and re-reads the root. Any changed version,
sequence, pointer or source interval rejects the result. A corrupt/missing root
or partial/restricted history cannot become a clean empty register. Even an
apparently empty record is queried for orphaned history.

The history request uses PageInfo Count=257 and PageNumber=1, no TopCount, total
count or joins. The reducer accepts at most 256 complete rows; any continuation,
truncation or mismatch fails rather than appearing complete. Larger histories
need a separately qualified pagination/checkpoint design. Queries retain only
minimum columns and an explicit ascending sequence order.

The returned immutable result includes the observed root version, projection
instant, source verification interval and recorded status separately. Reading
never renews that interval or updates scope. Currentness-unverified does not erase
a known recorded revocation. Results are always recorded data, not clearance.
No browser-supplied date, actor, scope or source claim is accepted by this route.

This is NOT a database snapshot-isolation guarantee. It relies on immutable
history and all authorised changes atomically advancing the root version. Direct
CRUD, privileged bypass, native timestamp/null fidelity, mapping and read/export
permissions must be secured and tested in the actual Dataverse environment. A
successful mock service cannot certify those deployment assumptions. The intended
outer handler must normalise errors without exposing record existence or private
fault details, and must not present a previously cached result as a fresh read.

All faults escape without retries, writes, messages or fallback to partial data.
No new packages, user forms, approval queues or manual reconciliations are added.
Tests use native SDK request objects and synthetic services; they verify query
bounds, exact versions, result isolation and failure propagation, not native
Dataverse security/concurrency. Existing locked restore, warnings-as-errors,
no-skip tests and whole-library coverage gates remain unchanged.

Still required: protected endpoint/registration and caller-role binding; native
read consistency and security tests; explicit-none storage representation;
Power Apps presentation and human acceptance. The no-admin Lists/Flow pilot is
unchanged and needs no part of this full-app adapter. No tenant, signed delegation,
app registration, live record, licence or CGov contract is changed.

Microsoft primary sources checked 24 September 2026:
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/org-service/queryexpression/page-results
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/optimistic-concurrency
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/org-service/entity-operations-retrieve
