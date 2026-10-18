# N03 confirmed writer and historical receipt recovery: source closeout

25 September 2026. Sanitized source archive, not operational acceptance.
Sequence: existing Decisions#36 -> resumed #37 -> #38 -> #39 -> portfolio closeout.
Full N03 remains IN PROGRESS. No tenant registration or data mutation was performed.

## Existing prerequisite: owner-bound intent

Decisions#36 was already merged at 3978c179396bbab244e158982cb57f571a2612e3
when this delivery started. Its explicit decision/event owner teams and complete
DecisionConfirmationHash were read as the source baseline, not newly merged or
independently requalified as a separate PR in this pass. Both owners, original
content, organization and journal version/sequence bindings are part of the intent.
An unowned synthetic fixture cannot produce a valid full confirmation digest.

## N03-W01: composed confirmed journal core

Resumed Decisions#37 and merged at 8034a7ce5ba62205e868ffbdbb8d48f0c5441e04.
Exact checked head: 31ec0026b76435058748e0e0d46e67340932f78a.

HumanConfirmedJournal joins the existing CallerResolver, DelegationGate, owner-bound
DecisionAppend and JournalWithOutbox instead of creating another writer. The same
verified caller-scoped service is retained. Checks bind the canonical person and
organization, exact root practitioner/profession/facility, original human-confirmed
digest, outcome/function/pathway, release/occupancy/evidence references and configured
nondefault owner-capable teams. Authority must cover the confirmation instant and
the present server-time recording attempt; later authority cannot retrospectively
authorise an earlier action. No technical owner selection is delegated to clinicians.

Final-head workflows all passed: Identity36107010889, Register36107010735,
Authority36107010774, Calendar36107010729, Card36107010767, Reference36107010897,
Validate36107010804. Actual downloaded artifact10851417479 was hashed and its
TRX/Cobertura parsed: 202/202 tests, zero skips, 278/278 Identity-library lines,
326/326 branches. SHA256:
da3313a8d6c0018b4dd10a6ee311c3b53bff549ebf8dec8e789d4f1dbe030e69.

The initial complete-coverage failure exposed a redundant lifted nullable-owner
comparison after the sealed owner/digest invariant. Compared validated concrete
GUIDs instead, retaining missing/same/different-owner tests and the whole-library
gate. Inspected dependency locks match the resolved graph; the temporary graph
resolver workflow is absent from the merged diff. No external version was changed.

IMPORTANT: Profile, Release, Authority.Request and HumanDecisionConfirmation are
trusted HOST snapshots. Their constructors and hashes are not evidence of native
source authenticity or an actual human confirmation. No public endpoint accepting
these objects is provided. The protected native source adapter and its concurrency
control remain necessary before this core can become an operational writer.

## N03-R01: own historical receipt, without another decision

Decisions#38 merged at 82039faabf4ea2d5bc1101471d1c838cb6624a43 directly on #37.
Exact checked head: 89c4fa4082fd09a1f9d5cc3700167720b4f0cf60.

ReadOwnDecisionReceipt is actual record-bound IPlugin source. Only Target and
DecisionId are accepted; identity comes from the same verified caller service.
The original caller's historical decision is read using seven bounded columns,
with independent record/actor/key/state/time/hash checks. Nine primitive outputs
retain the historical interpretation. A current account and record/decision read
access remain required, but current authority to approve again is not required
just to read an existing own decision. No writer, event repair or resubmission runs.

A valid receipt is not current scope, complete equality with a later edited payload,
a full confirmation-digest comparison or a consumer delivery acknowledgement.
An unavailable receipt does not establish that the original save failed. Do not
automatically generate another decision ID, repeat approval or bypass lost access.
Controlled reconciliation retains the original identity and ordinary accountability.

Final-head workflows passed: Identity36108683204, Register36108683222,
Authority36108683190, Calendar36108683217, Card36108683211, Reference36108683235,
Validate36108683214. Downloaded artifact10852585482 was hashed and its TRX/Cobertura
parsed: 238/238 tests (36 added), zero skips, 338/338 Identity-library lines,
430/430 branches. SHA256:
55c426fccaafe90351a6cee6127bc6a6a37ba720dbe42551a8b19526e0712761.

Applied the valid automated review finding: root access may disappear during the
decision read because sharing does not cascade. A final caller-scoped canonical
root read now precedes response output. Access loss or malformed final identity
clears the result; primitives are frozen before that final SDK call. Six regressions
cover access revocation, final identity faults and mutation during the last call.
This is point-in-time revalidation, not an atomic permissions snapshot. The review
thread was resolved after final tests. Initial test compilation was also corrected
by simulating missing collections through IPluginExecutionContext rather than
assigning RemoteExecutionContext's read-only properties. Negative checks remain.

## N03-R02: privilege-bound receipt API definition

Decisions#39 merged at ad5a0ccf0bd1a02f094732553e36b556c2a30c68 directly on #38.
Exact checked head: d4ae74a4e0df1e369f6b82825235997f9862e483.

OwnDecisionReceiptApiDefinition constructs metadata for the existing reader only.
Requires a canonical inspected exact handler, explicit existing execute privilege
and stable API identity. The register Target is platform-generated; DecisionId is
the sole explicit required Guid input. All nine primitive response names/types
are tested against an actual reader invocation in the synthetic SDK fixture,
not merely against another schema example. Native serialization is tested.
No identity/role/source/time overrides, processing extensions or SDK execution.
IsPrivate is discovery metadata, not authorization; no unsupported disabled-state
safety claim is made for Custom API metadata.

Final-head workflows passed: Identity36109204266, Register36109204294,
Authority36109204203, Calendar36109204233, Card36109204160, Reference36109204166,
Validate36109204237. Downloaded artifact10851459222 was hashed and its TRX/Cobertura
parsed: 249/249 tests (11 added), zero skips, 383/383 Identity-library lines,
458/458 branches. SHA256:
2e77f120487b58c6abd9bb73ada97a984f2c83227ad92e6f85bc03f65fb447a3.

Reviewed full diffs and actual evidence at each exact head before SHA-bound merges.
Existing tests, locked dependencies, warnings-as-errors and complete named-library
coverage gates were retained. Source/SDK tests are not whole-application coverage,
live Dataverse permission or transaction tests, or independent clinical/cyber review.
No local .NET execution is claimed. The 44-test browser/card suite was unchanged.

## Next native boundary and operational gates

Resolve original confirmation, approved outcome/ownership rules, released delegation,
source currentness and actual role occupancy from protected native records. Bind
these to the authenticated decision-maker and prevent concurrent withdrawal or
rebinding during the transaction. Do not accept trusted snapshot objects from a
browser, agent, caller-created hash or unauthenticated configuration. Complete
and register the protected writer only after direct Create/alternate-path controls,
source provenance and real native transaction/security tests are demonstrated.

The composed core is the same-decision-maker recording path. A supported secretariat
or administrative recording-on-behalf pathway must explicitly distinguish recorder
from actual decision-maker and preserve authority at the human decision time. It
must not be approximated by impersonation or an added demand to repeat the original
human confirmation. That separately governed pathway is not implemented here.

Integrate bounded historical-receipt recovery into the existing save experience,
not a new mandatory form or queue. Qualify actual API registration, execute privileges,
wire formats, field/row security, access changes and read-after-commit behavior.
Current recorded scope remains the separate current-scope read. Missing receipt,
lost response or expired authority must not automatically trigger another decision.

Native owner permissions, immutable history, null/empty/time precision, concurrency,
rollback, bypass controls, controlled corrections, lawful retention/disposal,
Dataverse/SharePoint recovery, standalone packaging and representative workbench
acceptance remain open. No signed CHHHS authority is certified by these source tests.
Only the completed source slices are archived; full N03 is not complete.

Full Dataverse remains the production target. No-admin Lists/connector-free Flow/
fixed-browser pilots stay independent and unchanged. No new Entra application,
tenant privilege, real practitioner record, clinical scope, paid service or CGov
arrangement was changed. No additional recurring clinician task is introduced.
