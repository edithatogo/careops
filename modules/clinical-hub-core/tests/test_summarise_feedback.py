import csv
import hashlib
from copy import deepcopy
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from summarise_feedback import FIELDS, run, summarise


def row(i, rec='', use=''):
    return dict(meeting_id='SYN-01', question_version='1', response_id=str(i), recommendation=rec, usefulness=use, comment='')


def test_denominator_missing_invalid_and_no_comment_disclosure():
    rows = [row(1, '10', '5'), row(2, '7', '3'), row(3, '6', ''), row(4, '', '9'), row(5, 'bad', '2')]
    rows[0]['comment'] = 'Private fictional concern'
    original = deepcopy(rows)
    result = summarise(rows, 'SYN-01', '1')
    assert result['recommendation']['nps'] == 0
    assert result['recommendation']['valid'] == 3
    assert result['recommendation']['missing'] == 1
    assert result['recommendation']['invalid'] == 1
    assert result['usefulness']['mean'] == 3.33
    assert result['comments_answered'] == 1
    assert 'Private fictional concern' not in str(result)
    assert rows == original


def test_passives_remain_in_nps_denominator():
    assert summarise([row(1,'9'),row(2,'8')], 'SYN-01','1')['recommendation']['nps'] == 50


@pytest.mark.parametrize('rows', [[], [row(1)], [row(1,'11','0')]])
def test_no_valid_scores_are_null(rows):
    result = summarise(rows, 'SYN-01','1')
    assert result['recommendation']['nps'] is None
    assert result['usefulness']['mean'] is None


@pytest.mark.parametrize('fault', ['duplicate','meeting','version','missing_id','extra','malformed'])
def test_ambiguous_inputs_block_summary(fault):
    rows = [row(1),row(2)]
    if fault == 'duplicate': rows[1]['response_id']='1'
    if fault == 'meeting': rows[1]['meeting_id']='SYN-02'
    if fault == 'version': rows[1]['question_version']='2'
    if fault == 'missing_id': rows[1]['response_id']=' '
    if fault == 'extra': rows[1]['email']='fictional@example.invalid'
    if fault == 'malformed': rows[1]['comment']=None
    with pytest.raises(ValueError): summarise(rows,'SYN-01','1')


def test_preserves_raw_and_refuses_overwrite(tmp_path):
    source=tmp_path/'input.csv'; output=tmp_path/'output.json'
    with source.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=sorted(FIELDS));writer.writeheader();writer.writerow(row(1,'9','5'))
    original=source.read_bytes()
    result=run(source,output,'SYN-01','1'); saved=output.read_bytes()
    assert result['provenance']['input_sha256']==hashlib.sha256(original).hexdigest()
    assert result['provenance']['calculation_version']=='1'
    with pytest.raises(FileExistsError): run(source,output,'SYN-01','1')
    assert source.read_bytes()==original and output.read_bytes()==saved
