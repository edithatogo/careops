# Minimum correspondence contract and capture candidate

Prepared 26 October 2026. This generic contract describes source implementation
and qualification requirements; actual native state and identities remain in private
Conductor. Intake activation is a separate selection. Use standard
Office 365 Outlook and SharePoint connectors. No Premium connectors, Copilot,
AI Builder, email actions or investigation of another person's access/workflow.

## Scope and record ownership

Capture messages from one configured sending office delivered into the requesting
user's selected work-mailbox folder, from an explicitly selected prospective
start time. The private profile supplies real bindings. Sender matching is a
routing rule, not proof of authenticity or substantive approval. Folder rules,
message moves and connector delivery gaps need native qualification before use.

The existing correspondence List remains the matter register. A technical receipts
List holds processing events and unmatched messages, not another business register.
This small addition supplies duplicate/recovery evidence and an exception queue
without overwriting human work. Both use existing standard SharePoint storage;
the receipts may use a separate existing authorised site when list-creation rights
differ from schema rights on the existing register. Do not broaden sharing.

| Information | Proposed binding / rule |
|---|---|
| Exact message identity | Trimmed Internet Message-ID, case preserved, 1–255 characters, single selected mailbox |
| Mailbox-local identity | SourceMessageId; preserve as provenance, not a cross-mailbox duplicate key |
| Matter identity | Existing List ID; each root correspondence record retains its ID/history |
| New receipt | Unique message key already registered → link existing record, never create another |
| Possible reply/matter match | Existing conversation or exact subject match → NeedsReview receipt; do not merge, close or overwrite existing matters |
| New root candidate | No exact key or possible match → create source facts only, CaptureState=NeedsReview |
| Missing/long identity or subject | NeedsReview receipt, no register create; no invented key/date/title |
| Malformed timestamp / failed dependency | Failed native run visible in run history; no blind replay or fabricated success |
| Human authority | Classification, business priority/deadline, responsibility, actions and correspondence closure remain human decisions |

Exact subject/conversation matches are conservative review signals. They are not
proof of the same matter. Changed-subject manual entries without a stored source
key cannot be reliably deduplicated automatically. Prospective manual registration
must preserve the source key or use the review path; legacy reconciliation remains
explicit, with no backfill or unsupported claim of complete historical deduplication.

## Minimum additive schema

Reuse existing Title, DateRecd, Recdby, ConversationID, LatestEmailDate and SavedEmail
for subject, received UTC, sender, conversation, latest source time and source web
link. Do not populate Progress/Completed, ToComplete, DueDate, Category, Actions,
Comments or filing fields by inference. In particular, capture is not completion.

Add only these register columns after exact schema qualification:

- SourceMessageKey: single-line text, maximum255, indexed and unique; optional for
  preserved legacy rows. Verify SharePoint permits existing blanks with uniqueness
  and test native case-sensitivity/collision behaviour before selecting it.
- SourceMessageId: multiline plain text; mailbox-local ID.
- CaptureState: choice NeedsReview/Reviewed, distinct from business progress.

Proposed technical receipts fields: Title (native run identity, unique/indexed
after qualification), MessageKey (multiline), SourceMessageId (multiline),
ConversationID (multiline), State (Registered/AlreadyRegistered/NeedsReview/Uncertain),
RegisterItemId (optional number), ErrorCode (text), ReceivedUtc (date/time).
Do not copy message bodies or attachments. The arrival trigger's outputs are
secured and includeAttachments=false; connector service processing still occurs.

Source URL is read through the proven Outlook HttpRequest GET operation, selecting
only id/internetMessageId/webLink. The exact dynamic response shape, source identity
and link usability need native validation; a saved mailbox-local ID alone is not
a verified source link. If the source cannot be verified, hold for review rather
than treating the candidate as ready for capture.

## Candidate behaviour and recovery

[The local compiler](../scripts/correspondence_capture.py) emits a flow candidate
with state Stopped, CaptureEnabled=false and CaptureStartUtc=2100-01-01. It uses
the documented OnNewEmailV3 sender filter and serial trigger processing, standard
Outlook GET for source metadata, and standard SharePoint HttpRequest operations.
There are no PATCH/delete operations or changes to existing correspondence rows.
The exact trigger's polling/notification shape remains subject to native validation;
schema validation alone does not establish arrival behaviour or licence/policy fit.

Source-key lookup precedes creation. The unique register key is the server-side
collision guard for concurrent/manual duplicates; serial flow execution alone is
insufficient. SharePoint may reject case-only key variants: compare the returned
case-preserved identity explicitly, and send collisions to review. After a
failed/timed-out create, query the same key and verify both exact key and mailbox-local
source ID before recording reconciliation; otherwise record Uncertain, with no second POST.
Connector retries are disabled. A receipt save failure makes the run visibly fail;
inspect existing state before recovery. Processing events may legitimately record
several delivery attempts against one correspondence record.

Last successful receipt and native run history provide initial capture-health
visibility. Failures before any receipt are visible in native run history, not a
fabricated healthy receipt. Bounded source-window reconciliation/outage catch-up
and recovery from missed triggers still require native qualification; the candidate
does not claim complete capture coverage. Define the operator's review interval
and retained evidence before reliance. No scheduled summary or email alert is added.

## Qualification evidence and remaining prerequisites

- Eight focused offline tests cover source boundaries, exact replay, ambiguous
  matching, held activation, connector restrictions, safe queries, uncertain create
  recovery and action dependencies. These are local checks, not native execution.
- Connector operation-detail checks identified OnNewEmailV3 and SharePoint
  HttpRequest parameters. The offline flow validator accepted the generated
  fictional definition. The proven mailbox probe remains independent and Stopped.
- Private deployment inputs bind the exact receipt List, receipt site and existing
  SharePoint connection after qualification. No placeholder may be deployed. Before native save,
  verify schemas/uniqueness, embedded connections, source-link shape, failure cases
  and the prospective journal event. Keep native state Stopped and capture false.
- Later activation requires its separately selected boundary and saved native
  readback. Linked Planner actions remain COR-12, the next committed increment.

From the module root, run focused checks using the verified repo-local Python:

```sh
.venv-ci/bin/python --version
.venv-ci/bin/python -m unittest discover -s tests -p test_correspondence_capture.py -v
```

The compiler can write a new local candidate with private or fictional bindings;
it contains no deployment, authentication, network or activation operation.


## Bounded native fictional qualification

Use a retained baseline and prospective native change journal. Temporarily replace
only the selected owned flow's trigger with a manual Button, replace source reads
with fictional metadata and bind isolated test register/receipt lists. Review all
connector targets and operations before enabling this manual harness. Match field
types to the real contract; omit unused connector references explicitly. Do not
start an arrival trigger, send email or write test rows into the business log.

Verify persisted records and receipts alongside complete paginated native action
history. Cover new capture, replay, case-only collision, possible matter matches,
missing identity, sender exclusion, source mismatch, loss of a create response,
failure before create and receipt failure followed by replay. A deliberate action
failure is expected evidence; a Succeeded batch alone is insufficient. Distinguish
injected failures from a real transport failure and fictional source links from
actual Outlook metadata/link usability. Test harness receipt titles may include
case identity; production receipts retain native run identity. Optional SharePoint
Text fields can persist empty strings as null; compare that exact semantic field
appropriately without normalising substantive values or dropping native evidence.

In finally, stop the harness before restoring the original arrival definition and
connections. Independently verify Stopped, false CaptureEnabled and future boundary,
plus preserved live records/receipts. Retain failed saves, comparison failures and
uncertain write reconciliation. Do not rerun a native mutation solely to fix a local
checker. Manual fictional qualification does not establish arrival coverage,
concurrent writes, outage catch-up, production failure termination or activation.
Actual run receipts and qualification status stay in private Conductor.


## Actual source-metadata and link qualification

A bounded, separately authorised manual probe may use existing email metadata
through the qualified Standard Outlook HttpRequest GET route. Limit the exact
sender, selected fields and sample count; never fetch bodies/attachments, follow
pagination, poll an arrival trigger or mutate mailbox/SharePoint records for this
check. Preserve protected raw connector outputs. Power Automate can propagate
protection into downstream summaries; test explicit constant pass/fail branches
and complete per-iteration native statuses rather than unsealing protected data.

Check exact mailbox ID/Internet Message-ID correspondence, key length, repeat-read
consistency, read flag and change key. Validate authoritative native webLink scheme
and host, and use a read-only target resolution only when its ID format is qualified.
A webLink identifier need not be text-identical to a Graph API ID. Preserve the
native URL; do not reconstruct it or invent a conversion. A failed link-derived
API lookup with successful original ID lookup is an unresolved representation gap,
not proof the browser URL is broken. Treat that sample as unqualified in evidence.
Opening Outlook can change read state, so keep interactive usability separate.

Use one reviewed manifest and fresh evidence names per batch. Restore the original
flow Stopped/disabled/future boundary in finally, even after a local evidence-read
error. Reconcile from actual saved actions/repetitions and terminal state without
reinvoking a probe solely because a local read filename was consumed. Public source
contains only this generic procedure; actual source identities and partial verdicts
remain in private Conductor. No activation or email follows from qualification.


For a link/API-ID mismatch, diagnose scheme/host, exact query-key shape, percent
encoding and observed equality through native boolean branches before attempting
conversion. Do not assume ordinary Base64 URL substitutions establish an Exchange
ID type. The documented [Standard Outlook HttpRequest routes](https://learn.microsoft.com/en-us/connectors/office365/#send-an-http-request)
do not include Graph translateExchangeIds; this does not authorise a Premium
connector or undocumented route. Preserve the authoritative native webLink and
record partial usability separately. Continue independent review/exception views
and manual fallback while keeping unresolved link validation in acceptance.


## Linked Planner increment: staged source contract

Explicitly select a correspondence record and an actionable outcome; do not create
a task for every captured email. Keep the register as correspondence authority and
Planner as task execution authority. Retain correspondence item identity, task ID,
plan ID and reciprocal links; reconcile an uncertain create by identity before retry.
Use a minimal title and source link, with due date/status only when explicitly set.
Do not copy message bodies/attachments or infer owners. Assignment, notifications,
completion synchronisation and edit-conflict behaviour require qualification before
activation. Do not auto-close correspondence when a task completes. Standard
connectors only. Pending an authorised route, retain existing Actions/manual links.
