"""Bounded offline property fuzzing: malformed reads never authorize writes."""
from copy import deepcopy

from hypothesis import given, settings, strategies as st
from scripts.meeting_calendar_compare import compare_snapshots
from test_meeting_calendar_compare import EXPECTED, event, snapshot

scalar = st.none() | st.booleans() | st.integers() | st.text(max_size=60)
json_value = st.recursive(scalar, lambda child: st.lists(child, max_size=5)
                          | st.dictionaries(st.text(max_size=20), child, max_size=5),
                          max_leaves=20)


@settings(max_examples=300, deadline=None, derandomize=True)
@given(before=json_value, current=json_value)
def test_arbitrary_snapshot_shapes_are_read_only_and_preserved(before, current):
    original = deepcopy((before, current))
    result = compare_snapshots(EXPECTED, before, current)
    assert result['state'] == 'blocked'
    assert result['write_proposed'] is False
    assert (before, current) == original


@settings(max_examples=300, deadline=None, derandomize=True)
@given(field=st.sampled_from(['event_id', 'occurrence_id', 'original_occurrence_id',
                             'series_id', 'organiser_id', 'audience_revision']),
       replacement=st.text(max_size=100))
def test_identity_drift_cannot_be_reported_as_unchanged(field, replacement):
    old = snapshot(event())
    current = snapshot(event(**{field: replacement}))
    original = deepcopy((old, current))
    result = compare_snapshots(EXPECTED, old, current)
    assert result['write_proposed'] is False
    if replacement != EXPECTED[field]:
        assert result['state'] == 'blocked'
    assert (old, current) == original


@settings(max_examples=300, deadline=None, derandomize=True)
@given(pack=json_value)
def test_unverified_pack_never_becomes_no_change(pack):
    current = snapshot(event(pack=pack))
    original = deepcopy(current)
    result = compare_snapshots(EXPECTED, snapshot(event()), current)
    assert result['state'] != 'no_change'
    assert result['write_proposed'] is False
    assert current == original
