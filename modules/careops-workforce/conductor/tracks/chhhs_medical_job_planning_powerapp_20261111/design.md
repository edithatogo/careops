# Technical design — Power Apps bootstrap

## Bootstrap decision B03

Acquire the **published PnP Weekly Timesheet Template v1.0 (8 Jan 2024)** from [sample](https://github.com/pnp/powerplatform-samples/tree/main/samples/weekly-timesheet-sharepoint). Verify current repo state, actual solution ZIP/hash, contributors' licence, component inventory, import into isolated development environment and connector dependency list. Compare with a fresh SharePoint-generated Power Apps canvas app using a weighted rubric: **security/data fit 25%, adaptation cost 25%, maintainability 20%, standard licensing 15%, source-based ALM 10%, accessibility 5%**. Reject reuse if a sample dependency is noncompliant/unsupported, inaccessible to inspect, or more work than clean bootstrap. Record evidence; do not silently assume the sample is maintained because its gallery remains live. Allow reuse of independent screen/components even if full solution rejected.

## Logical topology

Canvas App -> SharePoint lists (delegable list queries, item-level permissions) and standard solution-aware Power Automate flows -> SharePoint restricted document library. Entra ID supplies authenticated identity. Versioned rule/reference data are read-only to most staff. Drafts and approval evidence persist with separate permissions and audit. No custom public API, Dataverse tables, premium connector or AI dependency. In the dev environment use fictional identities and no patient-level data.

Use environment variables for SharePoint site and list GUIDs, and flow connection references/deployment settings. For canvas-app SharePoint OAuth use data-source environment variables, **not a blanket assumption that canvas apps use the same connection-reference mechanism as cloud flows**. Importing does not create underlying SharePoint structures automatically: deliver provisioning script/template plus idempotent readback and a separate installation checklist.

## Data entities (minimum; names provisional, SharePoint lists)

| Entity | Key / essential fields | Rules |
|---|---|---|
| MedicalOfficers | OfficerKey (pseudonymous dev ID), EntraObjectId, specialty/site, employment class, contracted FTE, entitlement-profile key | external HR source may later replace; minimise identifiable details |
| JobPlans | PlanId GUID, owner key, service, status, ActiveVersionId | one stable identity; status is view only, version governs truth |
| JobPlanVersions | VersionId GUID, PlanId, revision, cycle length, period start/end, FTE/hours reference, rule-set hash, prior version, content hash | approved record read-only; new revision to change |
| SessionBlocks | BlockId, VersionId, cycle week, day, start/end, location, primary code, hours, recurrence, site/travel, note | sessions must not overlap within defined capacity; hours additive and singular |
| OnCallActivities | ActivityId, VersionId or period, availability/telephone/recall/travel, duration, annualisation evidence, source | do not fold availability into ordinary work total |
| ActivityEvidence | EvidenceId, officer/plan/version, event period, activity code, actual duration, source, capture timestamp | immutable entry correction chain; separate from plan |
| Consultations | ConsultationId, VersionId, actor, action, comments category, timestamp | not equated to delegated approval |
| Decisions | DecisionId, VersionId, role, delegate authority reference, rule check, disposition, timestamp, rationale, hash | authorisation and audit trail |
| EmploymentRules | RuleSetId, version, eligible class, ordinary-hours basis, CST threshold, date range, authority and validation owner | unknown rules block approval |
| ActivityTaxonomy | Code, name, class, version, active dates | use renal example C/S/L/T/O as draft seed only |
| ReviewEvents | EventId, PlanId/VersionId, trigger, due, outcome, owner | explicit review cycle and escalation |

**Important SharePoint limitations:** list item-level security has scalability/delegation implications. Before implementation choose between service-scoped SharePoint sites/lists with group-based permissions versus restricted per-record permission breaks. No confidential staff plan is accessible solely via a Power Apps filter. If scale/per-item security is impractical in standard SharePoint, document stop/re-architecture gate rather than weakening access.

## Workflows / lifecycle

`Draft -> Consultation -> ComplianceReview -> PendingDelegatedApproval -> Approved -> Active -> Superseded`. Independent `Rejected`, `Withdrawn`, `ReviewDue`, `Suspended` paths. No approval state generated from silence, email notification or owner edits. Every transition validates caller role, version/ETag, industrial rule set, recorded consultations, required signatures and intended date. Failure remains pending with an actionable receipt. Revisions preserve historical baselines. Conflict resolution is a workflow with HR/IR and delegation boundaries, not a calculator override.

## Power Fx and rules

Prefer simple delegable filters and server-backed list views; keep numeric calculations in unit-testable definitions and independently compare with test oracle. Distinguish planned/actual ordinary hours, contracted FTE, required CST and on-call/recall. Validate sessions per cycle and fortnight (not only week), rounding/break edge cases, and mandatory time allocation. Do not rely on business rules enforced solely client-side: server transitions/flows independently revalidate eligible calculations and permissions.

## Reuse strategy

Retain the candidate's responsive containers/navigation and employee/manager pattern only if validated. **Discard canonical BillTo + TimeEntries weekday-number schema**. Introduce separate screen sets for officer, Clinical Director, Medical Administration and approver. Keep functional modules separable from existing CareOps-PPG; generic workforce job-plan module owned by careops-workforce must not depend on CHHHS legal terms.

## Test and delivery architecture

Source control a solution export/unpacked representation supported by current Microsoft tools after **verifying current pack/unpack/Git Integration status**. Use official Power Platform CLI/Build Tools and solution checker; GitHub Actions can validate source/artifacts but cannot claim import qualification without an authorised tenant. Provision dev Lists using supported Microsoft 365/SharePoint configuration; smoke import with fake accounts; verify flow connection references, environment variables, concurrency/permissions and clean rollback. Release the **unmanaged** source solution for dev, promote a **managed** compiled solution to test/prod only when approved. Provenance manifest pins sample and outputs, test receipts and deployment profiles. Never store access tokens, identifiable medical officer records or tenant-specific secrets in Git.

## Deployment requirements

Required authorised local inputs: development environment ID, target SharePoint site, service-owned connection identities, actual site/list GUIDs, publisher prefix, accessible identity groups, current delegated approver route, data classification/retention settings, DLP policy and document rendering preferences. Default to a manual operator gate before deployment to CHHHS tenant.

## Source and standards

PnP sample: https://pnp.github.io/powerplatform-samples/samples/weekly-timesheet-sharepoint/ ; Microsoft SharePoint canvas app data sources: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-data-source-canvas-apps ; connections: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-connection-reference ; Microsoft Lists canvas: https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-sharepoint-online

## Workforce module alignment and analytics contract

Retain `modules/careops-workforce/Workforce.pbip` as an **independent** workforce reporting asset, not as the app database. Its existing source-locked TMDL/PBIR reporting does not establish approved staffing, funded positions, individual job plans or roster actuals. Add separate versioned opt-in summary contracts for `PlanHours`, `CSTPlanned`, `CSTDelivered`, `RosterVariance`, `EstablishmentVariance` with period, location, speciality, employment class, position and approval-state dimensions where permitted; each metric must carry source, grain, completeness, suppression and decision-purpose metadata. DLP/access classifications govern every feed. Do not modify the existing PBIP or its source-lock merely to register this plan.

**Adjacent integrations:** credentialing capability remains disabled/read-only by default and can provide only a verified effective-dated SoCP reference; PPG provides authoritative policy/template links, not application ownership; Approve/Decisions are optional adapters; Finance and Costing may later receive aggregate conformed outputs. SharePoint standard-only baseline remains the operational store subject to scale and privacy gates.

## Reference-informed process design

The application is **not** a timesheet despite the potential PnP bootstrap. The canonical objects are service requirement/capacity snapshot, officer self-assessment, prospective plan revision, negotiated changes, resource-dependent outputs, industrial verification, delegated decision, implementation handoff and review/exception events. `ActualActivity` remains an optional separately secured observation, never the plan itself. A managed 4-hour session label is optional; authority and calculations are in hours and fortnightly entitlements. Support arbitrary validated repeated N-week cycles, dated activities that replace other allocations, variable annual budgets and alternate AM/PM displays.

### Proposed workflow (requiring adoption validation)

1. Clinical Director/authorised leader triggers appointment, role change, return or review.
2. Medical Workforce/HR supplies approved instrument and employment terms; system records authority version and applicability.
3. Service operations establishes demand, clinic/theatre/ward coverage, funded establishment, constraints and leave assumptions.
4. Medical officer enters prospective self-assessment, clinical/nonclinical duties, concerns, professional development and resource needs.
5. Medical officer and Clinical Director assemble and discuss **all contracted ordinary hours**, CST, indirect care, leadership, educational commitments, flexible/annualised time; on-call/recall recorded separately.
6. Document expected outputs as balanced ranges tied to capacity and enabling resources, not simple throughput scores.
7. Record consultation and outstanding disagreements; route to appropriate HR/IR and authorised decision-maker, with optional representation and safe interim arrangement.
8. On approval, issue immutable job plan and controlled export; translate to rosters/clinical templates as a separate action, without automatic production write.
9. Monitor displaced CST, cancellation reasons, workload above ordinary hours, service coverage and resource limits; trigger early, periodic or material-change review.

All durations, approval routes and rights are to be validated from current CHHHS instrument, not inferred from the draft. Private source originals remain excluded from source control; see source-boundary.md.

## Policy-based scheduling, self-initiated change and workspaces

See [lifecycle and dashboards](lifecycle-dashboard-design.md) and [flow/list catalogue](flow-list-artefact-catalogue.md). Two triggering pathways converge: (a) daily rule-based scheduled review obligation and (b) practitioner-initiated explicit revision submission. A draft may be prepared at any time; autosave is not approval submission. New candidates and consultation are separate from the active approved baseline, which remains effective until an authorised successor begins. Human no-change review is possible. Each review obligation pins the effective `ReviewRule` edition and original due date; subsequent rule edits do not silently alter historical obligations.

Add role-aware practitioner, approver and operator workspaces; a user may hold more than one role, with each view independently enforcing the relevant SharePoint/data access and segregation-of-duties. Provide immutable version timeline, side-by-side diffs, rendered approved historical plans, case SLA/reminders, dashboard notifications and acting-role delegations. Direct links and underlying SharePoint item permissions must match view entitlement; hidden UI is never sufficient.

**Nonpremium implementation correction:** Power Automate's hosted Approvals actions use Dataverse approval infrastructure and may need specific environment roles/licensing. Do not assume the built-in Approvals actions can be deployed as a wholly SharePoint-only workflow. First build a standard connector custom decision engine with an append-only SharePoint decision ledger and explicit delegated checks, then qualify evidentiary/security adequacy and licence posture in a real tenant. Hosted Approvals may be a separately validated opt-in alternative. Include the option for simpler in-app authenticated sign-off, not an unchecked electronic signature claim.
