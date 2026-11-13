# Registration assurance — MoSCoW requirements and acceptance criteria

Contract source: [integration contract](../../../docs/credentialing/registration-assurance-integration-contract.md). All identifiers below are new and **planned**; no check is marked complete by writing this document. "Must" applies to the identified release gate; a later source-qualified adapter does not become mandatory for a standalone mock/manual capability.

## Must

| ID | Gate | Requirement and acceptance proof |
| --- | --- | --- |
| RA-R01 | G0 | Publish immutable source archive SHA-256/file inventory, authorship and reuse/third-party licence assessment; import no original ZIP, binary, operational data or private metadata into public Git before qualification. |
| RA-R02 | G0 | Declare source-qualified responsibility matrix. Practitioner master, employment, formal credentialing and SoCP remain under Decisions/native authority; module only owns attempts, observations and exceptions. |
| RA-R03 | G0 | Define signed/versioned source-interface policy: allowed purpose, data rights/retention, fields, methods, regulator, capabilities, source freshness, identity, permissions and operator. An unqualified provider is disabled. |
| RA-R04 | G0 | Version normative RegistrationObservation schema, source/observation/evidence identity and compatibility policy. Consumer must reject missing/unknown major versions and privileged claims from discovery-only sources. |
| RA-R05 | G0 | Disable undocumented autocomplete as operational regulator verification; missing five-result suggestion, changed ordering or WAF denial cannot imply cancellation or non-registration. |
| RA-R06 | G0 | PIE integration has no fictional API contract: obtain actual organisational agreement and issued XML schema/auth/semantics before real adapter implementation. Browser Alerts are not assumed to be API push. |
| RA-R07 | G1 | Build portable, hermetic source generators and validators (no developer absolute paths), with clean-checkout dependency pins and canonical rebuild/diff verification of original artefacts. |
| RA-R08 | G1 | Identity requires source namespace + exact AHPRA registration number or unresolved candidate. Test homonyms, alias/renames, ambiguous common names, absent number and mismatched profession. |
| RA-R09 | G1 | Pure deterministic diff/reconciliation engine separates acquisition failure, source absence, identity uncertainty and actual independently verified registration-status change. No inferences from expiry date alone. |
| RA-R10 | G1 | Append-only observation/provenance and human-review history with source as-of/retrieval times, source version, hash/ref, qualification, rule mapping, error and correlation; no raw staff data in Git or logs. |
| RA-R11 | G1 | Idempotent retries, source switching, interrupted jobs and out-of-order/stale observations cannot mint duplicate cases/notices, overwrite reviewer edits or roll back more recent evidence. |
| RA-R12 | G1 | Provider stubs and manual fallback always produce an explicit uncertain/blocked state. Unknown data never automatically becomes verified/clear or adverse. |
| RA-R13 | G2 | Decide independently installable core and optional integration topology; each native package declares prerequisites, Power Platform licensing/costs, security scope, supported versions and removal path. No hidden cross-module dependency. |
| RA-R14 | G2 | Integrate with Decisions-owned credentialing records only through versioned, authenticated, permission-scoped, minimum-necessary adapters. Server-side write boundary and native readback/rollback required before any authorised write. |
| RA-R15 | G2 | Native model/solution/read-only review workbench preserves human actor, evidence/uncertainty, delegation, case revisions, access controls, time zone and source freshness; no automatic credentialing or employment decision. |
| RA-R16 | G2 | Secret storage/managed identity or approved service principal, private configurations, Australian residency assessment, RBAC, DLP, PIAs/records and approved retention/legal holds before any real record. |
| RA-R17 | G2 | Native job/retry/outbox/reconciliation contract with independent deadlines, leases, poison message/timeout/circuit breaker, tenant readback and operator recovery; no blind re-send after ambiguous delivery. |
| RA-R18 | G2 | Outbound email/scheduled notification defaults OFF; only explicit human approval for actual recipients/content/attachments/scope can enable send, consistent with `AGENTS.md`. |
| RA-R19 | G2 | Validate exact AHPRA agreement, documented provider, identity, XML parsing with XXE disabled, source response shapes, error statuses, freshness and approved operational polling before live source collection. |
| RA-R20 | G2 | Explicit service health, source provenance/currentness, incident and fallback monitoring; provider downtime must not disable existing credentialing work. |
| RA-R21 | G2 | Test access loss, conflicting authorisations, duplicate concurrent jobs, privacy leak, malformed XML, schema drift, stale response, restore/replay and source revocation in actual authorised non-production environment. |
| RA-R22 | G3 | Prospective silent evaluation uses independently verified registration references to measure identity matching, true adverse changes, omissions, false escalations, missingness, effort, cost and recovery; retain a manual comparator. |
| RA-R23 | G3 | Operational owner must sign off current clinical governance/legal authority, monitoring role, escalation response, restoration, support and active source limits before enabling any real flow. |
| RA-R24 | All | Machine and hosted evidence reports `passed / failed / blocked / unexecuted`; exact-head security/privacy/CI checks and protected merge are not bypassed. GitHub success is not native deployment. |

## Should

| ID | Requirement |
| --- | --- |
| RA-R25 | Reuse approved single-site source providers, Dataverse roles and supported M365 ALM artefacts before creating new adapters or tables; preserve current identities and owners. |
| RA-R26 | Provide read-only minimum-necessary Workforce aggregation: eligibility, check coverage, stale/exception counts, renewal risk (with confidence limits), never implicit current employment. |
| RA-R27 | Reference PPG/accreditation controls as versioned standards and evidence links; monitoring coverage is not proof of clinical accreditation compliance. |
| RA-R28 | Provide privacy-minimised Process events and reproducible Costing measures for time-to-verification, effort, false alerts and service benefit. |
| RA-R29 | Prefer documented API/licensed data exchange to brittle site HTML; no fallback escalation of data authority and no dependence on AI/Copilot. |
| RA-R30 | Reconcile source/derived status after recovery and use controlled per-provider capability manifests, versioned replay and negative contract fixtures across providers. |

## Could

| ID | Requirement |
| --- | --- |
| RA-R31 | Introduce an approved, optional PIE browser-alert intake with deterministic parsing and separate human review if contracted access and delivery rights support it; never falsely label it an API webhook. |
| RA-R32 | Add regulator-agnostic connectors only after tested namespace separation, licensing and legitimate use for each profession/regulator. |
| RA-R33 | Publish aggregate coverage dashboards and service forecasts once denominators, source freshness and suppressed small cell rules are qualified. |

## Won't / explicit exclusions

| ID | Exclusion |
| --- | --- |
| RA-R34 | Autonomous suspension/revocation, scope/roster/employment update, registration claim from name match or search omission, unreviewed adverse letters, AI registration determination. |
| RA-R35 | Unapproved scraping, counterfeit API emulation, fabricated PIE auth/status/expiry schemas, copying PIE data beyond contractual rights, disclosure to another organisation. |
| RA-R36 | Second practitioner master in SharePoint, second credentialing decision register, mandatory installed CareOps siblings or a live parent suite runtime. |
| RA-R37 | Public practitioner data, credentials, source archive import without provenance, automatic email sending, premium tenant activation or bypass of protected release checks. |

## Required fictional/adversarial fixture matrix

- Two practitioners with same full name but different registration numbers; common surname yields five suggestions, target omitted: **unresolved**, never deregistered.
- Public autocomplete returns empty, 403, HTML, CAPTCHA, malformed JSON, renamed fields, mixed profession or changed ordering: **source unavailable/discovery-only**, never adverse.
- Official XML with missing mandatory elements, external entity/DTD, duplicate matching records, stale as-of time or unknown status mapping: **rejected/held**, no false verified state.
- Expiry yesterday with regulator status still Registered, including renewal/grace period: no automatic lapse or roster action.
- Explicit verified material restriction/suspension with correct identity: priority human review, with source and retrieval time; **no automatic revocation**.
- Retry after unknown persistence result, duplicate alert/event, old provider reply after new reply, conflicting evidence, repeated identical poll: idempotent, chronological, auditable, no duplicate mail.
- Reviewer dismisses a false positive; incoming unchanged observations preserve prior disposition; genuinely material newer observation reopens only its dependent review.
- Missing PIE agreement, no secret, denied entitlement, no source, no sibling Decisions, offline source: standalone manual/mock still usable; no live provider run.
- Direct API access without privilege, SharePoint link disclosure, restored older state, deleted condition history and a purported agent approval: fail closed with immutable evidence.
- Unknown schema major or unsupported minor field: consumer refuses privileged interpretation and records compatibility exception.

A test is not a proof of native access control or regulatory permission unless run against the actual authorised environment and recorded as such.

## Additional pre-integration requirements (13 November; all mandatory before their relevant gates)

| ID | Gate | Requirement / acceptance |
| --- | --- | --- |
| RA-R38 | G1 | Preserve distinct general, specialist, limited, provisional, non-practising and unresolved registration categories with source-native vocabulary and separate specialty, endorsement, restriction/undertaking and supervision evidence; any restricted/unknown practice category requires human assessment, not automated authorisation. |
| RA-R39 | G1–G2 | Monitoring coverage denominator is authoritative eligible **engagements**, not number of successful source results: active VMOs, locums, regional/outreach, contractors and multihospital engagements are independently reconciled; duplicate or missing watch identity cannot count as covered. |
| RA-R40 | G1 | Use supported schema versions explicitly: `1.0.0` accepted as legacy, `1.1.0` includes detailed registration fields. Consumer refuses future/unknown minor and major versions unless explicitly qualified. Real registration status without required detail is not a positive practice assertion. |
| RA-R41 | G1–G3 | Maintain RA-H01–06 clinical safety case, trace hazards to tests and process controls, and require named owner and residual risk acceptance for live deployment. |
| RA-R42 | G0–G1 | Source admission is selective, not wholesale; no unqualified licence/provenance, old Excel master, active autocomplete or duplicate Logic Apps/Power Automate writers. |
| RA-R43 | G2 | Choose one native operational writer/identity per deployment; full-Dataverse credentialing remains canonical and Standard-M365 is a distinct manual option, not an unqualified mirror. |
| RA-R44 | G2–G3 | Pre-register pilot performance measures and success thresholds using independently verified source checks, rare-event confidence bounds, non-alert sampling, workload and actual cost, with operator-controlled degraded mode. |
| RA-R45 | G2–G3 | Version controlled QH-HSD-034, operative NSQHS 1.23/1.24 and May 2026 Commission guidance crosswalk; monitor evidence lineage without claiming legal/accreditation conformance or operative draft third-edition controls. |

The [source-admission decision](source-admission-decision.md), [clinical safety case](clinical-safety-case.md), and [coverage/evaluation contract](engagement-coverage-and-evaluation.md) supply the detailed outputs. These append to the earlier 37 requirements; they do not override existing authority, prohibition or commissioning gates.
