import json
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


MODULE = Path(__file__).parents[1] / 'scripts/validate_meeting_sources.py'
spec = importlib.util.spec_from_file_location('meeting_sources', MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def candidate(**updates):
    value = {
        'candidate_id': 'SYN-01',
        'source_ref': 'opsref:SYN-SOURCE-2026-04-27',
        'confirmation_ref': 'opsref:SYN-CONFIRM-2026-04-27',
        'document_meeting_date': '2026-04-27',
        'folder_meeting_date': '2026-04-27',
        'stored_folder_key': '2026-04',
        'expected_folder_key': '2026-04',
        'source_state': 'reviewed_candidate',
        'reviewer_alias': 'ctx_secretariat',
        'reviewed_at': '2026-09-25T09:00:00+10:00',
        'candidate_version_id': 'fictional-version-a',
        'confirmation_state': 'exact_version',
        'confirmed_version_id': 'fictional-version-a',
    }
    value.update(updates)
    return value


@pytest.mark.parametrize(('changes', 'outcome'), [
    ({'candidate_id': ' SYN-PADDED '}, 'hold_candidate_id_ambiguous'),
    ({'folder_meeting_date': '2026-05-25'}, 'hold_folder_date_conflict'),
    ({'stored_folder_key': '2026-05', 'expected_folder_key': '2026-04'}, 'hold_folder_identity_conflict'),
    ({'stored_folder_key': ' 2026-04'}, 'hold_folder_identity_ambiguous'),
    ({'expected_folder_key': '2026-04 '}, 'hold_folder_identity_ambiguous'),
    ({'confirmation_state': 'blank', 'confirmed_version_id': None, 'confirmation_ref': None}, 'hold_confirmation_blank'),
    ({'confirmation_state': 'meeting_only', 'confirmed_version_id': None}, 'hold_confirmation_not_version_bound'),
    ({'candidate_id': '   '}, 'hold_candidate_id_unknown'),
    ({'reviewer_alias': None}, 'hold_reviewer_provenance_missing'),
    ({'reviewed_at': None}, 'hold_reviewer_provenance_missing'),
    ({'confirmation_ref': None}, 'hold_confirmation_evidence_ref_unknown'),
    ({'confirmation_state': 'blank', 'confirmed_version_id': None,
      'confirmation_ref': 'opsref:SYN-CONFIRM-2026-04-27'}, 'hold_confirmation_evidence_ref_conflict'),
    ({'document_meeting_date': None}, 'hold_document_date_unknown'),
    ({'folder_meeting_date': None}, 'hold_folder_date_unknown'),
    ({'source_state': 'draft'}, 'hold_source_state_unresolved'),
    ({'candidate_version_id': None}, 'hold_candidate_version_unknown'),
    ({'candidate_version_id': ''}, 'hold_candidate_version_unknown'),
    ({'candidate_version_id': '  '}, 'hold_candidate_version_unknown'),
    ({'candidate_version_id': ' fictional-version-a'}, 'hold_candidate_version_ambiguous'),
    ({'confirmed_version_id': None}, 'hold_confirmation_version_unknown'),
    ({'confirmed_version_id': ''}, 'hold_confirmation_version_unknown'),
    ({'confirmed_version_id': 'fictional-version-b'}, 'hold_confirmation_version_mismatch'),
    ({'confirmed_version_id': 'Fictional-version-a'}, 'hold_confirmation_version_mismatch'),
    ({'confirmed_version_id': ' fictional-version-a'}, 'hold_confirmation_version_ambiguous'),
    ({'confirmation_state': 'blank', 'confirmed_version_id': 'fictional-version-a'}, 'hold_confirmation_metadata_conflict'),
])
def test_ambiguous_source_is_preserved_unselected(changes, outcome):
    result = validator.assess(candidate(**changes))
    assert result['outcome'] == outcome
    assert len(result['next_checks']) == len(result['hold_reasons'])
    assert all(reason in validator.HOLD_GUIDANCE for reason in result['hold_reasons'])
    assert result['selected'] is False
    assert result['approved'] is False


def test_matching_mapping_and_exact_version_confirmation_still_needs_human_review():
    result = validator.assess(candidate())
    assert result == {
        'candidate_id': 'SYN-01',
        'source_ref': 'opsref:SYN-SOURCE-2026-04-27',
        'confirmation_ref': 'opsref:SYN-CONFIRM-2026-04-27',
        'document_meeting_date': '2026-04-27',
        'folder_meeting_date': '2026-04-27',
        'stored_folder_key': '2026-04',
        'expected_folder_key': '2026-04',
        'source_state': 'reviewed_candidate',
        'reviewer_alias': 'ctx_secretariat',
        'reviewed_at': '2026-09-25T09:00:00+10:00',
        'candidate_version_id': 'fictional-version-a',
        'confirmation_state': 'exact_version',
        'confirmed_version_id': 'fictional-version-a',
        'outcome': 'structurally_consistent_human_review_required',
        'hold_reasons': [],
        'next_checks': [],
        'selected': False,
        'approved': False,
    }


def test_conflicting_document_date_is_not_normalized_to_folder_date():
    result = validator.assess(candidate(document_meeting_date='2026-02-23', folder_meeting_date='2026-02-25'))
    assert result['outcome'] == 'hold_folder_date_conflict'
    assert result['candidate_id'] == 'SYN-01'
    assert result['document_meeting_date'] == '2026-02-23'
    assert result['folder_meeting_date'] == '2026-02-25'
    assert result['stored_folder_key'] == result['expected_folder_key'] == '2026-04'


def test_folder_key_case_is_ignored_but_whitespace_is_not():
    result = validator.assess(candidate(stored_folder_key='Folder-April', expected_folder_key='folder-april'))
    assert result['outcome'] == 'structurally_consistent_human_review_required'
    result = validator.assess(candidate(stored_folder_key='Folder-April', expected_folder_key='folder-april '))
    assert result['outcome'] == 'hold_folder_identity_ambiguous'


def test_multiple_independent_conflicts_are_reported_together():
    result = validator.assess(candidate(
        folder_meeting_date='2026-05-25',
        stored_folder_key='2026-05',
        confirmed_version_id='fictional-version-b',
        source_state='draft',
    ))
    assert result['outcome'] == 'hold_confirmation_version_mismatch'
    assert result['hold_reasons'] == [
        'hold_confirmation_version_mismatch',
        'hold_folder_identity_conflict',
        'hold_folder_date_conflict',
        'hold_source_state_unresolved',
    ]
    assert len(result['next_checks']) == len(result['hold_reasons'])
    assert not result['selected'] and not result['approved']


@pytest.mark.parametrize('changes', [
    {'document_meeting_date': '27/04/2026'},
    {'source_ref': 'opsref:/private/source.docx'},
    {'source_ref': 'opsref:https.example/secret'},
    {'reviewer_alias': 'person@example.invalid'},
])
def test_inconsistent_or_unknown_metadata_fails_closed(changes):
    with pytest.raises(ValueError):
        validator.assess(candidate(**changes))


def test_unknown_confirmation_state_is_held_not_promoted():
    result = validator.assess(candidate(confirmation_state='confirmed', confirmed_version_id=None))
    assert result['outcome'] == 'hold_confirmation_state_unknown'
    assert result['selected'] is False
    assert result['approved'] is False


def test_duplicate_candidate_ids_remain_visible_and_held():
    result = validator.validate({'candidates': [candidate(), candidate(candidate_id=' syn-01 ')]})
    assert result['status'] == 'REVIEW_REQUIRED'
    assert [row['candidate_id'] for row in result['candidates']] == ['SYN-01', ' syn-01 ']
    assert result['candidates'][0]['outcome'] == 'hold_duplicate_candidate_id'
    assert result['candidates'][1]['outcome'] == 'hold_candidate_id_ambiguous'
    assert result['candidates'][0]['hold_reasons'] == ['hold_duplicate_candidate_id']
    assert result['candidates'][1]['hold_reasons'] == [
        'hold_candidate_id_ambiguous', 'hold_duplicate_candidate_id']
    assert all(not row['selected'] and not row['approved'] for row in result['candidates'])
    assert result['selected'] == result['approved'] == 0


def test_whitespace_only_candidate_id_is_held_without_dropping_batch_rows():
    result = validator.validate({'candidates': [candidate(), candidate(candidate_id='   ')]})
    assert [row['candidate_index'] for row in result['candidates']] == [1, 2]
    assert [row['candidate_id'] for row in result['candidates']] == ['SYN-01', '   ']
    assert result['candidates'][1]['outcome'] == 'hold_candidate_id_unknown'
    assert result['candidates'][1]['next_checks']
    assert result['selected'] == result['approved'] == 0


def test_cli_keeps_valid_rows_visible_next_to_whitespace_only_id(tmp_path):
    review = tmp_path / 'fictional-whitespace-id.json'
    review.write_text(json.dumps({'candidates': [candidate(), candidate(candidate_id='   ')]}),
                      encoding='utf-8')
    completed = subprocess.run(
        [sys.executable, str(MODULE), str(review)], capture_output=True, text=True, check=True)
    result = json.loads(completed.stdout)
    assert [row['candidate_index'] for row in result['candidates']] == [1, 2]
    assert result['candidates'][1]['candidate_id'] == '   '
    assert result['candidates'][1]['outcome'] == 'hold_candidate_id_unknown'
    assert result['selected'] == result['approved'] == 0


def test_all_outputs_remain_unselected_and_unapproved():
    result = validator.validate({'candidates': [
        candidate(),
        candidate(candidate_id='SYN-02', confirmation_state='blank', confirmed_version_id=None,
                  confirmation_ref=None),
    ]})
    assert result['status'] == 'REVIEW_REQUIRED'
    assert result['selected'] == result['approved'] == 0
    assert all(not row['selected'] and not row['approved'] for row in result['candidates'])
    assert 'not authenticated' in result['authority']


def test_cli_emits_review_required_without_selecting_or_approving(tmp_path):
    review = tmp_path / 'fictional-review.json'
    review.write_text(json.dumps({'candidates': [candidate()]}), encoding='utf-8')
    completed = subprocess.run(
        [sys.executable, str(MODULE), str(review)], capture_output=True, text=True, check=True)
    result = json.loads(completed.stdout)
    assert result['status'] == 'REVIEW_REQUIRED'
    assert result['selected'] == result['approved'] == 0
    assert result['candidates'][0]['outcome'] == 'structurally_consistent_human_review_required'
    assert result['candidates'][0]['document_meeting_date'] == '2026-04-27'
    assert result['candidates'][0]['stored_folder_key'] == '2026-04'
    assert result['candidates'][0]['source_state'] == 'reviewed_candidate'
    assert result['candidates'][0]['confirmation_state'] == 'exact_version'
    assert result['candidates'][0]['candidate_version_id'] == 'fictional-version-a'
    assert result['candidates'][0]['confirmed_version_id'] == 'fictional-version-a'
    assert result['candidates'][0]['source_ref'] == 'opsref:SYN-SOURCE-2026-04-27'
    assert result['candidates'][0]['reviewer_alias'] == 'ctx_secretariat'
    assert result['candidates'][0]['next_checks'] == []


def test_documented_synthetic_review_map_runs_through_cli():
    fixture = Path(__file__).parent / 'fixtures/meeting_source_review.json'
    completed = subprocess.run(
        [sys.executable, str(MODULE), str(fixture)],
        capture_output=True, text=True, check=True)
    result = json.loads(completed.stdout)
    assert result['status'] == 'REVIEW_REQUIRED'
    assert [row['outcome'] for row in result['candidates']] == [
        'structurally_consistent_human_review_required',
        'hold_confirmation_version_mismatch',
        'hold_candidate_version_unknown',
        'hold_confirmation_blank',
        'hold_duplicate_candidate_id',
        'hold_candidate_id_ambiguous',
    ]
    assert result['selected'] == result['approved'] == 0
    assert all(not row['selected'] and not row['approved'] for row in result['candidates'])
    assert [row['candidate_id'] for row in result['candidates'][-2:]] == [
        'SYN-DUPLICATE', ' syn-duplicate ']
    assert 'hold_duplicate_candidate_id' in result['candidates'][-1]['hold_reasons']
    assert 'hold_confirmation_version_mismatch' in result['candidates'][-1]['hold_reasons']
    assert len(result['candidates'][-1]['next_checks']) == len(result['candidates'][-1]['hold_reasons'])
    assert [row['candidate_index'] for row in result['candidates']] == [1, 2, 3, 4, 5, 6]
    assert len(result['candidates'][1]['hold_reasons']) > 1
    assert len(result['candidates'][1]['next_checks']) == len(result['candidates'][1]['hold_reasons'])


def test_cli_file_error_does_not_echo_path(tmp_path):
    missing = tmp_path / 'private-looking-source-map.json'
    completed = subprocess.run(
        [sys.executable, str(MODULE), str(missing)], capture_output=True, text=True)
    assert completed.returncode == 2
    assert 'Source review file-access error' in completed.stderr
    assert str(missing) not in completed.stderr


def test_cli_malformed_late_candidate_emits_no_partial_json(tmp_path):
    malformed = candidate(candidate_id='SYN-MALFORMED')
    del malformed['expected_folder_key']
    review = tmp_path / 'fictional-malformed-batch.json'
    review.write_text(json.dumps({'candidates': [candidate(), malformed]}), encoding='utf-8')
    completed = subprocess.run(
        [sys.executable, str(MODULE), str(review)], capture_output=True, text=True)
    assert completed.returncode == 2
    assert completed.stdout == ''
    assert 'documented source-review fields' in completed.stderr
    assert str(review) not in completed.stderr


def test_cli_rejects_duplicate_json_object_keys_without_partial_output(tmp_path):
    review = tmp_path / 'fictional-duplicate-keys.json'
    review.write_text('{"candidates": [], "candidates": []}', encoding='utf-8')
    completed = subprocess.run(
        [sys.executable, str(MODULE), str(review)], capture_output=True, text=True)
    assert completed.returncode == 2
    assert completed.stdout == ''
    assert 'Duplicate JSON object key' in completed.stderr


def test_unknown_confirmation_is_held_instead_of_dropped():
    result = validator.assess(candidate(confirmation_state='unrecognised', confirmed_version_id=None))
    assert result['outcome'] == 'hold_confirmation_state_unknown'
    assert result['selected'] is False
    assert result['approved'] is False


def test_unknown_source_state_is_held():
    result = validator.assess(candidate(source_state='unrecognised'))
    assert result['outcome'] == 'hold_source_state_unresolved'
    assert result['selected'] is False
    assert result['approved'] is False


def test_mixed_batch_keeps_version_mismatch_visible_next_to_matching_candidate():
    missing = candidate(candidate_id='SYN-MISSING')
    del missing['candidate_version_id']
    missing_confirmation = candidate(candidate_id='SYN-MISSING-CONFIRMATION')
    del missing_confirmation['confirmed_version_id']
    result = validator.validate({'candidates': [
        candidate(candidate_id='SYN-MATCH'),
        candidate(candidate_id='SYN-MISMATCH', confirmed_version_id='fictional-version-b'),
        missing,
        missing_confirmation,
    ]})
    assert result['status'] == 'REVIEW_REQUIRED'
    assert [row['candidate_id'] for row in result['candidates']] == [
        'SYN-MATCH', 'SYN-MISMATCH', 'SYN-MISSING', 'SYN-MISSING-CONFIRMATION']
    assert result['candidates'][1]['outcome'] == 'hold_confirmation_version_mismatch'
    assert result['candidates'][1]['candidate_version_id'] == 'fictional-version-a'
    assert result['candidates'][1]['confirmed_version_id'] == 'fictional-version-b'
    assert result['candidates'][1]['confirmation_state'] == 'exact_version'
    assert result['candidates'][2]['outcome'] == 'hold_candidate_version_unknown'
    assert result['candidates'][2]['candidate_version_id'] is None
    assert result['candidates'][3]['outcome'] == 'hold_confirmation_version_unknown'
    assert result['candidates'][3]['confirmed_version_id'] is None
    assert result['candidates'][3]['confirmation_state'] == 'exact_version'
    assert result['selected'] == result['approved'] == 0
    assert all(not row['selected'] and not row['approved'] for row in result['candidates'])


def test_missing_confirmation_version_field_is_held():
    value = candidate()
    del value['confirmed_version_id']
    result = validator.assess(value)
    assert result['outcome'] == 'hold_confirmation_version_unknown'
    assert result['confirmed_version_id'] is None
    assert result['selected'] is False
    assert result['approved'] is False
