# On-call notifications: disabled pilot

## Selected first slice

Use an owner-invoked Power Automate Button flow for one existing fictional
Handover item at its pinned revision. There is no recurrence, source-change
subscription, automatic roster summary or clinical escalation. This narrows the
first test independently of unassigned/unpublished Shifts cover and the deferred
contact-directory work. The wider roster notification backlog remains separate.

The proposed recipient is the existing authenticated owner's mailbox only,
through that owner's existing Outlook connection. No CC, BCC, attachment, channel
broadcast, new person or shared-mailbox sender is selected. The exact address,
source bindings and rendered message proposal are private. One specific user
authorisation was consumed by the fictional test below; these bindings provide
no continuing sending authority.

Message content is deliberately limited to a fictional-test heading, Handover
item ID, source revision, status, handover time and supported follow-up due time
(labelled UTC), a direct source link, and a delivery correlation key. Exclude
names, coordination notes, patient details, claim content and contact numbers.
An unset deadline remains unset; displaying an absent follow-up as not recorded
does not create a due date.

## Saved controls

The native flow is saved **Stopped**, with `DeliveryEnabled=false` and an empty
`SendingAuthorisationRef`. Both controls must be deliberately changed under
specific human authority before a send is possible. The Button takes no recipient
or content input: its source item/revision and owner-only audience are pinned.
The saved complete definition matches the candidate; its two bindings reuse the
existing connected SharePoint and Outlook connections. After the single
authorised test, the complete baseline definition and bindings were restored;
the flow is again stopped, delivery-disabled and without an authority reference.

The delivery implementation uses the Standard [SharePoint connector](https://learn.microsoft.com/en-us/connectors/sharepointonline/)
and [Office 365 Outlook connector](https://learn.microsoft.com/en-us/connectors/office365/),
with built-in conditions/composition. Connector classification, connection status,
preflight and native save are distinct from executed runtime qualification.
No premium connector, new consent, connection, licence or service identity was
introduced. No publishing, activation or delivery is implied by the saved flow.

Native readback also reports the platform failure-alert subscription enabled.
It has not been changed or tested. A future failed run can cause service-generated
owner notices in addition to the proposed message; Power Automate also documents
a weekly failure digest. These are not the bespoke notification action and cannot
be represented as a guaranteed one-email outcome. Include that distinction in
the activation decision; see [Microsoft failure-notification guidance](https://learn.microsoft.com/en-us/power-automate/understand-flow-failure-notifications).

## Deduplication and recovery

The existing authoritative List remains the source. A restricted, versioned
SharePoint **notification outbox** records delivery intent and recovery state;
it is neither another Handover register nor a recipient directory. Its Title
column is indexed and enforces unique delivery keys on the server.

Use a deterministic key comprising notification kind, source identity, source
revision and recipient-scope revision. Store the complete minimal payload
snapshot with that key. Do not substitute random keys on retry. The first
reservation is Held by default; duplicate reservations never enter sending.
A different payload under the same key is a conflict for manual review.

Before dispatch, re-read the source revision and the reserved payload. Claim the
outbox entry with its exact ETag and a stable attempt token. A competing or stale
claim must fail. Write **Uncertain before sending**, so interruption immediately
before or after the send cannot cause an automatic resend. The sending action
has retry policy **none**; subsequent failures leave the entry held for review.

On acknowledged connector success, conditionally record Sent only if the same
attempt and payload remain current. Here Sent means connector acceptance, not
recipient delivery or acknowledgement. Outlook's Send an email (V2) action
[does not return a message ID](https://learn.microsoft.com/en-us/connectors/office365/#known-issues-and-limitations-with-actions).
Keep the correlation key in the message and reconcile an uncertain result against
actual matching evidence before any separately authorised resend. Absence of
receipt evidence is not proof that sending failed. Do not promise exactly-once
email delivery: the outbox and mail service are not one transaction.

If a create/update acknowledgement is unavailable, read the existing key, full
payload, attempt, ETag and native history before another write. Preserve the
original error and human corrections. A source change requires a new reviewed
revision-specific intent; it does not silently update or resend an older message.
A pre-send source check cannot prevent edits after the check, so the message
explicitly identifies its source revision rather than claiming perpetual currency.

## Qualification and next operation

Native CLI checks verified the unique indexed key, Held default, inherited site
access and versioning. One fictional reservation was saved. Both an identical
reservation and a changed-payload reservation were rejected with the actual
`SPDuplicateValuesFoundException` (HTTP 500). A stale competing claim received
HTTP 412. Independent reads retained the original attempt and payload; the
fictional entry finished in Review with its four native versions preserved.

Initial field-name errors were retained. Native readback confirmed no rows from
those failed requests before the corrected reservation. A storage disconnect
interrupted local preparation: recovery reconciled preserved receipts with fresh
native state and did not replay the reservation or recreate the List.

These primitive checks remain distinct from flow execution. The user subsequently
authorised exactly one fictional message and temporary activation, including the
platform-notice caveat. The approved preview hashes, pinned source revision and
absence of an existing delivery key were checked first. Only the two delivery
parameter defaults were changed; their saved values were independently verified.
The preview tool's no-changes summary omits parameter-default changes, so it was
not treated as configuration proof.

One authenticated Button invocation succeeded. Native action inputs exactly
matched the approved recipient, subject and HTML body with no CC/BCC/attachments;
the send action returned HTTP 200. The one matching intent progressed through
Held, Uncertain and Sent in three native versions. The original Review fixture
remained unchanged. Run history contains one run; no replay was attempted.
The flow was stopped and its complete baseline definition/bindings restored,
including the false delivery default and cleared authority reference.

Exact-subject Sent Items and Inbox reads through the existing qualified CLI
connection returned HTTP 403. Mailbox probing stopped; there was no new consent,
client switch or resend. Connector acceptance and the outbox's Sent state do not
prove mailbox receipt. Native mailbox receipt remains unverified; any human
confirmation must be recorded as human observation rather than an API readback.

Actual failure/uncertain-send orchestration branches were not induced by this
single authorised happy-path run. Prior native uniqueness/CAS/recovery tests
remain valid at their recorded scope. Raw errors, action payloads, flow snapshots,
outbox history and authority evidence remain private. No real operational data,
people, broader alerts, document/app publication or continuing activation followed.

The next operation is receipt confirmation through permitted access or human
observation only. The one-run authority is consumed: any further activation or
send requires new explicit scope. Do not retry to obtain a receipt. Operational
recurrence, broader recipients, source adoption and roster alerts remain separate.
The contact-directory task stays deferred at the user's request, with no outreach.
