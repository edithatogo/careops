# Stopped flow candidates

`definitions/` contains standalone Power Automate flow payload candidates, a
process event projection contract, and a separate preparation receipt. Both flow
payloads declare `state: Stopped` and keep environment bindings unresolved.
Regenerate them with the repository-local Python 3.15.1 interpreter:

```sh
../../.venv-careops-privacy-hooks/bin/python tools/build_flows.py
```

The definitions are not included in the parent solution PAC ZIP. No qualified
solution workflow component metadata or connection-reference mapping source was
available for this work, so the standalone JSON files must not be described as
part of that package. Native import/save/readback and fictional runtime
qualification remain unperformed.

The event-capture flow periodically reads the bounded initiative list and
appends one immutable event per initiative revision, deduplicated by `SourceKey`.
Daily reconciliation replays the same event logic and reports counts and scan
completeness in run history. It stops on a scan beyond 5,000 items and does not
write a durable health ledger. The two schedules are stopped by default and each
has a false enable parameter.

Offline checks are in `tools/test_flows.py`. The downloaded Microsoft Logic Apps
workflow-definition schema was also checked against the generated definitions.
It does not recognize Power Automate's `OpenApiConnection` action type, used here
for the established SharePoint `HttpRequest` connector operation, so schema
validation reports those connector actions as incompatible. This is a schema
format boundary; it is not evidence of Power Automate native acceptance.

Both polling graphs hold subsequent writes after an item conflict, fail the
run outside the item loop, and reject missing or paginated source results.
A timed-out create is followed by a lookup of the immutable key before any
decision to retry. Replay compares the source effective instant; the original
observation timestamp remains capture provenance.

The local bootstrap exports process-mining.csv. For a departmental database
use the register CLI with `export --kind process-mining --output events.csv`.
Map InitiativeId to case, EventType to activity and EffectiveAt to event time.
ObservedAt is independent. Missing source metadata remains blank. Inspect
`feed-health` alongside the CSV to identify stale inputs.

PAC pack/unpack currently qualifies the scaffold only. Each of the two flows
requires its solution workflow component identity, workflow metadata and
client-data file association. The connector alias shared_sharepointonline
requires the solution connection-reference logical name and its target
SharePoint connection. SiteUrl, InitiativeListId and EventListId require
the selected site URL and the two distinct list IDs. No tenant-specific
bindings belong in this source.
