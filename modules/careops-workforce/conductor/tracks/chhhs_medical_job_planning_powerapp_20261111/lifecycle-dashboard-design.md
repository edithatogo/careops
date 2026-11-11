# Policy-driven lifecycle, practitioner and approver experience

**Status:** Proposed design, not implemented. Owner: CareOps Workforce. Approval and industrial schedule are driven by versioned, authoritative rules; the CHHHS draft medical job-planning work instruction is not an approved source of review dates.

## Governing invariant

- One `JobPlan` stable identity with `ActiveApprovedVersionId` and `NextReviewDueAt` projections. One or more **immutable** approved `JobPlanVersion` snapshots with effective date range, hash, schedule and recorded approvals. Do not use SharePoint version history as the sole legal/business version store.
- A practitioner may **initiate a draft at any time**, whether a review is scheduled or not, and may edit a draft until submission. Each material submission creates a new immutable candidate snapshot and a `ReviewCase`. Saving a draft does **not** send repeated approval emails. Resubmission of returned work creates a new candidate and links to the prior submission; preserve comments, decisions and receipt chains.
- An approved plan remains in force while changes await review; a new version becomes active **only at its approved effective time**. Existing active and pending versions are distinguishable in all views. Temporary/interim arrangements use their own approved effective-dated records and do not overwrite the historical baseline.
- The practitioner can see and download all **authorised** prior versions, their lifecycle status, effective intervals, approval dates and a field-level/weekly comparison. An approver can see only plans in their delegation and permitted historical cases. `ClonePriorVersion` always creates a new draft; never mutate history or restore a past approval into the active slot.
- Policy schedule: `ReviewRule` version with applicability, effective-from/to, frequency/interval, anchoring event (approval/start/previous-due etc.), grace policy, reminder offsets, exclusions, owner and source authority. `ReviewObligation` records an exact due date, applied rule edition, generated event key, status, expected reviewers and evidence. Policy edition changes do **not** overwrite old obligations or imply reapproval of existing plans. Recompute future obligations by an explicit, audited migration decision.
- Configurable draft-derived candidates include early review, annual individual review and quarterly **service-level exceptions**. These are *different obligation types*. No arbitrary review periodicity is asserted as approved CHHHS policy. Review due triggers a case/task or prompt, not a new approved version. A no-change review needs a captured human decision and evidence; it does not silently self-approve.
- Modifying a current approved version is **never direct**; every new submitted version enters the required checks. No forced resubmission of identical drafts: show diff and allow an explicit no-change review with delegated attestation. Approved minor changes may use a shorter authorised route only if separately permitted by the effective rule.

## State model

`Draft -> Submitted -> OfficerConsultation -> ClinicalDirectorReview -> HRIRValidation -> DelegatedApproval -> ApprovedPendingEffective -> Active`; optional `ReturnedForChanges`, `Withdrawn`, `Rejected`, `Escalated`, `Suspended`, `Superseded` states. Approval routing derives from role/service/delegation and must be independently rechecked before each state transition. Missing/expired authority fails closed. Parallel reviewer input may be allowed; employer approval is a distinct decision, not the officer's acknowledgement. Partial approvals stay in a pending case until the required set is satisfied. Multiple active appointments may require separate plans or approved linked components; do not assume one manager controls all services.

Schedule engine should run daily in Australia/Brisbane with deterministic `ReviewObligationKey=(PlanId,ReviewRuleVersion,ReviewPeriod)` and transactional/idempotent upsert; verify no duplicate tasks, emails or cases under retries. Schedule rule snapshots, later change notices, holidays, leave deferrals, inactive appointments and transfers must be handled explicitly. Reminders are batched/throttled, escalate only to authorised managers, and disclose minimal personal information.

## Practitioner dashboard (my plans)

- Current approved plan: **effective date, status, role, services, next review**, read-only live schedule; distinguish planned ordinary hours, CST, on-call and annualised commitments.
- Quick actions: `Start revision`, `Continue draft`, `Submit for review`, `Respond to changes requested`, `View history`, `Compare versions`, `Download approved copy`.
- Pending work: who currently holds it, stage, date submitted, turnaround, blockers, consultation/representation option, reason for returned proposal, notifications and audit trail.
- Upcoming: policy review due date, optional reminders, approved CST displacement/recovery and action obligations.
- History: filterable timeline, side-by-side/field-level diff for session weeks, employment hours, CST, leadership, work location, activity expectation and resources; previous rendered documents; no editing history.
- Accessibility: keyboard, screen reader, responsive tablet/desktop and phone summaries; no hidden-content security assumptions.

## Approver dashboard (my review queue)

- `Assigned to me`, `My team/service`, `Awaiting HR/IR`, `Escalated`, `Overdue`, `Recently decided`, and `Due for scheduled review` views limited by effective delegation and SharePoint access.
- Individual queue item: prior approved version vs proposed snapshot, changed hours/CST by category, delivery/resource implications, contracting/IR rule applicability, consultation record, comments, exceptions, current approver stage, source evidence. Offer `Approve`, `Return for changes`, `Request clarification`, `Escalate`, `Reject` only as delegated.
- Team metrics: scheduled due, submitted, aged, overdue, requests returned, pending consultations, unresolved CST exceptions, approved coverage changes. Avoid ranking individuals or conflating absence of data with zero performance.
- An approver who is also a practitioner has **both** workspaces through role-scoped tabs; selecting one view does not change underlying SharePoint permissions. Multiple concurrent roles/service delegations can be selected via a scoped context picker. Requestor cannot self-approve where segregation-of-duties applies, including delegated acting roles.
- Administrator/operator view is separate from employer approval: schedule configuration, failed flow replay, migration, permission/connection health and audit export. Operational admins must not inherit approver rights automatically.

## Permission and version-history controls

`RoleAssignment(ActorId, RoleId, ServiceId, PositionId?, DelegationId?, EffectiveFrom, EffectiveTo)` supports user-with-both-roles, user-with-one-role, substitutes, acting periods and explicit expiry. Direct SharePoint URLs and flow endpoints must enforce the same read/write constraints as the app. Any per-item SharePoint ACL churn must be tested for scale and correctness; if least privilege cannot be guaranteed, stop instead of relying on filters. Retention/records policies and version history settings are CHHHS decisions. Approved snapshots have explicit protected record identity, indexed audit events and a restricted export document library, with duplicate-safe file naming and hash verification.

## Visual review scenarios

1. Physician submits voluntary change mid-cycle; active approved plan unchanged pending consultation/HR check/approval; new plan effective on a future date; old version remains accessible.
2. Scheduled obligation and spontaneous submission occur same day; same review period may be satisfied by a qualified case without duplicate approvals.
3. Practitioner/Clinical Director has both dashboards; cannot approve their own case when policy prohibits.
4. Manager only sees delegated reports; practitioner only sees own plans; direct SharePoint URL for unrelated plan denied.
5. Returned revision -> re-draft -> resubmit; prior discussion preserved, reminders from obsolete case cancelled.
6. No-change annual attestation records a decision and advances due date under the effective rule without creating a fake amended plan.
7. Rule changes mid-cycle; historical due date remains, future remapping requires separate recorded migration.
8. Multiweek plan expires while a submission awaits review; defined approved interim/exception pathway rather than undocumented automatic extension.
