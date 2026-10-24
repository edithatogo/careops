import copy
import json

import pytest

from scripts.f12_configuration import validate_configuration


def fixture():
    b = {'event': {'id': 'fictional-event', 'originalStart': '2099-01-01T06:00:00Z',
                  'seriesMasterId': 'fictional-series', 'iCalUId': 'fictional-uid',
                  'subject': 'FICTIONAL meeting', 'type': 'occurrence',
                  'organizer': {'emailAddress': {'address': 'fictional@example.invalid'}},
                  'start': {'dateTime': '2099-01-01T06:00:00', 'timeZone': 'UTC'},
                  'end': {'dateTime': '2099-01-01T07:00:00', 'timeZone': 'UTC'},
                  'changeKey': 'fictional-revision', 'lastModifiedDateTime': '2098-12-01T00:00:00Z',
                  'isCancelled': False},
         'agenda': {'id': 'fictional-agenda', 'name': 'FICTIONAL.docx', 'size': 123,
                    'lastModifiedDateTime': '2098-12-01T00:00:00Z', 'contentType': 'application/docx',
                    '@odata.type': '#microsoft.graph.fileAttachment', 'isInline': False},
         'checked_at': '2098-12-01T00:00:00Z', 'baseline_run_id': 'fictional-run'}
    s = {'window_start': '2099-01-01T06:00:00Z', 'window_end': '2099-01-01T07:00:00Z',
         'subject': 'FICTIONAL meeting', 'organizer': 'fictional@example.invalid', 'agenda_name': 'FICTIONAL.docx'}
    return b, s


def call(b, s):
    return validate_configuration(json.dumps(b), json.dumps(s))


def commissioning_candidate():
    from scripts.f12_operator_inputs import FIELDS
    names = [('F12 accepted metadata baseline (comeet_F12Baseline)', 'comeet_F12Baseline'),
             ('F12 metadata selection (comeet_F12Selection)', 'comeet_F12Selection')]
    return {'properties': {'connectionReferences': {'original': {'source': 'Invoker'}},
        'definition': {'parameters': {name: {'type': 'Object', 'defaultValue': {},
            'metadata': {'schemaName': schema}} for name, schema in names},
            'triggers': {'manual': {'inputs': {'schema': {'properties': {
                key: {'type': 'string'} for key in ['configuration_mode', *FIELDS]}}}}},
            'actions': {'baseline': {'inputs': "@parameters('" + names[0][0] + "')"},
                        'selection': {'inputs': "@parameters('" + names[1][0] + "')"}}}}}


def test_commissioning_inputs_are_pure_unbound_and_preserve_native_contract():
    from scripts.f12_portable_definition import historical_commissioning_inputs, baseline_transport
    candidate = commissioning_candidate()
    b, s = fixture()
    before = copy.deepcopy((candidate, b, s))
    result = historical_commissioning_inputs(candidate, b, s)
    assert (candidate, b, s) == before
    assert result['properties']['connectionReferences'] == candidate['properties']['connectionReferences']
    d = result['properties']['definition']
    assert d['triggers'] == candidate['properties']['definition']['triggers']
    assert d['parameters']['F12 historical commissioning baseline'] == {
        'type': 'Object', 'defaultValue': baseline_transport(b)}
    assert d['parameters']['F12 historical commissioning selection'] == {
        'type': 'Object', 'defaultValue': s}
    assert d['actions']['selection']['inputs'] == "@parameters('F12 historical commissioning selection')"
    assert 'schemaName' not in json.dumps(d['parameters'])
    with pytest.raises(ValueError):
        historical_commissioning_inputs(result, b, s)


@pytest.mark.parametrize('mutation', ['override', 'missing_control', 'nonempty_default'])
def test_commissioning_inputs_refuse_parameter_or_operator_drift(mutation):
    from scripts.f12_portable_definition import historical_commissioning_inputs
    c = commissioning_candidate()
    d = c['properties']['definition']
    if mutation == 'override': c['properties']['parameters'] = {'unexpected': {'value': {}}}
    if mutation == 'missing_control': del d['triggers']['manual']['inputs']['schema']['properties']['subject']
    if mutation == 'nonempty_default':
        next(iter(d['parameters'].values()))['defaultValue'] = {'unexpected': True}
    with pytest.raises(ValueError):
        historical_commissioning_inputs(c, *fixture())


def test_valid_result_contains_no_input_values():
    b, s = fixture()
    result = call(b, s)
    assert result['comparison_fields'] == 21
    assert 'fictional' not in json.dumps(result)
    before = copy.deepcopy((b, s))
    call(b, s)
    assert (b, s) == before


@pytest.mark.parametrize('field', ['id', 'originalStart', 'seriesMasterId', 'iCalUId', 'subject',
                                 'type', 'organizer', 'start', 'end', 'changeKey', 'lastModifiedDateTime', 'isCancelled'])
def test_missing_baseline_field_rejected(field):
    b, s = fixture()
    del b['event'][field]
    with pytest.raises(ValueError):
        call(b, s)


@pytest.mark.parametrize('field', ['id', 'name', 'size', 'lastModifiedDateTime', 'contentType', '@odata.type', 'isInline'])
def test_missing_agenda_field_rejected(field):
    b, s = fixture()
    del b['agenda'][field]
    with pytest.raises(ValueError):
        call(b, s)


@pytest.mark.parametrize('mutation', ['bool_size', 'string_bool', 'unknown', 'selector_drift',
                                     'naive_window', 'reversed_window', 'nonutc', 'inline', 'invalid_date'])
def test_malformed_contract_rejected_without_echo(mutation):
    b, s = fixture()
    if mutation == 'bool_size': b['agenda']['size'] = True
    elif mutation == 'string_bool': b['event']['isCancelled'] = 'false'
    elif mutation == 'unknown': b['unknown'] = 'PRIVATE-SENTINEL'
    elif mutation == 'selector_drift': s['subject'] = 'PRIVATE-SENTINEL'
    elif mutation == 'naive_window': s['window_start'] = '2099-01-01T06:00:00'
    elif mutation == 'reversed_window': s['window_end'] = '2099-01-01T05:00:00Z'
    elif mutation == 'nonutc': b['event']['start']['timeZone'] = 'Unknown'
    elif mutation == 'inline': b['agenda']['isInline'] = True
    elif mutation == 'invalid_date': b['checked_at'] = 'PRIVATE-SENTINEL'
    with pytest.raises(ValueError) as error:
        call(b, s)
    assert 'PRIVATE-SENTINEL' not in str(error.value)


def test_actual_storage_text_character_boundary_and_unicode():
    b, s = fixture()
    b['baseline_run_id'] = 'fictional-é'
    raw = json.dumps(b, ensure_ascii=False)
    assert len(raw.encode()) > len(raw)
    raw += ' ' * (2000 - len(raw))
    assert validate_configuration(raw, json.dumps(s))['baseline_characters'] == 2000
    with pytest.raises(ValueError):
        validate_configuration(raw + ' ', json.dumps(s))
    with pytest.raises(ValueError):
        validate_configuration(json.dumps(b), json.dumps(s) + ' ' * 2000)


def test_supplementary_unicode_conservatively_counts_two_units():
    b, s = fixture()
    b['baseline_run_id'] = 'fictional-😀'
    raw = json.dumps(b, ensure_ascii=False)
    raw += ' ' * (2000 - len(raw))
    with pytest.raises(ValueError):
        validate_configuration(raw, json.dumps(s))


@pytest.mark.parametrize('raw', ['{', '{"event": {}, "event": {}}', 'null', '[]'])
def test_malformed_or_duplicate_json_rejected(raw):
    with pytest.raises(ValueError):
        validate_configuration(raw, json.dumps(fixture()[1]))
