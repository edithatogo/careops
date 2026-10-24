import csv
import importlib.util
from pathlib import Path

import pytest


MODULE = Path(__file__).parents[1] / 'scripts/validate_action_review.py'
spec = importlib.util.spec_from_file_location('action_review', MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

HEADERS = [
    'Review ID', 'Follow-up', 'Evidence classification',
    'People described in source (not assignments)', 'Timing as recorded',
    'Evidence', 'Outstanding qualification', 'Commissioning status',
    'Issue readiness',
]
ROW = [
    'F-01', 'Fictional follow-up', 'Fictional candidate', 'Not recorded',
    'Not recorded', 'Fictional source S1, paragraph 4', 'Needs fictional review',
    'Unresolved; chair classification required', 'Hold; no live issue or assignment',
]


def write_csv(path, rows=None, headers=None):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(HEADERS if headers is None else headers)
        writer.writerows([ROW] if rows is None else rows)
    return path


def test_synthetic_candidate_remains_held(tmp_path):
    result = validator.validate(write_csv(tmp_path / 'review.csv'))
    assert result['status'] == 'STRUCTURE_VALID'
    assert result['rows'] == 1
    assert result['promoted'] == 0
    assert 'no source truth' in result['authority']


def test_duplicate_local_review_id_is_rejected(tmp_path):
    duplicate = ROW.copy()
    duplicate[0] = ' f-01 '
    with pytest.raises(ValueError, match='duplicate local review ID'):
        validator.validate(write_csv(tmp_path / 'review.csv', [ROW, duplicate]))


def test_extra_unquoted_fields_are_rejected(tmp_path):
    path = tmp_path / 'review.csv'
    path.write_text(','.join(HEADERS) + '\n' + ','.join(ROW) + ',unexpected\n', encoding='utf-8')
    with pytest.raises(ValueError, match='extra CSV fields'):
        validator.validate(path)


def test_extra_empty_field_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='extra CSV fields'):
        validator.validate(write_csv(tmp_path / 'review.csv', [ROW + ['']]))


def test_short_row_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='Issue readiness must not be blank'):
        validator.validate(write_csv(tmp_path / 'review.csv', [ROW[:-1]]))


def test_malformed_quoting_is_rejected(tmp_path):
    path = tmp_path / 'review.csv'
    path.write_text(','.join(HEADERS) + '\n' + ','.join(ROW[:-1]) + ',"Hold\n', encoding='utf-8')
    with pytest.raises(csv.Error):
        validator.validate(path)


@pytest.mark.parametrize('header', ['Review ID ', 'review id'])
def test_duplicate_headers_after_normalization_are_rejected(tmp_path, header):
    headers = HEADERS + [header]
    row = ROW + ['extra']
    with pytest.raises(ValueError, match='column names must be unique'):
        validator.validate(write_csv(tmp_path / 'review.csv', [row], headers))


def test_required_header_whitespace_and_case_are_normalized(tmp_path):
    headers = HEADERS.copy()
    headers[0] = ' review id '
    headers[1] = 'FOLLOW-UP'
    result = validator.validate(write_csv(tmp_path / 'review.csv', [ROW], headers))
    assert result['status'] == 'STRUCTURE_VALID'


@pytest.mark.parametrize(('column', 'value'), [
    ('Issue readiness', 'issued'),
    ('Issue readiness', 'hold; issued after approval'),
    ('Commissioning status', 'commissioned'),
    ('Commissioning status', 'unresolved; commissioned'),
])
def test_validator_cannot_promote_or_accept_contradictory_status(tmp_path, column, value):
    row = ROW.copy()
    row[HEADERS.index(column)] = value
    with pytest.raises(ValueError, match='pending chair'):
        validator.validate(write_csv(tmp_path / 'review.csv', [row]))


def test_missing_required_cell_is_rejected(tmp_path):
    row = ROW.copy()
    row[HEADERS.index('Evidence')] = ''
    with pytest.raises(ValueError, match='Evidence must not be blank'):
        validator.validate(write_csv(tmp_path / 'review.csv', [row]))
