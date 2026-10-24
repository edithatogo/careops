from copy import deepcopy
import json
from xml.etree import ElementTree as ET
import pytest
from scripts.f12_environment_bindings import VARIABLES,bind_environment_metadata,environment_definition


def definition():
    return {'parameters':{schema:{'type':'Object','defaultValue':{}} for schema in VARIABLES},
            'actions':{'read':{'inputs':"@parameters('comeet_F12Baseline')?['event']"},
                       'selection':{'inputs':"@parameters('comeet_F12Selection')?['subject']"},
                       'unchanged':{'inputs':'PRESERVE'}}}


def test_metadata_and_every_reference_aligned_without_mutation():
    d=definition();before=deepcopy(d);r=bind_environment_metadata(d)
    assert d==before
    for schema,(display,description) in VARIABLES.items():
        friendly=f'{display} ({schema})'
        assert schema not in r['parameters']
        assert r['parameters'][friendly]=={'type':'Object','defaultValue':{},'metadata':{'schemaName':schema,'description':description}}
        assert f"parameters('{schema}')" not in json.dumps(r)
        assert f"parameters('{friendly}')" in json.dumps(r['actions'])
    assert r['actions']['unchanged']==d['actions']['unchanged']


@pytest.mark.parametrize('schema',VARIABLES)
def test_json_definition_excludes_defaults_and_current_values(schema):
    root=ET.fromstring(environment_definition(schema))
    assert root.attrib=={'schemaname':schema}
    assert root.findtext('type')=='100000003'
    assert root.find('defaultvalue') is None
    assert root.find('environmentvariablevalues') is None
    assert root.findtext('secretstore')=='0'


@pytest.mark.parametrize('value',[{'type':'String','defaultValue':''},{'type':'Object','defaultValue':{'secret':'private'}},{}])
def test_nonempty_or_unknown_parameter_refused(value):
    d=definition();d['parameters']['comeet_F12Baseline']=value
    with pytest.raises(ValueError) as error:bind_environment_metadata(d)
    assert 'private' not in str(error.value)


def test_second_binding_refused():
    r=bind_environment_metadata(definition())
    with pytest.raises(ValueError):bind_environment_metadata(r)
