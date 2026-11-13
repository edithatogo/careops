# REGASSURE-20261113 — executable Conductor integration plan

**Stage:** planned; source-contract deliverables only.  
**Implementation location:** `edithatogo/careops` on a feature branch; proposed implementation root `modules/careops-registration-assurance/` only after source admission and selected module architecture acceptance.  
**Parent dependencies:** N03 register ownership, N05 checks, N07 workbench, N09.04 optional Ahpra/Workforce adapter, N10 assurance and N12 operations.  
**Authoritative contracts:** [integration](../../../docs/credentialing/registration-assurance-integration-contract.md), [requirements](requirements.md), [design](design.md), [machine observation schema](registration-observation.schema.json).

## Work strategy

Use one selected owner per source and target object. Reconcile branch, PRs, source registry, existing native objects and test contracts before each implementation slice. Work in contract-driven, tests-first increments, then Conductor implement → independent review → correct findings → rerun targeted tests → accepted CI → protected merge; archive a track only when its scoped requirements and acceptance evidence are actually complete. Keep proposed external provider activation and tenant implementation in separately gated work, not a blocker for synthetic source-contract delivery.

All tasks below start as **not implemented**. "Blocked" applies only after identifying a specific missing external dependency. Source migration is not approved by this plan; the AHPRA archive is a local evidence input, not public source.

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
