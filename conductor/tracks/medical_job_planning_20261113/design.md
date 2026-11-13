# Medical Job Planning — architecture and decisions

**Status:** proposed; not a native Power Platform solution, deployment record, operational policy or approval. Read [integration contract](integration-contract.md) for normative inter-module semantics and [requirements](requirements.md) for acceptance criteria.

## D-01: independent CareOps module

Admit the reviewed v0.4.2 prototype, if permitted by source-boundary/provenance checks, into a proposed independent `modules/careops-medical-job-planning/`. It must install and operate without CareOps Workforce BI, Approve, PPG, Costing, Finance, Process, Sim, AI or a common runtime. Preserve `modules/careops-workforce/` as the separate, existing PBIP/TMDL report and 66-private-feed contract; do not silently redirect its report or redefine current feeds.

Proposed module tree (not yet created): `domain/` pure deterministic calculations; `contracts/` versioned schemas and fixtures; `adapters/sharepoint/` native mapping and reference tests; `adapters/local-policy/` verified offline snapshot; `powerplatform/` Studio/solution-authoritative actual source only; `provisioning/` dry-run manifests; `design-reference/` clearly non-importable Canvas and inert WDL documents, if admitted; `tests/`, `docs/`, `.careops/module.json`, `AGENTS.md`, `README.md`, `SOURCE_PROVENANCE.json`. Never present illustrative YAML as importable .msapp or a template WDL as a functional flow.

## D-02: source-of-truth and canonical identity

| Record | Owner | Identity/grain and invariant |
| --- | --- | --- |
| PractitionerRef | Existing authorised HR/person system | Source-qualified identity and edition, not a new employee master; private mapping |
| PositionRef | Authoritative establishment ledger | Position + effective interval + funding/organisation owner; may exist vacant |
| EmploymentAppointmentRef | HR/payroll | Appointment/contract version, FTE, classification and industrial instrument |
| ServiceAssignmentRef | Authorised workforce allocation source | Person-position-service + effective interval, multiple simultaneous assignments allowed |
| ServiceRequirement | Medical Job Planning or approved service-design authority | Coverage requirement/service/role/time slot, separately approved |
| PlanHead | Medical Job Planning | Plan ID, status, generation and last operation; minimal, not growing history |
| Draft | Medical Job Planning | Owner-scoped editable revision and ETag |
| PlanVersion | Medical Job Planning | Immutable submitted hash, effective interval, policy snapshot reference |
| PlanSession | Medical Job Planning | Activity category, service, timing, hours, CST status per PlanVersion |
| AnnualisedCommitment | Medical Job Planning | One versioned additional/replacement commitment with inclusion mode |
| ReviewCase/Task | Medical Job Planning | Version-specific human consultation, clinical, industrial and delegate stages |
| Decision/Consultation | Medical Job Planning or authoritative optional decision provider | Authenticated actor, effective delegation, decision, source payload hash |
| PolicyRuleSnapshot | Medical Job Planning | Adopted external/local rule edition bound to calculation and approval |
| ReviewObligation | Medical Job Planning | Plan + policy edition + due occurrence, independently identifiable |
| OperationReceipt/Artifact | Medical Job Planning | Durable idempotent command, saga state and immutable artifacts |
| CSTDisplacement/Recovery | Medical Job Planning | Independently evidenced exception/recovery, never inferred from session label |
| Roster/ActivityObservation | Existing roster/operations source | Actual vs planned never conflated, read-only source references |
| ReportingSnapshot | Optional Workforce/Costing consumers | Refresh-scoped, privacy-filtered aggregate and completeness evidence |

Every entity must separate occurrence time (UTC), business effective dates, observation/as-of, source revision and issuance time. Where relevant retain local zone and calendar basis. Store authoritative issued versions durably and reconstruct historical as-of state without rewriting prior decisions.

## D-03: rationalise physical SharePoint layout

The upload lists 20 logical Lists (JP_PlanHeads, JP_Drafts, JP_PlanVersions, JP_PlanSessions, JP_AnnualisedCommitments, JP_ReviewCases, JP_ReviewTasks, JP_Consultations, JP_Decisions, JP_RoleDelegations, JP_ReviewPolicies, JP_ReviewObligations, JP_IndustrialRules, JP_ActivityTaxonomy, JP_Operations, JP_Artifacts, JP_Notifications, JP_CSTLedger, JP_ServiceRequirements, JP_ActivityObservations) and JP_ApprovedPlanRecords library. The *four-list* CAS adapter is a bounded subset, not the full physical deployment design.

Do not deploy all 20 automatically. For each logical collection document: exact owner, sensitivity and access cohort, state transition, read/write frequency, natural key, retention, index strategy, growth and 5-year volume, permission scope, offline fallback and rollback. Use site/list/library partitioning where unique SharePoint item-level ACL count would be unsustainable. Confirm indexed views, $skiptoken completeness and physical API access in a representative tenant; Power Apps visible controls are not authorisation.

## D-04: business rules and review lifecycle

The upload's canonical offline engine is `planning_semantics.py` + `domain.py`. Its 0.5-hour reconciliation tolerance, CST rates, supplement/replace annualised commitments, calendar-day proration, half-even rounding, fixed monthly review anchoring and four-stage consultation -> clinical review -> industrial review -> delegated approval **are synthetic candidate rules**. None is an adopted CHHHS industrial policy. Keep rules as versioned, signed-off, effective-dated, explainable policy inputs and test with a golden fixture set approved by medical workforce/HR/IR owners.

State graph: Draft -> SubmittedImmutable -> Consultation -> ClinicalReview -> IndustrialReview -> DelegatedApproval -> ApprovedScheduled -> Active -> Superseded/Retired. Explicit Return, Reject, Cancel, Suspend and Appeal/Review branches as permitted by the adopted policy. A no-change attestation satisfies a due review only under the rule edition that created the obligation, without silently minting a new approved version. A future approved plan activates only on its authorised effective date.

The authoritative writer must verify identity, current service scope, delegation, no-self-approval, exact submitted version hash, policy edition, expected generation and effective time. Optional Approve/Decisions adapters may supply evidence of human decision, but may never silently alter plan state.

## D-05: bounded SharePoint CAS saga and trusted actor

Use the uploaded ETag/IF-MATCH SharePoint REST design as a **reference**, not a qualified native implementation. Correct the existing example ambiguity by requiring ETag-bearing metadata on GET; use exactly the SharePoint response representation qualified in tenant testing, not assumptions from static templates.

1. Resolve the execution identity and delegation using trusted service-side sources; reject caller-asserted actor/role.
2. Create/retrieve operation by (module, command, plan ID, unique operation ID, expected generation, canonical payload hash); reject key collisions with different contents.
3. Prepare immutable artifact with operation ID. Confirm staged artifacts are never visible as approved.
4. Read PlanHead and exact ETag; conditionally commit a single generation increment. HTTP 412 is a conflict, not grounds for wildcard retry.
5. Persist receipt. If interrupted after head write, reconcile LastOperation against artifact hash and recorded command. Quarantine ambiguous cases.
6. Bound 429/backoff/retry and reconcile partial multi-list writes; append audit trace without exposure of confidential plan payloads.

SharePoint is not ACID across Lists. Native Power Automate must demonstrate interrupted execution, duplicate trigger, dynamic delegation, throttling and recovery in a development tenant before relying on this saga.

## D-06: native solution and deployment profiles

One standalone core solution owns actual Studio-authoritative Canvas App, enabled/disabled solution-aware flows, connection references, environment variables and required source-controlled provisioning. An approved native connection and governed settings are prerequisites for actual deployment. App sends drafts through constrained list permissions; protected review/approval/activation/issued-document transitions are server-flow owned.

Initial reference profile uses standard SharePoint Lists and Library plus available Standard connectors, with email sending Off by default. Enable only after separate explicit approval for recipients/content/attachments and send scope. PPG, Approve, Process, Workforce BI, Costing and Sim adapters are optional, separately versioned and independently disabled. Dataverse, Fabric, AI, premium connectors and code-app previews are not core dependencies.

Environment gates: source-only fictional tests; dry-run configuration proof; clean development install and native request/readback; representative test acceptance including access denial and recovery; separately authorised limited pilot; explicit production go/no-go and rollback. CHHHS identity, site, groups, policies, receipts, personnel and records remain in private configuration/records stores.

## D-07: records, security and user experience

Model practitioner-private draft, service-scoped reviewer, industrial/delegated approval, audit/operations and issued plan record access separately. Verify access to direct SharePoint URL, REST endpoint, Canvas, exports, historical revisions, backup and report query. Role-revocation checks must occur at mutation, not only on initial form load. Privacy impact, retention, legal hold, right-to-access/correction and accessibility decisions are operational gates; never rely on UI hiding for security.

Issue an approved plan through a controlled template and preserve source/record version, human sign-offs, unresolved annotations, checksums and revision provenance. A generated Word/PDF artifact is not approval or circulation. No private plan or person data in public Git/CI or illustrative source fixtures.

## D-08: optional integration, versioning and quality

Use [integration-contract.md](integration-contract.md) as the normative per-adapter agreement and [contracts/envelope.schema.json](contracts/envelope.schema.json) as a machine-readable schema. Core is the only writer of job-plan lifecycle; adapters exchange source-qualified IDs, immutable references, redacted events, data-quality assertions and explicit human approvals only. Run standalone, missing-provider, stale-provider, mismatch, privacy, small-cell and replay tests for each adapter before any enablement.

Decision-record changes must be versioned; incompatible major versions are not silently accepted. Analytics consumers receive only approved aggregate scopes with completeness, suppression, denominator and as-of flags; no employee performance inference from plan data. An unavailable adapter cannot prevent core reads, create a default approval or produce falsely complete reporting.


## D-09: industrial interpretation is a versioned configuration, not a code constant

The current reference is [MOCA7, QIRC CB/2025/128](https://www.qirc.qld.gov.au/sites/default/files/2025-11/2025_cb128.pdf), operative 29 October 2025. For SMOs covered by clause 11.18, **minimum individual clinical support time is 10% of contracted ordinary hours per fortnight**; where that cannot be provided fortnightly, the SMO is consulted and time made available at an appropriate later point. Clause 11.18 also addresses protected ordinary-time purpose, Clinical Director consultation, usual place of work, other income and fatigue substitution. This is source evidence, **not a declaration that a specific CHHHS policy/rule has been approved or that other medical classifications have identical entitlements**. Verify current awards, agreements, preserved policies, classifications, individual arrangements and effective dates before adoption. See [W-1](pre-implementation-decisions.md).

Domain structures must distinguish `CSTEntitlement`, `PlannedAllocation`, `RecordedAccess`, `Displacement`, `Recovery`, `Shortfall` and `UnresolvedDispute`. These must not derive actual access from a scheduled block, nor erase an outstanding entitlement on a shortfall. Always preserve source edition, exact clause, rule version, effective interval, actor interpreting/adopting it and an auditable manual override. The existing v0.4.2 `0.5`-hour annualised tolerance, `fixed-grid` review cycle and synthetic `minimum_cst_fraction` stay unadopted until approved by policy authority. Add clause-based golden examples and independent legal/HR/IR review; machine checks cannot themselves adjudicate employment rights.

## D-10: secure storage choice is evidence-led

The user-selected starting preference remains SharePoint Standard, but the physical architecture is **provisional**. The storage ADR compares it with an independently licensed optional Dataverse profile on least-privilege ACL and direct API/file access, unique-scope projections (Microsoft recommends below ~5,000 unique scopes per list/library), historical revocation, indexed/delegable query accuracy with >5,000 records, isolation and permissions over five years, source history/retention, CAS transaction repair and measured total operational costs. Do not confuse 5,000 recommended *unique permissions* with the separate list-view threshold or with supported maximum 50,000 permissions; these are different controls. A physical permission breach blocks the design even if a low-cost/non-premium profile is desired. Partition by real security cohort when justified; a Canvas `Filter()` is not an ACL.

## D-11: negotiated review and industrial disputes

Represent at least `Draft`, `Proposed`, `Counterproposed`, `AgreedWithConditions`, `Disputed`, `Escalated`, `SubmittedImmutable`, `ReviewPending`, `FormalApproved`, `Issued`, `ScheduledEffective`, `Effective`, `Superseded` and `Retired`, with separately tracked cancellations and returns. A counterproposal produces an immutable evidence-linked new proposal revision, never edits the already-issued version. **Clinician agreement, Clinical Director negotiation, industrial advice and legal/delegated authorisation are independent evidence items**; a negotiated agreement alone does not approve a new plan. Preserve counterparty response, comments/conditions as restricted evidence references and human escalation. Do not automatically reject a valid shortfall or disagreement to create a green compliance metric.

## D-12: strict input and cross-engine arithmetic

The v0.4.2 `activities_from_sessions` implementation uses `ordinary=bool(raw.get(...))` and `cst=bool(raw.get(...))`. Therefore, the nonempty strings `"false"` and `"true"` are accepted and interpreted as `True`. This is a reproducible input defect, **not fixed by this planning update**; write a failing regression and fix it in the source-admission branch before any accepted plan data. Session input contract must use exact JSON booleans, bounded integer week/day/minute fields, non-empty code and site, prohibited unknown keys and no ambiguous float-to-decimal conversions. Numeric calculations must be compared through explicit golden fixtures across Python/Power Fx/flows, with exact rounding and date/zone policies. Test wrong type, corrupt values, overlapping sessions, incorrect CST flags and partial records.

## D-13: native identity chain and current Microsoft test route

The actual Canvas caller (possibly interactive), Power Apps flow trigger payload, run-only flow connections, service connection principal, SharePoint delegated rights, and authoritative current approval/delegation record are **distinct** trust boundaries. Prefer least-privilege service-side verification with an issuer-authenticated actor; the caller-provided `userUPN`/`role` are hints only. Tests attempt wrong-service, stale-delegation, self-approval, flow-owner connection elevation, unauthorized direct SharePoint URL and unauthorized historical/export access. Preserve the trusted actor/connection decision in private audit.

Use current supported PAC/Power Platform source routes, Microsoft Solution Checker and maintainable **Playwright** UI E2E tests; Microsoft deprecated Power Platform Test Engine in April 2026. Test Power Fx delegation and explicit full pagination with >5,000 synthetic records, plus missing/denied pages. Native cloud authentication and actual execution require their own qualified evidence, not source lint.

## D-14: clinician-first journey and service view

Produce one minimum usable *fictional* SMO experience before attempting all nine prototype screens: open a verified prepopulated plan, edit and reconcile sessions, identify CST entitlement/shortfall, negotiate a counterproposal, submit, receive a reason-coded human review, record delegated decision, issue immutable history and demonstrate the unresolved dispute path. A separate Clinical Director service view aggregates permitted planned service coverage, leaves, position vacancies and constraints **without treating a valid individual's plan as sufficient service staffing**. Verify accessibility and keyboard/reader behaviour; account for mobile and long sessions. No default auto-email.

## D-15: activity ontology, metrics and evaluation

Controlled activity taxonomy has stable source-qualified terms and independent attributes: care directness, CST eligibility, time class (ordinary/overtime/on-call/recall), role, site/service, date interval, funding source, contract basis, learning/research/governance domain, evidence status and potentially multiple classifications. Preserve distinctions between `entitlement`, `planned`, `committed`, `approved`, `observed`, `recovered`, and `unverified`. No assumption that a clinician's scope of practice or competence is inferred by activity labels.

Every cross-CareOps metric has a versioned definition, grain, units, denominator, source provenance, missingness/suppression policy, effective/as-of date and intended purpose; see [activity taxonomy](contracts/activity-taxonomy.json), [metric dictionary](contracts/metric-dictionary.json) and [integration contract](integration-contract.md). Baseline and post-pilot outcome collection must include practitioner/admin net effort, negotiation steps, accessibility, turnaround, rework, unresolved disputes, CST access versus allocation, anomalous data, actual service coverage (only from independent authorised sources) and adverse/unintended consequences. Costing and simulation are deferred to measured value after source quality, not required for core operation.

## D-16: executable contract proof before adapters

The versioned integration envelope is **not sufficient alone** for quality assertions. Add pure semantic conformance tests with explicit rules for matching module directions, message purpose, UTC timestamps/effective intervals, population grain, missingness, redaction, suppression, conditional decision evidence and exact interpretation of `complete/partial/unavailable`. Do not force JSON Schema to express inter-field numerical arithmetic it cannot represent. Implement cross-field checks in an independent standard-library semantic validator and use the project's existing pinned `jsonschema` implementation for Draft 2020-12 shape validation. All current positive fixtures must pass; adversarial schema and semantic fixtures must fail. Actor/delegation trust and external permissions remain **native-only** negative tests.
