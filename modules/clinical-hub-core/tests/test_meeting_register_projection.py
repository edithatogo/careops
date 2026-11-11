"""A shared register produces isolated, deterministic no-write meeting projections."""
from copy import deepcopy
from scripts.meeting_register_projection import project_register


def item(forum, record, status='open', **overrides):
    row = {
        'forum_ref': forum, 'record_id': record, 'occurrence_ref': 'occ-2026-11',
        'kind': 'action', 'status': status, 'version': '3.0',
        'source_ref': 'approved-minutes', 'source_revision': 'v1',
        'owner_ref': None, 'due_date': None, 'completion_evidence_ref': None,
    }
    row.update(overrides)
    return row


def test_independent_forums_with_one_shared_register():
    records = [item('medication', 'act-1'), item('quality', 'act-1', 'held')]
    original = deepcopy(records)
    result = project_register(['medication', 'quality'], records)
    assert result['state'] == 'review_only'
    assert len(result['forums']) == 2
    assert result['forums'][0]['forum_ref'] == 'medication'
    assert result['forums'][1]['forum_ref'] == 'quality'
    assert result['forums'][0]['open'] == 1
    assert result['forums'][1]['held'] == 1
    assert result['forums'][0]['records'][0]['key'] != result['forums'][1]['records'][0]['key']
    assert project_register(['quality', 'medication'], list(reversed(records)))['sha256'] == result['sha256']
    assert records == original
    assert result['native_write_authorised'] is False


def test_unexpected_forum_and_duplicate_identity_block_entire_projection():
    assert project_register(['medication'], [item('quality', 'act-1')])['state'] == 'blocked'
    assert project_register(['medication'], [item('medication', 'act-1'), item('medication', 'act-1')])['state'] == 'blocked'
    assert project_register(['medication', 'medication'], [])['state'] == 'blocked'


def test_completion_evidence_is_not_equivalent_to_accepted_resolution():
    result = project_register(['medication'], [item('medication', 'act-1', status='reported_complete', completion_evidence_ref='receipt-1')])
    assert result['state'] == 'review_only'
    assert result['forums'][0]['reported_complete'] == 1
    assert result['forums'][0]['resolved'] == 0
    assert result['forums'][0]['records'][0]['status'] == 'reported_complete'


def test_resolved_requires_evidence_and_rejects_incomplete_bindings():
    assert project_register(['medication'], [item('medication', 'act-1', 'resolved')])['state'] == 'blocked'
    assert project_register(['medication'], [item('medication', 'act-1', 'resolved', completion_evidence_ref='receipt-1')])['state'] == 'review_only'
    assert project_register(['medication'], [item('medication', 'act-1', 'open', source_revision='')])['state'] == 'blocked'


def test_rejects_unrecognised_fields_and_automatic_action_semantics():
    assert project_register(['medication'], [item('medication', 'act-1', issue_minutes=True)])['state'] == 'blocked'
    assert project_register(['medication'], [item('medication', 'act-1', status='auto_resolved')])['state'] == 'blocked'
    assert project_register(['medication'], [{'forum_ref': 'medication'}])['state'] == 'blocked'


def test_empty_register_supported_without_invented_actions():
    result = project_register(['medication'], [])
    assert result['state'] == 'review_only'
    assert result['forums'][0]['records'] == []
    assert result['forums'][0]['open'] == 0


def test_invalid_calendar_dates_and_unqualified_completion_are_refused():
    assert project_register(['medication'], [item('medication', 'act-1', due_date='2026-02-30')])['state'] == 'blocked'
    assert project_register(['medication'], [item('medication', 'act-1', status='reported_complete')])['state'] == 'blocked'
