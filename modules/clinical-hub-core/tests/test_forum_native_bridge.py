# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Fictional bridge compilation invariants, not cloud runtime acceptance."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import pytest
from scripts.forum_native_bridge import build_bridge,DISPLAY_NAME
from scripts.forum_native_mapping import map_package
from test_forum_native_mapping import sample,LIB


def bindings():
    d=sample();package=map_package(**d)['package']
    return dict(site='https://fictional-example.sharepoint.com/teams/Qualification',library_id=LIB,library_scope='/teams/Qualification/Existing Library',principal='operator@example.invalid',sharepoint_reference=dict(source='Invoker',tier='Standard',id='/providers/Microsoft.PowerApps/apis/shared_sharepointonline',connectionReferenceLogicalName='fictional_sharepoint_reference',connectionName='fictional-existing-sharepoint-connection'),runtime_url='https://fictional.common.australia.azure-apihub.net/apim/sharepointonline',qualified_packages=[dict(package=package,native=dict(item_id=100,file_id='99999999-1111-4111-8111-111111111111',file_etag='"fictional-package,1"',item_etag='"1"',version='1.0',name=package['package_name']))])


def walk(actions):
    for name,action in actions.items():
        yield name,action
        for branch in [action,action.get('else',{})]:
            yield from walk(branch.get('actions',{}))


def test_one_native_selected_file_bridge_stopped_and_existing_reference_unchanged():
    d=bindings();original=deepcopy(d);r=build_bridge(**d);assert d==original
    p=r['properties'];definition=p['definition'];t=definition['triggers']['manual']
    assert p['displayName']==DISPLAY_NAME and p['state']=='Stopped'
    assert 'flowFailureAlertSubscribed'not in p  # Ignored on create; native gate remains.
    assert p['connectionReferences']=={'shared_sharepointonline':d['sharepoint_reference']}
    assert t['type']=='Request' and t['kind']=='ApiConnection'
    assert t['inputs']['operationId']=='ForASelectedFileHybridTrigger'
    assert set(t['inputs']['host'])=={'connection'}  # Native save omits legacy host.api.
    assert t['inputs']['parameters']=={'dataset':d['site'],'table':LIB}
    choices=t['inputs']['schema']['properties']['rows']['items']['properties']
    assert choices['purpose']['enum']==['Preparation review','Calendar comparison inputs']
    assert set(choices)=={'purpose','entity'}
    assert t['runtimeConfiguration']['concurrency']['runs']==1


def test_only_one_create_only_receipt_write_no_send_source_or_business_writes():
    d=bindings();definition=build_bridge(**d)['properties']['definition']
    connectors=[(n,a)for n,a in walk(definition['actions'])if a['type']=='OpenApiConnection']
    writes=[]
    for name,a in connectors:
        i=a['inputs'];assert i['host']['operationId']=='HttpRequest'
        assert i['host']['connectionName']=='shared_sharepointonline'
        assert i['parameters']['dataset']==d['site'] and i['retryPolicy']=={'type':'none'}
        assert 'authentication'not in i
        if i['parameters']['parameters/method']!='GET':writes.append((name,i))
    assert len(writes)==1 and writes[0][0]=='Create_receipt'
    assert 'overwrite=false'in writes[0][1]['parameters']['parameters/uri']
    text=json.dumps(definition);assert all(s not in text for s in ['SendEmail','Recurrence','shared_office365','RunScript','shared_wordonlinebusiness','shared_commondataserviceforapps'])


def test_drift_package_identity_and_conflict_checks_precede_receipt_creation():
    a=build_bridge(**bindings())['properties']['definition']['actions']
    assert set(a['Find_package']['inputs'])=={'from','where'}
    assert "['occurrence_version']"in a['Find_package']['inputs']['where']
    assert "['item_etag']"in a['Check_native_pins']['actions']['Pin_matches']['expression']
    assert "['file_etag']"in a['Check_native_pins']['actions']['Pin_matches']['expression']
    assert a['Package_body_guard']['expression']=="@equals(outputs('Package_body'),outputs('Selected_package')?['package'])"
    assert a['Receipt_core']['runAfter']=={'Pin_guard':['Succeeded']}
    assert a['New_receipt']['runAfter']=={'Receipt_count_guard':['Succeeded']}
    assert all(a['Receipt_core']['inputs'][k]is False for k in ['native_authority','send_authority','activation_authority'])
    assert a['Create_if_absent']['expression']=="@empty(body('Find_receipt')?['value'])"
    assert a['Read_saved_receipt']['runAfter']=={'Create_if_absent':['Succeeded','Failed','TimedOut']}
    assert "['core'],outputs('Receipt_core')"in a['Receipt_readback_guard']['expression']
    assert a['Check_native_pins']['runtimeConfiguration']['concurrency']['repetitions']==1
    error=a['Check_native_pins']['actions']['Pin_matches']['else']['actions']['Record_pin_error']
    assert error['inputs']['value']=="@items('Check_native_pins')"


def test_injected_expression_text_is_quoted_inside_json_expression_not_interpreted():
    d=sample();d['profile']['H2Purpose']="Fictional @{concat('do','not','execute')} and O'Brien"
    b=bindings();p=map_package(**d)['package'];b['qualified_packages'][0]['package']=p;b['qualified_packages'][0]['native']['name']=p['package_name']
    data=build_bridge(**b)['properties']['definition']['actions']['Qualified_packages']['inputs']
    text=data[0]['package']['payload']['snapshot']['profile']['purpose']
    assert text.startswith("@string('")and text.endswith("')")
    inner=text[len("@string('"):-2].replace("''", "'")
    assert inner==d['profile']['H2Purpose']
    def literals(value):
        if isinstance(value,str):yield value
        elif isinstance(value,list):
            for v in value:yield from literals(v)
        elif isinstance(value,dict):
            for v in value.values():yield from literals(v)
    assert all(v.startswith("@string('")and v.endswith("')")and len(v)<=8192 for v in literals(data))


@pytest.mark.parametrize('case',['http-site','foreign-domain','site-query','site-userinfo','site-path','folder-outside','folder-traversal','folder-quote','runtime-domain','runtime-query','principal','embedded','premium','new-connector','reference-extra','missing-logical-ref','missing-physical-ref','physical-ref-url','physical-ref-object','catalog-empty','catalog-extra','wrong-library','wrong-native-name','native-item-bool','native-id-zero','native-etag-empty','native-version','duplicate-catalog','source-package-collision','body-change','unqualified-authority'])
def test_unqualified_or_ambiguous_binding_refuses(case):
    b=bindings();e=b['qualified_packages'][0]
    if case=='http-site':b['site']=b['site'].replace('https:','http:')
    elif case=='foreign-domain':b['site']=b['site'].replace('fictional-example.sharepoint.com','example.invalid')
    elif case=='site-query':b['site']+='?x=1'
    elif case=='site-userinfo':b['site']=b['site'].replace('https://','https://user@')
    elif case=='site-path':b['site']+='/Documents'
    elif case=='folder-outside':b['library_scope']='/teams/Other/Library'
    elif case=='folder-traversal':b['library_scope']+='/../Other'
    elif case=='folder-quote':b['library_scope']+="'"
    elif case=='runtime-domain':b['runtime_url']='https://example.invalid/apim/sharepointonline'
    elif case=='runtime-query':b['runtime_url']+='?token=fictional'
    elif case=='principal':b['principal']='not-selected'
    elif case=='embedded':b['sharepoint_reference']['source']='Embedded'
    elif case=='premium':b['sharepoint_reference']['tier']='Premium'
    elif case=='new-connector':b['sharepoint_reference']['id']='new-client'
    elif case=='reference-extra':b['sharepoint_reference']['authentication']='fictional'
    elif case=='missing-logical-ref':b['sharepoint_reference'].pop('connectionReferenceLogicalName')
    elif case=='missing-physical-ref':b['sharepoint_reference'].pop('connectionName')
    elif case=='physical-ref-url':b['sharepoint_reference']['connectionName']='https://example.invalid/new-connection'
    elif case=='physical-ref-object':b['sharepoint_reference']['connectionName']={}
    elif case=='catalog-empty':b['qualified_packages']=[]
    elif case=='catalog-extra':e['approved']=True
    elif case=='wrong-library':b['library_id']='22222222-1111-4111-8111-111111111111'
    elif case=='wrong-native-name':e['native']['name']='other.json'
    elif case=='native-item-bool':e['native']['item_id']=True
    elif case=='native-id-zero':e['native']['file_id']='00000000-0000-0000-0000-000000000000'
    elif case=='native-etag-empty':e['native']['file_etag']=''
    elif case=='native-version':e['native']['version']='latest'
    elif case=='duplicate-catalog':b['qualified_packages'].append(deepcopy(e))
    elif case=='source-package-collision':e['native']['item_id']=1
    elif case=='body-change':e['package']['canonical_json']+=' '
    elif case=='unqualified-authority':e['package']['canonical_json']=e['package']['canonical_json'].replace('"native_authority":false','"native_authority":true')
    with pytest.raises(ValueError):build_bridge(**b)


def test_compiler_has_no_native_auth_or_io_imports():
    source=(Path(__file__).parents[1]/'scripts/forum_native_bridge.py').read_text();tree=ast.parse(source)
    names={n.names[0].name.split('.')[0]for n in ast.walk(tree)if isinstance(n,ast.Import)}
    assert names<={'json','re','xml'}
    assert not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in {'open','eval','exec','__import__'}for n in ast.walk(tree))



def test_owned_schema_is_checked_before_any_package_or_receipt_use():
    a=build_bridge(**bindings())['properties']['definition']['actions']
    assert a['Qualified_packages']['runAfter']=={'Schema_guard':['Succeeded']}
    assert a['Read_owned_schema']['inputs']['parameters']['parameters/method']=='GET'
    assert "/fields?$select=Id,InternalName,StaticName,TypeAsString,Required,ReadOnlyField,Hidden,SchemaXml"in a['Read_owned_schema']['inputs']['parameters']['parameters/uri']
    assert a['Schema_guard']['expression']=="@empty(variables('Schema_errors'))"
    assert a['Check_owned_schema']['runtimeConfiguration']['concurrency']['repetitions']==1
    present=a['Check_owned_schema']['actions']['Field_present']
    assert present['expression']=="@equals(length(body('Find_owned_field')),1)"
    expr=present['actions']['Field_matches']['expression']
    assert all(v in expr for v in ["['InternalName']","['StaticName']","['Required']","['ReadOnlyField']","['Hidden']","['TypeAsString']","xpath(xml("])
    assert 'odata.nextLink'in a['Schema_page_guard']['expression']
    assert a['Read_owned_schema']['inputs']['retryPolicy']=={'type':'none'}


def test_all_owned_fields_and_exact_lookup_choices_are_pinned():
    from scripts.forum_native_bridge import _schema_pins
    pins=_schema_pins(LIB);assert len(pins)==32 and len({p['id']for p in pins})==32
    by_name={p['name']:p for p in pins}
    lookup=by_name['H2Profile']
    assert LIB in lookup['predicate'] and "/Field/@ShowField='Title'"in lookup['predicate']
    assert "not(/Field/@Mult='TRUE')"in lookup['predicate']
    multiple=by_name['H2Sources']
    assert multiple['kind']=='LookupMulti'and "/Field/@Mult='TRUE'"in multiple['predicate']
    assert "count(/Field/CHOICES/CHOICE)=4"in by_name['H2Controls']['predicate']
    assert "/Field/Default='Unverified'"in by_name['H2GovernanceState']['predicate']
    assert by_name['H2EventRef']['hidden']is True
    assert 'Title'not in by_name  # The existing default field is not owned by H2.
