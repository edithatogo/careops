# N03 caller-bound current-scope read: source closeout

24 September 2026. N03.07/N03.08 composed read SOURCE COMPLETE.
Full N03 remains IN PROGRESS; no native endpoint or tenant is deployed.

## Sequential delivery and actual evidence

Decisions#24 implemented the complete-history recorded-scope projection and #25
implemented the version-guarded SDK reader. Their already reviewed closeout is in
[projection-source-closeout-20260924.md](projection-source-closeout-20260924.md),
merged through CareOps#170 at 2158307c4008649310cb230ae41dc552a969f08f.

Decisions#27 then stacked directly on #25's merge
972ea7bbed5638dfe6708c0d554e9d09af180b75. It is merged at
b9ebc520a3e50bd16cf5fced6586191770f48282; exact tested/reviewed head
967e8876240554ab89be30e17193dcc407ec2ab9. All six applicable workflows passed:
Identity35989728764, Register35989728750, Authority35989728716,
Calendar35989728783, Reference35989728721 and Validate35989728711.

Downloaded artifact10803981254 from Identity35989728764 was hashed and its TRX
and Cobertura parsed directly:120/120 tests, zero skips;148/148 Identity-library
lines and184/184 branches covered. SHA256:
29f835202486c63c0168013bc1ca0881f9b3c1351655db322ea52cb6dc21def1.
This adds26 cases over the94-test identity baseline. RegisterSchema retains its
separate250-test gate and440/440 lines,442/442 branches. These counts describe
the named libraries, not whole-application coverage or native Dataverse behavior.

## What the source now composes

ReadCurrentRecordedScope is an IPlugin implementation for the reserved bound
API dft_ReadCurrentRecordedScopeV1. It validates a single exact Target, freezes
the record GUID before SDK calls, invokes the existing CallerResolver, obtains
the same caller's service and evaluates VersionedScopeReader at server UTC now.
No browser-supplied identity, role, evaluation time or source assertion is trusted.

Response fields separate read success, existence of an effective recorded decision,
recorded state and source currentness. Empty/future history is not a current grant.
Stale verification cannot hide a known recorded revocation. The response preserves
conditions and supervision, never private actor/case/authority papers or SDK
formatted values. It is always recorded data, not practice clearance.

Exceptions clear all partial/stale outputs, leave ReadSucceeded=false and raise
the same generic error without private underlying text or inner exceptions. There
is no automatic retry, write, message, elevated identity or extra staff queue.
The code does not claim a successful read remains current after it is returned.

## Review corrections and independence

Review added immutable Target capture and a mutable-input regression. A concurrent
#26 implemented a duplicate reader; it was closed UNMERGED and its branch retained.
#27 composes the single #25 reader, not a competing API or parallel workflow.

The only new assembly dependency is RegisterSchema inside the Decisions module.
Tests reference the actual assembly rather than recompiling a duplicate schema
class. Both dependency locks retain every external package/version/hash and add
only the module project edge. Locked restore and drift checks passed. No existing
workflow, assertion, analyser, threshold or coverage scope was weakened. Source
review and no outstanding inline threads were checked before SHA-bound merge.
The source contract requires approved dependent-assembly packaging/provenance;
it does not invent an unconditional strong-signing requirement.

## Gates that remain open

Source composition is not registered API availability. Require actual native
package/import qualification, API execute privilege, approved row/column/export
permissions, canonical-person indexes/mappings, nullable Entity response round-trip,
source fidelity, immutable history/direct-CRUD protection and real concurrency
and negative-access tests. Complete human-decision/authority-bound writes and the
Power Apps workbench remain open. SDK mocks are not authentication-engine tests,
and matching root versions are not independent database snapshot isolation.

Current signed CHHHS instruments, delegated authority, clinical/cyber review and
operational recovery acceptance are not certified by this source receipt. The
no-admin Lists/connector-free Flow pilot remains unchanged and independent. No
real practitioner record, scope, tenant permission, Entra app, paid service,
licence, external communication or CGov contract was changed. Archive only this
completed source slice; retain the parent N03 operational acceptance tasks.
