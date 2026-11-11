# Contracts and qualification evidence

Version all records/schemas/policies. IDs and shapes below are **design contracts**, not deployed objects. Required tests link to requirement IDs in [requirements](requirements.md).

## 1. Job plan identity and revision contract

`JobPlanId` is stable; each `VersionId` is immutable once approved, stamped with content SHA-256, schema version, industrial RuleSetId/version/hash, taxonomy version, employment classification, hours/FTE, cycle dates and actor identities. Changes to approved plans create a new draft revision linked to parent. Reference list codes cannot be retroactively changed for old revisions. ETag/version conflict returns explicit error with no partial update. Test: mutate approved record fails, concurrent edit only one success, branch/supersession audit complete (M04, M08, M10, M16).

## 2. Session and time calculation contract

Time block is atomic: date or cycle-day/week; start, end and timezone (Australia/Brisbane), location/site; `ActivityCode`, `Hours`, `IsOrdinary`, `IsCSTEligible` (derived from versioned rule), `IsTravel`, and optional on-call subtype. Mixed block must split; duplicates and overlap fail. Derive hours from timestamp duration with defined breaks, never allow free-text hours to override scheduled elapsed time without reconciliation. `total_planned_ordinary`, `total_CST_eligible`, `required_CST`, `CST_gap`, `contracted_ordinary`, `additional_hours`, `actual_hours` calculated with explicit denominator and time period. Test 40-hour-fortnight example must be evaluated against contracted **fortnightly** hours; no assumption 40 hours/week is universal. MOCA7 SMO minimum 10% is a **provisional authority-specific rule** requiring formal HR/IR verification before operational go-live. Distinguish on-call availability from actual recall/telephone/travel, no double count (M05–M08).

## 3. Authorisation contract

Only delegated authority identified in current CHHHS delegation register may approve. Consultation, compliance review and final authorisation have distinct decisions and timestamps. Actor/group permission checked in SharePoint/flow, not merely visible UI roles. A failed approval or missing rule is `Pending` with reason; no silent auto-approval. Every approval references immutable `VersionId`, rule set, delegation evidence and content hash. Status changes are idempotent; replay does not generate duplicate approvals (M03, M09, M10, M16).

## 4. Security/records contract

Plan information is personal employment/workforce information. Separate service-level aggregated reporting from individual plans. No patient identifiers, personal health diagnoses, performance case files or secrets. Permission matrix explicitly checks staff A cannot view or edit staff B; director A cannot see unrelated service; HR adviser can inspect only approved purpose; operator cannot silently approve; all write paths have change provenance. CHHHS data/records/privacy owners approve classification/retention/legal hold, auditing and physical location before real data. Reproduce negative tests for Power Apps, SharePoint direct links, API/list endpoints and flows. Stop if SharePoint cannot meet scale and permission requirements (M03, M13).

## 5. Solution/package contract

Source includes solution/unpacked code, application identity, publisher, version, flows, environment variables, SharePoint provisioning, security groups and post-import runbook. Every packaged artifact has hash, exact git commit, upstream pin/licence/notice and test results; no external tenant credentials. Import test creates lists/data, import canvas/flows, bind SharePoint site + list GUIDs, save/publish, synthetic actor walkthrough, remove/reimport, and rollback. Accept `source-only`, `dev-import-verified`, `pilot-approved`, `production-ready` as **separate statuses**. No 'importable' claim without a completed actual clean import and readback (M01, M02, M14, M15).

## 6. Flow contracts

Draft saves do not submit. Submit snapshots revision and creates one consultation request. Officer agreement is not employer authorisation. Validation evaluates authoritative eligible rule set; missing/expired source fails closed. Approver decision targets submitted revision only. Approval event creates one immutable record, notification is at-least-once but deduplicated on event key, failures sent to controlled retry queue/log. Revisions trigger no changes in active plan until approved. Scheduled review opens work item without modifying baseline. Every flow records `OperationId`, `CorrelationId`, actor, source version and outcome. Redact private comments in notifications (M09–M11, M16).

## 7. Acceptance evidence matrix

| Gate | Required artefacts | Block on |
|---|---|---|
| G0 candidate evaluation | source/ZIP hashes, licence analysis, import screenshots/logs, bootstrap ADR | unknown licence/dependencies, unsupported sample |
| G1 authority | signed or pending requirements review, classification, delegation and rule-source matrix | unvalidated industrial/retention/delegation rules for real data |
| G2 data | schema/provisioning code, readback, synthetic fixtures, permission denial tests | missing authority, excessive access |
| G3 functionality | app/flow source, Power Fx checks, scenario tests, concurrency/fault replay, accessibility | inconsistent approval, unprotected approved version |
| G4 packaging | clean solution import/export, connection binding, checker output, backup/rollback rehearsals | missing tenant-level proof |
| G5 pilot readiness | named CHHHS sign-offs, operator training, user acceptance tests, privacy/security approvals | no delegated approval of pilot |
| G6 production | monitored pilot receipts, residual risks, change control, owner and maintenance schedule | no post-launch stewardship or assurance |

## 8. Synthetic test fixtures

F01: full-time SMO multiweek schedule including clinic/CST/leadership/recall; F02: part-time SMO fortnight denominator; F03: Clinical Director overlapping leadership and clinic rejected; F04: RMO employment class not permitted to inherit SMO CST; F05: rural site travel and cross-site schedule; F06: two users concurrent edit and stale ETag; F07: recall outside ordinary hours; F08: officer rejects/requests amendment; F09: HR/IR rule expired; F10: delegate lacks authority; F11: staff in another service denied direct list access; F12: first review and annual review triggers without arbitrary auto-approval; F13: worked lunch and fatigue warning; F14: approved version correction/supersession; F15: outage, retry and duplicate flow event.

Each fixture requires expected status, permitted roles, records persisted, computed hours/CST, audit outcome and denial path; no real CHHHS employee names or IDs.

## 9. Workforce interoperability and measurement contracts

- `PositionAssignment`: versioned position/establishment identifier, incumbent identifier (restricted), specialty/site, FTE, effective interval, status and source; **not** inferred from a dashboard headcount.
- `RosterCoverageObservation`: source-qualified rostered hours, coverage type, interval, role, service and missingness. May be absent without blocking plan authoring; reconciliation status becomes `unverified`.
- `WorkforceCapacitySummary`: aggregate planned hours, rostered coverage, actual reported hours, funded establishment where independently sourced, delivered CST, exceptions, period/grain, snapshot, suppression threshold, completeness and confidence/uncertainty flags. No raw personal comments.
- `CredentialingReference`: optional read-only effective-dated practitioner/SoCP status with recorded provenance and expiry; absence does not imply authority to practice, and the app may not write to the credentialing register.
- `ChangeImpactPreview`: bounded what-if only; no roster, payroll, employment contract or credentialing updates until a separate approved integration pathway is implemented.

Tests: unknown establishment cannot produce a numeric deficit; partial/missing roster observations cannot be silently treated as zero; no small-cell reidentification; schema and effective interval validation; source-hash/readback; least-privilege consumer. Maintain explicit separation of workforce operational plan from individual performance data.
