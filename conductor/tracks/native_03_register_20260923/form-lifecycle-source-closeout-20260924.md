# N03 form lifecycle and browser-composition source closeout

24 September 2026. Sanitized source archive, not an operational track archive.
Full N03 remains IN PROGRESS. Current signed CHHHS authority and native tenant
registration/permissions are not certified by these records.

## N03-F01: model-driven form binding, source complete

Decisions#30 is stacked on #29 (88e44563b0645a50c88a6e670341c2ea8c4b4a17).
Merge18a1348d6accde1e1dd6c7716ceed22ea4d035ed; final inspected head
2bcae7b878a033174037597034d298e5b4beb410. All seven workflows passed:
Card36006169449, Register36006169438, Identity36006169164,
Authority36006169366, Calendar36006169165, Reference36006169170,
Validate36006169228.

The form library binds the existing read-only card to the current saved record
using native form data/tab events and getContentWindow. It disposes earlier
sessions, clears old snapshots and guards late frame/native-response/body results
against record changes. Only the fixed bound scope-read action is constructed.
The existing native platform session is used; no custom app ID/token/HTTP fallback,
actor claim, record write, new case form or extra approval queue is introduced.

An automated review identified that control visibility can remain true inside a
hidden section. The code now verifies the containing section and configured tab,
with regressions. Final local20-test suite passed under Node22.16.0. Hosted
Node24.21.0 executes44/44 tests (20 added), zero skips, and named-source100%
line/branch/function coverage for form-binding.js,scope-card.js and preview.js.
The CI explicitly requires the new product file's coverage row; an empty report
cannot be accepted. Existing native checks and strict thresholds remain intact.

Downloaded artifact10810368957 SHA256:
e4ce6750b25e9d1039e49994a9486e0548c03b811e551ab24b229d4bf5ff283e.
The Node report, standalone browser receipt and source bytes were independently
inspected. The original browser smoke is only the existing four-scenario preview;
it is not described as composed form evidence. The next slice supplies that test.

## N03-F02: real-browser composition, source qualification complete

Decisions#31 is stacked directly on #30. Merge
54c0ee87700a6f8b1ae73e21b38fb63a592d596f; final inspected head
8c0c86991fa8a9b495f6f94a35e401ffd4e66498. All seven workflows passed:
Card36007756533, Register36007756543, Identity36007756546,
Authority36007756517, Calendar36007756475, Reference36007756467,
Validate36007756445.

Actual hosted Chromium153.0.8010.12 loads both delivered scripts across a real
iframe. Native form/tab/Xrm objects are synthetic facades with two fixed records,
not real platform authentication. Tests exercise automatic initial read, keyboard
refresh/focus, a held old response after changing record, hidden section/collapsed
tab, repeat initialization, actual iframe document navigation and disposed
hooks/output. No page errors or external requests were recorded. A375px-wide
viewport was used. The screenshot was inspected; full native/assistive-technology
acceptance is still required. All44 Node tests and the earlier four-scenario
browser smoke remain passing; no new dependency or lowered threshold.

Downloaded artifact10811002437 SHA256:
6e906c9b4a3b87174b4b429cc7a25e3f1fb8d934b60fef11c167eef3d2ca43ea.
Both browser receipts and the Node report were independently parsed. The receipt
explicitly says native_dataverse_test=false and no credentialing decision.

Initial hosted testing exposed CSP-incompatible string-eval polling in the TEST
navigation wait. It was replaced by native frame.wait_for_url(load), without
adding unsafe-eval, disabling CSP or dropping iframe assertions. A separate review
alleged a held-refresh deadlock; source and executed traces show the awaited outer
form setup does not await the inner card read. The rationale was recorded and the
thread resolved after actual successful execution. Source reviews do not imply
independent clinical or cybersecurity acceptance.

The local browser was stopped by administrator navigation policy before loading;
that policy was not bypassed and no local browser success is claimed. Hosted
browser results above are the actual execution evidence.

## Remaining acceptance and module boundaries

No native form/resources/API were installed. Native serialization, execute/read
privileges, section/tab/form lifecycle and platform origin/CSP must be exercised
in the approved sandbox. Scripts are read-only and preserve as-of/currentness
warnings; this is not continuous scope monitoring or clearance to practise.

Finishing the complete credentialing service still requires protected human/case/
authority-bound writes, immutable root/history and direct-CRUD controls, genuine
native storage/concurrency/rollback/restore tests and the broader workbench.
Package/upgrade/standalone install and representative-user/accessibility acceptance
remain open. Do not archive N03 or count this as production authorization.

No-admin Lists/connector-free Flow and fixed visual preview remain independent,
synthetic-only options. Full Dataverse stays the production target. No actual
practitioner record, delegated scope, tenant permission, app registration, paid
service or CGov contract changed. There is no added recurring clinical task.
