"""Fictional H2 source rehearsals, without a store, native access or H2/F09 bridge."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from threading import Barrier
import pytest
from scripts.forum_configuration import resolve
from scripts.forum_compatibility import preparation_inputs, paper_candidate, calendar_inputs
from test_forum_compatibility import context, preparation, paper_baseline, paper_binding, calendar_fixture, digest
from test_meeting_commit_preview import case, run, bound_payload


def occurrence(index=0, second=False):
    p,s,_=context(index)
    if second:
        s['occurrence_ref']+='-SECOND';s['snapshot_revision']='s2';s['event']['event_ref']+='-SECOND'
        for k in ('start','end','window_start','window_end'):
            s[k]=(datetime.fromisoformat(s[k])+timedelta(days=7)).isoformat()
        s['event']['original_start']=s['start']
    observed={'state':'complete','sources':deepcopy(s['sources'])}
    r=resolve([p],s,observed_sources=observed);assert r['state']=='review_only'
    return p,s,dict(snapshot_json=r['snapshot_json'],expected_snapshot_sha256=r['snapshot_sha256'],observed_sources=observed)


def proposal(p,s):
    """Explicit caller mapping of fictional values; not production routing."""
    d,source,current,candidate,review=case()
    d['target']=current['target']=p['register_ref']
    current['item_id']=candidate['item_id']=s['occurrence_ref']+'-DECISION'
    source['source_ref']=candidate['source_ref']=s['occurrence_ref']+'-MINUTES'
    source['passage_ref']=candidate['passage_ref']=source['source_ref']+'#p1'
    return d,source,current,candidate,review


def key_history(c,key):
    d,_,current,candidate,review=c
    return [{'key':key,'binding':dict(destination={k:d[k]for k in ('target','schema_ref','use_ref','acceptance_ref','cutover_ref')},
        item_id=candidate['item_id'],before_version=current['version'],disposition=review['disposition'],payload=bound_payload(c))}]


def codes(r):return {b['code']for b in r['blockers']}


def assert_preview(r):
    assert r['preview_only'] and not r['committed']
    assert not any(r.get(k,False)for k in ('issued','assigned','notified','closed'))


def calendar(p,s,ctx):
    b,binding=calendar_fixture(p,s)
    for k in ('start','end'):
        b['event'][k]['dateTime']=datetime.fromisoformat(s[k]).astimezone(timezone.utc).replace(tzinfo=None).isoformat()
    return calendar_inputs(**ctx,baseline_text=json.dumps(b),binding=binding)


@pytest.mark.parametrize('field',['conditions','dissent','history','prior_history','action'])
def test_preview_edits_do_not_mutate_inputs_or_sibling_result(field):
    p,s,_=occurrence();c=proposal(p,s)
    if field=='prior_history':
        c[4]['prior_dispositions']=[dict(item_id=c[2]['item_id'],disposition='approve',wording=c[3]['wording'],notes=['Keep prior review'])]
    if field=='action':
        c[3]['kind']='action';c[3]['commission']=dict(explicit=True,authority_ref='FICTIONAL-COMMISSION',
            meeting_purpose='commission',owner_accepted=True,owner_ref='FICTIONAL-OWNER',owner_authority_ref='FICTIONAL-ROLE',
            owner_acceptance_ref='FICTIONAL-ACCEPTANCE',date_agreed=True,date_kind='due',date_value='2030-01-02',date_authority_ref='FICTIONAL-DATE')
    before=deepcopy(c);first=run(c);sibling=run(c);saved=deepcopy(sibling)
    assert first['state']=='APPROVED_PROPOSAL'
    if field in {'conditions','dissent'}:first['after'][field].append('Local proposed edit')
    elif field=='history':first['history'][0]['wording']='Local history edit'
    elif field=='prior_history':first['history'][1]['notes'].append('Local review edit')
    else:first['after']['action']['owner_ref']='FICTIONAL-OTHER-OWNER'
    assert c==before and sibling==saved and run(c)==saved


@pytest.mark.parametrize('kind',['prepare','paper','calendar','proposal'])
def test_overlapping_calls_isolate_two_forums_and_two_occurrences(kind):
    contexts=[occurrence(),occurrence(second=True),occurrence(1)];before=deepcopy(contexts)
    baseline=paper_baseline();baseline_before=deepcopy(baseline);gate=Barrier(9)
    def invoke(i):
        p,s,ctx=contexts[i%3];gate.wait(timeout=10)
        if kind=='prepare':r=preparation_inputs(**ctx,data=preparation(p,s))
        elif kind=='paper':r=paper_candidate(**ctx,baseline=baseline,expected_baseline_sha256=digest(baseline),binding=paper_binding(p,s))
        elif kind=='calendar':r=calendar(p,s,ctx)
        else:r=run(proposal(p,s))
        return i%3,r
    with ThreadPoolExecutor(max_workers=9) as pool:results=list(pool.map(invoke,range(9)))
    for i,r in results:
        assert r==next(x for j,x in results if i==j)
        if kind=='proposal':assert r['state']=='APPROVED_PROPOSAL';assert_preview(r)
        else:assert r['state']=='review_only' and not r['native_authority'] and not r['write_proposed']
    if kind=='prepare':
        assert len({r['payload']['meeting']for _,r in results})==3
        assert len({r['payload']['register']for _,r in results})==2
    if kind=='proposal':assert len({r['operation_key']for _,r in results})==3
    assert contexts==before and baseline==baseline_before


@pytest.mark.parametrize('when,revision,allowed',[
    ('2030-06-30T16:00:00+10:00','r1',True),('2030-07-01T00:00:00+10:00','r1',False),
    ('2030-06-30T16:00:00+10:00','r2',False),('2030-07-01T00:00:00+10:00','r2',True)])
def test_future_role_revision_requires_explicit_effective_selection(when,revision,allowed):
    p,s,ctx=occurrence();old=deepcopy(p);old['effective_until']='2030-07-01T00:00:00+10:00'
    new=deepcopy(p);new.update(profile_revision='r2',effective_from=old['effective_until'])
    new['roles']['chair']['role_ref']='FICTIONAL-FUTURE-CHAIR';before=deepcopy((old,new,ctx));start=datetime.fromisoformat(when)
    s.update(start=when,end=(start+timedelta(hours=1)).isoformat(),window_start=(start-timedelta(hours=1)).isoformat(),
             window_end=(start+timedelta(hours=2)).isoformat(),profile_revision=revision)
    r=resolve([old,new],s,observed_sources=ctx['observed_sources'])
    assert (r['state']=='review_only') is allowed
    if allowed:
        selected=json.loads(r['snapshot_json'])['profile']
        assert selected['roles']['chair']['role_ref']==(old if revision=='r1'else new)['roles']['chair']['role_ref']
        assert r['governance_state']=='unverified' and not r['native_authority']
    else:assert r['blockers']==['PROFILE_NOT_EFFECTIVE']
    assert (old,new,ctx)==before and json.loads(ctx['snapshot_json'])['profile']['profile_revision']=='r1'


@pytest.mark.parametrize('index,second',[(0,False),(0,True),(1,False)])
def test_replay_and_changed_payload_under_old_key_are_refused(index,second):
    p,s,_=occurrence(index,second);c=proposal(p,s);initial=run(c);history=key_history(c,initial['operation_key']);saved=deepcopy(history)
    duplicate=run(c,operation_keys=history);assert 'duplicate_operation'in codes(duplicate);assert_preview(duplicate)
    c[1]['passage_text']=c[3]['wording']='Fictional corrected source wording';c[4]['operation_key']=initial['operation_key']
    changed=run(c,operation_keys=history);assert 'operation_key_unbound'in codes(changed);assert_preview(changed)
    assert history==saved


@pytest.mark.parametrize('mode',['unknown','committed','conflict','partial','missing','extra'])
def test_unknown_or_partial_save_claim_never_permits_retry(mode):
    p,s,_=occurrence();c=proposal(p,s);target=c[0]['target'];c[3]['recovery_targets']=[target,'FICTIONAL-MINUTES']
    observed={target:'absent','FICTIONAL-MINUTES':'absent'}
    if mode=='partial':observed[target]='committed'
    elif mode=='missing':del observed[target]
    elif mode=='extra':observed['FICTIONAL-UNEXPECTED']='absent'
    else:observed['FICTIONAL-MINUTES']=mode
    before=deepcopy((c,observed));r=run(c,recovery=observed)
    assert r['state']=='BLOCKED' and codes(r)&{'reconciliation_required','recovery_targets_incomplete'}
    assert_preview(r);assert (c,observed)==before


def test_declared_absence_after_unknown_is_still_only_a_preview():
    p,s,_=occurrence();c=proposal(p,s);target=c[0]['target'];initial=run(c)
    assert run(c,recovery={target:'unknown'})['state']=='BLOCKED'
    absent=run(c,recovery={target:'absent'});assert absent==initial;assert_preview(absent)
    assert run(c,recovery={target:'committed'})['state']=='BLOCKED'


@pytest.mark.parametrize('boundary',['destination','register','paper-context','calendar-context'])
def test_wrong_target_blocks_without_changing_another_forum(boundary):
    p,s,ctx=occurrence();op,os,oc=occurrence(1);before=deepcopy((op,os,oc))
    if boundary=='destination':
        c=proposal(p,s);c[0]['target']=op['register_ref'];r=run(c);assert 'destination_mismatch'in codes(r)
    elif boundary=='register':
        data=preparation(p,s);data['register']=op['register_ref'];r=preparation_inputs(**ctx,data=data)
    elif boundary=='paper-context':
        base=paper_baseline();r=paper_candidate(**ctx,baseline=base,expected_baseline_sha256=digest(base),binding=paper_binding(op,os))
    else:
        b,binding=calendar_fixture(op,os);r=calendar_inputs(**ctx,baseline_text=json.dumps(b),binding=binding)
    assert r['state'].lower()=='blocked' and (op,os,oc)==before


@pytest.mark.parametrize('change',['revision','sha256','denied','incomplete','missing'])
def test_source_drift_or_unverified_read_claim_blocks_snapshot(change):
    p,s,ctx=occurrence();before=deepcopy((p,s))
    if change in {'revision','sha256'}:ctx['observed_sources']['sources'][0][change]='v2'if change=='revision'else'c'*64
    elif change=='missing':ctx['observed_sources']['sources']=[]
    else:ctx['observed_sources']['state']=change
    r=preparation_inputs(**ctx,data=preparation(p,s));assert r['state']=='blocked' and r['payload']is None and (p,s)==before


@pytest.mark.parametrize('kind',['occurrence','exception','cancelled'])
def test_moved_time_original_occurrence_and_cancellation_are_preserved(kind):
    p,s,_=occurrence();s['event']['type']='exception'if kind=='exception'else'occurrence';original=s['event']['original_start']
    if kind=='exception':
        for k in ('start','end'):s[k]=(datetime.fromisoformat(s[k])+timedelta(hours=1)).isoformat()
    s['event']['cancelled']=kind=='cancelled';observed={'state':'complete','sources':deepcopy(s['sources'])}
    r=resolve([p],s,observed_sources=observed)
    if kind=='cancelled':assert r['blockers']==['CANCELLED_OCCURRENCE'] and r['snapshot_json']is None
    else:
        ctx=dict(snapshot_json=r['snapshot_json'],expected_snapshot_sha256=r['snapshot_sha256'],observed_sources=observed)
        result=calendar(p,s,ctx);assert result['state']=='review_only'
        event=json.loads(result['payload']['baseline_text'])['event'];assert event['originalStart']==original and event['type']==kind
        assert s['event']['original_start']==original


def test_correction_retains_prior_source_output_and_other_forum_versions():
    p,s,_=occurrence();c=proposal(p,s);op,os,_=occurrence(1);other=proposal(op,os);other_before=deepcopy(other)
    original=run(c);original_before=deepcopy(original);c[2]['issued']=True
    c[4].update(disposition='amend',replacement_wording='Fictional corrected wording',amendment_authority_ref='FICTIONAL-AMENDMENT')
    assert 'issued_record_immutable'in codes(run(c))
    c[4].update(issued_record_correction_ref='FICTIONAL-CORRECTION-ROUTE',correction_ref='FICTIONAL-CORRECTION',
                prior_dispositions=deepcopy(original['history'][-1:]))
    corrected=run(c);assert corrected['state']=='AMENDED_PROPOSAL'
    assert corrected['before']['wording']==original['after']['wording'] and corrected['after']['wording']==c[4]['replacement_wording']
    assert corrected['operation_key']!=original['operation_key'] and corrected['source']==original['source']
    assert len(corrected['history'])==len(original['history'])+1 and original==original_before and other==other_before
    assert_preview(corrected)


def test_shared_input_concurrent_preview_edits_are_isolated_without_atomic_reservation():
    p,s,_=occurrence();c=proposal(p,s);before=deepcopy(c);gate=Barrier(6)
    def inspect(i):
        gate.wait(timeout=10);r=run(c);r['history'][0]['wording']='Local edit '+str(i)
        r['after']['conditions'].append('Local condition '+str(i));return r
    with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(inspect,range(6)))
    assert c==before
    assert len({r['operation_key']for r in results})==1
    for i,r in enumerate(results):
        assert r['history'][0]['wording']=='Local edit '+str(i)
        assert r['after']['conditions']==before[1]['conditions']+['Local condition '+str(i)]
        assert_preview(r)
    # The pure preview has no shared ledger/lock: identical concurrent previews
    # are allowed. This is not exactly-once reservation or native concurrency proof.


@pytest.mark.parametrize('index,second',[(0,False),(0,True),(1,False)])
def test_tampered_binding_for_existing_operation_key_requires_reconciliation(index,second):
    p,s,_=occurrence(index,second);c=proposal(p,s);initial=run(c)
    history=key_history(c,initial['operation_key']);history[0]['binding']['destination']['target']='FICTIONAL-WRONG-REGISTER'
    before=deepcopy(history);result=run(c,operation_keys=history)
    assert 'operation_key_reused'in codes(result) and result['state']=='BLOCKED'
    assert_preview(result);assert history==before


def test_unaccepted_destination_claim_cannot_be_promoted_by_forum_resolution():
    p,s,ctx=occurrence();assert json.loads(ctx['snapshot_json'])['profile']['governance']['state']=='unverified'
    c=proposal(p,s);c[0]['accepted']=False
    result=run(c);assert 'destination_unaccepted'in codes(result);assert_preview(result)
    # Neither this declaration nor a profile authenticates actual target audience.
