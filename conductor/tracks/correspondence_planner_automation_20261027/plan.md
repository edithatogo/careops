# Correspondence: automatic linked actions and completion reflection

## Current production state — 27 October 2026

The user authorised ongoing production activation for eligible existing log entries.
The existing worker is **On**, both enable flags true, using the same standard
SharePoint / Basic Planner connections and normal15-minute recurrence. Exact full
definition/reference/state readback and the first natural production cycle passed.
Task creation still requires human Reviewed status, an open matter, explicit Action
required and a nonblank approved short action title. No business entry was opted in
or edited to manufacture acceptance. Completing a task never closes correspondence.

No entries met the creation rule at commissioning. The first natural cycle created
zero tasks and made one qualified waiting-date projection; task/link/snapshot
creation writes were zero. A first real eligible task outcome remains prospective,
separate from verified activation. Existing capture and manual linked-action graphs,
connections, states and permissions remain unchanged. Actual ESO first use remains
explicitly deferred by the user; configured access is verified, not impersonated.

Existing CMO landing/health pages now show active status and the worker run-history
link. Ordinary page publication, retained content/control IDs/links and saved status
are verified. The new link's native colon encoding was reconciled through an exact
read-only comparison; no repeat save. A brief owned-worker maintenance pause ended
with full production graph/references restored On. The existing read-only probe was
restored exactly Stopped after page verification. No news, sharing or message added.

Native Planner activity notices remain explicitly approved; delivery was not
independently observed. No assignments, due dates, comments, custom email actions,
Premium connectors or Copilot were added. Keep current owner failure-digest opt-out
and worker repair alerts false. The scoped preflight found no modern list Rules or
custom receiver; existing Microsoft webhook/data-change registrations were retained.
This is not a tenant-wide guarantee of notification suppression.

Technical commissioning and COR-16 closeout are complete. Optional first-use and
first-real-outcome follow-up are recorded without reopening the activation hold.
Historical finite-pilot Off states, rejected candidates, observation interruptions
and actual-effect reconciliation remain retained privately and in source history.

## Historical bounded-pilot checkpoint

The following checkpoint preceded ongoing activation; its final Off state is historical.

COR-16.1–16.6 source, stopped native configuration and bounded fictional runtime /
recovery are verified. Two-person private Basic Planner sharing, configured log /
page / receipt access and manual-action run-only rights are verified. Existing CMO
review and exception links are published. Actual ESO first use is explicitly
**deferred by the user**, rather than a blocker for this pilot.

The authorised bounded pilot passed at isolated fictional scope: one natural
creation cycle produced one task, the completed task reflected on the first
recovery cycle, and the next recovery cycle at the normal15-minute interval
created nothing and wrote no unchanged completion snapshot. The no-action entry
retained its original version and no task. GET-only final audit verified exact task
identity/plan, reciprocal links, actual completion, open correspondence and unchanged
pre-existing fixture/live metadata.

The first observation hit a local CLI Keychain error; cleanup restored Off. The
original deadline and receipts remain unchanged. A finite recovery window reused
the same task/cohort, with no creation replay. SharePoint CLI renewal reached a
password prompt; the independently qualified existing Standard connector performed
the read-only final audit. Two recovery cycle start times establish normal cadence;
no continuous interval or15-minute completion latency across the earlier Off pause
is claimed. No other person's credentials or preferences were used.

Final independent readback verified exact fresh canonical production definition /
full references Stopped, both enable flags false, repair alerts false and no active
runs. Existing capture/manual graphs, states, references and ACL remain unchanged.
The hold is released; this final Off state is the agreed finite-pilot stop, not a
reinstated activation hold. Ongoing real operation remains a separate decision.

Prior source and fictional recovery checks remain valid for unchanged code. Owner
weekly failure digest remains disabled by explicit user choice; worker repair
alerts remain false. Source has no assignment, comment, task-completion or email
action. Approved native Planner notices are a separate provider effect.

This pilot cannot establish a live correspondence outcome, another person's actual
session or indefinite operation. Exact task identities, private receipts, source
metadata and activation/restoration journals remain outside public source.

[Implementation, tools, native contracts and recovery guide](../../../modules/clinical-hub-core/conductor/correspondence-automation.md).
This increment retains manual correspondence closure, no assignments, Standard
connectors only, no Premium or Copilot, no new email actions and unchanged intake.

Current authority: ongoing production activation explicitly authorised; native Planner activity notices approved, existing intake unchanged, no other email actions and manual correspondence closure. Earlier hold/finite-pilot limits describe historical stages.

Status: TECHNICAL COMMISSIONING COMPLETE. Restored27October2026; generic CMO/EDMS source. COR-16 extends the existing correspondence
solution; it does not reopen completed capture work. User requested this plan and
Conductor updates; later explicit user authority selected implementation and then released the hold for the bounded pilot. This document alone grants no activation, correspondence action, sharing or email authority. Earlier sharing authority remains separate.

## Outcome and MVP

After a person reviews a log entry and marks that an action is required, create
one linked Basic Planner task automatically. Reflect the linked task's current
state in the log. When it completes, show the correspondence in a closure-review
view. A person checks the overall matter and explicitly closes correspondence
using the existing Progress field. Completing a task never closes correspondence.

This removes the separate Run step without generating tasks for every incoming
email. Automation starts from an explicit human action decision, not classification
of the email or inference from free text. Recommended defaults below are proposed
configuration, not saved native settings or approved production activation.

## Existing capabilities to reuse

- Existing log is authoritative for correspondence status, review, source links
  and human notes. Displayed Progress has internal name Completed, a Choice field;
  it is not a Planner completion Boolean. Actions is multiline narrative, not a
  reliably structured task request. Qualify exact current choices before a build.
- Existing manual linked-action source uses one deterministic action key per
  list/item, ETag claim, task ID/URL, reciprocal link and partial-save recovery.
  Existing fields: PlannerActionKey, PlannerTaskId, PlannerTaskUrl, PlannerLinkState.
  Reuse its source compiler and proven action graph. Keep the manual flow's native
  identity, run-only audience, owner and working fallback.
- Existing Standard Planner and SharePoint connections, Basic plan and bucket,
  technical receipts, exception views, operational health page and CMO landing page.
- Existing exactly targeted CLI/native-save/readback process and qualified VS Code
  workload authentication. No Graph Tasks consent or new client is assumed.
- Deployment-specific access checkpoint remains private. Verify the CMO and ESO can use the exact Basic plan and log; run-only access must not grant flow editing. If personal-plan sharing needs a native password/MFA challenge, the user completes it. Local design/tests can proceed independently of that operator journey.

## Proposed contract

### Eligibility and one-task identity

Create only if all are true: CaptureState is Reviewed; correspondence is in a
qualified open Progress state; an explicit Action required flag is Yes; a human
approved action title is present (1–120 characters); and identity/link checks pass.
For blank/unknown Progress values, fail closed into an eligibility exception until
the contract defines the value. Do not infer an action from subject, sender, due
date, narrative Actions or task completion.

Reuse equivalent existing structured fields if present. Otherwise propose an
optional Action required Boolean default No, and short Planner action title text.
Do not populate or opt in existing correspondence during setup. The human can
express this decision in the normal log review form; no separate approval service.
Turning the flag off after creation does not delete, cancel or duplicate a task.
It suppresses new creation; existing links remain available for status reflection.
If a task is deleted, do not silently recreate it. Expose it for manual recovery.

Retain the exact existing deterministic key and one initial task per entry.
Existing IDs always take precedence over title matching. Reconcile task-created/
link-save-failed, ambiguous matches and incomplete pagination before any creation.
Manual and automatic paths must use the same ETag claim/key protocol; serialising
one worker alone does not prevent a collision with the manual flow.

Task title comes from approved action text; include existing key/link conventions.
Copy no email body, attachments or narrative by default. No default assignees,
due dates, comments, messages or email actions. Preserve later human task edits.
Multiple actions per correspondence and task dependency graphs are deferred.

### Completion reflection and manual closure

Propose only the missing display fields: Planner task state (Unknown, Not started,
In progress, Completed, Unavailable) and nullable Planner task completed at (UTC).
Use actual Planner percentComplete/completedDateTime only after qualifying their
connector response contract. Do not manufacture a completion date from run time.
Keep PlannerLinkState for linkage/recovery; do not overload it with task progress.

The worker verifies exact plan ID, task ID and stable record identity before any
field-scoped log patch. Only technical linkage/task snapshot fields are writable.
Progress/Completed, CaptureState, Actions, source links, response/approval fields,
human due dates and human task details are never written by status reflection.
Write only changed snapshots, using fresh ETags and re-reading a conflict; never
overwrite a concurrent human edit or retry an uncertain task create.

Completed task + open correspondence appears in Ready for closure review, with
links to the task, log and source. Label it as an action completed, not all work
finished. The person checks response/approval and any remaining work, then explicitly
edits Progress to its qualified closed value. Reuse native version history for the
human change; add no automatic closure or new approval flow. No-task correspondence
can still be closed manually when appropriate. Do not require completing a task
to close a matter cancelled or resolved another way.

If a task reopens while correspondence is open, update the snapshot and remove it
from closure review; retain prior completion in history/receipts. Never automatically
reopen a closed matter. Closed matters are excluded from routine polling; their
snapshot is historical, not a promise of current task state. Human reopening of a
matter resumes qualification/sync without creating another task. There is no atomic
transaction across Planner and SharePoint; final manual closure includes checking
the actual task, and no claim of race-free cross-system closure is made.

Unavailable/deleted/mismatched tasks or denied/throttled reads go to an exception
state, not Completed. Previously completed-at values may remain historical but the
entry must not qualify for closure review while current status is Unavailable.
Show cycle health/freshness alongside the view; stale/failed sync is visibly unknown.

### Scheduling, health and existing view protection

Prefer one small native recurrence worker, proposed every15minutes, concurrency1,
with separate creation and status-reflection phases. Use standard native recurrence,
SharePoint and Planner actions. Generate the common creation core from the existing
compiler; retain the existing manual flow rather than replacing its trigger or
assuming paid child-flow/HTTP invocation. New worker is prepared Stopped. Verify
the supported standard operation graph before selecting final implementation.

Bound each batch, index/filter the eligibility and active-linked queries, and
qualify pagination/continuation. Do not silently truncate a scan or treat partial
results as absence. Process stable task IDs for status; avoid scanning an entire
plan for each unchanged linked item. Creation reconciliation retains its complete-
scan requirement and fails closed when incomplete. Carry pending work forward
without another create. Capture poll interval and capacity limits in acceptance.

Reuse technical receipt/health conventions for creation, transitions, recovery and
errors, plus cycle success/freshness. Qualify the existing receipt schema/key space
before adding new operation types; do not collide with capture source keys, change
mandatory receipt fields or change the existing intake flow's graph. If incompatible, use existing flow
run history and the log's technical exception state as the MVP fallback; document
the exact gap rather than creating a second business register. No per-item log write
merely to refresh a poll timestamp. No new email or Teams alerting.

The existing waiting-too-long view uses Modified as a proxy. Even changed-only
technical updates can move it. Before activation, qualify a dedicated Waiting since
date based on actual human Progress transitions, using retained field-version
evidence where available. Do not use sync writes or first observation as an invented
historical waiting-start date. Unknown dates stay unknown and appear in an explicit
waiting-date-unknown view. Reuse a suitable existing business timestamp if qualified;
otherwise propose one optional field and the smallest supported transition capture.
Verify that task-sync writes do not reset this date or suppress overdue waiting
matters. An exact transition history gap stays explicit. Preserve existing waiting
status semantics and due-soon/overdue views; no bulk status/date backfill.

## Task-level sequence and exit evidence

Task status is recorded in the current checkpoint and checkboxes. Existing historical tests can be reused for
unchanged code only; they do not verify the new automatic route.

| Task | Work and dependencies | Observable exit evidence |
|---|---|---|
| COR-16.1 | Map exact current schema, open/closed choices, manual flow, receipts, views, connection contracts and plan access. Reuse retained CLI/auth; narrow read-only checks. | Field/operation/permission map; owner and exact resource bindings kept private; sharing blocker and scope denials separately recorded. |
| COR-16.2 | Finalise eligibility, missing fields, technical writable-field allowlist, snapshot/freshness semantics and waiting-date protection. Depends16.1. | One reviewed contract with matching/nonmatching cases; existing rows remain unselected; no ambiguous Progress value accepted. |
| COR-16.3 | Write focused fictional tests for auto/manual concurrency, idempotency, partial saves, snapshot updates and closure non-interference. Depends16.2. | Tests distinguish task completion from manual closure and fail for any automation write to Progress or other protected fields. Explicit repository Python3.15.1; no native calls. |
| COR-16.4 | Implement reusable source core and disabled worker candidate; reuse manual identity/graph and standard connections. Depends16.3. | Focused tests pass; full graph policy inspection excludes send, assignment, premium, Copilot, arbitrary HTTP and closure writes. Candidate default Off; existing manual route unchanged. |
| COR-16.5 | Prepare/reuse exact optional schema, saved views and stopped native worker only under later implementation authority. Depends16.4. | Native field/filter/definition/state readback; normal default fields do not alter existing business values; before/after the existing intake flow/manual flow and ACL comparison. |
| COR-16.6 | Bounded fictional native qualification of create, replay, complete, reopen and recovery. Depends16.5. | One task per eligible fictional row; both links; exact status reflection; correspondence never closes automatically; ETag/manual collision, denied/stale/deleted cases and waiting-date protection pass. Restore worker Stopped and reconcile all effects. |
| COR-16.7 | Add log/CMO closure-review and exception links; qualify intended-user access. Depends16.5 and16.6; the ESO journey depends on verified two-person Planner sharing. | Configured role access, log/task links and review view verified; only human closes a fictional matter; ESO cannot edit flows; actual first use explicitly deferred by the user. No maintainer impersonation. |
| COR-16.8 | Prepare prospective rollout, stop/rollback and finite pilot scope after16.6; execution depends on16.7. | Explicit opt-in/cutover rule, volume bounds, notification assessment, no bulk historical creation, fallback, in-flight reconciliation and original flow restoration procedure. Start only under explicit finite-pilot authority. |
| COR-16.9 | Only after later explicit implementation/activation authority, run a bounded eligible pilot, then decide ongoing activation. Depends16.8. | Normal recurrence creates once, later task completion reflects within the agreed interval, manual closure verified, no duplicate/manual race or view regression, exact final On/Off states and authorised scope read back. No eligible event is inconclusive. |
| COR-16.10 | Reconcile evidence, operator guide, generic source and Conductor closeout. Depends16.9. | State planned/local/native/runtime/operator evidence separately; portable CMO/EDMS wording, private IDs/data excluded, source release checks separate from native acceptance. No publication authority inferred. |

- [x] COR-16.1 — exact reuse and access map.
- [x] COR-16.2 — contract and view protection.
- [x] COR-16.3 — focused fictional tests first.
- [x] COR-16.4 — disabled local candidate.
- [x] COR-16.5 — stopped native preparation and readback.
- [x] COR-16.6 — fictional runtime/recovery proof and restoration.
- [x] COR-16.7 — review surfaces, two-person sharing and configured access verified; actual ESO first use explicitly deferred, not impersonated.
- [x] COR-16.8 — finite rollout/stop scope prepared; pilot authority and activity-email approval now recorded.
- [x] COR-16.9 — bounded pilot passed; ongoing production authorised, saved On and first natural production cycle verified.
- [x] COR-16.10 — scope-specific evidence, interruption/recovery, generic operator guidance and technical closeout; no operational acceptance invented.

Each phase ends with exact evidence/readback and a checkpoint before the next
dependency is marked complete, per the [portfolio workflow](../../workflow.md) and private native evidence requirements. A draft
plan, source test or native save alone is not runtime or operational acceptance.

## Required fictional cases

Unreviewed/no-action/closed/missing-title entries create nothing; eligible entry
creates once; repeated polls and simultaneous manual run yield one task; uncertain
create is reconciled without retry; missing link save recovers the same task;
ambiguous match and incomplete pagination stop creation; task edit is preserved;
task completes but log stays open; duplicate completion is a no-op; task reopens
and leaves closure review; task missing/wrong-plan/denied/stale is never marked
finished; manual closure and concurrent human edits survive sync; re-eligible
linked record does not create a second task; technical writes do not refresh
Waiting since; unknown waiting history remains visible; stop/rollback preserves
all real log records, task identities, links, history and original flow access.

## Tools, permissions and exclusions

| Route | Planned use and boundary |
|---|---|
| Guarded M365 CLI SDK | Exact SharePoint schema/views/conditional technical writes and flow management/definition/state/readback under later authority. Keep prospective journal and one-attempt transport. Target rights must be verified; login alone is insufficient. |
| Standard Planner connection | Supported create/get/details/list operations in the existing Basic plan. Connector runtime rights are separate from management auth. No direct Graph Tasks scope assumed. |
| Native Planner Share screen | Existing pending two-person sharing task only, already authorised separately. User completes password/MFA; verify actual saved group and plan/task identities. Does not grant flow editing. |
| VS Code workload auth recipes | Renew affected CLI resource only when expired, preserving successful client/account/tenant/callback and shared state. No stock login, new consent or client cycling after denial. |
| Repo-local source tools | Build/test disabled artifacts with explicit Python3.15.1; no local runtime service. |

Current authority permits ongoing production for entries meeting the established eligibility contract. Standard connectors only; no Premium,
Copilot, AI, new licence, background external monitor, assignments, automatic
reminders, other email actions or capture-source changes. Native Planner activity notices are now
explicitly approved for the existing two-person plan. The existing intake stays unchanged. Reuse existing receipts and resources;
additional authorised sources, summaries, reporting, classification assistance,
and multi-task orchestration remain deferred. Automatic correspondence closure is excluded.

## Recovery and evidence boundary

Recovered on27October2026 from the retained correspondence plan. Restoration itself made no tenant changes. Subsequent implementation produced the stopped configuration, then later explicit ongoing authority produced the verified On state above. All technical tasks are complete; actual ESO first use is explicitly deferred. Exact deployment bindings, native flow state, access grants, authentication handoffs, operational receipts and person-specific sharing authority remain private. Existing completed source and private qualification history are retained; this plan neither replays them nor grants implementation, activation, sharing or publication authority. Task creation/recovery are verified on bounded fictional records; ongoing production scheduling is verified, with a real task outcome prospective because commissioning found no eligible entry. Correspondence closure remains manual.


Notification assessment: current Microsoft guidance distinguishes new Planner from
legacy controls. The absent legacy group-email control is not proof of new-client
state. The user explicitly approved native activity notices for the bounded pilot;
no notification preference was changed and no delivery receipt is claimed.
