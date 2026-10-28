# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Fictional native property models; not authenticated service evidence."""
from copy import deepcopy
import json
import pytest
from scripts.forum_native_mapping import map_package

LIB='11111111-1111-4111-8111-111111111111'
PT='0x01010011111111111141118111111111111111'
OT='0x01010022222222222242228222222222222222'


def sample():
    def row(n,ct):
        return dict(Id=n,ContentTypeId=ct,FileSystemObjectType=0,Title='Fictional duplicate label',File=dict(Exists=True,UniqueId=f'{n:08d}-1111-4111-8111-111111111111',Name=f'Fictional-{n}.txt',UIVersionLabel='2.0',MajorVersion=2,MinorVersion=0,ETag='"fictional,2"'),**{'odata.etag':'"2"','odata.editLink':f"Web/Lists(guid'{LIB}')/Items({n})"})
    p=row(1,PT);o=row(2,OT)
    p.update(H2Revision='r1',H2EffectiveFrom='2030-01-01T00:00:00Z',H2EffectiveUntil=None,H2Purpose='Fictional review only',H2Controls=['Papers','Review'],H2AgendaSections=['Decisions','Discussion'],H2GovernanceState='Unverified',H2GovernanceSourceId=None,H2TemplateId=3,H2Destination='Existing qualification drafts',H2Register='Retained meeting action register (reference only)')
    for r in ['Chair','Delegate','Secretariat']:
        p.update({f'H2{r}Role':'Fictional '+r,f'H2{r}State':'Unverified',f'H2{r}EvidenceId':None})
    o.update(H2ProfileId=1,H2Start='2030-02-04T06:00:00Z',H2End='2030-02-04T07:00:00Z',H2OriginalStart='2030-02-04T06:00:00Z',H2TimeZone='Australia/Brisbane',H2Organiser='organiser@example.invalid',H2EventType='Recurring occurrence',H2Cancelled=False,H2EventRef='FICTIONAL-EVENT',H2SeriesRef='FICTIONAL-SERIES',H2SourcesId=[4],H2OutputRevision=1)
    sources=[dict(item=row(3,'0x0101'),kind='template',sha256='a'*64),dict(item=row(4,'0x0101'),kind='agenda',sha256='b'*64)]
    return dict(profile=p,occurrence=o,profile_sha256='c'*64,occurrence_sha256='d'*64,sources=sources,binding=dict(library_id=LIB,profile_type_id=PT,occurrence_type_id=OT,binding_ref='QUALIFIED-BINDING',destination_ref='QUALIFIED-DRAFTS',register_ref='RETAINED-REGISTER'),purpose='preparation-review')


def packet(d):
    return json.loads(map_package(**d)['package']['canonical_json'])


def test_typed_mapping_preserves_native_choice_identity_and_versions():
    d=sample();before=deepcopy(d);result=map_package(**d);p=packet(d);snap=p['payload']['snapshot']
    assert d==before and result['native_authority']is False
    assert snap['profile']['control_keys']==['papers','review']
    assert snap['profile']['roles']['chair']['state']=='unverified'
    assert snap['profile']['template_ref'].endswith(d['sources'][0]['item']['File']['UniqueId'])
    assert snap['selection']['snapshot_revision']=='v2.0'
    assert snap['selection']['sources'][0]['revision']=='v2.0'
    assert snap['selection']['event']['type']=='occurrence'
    assert p['send_authority']is False and p['activation_authority']is False
    assert result['role_descriptions']['chair']=='Fictional Chair'


def test_equal_display_names_do_not_choose_another_native_profile():
    a=sample();b=sample();b['profile']['File']['UniqueId']='99999999-1111-4111-8111-111111111111'
    assert packet(a)['identity']['forum_ref']!=packet(b)['identity']['forum_ref']


def test_governance_lookup_does_not_confer_approval_and_is_pinned():
    d=sample();source=deepcopy(d['sources'][1]);source['item']['Id']=5;source['item']['File']['UniqueId']='00000005-1111-4111-8111-111111111111';source['item']['odata.editLink']=f"Web/Lists(guid'{LIB}')/Items(5)";source['kind']='governance'
    d['sources'].append(source);d['profile'].update(H2GovernanceState='Recorded',H2GovernanceSourceId=5,H2ChairState='Draft',H2ChairEvidenceId=5)
    p=packet(d);assert p['payload']['snapshot']['profile']['governance']['state']=='recorded'
    assert len(p['payload']['native_pins'])==5 and p['native_authority']is False


def test_single_occurrence_and_calendar_selection_use_existing_contract():
    d=sample();d['purpose']='calendar-review';d['occurrence'].update(H2EventType='Single meeting',H2OriginalStart=None,H2SeriesRef=None)
    p=packet(d);f=p['payload']['f12_selection']
    assert f['agenda_name']=='Fictional-4.txt' and f['window_start']=='2030-02-04T06:00:00Z'
    assert p['payload']['snapshot']['selection']['event']['series_ref']is None


@pytest.mark.parametrize('case',['wrong-type','wrong-profile','wrong-library','missing-template','missing-source','extra-source','duplicate-source','wrong-template-kind','wrong-evidence-kind','recorded-no-source','missing-role','unknown-state','unknown-control','duplicate-controls','cancelled','invalid-event-type','missing-event-binding','missing-series','single-with-series','missing-timezone','naive-time','bad-time','end-before-start','not-effective','wrong-destination','wrong-register','missing-etag','bad-version','missing-hidden-field','folder','file-missing','output-bool','duplicate-lookup','source-hash','binding-extra','unselected-evidence','invalid-purpose'])
def test_incomplete_stale_or_wrong_context_selection_refuses(case):
    d=sample();p=d['profile'];o=d['occurrence'];s=d['sources']
    if case=='wrong-type':p['ContentTypeId']=OT
    elif case=='wrong-profile':o['H2ProfileId']=99
    elif case=='wrong-library':p['odata.editLink']=p['odata.editLink'].replace(LIB,'99999999-1111-4111-8111-111111111111')
    elif case=='missing-template':p['H2TemplateId']=None
    elif case=='missing-source':s.pop()
    elif case=='extra-source':o['H2SourcesId']=[]
    elif case=='duplicate-source':s.append(deepcopy(s[0]))
    elif case=='wrong-template-kind':s[0]['kind']='agenda'
    elif case=='wrong-evidence-kind':p['H2GovernanceSourceId']=4
    elif case=='recorded-no-source':p['H2GovernanceState']='Recorded'
    elif case=='missing-role':p['H2ChairRole']=''
    elif case=='unknown-state':p['H2ChairState']='Approved'
    elif case=='unknown-control':p['H2Controls']=['Email']
    elif case=='duplicate-controls':p['H2Controls']=['Papers','Papers']
    elif case=='cancelled':o['H2Cancelled']=True
    elif case=='invalid-event-type':o['H2EventType']='Not selected'
    elif case=='missing-event-binding':o['H2EventRef']=None
    elif case=='missing-series':o['H2SeriesRef']=None
    elif case=='single-with-series':o['H2EventType']='Single meeting'
    elif case=='missing-timezone':o['H2TimeZone']=''
    elif case=='naive-time':o['H2Start']='2030-02-04T06:00:00'
    elif case=='bad-time':o['H2Start']='2030-02-31T06:00:00Z'
    elif case=='end-before-start':o['H2End']=o['H2Start']
    elif case=='not-effective':p['H2EffectiveFrom']='2031-01-01T00:00:00Z'
    elif case=='wrong-destination':p['H2Destination']='Other drafts'
    elif case=='wrong-register':p['H2Register']='New action register'
    elif case=='missing-etag':p.pop('odata.etag')
    elif case=='bad-version':p['File']['UIVersionLabel']='1.0'
    elif case=='missing-hidden-field':o.pop('H2EventRef')
    elif case=='folder':p['FileSystemObjectType']=1
    elif case=='file-missing':p['File']['Exists']=False
    elif case=='output-bool':o['H2OutputRevision']=True
    elif case=='duplicate-lookup':o['H2SourcesId']=[4,4]
    elif case=='source-hash':s[0]['sha256']='unknown'
    elif case=='binding-extra':d['binding']['approved']=True
    elif case=='unselected-evidence':p['H2GovernanceSourceId']=5
    elif case=='invalid-purpose':d['purpose']='send'
    with pytest.raises(ValueError):map_package(**d)


def test_source_read_order_does_not_change_package_identity_or_bytes():
    d=sample();a=map_package(**d);d['sources'].reverse();assert map_package(**d)==a


def test_native_etag_drift_with_same_version_changes_payload_not_receipt():
    d=sample();a=map_package(**d)['package'];d['sources'][1]['item']['File']['ETag']='"fictional,3"';b=map_package(**d)['package']
    assert a['receipt_name']==b['receipt_name']and a['operation_key']==b['operation_key']
    assert a['payload_sha256']!=b['payload_sha256']


def test_unknown_native_agenda_choice_does_not_enter_existing_contract():
    d=sample();d['profile']['H2AgendaSections']=['Send approval']
    with pytest.raises(ValueError):map_package(**d)
