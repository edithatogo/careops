# Improvement register data contract

This module records initiative identity, routing metadata and evidence links. It
does not become the authoritative source for policy, delegated decisions,
clinical/research approval, delivery task state or finance. Keep opaque stable
identifiers and source revisions so records can be reconciled after a rename,
late arrival, correction or source outage.

## Keys and authority

| Entity | Grain and key | Authoritative owner | Register responsibility |
| --- | --- | --- | --- |
| Initiative | One improvement initiative; immutable `InitiativeId` | This register for identity and current descriptive metadata | Lead and participating service references, benefit statement, status, route and evidence links |
| Governance decision | One decision or referral outcome; source `DecisionRef` | Delegated decision owner / Decisions register | Link to initiative, route and decision reference; never infer approval from referral or status |
| Policy source | One exact policy edition; source key plus edition/revision | PPG source catalogue | Reference the policy edition considered; no copied policy narrative as authority |
| Delivery task | One task in its owning work system; source task ID | Planner or originating system | Link through initiative ID and source key; do not mirror task completion as initiative closure |
| Research output | One RIMS record; stable RIMS identifier and source revision | Research Information Management System (RIMS) | Link output references; publication status and bibliographic facts remain in RIMS |
| Event | One observed transition or outcome; `EventId` unique within source | Originating system for its event; reviewed measure owner for derived observation | Preserve source record ID, revision, event time, observation time and provenance |
| Cost observation | One amount for a defined period, cost category and initiative/source | Finance system or approved cost owner | Store or report reference, amount, currency, period, allocation basis and evidence; never calculate authoritative finance postings |

`InitiativeId` is assigned once and never reused. Display names may change.
Inbound adapters must use a source-qualified key (`source-system` plus source
record ID), and retain source revision, extraction time and a content hash when
available. Deduplicate only on a documented source key. A changed source
revision updates the linked snapshot while retaining the prior receipt/history.
When an import fails or is incomplete, retain the last successful import time
and mark the current view stale/unknown; do not translate missing rows into
deletions or zero activity.

## Governance routes

The portable packet route values are `local_qi`, `executive_innovation`, and
`research`. They describe a routing path, not permission to commence. The
SharePoint projection may use friendlier display labels, but must map them
explicitly to these importer values and retain the source route.
Each route has a separately maintained decision owner and decision type mapping
in the approved local governance directory. The route map must identify the
required referral package, delegated reviewer, decision record location,
possible outcomes and any prerequisite approvals. Do not encode a guessed
position title or delegate in portable defaults.

The importer requires `decision_id`, stable `source_key`, `initiative_id`,
`decision_kind`, `route`, explicit `reviewer`, and `outcome`. Supported decision
kinds are `sponsorship`, `commencement`, `data_access`, and `classification`.
Retain `submitted_at` and `decided_at` as ISO 8601 UTC timestamps when known;
leave `decided_at` null while a decision is pending. These timestamps are
preserved in the record payload, while a projection may expose decision status,
decision-owner reference and the upstream decision identifier as separate
fields. Only an explicit source decision from the delegated owner can set an
approval outcome. Registration, triage, a Planner task, an executive sponsor,
publication or research referral does not itself approve work or clinical use.
Research governance, ethics, information security, procurement and
clinical-safety approvals remain independent gates where applicable.

Importer event records use `effective_at` and `observed_at`. Both are ISO 8601
UTC values with an explicit `Z` or offset. The reporting projection can name the
semantic columns `effective_at_utc` and `observed_at_utc`, but performs that
normalization deliberately and does not change the packet field names.

## Example records (fictional)

`examples/packet.json` is the end-to-end fictional import example: three
initiatives, five tasks linked to one initiative, events, all four supported
decision kinds and benefit/adoption snapshots. `examples/initiative.json` is a
richer projection example for a list or reporting view; it is not itself an
import packet. `examples/source-inventory.json` is for the separate resource
bootstrap dry-run utility and is unrelated to importing register records.
