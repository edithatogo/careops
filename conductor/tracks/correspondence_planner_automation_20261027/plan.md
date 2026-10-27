# Correspondence: automatic linked actions and completion reflection

## Implementation checkpoint — 27 October 2026

COR-16.1–16.6 are complete at source, stopped native configuration and bounded
fictional runtime scope. Actual connector runs verified creation/replay, reciprocal
links, completion/reopening with manual closure, partial-save/lost-response recovery,
concurrent writers, conditional-claim conflict, unavailable/ambiguous tasks, real
SharePoint pagination and waiting-history protection. Wrong-plan/denied-read and
incomplete Planner catalogue cases use explicit fictional fault injection; they do
not claim a real permission revocation or another plan's access.

Runtime uncovered and corrected the SharePoint Yes/No numeric filter, both native
continuation property spellings, encoded list GUID continuation scope and failed
waiting-history projection cleanup. Version-date UTC interpretation is qualified
for the selected deployment through actual transition/version wire evidence.
The final canonical production graph is independently read back Stopped, both enable
flags false, with existing connections and no active runs. The original intake and
manual action graphs, states, connections and run-only access remain unchanged;
pre-existing live record IDs, versions and Modified timestamps are unchanged.

The current owner's weekly failure digest was explicitly disabled through the
supported unsubscribe control, separately from disabled worker repair alerts. This
is an owner preference, not tenant-wide or intended-user notification acceptance.
Fictional tasks are unassigned and no email/send action was used. Failed assertions,
interrupted observations and rejected harnesses remain in private evidence with
actual-effect reconciliation; only qualified cases count as acceptance.

Role journeys, two-person plan sharing and separately authorised pilot/activation
remain open. CMO review links and finite rollout preparation are completed below. Tests
used a temporary manual-only fixture harness; the production recurrence was never
enabled. Retained fictional records/tasks preserve the recovery evidence.

The existing CMO landing and operational health pages now contain additive closure-
review, sync-exception and waiting-date links with explicit Off/manual-closure
wording. Full saved content/control/link readback and major publication are verified.
Original views, live record metadata and all flow definitions/connections/states
remain unchanged. No flow run, sharing change or email send occurred.

Configured ESO page/receipt read and manual action run-only rights are verified;
actual intended-user operation remains unverified. The log other-user effective-
permission query returned403, which does not prove access absence. Native Planner
owner navigation works, but the plan remains private to the owner. Sharing requires
a group with no visible notification-suppression control; no sharing mutation was
made under the current no-email instruction. These are explicit access gates.

COR-16.8 preparation is complete as a finite rollout/stop proposal; execution remains
gated on COR-16.7 and new activation authority. The proposal specifies at most five
prospective IDs and an attended four-cycle/60-minute window, a new cohort-restricted
Stopped candidate before any Start, no backlog opt-in, exact stop/in-flight checks,
manual fallback and evidence preservation. No real cohort or activation was selected.

[Implementation, tools, native contracts and recovery guide](../../../modules/clinical-hub-core/conductor/correspondence-automation.md).
This increment retains manual correspondence closure, no assignments, Standard
connectors only, no Premium or Copilot, no new email delivery and unchanged intake.

Current authority, 27 October 2026: implement autonomously using Standard connectors only; keep activation on hold, existing intake unchanged, no emails and manual correspondence closure. Earlier plan-only text below records the original planning boundary and is superseded for implementation, not activation.

Status: IMPLEMENTATION IN PROGRESS. Restored27October2026; generic CMO/EDMS source. COR-16 extends the existing correspondence
solution; it does not reopen completed capture work. User requested this plan and
Conductor updates; later explicit user authority selected implementation while keeping activation held. This document alone grants no activation, correspondence action, sharing or email authority. Earlier sharing authority remains separate.

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
| COR-16.7 | Add log/CMO closure-review and exception links; qualify intended-user access. Depends16.5 and16.6; the ESO journey depends on verified two-person Planner sharing. | Both roles can use log/task links and review view; only human closes a fictional matter; the ESO cannot edit flows; no broader audience. Agent-owner navigation is not the ESO acceptance. |
| COR-16.8 | Prepare prospective rollout, stop/rollback and finite pilot scope after16.6; execution depends on16.7. | Explicit opt-in/cutover rule, volume bounds, notification assessment, no bulk historical creation, fallback, in-flight reconciliation and original flow restoration procedure. Activation remains separately held. |
| COR-16.9 | Only after later explicit implementation/activation authority, run a bounded eligible pilot, then decide ongoing activation. Depends16.8. | Normal recurrence creates once, later task completion reflects within the agreed interval, manual closure verified, no duplicate/manual race or view regression, exact final On/Off states and authorised scope read back. No eligible event is inconclusive. |
| COR-16.10 | Reconcile evidence, operator guide, generic source and Conductor closeout. Depends16.9. | State planned/local/native/runtime/operator evidence separately; portable CMO/EDMS wording, private IDs/data excluded, source release checks separate from native acceptance. No publication authority inferred. |

- [x] COR-16.1 — exact reuse and access map.
- [x] COR-16.2 — contract and view protection.
- [x] COR-16.3 — focused fictional tests first.
- [x] COR-16.4 — disabled local candidate.
- [x] COR-16.5 — stopped native preparation and readback.
- [x] COR-16.6 — fictional runtime/recovery proof and restoration.
- [ ] COR-16.7 — closure-review surface saved; configured access checked; actual ESO log/Planner journey and sharing unresolved.
- [x] COR-16.8 — finite rollout/stop proposal prepared; execution blocked by16.7 and activation hold.
- [ ] COR-16.9 — separately authorised bounded pilot and ongoing decision.
- [ ] COR-16.10 — evidence, generic guidance and closeout.

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

Current authority permits stopped implementation; activation remains held. Standard connectors only; no Premium,
Copilot, AI, new licence, background external monitor, assignments, automatic
reminders, email sends or capture-source changes. Prior approval for the ESO's
system-generated sharing notifications does not approve task notifications to
other recipients. the existing intake flow stays unchanged. Reuse existing receipts and resources;
additional authorised sources, summaries, reporting, classification assistance,
and multi-task orchestration remain deferred. Automatic correspondence closure is excluded.

## Recovery and evidence boundary

Recovered on27October2026 from the retained correspondence plan. Restoration itself made no tenant changes. Subsequent explicit implementation authority produced the stopped configuration in the checkpoint above; remaining operator/pilot tasks are not complete. Exact deployment bindings, native flow state, access grants, authentication handoffs, operational receipts and person-specific sharing authority remain private. Existing completed source and private qualification history are retained; this plan neither replays them nor grants implementation, activation, sharing or publication authority. Automatic task creation and completion reflection are qualified only on bounded fictional records; production activation remains held and correspondence closure remains manual.
