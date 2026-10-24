"""Pure, content-free comparison of fictional meeting calendar snapshots.

This is a local design harness, not a calendar client and not authority to
read or change a real event. See the F12 feature record and Conductor plan.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


_FIELDS = (
    ("event_id", "EVENT_ID_DRIFT", "The event identifier changed.", "Manually verify the existing invitation."),
    ("occurrence_id", "OCCURRENCE_DRIFT", "The occurrence identifier changed.", "Manually reconcile this occurrence against the invitation."),
    ("original_occurrence_id", "ORIGINAL_OCCURRENCE_DRIFT", "The original occurrence binding changed.", "Manually verify occurrence lineage; do not create a replacement."),
    ("series_id", "SERIES_DRIFT", "The recurrence series changed.", "Review the existing series and occurrence manually."),
    ("series_rule", "SERIES_RULE_DRIFT", "The recurrence rule changed.", "Review the series rule and affected occurrences manually."),
    ("organiser_id", "ORGANISER_DRIFT", "The organiser binding changed.", "Verify the organiser using the existing invitation."),
    ("audience_revision", "AUDIENCE_DRIFT", "The audience revision changed.", "Verify the intended audience through the approved route."),
)

_MESSAGES = {
    "NO_CHANGE": ("The selected calendar and pack metadata match the specified baseline; document contents and readiness are not verified.", "Retain the current invitation and pack and complete the existing manual review."),
    "READ_UNVERIFIED": ("The calendar read is incomplete or inaccessible.", "Check access and scope manually; absence is not established."),
    "ABSENT": ("The bound occurrence is absent from a complete scoped snapshot.", "Reconcile the existing invitation manually; do not book a replacement."),
    "PROPOSAL_ONLY": ("The item is still a proposal, not a confirmed occurrence.", "Use the existing invitation route to confirm status."),
    "NOT_CONFIRMED": ("The occurrence is not confirmed.", "Verify status in the existing invitation."),
    "CANCELLED_OCCURRENCE": ("The bound occurrence is cancelled.", "Review the cancellation manually; do not create a replacement."),
    "CANCELLED_SERIES": ("The recurrence series is cancelled.", "Review the existing series cancellation manually."),
    "AMBIGUOUS_IDENTITY": ("The event identity cannot be safely matched.", "Manually reconcile event and occurrence lineage; do not create a replacement."),
    "TIME_UNVERIFIED": ("The time or timezone cannot be verified safely.", "Check the source invitation's local time and timezone manually."),
    "RESCHEDULED": ("The bound occurrence time changed.", "Review the existing invitation; no event update is proposed."),
    "TIMEZONE_DRIFT": ("The timezone or wall-clock representation changed.", "Verify the intended local time and timezone manually."),
    "PACK_UNVERIFIED": ("The linked pack could not be verified.", "Open the existing approved pack route and confirm its revision."),
    "PACK_DRIFT": ("The linked pack does not match the expected accepted revision.", "Manually verify the approved pack ID, revision and hash."),
    "EVENT_ID_DRIFT": ("The event identifier changed.", "Manually verify the existing invitation."),
    "OCCURRENCE_DRIFT": ("The occurrence identifier changed.", "Manually reconcile this occurrence against the invitation."),
    "ORIGINAL_OCCURRENCE_DRIFT": ("The original occurrence binding changed.", "Manually verify occurrence lineage; do not create a replacement."),
    "SERIES_DRIFT": ("The recurrence series or rule changed.", "Review the existing series and occurrence manually."),
    "ORGANISER_DRIFT": ("The organiser binding changed.", "Verify the organiser using the existing invitation."),
    "AUDIENCE_DRIFT": ("The audience revision changed.", "Verify the intended audience through the approved route."),
    "BASELINE_UNCONFIRMED": ("The earlier snapshot was not a confirmed occurrence, so a change cannot be established safely.", "Verify the occurrence history using the existing invitation."),
    "CANCELLATION_SCOPE_UNVERIFIED": ("The cancellation does not identify whether it affects one occurrence or the whole series.", "Check the cancellation scope manually; do not create a replacement."),
    "SNAPSHOT_SHAPE_INVALID": ("The snapshot structure is incomplete or invalid.", "Recheck the source snapshot and compare manually."),
    "DURATION_DRIFT": ("The meeting end time or duration changed.", "Review the existing invitation and service-cover implications manually."),
}


def _issue(code: str, detail: str | None = None) -> dict:
    explanation, next_step = _MESSAGES[code]
    return {"code": code, "explanation": explanation, "manual_next_step": next_step, **({"detail": detail} if detail else {})}


def _complete(snapshot: dict, expected: dict) -> bool:
    return (
        snapshot.get("read_outcome") == "complete"
        and snapshot.get("complete") is True
        and "event" in snapshot
        and snapshot.get("scope") == {
            "calendar_id": expected.get("calendar_id"),
            "occurrence_id": expected.get("occurrence_id"),
        }
    )


def _valid_expected(expected: dict) -> bool:
    required = (
        "calendar_id", "occurrence_id", "event_id", "original_occurrence_id",
        "series_id", "series_rule", "organiser_id", "audience_revision",
        "pack_id", "pack_revision", "pack_hash", "pack_link_id",
    )
    return isinstance(expected, dict) and all(isinstance(expected.get(k), str) and expected[k].strip() for k in required)


def _valid_event(event: object) -> bool:
    required = (
        "event_id", "occurrence_id", "original_occurrence_id", "series_id",
        "series_rule", "organiser_id", "audience_revision", "status",
    )
    return isinstance(event, dict) and all(isinstance(event.get(k), str) and event[k].strip() for k in required)


def _time(snapshot: dict, field: str) -> tuple[datetime, str, str] | None:
    """Return UTC instant, zone name, and local wall time if fully verifiable."""
    raw = snapshot.get(field)
    zone_name = snapshot.get("time_zone")
    if not isinstance(raw, str) or not isinstance(zone_name, str):
        return None
    try:
        dt = datetime.fromisoformat(raw)
        zone = ZoneInfo(zone_name)
    except (ValueError, ZoneInfoNotFoundError):
        return None
    if dt.tzinfo is None or dt.utcoffset() is None:
        return None
    local = dt.astimezone(zone)
    # Require supplied offset and wall time to agree with the declared IANA zone.
    if local.replace(tzinfo=None) != dt.replace(tzinfo=None) or local.utcoffset() != dt.utcoffset():
        return None
    wall = dt.replace(tzinfo=None)
    # A wall time is valid only if a fold round-trips to the same wall time.
    valid_folds = []
    for fold in (0, 1):
        candidate = wall.replace(tzinfo=zone, fold=fold)
        back = candidate.astimezone(timezone.utc).astimezone(zone)
        if back.replace(tzinfo=None) == wall and back.utcoffset() == candidate.utcoffset():
            valid_folds.append(candidate)
    if not valid_folds or (len({x.utcoffset() for x in valid_folds}) > 1 and dt.fold not in (0, 1)):
        return None
    return dt.astimezone(timezone.utc), zone_name, wall.isoformat()


def compare_snapshots(expected: dict, before: dict, current: dict) -> dict:
    """Compare two content-free synthetic snapshots; never proposes a write."""
    issues: list[dict] = []
    if not _valid_expected(expected):
        return {"state": "blocked", "issues": [_issue("READ_UNVERIFIED")], "write_proposed": False}
    for snap in (before, current):
        if not isinstance(snap, dict) or not _complete(snap, expected):
            issues.append(_issue("READ_UNVERIFIED"))
            return {"state": "blocked", "issues": issues, "write_proposed": False}

    old = before.get("event")
    new = current.get("event")
    if old is None and new is None:
        issues.append(_issue("ABSENT"))
        return {"state": "blocked", "issues": issues, "write_proposed": False}
    if old is None or new is None:
        if new is None:
            issues.append(_issue("ABSENT"))
            return {"state": "blocked", "issues": issues, "write_proposed": False}
        issues.append(_issue("AMBIGUOUS_IDENTITY"))
        return {"state": "blocked", "issues": issues, "write_proposed": False}

    if not _valid_event(old) or not _valid_event(new):
        return {"state": "blocked", "issues": [_issue("SNAPSHOT_SHAPE_INVALID")], "write_proposed": False}

    # Validate event identity before status so an unrelated cancellation cannot
    # be attributed to the bound occurrence.
    for event in (old, new):
        for field in ("event_id", "occurrence_id", "original_occurrence_id", "series_id", "organiser_id", "audience_revision"):
            if event.get(field) != expected.get(field):
                code = {
                    "organiser_id": "ORGANISER_DRIFT",
                    "audience_revision": "AUDIENCE_DRIFT",
                    "series_id": "SERIES_DRIFT",
                    "occurrence_id": "OCCURRENCE_DRIFT",
                    "original_occurrence_id": "ORIGINAL_OCCURRENCE_DRIFT",
                }.get(field, "AMBIGUOUS_IDENTITY")
                return {"state": "blocked", "issues": [_issue(code)], "write_proposed": False}

    if new.get("status") == "cancelled":
        scope = new.get("cancelled_scope")
        if scope != "occurrence" and scope != "series":
            return {"state": "blocked", "issues": [_issue("CANCELLATION_SCOPE_UNVERIFIED")], "write_proposed": False}
        code = "CANCELLED_SERIES" if scope == "series" else "CANCELLED_OCCURRENCE"
        issues.append(_issue(code))
        return {"state": "blocked", "issues": issues, "write_proposed": False}
    if new.get("status") == "proposal":
        return {"state": "blocked", "issues": [_issue("PROPOSAL_ONLY")], "write_proposed": False}
    if new.get("status") != "confirmed":
        issues.append(_issue("NOT_CONFIRMED"))
        return {"state": "blocked", "issues": issues, "write_proposed": False}
    if old.get("status") == "proposal" or old.get("status") == "tentative":
        return {"state": "blocked", "issues": [_issue("BASELINE_UNCONFIRMED")], "write_proposed": False}
    if old.get("status") != "confirmed":
        return {"state": "blocked", "issues": [_issue("NOT_CONFIRMED")], "write_proposed": False}

    for field, code, explanation, next_step in _FIELDS:
        if old.get(field) != new.get(field):
            issues.append({"code": code, "explanation": explanation, "manual_next_step": next_step})
    if old.get("series_rule") != expected.get("series_rule") or new.get("series_rule") != expected.get("series_rule"):
        issues.append(_issue("SERIES_DRIFT"))

    old_time, new_time = _time(old, "start"), _time(new, "start")
    old_end, new_end = _time(old, "end"), _time(new, "end")
    if old_time is None or new_time is None or old_end is None or new_end is None:
        issues.append(_issue("TIME_UNVERIFIED"))
    else:
        if old_time[1] != new_time[1]:
            issues.append(_issue("TIMEZONE_DRIFT"))
        if old_end[1] != new_end[1] and old_time[1] == new_time[1]:
            issues.append(_issue("TIMEZONE_DRIFT"))
        if old_time[0] != new_time[0]:
            issues.append(_issue("RESCHEDULED"))
        if old_end[0] <= old_time[0] or new_end[0] <= new_time[0]:
            issues.append(_issue("TIME_UNVERIFIED"))
        elif (old_end[0] - old_time[0]) != (new_end[0] - new_time[0]):
            issues.append(_issue("DURATION_DRIFT"))

    for event in (old, new):
        pack = event.get("pack")
        if not isinstance(pack, dict) or pack.get("read_outcome") != "complete":
            issues.append(_issue("PACK_UNVERIFIED"))
            break
        if any(pack.get(k) != expected.get(k) for k in ("pack_link_id", "pack_id", "pack_revision", "pack_hash")) or pack.get("approved") is not True:
            issues.append(_issue("PACK_DRIFT"))
            break

    if not issues:
        issues.append(_issue("NO_CHANGE"))
        return {"state": "no_change", "issues": issues, "write_proposed": False}
    return {"state": "discrepancy", "issues": issues, "write_proposed": False}
