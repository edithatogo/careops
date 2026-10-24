# On-call handover and fallback

## Selected route

Use the existing restricted Handover List for coordination and On-call references
as an index to maintained sources. Keep patient narratives, incident records and
actual work in their existing authoritative systems. The reference index is not
itself a verified contact directory. Shifts identifies scheduled cover only after
its assignments and publication are separately authorised; an unassigned draft
cannot identify the person to contact.

This is a development procedure, not an issued hospital operating procedure.
The authoritative contact reference and an operational downtime location still
need to be identified and verified. Do not treat a development snapshot as live
cover, a delegation, or a service-wide fallback.

## Manual handover

1. Check the authorised published cover for the exact interval, including partial
   cover. Verify the contact route against the maintained directory/reference,
   including its source, revision, review date and validity. If either is missing
   or stale, use an already established local escalation procedure; this document
   does not supply a new emergency number or escalation route.
2. Create one Handover item with the handover time, a concise coordination note,
   links to authoritative records and any follow-up due time. Do not duplicate
   patient details. Leave a disputed or unsupported deadline unset.
3. Outgoing and incoming operators review unresolved work and current cover.
   Record acknowledgement, its time, unresolved matters and the next action in
   the coordination note before changing Status to **Handed over**. This manual
   acknowledgement is not a platform approval or proof of legal delegation.
4. Correct the current item rather than creating another authoritative register.
   Read the latest item/version first and preserve other human edits. Close only
   resolved items; keep unresolved work visible for the next handover.

## Save and recovery

Record the item identity, expected version and intended changed fields. For CLI
updates use the exact current ETag, never a wildcard. A stale-version refusal
requires a fresh read and comparison, not blind replay. If the response is lost,
look up the existing item/recovery marker and compare all intended saved fields
before deciding whether to retry. Do not create another item solely because an
acknowledgement was unavailable.

For a correction, inspect native version history and recover only the intended
field using a conditional update against the current version. Keep later human
notes and the original history. This route creates a new revision; it does not
rewind or delete the item. A historical version listing alone is not recovery
proof: read its field values and verify the resulting current item.

## Fallback

Keep the online List authoritative. A fallback is a read-only, timestamped
snapshot, not another editable roster or handover register. Include source links,
item identities and versions, capture time/timezone, cover interval, contact
reference revision and an explicit valid-through time. Missing contact/coverage
validation or expiry makes it unsuitable for operational use. Do not infer
validity from the download time.

For development, keep the snapshot in the existing ignored private workspace,
with owner-only file permissions and a checksum manifest. Keep prior captures;
write a new file for each revision. Verify it can be read from disk without
contacting Microsoft 365. Recover a damaged *copy* into a separate file and compare
its checksum and contents with the preserved original. This verifies local-file
handling only, not hospital network-drive availability, another user's access,
encryption, mobile/offline Teams use, or disaster resilience.

For actual downtime use, select an existing approved location accessible to the
intended operators without the same cloud dependency. Verify those operators'
read access, expiry handling and replacement/recovery there before relying on it.
No new access, recipients, automatic export, email or workflow follows from this
procedure. After service recovery, reconcile offline notes against the latest
native versions and preserve conflicts for manual resolution.

## Recorded qualification and remaining operations

The private native receipt records successful current-operator reads of both
Lists, inherited List access and enabled versioning. A fictional Handover item
passed create/read, manual correction, HTTP 412 stale-write rejection, selective
recovery from historical field values while preserving later notes, and final
readback/history verification. The fictional item remains clearly marked and
closed. These are native SharePoint results, not local substitutes.

Rules and alerts were empty at preflight. An existing system-managed SharePoint
UI push subscription and its matching receivers were retained; no claim of zero
platform events is made. No workflow was created or activated, no person added,
no roster published and no email sent.

The development snapshot passed local content/checksum and damaged-copy recovery
checks. Remaining operational requirements are the actual maintained contact
source, a valid published cover interval, and the intended downtime location and
operator access. Other-member, device and Teams-embedded checks were not performed.
Detailed identities, URLs, snapshots and receipts remain private.
