"""Local shape/preservation checks, not native runtime proof."""
from copy import deepcopy
import re
import pytest
from scripts.f15_persistent_flow import build_persistent_lifecycle, schemas, FIELD
from scripts.f09_isolated_writer import REGISTER_FIELD_TYPES


def config():
    return dict(site='https://fictional-example.sharepoint.com/teams/Fictional',
        list_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',item_id=8,
        item_guid='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',title='FICTIONAL F15 lifecycle',
        legacy_id='FICTIONAL-F15-A1',entity_type='SP.Data.FictionalListItem',
        field_map={k:k for k in REGISTER_FIELD_TYPES},sharepoint_reference={
            'runtimeSource':'invoker','connection':{'connectionReferenceLogicalName':'existing_sharepoint'},
            'api':{'name':'shared_sharepointonline'}})


def build():
    return build_persistent_lifecycle({'name':'canonical','properties':{'state':'Stopped',
        'connectionReferences':{},'definition':{'parameters':{}}}},**config())


def walk(actions):
    for n,a in actions.items():
        yield n,a
        yield from walk(a.get('actions',{}))
        yield from walk(a.get('else',{}).get('actions',{}))


def test_single_field_conditional_write_and_full_native_source_readback():
    g=build();a=g['properties']['definition']['actions']
    writes=[x for _,x in walk(a) if x['type']=='OpenApiConnection' and x['inputs']['parameters']['parameters/method']!='GET']
    assert len(writes)==1
    w=writes[0]['inputs'];assert w['retryPolicy']=={'type':'none'}
    assert set(w['parameters']['parameters/body'])=={'__metadata',FIELD}
    assert w['parameters']['parameters/headers']['IF-MATCH']=="@triggerBody()?['expected_etag']"
    assert set(a['Native_source']['inputs'])==set(REGISTER_FIELD_TYPES)
    assert "body('Read_item')?['SourceRevision']" in a['Source_guard']['expression']
    assert 'register_revision' in a['Source_guard']['expression']
    assert "body('Read_saved')?['SourceRevision']" in a['Saved_guard']['expression']
    assert all(v in a['Saved_guard']['expression'] for v in REGISTER_FIELD_TYPES)
    assert g['name']=='canonical' and g['properties']['state']=='Stopped'


def test_response_closure_history_and_reopen_graph_present():
    a=build()['properties']['definition']['actions']
    for name in ('Response_guard','Closure_guard','Evidence_guard','Size_guard','Source_guard','Role_replay_guard'):
        assert next(iter(a[name]['else']['actions'].values()))['type']=='Terminate'
    assert 'minutes_revision' in a['Closure_guard']['expression']
    assert 'Unreviewed_responses' in a['Closure_guard']['expression']
    assert 'Coverage' in a['Closure_guard']['expression']
    assert 'Superseded' in a['Active_responses']['inputs']['where']
    assert 'prior_closure' in a['Event']['inputs']
    assert 'reopened' in a['Target_state']['inputs']
    assert "'reported_completion'" in a['Next_state']['inputs']
    assert "'history'" in a['Next_state']['inputs']
    assert a['Result']['inputs']['business_approval'] is False


def test_unique_names_references_sibling_dependencies_and_no_nested_terminate():
    a=build()['properties']['definition']['actions'];names=[n for n,_ in walk(a)]
    assert len(names)==len(set(names))
    def check(actions, in_loop=False, depth=1):
        assert depth<=8
        for n,x in actions.items():
            assert set(x.get('runAfter',{}))<=actions.keys(),n
            assert not (in_loop and x['type']=='Terminate')
            check(x.get('actions',{}),in_loop or x['type']=='Foreach',depth+1)
            check(x.get('else',{}).get('actions',{}),in_loop,depth+1)
    check(a)
    def strings(v):
        if isinstance(v,str):yield v
        elif isinstance(v,dict):
            for x in v.values():yield from strings(x)
        elif isinstance(v,list):
            for x in v:yield from strings(x)
    for text in strings(a):
        for name in re.findall(r"(?:body|outputs)\('([^']+)'\)",text):assert name in names,name


def test_schemas_do_not_use_unsupported_regex_features():
    def check(v):
        if isinstance(v,dict):
            assert 'pattern' not in v and 'patternProperties' not in v
            for x in v.values():check(x)
        elif isinstance(v,list):
            for x in v:check(x)
    for schema in schemas():check(schema)


def test_native_flow_rp_invoker_shape_is_preserved_exactly():
    cfg=config();cfg['sharepoint_reference']={'source':'Invoker',
        'connectionReferenceLogicalName':'existing_sharepoint',
        'id':'/providers/Microsoft.PowerApps/apis/shared_sharepointonline','tier':'Standard'}
    baseline={'properties':{'state':'Stopped','definition':{}}}
    result=build_persistent_lifecycle(baseline,**cfg)
    assert result['properties']['connectionReferences']['shared_sharepointonline']==cfg['sharepoint_reference']


@pytest.mark.parametrize('fault',['title','site','mapping','reference','state'])
def test_unqualified_inputs_refused_without_mutating_baseline(fault):
    cfg=config();b={'properties':{'state':'Stopped','definition':{}}}
    if fault=='title':cfg['title']='Real item'
    if fault=='site':cfg['site']='https://other.example/teams/test'
    if fault=='mapping':cfg['field_map']['Title']='SnapshotJson'
    if fault=='reference':cfg['sharepoint_reference']['runtimeSource']='embedded'
    if fault=='state':b['properties']['state']='Started'
    old=deepcopy(b)
    with pytest.raises(ValueError):build_persistent_lifecycle(b,**cfg)
    assert b==old
