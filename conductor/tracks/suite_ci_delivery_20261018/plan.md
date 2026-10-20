# Suite CI/CD plan

Status: in progress. Existing user goal retains the full suite scope.

## 1. Contract and ownership
- [x] CI1.1 Refresh current heads, workflow/dependency inventory and check protection.
- [x] CI1.2 Assign RIMS/PPG/Clinical Hub CI to existing chats; parent retains shared workflows and remaining modules. No new chats or acknowledgement polling.
- [x] CI1.3 Implement common contract, trustworthy upstream resolution, lock generation and outcome classification with negative tests.
- [x] CI1.4 Qualify foundation on GitHub, merge only with every check green, publish immutable adoption revision.

## 2. Dependencies and shared CI
- [x] CI2.1 Qualify latest parent tools/actions, automate lock repair/update proposals and verify an actual generated-lock update.
- [x] CI2.2 Implement reusable source/workflow/security baseline; retain existing test commands and independently runnable modules.
- [ ] CI2.3 Roll out to every owned module in the rollout matrix, qualify action/submodule updates without disturbing owner work.
- [ ] CI2.4 Verify required checks and update automation through native API and fresh runs; merge sequentially with all checks passing.

## 3. Development canaries
- [x] CI3.1 Scheduled bounded tool/runtime development candidates, exact version and integrity receipts; no native writes or automatic promotion.
- [x] CI3.2 Exercise candidate resolution and representative failure; preserve working lock and record promotion/recovery conditions.
- [ ] CI3.3 Run/verify each module canary and record latest result without conflating skipped, blocked and passed.

## 4. Compatibility and releases
- [ ] CI4.1 Cross-module fixtures exercise actual optional producer/consumer interfaces, source-qualified identity, absence, incompatible versions, stale/missing input and duplicate retries.
- [ ] CI4.2 Build actual independently useful release packages once, emit SBOMs and SHA256 digests, generate GitHub build/SBOM attestations through qualified OIDC.
- [ ] CI4.3 Verify package contents, SBOM and downloaded artifact attestation; keep private artifacts private. No fabricated release acceptance for templates.

## 5. Suite adoption and completion audit
- [ ] CI5.1 Resolve eligible protection/update gaps; preserve stronger controls and record private-host feature/payment constraints separately.
- [ ] CI5.2 Classify each hosted outcome from jobs/annotations; billing blocks are not executed test failures or passes.
- [ ] CI5.3 Collect exact current-head evidence from module owners; inspect actual rollout against all five requirements.
- [ ] CI5.4 Sequential green merges and main readbacks; keep goal active until every applicable module is implemented and verified.

## Ownership — 18 October 2026
CareOps parent: shared contract/workflows and Approve/Process/Sim/Finance/Costing/
Decisions source CI. RIMS Flow bootstrap chat: public RIMS CI. PPG Repository and
security chat: PPG CI. Clinical Hub Platform integration chat: public/private
Clinical Hub CI definitions. Existing native writers retain their objects.

Audit correction: CodeQL v4 annotated tag f051dc8 peels to the already pinned
6f2ac81 commit. No CodeQL upgrade follows from comparing tag-object IDs. Ruff
0.17.1 is the current parent patch candidate; other direct tool releases matched
the discovery baseline. Approve pin is 15 commits behind default and Conductor
2 behind; commit distance is discovery, not qualification.

First foundation merged in PR #11 at 953eba2 after all 17 checks passed.
Automatic hash-lock regeneration ran on GitHub, and its downloaded lock matched
the receipt digest with Ruff 0.17.1. Guarded shared security passed; privacy
logging/storage findings and three workflow review findings were fixed and
resolved. Initial post-merge caller could not load the pre-squash policy commit,
so its reference is being advanced to the reachable merged commit before adoption.
Tool preview canary passed. The runtime job correctly failed setup because no
3.16-dev build exists for the runner; discovery now records actual availability
and does not downgrade to an older preview or claim skipped tests passed.

Foundation acceptance: PR #12 merged at 3712b88; all eight current main workflows
including manual canary 39121252499 passed. Downloaded tool lock and receipt digest
match. Runtime discovery freezes manifest 49858b9/digest and correctly records
unavailable, runtimeTestsExecuted=false and skipped; no runtime promotion. Main
protection readback confirms strict/admin enforcement, no force/delete, existing
three checks plus GitHub's PR-only CodeQL alert check and shared-security check.

PPG owner delivered public PR #3 at 33c2215: all eight PR checks and post-merge
run 39121301356 passed; four exact required app-bound checks/admin enforcement
and weekly Actions updates verified. Native 80 Python tests, two JavaScript
suites and assembler retained. Its development canary, applicable release and
compatibility assessment remain open; no blanket module completion claimed.

Next parent slice: deterministic integrated Incidents source package with matching
SPDX schema/content checks, build and SBOM attestations, and downloaded artifact
verification. This addresses real source distribution, not a fabricated native
release. Cross-module interfaces and remaining module CI remain queued. Approve
is being prepared in an isolated clone, preserving its owner checkout and tests.

Release qualification: PR #13 merged at 8bceb08 with all checks green. Source
run 39122669823 built the package and both attestations; its provenance check
passed, but SBOM verification used an unversioned predicate URI and failed. The
retained candidate was not rebuilt: its downloaded121files, package/SBOM digests
and signed SBOM payload were independently checked; gh verified both signatures
with expected repo/workflow/main/source commit and hosted signing. Actual SDK
predicate is https://spdx.dev/Document/v2.3. The workflow filter and exact-source
checks are being corrected before claiming the hosted release workflow complete.

Corrected source-release run 39123515957 passed on d88ae694. The downloaded
Incidents archive has121files matching SPDX SHA256s; both provenance and versioned
SPDX attestations independently verify exact source/signer commit, repository,
workflow, main ref and hosted signing. This closes the Incidents source-package
proof only; cross-module interfaces and other releases remain open.

Approve PR #74 merged at da07812 after all eleven checks passed, including
PAC2.13.1/.NET10.0.402 offline packaging and109Python tests with100%branch
coverage. Ten unfiltered app-bound checks are now required with strict freshness
and admin enforcement; existing no-force/no-delete/conversation safeguards remain.
Canary/automatic-lock follow-up is under qualification; no native deployment ran
and the parent optional gitlink remains unchanged pending interface qualification.

Approve's stale-lock negative run39125002875 showed successful candidate install
and tests followed by the intentional uncommitted-lock refusal; its repair
artifact survived. The downloaded digest was verified and exact generated lock
applied. Parent lock generation now adopts the same fail-closed source-commit
gate for both lock and dependency inventory, with an executed workflow-step
regression covering clean and stale source. No privileged auto-write workflow.

Process PR #78 completed both review fixes: early setup/preparation failures now
retain receipts; dependency resolution/install failures classify as executed
failures. Seven stage regressions execute the actual workflow receipt. All seven
current-head checks passed at 3d7f896, including full source qualifications on
Python 3.14.8 and 3.15.0. Downloaded candidate locks match recorded SHA256s.
Normal protected squash merge completed; main canary verification follows.
No runtime range promotion, native writes or PM4Py adapter qualification implied.

Current parent slice adds bounded actual ZIP/wheel SPDX inventories and rejects
stale caller exact CI declarations in the reusable job. Publish this policy first,
then qualify consumer pins against its reachable merged revision. Remaining Sim,
Finance, Costing, Decisions and actual cross-module interfaces remain in scope.

PR #17 merged at1373e971 after all eleven checks passed. The parent is now
qualifying its own caller against that reachable published policy revision.
Process main canary39129780064 passed; both runtime locks independently match
their receipts and exact merged source5de05c25961b73634e2ec9728753b1dec9eec7a8.
Finance PR #14 preserves all existing required check names and domain tests,
updates immutable actions, and centralizes security. Its local repository hygiene
and four evidence techniques pass; full validation needs Windows Registry.
Hosted refusal annotations are being classified before any merge.

Finance runs39130225562/39130225787/39130225801 have zero executed steps and
verified billing-refusal annotations. PR14 remains unmerged; local results do not
replace Windows hosted qualification. Independent public module work continues.

Actual release evidence: Approve PR76 merged69f35dd, main39130836397 passed.
Downloaded ZIP/SPDX3files and official schema pass; independent provenance/SPDX
signatures bind exact source/signer/workflow/repo/main and hosted signing.
Process PR79 merged1e092ff, main39131007181 passed. Downloaded wheel/SPDX36files
and official schema pass; independent signature checks prove the same bindings.
Its separate frozen CycloneDX inventory covers base/optional dependencies and
excludes build/test tooling. Installed wheel fictional pipeline and reproducible
local builds pass. Actual optional interfaces remain outstanding; package proof
is not deployment, provider implementation or operational acceptance.
Costing source CI preparation removes legacy cached PAC2.3.2 shadowing, with
executed PATH/missing-command regressions and no deployment workflow dispatch.

Costing PR14 source run39131313940 has verified billing-refusal annotations
and zero executed job steps; no merge. UI export dependency/lock qualification
remains part of this module rollout, separate from managed package execution.

PR21 review correction: Approve policy1373e971 is qualified by actual shared
security run39130538284 at PR76 head898e1df, alongside package39130537841.
The older package39124187923 remains explicitly historical, not evidence for
the subsequently published policy. No completed native/interface scope inferred.

19October: Decisions PR52 contains immutable actions, canonical exact SDK,
Python/browser hash locks, automatic regeneration and scheduled prerelease
discovery. Local75Python/44JS tests have100%coverage; both synthetic Chromium
tests, dependency audits and full source gate pass. Fixed actual locale date
regression with six renderer cases. Ten hosted runs/eleven jobs were refused
before execution by billing; no merge or Windows runtime claim. Native preview,
actual release/interface/protection qualification remain in scope.
Clinical Hub public PR5 policy1373e971 adoption merged23079b0; exact-head
main39133123335 success independently read back, with existing owner-preserved
domain tests and controls. No native or authentication change implied.

Public compatibility slice: add PR/push/scheduled pinned public Approve69f35dd
and Process1e092ff checks without a cross-repository credential. Build and install
the actual Process wheel from its frozen base/build lock; exercise its parser,
summary, incompatible versions, missing fields, duplicate replay, stale-watermark
non-regression, conflicting edited replay preservation, cross-source refusal
and private-content rejection. Verify each clean checked-out revision and retain
contract/implementation hashes. Approve's producer remains a disabled blueprint;
no executable emitter, native integration or freshness cutoff is claimed. The
historical full private release-train gate remains explicitly manual and separate.
Local nine consumer/boundary cases and exact-revision/dirty/absent-source guards
pass; hosted qualification and actual producer implementation remain outstanding.

19 October verified adoption: public compatibility PR23 mergedda7e0f4 after
all current-head checks and both review findings were resolved. Its main
consumer/boundary run39136597689 passed; Approve emitter remains unimplemented.
Process PR77 merged5436642 after both exact-runtime quality gates and both
prerelease dependency canaries passed. All73 package versions preserved,
166tests/90.88%coverage; canonical3.15.0 retains3.14.8 compatibility. Independently
verified downloaded candidate archive/lock hashes and PR ancestry. Added
app-bound required3.15 quality and actual-package checks without removing the
existing four/strict/admin controls. Main package39136841452 builds and exercises
the wheel on3.15.0; independent official-schema SPDX/all36file/archive checks and
exact-source/signer/workflow/main hosted provenance/SPDX signatures pass.
Finance PR14 now prepares an isolated official PowerShell preview canary, with
seven local resolver/integrity/refusal cases. Its latest ten hosted jobs were
billing-refused before execution and coverage skipped; no merge or preview pass.
Other dependency proposals, Sim adoption, actual producer/remaining interfaces
and private hosted qualification remain open; the overall goal is not complete.

Approve gitlink PR19 qualification: preserve the historical September manifest
and release receipt at ec7d723. The separately reviewed current source pin69f35dd
must match the public inventory and public runtime qualification record. Fetch
that public source history and compare all three release-facing contract bytes
against ec7d723 and their recorded SHA256s. Exact current/baseline/public pins,
complete contract set and valid digests are mandatory; negative cases reject
unqualified current, wrong baseline, missing contract, invalid digest and
unreviewed publication pin. Nine actual Process-consumer cases remain separate
from the disabled Approve emitter. Local qualification passes; normal current-head
hosted checks are required before adopting the updated gitlink. No historical
release evidence or production integration is relabelled.

The same PR advances the public Process consumer from1e092ff to the independently
qualified aec8025 package source, exercising exact Python3.15.0. Process PR76
changed only the optional PM4Py pin to2.7.23.11; both canonical/compatibility
quality jobs, both development canaries, package and security checks passed
before normal merge. Main39137173288 and all other main checks passed; the
downloaded attested artifact/archive/file digests, dependency inventory and both
exact-source hosted signatures were independently verified. Optional dependency
loading is not an implemented production provider or licence-adoption decision.

Sim PR159 source stage is in progress at39afce5. Isolated leased worktrees,
per-commit scope checks and immediate lease release preserve native ownership.
Current source/security and hash-lock job passes; all dedicated native lanes
passed on Linux/macOS, with the full context mutation step still running.
First hosted setup failures were real unexecuted-test setup failures, corrected
by exactPython3.14.8 selection without dropping hashes/wheel-only policy. Local
81schema cases, actual lock/receipt guards and repaired action-retention tests
pass. Protect the always-running shared check after current-head qualification.
Official package metadata identifies rpds-py2026.9.1 as a later candidate; the
other four schema packages are current with no newer development release.
Development canaries, actual native package/signatures and optional-interface
qualification remain open; no MVP/native acceptance or full suite closeout.

Next prepared Sim task: draftPR160 is isolated from PR159 and changes only the
RPDS pin to2026.9.1 plus regenerated hashes and existing maintenance evidence.
Fresh3.14.8 verified-wheel installation, all81schema cases and dependency audit
pass. Preserve the other four package versions. Do not merge the draft into the
feature branch: finish159 first, retarget160 to main, then require new current-head
full/domain checks and normal protected merge. Both worktrees are clean and
per-commit leases released; no source/native acceptance is inferred from a draft.

Conductor development pin PR18: review f06add3→6e8f9a8 finds exactly one changed
file, the setup skill catalogue. Eleven catalogue URL edits resolve to ten
distinct Firebase/GCP skill targets, each responding200 to a read-only HEAD
probe. Plugin metadata/version/licence and every executable/other source file
are unchanged. Catalogue SHA256 is
56b81344f0cb63bfd18608b7aca71e08fca571ef854fcd7be931ccfe1f1bcede.
Update only the reviewed gitlink/publication inventory; do not install any
referenced skills or treat mutable catalogue URLs as trusted installation
authority. This is source-catalogue qualification, not new cloud capability or
permission. Require all current-head parent checks before normal adoption.

Sim adoption update: PR159 merged0a34dbd after all14checks passed. Protection
now requires four GitHub-Actions-app-bound checks, including shared security,
with strict freshness/admin enforcement and no force pushes/deletions. PR160
merged76d024e after another complete14-check qualification; downloaded regenerated
lock matches the reviewed RPDS2026.9.1 source and all receipt stages succeeded.
The hosted merge-candidate receipt includes the exact reviewed PR head.

PR162 adds isolated weekly/manual schema development candidates on3.14.8,3.15.0
and the next published preview when available. Actual local workflow installation,
all81schema cases and installed-version audits pass on both exact runtimes; four
actual-code negative regressions and syntax/ShellCheck/Zizmor checks pass.
Main integration preserved the candidate tree byte-for-byte; fresh hosted checks
are running. Hosted canary execution, native release artifacts and interfaces
remain pending. Historical observations above are retained, not current closeout.

Release/canary follow-up: Sim162 merged6e1dd71 after all13checks passed. Its
first main dispatch39145413714 failed discovery setup before any candidate tests: a
required shared CLI argument was omitted. Repair165 passes actual hosted discovery
and retains schedule/manual-only candidate tests; full current-head gates remain
running. SHA2candidate164 retains Rust1.99.0, passes295local native tests and5
rollback drills, and has independently verified current-head lock artifact and
receipt39145460844; context qualification remains running. No candidate promotion.

Sim native package163 compiled the actual CLI but correctly refused the missing
parent licence. The README explicitly records redistribution as not_established;
parent Cargo Apache metadata is not substituted for the outstanding decision.
Draft remains blocked at packaging, with no consumer/signature success claimed.

Private source-package follow-ups remain separate drafts: Finance15 packages256
actual tracked source/contract/script/doc files; Costing19 locally packs a managed
solution; Decisions53 locally packs the existing unmanaged source scaffold. All
three archives independently match their file SHA256 inventories and pass official
SPDX2.3 schema validation. Costing/Decisions identity and managed-mode checks use
canonical source identities, with wrong-mode/identity/missing-part refusals.
These do not establish native operation, compiled-module inclusion, hosted signing
or compatibility. Finance11jobs/4runs and Costing4jobs have fresh verified billing
refusals with zero executed steps. Retarget only after their source-CI base PRs
qualify/merge, then rerun all applicable checks; no private billing bypass.

Shared runtime-finalizer correction: unsuccessful discovery now receives a terminal
receipt, including missing/partial discovery files. Invalid evidence is retained
and refused. Actual CLI regression tests cover missing, partial and corrupt input;
45 delivery checks pass locally. Hosted qualification and downstream adoption remain
pending until the shared correction merges through its existing protection gates.

Qualified integration follow-up: CareOps28 merged after all current-head checks.
Its runtime finalizer records failed discovery and refuses contradictory or
incomplete successful-discovery evidence. PPG6 and RIMS4 adopt the exact merged
policy2b5eccb, pass executable failed-discovery probes and all applicable PR gates,
and merge normally. Main package/signature and dispatched canary qualification
remain pending; RIMS now enforces five strict app-bound source/package checks.
Public CI ownership is with this support lane; private/native owners are unchanged.

Sim164 merged exact SHA2 0.11.1 and regenerated Cargo lock after all14applicable
checks; main native run39149176806 passed. Sim165 discovery repair merged and
main canary39147083098 independently verifies actual3.14.8/3.15.0 candidate
qualification artifacts without promotion. Preserve the earlier setup failure.
Sim163 parent licence and private-module hosted billing remain separate blockers.

Main closeout evidence: RIMS39152095551 and PPG39152089749 both pass actual
package/signature qualification. Independent downloads verify624/65actual file
hashes, official SPDX2.3 schema and both signatures against exact source/workflow
identity. Main canaries39152121965/39152124945 pass; downloaded tool locks and
all stage outcomes verify. Frozen manifest selection reproduces newer-preview
unavailability, so runtime tests are explicitly skipped rather than qualified.
Module main source checks also passed. No deployment, licensing grant or native
acceptance is inferred; optional producer/interface work remains open.

Process80 lock maintenance merges certifi2026.10.18 after current-head domain,
package, security and canary checks. Exact hashes/sizes match non-yanked PyPI
records. Reconciled Process74 and Approve73 modular guidance now merge on current
qualified CI without reverting workflows, SDK/PAC versions or updater settings.
Approve also passes9flow-health fixtures and its full local source harness.

Refresh the public compatibility candidate to Approvea136e68 and Processfec8ede.
Actual installed Process passes9cases and4provenance/refusal cases locally;
historical release pins and3contract hashes remain unchanged. Hosted integration
qualification remains pending and producerRuntimeQualified stays false.

Current integration evidence: CareOps30 merged after all applicable checks and
main39153151365 passes9actual consumer cases. Independently downloaded receipt
verifies parent/module/source-file identities; producerRuntimeQualified remains
false. Current Approvea136e68/Processfec8ede packages independently verify all3/36
file hashes, official SPDX schema and exact source/workflow provenance/SBOM
signatures. Approve77 fixes failed-discovery finalization and main39153345999
passes all4canary jobs; exact tool lock and actual PAC2.13.1 package on
SDK11.0.100-rc.2.26504.105 verify without promotion.

Sim161 adopts Python3.15.0 after15applicable current-head checks. Main schema-lock,
harness and shared security pass; main native/context39153507557 is running.
Rust157 remains an unqualified single-file change: context consistency fails,
so coordinated qualification is still required before changing the canonical pin.
Licence and private hosted-billing gates remain open.

Clinical source-CI owner completes PR6/fca1abe using the same qualified shared
finalizer. MainCI39153423966, canary39153429698 and package39153433041 all
succeed on independent remote readback. Owner verifies exact failure probe,
candidate lock/frozen manifest,78actual source files/SPDX and both signatures.
Native/auth/private operational ownership and acceptance remain unchanged.

Approve digest31 preparation aligns the f53bebc gitlink, reviewed public-source
inventory, compatibility manifest and actual checkout references. Nine installed
consumer cases, four provenance/refusal cases and45delivery checks pass locally;
hosted current-head qualification remains required. Independently verify current
Approve39153345345 package's3actual file hashes/SPDX and both exact-source
signatures. Historical release baseline and producer limitations are unchanged.

Sim166 repaired Rust canary now passes all3actual compiler candidates on
run39156445517:295native tests each, plus doctests and Clippy. Independent
downloads verify complete parent/submodule source fingerprints, frozen compiler
identity, exact native commands/exits and actual log hashes. Real Git regressions
cover dirty/hidden source edits, moved submodules, incomplete/tampered receipts
and larger-checkout pipe handling;14focused cases pass. Full current-head context
gate remains pending; canonical Rust1.99.0 and release/licence gates are unchanged.


### Current main compatibility and CI lock refresh — 19 October 2026

CareOps PR31 is merged at e4c93aedfecad2f356b8c883c3b873c71be315d8.
Main compatibility run39157322952 passed its9actual synthetic consumer cases.
Independent artifact download verifies the API digest, exact Approve/Process
commits, all3source hashes and unchanged historical contract hashes. The disabled
producer and native-operation limits remain explicit; no new interface is claimed.

A targeted certifi2026.7.22→2026.10.18 CI lock candidate preserves every direct
declaration and other resolved version. The existing lock generator reproduces
the selected hashes; official wheel/sdist hashes, sizes and non-yanked status
were verified independently. Isolated Python3.15 hash install,45delivery tests,
6fuzz tests and advisory audit pass. Current-head hosted gates remain required
before normal protected merge. Recovery is the previous committed hash lock.


### Shared policy adoption candidate — 19 October 2026

Core PR33 merged at f0e8db252b181955d31185f1ccdd1e77dee1f5f9 after all14
current-head checks passed. All6 triggered main workflows also passed. This
revision includes the qualified certifi2026.10.18 policy lock. Align both core
security and standalone-package callers to this immutable revision, including
the matching policy-revision input. Each consumer adoption still requires its
own current-head checks; no mutable workflow reference or inherited secret is
introduced. The release packaging job still requires main and retains actual
archive/SPDX/signature verification. Prior policy revisions remain historical.


### Qualified module policy integration — 19 October 2026

Core34, Approve78, Process81, RIMS6, PPG7 and owner-managed Clinical7 merged
after their applicable current-head checks. Exact main runs are independently
read back in the rollout matrix. All adopt immutable policyf0e8db2; historical
refs remain history. Core main release39161186813 independently verifies121actual
file hashes, the exact official SPDX schema and both exact-source/workflow/main
provenance and SBOM signatures. This is source-package qualification only.

Reconcile the Approve gitlink/source allowlist and Approve/Process compatibility
refs to their now-qualified63345a8 and2627c2f revisions. All9actual installed
consumer cases pass locally; historical release baseline and contracts remain
unchanged. Current-head hosted integration remains required before normal merge.
The producer remains a disabled declared boundary; no native operation is inferred.


### Release/protection audit and archived scope correction — 19 October 2026

Independent current-main verification now covers Approve3files, Process36files,
RIMS624files and PPG65files. Every actual hash matches official-schema-valid
SPDX; both signatures bind exact repository/workflow/main/source/signer and hosted
identity. Signed SPDX predicates equal the downloaded SBOM documents, including
the previously verified121file Incidents package. No native acceptance follows.

All7public branch protections were freshly read back: strict and administrator
enforcement retained, no force pushes/deletions, existing app-bound checks intact.
Finance, Costing and Decisions source proposals now pin qualified policyf0e8db2;
local workflow checks passed, but every new-head hosted run remains billing-blocked
with0executed steps. No private proposal merged. Raw annotations stay private.

The old private Clinical repository is intentionally archived by an earlier human
decision. Native GitHub readback and its existing owner confirm this. Its stale CI
queue is retired as not applicable to active source delivery; it must not be
unarchived or treated as unfinished implementation. Public clinical-hub-core is
the active qualified source. Private RIMS is not archived; its existing source
owner now has the bounded remaining CI task, after their in-flight native checkpoint.
Conductor extension pin6e8f9a8 matches upstream main; no update is needed.


### Rust retry and sequential integration — 19 October 2026

Sim169 merged37de980 after all15current-head checks passed atfbce179.
Run39163739669 attempt2 succeeded; attempt1 retained an artifact-upload
ETIMEDOUT after domain/mutation checks passed. Both genuine review findings were
fixed and resolved. No test thresholds, time budgets or protections were weakened.
Obsolete single-file Rust157 is closed. Canonical compiler is now1.99.1.

Schema terminal-evidence170 now integrates that exact main baseline atcb5714b;
seven focused actual-workflow checks pass on the qualified Python environment.
Current-head hosted qualification remains required before normal sequential merge.
RIMS95f8313 main package39188558356 and source39188558918 pass; PPG836f5df
main package39164600222 passes. Independent newest-package verification now passes all70/624actual file hashes,
official SPDX schema, both exact-source hosted signatures and equality of the
signed SPDX predicates with the downloaded documents. Prior evidence retains
its original source identity. Rust post-merge main runs39206423894,39206423937,
39206423962,39206424023 and39206424280 all pass.
Private hosted billing, Sim distribution licence and owned private RIMS CI remain
explicit outstanding gates. This is progress, not full CI/CD rollout completion.


Schema170 closeout: all15applicable checks atcb5714b passed, including the full
context/mutation gate39237484844. Candidate-runtime execution is intentionally
skipped on pull requests; the independently verified manual canary39162723352
remains separate evidence. No unresolved review threads. Normal protected merge
produced5d127a3; post-merge qualification is pending. No billing, licence, native
acceptance or overall rollout gate has been waived.


### Current-main canaries and private RIMS CI candidate — 19 October 2026

CareOps run 39251411448, RIMS 39251401388, PPG 39251406340 and Clinical
39251437583 all passed on the exact main commits in the rollout matrix.
Independent artifact downloads verify candidate lock digests and frozen manifest
hashes. Tool candidates passed; newer Python runtime candidates were unavailable,
their tests explicitly skipped, and no versions promoted. These receipts do not
apply to later source commits.

Private RIMS PR6 adds the exact shared security policy, immutable actions and
scheduled/manual development canaries while retaining every existing source
check. The existing module-summary test incorrectly counted a separate overview
as another module. Its repair checks the overview and each of the six modules
independently, including diagrams and requirements/design text. All 477 tests ran
with eight existing skips. Source harness, visual/flow contracts and workflow
linters pass. Full ancestry secret scanning passes with three exact historical
record-identity/synthetic-checksum exceptions; a new generated synthetic credential
is rejected. No file-wide exceptions or native changes are included. Hosted run
39252033837 was refused for payment/spending-limit settings with zero executed
steps. PR6 remains unmerged; canary/protection/release gates remain open.

A current parent lock candidate adopts Hypothesis 6.170.2, filelock 4.2.4 and
platformdirs 4.13.5 through the existing automatic generator. All 82 hashes match
official non-yanked artifacts. Isolated hash installation, 45 delivery tests and
six fuzz cases pass. Current-head hosted checks remain required before promotion.
Recovery retains the previous declarations, lock and inventory as one revision.
Sim170 main source, security, harness, schema-lock and schema-candidate workflows
all passed at 5d127a3. Sim163 native package licensing and private hosted billing
remain separate outstanding gates. The full suite objective remains open.


### Parent lock promotion and immutable caller adoption — 19 October 2026

CareOps PR43 merged as 6319d0c after all 14 current-head checks passed. All six
source-main workflows passed. Hosted automatic regeneration run 39252673420
produced byte-identical source lock/inventory and an empty repair patch; its
downloaded receipt matches the lock SHA256 in the rollout matrix. This qualifies
the three-version parent update and closes CI2.1, not the module rollout.

Candidate resolution and representative failure evidence are also verified:
the four current-main tool locks match their receipts, frozen runtime manifests
match their hashes, and Clinical's actual failed-discovery probe retains terminal
failure with runtimeTestsExecuted=false. The delivery suite exercises the shared
failure and contradiction cases. CI3.2 is complete; per-module CI3.3 remains open.

Approve80, Process83, RIMS11 and PPG12 propose only exact shared-policy/helper
references to 6319d0c. Workflow syntax/security and changed-commit secret scans
pass; current-head module checks remain mandatory before normal merge. Clinical's
existing owner has the same bounded public CI task. Earlier adopted revisions
remain historical qualification evidence. No native configuration is changed.

Independent verification of the RIMS package at 9f3741d now covers all 636 files,
archive CRC/SHA256 and official SPDX schema. Both signatures verify exact hosted
source/signer/workflow/main identity, and the signed SPDX predicate equals the
downloaded inventory. This is source-package proof, not native acceptance.
Private billing and Sim distribution licensing remain outstanding.


## Qualified policy adoption — 19 October, follow-up

The reviewed shared policy remains `6319d0c0c76ee672223c156abce9d4181c41aa9a`.
Normal green merges adopted it in Approve #80 (`1be3261`), Process #83
(`cc095d5`), RIMS #11 (`345d554`), PPG #12 (`82641e6`), Clinical Hub #14
(`8d2c811`), and Sim #171 (`2603c0b`). Sim's critical mutation and aggregate
required checks passed on exact reviewed head `85bc14b`; the intended PR-only
schema candidate skip is not recorded as executed qualification. Its new main
canary is run `39258597948`; main readbacks remain pending.

Post-adoption canary workflows completed successfully for parent `39257024924`,
Approve `39257026191`, Process `39257025221`, RIMS `39257025013`, and PPG
`39257024948`. Workflow success alone does not establish preview-runtime
execution; retain their discovery receipts before claiming runtime promotion.
Clinical owner verified current-main canary `39254392999`, with runtime absent
and no promotion.

Independent downloaded release verification checked official SPDX schema,
every archive file digest, exact-source/workflow/hosted-signer provenance and
SBOM signatures, and equality of signed SPDX with downloaded SPDX: Approve
3 files at `1be3261`, Process36 at `cc095d5`, RIMS636 at `345d554`, PPG78 at
`82641e6`. Approve remains a source scaffold, not a qualified native runtime.
Parent source run `39255126879` similarly verified all121 files at `7b4c8ad`.
Private raw receipts remain in ignored local audit storage.

The optional public integration candidate advances only qualified Approve and
Process source pins; historical release schema identities remain unchanged.
The actual Process consumer passed all nine compatibility/refusal cases locally;
producer runtime remains unqualified and production writes remain disabled.
Hosted qualification of this new parent candidate is still required.

Full-suite completion remains open: private hosted payment/spending refusals
prevent tested adoption, Sim packaging retains its unresolved parent licence,
and remaining per-module/protection/release checks must be reconciled with the
rollout matrix. No public-source result establishes native deployment acceptance.


## Licensed native delivery continuation — 20 October 2026

CareOps PR45 merged normally at0d3371e after all applicable exact-head checks;
all8main workflows passed. The downloaded hosted compatibility receipt is from PR run39259407417, whose merge-candidate6565078 contains
reviewed head0831773 and base7b4c8ad. All9actual Process consumer/refusal cases
passed with qualified Approve1be3261 and Processcc095d5 pins; historical schemas
remain unchanged and producer runtime/native acceptance remain unqualified.

The owner explicitly selected Apache-2.0 for Sim project-owned code. PR172
merged at64d1425 after all13applicable checks passed. Root LICENSE/NOTICE and
README preserve third-party terms and separately governed data holds. Earlier
Sim main CI39258580773 completed successfully. Current licensed main CI remains
under qualification rather than being inferred from the previous result.

Existing native PR163 includes licensed main, canonical Rust1.99.1 and immutable
CareOps artifact tooling6319d0c. First licensed native job39369196500 compiled,
packaged and exercised the real unpacked CLI outside source. Its downloaded
9file ZIP/CRC/allSPDX digests and exact project/Kairos notice bytes independently
match; archive SHA2563485feabfaf3a79196eb6a81379ba88f99b76f06c37df030fd5103c7a3e852f7.
This is PR merge-candidate89a87d9 containing reviewed headb7d936e, not a main
signed release. Follow-up f0e0a46 strengthens actual consumer identity/results,
deterministic replay and invalid-input refusal; the first new oracle incorrectly expected usage error2
for malformed config. Run39369503281 retained that failure; follow-up572a9c1
uses the existing MalformedConfig4 and diagnostic. Its fresh hosted checks and
post-main signatures/download verification remain required.

One bounded private RIMS exact-head retry of39257208210, attempt2, still refused
both jobs before any steps with explicit billing annotations. Keep all private
CI candidates unmerged; local passes do not replace hosted qualification. The
full five-part suite goal remains in progress; no licence, native flow, billing,
credential or protection bypass is used to close missing evidence.

Corrected native package run39369737226 passed on572a9c1, including exact
source/seed/output invariants, same-seed byte replay and MalformedConfig4
refusal/diagnostic. Full current-head domain CI39369737129 is still live; do not
merge based only on package success or claim main attestations before execution.


## Sim native package qualification — 20 October 2026

PR163 merged normally at8ca0e5e after every applicable reviewed-head check passed
(including the critical mutation/context aggregate). All4main workflows passed: native
CI39370984674, session guards39370984638, shared security39370985078 and native
package/attestations39370984641. The package is the real Linuxx64 CLI; its unpacked
help, scenario validation, source/seed/result invariants, same-seed byte replay and
MalformedConfig4 refusal passed. No rehearsal stub or clinical acceptance is inferred.

Independent main artifact verification downloaded the actual9file archive and
checked ZIPCRC/regular unique members, ELF/executable mode, every file digest, exact
project and pinned Kairos notice bytes, source identity and consumer input/result.
Official frozen SPDX2.3 schema passes. Both gh build/SPDX signatures verify exact
repository/workflow/main/source and signer8ca0e5e with hosted runners; the signed
SPDX predicate equals the downloaded inventory. Archive SHA256:
640df813852c845bb8134abd593ee88b829a6192716ca73a10c302acb8d57fda.
Cargo.lock remains separate source-resolution evidence, not full binary closure.
Raw receipts remain private internal .local/sim-native-main-8ca0e5e.

The old single-file Rust PR157 is closed and superseded by coordinated PR169
(37de980/Rust1.99.1); earlier records retain their actual compiler identities.
Rust canary PR166 is merged atffe2f10 with all applicable checks passed. Current
main development refreshes39376080429(Rust) and39376083693(schema) are running;
record their actual terminal receipts before claiming refreshed candidates.

Whole-suite tasks remain open for private hosted qualification, protection and
release evidence. Public Sim completion does not substitute for those modules.

Refresh terminal results: Rust39376080429 and schema39376083693 both passed.
Downloaded beta1.100.0-beta.7/compilerfd8e211 and nightly20Oct1.101.0/compiler
07e526d each passed296workspace tests, doctests and strict Clippy. All10command
log hashes, both frozen Rust manifests/compiler identities and complete source/
submodule snapshots independently match. Both schema lanes3.14.8/3.15.0 passed
all11stages with downloaded lock/inventory hashes verified. Newer Python preview
remains unavailable and unexecuted; no canary promotion/native writes occurred.

Private RIMS39257208210 attempt3 again refused both jobs before any steps;
actual fresh annotations confirm billing. Stop unchanged retries pending the
external billing condition. This is not executed test failure or source adoption.


## Private package policy reconciliation — 20 October 2026

Finance15, Costing19 and Decisions53 remain draft and unmerged. Each now
integrates its latest source-CI candidate and uses qualified policy6319d0c for
both shared checks and actual-package inventory tooling. Actionlint, offline
pedantic Zizmor and diff checks pass on the changed workflows. Prior package
hashes and hosted billing receipts retain their original source identities;
these local workflow checks do not establish new-head hosted package execution.
Exact candidate heads are recorded in portfolio/ci-rollout.json.

Private GitHub artifact attestations require Enterprise Cloud according to
[GitHub documentation](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
The authenticated account API did not expose plan eligibility. This prerequisite
is separate from the observed zero-step Actions billing refusals; neither an
account payment repair nor a local SBOM establishes signing availability.
Keep source CI and signing qualification pending without purchase, visibility
changes, public transparency submission, new credentials or bypass. Next:
once hosted execution is available, qualify the exact source-CI heads, then
these stacked package candidates and their private main-only signing route.
