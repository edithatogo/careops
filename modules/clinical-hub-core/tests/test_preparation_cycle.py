from copy import deepcopy
import pytest
from scripts.preparation_cycle import next_cycle, validate
from scripts.reviewed_action_comparison import action_discrepancies


def cycle():
    return dict(cycle='FICTIONAL-1',meeting='To confirm',priorities='Unanswered concern',pack='fixture://pack',
        register='fixture://register',previous_cycle=None,controls={
        'one':dict(state='Waiting for input',note='Retain unresolved source',source='fixture://one'),
        'two':dict(state='Ready for chair review',note='Earlier review',source='fixture://two')})


def test_contract_and_carry_preserve_input_and_unresolved_work():
    data=cycle();before=deepcopy(data)
    result=next_cycle(data,'FICTIONAL-2','fixture://prior',control_keys=['one','two'])
    assert data==before and result['controls']['one']==data['controls']['one']
    assert result['controls']['two']['state']=='Not started' and result['previous_cycle']=='fixture://prior'


@pytest.mark.parametrize('keys',[[],['one'],['one','one'],['one',None],None])
def test_unqualified_control_contract_refused(keys):
    with pytest.raises(ValueError):validate(cycle(),control_keys=keys)


def test_same_cycle_and_unsupported_assignments_refused():
    data=cycle()
    with pytest.raises(ValueError):next_cycle(data,'FICTIONAL-1','prior',control_keys=['one','two'])
    data['controls']['one']['assigned_to']='Fictional role'
    with pytest.raises(ValueError):validate(data,control_keys=['one','two'])


def test_source_comparator_rejects_invention_omission_changes_and_duplicates():
    expected=[dict(id='FICTIONAL-1',owner='Fictional accepted role'),dict(id='FICTIONAL-2',owner='Another fictional role')]
    assert set(action_discrepancies(expected,[dict(id='FICTIONAL-1',owner='Wrong'),dict(id='FICTIONAL-3')]))=={
        'omitted:FICTIONAL-2','invented:FICTIONAL-3','incorrect:FICTIONAL-1:owner'}
    assert action_discrepancies(expected,expected+[expected[0]])==['duplicate:FICTIONAL-1']


@pytest.mark.parametrize('expected,proposed',[
    ([{'id':'one'},{'id':'one'}],[]),
    ([{'id':'one'}],[{'id':None}]),
    ([{'id':[]}],[]),
])
def test_ambiguous_or_malformed_source_cannot_pass_comparison(expected,proposed):
    with pytest.raises(ValueError):action_discrepancies(expected,proposed)


def test_added_claims_require_source_support():
    assert action_discrepancies([{'id':'one'}],[{'id':'one','commissioned':True}])==['unexpected:one:commissioned']
