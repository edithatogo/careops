# Suite CI/CD plan

Status: in progress. Existing user goal retains the full suite scope.

## 1. Contract and ownership
- [x] CI1.1 Refresh current heads, workflow/dependency inventory and check protection.
- [x] CI1.2 Assign RIMS/PPG/Clinical Hub CI to existing chats; parent retains shared workflows and remaining modules. No new chats or acknowledgement polling.
- [~] CI1.3 Implement common contract, trustworthy upstream resolution, lock generation and outcome classification with negative tests.
- [ ] CI1.4 Qualify foundation on GitHub, merge only with every check green, publish immutable adoption revision.

## 2. Dependencies and shared CI
- [ ] CI2.1 Qualify latest parent tools/actions, automate lock repair/update proposals and verify an actual generated-lock update.
- [ ] CI2.2 Implement reusable source/workflow/security baseline; retain existing test commands and independently runnable modules.
- [ ] CI2.3 Roll out to every owned module in the rollout matrix, qualify action/submodule updates without disturbing owner work.
- [ ] CI2.4 Verify required checks and update automation through native API and fresh runs; merge sequentially with all checks passing.

## 3. Development canaries
- [ ] CI3.1 Scheduled bounded tool/runtime development candidates, exact version and integrity receipts; no native writes or automatic promotion.
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
