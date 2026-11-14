"""Adapters for complete, fictional departmental export files."""
import csv
import json


def packet(kind, path, feed):
    if kind == "excel":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = csv.DictReader(stream, strict=True)
            required = {"RowKey", "InitiativeId", "Title", "Revision"}
            if not required.issubset(rows.fieldnames or []):
                raise ValueError("Missing initiative table columns")
            return {"initiatives": [
                {"initiative_id": r["InitiativeId"], "source_key": f"{feed}:{r['RowKey']}",
                 "title": r["Title"], "revision": int(r["Revision"])}
                for r in validate_rows(rows, "RowKey")]}

    export = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(export, dict) or not isinstance(export.get("value"), list) or "@odata.nextLink" in export:
        raise ValueError("Supply a complete JSON value array")
    rows = validate_rows(export["value"], "id")
    if kind == "planner":
        return {"tasks": [
            {"task_id": f"{feed}:{r['id']}", "source_key": f"{feed}:{r['id']}",
             "initiative_id": r["InitiativeId"], "title": r["title"], "revision": r["Revision"]}
            for r in rows]}
    events = []
    for row in rows:
        fields = row["fields"]
        fallback = f"{feed}:{row['id']}"
        event = {"event_id": fields.get("EventId", fallback),
                 "source_key": fields.get("SourceKey", fallback),
                 "initiative_id": fields["InitiativeId"], "event_type": fields["EventType"],
                 "effective_at": fields["EffectiveAt"]}
        for column, member in EVENT_COLUMNS.items():
            if column in fields and member not in event:
                event[member] = fields[column]
        events.append(event)
    return {"events": events}


EVENT_COLUMNS = {
    "InitiativeId": "initiative_id", "EventType": "event_type", "EffectiveAt": "effective_at",
    "ObservedAt": "observed_at", "SourceKey": "source_key", "SourceRecordId": "source_record_id",
    "SourceRevision": "source_revision", "ActorRef": "actor_ref", "SourceSystem": "source_system",
    "Outcome": "outcome", "EvidenceRef": "evidence_ref",
}


def validate_rows(rows, key):
    seen = set()
    for row in rows:
        value = row.get(key) if isinstance(row, dict) else None
        if not isinstance(value, str) or not value.strip() or value in seen:
            raise ValueError("Missing or duplicate source row key")
        seen.add(value)
        yield row
