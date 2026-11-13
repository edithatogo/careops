# CareOps registration assurance — integration contract

**Contract ID:** `careops.registration-assurance`  
**Version:** `1.1.0-design` (candidate, not deployed; additive to initial source contract)  
**Date:** 2026-11-13  
**Track:** [registration_assurance_20261113](../../conductor/tracks/registration_assurance_20261113/index.md)  
**Machine envelope:** [registration-observation.schema.json](../../conductor/tracks/registration_assurance_20261113/registration-observation.schema.json)

## 1. Purpose and normative scope

Introduce a **bounded, optional registration-source observation and assurance capability** to CareOps using the provided AHPRA monitoring archive as unqualified source material. The service obtains permitted observations, matches them to source-qualified practitioner references, identifies changes or uncertainty, creates reviewable exceptions, and supplies verification evidence to the existing credentialing owner. It MUST NOT itself become the practitioner register, professional licensing authority, scope-of-practice engine, clinical roster, delegated decision-maker or employment decision-maker.

MUST/SHOULD/MAY/MUST NOT define contract obligations. This document is a *source and architecture contract*, not a statement of production approval, implementation, legal clearance or tenant deployment.

The source package is `ahpra-registration-monitoring-repo-v3.1_2026-11-12 (2).zip`, 67 files, SHA-256 `daca9af1089cd893a318079f6b9a0cfbd7661d51652c39a90a1051fca96e87ff`. It contains three overlapping versioned solutions, builders, validators, Power Automate and Logic Apps definitions, SharePoint schemas and a mock provider. It includes **no licence file**. Keep this source archive outside the public CareOps repository; establish provenance, authorship/reuse rights, privacy and third-party notices before importing any implementation code or binaries. Documentation and synthetic contracts may be developed independently.

## 2. Ownership and deployment boundaries

| Concern | Authority / destination | Exclusion |
| --- | --- | --- |
| Practitioner master identity, employment association, credentialing case, conditions, SoCP and delegated decisions | Existing CareOps Decisions/credentialing owner and its approved enterprise sources; N03 and related native tracks | No duplicate authoritative register, practitioner-employment claims, scope activation or adverse decision |
| Source observations, check attempts, source/contract health and exception candidates | Optional `careops-registration-assurance` capability, proposed source location `modules/careops-registration-assurance/` | No presumption that an observation is a determination |
| Intake and routing | Existing CareOps Approve or approved local standalone intake | Neither sibling module nor central CareOps runtime is mandatory |
| Human review and governance | Decisions/approved credentialing owner through a versioned optional adapter | No agentic or poll-driven credentialing decision |
| Controlled documents and accreditation assertions | CareOps PPG / existing accreditation owner | A stale or incomplete source cannot establish conformance |
| Workforce reporting | CareOps Workforce via read-only, minimum-necessary approved aggregate adapter | No second personnel master or live employment assignment |
| Performance and costing | Process and Costing via minimised events/aggregates | No unapproved practitioner-level telemetry or financial write |
| Evidence/records | Approved SharePoint library / Dataverse reference + retention schedule | No public Git payloads, unmanaged Excel history, personal OneDrive, or second editable List mirror |

The registration-assurance capability MUST work with a synthetic/watch-reference input without installing sibling CareOps products, AI/Copilot or a live Policy Atlas. A file/manual evidence intake is an acceptable standalone supported mode; automated source ingestion is **optional** and only when separately qualified. Integrating with the Dataverse credentialing register MUST use a separately deployed, versioned adapter and preserve Decisions-owned records. The parent repository is build/source composition only, never an operational runtime dependency. No mandatory premium/Azure route shall be concealed inside a standard-M365 profile.

## 3. Provider and permitted-use contract

| Provider | Data use / capabilities | Default |
| --- | --- | --- |
| Synthetic mock | Full fictional regression scenarios; never proof of live service | Available for tests |
| Human-verified AHPRA public register | Individual current registration review, with actual reviewer, source time and durable evidence reference under policy | Opt-in manual path |
| Undocumented public `GetPredictions` autocomplete | At most a name-discovery *candidate*; results may be truncated or blocked; cannot prove registration, expiry, conditions or absence | **Disabled in operational monitoring**; may retain historical compatibility tests |
| AHPRA PIE Find (browser or API where approved) | Official registration verification with AHPRA registration number and contract-qualified field mappings | **Disabled until agreement, documentation, credentials, permitted use and native qualification** |
| PIE Identity | Optional separate identity matching where approved and lawful; do not infer that DOB is returned | Disabled |
| PIE Alerts | Browser-mode alerts where approved; **do not assume API push/webhook capability** | Disabled until confirmed |

The current public AHPRA PIE FAQ says API responses are **XML**, the AHPRA registration number is required, and secure technical specifications are issued after onboarding. The public PIE service sheet describes Find/Identity API access and **Alerts as browser-only**. The archive's presumed JSON/OAuth2 API contract is **unverified**; an endpoint/variable flip is not an implemented PIE adapter. Authentication, rate limits, batching, expiry semantics, status vocabulary, endpoints and permitted persistence MUST be qualified against the issued agreement and interface specification. Do not embed guessed credentials, API schemas, costs or operational commitments.

**Source qualification** MUST record: provider identifier and revision, approved purpose/recipient, source terms and sharing/replication constraints, official interface/schema version, access method, permission/licence receipt (private), data classification, retention boundary, approved field allowlist, freshness, polling limits, operational owner, expiry/requalification and disabled/enabled state. An unqualified provider MUST fail closed; switching to a fallback provider MUST NOT silently expand evidence authority.

Primary regulator material (checked 13 November 2026):
- https://www.ahpra.gov.au/Registration/Employer-Services/External-data-exchange-services
- https://www.ahpra.gov.au/Registration/Employer-Services/External-data-exchange-services/Practitioner-information-exchange/PIE-FAQ
- https://www.ahpra.gov.au/documents/default.aspx?chksum=LPgWES2EkyenaPk0Mm4xZw%3D%3D&dbid=AP&record=WD13%2F12812
- https://www.ahpra.gov.au/documents/default.aspx?chksum=ygED3xFopRlC4xxIULq7zw%3D%3D&dbid=AP&record=WD23%2F32732

## 4. Versioned event and identity contract

The normalized `RegistrationObservation` envelope (machine schema linked above) is the only initial cross-component data product. Required semantic fields are:

- `schemaVersion` (major/minor), globally unique `observationId`, stable `watchRef`, source-qualified regulator namespace, *nullable until established* registration number, correlation ID and deterministic idempotency key.
- Provider kind, qualification/reference, evidence ceiling (`test_only`, `discovery_only`, `qualified_regulatory`, `human_verified`), attempt/observation times in UTC, source-health, source as-of time (when known), source revision and hash/reference to an access-controlled payload.
- Explicit identity-match state (`matched`, `candidate`, `ambiguous`, `unresolved`), normalized registration signal (`registered`, `not_registered`, `suspended`, `cancelled`, `unknown`), expiry as date or null, conditions indicator (`present`, `absent`, `unknown`), and rule-assessment/review status.
- Versioned mapping/rule ID, reasons, source freshness and uncertainty. A receipt or checksum is *not* an identity proof, permission grant or clinical authority.

Practitioner identity is regulator + exact validated registration number, scoped to the source; names, aliases, locations and five-result suggestions MUST NOT merge people or establish employment. Watch references MUST be source-qualified and pseudonymous across optional adapters. The existing credentialing owner alone resolves watch-to-person and employment membership. Source observations MUST be append-only/versioned; supersession does not erase prior evidence or approved human dispositions.

**Conditional invariants (also enforced in code/fixtures, beyond the schema):**
1. An autocomplete observation MUST have an `unknown` registration signal, unknown conditions, null expiry, a `discovery_only` evidence ceiling and no `matched` identity assertion; omission is not deregistration.
2. `blocked`, `rate_limited`, `schema_drift`, `stale` or transport failure MUST produce `unavailable/needs_review` source health, never `not_registered` or `cancelled`.
3. Only a current, qualified PIE Find mapping or independently documented human register check may yield a registration-status verification. Its exact source revision, retrieval/as-of time and field mapping MUST remain inspectable.
4. A future expiry or expired date alone MUST NOT infer unregistration, cancellation or inability to practise; apply current regulator status, renewal/grace guidance and human review.
5. A credible adverse source observation MUST trigger priority review by an authorised owner, not automated restriction, roster removal, employment action or letter.
6. Duplicate delivery, out-of-order old observations, provider switching and retry after ambiguous save MUST NOT rewrite current authority, emit repeated notices or overwrite a reviewed finding.
7. Source-provider timeout/unavailability preserves last known **historical** observation with stale warning and an exception. It is not a current registration confirmation.
8. A candidate, a source-verified fact, a human adjudication, a committee recommendation and a delegate's decision MUST be separate state and audit records.

## 5. Processing and operational invariants

An observation pipeline is `watch intent -> policy-qualified provider -> exact identity reconciliation -> immutable observation -> deterministic comparison -> material uncertainty/exception -> authorised review -> optional downstream reference`. Each check has job ID, version, lock/lease, bounded retry, checkpoint and explicit owner for dead letters. Jobs MUST be independently resumable. Ingestion and decisions MUST use inbox/outbox and compare-and-swap/version checks; no exactly-once delivery assumption. **No silent source substitution** when a provider is absent.

Material changed conditions/status MUST carry `needs_review`, reason codes and temporal evidence until qualified; a correction or verified clean result may supersede an exception but never delete its audit history. Severity is an operational routing aid, not a clinical/legal determination. Regulatory emergency procedures and manual register checking remain available independent of provider, Power BI and AI.

Power Platform solution source MUST be solution-aware and separately packaged for the monitoring core and optional Decisions/Workforce/PPG/Process adapters. Preserve existing native owner and connector identities. Dataverse write protections must be server-side if a write is later approved. SharePoint holds restricted evidence and final artefacts, **not** another editable practitioner master. Use managed identity/approved application identity, Key Vault/connection references, RBAC/field-level controls, managed environments where approved, approved Australian residency, DLP, retention/legal holds, restoration readback and explicit data-flow mapping. External secret or personnel data MUST NOT appear in public source or CI logs.

Email and other outbound notifications are **Off by default**. Under CareOps `AGENTS.md`, no code, schedule, flow or agent sends an email without explicit human approval for the actual recipients, message/attachments and send scope. A plan or credentialing source change is not delivery approval. Prior approved manual escalation pathways remain unchanged.

## 6. Compatibility, metrics and release gates

Supported initial schema major version: 1. Consumers MUST reject unknown majors, missing mandatory fields, unqualified source claims and malformed/ambiguous identifiers; minor-version additions may be ignored only if explicitly allowlisted. Every adapter records source/target version, source revision, purpose, classification, idempotency, acknowledgement/rejection and reconciliation owner. Adapters are independently removable without deleting authority, an approval or the core monitoring history.

Silent evaluation MUST measure eligible watchlist denominator; source coverage and last-success age; exact verified status coverage; identity false matches; false adverse escalation; missed independently verified material changes; alert precision/recall with verification ground truth where measurable; review burden/time; provider failure frequency and recovery; change/decision lag; accessibility; and total run/licensing costs. Use baseline manual checks and independently adjudicated fictional/approved silent cases; never present metrics based on autocomplete suggestions as verified regulatory accuracy.

**G0 source-contract merge**: public-safe contract/schema, MoSCoW plan, source archive provenance and explicit disabled defaults; all exact-head checks pass. **G1 source implementation**: qualified provider stubs, normalized contract tests and deterministic exception engine against fictional fixtures; no tenant activation. **G2 native silent integration**: accepted tenant permissions, specific AHPRA agreement and field-use rights, current governance/delegations, security/privacy/records assessment, actual solution install and negative permission tests, replay/recovery and silent comparison. **G3 operational commissioning**: approved business owner, runbook, roster of exception reviewers, measured false-alert/omission performance, business continuity, protected deployment, independent current-head checks and explicit production activation decision.

No G2/G3 gate is satisfied merely by a successful GitHub merge, an ARM template or a synthetic mock. Preserve a dated evidence matrix with `passed`, `failed`, `blocked` and `unexecuted` (never convert a refused/billing-blocked hosted run to pass).

## 7. Amendment: lossless regulatory detail and bounded source assurance (13 November 2026)

The canonical envelope supports legacy `schemaVersion=1.0.0` and the additive `1.1.0`. Version 1.1 **requires** `registrationDetail` with original regulator-native status code, vocabulary revision, independently identified registration categories, specialty identifiers, endorsements and structured restriction references. Do not collapse conditions, undertakings, supervision requirements, provisional or limited registration into a Boolean. If the licensed source lacks a field, use `unknown`/held evidence, never absence as proof of no restriction. Retain native values as protected restricted evidence where permitted; release only source-linked minimum-necessary references to consumers.

Only `AHPRA_PIE_FIND` (contract-qualified official registration facts) and `AHPRA_PUBLIC_REGISTER_HUMAN` (properly documented manual verification) may carry status evidence in the approved native deployment. `AHPRA_PIE_IDENTITY` has `qualified_identity_only`, and cannot produce a current registration-status finding. Test/mock/discovery credentials are not technical authorisation and never become operative verification. The source-only reference engine is *not* a production provider identity or licence enforcement service.

`EngagementCoverage` is the independently sourced eligible active engagement denominator (with rural, VMO, locum, contract, private practice and regional/statewide variations). An enabled watch entry proves only an entry is tracked, **not** that its registration is current, the practitioner is employed or has an active SoCP. Missing, ambiguous, expired and unmatched engagements are separately measured and reconciled to their real data owners.

Required cross-cutting deliverables are [ADR RA-001](../../conductor/tracks/registration_assurance_20261113/source-admission-decision.md), [RA-H01–06 safety case](../../conductor/tracks/registration_assurance_20261113/clinical-safety-case.md), and [eligibility, evaluation and accreditation contract](../../conductor/tracks/registration_assurance_20261113/engagement-coverage-and-evaluation.md). G2/G3 require signed native clinical, security, legal, data stewardship and operational evidence, not just schema/unit-test success.
