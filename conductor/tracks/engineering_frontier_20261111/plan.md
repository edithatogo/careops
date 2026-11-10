# Technical frontier — executable implementation sequence

Status: **all tasks below open**, except previously completed work identified as an existing dependency. Documentation completion is not implementation. No operational-effectiveness evaluation is in scope.

Task IDs are stable. Every task's completion receipt must state changed paths, source/head SHA, focused RED/GREEN test (for behaviour), full relevant integration gate, detected defects and exact qualification scope. A documentation-only plan update cannot close an executable task. Keep existing one-maintainer workflow; modules run independently.

## EF-00 — Restore trustworthy integration (P0)

Depends on existing `suite_ci_delivery_20261018`; current blocker #301. Existing required checks and branch protection must remain intact.

- [ ] **EF-00.01** Classify each open PR's *latest exact head*: passed, executed failure, unexecuted/billing, skipped, conflict, and superseded. Capture a machine-readable, non-sensitive summary.
- [ ] **EF-00.02** Restore or obtain genuinely executable hosted Actions for protected heads. Retain failed/billing receipts; do not disable required checks, forge statuses or merge on local evidence alone.
- [ ] **EF-00.03** Rebase/reconcile the eligible technical PRs one at a time (notably #309/#311/#312 and dependency PRs), run exact-head tests, merge normally and verify receiving-main checks. Leave draft/conflicting work queued.
- [ ] **EF-00.04** Reconcile required check contexts with current CI workflow and private-repository release eligibility; record unavailable signed artifacts as unsupported, not passed.

**Exit:** every merged candidate has actual eligible green exact-head checks and checked receiving-main; all blocked candidates remain clearly pending.

## EF-01 — Inventory and benchmark the real engineering harness (P0)

Owner: parent `harness/`, `AGENTS.md`, `.github/agents`, `.github/skills` and existing child-agent instructions. No new mandatory agent platform.

- [ ] **EF-01.01** Inventory executable entrypoints, agent skills, task/test mapping, source/module topology and trust boundaries; distinguish present, script-only, documented-only and not qualified.
- [ ] **EF-01.02** Freeze a synthetic task corpus spanning at least six modules with precise expected owner/context/tests/refusals and baseline current-harness execution evidence.
- [ ] **EF-01.03** Audit stale/conflicting instructions and unnecessary context copies; repair the current platform-architect agent's historical polyrepo assumption without changing source topology.
- [ ] **EF-01.04** Benchmark current context relevance, missing critical facts, extra context, unsafe tool proposals, tool count and reproducibility.

**Exit:** repeatable baseline command and fixture manifest; at least one real baseline failure/limitation reproduced and tracked.

## EF-02 — Deterministic context packets and tool mediation (P1)

Depends EF-01. Use existing source registry, profile, `run_tests.py` and JSON Schema validator where possible.

- [ ] **EF-02.01** Write failing fixtures for wrong module ownership, stale source, missing/overbroad task scope, invalid tool request and injected instructions.
- [ ] **EF-02.02** Implement EF-C01 task packet generation and bounded retrieval with content digests and current source/gitlink proof; verify RED → GREEN and independent module install.
- [ ] **EF-02.03** Implement EF-C02 policy gateway with allowlisted operations, task-local paths, no ambient secrets, no recursive privilege elevation, capped tool/attempt budgets.
- [ ] **EF-02.04** Implement a read-only/plan-only dry-run operation and deterministic log/denial receipt. Exercise a fake tool service attempting network, tenant and email effects.
- [ ] **EF-02.05** Integrate existing Conductor and agent instructions with the new entrypoint; ensure direct non-agent workflows remain unchanged.

**Exit:** passing adversarial and non-AI tests; no new mandatory service, consent or premium dependency.

## EF-03 — Unified developer and execution harness (P1)

Depends EF-02; reuse `portfolio-scripts/run_tests.py`, PowerShell `Test-Harness.ps1`, module-native runners and GitHub Actions.

- [ ] **EF-03.01** Add one offline command to resolve owner, task packet, smallest valid focused tests and native/build prerequisites from changed paths; compare selected set to a known-full test inventory.
- [ ] **EF-03.02** Test fresh checkout, missing optional module, missing runtime, denied permission, concurrent change, disabled network and stale lock; never auto-install credentials or follow floating dependencies.
- [ ] **EF-03.03** Add source-only test/build/review/pack mode and reproducible cache keyed by source/toolchain/fixtures; full required release checks remain independent.
- [ ] **EF-03.04** Produce EF-C03 evidence in no-PII JSON, including non-executed classifications and failed command identity.
- [ ] **EF-03.05** Add code-agent repair flow that proposes a patch to a disposable branch, reruns failing test and obtains independent reviewer/check results; no self-approval/auto-merge.

**Exit:** identical inputs yield identical task selection/evidence and no disallowed tool execution; full release gate still executes.

## EF-04 — Quality engineering and compatibility (P1)

Module owners retain domain tests; the parent controls cross-module contracts. Reuse existing Hypothesis/property, mutation/metamorphic, Playwright and source-package tools where already implemented.

- [ ] **EF-04.01** Build a module-by-module coverage *matrix by failure mode*, not tool-name checklist: malformed input, duplicate/replay, concurrency, schema/version, licence, restore, permission, optional absence, degraded offline mode.
- [ ] **EF-04.02** Add contract fixtures EF-C08 and required no-AI/non-premium tests for two existing producer/consumer seams before expanding to all selected interfaces.
- [ ] **EF-04.03** Use stateful/property/metamorphic tests on selected consequential code; introduce mutation testing only where it demonstrates a missed bug, with reproducible seeds and survivor review.
- [ ] **EF-04.04** Add failure injection and representative performance budgets to sync/retry, typed caches and Power Platform package generation; keep CI run-time bounded with separately scheduled deep jobs.
- [ ] **EF-04.05** Reconcile browser and native Power Platform testing on actively supported tools; verify actual authoring outputs, not only mocked parsers.

**Exit:** evidence of meaningful defects caught and no high-severity known contract mutants surviving selected critical tests.

## EF-05 — Privacy, application security and agent abuse resistance (P1)

Depends existing security/CI and PR #311; do not duplicate scanners or weaken current reviewed baselines.

- [ ] **EF-05.01** Establish explicit trust and data-flow threat models for source, PRs, docs, tools/MCP, execution sandboxes, native target selection and release artifacts.
- [ ] **EF-05.02** Extend synthetic privacy/secret test corpus to encoded forms, Office/archive/binary limitations, corpus poisoning and adversarial source inputs; record scanner coverage and gaps.
- [ ] **EF-05.03** Audit permissions at every tool boundary (GitHub, filesystem, network, native Microsoft) and implement least-agency test cases with deny-by-default receipts; do not put authority only in prompts.
- [ ] **EF-05.04** Reconcile SAST, dependency/OSV, licence, malicious package and API-surface scanning at their existing owners; review exact findings and time-limited exemptions.
- [ ] **EF-05.05** Run recurring synthetic red-team tests for tool-output injection, forged approvals, cross-module leakage, prompt/context tampering, write-chain escalation and unsafe recovery.
- [ ] **EF-05.06** Prove local logs, test artifacts and agent context exclude classified source and secrets; preserve only minimal necessary hashes/path references.

**Exit:** known synthetic critical attacker cases are denied by executable policy; scanner coverage/exclusions are reported honestly, not as complete de-identification.

## EF-06 — Supply chain and reproducible release (P1)

Depends EF-00 and existing suite CI track. Do not infer eligibility for private GitHub-attestation features.

- [ ] **EF-06.01** Map selected module release chains against NIST SSDF, SLSA source/build controls, SPDX/CycloneDX, pinned Actions, integrity and exact builder identity; preserve unqualified states.
- [ ] **EF-06.02** Verify package bytes, SBOM dependency/file closure and upstream provenance with adversarial tamper fixtures. Reuse existing source-packaging workflows.
- [ ] **EF-06.03** Qualify signing/attestation *only where supported*; otherwise prove independent digests/downloads and record signature unavailable.
- [ ] **EF-06.04** Standardise versioned rollback, source provenance and reproducible rebuild across two representative package kinds, then expand.

**Exit:** independent verifier rejects deliberately altered candidates and identifies exact usable recovery revision.

## EF-07 — Non-premium Power Platform source and native automation (P1)

Owner: existing Approve/Decisions/PPG/Clinical Hub/RIMS/native ALM tracks. No new mandatory central Power Platform service.

- [ ] **EF-07.01** Define and test EF-C04 connector/licensing manifest; negative fixture has premium, unknown, custom and hidden Dataverse reference.
- [ ] **EF-07.02** Validate generated Power Automate flows, SharePoint resources, PBIP and solution packaging for exact source/component coverage, typed fields, versioned deployment dependencies and standard-connector functionality.
- [ ] **EF-07.03** Isolate dev/test target identity and build exact-target readback tests; prevent fallback to ambient PAC/CLI sessions or guessed connector fields.
- [ ] **EF-07.04** Add native test matrix for idempotency, ETags, pagination, failure/restore, access controls, concurrency and stopped-flow recovery, retaining separate qualification from offline tests.
- [ ] **EF-07.05** Build representative typed, replayable file snapshot interchange with minimal dependency (JSONL+schema/SQLite/Parquet as selected), preserving lineage and a clear source-authority boundary.

**Exit:** a non-premium core module is installable independently in an appropriately qualified environment; unknown entitlement and native readback remain explicit holds.

## EF-08 — Frontier and beyond-frontier engineering evaluation (P2)

Depends EF-02–07. This work evaluates **technical properties only**, not health-service effectiveness.

- [ ] **EF-08.01** Establish EF-C06 fixed benchmark and exact baseline for context routing, test discovery, policy refusal, repair correctness, wall time and resource cost.
- [ ] **EF-08.02** Prove task packets outperform or equal current manual/source-guided approach in correctness and completeness without increased unsafe actions.
- [ ] **EF-08.03** Compare agent-free deterministic automation, optional single agent and optional multiple agents using identical fixtures, budgets and external permissions; no assumed advantage from extra agents.
- [ ] **EF-08.04** Add constrained architecture-aware impact selection and generated regression fixtures, independently verified against exhaustive selected tests for false-negative coverage.
- [ ] **EF-08.05** Evaluate self-repair on intentionally broken synthetic branches: reproducible RED, bounded proposed patch, GREEN and independent adversarial review; blocked protected merge must remain blocked.
- [ ] **EF-08.06** Publish versioned non-sensitive machine-readable results and limitations alongside the repository; keep real private data and native receipts external.

**Exit:** evidence demonstrates at least one independently repeatable technical improvement and records failure modes; do not call the platform beyond frontier merely from the presence of this plan.

## Immediate sequencing / ownership

1. **Now:** EF-00 and EF-01 discovery are the only critical-path blockers; avoid launching new expensive module restructures while hosted runs cannot execute.
2. **Parallel source-only work:** EF-02 packet schemas and negative fixtures, EF-04 failure-mode matrix, EF-05 threat/coverage fixtures. Existing PR #311 remains the shared scanner owner.
3. **Then:** EF-03 execution harness; EF-06 exact package verification; EF-07 non-premium/native qualifiers; EF-08 benchmarking.
4. **Release:** Reconcile existing parent/module tracks, preserve history, mark tasks complete only after exact evidence; keep queued PRs unmerged until their true current-head checks pass.

**Do not create separate committees or review bureaucracy.** A coding agent, an existing independent source reviewer and CI checks suffice for source changes; native operation retains its established owner.

---

## 11 November 2026 — implemented source slice and remaining proof

The linked [implementation checkpoint](implementation-20261111.md) records the first **offline** EF-02 task/context and CI status preflight, the attached synthetic negative tests, and its explicit non-enforcement boundary. [CI triage](ci-reconciliation-20261111.md) identifies all 19 open PRs without calling failed/unexecuted checks successful. [Publication risks](publication-sensitivity-20261111.md) are separate from CI and do not authorize visibility changes.

**EF-00:** Current-hosted execution and protected merges remain blocked, not qualified. **EF-01:** harness inventory and corrected source topology are partial; baseline benchmark still pending. **EF-02:** packet + offline permission preflight written; no external tool-gateway enforcement. **EF-03:** local parent test selector and non-sensitive check receipt written; no integrated selected runner, agent execution, repair or cross-module cache. All existing unchecked tasks remain unchecked pending genuine runtime/host evidence.

Platform-native CI details and constraints: [technical ALM assessment](../../../docs/platform-native-ci-frontier-20261111.md). No clinical effectiveness work is added.
