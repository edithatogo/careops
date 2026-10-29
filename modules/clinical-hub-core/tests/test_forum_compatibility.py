"""Pure adapter equivalence and refusal tests; no native configuration is read."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

import pytest

from scripts.forum_configuration import resolve
from scripts.forum_compatibility import (
    preparation_inputs, next_preparation_inputs, paper_candidate, calendar_inputs,
)
from scripts.preparation_cycle import validate, next_cycle
from scripts.f07_operator_inputs import build_operator_inputs
from scripts.f12_configuration import validate_configuration


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def context(index=0):
    x=json.loads((Path(__file__).parent/'fixtures/forum_profiles/two_forums.json').read_text())
    s=x['selections'][index];p=x['profiles'][index]
    observed={'state':'complete','sources':deepcopy(s['sources'])}
    r=resolve(x['profiles'],s,observed_sources=observed)
    return p,s,dict(snapshot_json=r['snapshot_json'],expected_snapshot_sha256=r['snapshot_sha256'],observed_sources=observed)


def preparation(p,s):
    return dict(cycle='FICTIONAL-CYCLE',meeting=s['occurrence_ref'],priorities='Unresolved fictional input',
                pack=s['sources'][0]['source_ref'],register=p['register_ref'],previous_cycle=None,
                controls={k:dict(state='Ready for chair review',note='Keep this human note',source='FICTIONAL-SOURCE')for k in p['control_keys']})


def paper_baseline():
    guard={'actions':{'Parse_manifest':{'inputs':{}},'Check_unique_identifiers':{'actions':{
        'For_each_paper':{'actions':{'Check_paper_binding':{'actions':{
            'Get_paper_metadata':{'inputs':{'parameters':{}}},
            'Check_reviewed_etag':{'actions':{'Append_match':{'inputs':{'value':{}}}},
                                   'else':{'actions':{'Append_review_drift':{'inputs':{'value':{}}}}}}
        }}}},'Manifest_results':{'inputs':{'paper_readiness':False}}
    }}},'else':{'actions':{'Stop_missing_manifest_input':{'inputs':{}}}}}
    return {'name':'FICTIONAL-EXISTING-F07','properties':{'displayName':'Fictional paper check','state':'Stopped',
        'definition':{'triggers':{'manual':{'inputs':{}}},'actions':{'Check_manifest_input':guard,'Initialize_expected_count':{}}},
        'connectionReferences':{'existing':{'source':'Invoker','id':'FICTIONAL-CONNECTION'}}}}


def paper_binding(p,s):
    pin=s['sources'][0]
    return dict(forum_ref=p['forum_ref'],occurrence_ref=s['occurrence_ref'],binding_ref=p['binding_ref'],
                source_ref=pin['source_ref'],site='https://fictional-example.sharepoint.com/teams/Fictional',
                path='/Shared Documents/'+pin['name'],name=pin['name'],version=pin['revision'],
                etag='"fictional-native-etag"',sha256=pin['sha256'])


def calendar_fixture(p,s):
    pin=s['sources'][0]
    binding=dict(forum_ref=p['forum_ref'],occurrence_ref=s['occurrence_ref'],binding_ref=p['binding_ref'],
                 event_ref=s['event']['event_ref'],event_id='fictional-native-event-'+p['forum_ref']+'==',
                 series_ref=s['event']['series_ref'],series_id='fictional-native-series-'+p['forum_ref']+'==',
                 agenda_ref=pin['source_ref'],agenda_id='fictional-native-attachment-'+p['forum_ref']+'==',
                 agenda_revision=pin['revision'],agenda_sha256=pin['sha256'])
    b=dict(event=dict(id=binding['event_id'],originalStart=s['event']['original_start'],seriesMasterId=binding['series_id'],
        iCalUId='FICTIONAL-ICAL',subject=s['event']['subject'],type=s['event']['type'],
        organizer={'emailAddress':{'address':s['event']['organizer']}},
        start={'dateTime':'2030-02-04T06:00:00','timeZone':'UTC'},end={'dateTime':'2030-02-04T07:00:00','timeZone':'UTC'},
        changeKey='FICTIONAL-CHANGE',lastModifiedDateTime='2030-02-01T00:00:00Z',isCancelled=False),
        agenda=dict(id=binding['agenda_id'],name=pin['name'],size=20,lastModifiedDateTime='2030-02-01T00:00:00Z',
                    contentType='application/docx',**{'@odata.type':'#fixture.attachment'},isInline=False),
        checked_at='2030-02-01T00:00:00Z',baseline_run_id='FICTIONAL-RUN')
    return b,binding


@pytest.mark.parametrize('index',[0,1])
def test_preparation_and_carry_forward_equal_legacy_without_mutation(index):
    p,s,c=context(index);d=preparation(p,s);before=deepcopy((c,d))
    result=preparation_inputs(**c,data=d)
    assert result['state']=='review_only'
    assert result['payload']==validate(deepcopy(d),control_keys=p['control_keys'])
    carried=next_preparation_inputs(**c,data=d,cycle='FICTIONAL-NEXT',previous_ref='FICTIONAL-PRIOR')
    assert carried['payload']==next_cycle(d,'FICTIONAL-NEXT','FICTIONAL-PRIOR',control_keys=p['control_keys'])
    assert carried['payload']['meeting']=='To confirm'
    assert carried['payload']['priorities']=='To confirm'
    assert carried['payload']['controls'][p['control_keys'][0]]['state']=='Not started'
    assert (c,d)==before
    result['payload']['controls'][p['control_keys'][0]]['note']='Local result edit'
    assert d==before[1]
    for r in (result,carried):assert not r['native_authority'] and not r['write_proposed']


@pytest.mark.parametrize('index',[0,1])
def test_f07_candidate_matches_legacy_and_preserves_complete_identity_references(index):
    p,s,c=context(index);base=paper_baseline();binding=paper_binding(p,s);before=deepcopy((c,base,binding))
    result=paper_candidate(**c,baseline=base,expected_baseline_sha256=digest(base),binding=binding)
    kwargs={k:binding[k]for k in ['site','path','name','version','etag']};kwargs['paper_ref']=binding['source_ref']
    expected=build_operator_inputs(base,**kwargs)
    assert result['state']=='review_only' and result['payload']==expected
    assert (c,base,binding)==before
    for k,v in base.items():
        if k!='properties':assert result['payload'][k]==v
    for k,v in base['properties'].items():
        if k!='definition':assert result['payload']['properties'][k]==v
    inner=result['payload']['properties']['definition']['actions']['Check_manifest_input']['actions']['Check_unique_identifiers']['actions']
    assert inner['Manifest_results']['inputs']['paper_readiness'] is False
    assert inner['Manifest_results']['inputs']['meeting_ref'].startswith('Not confirmed')


@pytest.mark.parametrize('index',[0,1])
def test_f12_payload_reuses_unchanged_full_validator_and_exact_raw_baseline(index):
    p,s,c=context(index);base,binding=calendar_fixture(p,s);text=json.dumps(base,indent=1);before=deepcopy((c,binding,text))
    result=calendar_inputs(**c,baseline_text=text,binding=binding)
    assert result['state']=='review_only'
    assert result['payload']['baseline_text']==text
    assert validate_configuration(**result['payload'])==result['legacy_validation']
    assert result['legacy_validation']['comparison_fields']==21
    assert (c,binding,text)==before
    assert not result['native_authority'] and not result['write_proposed']


@pytest.mark.parametrize('field',['meeting','pack','register'])
def test_preparation_cross_context_is_blocked(field):
    p,s,c=context();data=preparation(p,s);data[field]='FICTIONAL-OTHER-FORUM'
    assert preparation_inputs(**c,data=data)['state']=='blocked'


@pytest.mark.parametrize('mode',['digest','json','derived','observed','capability','duplicate-json'])
def test_context_is_revalidated_not_taken_from_mutable_result_flags(mode):
    p,s,c=context();data=preparation(p,s)
    if mode=='digest':c['expected_snapshot_sha256']='0'*64
    if mode=='json':c['snapshot_json']='not-json';c['expected_snapshot_sha256']=hashlib.sha256(b'not-json').hexdigest()
    if mode=='derived':c['approved']=True
    if mode=='observed':c['observed_sources']['state']='incomplete'
    if mode=='capability':
        snap=json.loads(c['snapshot_json']);snap['selection']['capabilities']=['compare_calendar'];c['snapshot_json']=json.dumps(snap,sort_keys=True,separators=(',',':'));c['expected_snapshot_sha256']=hashlib.sha256(c['snapshot_json'].encode()).hexdigest()
    if mode=='duplicate-json':
        c['snapshot_json']='{"profile":{},"profile":{},"selection":{}}';c['expected_snapshot_sha256']=hashlib.sha256(c['snapshot_json'].encode()).hexdigest()
    if mode=='derived':
        with pytest.raises(TypeError):preparation_inputs(**c,data=data)
    else:
        r=preparation_inputs(**c,data=data)
        assert r['state']=='blocked' and r['payload'] is None


@pytest.mark.parametrize('field',['forum_ref','occurrence_ref','binding_ref','source_ref','name','version','sha256','site','path','etag'])
def test_f07_bad_or_wrong_source_bindings_are_blocked(field):
    p,s,c=context();base=paper_baseline();binding=paper_binding(p,s)
    binding[field]={'site':'https://attacker.example.invalid','path':'/../wrong','etag':''}.get(field,'wrong')
    r=paper_candidate(**c,baseline=base,expected_baseline_sha256=digest(base),binding=binding)
    assert r['state']=='blocked' and r['payload'] is None


def test_f07_started_or_stale_baseline_refused_without_saving():
    p,s,c=context();base=paper_baseline();binding=paper_binding(p,s)
    assert paper_candidate(**c,baseline=base,expected_baseline_sha256='0'*64,binding=binding)['state']=='blocked'
    base['properties']['state']='Started'
    assert paper_candidate(**c,baseline=base,expected_baseline_sha256=digest(base),binding=binding)['state']=='blocked'


@pytest.mark.parametrize('field',['id','seriesMasterId','originalStart','type','isCancelled','start','end'])
def test_f12_shape_valid_but_different_occurrence_is_refused(field):
    p,s,c=context();base,binding=calendar_fixture(p,s)
    replacements={'originalStart':'2030-01-28T06:00:00Z','type':'exception','isCancelled':True,
                  'start':{'dateTime':'2030-02-04T06:15:00','timeZone':'UTC'},
                  'end':{'dateTime':'2030-02-04T07:15:00','timeZone':'UTC'}}
    base['event'][field]=replacements.get(field,'FICTIONAL-DIFFERENT')
    assert calendar_inputs(**c,baseline_text=json.dumps(base),binding=binding)['state']=='blocked'


@pytest.mark.parametrize('field',['forum_ref','occurrence_ref','binding_ref','event_ref','event_id','series_ref','series_id','agenda_ref','agenda_id','agenda_revision','agenda_sha256'])
def test_f12_mapping_cannot_silently_cross_forum_or_source(field):
    p,s,c=context();base,binding=calendar_fixture(p,s);binding[field]='FICTIONAL-WRONG'
    assert calendar_inputs(**c,baseline_text=json.dumps(base),binding=binding)['state']=='blocked'


def test_f12_missing_fields_and_oversize_raw_baseline_remain_legacy_errors():
    p,s,c=context();base,binding=calendar_fixture(p,s);del base['event']['changeKey']
    assert calendar_inputs(**c,baseline_text=json.dumps(base),binding=binding)['state']=='blocked'
    base,binding=calendar_fixture(p,s)
    assert calendar_inputs(**c,baseline_text=' '*2001+json.dumps(base),binding=binding)['state']=='blocked'


def test_f12_preserves_exception_but_does_not_invent_unsupported_single_instance_metadata():
    x=json.loads((Path(__file__).parent/'fixtures/forum_profiles/two_forums.json').read_text());p=x['profiles'][0];s=x['selections'][0]
    s['event'].update(type='exception',original_start='2030-01-28T16:00:00+10:00')
    observed={'state':'complete','sources':s['sources']};r=resolve(x['profiles'],s,observed_sources=observed)
    c=dict(snapshot_json=r['snapshot_json'],expected_snapshot_sha256=r['snapshot_sha256'],observed_sources=observed)
    base,binding=calendar_fixture(p,s)
    assert calendar_inputs(**c,baseline_text=json.dumps(base),binding=binding)['state']=='review_only'
    s['event'].update(type='singleInstance',series_ref=None,original_start=None)
    r=resolve(x['profiles'],s,observed_sources=observed);c.update(snapshot_json=r['snapshot_json'],expected_snapshot_sha256=r['snapshot_sha256'])
    assert calendar_inputs(**c,baseline_text=json.dumps(base),binding=binding)['state']=='blocked'


def test_cross_forum_bindings_and_stale_source_observations_do_not_produce_payloads():
    p,s,c=context();other_p,other_s,_=context(1);base=paper_baseline()
    r=paper_candidate(**c,baseline=base,expected_baseline_sha256=digest(base),binding=paper_binding(other_p,other_s))
    assert r['state']=='blocked' and r['payload'] is None
    b,_=calendar_fixture(p,s);_,other=calendar_fixture(other_p,other_s)
    assert calendar_inputs(**c,baseline_text=json.dumps(b),binding=other)['state']=='blocked'
    c['observed_sources']['sources'][0]['sha256']='0'*64
    assert preparation_inputs(**c,data=preparation(p,s))['state']=='blocked'


def test_legacy_direct_entry_points_remain_available_without_forum_context():
    p,s,_=context();data=preparation(p,s)
    assert validate(data,control_keys=p['control_keys'])==data
    base,binding=calendar_fixture(p,s)
    selection=dict(window_start=s['window_start'],window_end=s['window_end'],subject=s['event']['subject'],
                   organizer=s['event']['organizer'],agenda_name=s['sources'][0]['name'])
    assert validate_configuration(json.dumps(base),json.dumps(selection))['status']=='PASS'


@pytest.mark.parametrize('state',['unverified','draft','conflicting','recorded'])
def test_h1_governance_assertions_never_promote_source_candidate_to_native_authority(state):
    x=json.loads((Path(__file__).parent/'fixtures/forum_profiles/two_forums.json').read_text())
    p=x['profiles'][0];s=x['selections'][0]
    p['governance']={'state':state,'source_ref':'FICTIONAL-EVIDENCE'if state=='recorded'else None}
    observed={'state':'complete','sources':s['sources']};r=resolve(x['profiles'],s,observed_sources=observed)
    c=dict(snapshot_json=r['snapshot_json'],expected_snapshot_sha256=r['snapshot_sha256'],observed_sources=observed)
    result=paper_candidate(**c,baseline=paper_baseline(),expected_baseline_sha256=digest(paper_baseline()),binding=paper_binding(p,s))
    assert result['state']=='review_only' and result['preview_only']
    assert not result['native_authority'] and not result['write_proposed']


def test_adapter_module_imports_only_known_pure_legacy_functions_and_standard_parsers():
    import ast
    tree=ast.parse((Path(__file__).parents[1]/'scripts/forum_compatibility.py').read_text())
    modules={n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)}
    modules|={a.name for n in ast.walk(tree)if isinstance(n,ast.Import)for a in n.names}
    assert modules <= {'copy','hashlib','json','urllib.parse','scripts.forum_configuration',
                       'scripts.preparation_cycle','scripts.f07_operator_inputs','scripts.f12_configuration'}
    calls={n.func.id for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)}
    assert not calls & {'open','exec','eval','compile','__import__'}


@pytest.mark.parametrize('site',[1,True,[],{}])
def test_nontext_source_site_is_blocked_without_parser_exception(site):
    p,s,c=context();base=paper_baseline();binding=paper_binding(p,s);binding['site']=site
    assert paper_candidate(**c,baseline=base,expected_baseline_sha256=digest(base),binding=binding)['state']=='blocked'


def test_overdeep_snapshot_is_blocked_without_recursion_exception():
    p,s,c=context();c['snapshot_json']='{"profile":'+'['*1100+'0'+']'*1100+',"selection":{}}'
    c['expected_snapshot_sha256']=hashlib.sha256(c['snapshot_json'].encode()).hexdigest()
    assert preparation_inputs(**c,data=preparation(p,s))['state']=='blocked'
