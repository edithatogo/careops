# Correspondence review and manual fallback

This guide describes the generic CMO/EDMS correspondence working surface.
Native links, actual state, identities and verification receipts live in private
Conductor. The guide does not activate intake, send email or change records.

## Views and meaning

| View | Existing source and filter | Working columns | Sort |
|---|---|---|---|
| Review and active | Business register: CaptureState=NeedsReview OR Progress=In Progress | Subject, received date, due date, Progress, CaptureState, To Complete, Saved Email, Actions | Due date ascending, received date descending |
| Waiting | Business register: Progress=Awaiting further info | Subject, due date, received date, To Complete, Comments, Actions, Saved Email | Due date ascending, received date descending |
| Planner actions | Business register: CaptureState=Reviewed OR PlannerActionKey present | Subject, task link, link state, Progress, due date, CaptureState | ID descending |
| Capture exceptions | Technical receipts: State=NeedsReview OR State=Uncertain | Created, State, ErrorCode, RegisterItemId, MessageKey, received UTC, run identity | Created descending |

Use the verified internal field `Completed` for the display field Progress; it is
a Choice, not a Boolean. The views are additional public views within existing
list permissions, nondefault, with30-row paging. All Items and every earlier view
remain available. Public view does not mean public internet access or wider sharing.
Open the existing correspondence tab or the list's saved-view link. If the tab
hides view selection, open the existing list in SharePoint; no new channel/tab is
required. Saved configuration/API qualification does not establish visual rendering.

Review and active contains both captured items needing review and existing active
work. Waiting items can also appear in Review and active if CaptureState still
needs review; the fields describe different decisions. Other existing Progress
choices remain available through All Items. Blank due dates are preserved, not
converted into deadlines. Views do not assign responsibility, classify content,
close correspondence or decide what response is required.

## Normal manual handling

1. Use Review and active to inspect source facts and identify the existing matter.
   Source identity and link provenance are separate from business review. Preserve
   the native source URL and existing comments, actions, filing and issued history.
2. When human review is actually complete, the operator may set CaptureState to
   Reviewed through the existing form. This does not itself change Progress,
   responsibility or deadlines. Only make those decisions when substantively known.
3. Use Waiting for matters already marked Awaiting further info. Enter that Progress
   state only when it accurately describes the matter; no message or reminder is sent.
4. Use All Items for other classes, legacy records and manual entry. Do not bulk
   classify legacy blank CaptureState values. A view omission is not a lost record.

These are instructions for later human handling, not record changes performed by
setup. No role-specific coordination view or another person's workflow is needed.

## While capture is Stopped or unavailable

Continue the existing manual log process. Check whether the matter already exists
before creating a row. Record verified subject, receipt date, source and source URL;
retain established manual conventions for business fields. Do not invent source IDs,
dates, responsibility, deadlines or an automated receipt.

Where the exact Internet Message-ID is available, retain its trimmed case-preserved
value in SourceMessageKey (maximum255) and the actual mailbox-local ID separately.
Do not use a subject, conversation ID or reconstructed URL as a substitute key.
Optional keys may remain blank when not known. A manual blank-key record cannot be
reliably deduplicated by exact message identity; note that limitation for later
human reconciliation. A duplicate/case-only key rejection means inspect the existing
record, not remove its guard or repeatedly submit another create. New prospective
manual captures may use NeedsReview; preserve existing historical values.

When capture is unavailable, keep it Stopped while reconciling the cause. Do not
resubmit it merely to fill a gap. An authorised recovery needs
an explicit source window and exact-match checks; this guide does not grant them.

## Recovering a capture exception

1. Read the receipt's State, ErrorCode, MessageKey and any RegisterItemId. The
   receipt run identity links it to native flow history. Open that existing record
   if present; a receipt is a technical event, not another correspondence matter.
2. Match source identity first. If the register already contains that exact key,
   retain the existing record/history and reconcile the event. A failed run can
   occur after a successful create. Do not blindly create another item or edit a
   source key merely to clear an exception.
3. If no exact match or identity/link remains ambiguous, retain NeedsReview or
   Uncertain and handle manually. Confirm source facts and any earlier manual
   registration before selecting a recovery action. Never mark the technical
   outcome resolved solely because the business Progress is Completed.
4. Preserve append-only receipt history. Do not delete a failed receipt, fabricate
   a success or use a test send to prove recovery. Record technical remediation in
   the existing private change/run evidence before an authorised native recovery.

An empty exception view is not a healthy-capture signal. In particular, a Stopped
flow produces no new live receipts. Failures before a receipt exists are visible
in native run history; use the actual run/action status and last successful receipt
alongside the queue. Connection expiry uses the retained qualified CLI/auth route,
not a new app/consent or a changed identity. No automatic health email is configured.

## Source-link and activation limits

Preserve the webLink supplied by the native source metadata API. One observed
link/API-ID representation remains unqualified; do not label that browser link
broken, reconstruct it or guess a conversion. Intentional Outlook opening may
change read state and is separate from read-only API qualification.

Saved views and this manual fallback form the minimum working surface. Actual
arrival payload/filter/folder/start-boundary behaviour, outage catch-up/concurrency,
source-link usability and operational review remain separate acceptance items.
The working surface uses Standard connectors. Selected linked actions are now
qualified through the existing Planner connector; other optional features stay deferred.


## Intended final flow states

| Flow role | Delivery state | Execution boundary |
|---|---|---|
| Production correspondence arrival capture | On after source/runtime and rollout qualification | Prospective selected intake only; no sending |
| Bounded observation candidate | Stopped after its finite attended window | Restore original graph; deadline alone is not stop proof |
| Read-only diagnostic probe | Stopped between explicitly bounded tests | Not a second intake processor |
| Fictional qualification harness | Stopped and original graph restored | Isolated fictional targets; never production mail |
| Linked action operation | Manual/on-demand when an authorised Standard route is qualified | Explicit selected record; no task per email or automatic assignment |
| Superseded candidate | Stopped, with identity/history retained | No automatic deletion or repurposing |
| Email-delivery path | Off/fail-closed | Exact recipient/content/attachment/send approval required |

This table sets design intent, not current native state. Other Clinical Hub flows
retain their own purpose, owners and qualification; do not switch on an entire
catalogue as a batch. A manual trigger may require an enabled native definition
while still running only on demand. Qualify that behaviour for the selected flow.

Before rollout, re-read the exact baseline and bindings, check pending runs and
connection health, and preserve the stop/restore instructions. After activation,
verify an actual eligible arrival and stored outcome, plus an excluded source or
boundary case using retained fictional evidence where applicable. A quiet mailbox
is not operational proof. Do not claim outage coverage without full pagination and
an explicit bounded source window. If identity/coverage cannot be established,
stop automatic processing and continue the existing manual log.


## Bounded manual recovery qualification

The qualified pattern enumerates an explicit half-open UTC window `[start,end)`
for the selected sender through the existing Standard Outlook GET connector.
Use a small page size to test actual continuation; follow only native next links
that retain HTTPS, the approved host/path and both original time boundaries.
Stop at the reviewed page/time cap. A remaining next link, missing selected identity,
request failure or route change means incomplete coverage; do not mark it caught up.
Deduplicate enumerated source identities and preserve the exact window privately.

Selected replay must use the existing source-key lookup and uncertain-create guard.
Qualification used existing messages read-only and isolated register/receipt lists;
synthetic subjects/conversations avoided copying correspondence content. Native
reads, persisted field mappings, one-root replay, source read metadata and original
flow restoration were verified. A mailbox-level recovery query is distinct from
Inbox arrival-trigger qualification; it does not authorise automatic import of all
messages found in that window. Human selection and production recovery remain
explicit operations. No historical production import was performed.

For a real outage, first enumerate and reconcile the selected window against
register keys and any manual entries. Preserve records and receipts. Use the
manual review path when keys or coverage are ambiguous. No automatic recovery
schedule or repeated create is introduced by this procedure.


## Selected linked Planner action

Use the owned **Create linked action** manual flow for a specific reviewed record.
Enter its integer ItemId and a short action title. It creates one initial action
in the selected private Basic plan, with a link back to the register, and saves
the task URL on that record. The Planner actions view exposes the reciprocal link.
A blank task link means no action has been requested. Native IDs, URLs and the
current On/Off state belong in private Conductor.

The operation refuses unreviewed records. It does not assign a person, set dates,
add comments, send email or change correspondence Progress. Completing a task
does not close correspondence. Human edits to task notes are preserved. The
correspondence key in the initial title and source attachment support recovery;
retain them until the reciprocal record link is verified.

Before creation, an ETag-protected claim records the deterministic action key and
Creating state. Replay reuses an existing task ID or exactly one matching task.
An uncertain create never blindly creates again. A task-created/link-save-failed
case reconciles the existing task, preserves its ID and retries only the missing
link stage using fresh record state. Ambiguous matches, a partial plan scan, changed
source or conflicting link fail visibly. Preserve the key, task and run evidence;
do not clear Creating/Uncertain or delete a task merely to force another create.
The initial increment supports one task per record, not arbitrary task replication.

### Notification boundaries

The generated graph has no email, assignment, due reminder, comment or chat action.
Fictional runtime checks used unassigned tasks without dates/comments; no test send
was performed. Per-flow repair alerts were independently verified Off. Provider
weekly failure digests are separate account-wide service behaviour; the per-flow
switch does not prove their suppression. No account-wide preference was changed.
Later human assignment, dates or comments may trigger native Planner notifications.
Do not introduce those automatically without evaluating the selected send scope.
Monitor run history and the technical exception view, including failures before a
receipt exists. Absence of email is not the health signal.

### Production cutover and operational evidence

Commission capture prospectively by preserving the qualified graph and bindings,
selecting a future UTC start, enabling CaptureEnabled, then independently reading
back On and the exact boundary. Keep the manual linked-action flow On with real
register bindings, without invoking it against real records during setup. Probes
and fictional harnesses remain Stopped. Do not import historical messages.

A quiet mailbox leaves first natural-arrival evidence pending while capture is
On and ready. It is not an activation hold or proof of end-to-end operation. On the
first eligible source, verify the actual trigger payload, source key/native link,
one persisted NeedsReview root and receipt. For unexpected failure or uncertain
identity, stop capture, retain records and receipts and use the manual fallback.
