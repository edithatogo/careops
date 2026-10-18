# Suite CI/CD plan

Status: in progress. Existing user goal retains the full suite scope.

## 1. Contract and ownership
- [x] CI1.1 Refresh current heads, workflow/dependency inventory and check protection.
- [x] CI1.2 Assign RIMS/PPG/Clinical Hub CI to existing chats; parent retains shared workflows and remaining modules. No new chats or acknowledgement polling.
- [x] CI1.3 Implement common contract, trustworthy upstream resolution, lock generation and outcome classification with negative tests.
- [x] CI1.4 Qualify foundation on GitHub, merge only with every check green, publish immutable adoption revision.

## 2. Dependencies and shared CI
- [ ] CI2.1 Qualify latest parent tools/actions, automate lock repair/update proposals and verify an actual generated-lock update.
- [x] CI2.2 Implement reusable source/workflow/security baseline; retain existing test commands and independently runnable modules.
- [ ] CI2.3 Roll out to every owned module in the rollout matrix, qualify action/submodule updates without disturbing owner work.
- [ ] CI2.4 Verify required checks and update automation through native API and fresh runs; merge sequentially with all checks passing.

## 3. Development canaries
- [x] CI3.1 Scheduled bounded tool/runtime development candidates, exact version and integrity receipts; no native writes or automatic promotion.
- [ ] CI3.2 Exercise candidate resolution and representative failure; preserve working lock and record promotion/recovery conditions.
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
