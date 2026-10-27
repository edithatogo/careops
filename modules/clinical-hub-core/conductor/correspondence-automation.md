# Automatic Planner actions: prepared, activation held

Implementation checkpoint, 27 October 2026. The portable compiler is
[correspondence_planner_automation.py](../scripts/correspondence_planner_automation.py).
The deployment-specific worker is prepared Stopped with AutomationEnabled=false
and LinkEnabled=false. Bounded isolated fictional end-to-end and recovery checks are verified; production recurrence and intended-user acceptance remain held.
Exact native IDs, bindings, run histories and readbacks remain private.

## What it will do when separately qualified and enabled

The proposed15-minute worker scans a bounded, paginated set of open entries.
Only Reviewed entries with PlannerActionRequired=true and a nonblank, approved
PlannerActionTitle (maximum120characters) can create a task. Existing rows are
not opted in. The existing manual linked-action compiler supplies the same stable
key, ETag claim and partial-create/link recovery. Manual and automatic writers
must retain that shared protocol. One serial worker alone is not a cross-flow lock.

One Basic Planner task is linked to one correspondence entry. Existing task IDs
are checked directly; a plan-wide scan is needed only for creation/reconciliation.
Incomplete scans and ambiguous matches refuse creation. An uncertain create is
never retried blindly. Recovered backlinks retain existing task references and
human edits. Deleted linked tasks become unavailable, rather than being recreated.

PlannerTaskState and PlannerTaskCompletedAt reflect the linked action. Missing,
invalid, deleted or inaccessible tasks cannot be marked Completed. Reopening a
task updates an open correspondence snapshot and clears its current completion
date; history remains. Closed correspondence is excluded from routine polling.

**Completing a task never closes or reopens correspondence.** Ready for closure
review is a last-recorded action snapshot. A person checks the actual task, the
whole correspondence, response/approval and remaining work, then explicitly edits
Progress. Progress, review state, source links, human notes and human due dates
are not part of the worker's write allowlist. Cross-system closure is not atomic.

## Prepared fields and views

Reuse equivalent qualified fields; the additive optional fields are
PlannerActionRequired (default No), PlannerActionTitle, PlannerTaskState,
PlannerTaskCompletedAt and WaitingSince. The existing four task-link fields retain
their meanings. Do not overload PlannerLinkState with task progress.

The staged nondefault views are Ready for closure review, Planner sync exceptions,
Waiting too long - qualified and Waiting date unknown. Original views/defaults
remain intact while held. No automatic task snapshots exist merely because a
view was saved. Creation/claim errors remain visible in run history and the existing
link-exception route; the sync view specifically shows Unavailable task snapshots.

WaitingSince is a technical projection of the actual contiguous waiting-status
interval, not Modified or first observation. It uses descending version IDs,
the current version label and an actual status boundary. Missing/truncated history
stays unknown. A page exactly at the100-version cap cannot prove complete history
without a visible status boundary. Re-entry starts a new interval; leaving waiting
clears the current projection. A stale ETag prevents a conflicting date write.

VersionDatesUtcQualified is true only for the deployment whose version-date wire
format/timezone and actual waiting transitions were qualified in bounded runtime.
Portable defaults remain false for every unqualified deployment. SharePoint version
Created can omit an offset; never append Z on an unqualified assumption. The first
metadata sample matching an item UTC date does not prove a complete waiting
transition. Do not switch the existing Modified-based waiting view to the qualified
view or activate task sync before this dependency is resolved. Unknown dates have
their own view; no historical business dates are guessed or bulk filled.

Unchanged task snapshots and waiting dates cause no log write. Cycle status and
freshness use native run history; do not update every log row just to show a poll
timestamp. Existing capture receipts retain their source-message contract. Do not
invent email keys or widen required receipt fields to store Planner events. Use
the qualified run-history/technical-state fallback until a compatible existing
receipt operation is separately mapped. No second business register or monitor.

## Tools and native-save details

- Generate the stopped candidate from explicit private bindings using the repository
  Python3.15.1 environment. Local source compilation performs no tenant request.
- Use the guarded M365 CLI SDK for exact flow/schema/view operations, prospective
  journal checks, one transport attempt, no redirects and independent readback.
  Retain the successful VS Code workload client/account/tenant/resource and callback.
  Do not request Graph Tasks consent to bypass its scoped permission gap.
- Use only native recurrence/control actions and Standard SharePoint/Planner
  connections. SharePoint HttpRequest here is the standard SharePoint connector
  operation, not a Premium HTTP/custom connector. No email, assignment, due-date,
  comments, Copilot, AI, paid child-flow or external runtime action is present.
- With application/json;odata=nometadata, view-creation ViewFields is a plain JSON
  array. A results-wrapper is rejected as StartObject where StartArray is required.
  Inspect ordered fields using the view's ViewFields navigation endpoint; selecting
  ViewFields on view metadata does not implicitly expand it. Reconcile a saved
  view before retrying when only the local readback assertion failed.
- ParseJson supports secure inputs here, not secure outputs. The task-contract
  parser projects only numeric percentComplete; the GetTask action retains secure
  inputs/outputs. Never strip supported data protection to pass validation.
- The native validator is not runtime proof. Native definition readback may add the
  known OpenApiConnection authentication annotation or identical evaluated recurrence;
  validate exact permitted additions, complete definitions, both connections and
  Stopped state. Preserve errors and reconcile actual effects before a new save.

## Held runtime, rollout and recovery

The [COR-16 track](../../../conductor/tracks/correspondence_planner_automation_20261027/index.md)
keeps verified fictional native runtime, outstanding operator journeys and activation separate. The
current activation hold is not released by source tests or saved configuration.
The worker is restored Stopped after temporary manual-only fictional harness runs.
Production recurrence must not start under the activation hold. No test email is needed.

Before activation: verify intended two-person plan access, final review surfaces,
finite rollout scope and intended-role notification behaviour.
Provider account-wide failure digests are separate from per-flow repair alerts;
do not claim no service emails merely because the graph has no Send action.

Use isolated fictional correspondence and unassigned fictional tasks for the
bounded native cases: repeated/manual collisions, partial create/link save,
completion/reopen/deleted tasks, stale ETags, incomplete pages, unavailable reads,
waiting history gaps and manual closure. Retain the production rejection semantics;
a harness that changes failure into success does not prove the production terminator.
Inspect effects, not only the run result. Keep real entries unselected and unchanged.

For a later pilot, choose a finite prospective opt-in cohort and explicit start/end,
bound pages/volume, inspect cycle health and exactly-one task/link/state outcomes,
then decide ongoing use separately. Default page size20/max5pages and serial10-second
per-item delay are provisional capacity limits, not measured performance or a
guaranteed15-minute update time. A remaining page fails the cycle visibly.

Stopping the owned worker, with both flags false, is the fallback. Reconcile queued
and in-flight effects; stopping cannot undo a task already created. Preserve task
IDs, backlinks, log history, captured records, original views, manual flow and its
run-only ACL. Use the existing manual action while automatic work is held. Retain
new optional fields/staged views inert rather than deleting records to clean a test.
Existing intake is unchanged throughout this increment. Future sources, summaries,
reporting, classification assistance, assignments and multiple tasks remain deferred.

## Qualified runtime and recovery checkpoint

Actual connector effects verified one task per eligible fictional record, reciprocal
links, repeated-completion no-op, completion/reopening reflection and preserved
human task titles. Manual correspondence closure survives synchronization. A
created task with its link save deliberately omitted is recovered without another
create. A real create followed by injected lost-response failure is reconciled;
the handled cycle succeeds, which is distinct from hiding an unhandled failure.

Concurrent copied manual/automatic cores produced one task through catalogue
reconciliation, with a backlink conflict retained as a failed cycle. A separate
parallel conditional-claim primitive accepted one identical native ETag claim and
rejected the other with PreconditionFailed; it performed no task operation.
Missing tasks, wrong-record identity, ambiguous keys and pending claims fail closed.
Wrong-plan and denied-read outcomes were injected, with no actual ACL change or
read of another plan. The existing manual flow itself was not invoked or modified.

Native SharePoint Yes/No OData filtering requires numeric1 for this route; Boolean
true unexpectedly selected No values. Keep the independent fresh Boolean eligibility
guard. Actual pages expose odata.nextLink and encode GUID quotes as %27; accept only
the exact same site/list/items prefix in either qualified form, preserving its
query encoding. Both continuation spellings are checked for history completeness.
Real multi-page scans succeeded; page-cap and injected incomplete Planner results
retain the production failure terminator and refuse speculative creation.

Waiting dates use the actual contiguous human status transition, excluding later
technical edits. Empty/incomplete history leaves unknown. If history processing
fails, a fresh ETag-protected technical-only fallback clears a stale projection
while retaining the failed cycle. A concurrent edit causes conflict, never an
unconditional overwrite. Fixture fault responses must wrap the connector DTO in
body when Compose substitutes an action referenced through body(action).

Inspect loop action repetitions for per-record evidence: a flat actions summary
can show only one iteration and is insufficient to count actual creates/recovery.
Preserve the exact run identity after interrupted observations; resume bounded
GET-only observation without another invocation. Reuse one cached qualified SDK
client in a bounded read batch to reduce repeated Keychain initialization. Never
log raw Axios exceptions or transport/auth objects; store sanitized status/message.
Do not replay consumed write manifests or rewrite historical journal entries.

The current owner's account-wide failure digest is disabled by explicit user
choice and native unsubscribe success, separately from worker repair alerts. This
does not prove all-user notification suppression. No assignments, due dates,
comments, email actions or live-record opt-ins were added. Fictional evidence is
retained privately; no natural-arrival or production acceptance is claimed.
