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
