# REGASSURE-20261113 — executable Conductor integration plan

**Stage:** source-only reference implementation partially delivered; G0 rights and G1 durability/qualification remain open, G2/G3 not authorised.  
**Implementation location:** `edithatogo/careops` on a feature branch; proposed implementation root `modules/careops-registration-assurance/` only after source admission and selected module architecture acceptance.  
**Parent dependencies:** N03 register ownership, N05 checks, N07 workbench, N09.04 optional Ahpra/Workforce adapter, N10 assurance and N12 operations.  
**Authoritative contracts:** [integration](../../../docs/credentialing/registration-assurance-integration-contract.md), [requirements](requirements.md), [design](design.md), [machine observation schema](registration-observation.schema.json).

## Work strategy

Use one selected owner per source and target object. Reconcile branch, PRs, source registry, existing native objects and test contracts before each implementation slice. Work in contract-driven, tests-first increments, then Conductor implement → independent review → correct findings → rerun targeted tests → accepted CI → protected merge; archive a track only when its scoped requirements and acceptance evidence are actually complete. Keep proposed external provider activation and tenant implementation in separately gated work, not a blocker for synthetic source-contract delivery.

The original task tables below describe the complete contracted work and should not be reinterpreted as complete merely because the new source reference exists. "Blocked" applies only after identifying a specific missing external dependency. Source migration is not approved by this plan; the AHPRA archive is a local evidence input, not public source.

## Phase 0 — source admission and contractual foundations (G0)

| Task | Priority / depends on | Executable work and measurable exit evidence |
| --- | --- | --- |
| RA-T01 Inventory and reconcile | Must / none | Record main SHA, open credentialing/standard-M365 PR changes, in-tree module topology and N03/N09 owners; archive SHA, 67-file list, three package generations; no duplicate branch/source import. Diff provenance against any same-name existing assets. |
| RA-T02 Source rights and safe admission | Must / T01 | Confirm archive ownership, Apache-2.0 compatibility or reuse permission, third-party notices; static review of all files for staff records, endpoints, secrets and operational identifiers. Produce allowlisted public-source manifest. Refuse unqualified artefacts. |
| RA-T03 Repair package portability | Must / T01–02 | Replace absolute working-directory assumptions in four failed validators/builders, deterministic paths/config and clean temporary output; demonstrate cold-checkout runs under repository's pinned Python 3.15.1 with positive and corrupt-input negative tests. |
| RA-T04 Machine contract and examples | Must / T01 | Implement/validate `RegistrationObservation` schema plus synthetic positive/negative fixtures; verify all invariants in normative contract, version rejection and test-only/discovery-only evidence ceilings. |
| RA-T05 Qualified provider capability table | Must / T02, T04 | Record each provider's permitted use, access/license, source field mask, freshness, date semantics, claim ceiling, failure/retention and enable flag. Autocomplete operational mode held. PIE adapter remains disabled pending issued spec. |
| RA-T06 Architecture/ownership ADR | Must / T01, T04 | Bind standalone monitoring state to approved owner and optional Decisions adapter; no second master, mandatory premium HTTP, live parent runtime, direct Dataverse write or implicit email. Document independent installation and recovery route. |

**G0 evidence:** signed-off public-safe contract+schema, requirements traceability, uploaded-source receipt kept privately, current-branch source inventory, exact-head required CI checks, explicit `source-only` release note. The present planning PR may satisfy the *documentation portion* of G0 once merged; T02–T06 and clean-checkout implementations remain outstanding.

## Phase 1 — deterministic registration assurance core (G1)

| Task | Priority / depends on | Executable work and measurable exit evidence |
| --- | --- | --- |
| RA-T07 Mock/manual adapters | Must / T03–05 | Pure fictional fixture/mocked transport, explicit disabled live source; manual reviewer evidence route for legitimately captured register checks, with actor/time/version. Test missing provider, malformed input and no network. |
| RA-T08 Source-qualified identity | Must / T04, T07 | Exact regulator+registration number match, duplicate/collision/alias ambiguity, profession conflict and missing number. Negative tests prove name-only and first-five suggestions never resolve or auto-join. |
| RA-T09 Source-status classifier | Must / T05, T07–08 | Deterministic health/match/signal/review axes with source capability ceiling. Test blocked, drift, timeout, stale, expiry grace, unknown status and genuine verified adverse; any adverse produces review only. |
| RA-T10 Event and replay engine | Must / T08–09 | Append-only normalized observations, bitemporal as-of/observed-at, stable idempotency and selective supersession. Test identical replay, out-of-order reply, provider-switch and corrected source without clobbering review. |
| RA-T11 Resumable job and fault contract | Must / T09–10 | Request jobs, bounded retry/backoff, leases, deadlines, circuit breaker, dead-letter ownership and inbox/outbox; prove no absent source becomes a clean result, no ambiguous-send duplicate and no whole-case blocking. |
| RA-T12 Minimal exception review API | Must / T09–11 | Read-only review queue contract with reason, source evidence, currentness, suggested priority and expected revision; reviewer actions recorded separately. Conflicting/stale corrections are held, not silently accepted. |
| RA-T13 Source integration tests/CI | Must / T07–12 | Contract fixtures, Hypothesis/property and metamorphic tests, identity collision, malformed/XXE XML, generated WDL JSON validation, security/secret/SBOM/privacy and isolated no-network tests. Use source generator for packed artefacts and compare semantic diff. |

**G1 evidence:** accepted source-only module/adapter contract, cold-checkout deterministic tests and current-head CI, marked source/fixture limitations, no credentials, real records, notifications or native deployment. Keep source-only failure rates separate from external production performance.

## Phase 2 — native integration and optional PIE (G2)

| Task | Priority / depends on | Executable work and measurable exit evidence |
| --- | --- | --- |
| RA-T14 Native storage and ALM | Must / T06, T10–13 | Define solution-aware Dataverse/Power Apps/Power Automate pack as approved, with monitoring-owned entities only, restricted evidence reference, environment-variable/connection references, assigned identity, permissions and standard-vs-premium licensing matrix. Perform dry install/uninstall/upgrade in isolated approved environment and inspect dependency tree. |
| RA-T15 Decisions adapter | Must / T06, T12, T14 | Stable versioned source-reference interface using existing Decisions practitioner identity and human governance; source observation cannot activate, suspend, renew or delete registration. Test direct API privilege bypass, stale approved case and register readback under actual native security. |
| RA-T16 Review workbench | Must / T12, T14–15 | Accessible queue and explicit human verification with original source, as-of time, conflicts, status mapping, no preview implying approved scope, versioned disposition and recovery tests. |
| RA-T17 PIE access and contract qualification | Must for automated PIE / T02, T05 | Obtain organisational agreement, issued XML/auth/Find technical specification and data-use rights; field-map fixtures, access-scoped token/identity; record the approved API service, source refresh, check volumes and fees privately. No guessed OAuth2/JSON or API Alerts. If unavailable, mark blocked and retain manual/mock. |
| RA-T18 PIE XML adapter and canary | Must for automated PIE / T13, T17 | Hardened XML parser with DTD/XXE denial; exact spec-driven Find mapping, error taxonomy, capability contract, tenant secret storage, throttle and drift telemetry. Test schema/contract change, 403/429, not-found ambiguity, stale source and rollback. |
| RA-T19 Native operations/security/recovery | Must / T14–18 as applicable | Named account, approved Australian region/PIA, records/legal hold, DLP, credential rotation, access control via direct API/document link, Key Vault, Dataverse/SharePoint restore, quarantined outbox and continuity exercise. Actual native checks required, no source-only inference. |
| RA-T20 Notifications and escalations | Should / T16, T19 | Draft-only notification templates, configurable priority/work owner and manual fallback; default OFF. Never send without explicit approval for exact recipient/content/scope, separate from deploying the solution. |
| RA-T21 Optional consumer adapters | Should / T15, T19 | Bounded source-only/read-only Workforce, PPG/accreditation, Process and Costing payloads. Test denied access, absent provider, unsupported schema, missing staff membership, denominators and no duplicate authoritative write. |

**G2 evidence:** approved tenant/connector identity and regulator access, imported solution readback, actual native access failure tests, source revision and logs, demonstrated no-mail default, duplicate/recovery/restore tests, confirmed licencing and explicit **silent mode**. If source permission is unavailable, the automated PIE gate remains blocked while bounded manual work can proceed independently.

## Phase 3 — evaluation, operating decision, and release (G3)

| Task | Priority / depends on | Executable work and measurable exit evidence |
| --- | --- | --- |
| RA-T22 Baseline and retrospective evaluation | Must / T15–19 | Define eligible practitioner denominator, source age and manual work baseline; independently adjudicate approved, minimum-necessary historical cases. Measure omission/false-match/false-adverse/reviewer time; never benchmark status on suggestion output alone. |
| RA-T23 Prospective silent pilot | Must / T22 | Run a separately authorised, time-bounded silent comparison without employment/SoCP/roster writes or staff emails. Measure source check completion, independent registration agreement, alerts missed/false, review SLA, degraded operations and cost; report uncertainty and sample limits. |
| RA-T24 Controlled commissioning | Must / T23 | Complete named clinical/business/service owner acceptance, current legal/PIE rights, information management/privacy/security and native operational checks, on-call/escalation, rollback and tested recovery. Production enablement is a distinct recorded act. |
| RA-T25 Optional reporting and accreditation outcomes | Should / T21–24 | Validate aggregate denominators and source lineage in existing Workforce/PPG/Process/Costing reporting. Monitor control evidence, not claim wholesale accreditation compliance. |
| RA-T26 Retirement, rollback and provenance | Must / T24 | Quiesce old Excel/List/Logic Apps duplicates, reconcile open jobs and persisted evidence, preserve records/holds, retire only authorised redundant runtimes, audit no duplicate emails or lost cases, verify recovery from qualified release. |

**G3 evidence:** separate human business authorisation, actual provider/tenant receipts, measured pilot results and documented operational outcome. No timeline, cost, clinical success rate, or original live provider access is assumed at source-plan stage.

## Engineering review and test harness

Use CareOps's current pinned Python interpreter, exact locked dependencies, platform test scripts and security tools (`ruff`, strict type checks where applicable, `pytest`/`Hypothesis`, source privacy scans, Gitleaks, static/Power Platform checks, XML safety, provenance/SBOM). Where applicable qualify tests in native .NET and Microsoft PAC/Power Platform solution checker; do not replace native qualification with a Python-only generator/validator. Include negative integration test routes for 403/429, timeouts, malformed/empty XML, WAF challenge/empty autocomplete, common names, duplicate/out-of-order observations, schema-major rejection, expired-with-grace, actual current restriction, reviewer overrides, permission loss, unusable tenant backup, XML XXE, email disabled and unlicensed source.

Review loop for each unit: (1) reconcile exact current main and open PRs; (2) write failing fictional proof; (3) implement smallest accepted delta; (4) check behavior and security/privacy/evidence; (5) inspect native/solution semantics when relevant; (6) fix and rerun; (7) update Conductor acceptance matrix and source inventory; (8) open bounded PR and merge only after *actual* required exact-head checks. Feature branches cannot change main through bypass. Stop automated activation when consent, agreement, live platform or required evidence is missing.

## Status accounting and completion claim boundary

- `planned`: contract/requirements exist; no module feature evidence.
- `source_implemented`: code + fictional tests merged; no production authority.
- `native_qualified`: authorised tenant deployment/permissions and resilience tests evidenced; still not necessarily in clinical use.
- `silent_evaluated`: real comparison measured and limitations documented; no automated decision.
- `operationally_accepted`: separate accountable activation and supported business runbook.

Current documented progress is **planned**. No v3.1 flow is imported, executed or scheduled; no official PIE account, signed agreement, native workflow or real practitioner record has been accessed. Do not mark the track archived while implementation and operating gates remain open. Retain earlier credentialing Conductor accomplishments without reopening or rewriting their evidence.

## Preintegration acceptance amendments

These five work products refine RA-T01–RA-T26 without creating a second module or making optional native pathways a prerequisite for the synthetic proof.

| Deliverable | Owned tasks | Required acceptance evidence |
| --- | --- | --- |
| **RA-X01 Selective-source ADR** | RA-T01–03, RA-T06 | [ADR RA-001](source-admission-decision.md) explicitly accepts/rejects each legacy asset; only selected builder validators are made portable *after* reuse rights and CI relevance are established. No wholesale migration. |
| **RA-X02 Lossless regulatory ontology and tested compatibility** | RA-T04–05, RA-T08–10 | Version 1.1 category/specialty/endorsement/restriction refs preserve regulator-native vocabulary, reject unqualified identity-only status, require explicit source time and review limited/provisional/non-practising/unknown cases. For source version 1.0 inputs, do not emit positive source-verified status without category evidence. Unrecognised future schema versions fail closed until adapter qualification. |
| **RA-X03 Workforce eligible-engagement denominator** | RA-T08, RA-T15, RA-T21–23 | [Coverage/evaluation contract](engagement-coverage-and-evaluation.md): active locum/VMO/contractor/dual-site and regional-service population from independently approved source owners, watch coverage gaps by facility/profession, no inferred employment. Synthetic coverage counts are not real CHHHS results. |
| **RA-X04 Clinical safety case** | RA-T09–13, RA-T16, RA-T19, RA-T23–24 | [Hazard/controls case](clinical-safety-case.md): RA-H01–06 tested at source and actual native boundary; named owner, human escalation, restoration/manual fallback and separately signed residual-risk acceptance before activation. |
| **RA-X05 Evaluation, deployment and accreditation decision** | RA-T14, RA-T20–25 | Single writer and clear Standard-M365/manual vs full Dataverse target; no concurrent active Logic Apps/Power Automate writers. Pre-register sensitivity/PPV, rarity/uncertainty, false negative audit, clinician eligibility, service burden, pricing, source freshness and success thresholds. [QH-HSD-034 and NSQHS 1.23/1.24 crosswalk](engagement-coverage-and-evaluation.md) is process evidence, not a claim of accreditation compliance. |

### Implemented source slice and remaining gates

- **Implemented locally as new GitHub source (feature branch only):** `modules/careops-registration-assurance/src/registration_assurance/assurance.py` (pure deterministic classification, observation replay and watch coverage) and synthetic `unittest` fixtures. No AHPRA calls, private data, production registers, notifications or persistence.
- **Earlier baseline:** 35 synthetic tests passed under the exact Python 3.15.1 GitHub workflow. The expanded 87-method unit/property source suite is committed but its latest-head result and the repository security checks still require exact-head verification.
- **Unimplemented:** source reuse rights and portable retained builders; real contract/mapping/version consumer validator and robust property tests; stable storage/transactions, actual engagement source integration, native Power Platform managed solution, PIE technical specifications/rights, native security/restore, silent evaluation and operational approval.
- **Do not mark RA-T01–RA-T26 complete** based on this source slice. G0 planning and partial G1 reference behaviour only. Hosted workflow billing/queued/refusal is `unexecuted` until an actual terminal job result exists.

## Source expansion and task-state reconciliation — 13 November 2026

| Task cluster | Delivered as synthetic-only code | Remaining acceptance |
| --- | --- | --- |
| RA-T01–03 | Verified 67-file archive digest; documented no original licence, nine absolute-path Python scripts and asset-by-asset reject/retain ADR; no original code copied | Proven reuse rights if any old asset is imported, detailed source classification, selected portability repair only if rights/use justify it |
| RA-T04–06 | Observation schema 1.0/1.1, conditional refusal/format tests, source qualification design and standalone architecture | Actual source interface signed entitlement, compatibility consumer test across native boundary, current clinical policy |
| RA-T07–10 | Mock-like fictional fixtures, exact identity/signal checks, pure reference diff, source temporal checks and in-memory replay | Real approved manual observation pathway, true source identity authentication, durable append-only native storage, concurrency/restore |
| RA-T11 | `jobs.py` bounded lease/retry/dead-letter/ambiguous-delivery + source-only outbox protocol | Real authenticated, transactional, resumable native jobs, durable outbox, idempotent readback and operator recovery |
| RA-T12 | `review.py` versioned, material-diff idempotency and explicit human disposition reference | Actual permissioned clinical review workbench, actor/delegate resolution and native storage-side CAS |
| RA-T13 | 87 authored synthetic unittest methods including Draft202012 schema, review, provider and Hypothesis properties | Exact-head 3.15.1 CI + security/privacy checks, adversarial contract/fuzz/mutation qualification, native tests where applicable |
| RA-T14–26 | Contracts, ADR, hazard analysis, coverage and controlled evaluation requirements only | Managed solution/tenant, PIE approved XML/auth rights, native access/recovery, silent evaluation, named clinical owners, commissioning and later consumer adapters |

**Source implementation ≠ producer authenticity or deployment.** Trust-boundary interfaces in pure code remain test doubles until actual regulator agreements, approved private configuration, real native permission enforcement and validated operational evidence are present. No inference of approved clinical practice or automatic outbound communication is permitted.

## Offline silent-evaluation metric reference (RA-T22, partial synthetic)

`modules/careops-registration-assurance/src/registration_assurance/evaluation.py` provides a pure, independently authored evaluation helper with 12 additional synthetic tests. It requires explicit adjudication status and a nonempty independent-reference record for assessed truth, preserves unknown/abstained cases outside the TP/FP/FN/TN matrix, rejects duplicate engagement denominators, reports Wilson uncertainty rather than treating zero observed adverse events as proof of perfect sensitivity, and refuses a population prevalence claim without explicit representative sampling and a separately asserted verified sampling frame. The code does **not** establish reference-source independence, a valid epidemiological sample, clinical impact, current AHPRA rights or prospective pilot acceptance. RA-T22 and G3 remain incomplete until a separately authorised real comparison supplies qualified evidence.

## Deterministic-core implementation increment (13 November 2026)

The source-only reference core is extended in `modules/careops-registration-assurance/src/registration_assurance/`:

- `identity.py`: exact regulator-number-profession/source-watch identity, effective-dated trusted bindings and explicit collision/ambiguity refusal (RA-T08).
- `deterministic.py`: full 1.1 JSON Schema with format assertions, synthetic-only admission, purpose/source qualification, approved native vocabulary, exact effective identity and reuse of the already selected deterministic source classifier (RA-T04, RA-T05, RA-T09).
- `durable.py`: offline SQLite **reference-only** transaction model for append-only observations, per-watch hash chaining and ledger CAS, independently revised current projection, conflict/old-revision preservation, internal outbox, job/review CAS, simulated crash rollback and recovery manifest (RA-T10–RA-T12). Not a production Dataverse backend and not approved for real records.
- `tests/test_deterministic_core.py`: synthetic end-to-end and adversarial test cases for identity, qualification, duplicate replay, out-of-order evidence, concurrent CAS, rollback, extended projection/outbox/review/job integrity and process owner separation.
- [Deterministic core contract](../../../modules/careops-registration-assurance/docs/deterministic-core-contract.md): interface, exclusions, native parity requirements and verification instructions.

**Maturity:** deterministic reference-core *source authored*, complete only after clean Python 3.15.1 exact-head tests, security/privacy checks and protected merge. RA-T07 manual AHPRA input, actual native protected transaction/security/retention, real provider rights, deployment and operational accreditation remain **open**. SQLite tests must never be confused with actual Dataverse concurrency, transactions, backups, authorization or resilience. No data collected, no jobs scheduled, no emails sent.

### Deterministic core source-test evidence

The registration-assurance GitHub source workflow verified **121/121 methods on Python 3.15.1** at a candidate head on 13 November 2026, including 34 new focused regression methods and the existing 87-method baseline. This verifies the synthetic reference behaviour only; the final commit's exact-head result, protected merge and future native Dataverse/PIE gates remain separate.

### Standalone schema portability correction

The exact 1.1 `RegistrationObservation` Schema is bundled under `modules/careops-registration-assurance/contracts/`, so runtime validation no longer depends on a parent CareOps Conductor checkout. `test_schema.py` verifies byte identity against the canonical Conductor design contract. Previous candidate-head Python 3.15.1 tests: **121/121**; current authored source total is **124** following the parity test, subject to final exact-head CI. Native deployment gates and real-data access remain open.

### Exact security finding remediation

The first current-head Python/OpenGrep source security pass found seven new Bandit/Semgrep SQL-formatting findings in `durable.py` (versioned review/job table interpolation and dynamically formatted recovery count). All SQL table/column identifiers are now **fixed, allowlisted literals** and all values bound as query parameters; no source-security rule exceptions or new reviews were added. Two adversarial synthetic regressions cover rejected dynamic table identifiers and a SQL-shaped case ID as inert data. The resulting 124-method suite and source-security checks require current-head GitHub confirmation before protected merge.
