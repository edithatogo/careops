from copy import deepcopy

from scripts.meeting_calendar_compare import compare_snapshots


EXPECTED = {
    "calendar_id": "calendar-fictional-1",
    "occurrence_id": "occ-2026-10-01",
    "event_id": "event-1",
    "original_occurrence_id": "original-1",
    "series_id": "series-1",
    "series_rule": "FREQ=MONTHLY;BYDAY=1TH",
    "organiser_id": "person-fictional-1",
    "audience_revision": "audience-r3",
    "pack_id": "pack-1",
    "pack_revision": "rev-4",
    "pack_hash": "sha256:fictional-4",
    "pack_link_id": "link-1",
}


def event(**changes):
    value = {
        "event_id": EXPECTED["event_id"],
        "occurrence_id": EXPECTED["occurrence_id"],
        "original_occurrence_id": EXPECTED["original_occurrence_id"],
        "series_id": EXPECTED["series_id"],
        "series_rule": EXPECTED["series_rule"],
        "organiser_id": EXPECTED["organiser_id"],
        "audience_revision": EXPECTED["audience_revision"],
        "status": "confirmed",
        "start": "2026-10-01T09:00:00+10:00",
        "end": "2026-10-01T10:00:00+10:00",
        "time_zone": "Australia/Brisbane",
        "pack": {"read_outcome": "complete", "pack_link_id": "link-1", "pack_id": "pack-1", "pack_revision": "rev-4", "pack_hash": "sha256:fictional-4", "approved": True},
    }
    value.update(changes)
    return value


def snapshot(value, *, complete=True, outcome="complete", scope=None):
    return {
        "read_outcome": outcome,
        "complete": complete,
        "scope": scope or {"calendar_id": EXPECTED["calendar_id"], "occurrence_id": EXPECTED["occurrence_id"]},
        "event": value,
    }


def code(result):
    return [item["code"] for item in result["issues"]]


def compare(old=None, new=None):
    return compare_snapshots(EXPECTED, snapshot(old or event()), snapshot(new or event()))


def test_identical_is_quiet_deterministic_noop_and_does_not_mutate_inputs():
    old, new = snapshot(event()), snapshot(event())
    before = deepcopy((old, new))
    first = compare_snapshots(EXPECTED, old, new)
    second = compare_snapshots(EXPECTED, old, new)
    assert first == second
    assert first["state"] == "no_change"
    assert code(first) == ["NO_CHANGE"]
    assert first["write_proposed"] is False
    assert (old, new) == before


def test_offset_equivalent_instants_are_noop_when_zone_and_wall_time_match():
    old = event(start="2026-10-01T09:00:00+10:00")
    new = event(start="2026-10-01T09:00:00+10:00")
    assert compare(old, new)["state"] == "no_change"


def test_timezone_or_wall_clock_drift_is_reported_even_when_instant_matches():
    old = event()
    new = event(start="2026-10-01T07:00:00+08:00", end="2026-10-01T08:00:00+08:00", time_zone="Australia/Perth")
    assert "TIMEZONE_DRIFT" in code(compare(old, new))


def test_changed_instant_is_reschedule_but_not_write_proposal():
    old = event()
    new = event(start="2026-10-01T10:00:00+10:00")
    result = compare(old, new)
    assert "RESCHEDULED" in code(result)
    assert result["write_proposed"] is False


def test_incomplete_denied_or_wrong_scope_never_proves_absence():
    old, new = snapshot(event()), snapshot(None, complete=False, outcome="partial")
    assert "READ_UNVERIFIED" in code(compare_snapshots(EXPECTED, old, new))
    omitted_event = snapshot(event())
    omitted_event.pop("event")
    assert "READ_UNVERIFIED" in code(compare_snapshots(EXPECTED, old, omitted_event))
    old, new = snapshot(event()), snapshot(None, outcome="inaccessible")
    assert "READ_UNVERIFIED" in code(compare_snapshots(EXPECTED, old, new))
    old, new = snapshot(event()), snapshot(None, scope={"calendar_id": "other", "occurrence_id": EXPECTED["occurrence_id"]})
    assert "READ_UNVERIFIED" in code(compare_snapshots(EXPECTED, old, new))


def test_absence_only_follows_complete_scoped_read_and_never_suggests_rebooking():
    result = compare_snapshots(EXPECTED, snapshot(event()), snapshot(None))
    assert code(result) == ["ABSENT"]
    assert "do not book a replacement" in result["issues"][0]["manual_next_step"]
    assert result["write_proposed"] is False


def test_proposal_tentative_and_cancellation_are_distinct_and_no_replacement():
    assert "PROPOSAL_ONLY" in code(compare(event(status="proposal"), event(status="proposal")))
    assert "NOT_CONFIRMED" in code(compare(event(status="tentative"), event(status="tentative")))
    cancelled = event(status="cancelled", cancelled_scope="occurrence")
    result = compare(event(), cancelled)
    assert "CANCELLED_OCCURRENCE" in code(result)
    assert "do not create a replacement" in result["issues"][0]["manual_next_step"]
    series = event(status="cancelled", cancelled_scope="series")
    assert "CANCELLED_SERIES" in code(compare(event(), series))
    for scope in (None, "unknown"):
        uncertain = event(status="cancelled")
        if scope is not None:
            uncertain["cancelled_scope"] = scope
        assert "CANCELLATION_SCOPE_UNVERIFIED" in code(compare(event(), uncertain))
    malformed_scope = event(status="cancelled", cancelled_scope=[])
    assert "CANCELLATION_SCOPE_UNVERIFIED" in code(compare(event(), malformed_scope))


def test_confirmed_event_after_proposal_baseline_is_not_mislabeled_as_current_proposal():
    result = compare(event(status="proposal"), event(status="confirmed"))
    assert code(result) == ["BASELINE_UNCONFIRMED"]
    assert "still a proposal" not in result["issues"][0]["explanation"]


def test_identity_mismatch_blocks_with_specific_content_free_code():
    for change, expected_code in (
        ({"organiser_id": "other"}, "ORGANISER_DRIFT"),
        ({"audience_revision": "other"}, "AUDIENCE_DRIFT"),
        ({"series_id": "other"}, "SERIES_DRIFT"),
        ({"occurrence_id": "other"}, "OCCURRENCE_DRIFT"),
        ({"original_occurrence_id": "other"}, "ORIGINAL_OCCURRENCE_DRIFT"),
        ({"event_id": "replacement"}, "AMBIGUOUS_IDENTITY"),
    ):
        result = compare(event(), event(**change))
        assert expected_code in code(result)
        assert result["write_proposed"] is False
        assert all("fictional" not in str(item).lower() for item in result["issues"])


def test_series_rule_drift_and_single_occurrence_lineage_are_not_conflated():
    changed = event(series_rule="FREQ=WEEKLY")
    assert "SERIES_DRIFT" in code(compare(event(), changed))
    moved = event(start="2026-10-01T10:00:00+10:00")
    assert "RESCHEDULED" in code(compare(event(), moved))


def test_naive_nonexistent_and_ambiguous_local_times_fail_closed():
    for raw, zone in (
        ("2026-10-04T02:30:00", "Australia/Sydney"),  # spring gap; no offset
        ("2026-04-05T02:30:00", "Australia/Sydney"),  # fall fold; no offset
        ("2026-10-04T02:30:00+10:00", "Australia/Sydney"),  # nonexistent wall time
        ("2026-01-01T09:00:00+10:00", "Australia/Sydney"),  # wrong zone offset
    ):
        result = compare(event(), event(start=raw, time_zone=zone))
        assert "TIME_UNVERIFIED" in code(result)


def test_stale_unapproved_changed_hash_and_inaccessible_pack_are_distinct_from_noop():
    for pack, expected_code in (
        ({"read_outcome": "complete", "pack_id": "pack-1", "pack_revision": "rev-3", "pack_hash": "sha256:fictional-3", "approved": True}, "PACK_DRIFT"),
        ({"read_outcome": "complete", "pack_id": "pack-1", "pack_revision": "rev-4", "pack_hash": "changed", "approved": True}, "PACK_DRIFT"),
        ({"read_outcome": "complete", "pack_link_id": "wrong-link", "pack_id": "pack-1", "pack_revision": "rev-4", "pack_hash": "sha256:fictional-4", "approved": True}, "PACK_DRIFT"),
        ({"read_outcome": "complete", "pack_id": "pack-1", "pack_revision": "rev-5", "pack_hash": "new", "approved": False}, "PACK_DRIFT"),
        ({"read_outcome": "inaccessible"}, "PACK_UNVERIFIED"),
    ):
        assert expected_code in code(compare(event(), event(pack=pack)))


def test_end_only_change_reports_duration_drift():
    result = compare(event(), event(end="2026-10-01T10:30:00+10:00"))
    assert "DURATION_DRIFT" in code(result)


def test_reschedule_is_not_timezone_drift_and_duration_is_compared_independently():
    moved = event(start="2026-10-01T10:00:00+10:00", end="2026-10-01T11:00:00+10:00")
    result = compare(event(), moved)
    assert "RESCHEDULED" in code(result)
    assert "TIMEZONE_DRIFT" not in code(result)
    longer_and_moved = event(start="2026-10-01T10:00:00+10:00", end="2026-10-01T11:30:00+10:00")
    assert {"RESCHEDULED", "DURATION_DRIFT"} <= set(code(compare(event(), longer_and_moved)))


def test_end_before_start_is_never_a_noop():
    result = compare(event(), event(start="2026-10-01T10:00:00+10:00", end="2026-10-01T09:00:00+10:00"))
    assert "TIME_UNVERIFIED" in code(result)


def test_missing_expected_bindings_and_malformed_event_fail_closed():
    old = snapshot(event())
    assert compare_snapshots({}, old, old)["state"] == "blocked"
    broken = snapshot(["not", "an", "event"])
    assert code(compare_snapshots(EXPECTED, broken, broken)) == ["SNAPSHOT_SHAPE_INVALID"]


def test_pure_module_has_no_external_io_or_calendar_connector_imports():
    import ast
    from pathlib import Path

    tree = ast.parse(Path("scripts/meeting_calendar_compare.py").read_text())
    imported = {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    imported.update(alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    assert imported <= {"__future__", "datetime", "zoneinfo"}


def test_metadata_match_does_not_claim_pack_readiness_or_remove_manual_review():
    result = compare()
    issue = result["issues"][0]
    assert issue["code"] == "NO_CHANGE"
    assert "metadata match the specified baseline" in issue["explanation"]
    assert "document contents and readiness are not verified" in issue["explanation"]
    assert "existing manual review" in issue["manual_next_step"]
