# Correspondence operator guide

Start here for routine CMO/EDMS correspondence work. Use the existing channel pages,
log, private Basic Planner board and manual-action form; native links and identities
remain in the existing private deployment record. This guide neither changes records
nor grants permission to activate, stop, replay or send anything.

## System and last verified state

Selected intake → existing correspondence log → human review → eligible linked
Planner action → human closure review. Receipts and run history describe technical
processing; the log remains authoritative for the matter, and Planner for its task.

The 27 October 2026 commissioning snapshot records:

| Component | Last verified state | Purpose |
|---|---|---|
| Existing selected arrival capture | On | Capture the authorised source with identity/duplicate checks and receipts |
| Automatic Planner worker | On; both enable flags true; every15minutes | Create one eligible linked task and reflect qualified task/waiting state |
| Existing Create linked action flow | Enabled, manual/on-demand | Selected-action fallback with the same key/recovery protocol |
| Read-only diagnostic probe | Stopped between bounded tests | Technical qualification, not a second intake processor |
| Existing CMO landing/health pages | Published with active wording and worker-history link | Navigation and review; not a continuously refreshed health monitor |

These are dated retained results, not a new live read. Exact scope and evidence are
in private Conductor. New source candidates keep Off defaults. A quiet mailbox or
an empty queue is not proof of healthy processing. Do not turn on an entire flow
catalogue or apply a completed pilot's Off restoration to the running worker.

## Choose the right view

| View | Use and limit |
|---|---|
| Review and active | Captures needing review or matters in progress; review state and business progress are separate |
| Due soon / Overdue | Existing business due dates using the site calendar; missing dates do not become deadlines |
| Waiting | Matters already marked Awaiting further info |
| Waiting too long - qualified | Proven waiting-status start; technical Modified updates must not reset that date |
| Waiting date unknown | Waiting start is unproven; unknown does not mean recent |
| Planner actions | Reviewed entries and existing linkage; a missing link can also be a partial save |
| Ready for closure review | Last recorded completed task on open correspondence; check the actual task and whole matter |
| Planner sync exceptions | Unavailable, ambiguous or mismatched linkage/status; never proof of completion |
| Capture exceptions | Existing technical NeedsReview/Uncertain receipts, including their register/run references |
| All Items | Complete register, preserved legacy values and manual entry |

Open the existing list in SharePoint if a tab hides view selection. Saved public
views still use existing list permissions; they do not make data internet-public.
Original/default views remain available. The older Waiting too long view uses
Modified as a proxy; use the qualified/unknown-date pair for waiting-start reasoning.
Progress is the display label for the Choice field `Completed`, not a Boolean.

## Review, linked actions and manual closure

1. Open the existing matter and its saved source link. Preserve source identity,
   comments, actions, filing and issued history. Capture is not substantive review.
2. Mark CaptureState Reviewed only after actual human review. Set Progress,
   responsibility and due date only when substantively known; preserve unknowns.
3. If an action is needed, record the explicit Action required decision and a short,
   approved action title. Reviewed alone does not create a task. Automatic creation
   also requires open Progress: In Progress or Awaiting further info.
4. Allow the normal15-minute worker interval and check the existing task link and
   latest successful run. One initial task is supported per matter. The interval
   is a schedule, not a guaranteed completion time during outages or a large queue.
   Do not run another create merely because the link has not yet appeared.
5. Complete the actual task in Planner when that action is finished. Qualified
   state/completion time is reflected back; the log's Progress remains unchanged.
6. In Ready for closure review, inspect the actual task, response, approvals and
   remaining work. A person explicitly closes correspondence in Progress only when
   the whole matter is resolved. A completed task or stored snapshot is insufficient.

No-action matters can still be closed manually when appropriate. Completing or
closing correspondence does not promise that a separate open task was completed.
When an open matter's task reopens, sync reflects that state and removes it from
closure review. Closed correspondence is excluded from routine sync; the worker
never automatically reopens or closes it. A human reopening resumes qualification
against the existing linkage, not a fresh task identity.

These are instructions for authorised human use, not actions performed by setup or
handover. Initial production creation eligibility was zero; no real business entry
was marked reviewed/action-required to manufacture a task outcome.

## Selected linked Planner action

The existing Create linked action form remains the manual fallback for a specific
reviewed entry. Use its record ID and approved short action title. Check the current
worker run, deterministic key, task ID and link state first. Manual and automatic
paths share an ETag-protected claim and one-task identity protocol; leave the
automatic eligibility decision as the human actually set it.

A blank link may mean no action, a pending claim or a failed link save. Inspect
Creating/Uncertain/link state and existing tasks before another invocation. Never
clear a key, remove a task or manufacture a new title to force another create.
An accepted create with a failed link save must reuse that task and repair only
the missing link after technical reconciliation. Preserve human task edits and
existing references. Ambiguous matches or an incomplete plan scan remain exceptions.

## Health checks and exceptions

Use the existing operational-health page to open capture receipts, sync exceptions
and the relevant flow's actual run history. Check last successful run/receipt time,
record/task links and freshness together. Failures before a receipt exists appear
in run history; absence of email is not a health signal. Views show stored records,
not continuously verified Planner state or proof that every arrival was captured.

| Situation | Safe response |
|---|---|
| Capture receipt NeedsReview/Uncertain | Match the exact source key and any existing register item first; a failed run may follow a successful create |
| Creating, Uncertain or missing reciprocal task link | Preserve key/task/run evidence; maintainer reconciles the existing task before a field-scoped repair |
| Unavailable/missing/wrong-plan task or stale/failed sync | Treat task state as unknown; do not treat the matter as ready to close or create a replacement blindly |
| Waiting start unknown or version history incomplete | Keep the unknown-date indication; do not infer a date from Modified or first observation |
| Permission or connection error | Preserve the exact client/resource/operation failure; maintainer uses the qualified route, not a new app, consent or copied credentials |
| Unexpected write, duplicate or scope/audience mismatch | Preserve records and history; use the existing manual fallback and obtain exact authorised technical reconciliation |

Routine operator/run-only rights do not include flow editing or state changes.
This guide is not authority to stop the capture flow, change a folder/filter,
invoke a recovery batch, backfill records or send a test email.

## Manual fallback and recovery

When capture is unavailable, continue the established manual log process after
checking existing matters and exact source keys. Record only verified source facts
and links; preserve business fields and do not invent an automatic receipt. Keep
an actual Internet Message-ID, when available, separately from the mailbox-local
ID. Do not substitute subject/conversation text or reconstruct a source URL.
Blank manual keys remain an explicit deduplication limit, not a reason to remove
the unique-key guard. A case-only key rejection requires inspection of the existing
record, not repeated create attempts.

A recovery needs its own authorised source window, complete pagination, exact-match
checks and reconciliation with manual entries. Reuse an existing registration or
task after an uncertain result; do not repeat an email send or create to test it.
Preserve append-only receipts, source history, human edits and issued records. The
maintainer verifies saved effects and fresh ETags before an allowed repair; technical
success is not business closure. Restore a temporary probe to its exact recorded
baseline, not an assumed Off copy of an unrelated production flow.

## Roles, tools and notifications

- CMO/ESO use existing pages, log and the private two-person Basic plan. The ESO's
  selected-action access is run-only; flow editing remains with current maintainers.
  Configured sharing/access is verified; actual ESO first use is explicitly deferred.
- Maintainers use guarded CLI exact-target management/reads and the existing standard
  Outlook, SharePoint and Planner connections. Connector rights differ from CLI login
  or direct Graph Tasks scopes. Use the retained VS Code workload renewal recipe;
  password/MFA/new consent remain human. Never bypass a denial or transfer caches.
- Native Planner activity notices are approved for the existing deployment. Actual
  delivery is unobserved. The worker adds no assignments, due dates, comments, custom
  email/chat actions or new recipients. Do not treat this guide as wider send/sharing
  authority or change another person's preferences.
- Worker repair alerts were verified Off and the current owner previously chose to
  disable the account-wide weekly failure digest. Preserve that choice. The switches
  cover different provider behaviours and do not prove tenant-wide suppression.
- Standard connectors only: no Premium, Copilot, AI Builder or paid runtime dependency.

## Handover and retained follow-ups

Technical continuity and commissioning are complete. Retain actual ESO first use
and fresh automatic intake arrival as explicitly deferred; the first real eligible
automatic-task outcome is prospective and notice delivery remains unobserved. These
are not activation holds. Do not generate an email, opt in a real record or impersonate
an operator to resolve them. Optional sources, summaries, reporting, classification
assistance and multiple tasks remain deferred; automatic correspondence closure
is excluded.

The [continuity plan](../../../conductor/tracks/correspondence_system_20261027/plan.md#retained-follow-ups--not-activation-or-technical-close-out-gates)
records the follow-ups. Use [qualification boundaries](correspondence-readiness.md)
for evidence scope and [technical automation/recovery detail](correspondence-automation.md)
for later authorised maintainer work. Public generic source, private native evidence,
actual operator experience and website publication remain distinct.
