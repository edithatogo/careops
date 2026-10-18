# N02 completed source slices

Updated 24 September 2026. Sanitized source-closeout archive only.
Full N02 remains IN PROGRESS; no current CHHHS signed authority is certified here.

## N02-C01: calendar arithmetic, part of N02.08

Predecessor careops-approve#57 merged at 326cd7c93dc5f2728135630de8f63b89fe66843b.
Decisions#14 implemented the native net462 calendar library and tests;
merge ede4af4493f4e960a50656f09acc2dee5c00582f, final head
bc29c8f8c10be418b1024aab3afcdcb722f34458. Native 35816303246,
Reference 35816303252 and Validate 35816303243 passed before SHA-bound merge.
22 native tests, zero skips; 41/41 library lines and 52/52 branches.

The collector initially returned no coverage despite passing tests, correctly
failing the evidence gate. The compatible MSBuild driver, committed dependency
locks and locked restore passed without weaker tests/thresholds. The component
uses explicit civil dates/calendars; it does not guess holidays, extend scope or
change authority. Native host/calendar approval remains required.

## N02-C02: native delegation predicates, parts of N02.06/N02.07

Resumed and reviewed existing Decisions#15 after #14 and CareOps#165.
Merge 6498e8e75080e7079d2ce91e7bd0efaa9b8b46fd; final head
da8ca454193d4e137663d4a44ed0d90c8b8bd6e4. Final successful workflows:
Authority 35873880948, Calendar 35873880944, Reference 35873880927,
Validate 35873880938. Downloaded artifact 10756251061 confirms 22/22 tests,
132/132 lines, 108/108 branches; SHA-256
ceef340bca0c811fe621d8f6fb4487d55d051d7c577b954fc42b0f80f448a8fc.

Review fixed an unsafe enum default: zero is Unverified, never Permitted. Added
zero/undefined-value tests and an independently encoded native digest vector.
Recovered actual dependency locks, committed them and repeated locked restore;
the corresponding automated review finding was fixed and resolved. The existing
synthetic concurrency test scheduling fix retains actual competing connections;
it neither adds production SQLite work nor removes its assertions.

The library checks exact approved content, organization, periods, role occupancy,
self-decision/conflicts, grant uniqueness, committee independence and conditions.
These use trusted server-resolved facts; a browser/agent cannot supply trusted
identity/source claims. This is not authentication, signed authority or a decision.

## N02-C03: exact delegation change review, part of N02.06

Stacked directly on #15. Decisions#16 merge
8bf56acbc16d2add7f27f75c94e6e66a88656479; final head
afd19cf9e0c73c9c7aa408d20438a13ad023f664. Successful workflows:
Authority 35875136883, Calendar 35875136673, Reference 35875137009,
Validate 35875136749. Artifact 10757078411 confirms 34/34 authority tests
(12 added), 185/185 lines and 134/134 branches. SHA-256
900d3c200904c37893d04cb442c49838ed25c42f9df1b60bae14e7e745480b8e.

Immutable exact comparisons bind both full profile hashes. Added/removed grants,
empty conditions and every changed field remain visible. Equivalent set order
and timezone offsets do not create unnecessary work. A property-inventory test
forces future schema additions to receive digest/comparison review. This prepares
one existing configuration approval; it neither approves changes nor adds an
approval step to practitioner cases. No new package dependency was introduced.

## N02-C04: read-only caller-to-person binding, part of N02.07

Resumed Decisions#17 and reconciled it with current #18 main through a two-parent
commit, preserving #16/#18 without a forced update. Merge
4f8f9d1505a605d0ece954f9a91bb367a5d81be0; final checked head
d5c4a12de03a3860d4e8aae1d8bd014dc3400d36. Successful final workflows:
Identity 35882151700, Calendar 35882151692, Authority 35882151321,
Schema 35882151315, Reference 35882151407 and Validate 35882151464.

Downloaded qualifying artifact 10760827596 from run 35881638436:
57/57 tests, zero skips; 56/56 library lines and 92/92 branches. SHA-256
b7f8cce78fea0f1dff965a223f1e6f64c0bb5791699615d675f45bab5452350c.
The actual dependency graphs were committed, then qualification repeated using
locked restore. The missing-lock review thread was addressed and resolved.
SDK metadata properties are server-read-only; failing fixtures now set them only
through test-local internal setters. Production guards were not changed or bypassed.

The adapter resolves the initiating account, WhoAmI organization, non-application
account and canonical Decisions-owned person mapping under caller-scoped access.
A published Active identity key is required before relying on caller-visible
uniqueness. Missing/malformed/ambiguous responses do not select the first row,
guess an email/title, elevate to SYSTEM, retry or create a person.

This identifies an account/person, NOT a present human interaction or decision
confirmation. Delegated automation may use a user's connection. Protected mapping
maintenance, canonical identity reconciliation, native index/permission tests,
current occupancy/authority and exact-case confirmation remain required. These
tests simulate SDK responses; they are not Dataverse authentication-engine tests.
The separate no-admin M365 pilot has no dependency on this full-app adapter.

## Review and remaining gates

All above source reviews were recorded on their exact PR heads. Artifacts were
independently parsed for executed tests and coverage; this does not mean an
independent clinical/cyber/legal reviewer approved the service. Full coverage
applies to the stated small libraries, not the entire credentialing application.

Current signed CHHHS instruments and separate credentialing delegation; verified
role mappings; native protected identity/occupancy/source resolution; Dataverse
profile persistence and approved release lifecycle; the Power Apps change-review
screen; actual calendar/timezone mapping; native sandbox and operational acceptance
are still required. The no-admin Lists/Flow pilot is independent and unchanged.
Only these source deliveries are closed; do not archive the full N02 track.
