# CareOps Medical Job Planning Integration Contract

**Contract ID:** `careops.medical-job-planning.integration`  
**Candidate edition:** `1.0.0-draft` (13 November 2026)  
**Status:** proposed public, synthetic, source-level interface specification; **not implemented, deployed, authorised or accepted by any service owner.**  
**Owner of core records:** Medical Job Planning module. **Interface owners:** each sending and receiving module retains authority over its native source and consumer.  
**Companion normative schema:** [contracts/envelope.schema.json](contracts/envelope.schema.json); typed payload constraints are inside this schema; synthetic [positive messages](contracts/fixtures/valid-messages.json), [negative conformance cases](contracts/fixtures/negative-cases.json), [strict session schema](contracts/session.schema.json), [activity taxonomy](contracts/activity-taxonomy.json), [metric dictionary](contracts/metric-dictionary.json), and [semantic validator](contracts/semantic_validation.py) are in [contracts/fixtures/](contracts/fixtures/).  
**Normative vocabulary:** MUST, MUST NOT, SHOULD and MAY express requirements for future implementation. They do not represent deployment entitlement.

## 1. Purpose, applicability and invariants

This contract defines the boundary between a standalone Medical Job Planning core and **optional** CareOps PPG, Approve/Decisions, Workforce BI, Process, Costing/Finance and Sim integrations. It also describes external HR/establishment/rostering references without claiming CareOps owns those systems. It complements [CareOps standalone-module contract](../../../docs/standalone-module-contract.md) and the parent CI, privacy and email rules.

1. **No other module is required** to install or use the Medical Job Planning core with a separately adopted local policy snapshot and an accountable human decision path.
2. **One authoritative writer:** Medical Job Planning owns PlanHead, PlanVersion, sessions, case and activation. The approved external HR/establishment/roster source owns people, appointments, positions and actual worked activity. Optional adapters MUST NOT mutate either owner's records as a side effect.
3. **Separate obligations and approvals:** PPG owns policy lifecycle; Approve/Decisions may provide a human decision receipt but cannot unilaterally approve or activate a job plan. Core MUST verify delegation, plan hash, rule edition, no-self-approval and current service scope before applying any result.
4. **Minimum necessary:** confidential practitioner-level data and actual work schedules MUST NOT be exported to analytics or simulation adapters by default. Access is enforced at source/transport and report/asset boundaries; a schema classification or pseudonym alone is not an access grant.
5. **Explicit incompleteness:** stale, inaccessible, truncated, partial or denied sources yield `partial/unavailable/unverified`; never silently zero, complete or compliant. Missing optional services MUST NOT block core reads, drafts, approved versions or local human review.
6. **No implicit notifications:** email delivery remains Off/fail-closed and follows the exact human-send approval rule in CareOps AGENTS.md, independently of adapter enablement.
7. **No semantic invention:** industrial/CST/annualised/FTE or cost assumptions MUST be sourced from an adopted, versioned rule or appropriately labelled synthetic scenario; policy reference does not imply policy adoption.

## 2. Interface registry and ownership

| Interface | Direction and type | Authority and source grain | Transport / fallback | Priority |
|---|---|---|---|---|
| `MJP-POL-01` | PPG -> MJP `policy.reference` (pull, read only) | PPG document + edition + effective interval; execution rule is a separately approved local snapshot | Standards-based read/reference; pinned local adopted snapshot when PPG absent; expiry fail-closed for *new* approvals | Should |
| `MJP-APP-01` | MJP -> Approve `approval.request` (optional) | MJP one immutable PlanVersion and ReviewCase | Versioned request; local accountable review when absent; no duplicate final decision writer | Should |
| `MJP-APP-02` | Approve or Decisions -> MJP `approval.result` (verified receipt only) | Provider's one formal human decision; MJP applies if policy/security valid | Authenticated provider readback and idempotency; reject unauthorised, stale, ambiguous | Should |
| `MJP-PRC-01` | MJP -> Process `lifecycle.event` (append-only) | One event per accepted state transition with minimised/pseudonymous case key | At-least-once idempotent event export; queue/retry; core independent | Should |
| `MJP-WRF-01` | MJP -> Workforce BI `workforce.aggregate` (read only) | One service/period/measure/plan-version selection and declared population | Approved aggregate snapshot + completeness and disclosure control; current PBIP remains unchanged until accepted adapter | Should |
| `MJP-CST-01` | MJP -> Costing/Finance `costing.aggregate` (read only) | One service/period/cost-basis and assumption set | Versioned approved aggregate; existing authoritative finance/employment denominators remain separate | Should |
| `MJP-SIM-01` | MJP -> Sim `simulation.scenario` (read only, synthetic/de-identified only) | One scenario/assumption/seed and input edition | Optional file/contract adapter, no feedback into job-plan decisions | Could |
| `MJP-EXT-01` | External HR/establishment/roster -> MJP `source.reference` | Source-qualified appointment/position/assignment/roster reference; source remains authoritative | Explicit permitted read/snapshot or manual verified entry where authorised; never infer actual work from plans | Must for real deployment |

No direct cross-module Dataverse foreign key, common staff database, shared mandatory flow, central orchestration service or bilateral cloud dependency is introduced. Each adapter can be disabled, upgraded and removed independently with bounded recovery.

## 3. Common wire envelope: major version 1

Messages MUST conform to the committed JSON Schema in `contracts/envelope.schema.json`, validated at each producing and consuming boundary. Schemas control *shape*, not entitlement or business authority.

| Property | Requirement |
|---|---|
| `contract_id`, `contract_version`, `message_type` | Exact interface identification and SemVer of wire contract; unsupported major = reject/quarantine |
| `message_id`, `correlation_id`, `causation_id` | Globally unique message, end-to-end operation trace and optional causation chain |
| `idempotency_key` | Stable for logically identical command/event; payload/hash conflict rejected |
| `producer`, `consumer` | Source-qualified modules and exact provider/consumer contract or build revisions |
| `source` | `system`, `resource_type`, `resource_id`, `revision`, `digest_sha256` where content-addressable |
| `context` | Organisation/service scope as approved source-qualified opaque IDs; no names/UPNs in illustrative fixtures |
| `observed_at`, `effective_from`, `effective_to`, `as_of` | RFC3339 timestamps in UTC; state-effective, observed and projection-as-of distinguished |
| `classification`, `purpose` | Data sensitivity and allowed processing purpose; enforce independently at transport and read |
| `quality` | `status` = complete/partial/unavailable, `coverage`/freshness, `suppression` and evidence, no assumed completeness |
| `payload` | Typed message-specific payload matching `message_type`; canonical JSON schema with unknown fields rejected on core v1 |

The producer MUST preserve stable source identity independent of renamed entities and preserve immutable revisions/digests. Transport auth MUST come from a qualified workload identity/managed Microsoft connector connection with least privilege; a hash, event source label, actor ID or SharePoint URL alone is not authentication. System clocks, timezone conversion and snapshot/cutoff semantics are contract tested.

**SemVer:** additive optional fields = minor after consumer tests; tightened/removed required fields, changed grain, status meanings, data classification, identity or decision semantics = major. Patch is non-semantic clarification only. Producers publish supported major and exact schema digest. During compatible parallel rollouts, consumers support a bounded declared range and reject unknown required fields or unseen major versions; never silently coerce. No automatic activation upon source merge.

## 4. Typed data semantics and decision points

### 4.1 `policy.reference` — PPG

Fields include policy key, approved edition, source document reference/hash, owning authority, status, `effective_from`, `effective_to`, and business-rule identifier. A document reference is **not** an executable industrial rule. An accountable medical workforce/HR/industrial owner must approve the local executable mapping and golden cases before it controls any plan. Missing/stale/withdrawn policy blocks newly operative approvals and raises review; it does not erase valid issued history.

### 4.2 `approval.request` and `approval.result`

Request binds ReviewCaseKey, PlanVersionKey, SHA-256 of submitted immutable content, requested decision stage, policy snapshot/edition, expected PlanHead generation, effective service scope and the verified delegation reference. No raw practitioner schedule or plan narrative in the interface by default; use an access-controlled deep link.

Result binds external decision ID/revision, ReviewCaseKey, exact PlanVersionKey/hash, provider verified actor reference, authority/delegation evidence ref, selected outcome (approved/returned/rejected/abstained), decided-at timestamp, conditions evidence and audit receipt. The core MUST re-check actor identity and effective delegation server-side, prevent self-approval and reject version mismatch, duplicate conflicting result, wrong service and stale authority. External approval does not equal PlanHead activation; the core performs an atomic generation check and records the applied result or a quarantined exception.

If a Decisions pathway is authorised, the relevant Decisions record is the authoritative *formal decision* while MJP remains authoritative for *plan state*; do not mint a second legal decision. Route choice is a deployment-profile decision rather than inferred from a provider being installed.

### 4.3 `lifecycle.event` — Process

A single accepted transition: pseudonymous case ref, stable event ID, from/to states, stage and event time, optional coded exception and duration. Do not export personnel identity, plan body, industrial narrative or free text by default. Exports are append-only and at-least-once, with Process deduplicating event_id; source recovery maintains original event identity. A Process outage cannot stop approval.

### 4.4 `workforce.aggregate` — Workforce BI

Source grain: **service + reporting interval + metric ID + reporting as-of + measure definition version**, *not* one practitioner or one plan. Distinguish:
- approved planned clinical hours vs approved CST hours vs total contracted reference hours;
- approved FTE/establishment reference vs occupied appointment FTE vs capacity coverage;
- observed worked hours, provided **only** when sourced independently and permitted;
- valid plan count, eligible population, missing/denied source count, version selection, coverage and proportion with approved plans;
- numerator/denominator, units, calendar basis, time grain and uncertainty/quality.

Apply an approved small-cell disclosure policy before releasing an extract and suppress potentially inferential complements. Suppressed values MUST be null with explicit suppression metadata, not zero. Workforce BI consumes a dedicated optional feed/semantic version, not a silent modification to existing 66 private feeds. PBIP/TMDL/PBIR change, private feed binding, RLS, exact deployment and all report measures require separate owner signoff and refresh/row/measure reconciliation.

### 4.5 `costing.aggregate` — Costing/Finance

Source grain: service + period + cost-basis/rule edition + scenario or actual/approved source designation. Must retain costing method, FTE/hours basis, underlying external establishment/salary/award reference, price year, currency, assumptions, missingness, privacy and uncertainty. **Planned job-plan hours are not paid hours, costs, observed work or staffing establishment.** Costing and Finance retain their own calculation and ledger authority.

### 4.6 `simulation.scenario` — Sim

Requires scenario ID/version, seed, synthetic/approved de-identified classification, source snapshot, explicit assumptions and scenario output reference. Sim must not ingest individual live practitioner records by default. Its results cannot change an active plan or serve as industrial compliance determinations.

### 4.7 `source.reference` — authoritative external systems

Only permitted, verified effective-dated source references: practitioner, position, appointment, service assignment, contract/instrument and independently observed activity. Return status observed/complete/partial/denied/stale; no `null` response silently means no employment contract. Define retention and source agreements before live integration. Any manual verified record is marked as **not externally reconciled** until checked.

## 5. Transport, privacy, consistency and operational outcomes

- **Transport:** v1 is provider-neutral canonical JSON over an approved native SharePoint/M365 adapter, or an immutable approved file-backed read-only snapshot. Endpoint paths, tenant IDs, OAuth/workload identities and Power Platform component IDs belong to private deployment profiles. No invented public API or assumed Microsoft connector capability.
- **Trust:** validate provider identity, purpose, scope, policy/delegation authority, payload schema and digest before applying. Never accept `actor`, `role`, `effective_time` or `approved` solely from a Canvas parameter.
- **Idempotency:** enforce unique key + digest; replay same event is a no-op; conflicting duplicate is rejected with an audit receipt. At-least-once delivery is assumed; exactly-once delivery is **not** claimed.
- **Ordering:** event sequence and source revision/expected generation are explicit; out-of-order updates quarantine or reconstruct by version. For approvals, core CAS head is the commit point; multi-list writes are a recoverable saga.
- **Timeout/retry:** finite retries honour `Retry-After` for 429, bounded jitter and a durable dead-letter/exception queue. Never retry an outdated 412 head blindly or force `IF-MATCH: *`.
- **Degraded mode:** absent optional adapter -> core continues; stale policy -> block *new* effective determinations with a documented local snapshot policy; denied source -> unknown, not zero; pending decision -> no approval; unavailable analytics -> unavailable/partial.
- **Reconciliation:** source-qualified identities, revisions, item counts, hashes, watermark/as-of, page coverage, outcome state and rejected messages are checked. Recovery responsibility remains with adapter/module owner.
- **Confidentiality:** minimum scope, no raw schedules/narratives in public source, CI, metrics, events or examples; prohibit emails, browser URLs and unrestricted exports as covert data channels. Use class-based retention, data loss prevention and explicit export reviews. Respect identity lifecycle/revocation.
- **Audit and retention:** each decision/result and issued record links exact provenance/evidence and effective date, stored in approved records system. Audit events are immutable per source; correction is a new event, not history rewrite.

## 6. Conformance test suite (required before enabling each interface)

| Test ID | Required proof |
|---|---|
| `MJP-IC-01` | Schema validation, unknown/invalid version rejected, provider/consumer supported version matrix and reverse/forward fixture parity |
| `MJP-IC-02` | Repeated identical message accepted idempotently; same key with altered plan hash, actor, stage or payload rejected |
| `MJP-IC-03` | Unauthorized service, caller-spoofed identity, expired/revoked delegation, self-approval and copied direct SharePoint URL all denied |
| `MJP-IC-04` | Approval result on superseded/stale PlanVersion, unexpected generation or policy edition quarantined; no activation |
| `MJP-IC-05` | Absent PPG/Approve/Workforce/Process/Costing/Sim leaves core functional; absent policy authority blocks new effective approval but retains issued history |
| `MJP-IC-06` | Partial page, 429 throttle, late feed, denied source or unsynchronised as-of returns explicit partial/unavailable; never false 0 |
| `MJP-IC-07` | Loss mid-CAS, crash-after-commit, out-of-order events and at-least-once duplicates recover without dual active plan |
| `MJP-IC-08` | Worker-level data blocked from BI, Process/Costing/Sim; permitted aggregates suppress small/derivable cells and honour source RLS/access |
| `MJP-IC-09` | Exact cross-output hours/CST/FTE/calculation parity on synthetic golden fixtures; planned vs actual never conflated |
| `MJP-IC-10` | Consumer v1 minor/patch compatibility; v2 major mismatch fail closed; rollback of adapter preserves core and source records |
| `MJP-IC-11` | Plan and issued document provenance, effective-dated as-of, revocation, retention and records readback |
| `MJP-IC-12` | No automatic mail, hidden tenant binding or premium dependency introduced; native solution export/import and effective runtime access qualified separately |

**Qualification evidence per adapter:** owner, purpose, exact provider/consumer versions and hashes, environment, protocol/fixture set, classification, security approval, successful and deliberately failed tests, source/refresh reconciliation, known gaps, rollback path, real/native result and decision on whether the adapter is enabled. Store private deployment receipts outside the public repository. A passing source contract is not production permission.

## 7. Industrial and negotiation semantics incorporated before implementation

The initial target may be the Queensland Health employment environment, but the core remains organisation-neutral. The adopted local rule pack must distinguish a clinician's **individual industrial entitlement**, job-plan **allocation**, independently observed **access**, any **displacement**, and a separately evidenced **recovery or shortfall**. Do not collapse them into a single percentage or interpret the upload's synthetic `required_cst_fraction`, `annualised_hours`, 0.5-hour tolerance or fixed review anchor as industrial authority.

For an eligible SMO under [MOCA7 QIRC CB/2025/128](https://www.qirc.qld.gov.au/sites/default/files/2025-11/2025_cb128.pdf), clause 11.18.3–5 expresses minimum individual protected CST at 10% of contracted ordinary fortnightly hours, with consultation and appropriate later access when fortnightly delivery is not possible. The applicability of any instrument, individual variation or preserved HR policy, including VMO/RMO differences, must be independently reviewed. Each operative rule requires a source document/edition/hash, clause and adoption record. The same applies to non-arithmetic matters such as place of work, conflicts with paid outside activity and fatigue management.

Internal MJP negotiation stores may represent proposed, counterproposed, agreed, disputed, escalated, conditionally agreed, formally authorised, issued and effective states, all with versioned evidence. A negotiated agreement is not a delegated decision; an `approval.result` with `conditional_approval` MUST contain `conditions_evidence_ref`. Source and native owner must agree on whether conditions are satisfied before the core can issue or activate any version. Unresolved shortfalls or disagreements remain visible and do not silently become compliant.

## 8. Executable quality, identity and reporting invariants

`envelope.schema.json` validates structural conformance and additionally requires metric-definition references and condition evidence. `semantic_validation.py` checks compatible module directions, purposes, UTC/as-of ordering, scope/period coherence, workforce population count consistency and envelope-vs-payload suppression. The project-pinned JSON Schema validator must run **both** layers in CI on [positive](contracts/fixtures/valid-messages.json) and [negative](contracts/fixtures/negative-cases.json) fixtures, with no skip after failures. The semantics layer is **not** an industrial rules interpreter or native identity authoriser.

**Data completeness vocabulary, v1:** for a defined complete source cohort, `eligible_count = observed_count + missing_count`. `complete` requires no known missing records; `partial` is not zero; `unavailable` cannot have positive observed records. Population counts are only meaningful where the source cohort is defined and need not be included for standalone events. In a workforce aggregate, `payload.eligible_population` and `payload.missing_count` mirror the quality envelope, and aggregate service scope must equal the authorised context. Suppressed numeric values and denominator/count fields are `null` with matching suppression status on both envelope and payload; never substitute zero.

**Metric identity:** [metric dictionary v1](contracts/metric-dictionary.json) is the provenance contract for aggregate metric ID, definition ref/version, grain, basis, unit, eligible population and analytical meaning. It is **not** an implemented DAX/Power BI model. Costing uses its own forecast/actual basis, price year, and external wage/source assumptions, not plan hours as payroll observations. Changes to metric meaning, time grain, population, confidentiality, formula or denominator require versioned consumer review rather than an in-place silent edit.

**Identity boundary:** Power Apps caller, Power Automate trigger arguments, run-only flow connection, execution principal, SharePoint resource permission and effective delegate are distinct. Service-side authenticated actor/delegation checks MUST precede any authoritative action. A run-only flow executing via its owner connection or a supplied `actorUPN` has **no inherent authority** to approve. Verify direct SharePoint/REST/file reads, stale delegation, return/dispute and self-approval in the actual development environment.

**Native test route:** use maintained Playwright samples and PAC/Solution Checker with specific connector and site configuration; Microsoft's Power Platform Test Engine was deprecated effective April 2026. Prove indexed/delegable queries and complete paging over representative >5,000 synthetic plan records, including authorised/denied and late pages. Qualify actual physical SharePoint permission-scope growth versus Dataverse before native solution construction; Microsoft recommends keeping unique SharePoint scopes below 5,000 per list or library, separate from list-view query thresholds.

**Defect gate:** the v0.4.2 Python `bool("false") == True` coercion is confirmed in the archive but **not fixed in the prototype by this contract update**. The [strict session JSON Schema](contracts/session.schema.json) rejects boolean-looking strings, and regression/source-parity tests must be applied to the admitted source before native processing.

## 9. Acceptance and change control

- **Source-contract accepted:** source owner and each involved interface owner agree on authority/fields, schema fixtures pass, source changes and public inventory reviewed, and all required current-head CI checks pass.
- **Native-integrated:** exact environment, connections, list/field internal names, controlled role resolver, tenant permissions, trigger and retry behaviour, cloud readback, full records and rollback are verified by the relevant owners.
- **Operational:** CHHHS (or the chosen deployment organisation) independently approves industrial rules, security/privacy, records/retention, delegation, licences, staff consultation and pilot outcomes; production enablement is a separate decision.

Integration amendments require a numbered ADR, semantic-version determination, producer/consumer conformance update, privacy/security check, actual current-head source checks and independently approved native rollout. This draft contract alone changes no access, lists, flows, records or employment decisions.
