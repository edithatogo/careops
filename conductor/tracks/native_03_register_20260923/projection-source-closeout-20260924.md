# N03 recorded projection and versioned-read source closeout

24 September 2026. Sanitized archive of completed code slices only.
Full N03 remains IN PROGRESS; no tenant, practitioner record or authority changed.

## N03-P01: complete-history recorded projection

Continued existing Decisions#24 on #23 rather than overwriting concurrent branch
work. Final head24fd302d44f17dcd968d84334e518926eefd16f1 was reviewed and merged
at394845ecad88fc9967163da9808ad4bc2e7cfb9c. All six workflows passed:
Register35987643418, Identity35987643426, Calendar35987643487,
Authority35987643548, Reference35987643510, Validate35987643431.

Downloaded artifact10803395138 and independently parsed actual TRX/Cobertura:
203/203 tests, zero skips;392/392 register-library lines and354/354 branches.
SHA256 e81fb8fcd5424e51a2d5be170869ce84346dc7e3c167b4d928e06b5eec641e5f.
The 720-combination temporal/state matrix runs inside one test, not 720 additional
reported tests. Incomplete future revisions, query ordering, boundary validity,
corrupt/hidden history and defensive output are also checked.

Review corrected the disposition property without suppressing the analyzer.
A concurrent head-comparison clarification was inspected after a stale update
was rejected. Empty GUIDs are rejected before GetValueOrDefault comparison, so
that expression preserves validated empty-chain semantics without unreachable
lifted-nullable coverage branches. No malformed-input guard, test or threshold
was removed. Source review is recorded, not independent clinical/cyber approval.

The reducer validates the entire ordered same-record chain, then selects the
highest eligible SEQUENCE, not the greatest effective timestamp. Validity is
checked after selection. Expiry cannot restore an older grant, and an older
scheduled grant cannot revive after a later revocation. Recorded restrictions
remain visible even when source currentness is unverified. Output is a minimal
immutable view, never automatic practice clearance. It performs no SDK operations.

## N03-P02: native version-guarded read adapter

Directly stacked on #24, Decisions#25 merged at
972ea7bbed5638dfe6708c0d554e9d09af180b75. Final head
84346c11b20935f344affe99f3cc484127c707b7 passed all six workflows:
Register35988368157, Identity35988368148, Calendar35988368171,
Authority35988368224, Reference35988368172, Validate35988368313.

Actual downloaded artifact10802837269:
250/250 tests (47 added), zero skips;440/440 library lines and442/442 branches.
SHA256 9c351d49fa360d697de56f68a4b6005f792c312433b6f201ad9fd347cf1ecb0b.
TRX and Cobertura were parsed directly. No dependencies, existing checks,
coverage thresholds or suppression rules were changed. Reviewed on the exact
head and no unresolved inline review threads returned before SHA-bound merge.

The native adapter checks direct execution context and WhoAmI consistency, reads
and freezes the root version/sequence/head/currentness, retrieves the complete
bounded ordered journal, computes the reducer output, and checks a second root
read. Inconsistent markers and partial/hidden history discard the result. It
uses no retries, elevated identity, cached-scope fallback, writes or external
messages. SDK object reuse cannot mutate the frozen first marker or result.

## Inventory delta and remaining acceptance

The historical #21 parity inventory remains intact. Its native-projection gap
now has a tested reducer and native retrieval adapter. This closes code slices,
not actual row/team/column authorization, native source verification, snapshot
isolation or deployment. Double-root checking detects protected atomic updates;
unauthorised direct history edits must still be prevented. WhoAmI consistency is
not an independent proof of a human decision or a factory-bound service.

Compose the existing caller resolver and read adapter into an actual protected
current-scope handler with its request/output contract and generic error boundary.
Complete and qualify the authority/case-bound write endpoint, native storage
representation, direct-write prevention, genuine sandbox concurrency/rollback,
UI/export, time-boundary refresh and recovery. Larger histories require a
separately qualified bounded path; the 256-entry ceiling is not clinical policy.
Never silently treat missing conditions/supervision as an empty unrestricted scope.

No-admin synthetic Lists/connector-free Flow pilot remains independent and
unchanged. No Dataverse environment, app registration, permission, current signed
CHHHS delegation, clinical scope, notification, paid service or CGov contract was
changed. No extra staff queue/form is introduced. Raw excluded Conductor archives
are not published; all 12 tracks/120 tasks and earlier receipts are retained.
