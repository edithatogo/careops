"""Fictional maker-package inputs are models, never native auth/save evidence."""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import ast
import hashlib
import json
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL
import pytest
from scripts.forum_native_package import build_package

LIB='11111111-1111-4111-8111-111111111111'
OTHER='22222222-2222-4222-8222-222222222222'


def sample(index=0):
    x=json.loads((Path(__file__).parent/'fixtures/forum_profiles/two_forums.json').read_text());s=x['selections'][index]
    pairs=[('profile',s['forum_ref'],'e'*64),('occurrence',s['occurrence_ref'],'f'*64)]+[('source',v['source_ref'],v['sha256'].lower())for v in s['sources']]
    pins=[dict(role=role,ref=ref,list_id=LIB,item_id=i+1,file_id=str(uuid5(NAMESPACE_URL,'https://fictional.invalid/'+role+'/'+ref)),item_etag='"1"',file_etag='"fictional,1"',file_version='1.0',sha256=sha)for i,(role,ref,sha)in enumerate(pairs)]
    return dict(profiles=x['profiles'],selection=s,observed_sources={'state':'complete','sources':deepcopy(s['sources'])},native_pins=pins,purpose='preparation-review',output_revision=1)


def build(data):
    return build_package(**data)


def test_package_reuses_resolver_and_preserves_snapshot_without_granting_authority():
    d=sample();before=deepcopy(d);r=build(d);packet=json.loads(r['canonical_json']);assert d==before
    assert hashlib.sha256(r['canonical_json'].encode()).hexdigest()==r['sha256']
    assert packet['payload']['snapshot']=={'profile':d['profiles'][0],'selection':d['selection']}
    assert packet['state']=='candidate'and packet['review_only']is True
    assert all(packet[k]is False for k in ['native_authority','send_authority','activation_authority'])
    assert r['package_name'].startswith('H2-package-')and r['receipt_name'].startswith('H2-receipt-')
    assert packet['payload']['preparation_control_keys']==['papers','review']


def test_pin_order_has_no_effect_but_changed_etag_is_same_operation_conflict():
    d=sample();r=build(d);d['native_pins'].reverse();assert build(d)==r
    d['native_pins'][0]['file_etag']='"fictional,2"';changed=build(d)
    assert changed['operation_key']==r['operation_key']and changed['receipt_name']==r['receipt_name']
    assert changed['payload_sha256']!=r['payload_sha256']


def test_new_occurrence_version_does_not_mint_a_new_operation_or_receipt():
    d=sample();a=build(d);next(p for p in d['native_pins']if p['role']=='occurrence')['file_version']='2.0';b=build(d)
    assert a['receipt_name']==b['receipt_name']and a['operation_key']==b['operation_key']
    assert a['package_name']!=b['package_name']and a['sha256']!=b['sha256']
    d['output_revision']=2;c=build(d);assert c['operation_key']!=b['operation_key']and c['receipt_name']!=b['receipt_name']


@pytest.mark.parametrize('case',['missing','extra','duplicate','wrong-ref','wrong-role','role-object','ref-object','extra-field','missing-field','list-guid','file-guid','zero-guid','braced-guid','item-bool','item-zero','etag-empty','etag-control','version-empty','version-zero','version-text','hash-missing','hash-mismatch','wrong-config-library','same-config-file','native-alias-conflict','approval-claim','cancelled','incomplete-observation','source-drift'])
def test_unqualified_or_inconsistent_inputs_have_no_package(case):
    d=sample();p=d['native_pins'][0]
    if case=='missing':d['native_pins'].pop()
    elif case=='extra':d['native_pins'].append(deepcopy(p))
    elif case=='duplicate':d['native_pins'][-1]=deepcopy(p)
    elif case=='wrong-ref':p['ref']='OTHER'
    elif case=='wrong-role':p['role']='owner'
    elif case=='role-object':p['role']=[]
    elif case=='ref-object':p['ref']=[]
    elif case=='extra-field':p['approved']=True
    elif case=='missing-field':p.pop('file_etag')
    elif case=='list-guid':p['list_id']='unknown'
    elif case=='file-guid':p['file_id']='unknown'
    elif case=='zero-guid':p['file_id']='00000000-0000-0000-0000-000000000000'
    elif case=='braced-guid':p['list_id']='{'+LIB+'}'
    elif case=='item-bool':p['item_id']=True
    elif case=='item-zero':p['item_id']=0
    elif case=='etag-empty':p['item_etag']=''
    elif case=='etag-control':p['file_etag']='x\ny'
    elif case=='version-empty':p['file_version']=''
    elif case=='version-zero':p['file_version']='0.0'
    elif case=='version-text':p['file_version']='latest'
    elif case=='hash-missing':p['sha256']=''
    elif case=='hash-mismatch':next(x for x in d['native_pins']if x['role']=='source')['sha256']='0'*64
    elif case=='wrong-config-library':p['list_id']=OTHER
    elif case=='same-config-file':d['native_pins'][1].update({k:v for k,v in p.items()if k not in {'role','ref'}})
    elif case=='native-alias-conflict':d['native_pins'][-1]['file_id']=p['file_id']
    elif case=='approval-claim':d['profiles'][0]['approved']=True
    elif case=='cancelled':d['selection']['event']['cancelled']=True
    elif case=='incomplete-observation':d['observed_sources']['state']='incomplete'
    elif case=='source-drift':d['observed_sources']['sources'].pop()
    with pytest.raises(ValueError):build(d)


@pytest.mark.parametrize('purpose,revision',[(None,1),([],1),('send',1),('preparation-review',0),('preparation-review',True),('preparation-review',1.5),('preparation-review',2147483648)])
def test_purpose_and_revision_are_explicit(purpose,revision):
    d=sample();d.update(purpose=purpose,output_revision=revision)
    with pytest.raises(ValueError):build(d)


def test_calendar_purpose_must_be_selected_and_uses_existing_f12_selection():
    d=sample();d['purpose']='calendar-review';r=build(d);assert json.loads(r['canonical_json'])['payload']['f12_selection']['subject']==d['selection']['event']['subject']
    d['selection']['capabilities']=['prepare']
    with pytest.raises(ValueError,match='Purpose not selected'):build(d)


def test_two_forums_and_parallel_calls_do_not_share_mutable_state():
    a,b=sample(0),sample(1)
    with ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(build,[deepcopy(a),deepcopy(b)]*8))
    assert all(x==results[i%2]for i,x in enumerate(results))
    assert results[0]['receipt_name']!=results[1]['receipt_name']
    decoded=json.loads(results[0]['canonical_json']);decoded['payload']['snapshot']['profile']['purpose']='CHANGED'
    assert build(a)==results[0]


def test_package_source_has_no_native_io_or_auth_imports():
    tree=ast.parse((Path(__file__).parents[1]/'scripts/forum_native_package.py').read_text())
    imports={n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree)if isinstance(n,ast.Import)for a in n.names}
    assert imports<={'hashlib','json','re','uuid','scripts.forum_configuration'}
