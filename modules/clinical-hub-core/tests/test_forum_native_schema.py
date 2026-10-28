"""Portable H2 native-schema safety: existing library content is not provisioned here."""
import ast
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from scripts.forum_native_schema import build_schema

LIB='11111111-1111-4111-8111-111111111111'
OTHER='22222222-2222-4222-8222-222222222222'


def test_additive_schema_does_not_change_existing_document_fields_or_default_view():
    result=build_schema(LIB)
    assert result['schema_version']==1 and len(result['fields'])==32 and len(result['content_types'])==2
    assert result['field_add_options']==10  # NoContentType(2) + InternalNameHint(8).
    assert result['field_add_options'] & (1|4|16) == 0
    assert result['default_content_type_change'] is False
    assert result['default_view_change'] is False
    assert result['permission_change'] is False
    assert result['create_library'] is False
    assert result['native_authority'] is False
    names={f['name']for f in result['fields']}
    assert all(n.startswith('H2')for n in names) and len(names)==32
    assert not names & {'Title','FileLeafRef','_ExtendedDescription','ContentType'}
    for f in result['fields']:
        xml=ET.fromstring(f['xml'])
        assert xml.attrib['Required']=='FALSE'
        assert xml.attrib['Name']==f['name']
        assert xml.attrib['ID']==f['id']


def test_deterministic_ids_and_separate_native_library_binding():
    left=build_schema(LIB);right=build_schema(OTHER)
    assert left==build_schema(LIB.upper())
    assert [(f['name'],f['id'])for f in left['fields']]==[(f['name'],f['id'])for f in right['fields']]
    assert len({f['id']for f in left['fields']})==32
    assert left['content_types']==right['content_types']
    for f in left['fields']:
        xml=ET.fromstring(f['xml'])
        if f['type']in {'Lookup','LookupMulti'}:
            assert xml.attrib['List']=='{'+LIB+'}' and xml.attrib['ShowField']=='Title'
            assert xml.attrib['Mult']==('TRUE'if f['type']=='LookupMulti'else'FALSE')


def test_governance_defaults_cannot_be_approval_or_prequalified_roles():
    fields={f['name']:ET.fromstring(f['xml'])for f in build_schema(LIB)['fields']}
    for n in ['H2GovernanceState','H2ChairState','H2DelegateState','H2SecretariatState']:
        choices=[c.text for c in fields[n].findall('CHOICES/CHOICE')]
        assert choices==['Unverified','Draft','Conflicting','Recorded']
        assert fields[n].findtext('Default')=='Unverified'
        assert not any(x.lower()in {'approved','authorised'}for x in choices)
    assert fields['H2EventType'].findtext('Default')=='Not selected'
    assert fields['H2OutputRevision'].attrib['Min']=='1'


def test_technical_bindings_are_not_ordinary_form_inputs_or_claimed_acl_protection():
    fields={f['name']:ET.fromstring(f['xml'])for f in build_schema(LIB)['fields']}
    for n in ['H2EventRef','H2SeriesRef']:
        assert fields[n].attrib['Hidden']=='TRUE'
        assert fields[n].attrib['ShowInEditForm']==fields[n].attrib['ShowInNewForm']=='FALSE'
        assert fields[n].attrib['ReadOnly']=='FALSE'  # Maker can write; hiding is not security.


def test_content_types_only_link_their_fields_and_leave_parent_document_intact():
    result=build_schema(LIB);fields={f['name']for f in result['fields']}
    profile,occurrence=result['content_types']
    assert profile['id']!=occurrence['id'] and all(t['id'].startswith('0x010100')for t in [profile,occurrence])
    assert set(profile['fields'])|set(occurrence['fields'])==fields|{'Title'}
    assert set(profile['required_fields'])<=set(profile['fields'])
    assert set(occurrence['required_fields'])<=set(occurrence['fields'])
    assert 'Title'in profile['required_fields'] and 'Title'in occurrence['required_fields']
    assert 'H2Profile'not in profile['fields'] and 'H2EffectiveFrom'not in occurrence['fields']


@pytest.mark.parametrize('value',[None,'',True,'not-a-guid',LIB+'/other','{'+LIB+'}'])
def test_unknown_or_injected_target_is_refused(value):
    with pytest.raises(ValueError):build_schema(value)


def test_results_do_not_share_mutable_configuration_state():
    one=build_schema(LIB);two=build_schema(LIB)
    one['fields'][0]['xml']='Changed';one['content_types'][0]['fields'].append('Injected')
    assert build_schema(LIB)==two


def test_schema_builder_has_no_native_io_auth_or_persistence_import():
    tree=ast.parse((Path(__file__).parents[1]/'scripts/forum_native_schema.py').read_text())
    imports={n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)}|{a.name for n in ast.walk(tree)if isinstance(n,ast.Import)for a in n.names}
    assert imports<={'uuid','xml.etree.ElementTree'}


def observed_field(field):
    xml=ET.fromstring(field['xml'])
    result=dict(Id=field['id'].strip('{}'),InternalName=field['name'],StaticName=field['name'],
                Required=False,ReadOnlyField=False,Hidden=xml.get('Hidden')=='TRUE',
                TypeAsString=field['type'],SchemaXml=field['xml'],DefaultValue=xml.findtext('Default'))
    if field['type']in {'Lookup','LookupMulti'}:
        result.update(LookupList=xml.get('List'),LookupField='Title',AllowMultipleValues=field['type']=='LookupMulti')
    if field['type']in {'Choice','MultiChoice'}:result['Choices']=[c.text for c in xml.findall('CHOICES/CHOICE')]
    return result


@pytest.mark.parametrize('native_type',['Lookup','LookupMulti'])
def test_explicit_multi_lookup_readback_does_not_require_an_unnecessary_rewrite(native_type):
    from scripts.forum_native_schema import validate_field_readback
    field=next(f for f in build_schema(LIB)['fields']if f['name']=='H2Sources')
    actual=observed_field(field);actual['TypeAsString']=native_type
    assert validate_field_readback(field,actual)['status']=='PASS'
    actual['AllowMultipleValues']=False
    with pytest.raises(ValueError):validate_field_readback(field,actual)


@pytest.mark.parametrize('key,value',[('Id',OTHER),('InternalName','Profile_x0020_revision'),
    ('Required',True),('ReadOnlyField',True),('Hidden',True),('TypeAsString','Note')])
def test_identity_type_and_flag_drift_is_not_normalised_away(key,value):
    from scripts.forum_native_schema import validate_field_readback
    field=build_schema(LIB)['fields'][0];actual=observed_field(field);actual[key]=value
    with pytest.raises(ValueError):validate_field_readback(field,actual)


def test_wrong_lookup_target_or_positive_governance_default_is_refused():
    from scripts.forum_native_schema import validate_field_readback
    rows=build_schema(LIB)['fields']
    field=next(f for f in rows if f['name']=='H2Sources');actual=observed_field(field);actual['LookupList']=OTHER
    with pytest.raises(ValueError):validate_field_readback(field,actual)
    field=next(f for f in rows if f['name']=='H2GovernanceState');actual=observed_field(field);actual['DefaultValue']='Approved'
    with pytest.raises(ValueError):validate_field_readback(field,actual)
    actual=observed_field(field);actual['Choices'].append('Approved')
    with pytest.raises(ValueError):validate_field_readback(field,actual)
