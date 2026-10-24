"""Fictional offline boundaries; no provider, tenant or native writes."""
from copy import deepcopy
import pytest
from scripts.f10_source_adapter import carry_identity_key
from scripts.optional_action_reference import propose

SOURCE = '11111111-1111-4111-8111-111111111111'
OTHER = '22222222-2222-4222-8222-222222222222'


def fixture():
    envelope = dict(contract_version=1, source_id=SOURCE, record_id='Action-1',
                    meeting_id='SYN-2026-10', revision='v2', operation_key='attempt-1',
                    fields={'Title': 'Fictional review', 'Question_x0020_or_x0020_help_x00':
                            'Review fictional proposal', 'Meeting_x0020_date': '2026-10-24'})
    row = dict(envelope['fields'], Id=1, OData__UIVersionString='3.0',
               **{'odata.etag': '"3"'}, CarryForwardKey=carry_identity_key(SOURCE, 'Action-1', 'SYN-2026-10'))
    return envelope, row


def test_standalone_preserves_rows_and_returns_detached_snapshot():
    _, row = fixture(); rows = [row]
    result = propose(rows)
    assert result['status'] == 'standalone' and not result['write_proposed']
    result['local_rows'][0]['Title'] = 'Changed result'
    assert rows[0]['Title'] == 'Fictional review'


def test_cross_source_same_record_is_not_merged():
    envelope, row = fixture(); envelope['source_id'] = OTHER
    result = propose([row], envelope, expected_revision='v2')
    assert result['status'] == 'NOT_FOUND' and result['proposal'] is None
    assert result['receipt']['source_identity'] == 'f10:native1|22222222-2222-4222-8222-222222222222|Action-1|SYN-2026-10'
    assert not result['write_proposed']


@pytest.mark.parametrize('revision', [None, 'v1'])
def test_unverified_or_stale_revision_holds_even_for_existing_match(revision):
    envelope, row = fixture()
    result = propose([row], envelope, expected_revision=revision)
    assert result['status'] == 'stale_or_unverified' and result['proposal'] is None


def test_exact_match_and_duplicate_retry_never_write():
    envelope, row = fixture()
    first = propose([row], envelope, expected_revision='v2')
    assert first['status'] == 'EXISTING_MATCH' and first['proposal'] == envelope['fields']
    again = propose([row], envelope, expected_revision='v2', prior=first['receipt'])
    assert again['status'] == 'duplicate' and not again['write_proposed']
    assert again['proposal'] is None


def test_changed_retry_requires_reconciliation():
    envelope, row = fixture(); first = propose([row], envelope, expected_revision='v2')
    envelope['operation_key'] = 'attempt-2'
    result = propose([row], envelope, expected_revision='v2', prior=first['receipt'])
    assert result['status'] == 'reconciliation_required' and result['proposal'] is None


@pytest.mark.parametrize('duplicate', [True, False])
def test_ambiguous_identity_and_human_edits_are_preserved(duplicate):
    envelope, row = fixture(); rows = [row, deepcopy(row)] if duplicate else [row]
    if not duplicate:
        rows[0]['Title'] = 'Fictional human edit'
    original = deepcopy((rows, envelope))
    result = propose(rows, envelope, expected_revision='v2')
    assert result['status'] == ('AMBIGUOUS_IDENTITY' if duplicate else 'HUMAN_EDIT_OR_SOURCE_CHANGE')
    assert result['proposal'] is None and not result['write_proposed']
    assert (rows, envelope) == original and result['local_rows'] == rows


def test_prior_receipt_does_not_hide_later_human_edit():
    envelope, row = fixture(); first = propose([row], envelope, expected_revision='v2')
    row['Title'] = 'Fictional later edit'
    result = propose([row], envelope, expected_revision='v2', prior=first['receipt'])
    assert result['status'] == 'HUMAN_EDIT_OR_SOURCE_CHANGE'


@pytest.mark.parametrize('change', [{'contract_version': True}, {'source_id': 'invalid'},
                                   {'revision': ''}, {'record_id': False},
                                   {'fields': {'Title': 'Incomplete'}}, {'extra': 'field'}])
def test_malformed_envelopes_fail_closed(change):
    envelope, row = fixture(); envelope.update(change)
    result = propose([row], envelope, expected_revision='v2')
    assert result['status'] == 'invalid_envelope' and result['proposal'] is None
    assert not result['write_proposed']
