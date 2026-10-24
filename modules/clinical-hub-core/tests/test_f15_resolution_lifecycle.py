from copy import deepcopy
import pytest
from scripts.f15_resolution_lifecycle import propose_lifecycle, ACTIONS


def state():
    binding = dict(action_id='FICTIONAL-A1', register_revision='r1', minutes_record_id='FICTIONAL-M1',
                   minutes_revision='m1', permission_revision='p1')
    return dict(schema='f15-lifecycle-v1', synthetic_only=True, status='open', state_version=0,
        history=[], responses=[], binding=binding, current_binding=deepcopy(binding),
        required_components=['ask1','ask2'], reported_completion='unknown', closure=None,
        concern='Retain unanswered concern', dissent=['Retain dissent'],
        policy={'revision':'p1','actions_by_role':{'chair':sorted(ACTIONS),
                'secretariat':['record_response','report_complete','refer','hold','return']}})


def req(action, s, **changes):
    r=dict(request_id=f'FICTIONAL-REQ-{s["state_version"]}', expected_version=s['state_version'],
           actor_role='chair',action=action,reason='FICTIONAL reason',evidence_ref='FICTIONAL-EVIDENCE')
    r.update(changes)
    return r


def response(**changes):
    r=dict(response_id='FICTIONAL-R1', action_id='FICTIONAL-A1', state='complete',relevance='relevant',
           evidence_ref='FICTIONAL-E1',evidence_revision='e1',components=['ask1','ask2'],
           date_state='unknown',date_value=None,supersedes=[])
    r.update(changes);return r


def closure():
    return dict(authority_ref='FICTIONAL-CHAIR',decision_ref='FICTIONAL-M1',decision_revision='m1',
                evidence_ref='FICTIONAL-DECISION',date_state='unknown',date_value=None)


def step(s, action, **changes):
    result=propose_lifecycle(s,req(action,s,**changes));assert result['ok'],result
    return result['proposal']


def test_reported_completion_and_referral_do_not_resolve():
    s=state();s=step(s,'report_complete');assert s['status']=='open'
    assert s['reported_completion']=='complete' and s['closure'] is None
    s=step(s,'refer');assert s['status']=='referred'
    assert propose_lifecycle(s,req('resolve',s,closure=closure()))['code']=='RESPONSE_REVIEW_REQUIRED'


@pytest.mark.parametrize('status',['partial','disputed','withdrawn','delayed'])
def test_incomplete_response_prevents_closure(status):
    s=step(state(),'record_response',response=response(state=status))
    assert propose_lifecycle(s,req('resolve',s,closure=closure()))['code']=='RESPONSE_REVIEW_REQUIRED'


def test_resolution_reopen_and_disputed_closure_retain_history():
    initial=state();original=deepcopy(initial)
    s=step(initial,'record_response',response=response());s=step(s,'resolve',closure=closure())
    assert s['status']=='resolved' and initial==original
    prior=deepcopy(s);s=step(s,'record_response',response=response(response_id='FICTIONAL-R2',state='disputed'))
    assert s['status']=='reopened' and s['history'][:-1]==prior['history']
    assert s['closure']==prior['closure'] and s['history'][-1]['prior_closure']==prior['closure']
    assert s['concern']==original['concern'] and s['dissent']==original['dissent']
    assert all(r['date_value'] is None for r in s['responses'])


def test_complete_response_explicitly_supersedes_partial_without_erasing_it():
    s=step(state(),'record_response',response=response(state='partial'))
    s=step(s,'record_response',response=response(response_id='FICTIONAL-R2',supersedes=['FICTIONAL-R1']))
    s=step(s,'resolve',closure=closure());assert s['status']=='resolved'
    assert len(s['responses'])==2 and s['responses'][0]['state']=='partial'


def test_referral_hold_return_supersede_reopen():
    s=state()
    for action,target in [('refer','referred'),('hold','held'),('return','returned'),
                           ('supersede','superseded'),('reopen','reopened')]:
        s=step(s,action,successor_ref='FICTIONAL-A2');assert s['status']==target
    assert len(s['history'])==5


@pytest.mark.parametrize('fault,code',[('version','STALE_STATE'),('role','ROLE_REFUSED'),
    ('binding','SOURCE_BINDING_CHANGED'),('policy','POLICY_CHANGED'),('scope','FICTIONAL_SCOPE_REQUIRED')])
def test_refusals_do_not_change_state(fault,code):
    s=state();r=req('hold',s)
    if fault=='version':r['expected_version']=10
    if fault=='role':r['actor_role']='unknown'
    if fault=='binding':s['current_binding']['minutes_revision']='changed'
    if fault=='policy':s['policy']['revision']='changed'
    if fault=='scope':s['synthetic_only']=False
    before=deepcopy(s);result=propose_lifecycle(s,r)
    assert result['code']==code and result['proposal'] is None and s==before


def test_duplicate_and_incomplete_components_refused():
    s=step(state(),'hold');r=req('return',s,request_id=s['history'][0]['request_id'])
    assert propose_lifecycle(s,r)['code']=='DUPLICATE_REQUEST'
    s=step(s,'record_response',response=response(components=['ask1']))
    assert propose_lifecycle(s,req('resolve',s,closure=closure()))['code']=='RESPONSE_COMPONENTS_UNCOVERED'
