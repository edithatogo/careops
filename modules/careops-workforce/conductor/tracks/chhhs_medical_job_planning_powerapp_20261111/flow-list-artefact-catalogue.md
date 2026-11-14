# Proposed lists, flows, artefacts and automations — medical job planning

**Status:** Solution design, not yet provisioned. **Baseline:** standard Power Apps canvas app, SharePoint Lists/libraries, standard Power Automate/M365 connectors. Any native Power Automate Approvals action requires separate tenant/licensing/Dataverse infrastructure qualification; prefer a custom SharePoint-backed decision engine with explicit delegated status and immutable evidence for the baseline.

## Canonical list/data boundaries

| Entity / SharePoint list | Purpose | Key |
|---|---|---|
| `PractitionerAssignments` | Privacy-limited effective-dated owner, position, contracted arrangement, service/role; reference authority not HR master | AssignmentId |
| `PositionAndServiceRequirements` | establishment, service capacity, resource assumptions and source scope | RequirementId, source edition |
| `JobPlans` | Stable plan pointer; one active approved version, schedule projection and last decision | PlanId |
| `JobPlanVersions` | Append-only submitted/approved snapshots and their exact content/rule/taxonomy hashes | VersionId, ParentVersionId |
| `PlanDrafts` | Restricted mutable work in progress; never a governing approved plan | DraftId, OwnerId, ETag |
| `PlanSessions` | Cycle-aware schedule by version/week/day/time/location/activity | SessionId + VersionId |
| `AnnualisedCommitments` | Time budget, expected deliverables and inclusion in contracted hour reconciliation | CommitmentId |
| `ClinicalSupportTimeLedger` | Planned/delivered/displaced/recovered CST as separate typed events and balances | CSTEventId |
| `ReviewPolicies` | Versioned review and reminder rules, class/service scope and authority | ReviewRuleId + Version |
| `ReviewObligations` | Due dates, reminder escalation, supersession and fulfilment evidence | ObligationId, idempotency key |
| `ReviewCases` | Case identity, submitted candidate, current stage, disposition and assigned reviewers | CaseId, SubmittedVersionId |
| `ReviewTasks` | Per-stage actionable items with due, delegation, reassignment, SLA and expiry | TaskId |
| `ConsultationRecords` | Officer/manager discussion, options and unresolved matters | ConsultationId |
| `ApprovalDecisions` | Append-only authenticated HR/IR/clinical/delegated decisions, effective intervals and delegation evidence | DecisionId |
| `RoleDelegations` | User role, service authority, acting/substitute and conflict-of-interest controls | AssignmentId + valid interval |
| `ActivityTaxonomy` and `IndustrialRules` | Effective-dated job-plan codes and eligibility/calculation authority | Versioned keys |
| `ReviewNotifications` | Idempotent notification/digest ledger and consented contact route | NotificationId |
| `FlowOperations` | OperationId, retry, outcomes and failure receipts without private free text | OperationId |
| `ChangeEvents` | Controlled append-only lifecycle event/audit envelope | EventId |
| `ActivityObservations` | Optional separate planned/rostered/delivered evidence, not a de facto attendance master | ObservationId |

**Physical design caution:** Logical entities need not each be separate Lists. Optimise SharePoint count, threshold/indexing, access boundaries and batch concurrency; use actual source/list/readback qualification before freezing physical design. Distinct snapshots and operation identities must remain logically separate.

## Minimum solution-aware flows

| ID | Trigger | Outcome and failure contract |
|---|---|---|
| F01 `CreateRevisionDraft` | practitioner/authorised initiator action | clone permitted active version to private draft; no approval triggered |
| F02 `SubmitRevision` | explicit submit action | check ETag, hours, policy, actor and diff; freeze candidate, create exactly one review case, correlate rule version |
| F03 `ReviewScheduleSweep` | daily recurrence | materialise due/soon-due obligations from versioned rules; deduplicate on plan+period+rule |
| F04 `ReminderAndDigest` | due obligations/case age | 1st/2nd reminders and privacy-minimised daily/weekly digest; throttle and opt-in channels |
| F05 `RouteReviewCase` | submitted/transition event | resolve authorised reviewers, acting coverage, no self-approval; return actionable tasks |
| F06 `CaptureConsultation` | consultation event | preserve officer response, representative option and material issues; advance only on satisfied rules |
| F07 `ValidateIndustrialAndCapacity` | case review stage | validate versioned hours/CST/SoCP/resource constraints; unknown or expired rules block lawful approval |
| F08 `RecordDelegatedDecision` | authorised approver action | assert snapshot hash, delegation and concurrency, append one decision; reject replay |
| F09 `ActivateApprovedVersion` | authorised effective-time event | atomically switch active pointer when effective; supersede previous version, preserve history |
| F10 `ReturnReviseResubmit` | changes requested/clarification | return case with reasons, preserve old submission; link new candidate |
| F11 `ReviewWithoutChange` | scheduled review closure | qualified human attestation, no fake new approved version; advance due under applicable rule |
| F12 `ExceptionAndCSTRecovery` | resource, CST, overtime, cancellation event | restricted exception, recovery task, safe escalation; not automatic adverse inference |
| F13 `VersionExport` | approval/copy request | generate protected PDF/Word where supported, hash and controlled storage metadata; no personal files in CI/Git |
| F14 `ReconcileAndAssure` | daily/weekly | detect orphan tasks, unsupported states, expired delegations, overdue approvals and missing snapshot files |
| F15 `PolicyEditionMigration` | authorised rule edition change | evaluate prospective obligations; no historical rewrite, documented migration batch/replay |
| F16 `AssignmentChange` | authorised position/role update | recompute next review and assessor route; acting role/transfer boundary checked |
| F17 `OperationalHealth` | scheduled or explicit operator | connection/list/permission health, retry and dead-letter-like controlled failures; no email content leakage |
| F18 `ArchiveAndRetention` | controlled retention event | enforce approved retention/hold and archival; never simply delete an approval record on time-out |

Flows must be **solution-aware**, idempotent and bounded, using event/operation ledgers, correlation IDs, immutable submitted payloads and controlled retries. Trigger conditions are necessary but not sufficient to avoid SharePoint list update loops. No future-dated activation, final approval, delegation change or bulk permission modification may occur from an unreviewed automation or time-out alone.

## Artefacts and outputs

- Canvas App with three role-scoped workspaces (practitioner, approver, operator) plus role-aware navigation/dual dashboard.
- Solution package(s), environment-specific deployment settings, connector inventory and standard connector licensing evidence.
- SharePoint schema/index/ACL provisioning and readback, migration/rollback scripts and synthetic fixtures.
- Rulebook and authority/effective-date matrices; workflow state machine and source Mermaid diagrams; reviewed approval RACI and delegated matrix.
- Immutable plan snapshot JSON + approved DOCX/PDF render and side-by-side version differences; controlled links in the app.
- Email/Teams templates with no confidential work-plan contents; in-app task/notification centre and digest schedules.
- Validation report: ordinary hours/CST/annualised allocations, coverage, required resources, exceptions and rule citations.
- Operator console, flow runbooks, error classes, correlation/audit report, retention/records mapping, availability/support ownership.
- Permissions/segregation-of-duties threat model; accessible interaction designs; performance and delegation tests; backout/restore evidence.
- Privacy-minimised service metrics and analytical contract for existing CareOps Workforce PBIP; not per-clinician scoring by default.

## Decision trade-offs and optional roadmap

**First release:** F01–F11, F13–F14, F17 and core rule/permission/reporting controls. F12 for important CST exceptions, staged as essential if the policy requires it. Rule changes and retention F15/F18 must have safe manual baseline even before full automation. Prefer review reminders and approval queues over indiscriminate emails.

**Later:** bulk onboarding, confidentially approved import of historical approved versions, delegated leave-cover reassignment, configurable SLA/escalation analytics, integration with rostering/HR/credentialing/finance, service portfolio planning, demand/capacity simulation and offline/low-connectivity practitioner experience subject to device/local-data controls. No production worker data, insurer/clinical records or actual staff schedules in source repository.

**Microsoft Approvals caveat:** Microsoft's hosted approval actions depend on Dataverse approvals infrastructure and tenant licensing/roles; do not assume these are a free, dependency-free SharePoint-only component. Custom authenticated SharePoint workflow needs its own review of tamper resistance, permission separation, legal evidentiary sufficiency, delegated signature and supported audit retention.
