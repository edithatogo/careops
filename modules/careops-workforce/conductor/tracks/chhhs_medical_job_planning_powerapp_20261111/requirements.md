# Requirements — CHHHS medical job planning app

**Rule:** MUST mandatory, SHOULD recommended, MAY optional. MoSCoW is delivery priority and does not alter industrial, privacy or clinical obligations. All requirement IDs must have automated or human acceptance receipts.

## Must (M)

| ID | Requirement | Verification |
|---|---|---|
| M01 | Importable Power Platform solution containing responsive Canvas App and solution-aware flows; preserve source/versions and reusable deployment config | clean dev import/export, solution checker, dependency inventory |
| M02 | Standard connectors only in baseline (SharePoint, M365 users, standard Power Automate as appropriate); no premium/Copilot/AI requirement | connector/solution inventory and licensing check |
| M03 | Roles: medical officer, Clinical Director/delegate, medical workforce/HR assurance, authorised approver, system operator; no accidental global visibility | permission matrix and negative tests |
| M04 | Separate JobPlan, JobPlanVersion, SessionBlock, ApprovalDecision, ActivityEvidence, OnCallActivity and ReferenceData records; links and revision snapshots | schema contract tests |
| M05 | Variable multi-week cycles, site and speciality, cross-site travel, indirect patient care, leadership, education, research, governance and on-call; preserve C1–C9/S1–S8/L1–L2/T/O codes | synthetic 1/2/5-week scenario fixtures |
| M06 | Allocate explicit numeric hours to an exclusive principal category per block; prevent overlapping sessions and double counting | deterministic boundary/property cases |
| M07 | Contracted vs scheduled vs delivered hours, clinical support time percentage, leave/paid breaks/extraordinary hours and availability/recall distinguished; avoid treating UK 'PAs' as Queensland hours | calculation oracle and IR sign-off |
| M08 | Industrial eligibility/profile versioning with explicit effective date, source and applicability; MOCA7 10% individual SMO CST test; do not apply SMO rules indiscriminately | tests: SMO/VMO/RMO/MPPP, exemptions and unknown rule fail closed |
| M09 | Officer consultation, proposed amendments, HR/IR/compliance validation and delegated approval are distinct events with captured timestamp, identity, version and outcome | state-transition/authorisation tests |
| M10 | Approved versions immutable; amendments create new versions; rejected/withdrawn/expired plans retained with defensible access and records lifecycle | immutability / concurrency tests |
| M11 | Change triggers: workload, scope, duties, FTE, fatigue, service model and scheduled periodic review; monitor approved vs actual | scenario and flow tests |
| M12 | A human-readable export/job plan with taxonomy, schedule, hours, versions, consultations and approvals, referencing the current CHHHS controlled template if available | PDF/Word export visual checks and content audit |
| M13 | Minimum necessary information, privacy classification, retention/legal-hold route, audit records, permission enforcement in SharePoint, no secrets or real staff data in Git | negative permissions, DLP, PIA/records assessment |
| M14 | Source-first/licence-reviewed reuse: hash/pin upstream sample; include notices and record modifications; bootstrap go/no-go | SBOM/provenance record and decision |
| M15 | Dev/test deployment path with environment variables for SharePoint site/list GUIDs, flow references, solution version, rollback and synthetic smoke checks | install in clean authorised dev environment |
| M16 | Fail-safe multi-step writes, idempotent flows, optimistic concurrency and retriable errors, avoiding phantom approvals and lost updates | fault/replay tests |
| M17 | Accessibility, keyboard/screen reader testing, responsive tablet/desktop and acceptable mobile use; health services data minimisation | WCAG review + usability scenarios |

## Should (S)

| ID | Requirement | Verification |
|---|---|---|
| S01 | Configurable specialty/session presets, recurring meeting blocks and departmental capacity summary | clinician scenario |
| S02 | Templates for 3-month first review and annual review as configurable defaults, not assumed universal mandates | review trigger tests |
| S03 | Delegation-aware dashboards, service workload/CST exception trends with minimal identifiability | permission and aggregation tests |
| S04 | Controlled export to a document library with version metadata and restricted access, plus documented manual fallback | file/hash/source link checks |
| S05 | Officer and manager notifications with throttling, no sensitive content in emails, escalation on outstanding actions | flow tests |
| S06 | Repeatable developer provisioning using supported Microsoft mechanisms (PnP/CLI), not solely Python-made local files | dev rebuild evidence |
| S07 | Automated static checks for Power Fx/solution XML, dependency graph, flow definition verification, synthetic UX replay | CI receipts |
| S08 | Bounded import of legacy draft plans (including renal five-week example) after de-identification | migration reconciliation |
| S09 | Structured status and workload event exports (CSV/JSON) for offline analysis, with file protection | export schema tests |

## Could (C)

C01: API/connector adapter for future workforce/rostering systems; C02: richer demand/capacity forecasts; C03: shared CareOps Decisions/Approve integration via narrow contracts; C04: Power BI embedded reporting if authorised and licensed; C05: multidimensional optimisation with independent solver; C06: e-signature integration subject to licensing and approvals.

## Won't now (W)

W01: automated staff payroll/HR master updates; W02: automated industrial legal determination or unattended approval; W03: production import/live medical officer records before tenant approval; W04: premium Dataverse/Copilot as a baseline requirement; W05: encoding individual health or sensitive performance particulars in plan descriptions; W06: building an alternative enterprise-wide PPG approval platform.

## Key clinical/industrial source references to revalidate

- CHHHS renal Clinical Director five-week individual draft (16 Sep 2026): illustrative session taxonomy and workload approach, not approved organisation-wide procedure.
- Draft CHHHS medical job planning policy/procedure/guideline/job-plan pack; approval and exact official Word master status **unverified**.
- MOCA7 and current Medical Officers Award; other medical employment agreements and contracts by class — verify current editions/clauses and interpretation with HR/IR.
- CHHHS Controlled Document Management Policy and Controlled Documents Guideline; retained existing delegated approval routes.

## Additional prioritised capabilities — 11 November 2026

### Must for the first usable release

| ID | Requirement | Validation |
|---|---|---|
| M18 | Effective-dated job plan and employment/role eligibility with explicit acting, part-time, leave and cross-site periods | synthetic overlap, vacancy, split-site and mid-cycle change tests |
| M19 | Contracted establishment/position reference kept separate from incumbent, job-plan hours and delivered roster; no inferred funding/establishment from payroll observations | independent reconciliation and unknown-source fail-closed tests |
| M20 | Planned vs rostered vs performed allocation reconciled at compatible time grain, with missing roster data represented as unknown, not zero | source/provenance/variance fixtures |
| M21 | Protected-time assurance: planned and actually delivered CST, displacement reason, make-up scheduling, trend and exception pathway | synthetic displaced CST/partial FTE tests |
| M22 | Defined and traceable approval delegation for acting positions and multiple services, with manager conflict-of-interest handling | delegated authority negative tests |

### Should in first iteration / early expansion

| ID | Requirement | Validation |
|---|---|---|
| S10 | Job-plan scenario comparison showing service coverage impact before committing a change | version comparison / no premature writes |
| S11 | Reusable specialty profiles and clinical-director portfolio allocation including time for governance and service management | scenarios for renal/rural/acute services |
| S12 | Workload, leave, backfill, vacancy and escalation evidence with no private performance-case detail | safe synthetic test |
| S13 | Service-level capacity report with named source, temporal grain, exclusions and uncertainty, not an unqualified productivity score | metric-source tests |
| S14 | Plan change-impact preview (roster, clinic capacity, service hours, training/CPD) with no automatic cross-system change | downstream read-only contract tests |

### Could — roadmap, not baseline

C07: demand/capacity simulation using CareOps-Sim where independently justified; C08: equitable distribution of clinical/nonclinical portfolios without opaque ranking; C09: rotation and cross-facility job-plan library; C10: credentialing SoCP and temporary/expiry signals as read-only, authority-qualified guardrails; C11: establishment/payroll/finance and costing reconciliation by source-qualified feeds; C12: optional rostering, leave and HR system adapters; C13: controlled annual review analytics; C14: longitudinal staff career/development and education planning (separate privacy purpose and authorisation); C15: rule-change impact simulator and backwards-compatible migration; C16: regional/rural travel and outreach capacity optimisation; C17: generic job-plan engine with HHS-specific configuration and separately governed credentialing adapter.

### Exclusions and harm-reduction guards

No automated performance ranking or employment decisions; no combining private credentialing, complaint, HR case and productivity information without explicit approved purpose, lawful authority and tested access boundaries. Job-plan versus actual activity is an operational planning measure, not evidence of individual productivity or compliance by itself. Avoid automation of roster/payroll changes without reconciliation, consent/authority and rollback.

## Source-informed clarification — prospective job planning (draft instruction and restricted exemplars)

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| M23 | Must | Clinician self-assessment before documented negotiation; record proposed work, pressures, portfolio, objectives and enabling-resource dependencies | synthetic self-assessment and negotiation scenarios |
| M24 | Must | Whole-of-job prospective plan with service-level demand/capacity assessment and funded establishment reference before individual allocation | dependency/source completeness gate |
| M25 | Must | Hours first; four-hour sessions optional display; fortnightly hours reconciliation; optional N-week schedule cycle and annualised activities; no crude timesheet-only model | cycle/denominator/property tests |
| M26 | Must | Consultation outcome, union/representative option and employer determination separately documented; preserve safe interim/dispute state and consultation/notice configuration | negative/positive state tests |
| M27 | Must | Resource-dependent outputs, quality/safety ranges, exclusions and reasons for cancellations; avoid punitive automatic performance scoring | output/resource validation + privacy review |
| M28 | Must | Exception workflows for CST loss/recovery, cancellations, leave/vacancy cover, change of FTE/SoCP, work beyond ordinary hours and roster changes | scenario matrix |
| M29 | Must | Keep originals, extracted text, identifiable schedules, document metadata and real staff evidence out of Git, PRs, test artifacts and generated releases; prohibit synthetic fixtures based on personal examples | .gitignore, staged-file/asset checks, privacy leak scans, review |
| S15 | Should | Alternate schedule perspectives: week/date, multiweek cycle, AM/PM session, portfolio and annualised budget | synthetic UX tests |
| S16 | Should | 8–12 week new-plan check, quarterly service-level exception review and annual individual review as configurable draft-derived defaults, not silently enacted local policy | rule-version tests |
| S17 | Should | Explicit meal breaks, off-service/on-service handover constraints and cross-site resource dependencies | overlapping and capacity fixtures |

These originate from an unapproved draft work instruction and historical individual schedules held off repository. For industrial requirements, confirm current authority before activation; current sample values are illustrative design tests only. See [restricted-source boundary](source-boundary.md).

## Policy-driven lifecycle and role dashboards — added requirement set

| ID | MoSCoW | Requirement | Required acceptance |
|---|---|---|---|
| M30 | Must | Versioned effective-dated policy-driven regular individual review obligations with adjustable frequency, reminder lead times and explicit migration of future dates | due/no-change/change/new-policy/idempotency tests |
| M31 | Must | Medical officer may create and edit a draft at any time; **explicit submission** starts consultation/validation/approval; draft autosaves do not send repeated approvals | role-scoped state transition and duplicate-notification tests |
| M32 | Must | Preserve each submitted and approved version immutably, with active/effective interval, parent/changes, exact decisions and archival metadata; view/compare permitted prior versions | version-diff, concurrent revision, old-link readback tests |
| M33 | Must | Practitioner dashboard with active plan, pending work, requested changes, due reviews, prior versions, exports and actionable self-service | synthetic actor UX/accessibility tests |
| M34 | Must | Approver dashboard with delegated case queue, due/overdue, diffs, rule and CST exceptions, review history and explicit human decisions | delegated-role acceptance and negative direct-access tests |
| M35 | Must | Users with both practitioner and approver roles receive both independently scoped workspaces; single-role users see only authorised workspace and direct data | dual-role/acting/scope conflicts, cross-service and segregation-of-duties tests |
| M36 | Must | Review without change supported as documented human attestation with due-date advancement, not manufactured revision or auto-approval | unchanged review + history evidence tests |
| M37 | Must | No replacement of active approved plan until future effective date and delegated authorisation; pending, rejected, withdrawn and interim statuses preserved | failover/effective-date/delayed-approval tests |
| M38 | Must | Idempotent schedule, routing, notification, decisions, activation, export, retries with operations/evidence ledger | at-least-once replay and concurrency tests |
| M39 | Must | Confidential history access, retention/hold, direct SharePoint endpoint denial and history export restricted by role/record purpose; no employee plans in Git or CI | threat model, bypass and record-retention tests |
| M40 | Must | Qualify standard-only SharePoint-based decision engine and verify hosted Power Automate Approvals' Dataverse dependency/licensing before using optional connector | deployment inventory/licence and delegated-signature review |
| S18 | Should | Consolidated notifications and reminder/escalation settings without private contents | digest throttling/leave/expiry cases |
| S19 | Should | Reassignment/acting-manager and multi-service delegated case routing | authority valid interval and no-self-approval cases |
| S20 | Should | Automated orphan-task, rule-expiry, approval-latency, connection and snapshot integrity monitoring | operational health and reconciliation cases |
| S21 | Should | Aggregate approved plan coverage and workflow cycle-time reporting with privacy suppression | aggregate scope/grain tests |
| C18 | Could | Optional read-only team demand/capacity summary and portfolio heatmap, subject to data source qualification | design prototype |

See [lifecycle design](lifecycle-dashboard-design.md) and [lists/flows/artefacts](flow-list-artefact-catalogue.md). **Due-date defaults remain unapproved until an authoritative CHHHS policy edition and delegated owner are confirmed.**
