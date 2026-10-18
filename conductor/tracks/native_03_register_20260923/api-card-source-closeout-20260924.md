# N03 API definition and register card: source closeout

24 September 2026. Completed source slices only; full N03 remains IN PROGRESS.
No tenant registration, live credentialing record or operational authority changed.

## N03-R01: native definition for the existing read API

Decisions#28 follows #27 and is merged at
21bb8273da7e421fc2516e12529a000e4acb8c7b. Final reviewed head:
0f8770b589975360c1c2d6988fcec2e7a2d93c06. All six workflows passed:
Identity35992517882, Register35992517936, Calendar35992517873,
Authority35992517794, Reference35992517992 and Validate35992517899.

Actual downloaded artifact10805145684 has SHA256:
dcf8f080ca1c5844f69d486ab813701b49d3afad7dfa86118eb73f07c6816a0d.
Parsed TRX/Cobertura: 144/144 Identity-library tests, zero skips, 201/201 lines
and 214/214 branches. This adds 24 definition tests; the other module suites
remain intact. Full coverage is for the named library, not the entire app.

The native factory constructs a single SDK deep-create definition for the current
scope-read plug-in and ten typed response fields. It requires an inspected exact
plug-in type and a named existing execute privilege; blank privilege cannot become
an unrestricted default. It adds no role, identity/time input or second endpoint.
Private metadata is explicitly not authorization. It constructs requests only:
real package/privilege provenance, native execution and permission/response tests
remain gates. No external package or existing safety check changed.

## N03-R02: read-only scope card and fixed synthetic preview

Decisions#29 stacks directly on #28 and is merged at
88e44563b0645a50c88a6e670341c2ea8c4b4a17. Final reviewed head:
dcfe4310ea33e452c0851c4bf3c74b36320b42fe. All seven workflows passed:
Card35994804683, Identity35994804624, Register35994804719,
Authority35994804596, Calendar35994804554, Reference35994804564,
Validate35994804634. Source is in Decisions at:
`powerplatform/src/app/credentialing-register/`.

The card is a read-only HTML/CSS/JavaScript web-resource source component, not a
new case form or approval queue. It displays recorded status, source currentness,
as-of UTC time, scope, full conditions/supervision and validity separately. It
never presents green practice clearance. Exact record/response/status validation
preserves all seven fractional UTC digits and rejects missing restrictions rather
than treating them as none. Narratives render as text, not executable markup.

Refresh removes the prior snapshot immediately. Generation checks discard stale,
disposed or timed-out responses; invalid rebinding clears the old record first.
The 15-second display timeout does not claim transport cancellation or retry.
There is no browser persistence, telemetry, privileged fallback or write. The
same controller handles manual refresh without accumulating click handlers.

The additional visual preview has four fixed SYNTHETIC scenarios: recorded scope,
revocation with stale source verification, expired grant, and missing conditions.
It has no upload, real-data entry, Dataverse dependency or new Entra application.
Its connection policy prohibits external connections; it is not a live register.
Existing no-admin Lists/connector-free Flow routes are independent and unchanged.

## Actual browser evidence and review fixes

Downloaded artifact10805288306, SHA256:
01d99c8971c85b0fcd1affd0e8684cd3fec70c98b43d3a562b33067b48b9911e.
Parsed Node report: 24/24 tests, zero failures/skips; 100% line, branch and function
coverage across both product JavaScript files. Pinned Node24.21.0 and test-only
Playwright1.63.0 executed on hosted CI. Actual Chromium153.0.8010.12 checked all
four scenarios, keyboard refresh/focus, 375px layout without horizontal overflow,
no page errors/external requests, and the unbound page's disabled refresh state.
The successful browser receipt and screenshot were inspected, not inferred from
unit tests. These are synthetic browser tests, not a Microsoft tenant or assistive-
technology certification. Local browser navigation was blocked by environment
policy; no local browser success is claimed. The README's 23 local tests describe
the initial baseline; the final hosted suite has the additional timer regression.

Initial CI and automated review found a missing GUID group in the pushed pattern.
It was fixed to the full canonical shape without relaxing negative checks. Real
browser smoke then failed despite Node passing; native timer functions now retain
the Window/global receiver and a dedicated regression covers that requirement.
The final browser test passed after the fix. Failed-browser diagnostics are
retained when needed, and no browser or coverage gate was skipped. The inline
review finding was answered and resolved; final source review preceded SHA-bound
merge. No independent clinical/cyber approval is implied by those source reviews.

## Remaining acceptance and next integration

The read API definition and card are source, not registered/installed native
components. Qualify the approved package, actual handler and privilege, native
SDK/Web API response (including nullable Entity and exact date/text representation),
record/tab lifecycle and caller row/column/export rights. Front-end checking is
not an access-control boundary. Preserve all current signed CHHHS source/delegation,
write-handler/direct-CRUD, genuine native concurrency/storage/recovery and local
clinical/cyber gates. Full workbench and representative-user/screen-reader/zoom/
contrast acceptance remain open. The preview must not be promoted to live data.

Use the supported form getContentWindow/client API path and one same-user executor,
not unsupported DOM or independent credentials. A snapshot is not a continuous
safety alert; any future caching/refresh needs journal, source and temporal
invalidation. No automatic applicant return or downstream notification is enabled.
No paid service, permission, scope, live record or CGov contract was changed.
All 12 tracks/120 tasks and historical receipts are retained. Archive these
completed source slices, not the unfinished N03 or N07 operational track.
