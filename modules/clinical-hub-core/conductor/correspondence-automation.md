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


## Review surfaces and access checkpoint

The existing CMO correspondence landing page and operational health page now link
to the existing Ready for closure review, Planner sync exceptions and waiting-date
views. Existing content, control identities, original waiting view and default
views are retained. The landing page explicitly says automatic processing is Off;
these views display stored snapshots, not continuously verified current task state.
The qualified waiting views remain staged alongside the original Modified-based
view until the automatic projection is activated under separate authority.

Native page save, major check-in and full text/ordered-link/control readback are
verified. SharePoint can normalize same-host absolute links to relative encoded
paths. Compare parsed HTML with exact same-origin URL resolution; do not unescape
encoded JSON attributes before HTML parsing. Preserve failed local comparisons,
reconcile the already-saved content and avoid repeating a save.

The intended ESO principal has effective page/receipt read rights and the existing
manual action's CanView/run-only grant. Owner-only automatic-worker editing and
original manual-flow editing rights remain unchanged. This is configured access,
not an actual ESO sign-in/session acceptance.

The existing Basic plan is now shared through its native Share screen in a private
Microsoft365 group limited to the two authorised operators. Exact member/owner
readback independently confirms the saved audience; fresh native Manage Access also
shows the two members. The same plan URL and existing task board are retained. Only
system-generated sharing notifications to the ESO were explicitly approved; no
manual email or task assignment/comment action was sent. Notification delivery is
not independently verified. No flow was invoked or changed for sharing.

Configured log access is resolved without another permission grant. Native list
Manage Access identifies the existing Owners/Member grants. SharePoint group
principals identify the exact Microsoft365 group owner/member claims; bounded
directory reads confirm the ESO is both an owner and member of that group. Preserve
the earlier direct other-user effective-permission403 as a scoped limitation, not
absence of access. An empty SharePoint User.Groups result does not enumerate the
user's nested Microsoft365 group owner/member access.

Keep actual intended-user log/task/form journeys separate from configured access;
do not impersonate another account or count maintainer navigation as ESO acceptance.
These remain in the separately held pilot. Existing log records, task content,
flow graphs, connections, run-only/editor ACL and activation flags are unchanged.

After native sharing, record the actual new group privately while retaining old
qualification bindings as historical evidence. Do not rewrite an existing flow just
to refresh its Group Id dropdown when its stable Plan Id is unchanged: Microsoft
[documents that Group Id supports dependent dropdown selection rather than runtime
plan validation](https://learn.microsoft.com/en-us/connectors/planner/#known-issues-and-limitations).
This documentation is not a new post-sharing connector runtime test; keep that
runtime check with the later authorised pilot and preserve current working flows.

## Prepared finite rollout and stop procedure

This is a prepared proposal, not activation authority. Configured access is verified; actual operator-session
acceptance and activation gates remain unresolved. Current production recurrence is Off and both
AutomationEnabled and LinkEnabled are false; no records have been opted in.

1. Before a later authorised pilot, verify the exact existing Basic plan/bucket,
   Standard connections, two-person audience and effective intended-role use of
   the page, log, linked task and manual action form. Verify the ESO cannot edit
   either flow. Resolve notification policy without silently sending invitations.
2. Re-read the canonical worker and original capture/manual graph, references,
   states, ACL and live register metadata into new private evidence. Retain current
   IDs and history. Verify no active or queued worker run; do not reuse consumed
   runtime manifests or restore an obsolete test baseline.
3. Select at most five explicitly approved prospective record IDs. A human must
   first review each matter, choose an action and provide its short approved title.
   Do not select historical backlog or populate action flags/titles during setup.
   Creation eligibility remains Reviewed + qualified open Progress + Action required
   Yes + valid title. Existing linked IDs take precedence; no automatic replacement.
4. Prepare a new Stopped pilot candidate restricted to those exact IDs in the native
   first-page filter, preserving scoped continuation. The current canonical scan
   is broader: it includes active linked and waiting records, so enable flags alone
   do not enforce a finite cohort. Do not activate that unrestricted graph as the
   proposed pilot. The existing fictional ID-filter/pagination method is proven;
   no real pilot IDs or candidate have been selected/saved in this preparation.
5. Under later explicit activation authority, verify the exact cohort graph and
   current bound connections before Start. Run an attended window of at most four
   recurrence opportunities or60minutes, whichever comes first. Proposed recurrence
   remains15minutes/concurrency1; page limit5 and item limit are ceilings, not a
   guaranteed completion latency. The window needs an active maintainer stop; no
   automatic expiry, background monitor or unattended timer has been implemented.
6. Inspect each cycle's terminal state and per-record action repetitions. Reconcile
   exactly one task, stable key, both links and the actual snapshot. Check completion
   leaves correspondence open, reopening clears current completion, and only a
   person closes the whole matter. No eligible arrival/completion is inconclusive,
   not a successful pilot. Do not assign tasks, due dates, comments or notifications
   as part of commissioning. Service digest preference is owner-specific.
7. Stop immediately on unexpected audience/notification, wrong record/plan, duplicate
   or ambiguous task, incomplete scan, conflict, stale/unknown projection or lost
   response. Stop only the owned automatic worker. Read active/queued runs and
   preserve in-flight effects; stopping does not cancel or undo created tasks.
   Reconcile IDs/links before any retry and never blindly repeat a task create.
8. At window end, verify Stopped/no active runs, then save both flags false using
   the current canonical definition and full references. If reverting code, use
   the immediately preceding qualified deployment snapshot after reconciliation,
   not a historical fixture harness. Keep receipts, task identities, backlinks,
   optional fields, nondefault views and native history. Never roll back human
   Progress, notes, source links or unrelated concurrent work. Capture and the
   existing selected manual action remain unchanged and provide the fallback.
9. Reconcile exact native readbacks and the operator evidence. Continuing operation
   requires a separate explicit decision; the finite pilot does not imply ongoing
   activation, whole-lane completion or public source publication.

Private deployment records hold audience, bindings, evidence, baseline snapshots
and pending checks. Source remains generic CMO/EDMS, Standard-only, without Premium,
Copilot, new connections, service identities, email delivery or automatic closure.
