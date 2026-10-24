from copy import deepcopy
import json
import pytest
from jsonschema import Draft7Validator, FormatChecker
from scripts.f12_portable_definition import guarded_definition, configuration_schemas, BASELINE, SELECTION
from scripts.f12_comparator_binding import FIELDS


def source():
    checks = {}
    for name, path in FIELDS.items():
        action = 'Find_exact_occurrence' if path[0] == 'event' else 'Find_issued_agenda'
        observed = f"first(body('{action}'))" + ''.join(f"?['{p}']" for p in path[1:])
        if name == 'event_organizer': observed = f"toLower(coalesce({observed},''))"
        value = 'false' if name in {'event_cancelled','agenda_inline'} else '42' if name=='agenda_size' else "'FICTIONAL'"
        checks[name] = f'@equals({observed},{value})'
    inputs = {'checks':checks, 'state':'@and('+','.join(x[1:] for x in checks.values())+')',
              'baseline_run_id':'FICTIONAL-RUN','baseline_checked_at':'2099-01-01T00:00:00Z','scope':'FICTIONAL-SCOPE','meeting_checked':'FICTIONAL-MEETING'}
    selector = "@and(equals(item()?['subject'],'FICTIONAL'),equals(toLower(coalesce(item()?['organizer']?['emailAddress']?['address'],'')),'fictional@example.invalid'),startsWith(coalesce(item()?['start']?['dateTime'],''),'2099-01-01T06:00:00'),startsWith(coalesce(item()?['end']?['dateTime'],''),'2099-01-01T07:00:00'),equals(item()?['start']?['timeZone'],'UTC'),equals(item()?['end']?['timeZone'],'UTC'),not(empty(item()?['id'])))"
    return {'parameters':{'existing':{'type':'Object','defaultValue':{}}}, 'triggers':{'manual':{'type':'Request'}}, 'actions':{
        'Read_approved_window':{'type':'OpenApiConnection','runAfter':{},'inputs':{'parameters':{'Uri':'https://graph.microsoft.com/v1.0/me/calendar/calendarView?startDateTime=2099-01-01T06:00:00Z&endDateTime=2099-01-01T07:00:00Z&%24filter=subject%20eq%20%27FICTIONAL%27&%24select=id,subject&%24top=10','Method':'GET'}}},
        'Find_exact_occurrence':{'inputs':{'where':selector},'runAfter':{'Read_approved_window':['Succeeded']}},
        'Calendar_read_unverified':{'inputs':'EXISTING_FAILURE','runAfter':{'Read_approved_window':['Failed','TimedOut']}},
        'Require_one_occurrence':{'expression':'UNIQUE_COMPLETE_EVENT_GUARD','actions':{
            'Read_agenda_metadata':{'inputs':'EXISTING_GET'},
            'Find_issued_agenda':{'inputs':{'where':"@and(equals(item()?['name'],'FICTIONAL.docx'),equals(item()?['isInline'],false))"}},
            'Require_one_agenda':{'expression':'UNIQUE_COMPLETE_AGENDA_GUARD','actions':{'Observed_baseline':{'inputs':inputs}}}}}}}


def metadata_repair_source():
    from scripts.f12_portable_definition import EVENT_METADATA_FIELDS
    d, _ = guarded_definition(source())
    a = d['actions']['Require_configuration']['actions']
    uri = a['Read_approved_window']['inputs']['parameters']['Uri']
    a['Read_approved_window']['inputs']['parameters']['Uri'] = uri.replace(
        'id%2Csubject&%24top=10', '%2C'.join(EVENT_METADATA_FIELDS) + '&%24top=10')
    occurrence = a['Require_one_occurrence']
    occurrence['expression'] = "@and(equals(length(body('Find_exact_occurrence')),1),empty(body('Read_approved_window')?['@odata.nextLink']))"
    n = occurrence['actions']
    n['Require_one_agenda']['expression'] = "@and(equals(length(body('Find_issued_agenda')),1),empty(body('Read_agenda_metadata')?['@odata.nextLink']))"
    n['Read_agenda_metadata'] = {'type': 'OpenApiConnection', 'runAfter': {}, 'inputs': {
        'host': {'operationId': 'HttpRequest', 'connectionName': 'existing_outlook'},
        'retryPolicy': {'type': 'none'}, 'parameters': {'Method': 'GET',
            'CustomHeader1': 'Prefer: outlook.timezone="UTC"',
            'Uri': "@concat('https://graph.microsoft.com/v1.0/me/events/',uriComponent(first(body('Find_exact_occurrence'))?['id']),'/attachments?$select=id,name,size,lastModifiedDateTime,contentType,isInline&$top=10')"}}}
    n['Attachment_read_unverified'] = {'type': 'Compose', 'inputs': 'EXISTING_FAILURE',
                                      'runAfter': {'Read_agenda_metadata': ['Failed', 'TimedOut']}}
    return {'name': 'existing-fictional-f12', 'properties': {
        'state': 'Stopped', 'connectionReferences': {'existing_outlook': {'preserve': True}},
        'definition': d}}


def repair_metadata(baseline=None):
    import hashlib
    from scripts.f12_portable_definition import repair_calendar_metadata_reads
    baseline = metadata_repair_source() if baseline is None else baseline
    pin = hashlib.sha256(json.dumps(baseline, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode()).hexdigest()
    return repair_calendar_metadata_reads(baseline, expected_sha256=pin)


def metadata_guard_parts(candidate):
    a = candidate['properties']['definition']['actions']['Require_configuration']['actions']
    before = a['Require_one_occurrence']['actions']['Require_event_metadata']
    agenda = before['actions']['Require_one_agenda']
    return a, before, agenda['actions']['Require_stable_event']


def evaluate_metadata(expression, context):
    """Evaluate this small emitted guard subset; not a native WDL validator."""
    import re
    from datetime import datetime, timezone
    from scripts.wdl_arguments import _split_args
    expression = expression.removeprefix('@')
    ref = re.fullmatch(r"(first\(body\('([^']+)'\)\)|body\('([^']+)'\)|parameters\('([^']+)'\))((?:\?\['[^']+'\])*)", expression)
    if ref:
        key = ref[2] or ref[3] or ref[4]
        value = context['parameters'][key] if ref[4] else context[key]
        if ref[2]: value = value[0]
        for field in re.findall(r"\?\['([^']+)'\]", ref[5]):
            value = value.get(field) if isinstance(value, dict) else None
        return value
    if expression.startswith("'"): return expression[1:-1]
    if expression == 'null': return None
    if expression in ('true', 'false'): return expression == 'true'
    if expression.isdigit(): return int(expression)
    if expression == 'utcNow()': return '2030-02-20T00:00:00Z'
    name, rest = expression.split('(', 1)
    values = [evaluate_metadata(x, context) for x in _split_args(rest[:-1])]
    if name == 'ticks':
        dt = datetime.fromisoformat(values[0].replace('Z', '+00:00'))
        return (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt).timestamp()
    if name == 'and': return all(values)
    if name == 'equals': return values[0] == values[1]
    if name == 'empty': return values[0] in (None, '', [], {})
    if name == 'length': return len(values[0])
    if name == 'not': return not values[0]
    if name == 'greaterOrEquals': return values[0] >= values[1]
    if name == 'lessOrEquals': return values[0] <= values[1]
    raise ValueError(name)


def event_metadata_context():
    event = {'id': 'FICTIONAL-EVENT', 'originalStart': '2030-02-18T06:00:00Z',
        'seriesMasterId': 'FICTIONAL-SERIES', 'iCalUId': 'FICTIONAL-ICAL',
        'subject': 'FICTIONAL', 'type': 'exception',
        'organizer': {'emailAddress': {'address': 'fictional@example.invalid'}},
        'start': {'dateTime': '2030-02-18T06:00:00', 'timeZone': 'UTC'},
        'end': {'dateTime': '2030-02-18T07:00:00', 'timeZone': 'UTC'},
        'changeKey': 'FICTIONAL-V1', 'lastModifiedDateTime': '2030-02-18T00:00:00Z',
        'isCancelled': False}
    return {'Find_exact_occurrence': [deepcopy(event)], 'Read_event_metadata': deepcopy(event),
            'Read_event_after_agenda': deepcopy(event),
            'parameters': {BASELINE: {'event': deepcopy(event)}}}


def test_metadata_repair_preserves_operator_guards_and_selects_no_content():
    baseline = metadata_repair_source(); old = deepcopy(baseline)
    candidate, receipt = repair_metadata(baseline)
    assert baseline == old and receipt['deployment_ready'] is False
    assert candidate['properties']['state'] == 'Stopped'
    assert candidate['properties']['connectionReferences'] == baseline['properties']['connectionReferences']
    d = candidate['properties']['definition']; original = baseline['properties']['definition']
    assert d['triggers'] == original['triggers'] and d['parameters'] == original['parameters']
    assert d['actions']['Parse_configuration'] == original['actions']['Parse_configuration']
    a, pre, post = metadata_guard_parts(candidate)
    uri = a['Read_approved_window']['inputs']['parameters']['Uri']
    assert 'lastModifiedDateTime' not in uri and '%24top=10' in uri
    n = a['Require_one_occurrence']['actions']
    read = n['Read_event_metadata']['inputs']['parameters']['Uri']
    assert "uriComponent(first(body('Find_exact_occurrence'))?['id'])" in read
    assert 'lastModifiedDateTime' in read
    assert 'lastModifiedDateTime' in pre['actions']['Require_one_agenda']['actions']['Read_event_after_agenda']['inputs']['parameters']['Uri']
    assert set(post['actions']['Observed_baseline']['inputs']['checks']) == set(FIELDS)
    assert "body('Read_event_metadata')" in post['actions']['Observed_baseline']['inputs']['checks']['event_modified']
    for request in [read, pre['actions']['Read_agenda_metadata']['inputs']['parameters']['Uri']]:
        assert not any(x in request.lower() for x in ['contentbytes', 'attendees', 'onlinemeeting', ',body'])
    assert evaluate_metadata(pre['expression'], event_metadata_context()) is True
    assert evaluate_metadata(post['expression'], event_metadata_context()) is True


@pytest.mark.parametrize('field', ['id', 'originalStart', 'seriesMasterId', 'iCalUId',
                                  'changeKey', 'lastModifiedDateTime', 'isCancelled'])
def test_metadata_missing_fields_block_comparison(field):
    _, pre, post = metadata_guard_parts(repair_metadata()[0]); context = event_metadata_context()
    context['Read_event_metadata'].pop(field)
    try: outcome = evaluate_metadata(pre['expression'], context)
    except (TypeError, AttributeError, ValueError): outcome = False
    assert outcome is False


@pytest.mark.parametrize('action', ['Read_event_metadata', 'Read_event_after_agenda'])
def test_future_event_modified_metadata_refused(action):
    _, pre, post = metadata_guard_parts(repair_metadata()[0]); context = event_metadata_context()
    context[action]['lastModifiedDateTime'] = '2030-02-21T00:00:00Z'
    assert evaluate_metadata((pre if action == 'Read_event_metadata' else post)['expression'], context) is False


@pytest.mark.parametrize('field,value', [('changeKey', 'FICTIONAL-V2'), ('isCancelled', True),
    ('originalStart', '2030-02-19T06:00:00Z'), ('type', 'occurrence'), ('seriesMasterId', 'OTHER')])
def test_changed_or_stale_event_snapshot_refused(field, value):
    _, pre, post = metadata_guard_parts(repair_metadata()[0]); context = event_metadata_context()
    context['Read_event_metadata'][field] = value
    assert evaluate_metadata(pre['expression'], context) is False
    context = event_metadata_context(); context['Read_event_after_agenda'][field] = value
    assert evaluate_metadata(post['expression'], context) is False


def test_stale_baseline_remains_comparator_mismatch_not_missing_metadata():
    _, pre, post = metadata_guard_parts(repair_metadata()[0]); context = event_metadata_context()
    context['parameters'][BASELINE]['event']['lastModifiedDateTime'] = '2030-02-17T00:00:00Z'
    assert evaluate_metadata(pre['expression'], context) is True
    check = post['actions']['Observed_baseline']['inputs']['checks']['event_modified']
    assert evaluate_metadata(check, context) is False


@pytest.mark.parametrize('kind', ['occurrence', 'attachment'])
def test_ambiguous_or_partial_source_guard_preserved(kind):
    baseline = metadata_repair_source(); candidate, _ = repair_metadata(baseline)
    old = baseline['properties']['definition']['actions']['Require_configuration']['actions']['Require_one_occurrence']
    a, pre, _ = metadata_guard_parts(candidate)
    original = old if kind == 'occurrence' else old['actions']['Require_one_agenda']
    actual = a['Require_one_occurrence'] if kind == 'occurrence' else pre['actions']['Require_one_agenda']
    assert actual['expression'] == original['expression']
    assert 'length(' in actual['expression'] and "['@odata.nextLink']" in actual['expression']


@pytest.mark.parametrize('count,next_page', [(0, False), (2, False), (1, True)])
def test_metadata_pipeline_refuses_ambiguous_or_incomplete_collections(count, next_page):
    a, pre, _ = metadata_guard_parts(repair_metadata()[0])
    for selector, read, guard in [
        ('Find_exact_occurrence', 'Read_approved_window', a['Require_one_occurrence']),
        ('Find_issued_agenda', 'Read_agenda_metadata', pre['actions']['Require_one_agenda'])]:
        context = {selector: [{}] * count, read: {'@odata.nextLink': 'unfollowed'} if next_page else {}}
        assert evaluate_metadata(guard['expression'], context) is False


@pytest.mark.parametrize('field,value', [('start', {'dateTime': '2030-02-18T06:00:00', 'timeZone': 'Australia/Brisbane'}),
    ('end', {'dateTime': '2030-02-18T08:00:00', 'timeZone': 'UTC'}),
    ('organizer', {'emailAddress': {'address': 'other@example.invalid'}})])
def test_metadata_time_zone_window_and_organiser_drift_refused(field, value):
    _, pre, post = metadata_guard_parts(repair_metadata()[0]); context = event_metadata_context()
    context['Read_event_metadata'][field] = value
    assert evaluate_metadata(pre['expression'], context) is False
    context = event_metadata_context(); context['Read_event_after_agenda'][field] = value
    assert evaluate_metadata(post['expression'], context) is False


def test_metadata_repair_rejects_changed_pinned_source_and_repeated_repair():
    from scripts.f12_portable_definition import repair_calendar_metadata_reads
    with pytest.raises(ValueError, match='baseline drift'):
        repair_calendar_metadata_reads(metadata_repair_source(), expected_sha256='0' * 64)
    candidate, _ = repair_metadata()
    with pytest.raises(ValueError, match='attachment graph drift'):
        repair_metadata(candidate)


def test_exact_source_trial_never_searches_or_adopts_baseline():
    import hashlib
    from scripts.f12_portable_definition import exact_source_qualification
    baseline = metadata_repair_source(); old = deepcopy(baseline)
    pin = hashlib.sha256(json.dumps(baseline, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
    candidate, review = exact_source_qualification(baseline, expected_sha256=pin,
        event_id='FICTIONAL-EVENT', attachment_id='FICTIONAL-ATTACHMENT', baseline_parameter=BASELINE)
    assert baseline == old and review['deployment_ready'] is False
    assert candidate['properties']['definition']['parameters'] == old['properties']['definition']['parameters']
    a, pre, post = metadata_guard_parts(candidate)
    assert 'calendarView' not in json.dumps(candidate['properties']['definition'])
    assert '/attachments/' in pre['actions']['Read_agenda_metadata']['inputs']['parameters']['Uri']
    assert "uriComponent('FICTIONAL-ATTACHMENT')" in pre['actions']['Read_agenda_metadata']['inputs']['parameters']['Uri']
    assert a['Find_exact_occurrence']['inputs']['from'] == "@createArray(body('Read_approved_window'))"
    assert pre['actions']['Find_issued_agenda']['inputs']['from'] == "@createArray(body('Read_agenda_metadata'))"
    guard = candidate['properties']['definition']['actions']['Require_configuration']['expression']
    assert "?['event']?['id'],'FICTIONAL-EVENT')" in guard
    assert "?['agenda']?['id'],'FICTIONAL-ATTACHMENT')" in guard
    assert set(post['actions']['Observed_baseline']['inputs']['checks']) == set(FIELDS)


@pytest.mark.parametrize('identifier', ['', ' ', 'bad\nidentifier', 'x' * 2049])
def test_exact_source_trial_rejects_invalid_retained_id(identifier):
    from scripts.f12_portable_definition import exact_source_qualification
    with pytest.raises(ValueError, match='retained service identifiers'):
        exact_source_qualification(metadata_repair_source(), expected_sha256='unused',
                                   event_id=identifier, attachment_id='FICTIONAL')


@pytest.mark.parametrize('field', ['lastModifiedDateTime', 'LastModifiedDateTime', 'createdDateTime'])
def test_portable_builder_refuses_unsupported_calendar_select(field):
    d = source(); d['actions']['Read_approved_window']['inputs']['parameters']['Uri'] = d['actions']['Read_approved_window']['inputs']['parameters']['Uri'].replace('id,subject', 'id,subject,' + field)
    with pytest.raises(ValueError, match='cannot be selected'):
        guarded_definition(d)


def test_reads_only_in_valid_branch_and_original_controls_preserved():
    d=source();before=deepcopy(d);r,receipt=guarded_definition(d)
    assert d==before and not receipt['deployment_ready']
    assert receipt['configuration_guard']=='Invalid configuration blocks reads; guard or execution failures return an unverified outcome.'
    assert r['triggers']==d['triggers']
    true=r['actions']['Require_configuration']['actions']
    assert set(true)==set(d['actions'])
    assert true['Require_one_occurrence']['expression']=='UNIQUE_COMPLETE_EVENT_GUARD'
    assert true['Require_one_occurrence']['actions']['Require_one_agenda']['expression']=='UNIQUE_COMPLETE_AGENDA_GUARD'
    assert true['Calendar_read_unverified']==d['actions']['Calendar_read_unverified']
    assert true['Require_one_occurrence']['actions']['Read_agenda_metadata']==d['actions']['Require_one_occurrence']['actions']['Read_agenda_metadata']
    assert r['actions']['Require_configuration']['runAfter']=={'Parse_configuration':['Succeeded']}
    for key in [BASELINE,SELECTION]:assert r['parameters'][key]=={'type':'Object','defaultValue':{}}
    assert 'FICTIONAL' not in json.dumps(r)
    assert '%24filter=' in true['Read_approved_window']['inputs']['parameters']['Uri']
    assert "replace(parameters('comeet_F12Selection')?['subject']" in true['Read_approved_window']['inputs']['parameters']['Uri']


def test_failure_paths_have_no_read_and_no_values():
    r,_=guarded_definition(source());a=r['actions']
    for key in ['Configuration_unverified','Guard_or_execution_unverified']:
        assert a[key]['type']=='Compose'
        assert a[key]['inputs']['state']=='unable_to_verify'
        assert a[key]['inputs']['write_proposed'] is False
        assert not 'FICTIONAL' in json.dumps(a[key])
    assert a['Guard_or_execution_unverified']['runAfter']=={'Require_configuration':['Failed','TimedOut']}
    assert a['Require_configuration']['else']['actions']['Configuration_mismatch']['type']=='Compose'
    for action in a['Parse_configuration']['actions'].values():
        if action['type'] in ['ParseJson','Select']:
            assert action['runtimeConfiguration']['secureData']['properties']==['inputs']
        else:
            assert action['type']=='Query'
            assert action['inputs']['where']=="@not(item()?['valid'])"


@pytest.mark.parametrize('change',['field','operator','query','root','duplicate'])
def test_unknown_source_drift_refused(change):
    d=source()
    if change=='field':d['actions']['Find_exact_occurrence']['inputs']['where']=d['actions']['Find_exact_occurrence']['inputs']['where'].replace("['subject']","['unknown']")
    if change=='operator':d['actions']['Find_exact_occurrence']['inputs']['where']=d['actions']['Find_exact_occurrence']['inputs']['where'].replace('startsWith','equals')
    if change=='query':d['actions']['Read_approved_window']['inputs']['parameters']['Uri']+='&unknown=1'
    if change=='root':d['actions']['unknown']={}
    if change=='duplicate':d['parameters'][BASELINE]={}
    before=deepcopy(d)
    with pytest.raises(ValueError):guarded_definition(d)
    assert d==before


@pytest.mark.parametrize('which',[0,1])
def test_empty_default_rejected_by_schema(which):
    validator=Draft7Validator(configuration_schemas()[which],format_checker=FormatChecker())
    assert list(validator.iter_errors({}))


def test_schema_baseline_types_and_timezone():
    schema=configuration_schemas()[0];v=Draft7Validator(schema,format_checker=FormatChecker())
    event={key:'fictional' for key in schema['properties']['event']['properties']}
    event.update(originalStart='2099-01-01T06:00:00Z',lastModifiedDateTime='2099-01-01T00:00:00Z',isCancelled=False,
                 organizer={'emailAddress':{'address':'fictional@example.invalid'}},
                 start={'dateTime':'2099-01-01T06:00:00','timeZone':'UTC'},end={'dateTime':'2099-01-01T07:00:00','timeZone':'UTC'})
    agenda={key:'fictional' for key in schema['properties']['agenda']['properties']}
    agenda.update(size=42,isInline=False,lastModifiedDateTime='2099-01-01T00:00:00Z')
    baseline={'event':event,'agenda':agenda,'checked_at':'2099-01-01T00:00:00Z','baseline_run_id':'fictional-run'}
    assert v.is_valid(baseline)
    for mutate in [lambda x:x['event']['start'].update(timeZone='Unknown'),lambda x:x['agenda'].update(size=True),lambda x:x['agenda'].update(isInline=True),lambda x:x.update(unknown=True),lambda x:x['event']['start'].update(dateTime='2099-01-01T06:00:00+10:00')]:
        bad=deepcopy(baseline);mutate(bad);assert not v.is_valid(bad)


def test_supported_schema_and_guard_pipeline_preserve_metadata_boundary():
    from scripts.f12_portable_definition import supported_schema, METADATA_FIELD
    raw = configuration_schemas()[0]
    schema = supported_schema(raw)
    assert 'pattern' not in json.dumps(schema)
    agenda = schema['properties']['agenda']
    assert METADATA_FIELD in agenda['required']
    assert agenda['properties'][METADATA_FIELD] == {'type':'string','minLength':1}
    result, _ = guarded_definition(source())
    parse = result['actions']['Parse_configuration']['actions']
    assert parse['Parse_baseline']['inputs']['content'] == "@parameters('comeet_F12Baseline')"
    assert "removeProperty" not in parse['Parse_baseline']['inputs']['content']
    assert parse['Text_validation_results']['runAfter'] == {'Parse_selection':['Succeeded']}
    assert parse['Invalid_text_fields']['runAfter'] == {'Text_validation_results':['Succeeded']}
    assert parse['Date_validation_results']['runAfter'] == {'Invalid_text_fields':['Succeeded']}
    assert parse['Invalid_date_fields']['runAfter'] == {'Date_validation_results':['Succeeded']}
    conditions = result['actions']['Require_configuration']['expression']
    assert "not(contains(parameters('comeet_F12Baseline')?['agenda'],'@odata.type'))" in conditions
    assert "length(body('Invalid_text_fields'))" in conditions
    assert "length(body('Invalid_date_fields'))" in conditions
    assert len(parse['Date_validation_results']['inputs']['select']['valid']) < 8192
    assert len(parse['Text_validation_results']['inputs']['select']['valid']) < 8192
    checks = result['actions']['Require_configuration']['actions']['Require_one_occurrence']['actions']['Require_one_agenda']['actions']['Observed_baseline']['inputs']['checks']
    assert "?['@odata.type']" in checks['agenda_graph_type']


def evaluate_shape(expression, value):
    from scripts.wdl_arguments import _split_args
    if expression == "item()?['value']": return value
    if expression == 'item()': return value
    if expression.startswith('@'): return evaluate_shape(expression[1:],value)
    if expression.startswith("'"): return expression[1:-1]
    if expression.isdigit(): return int(expression)
    if expression in ['true','false']: return expression == 'true'
    name, rest = expression.split('(', 1)
    args = _split_args(rest[:-1])
    if name == 'if':
        return evaluate_shape(args[1] if evaluate_shape(args[0],value) else args[2],value)
    values = [evaluate_shape(arg,value) for arg in args]
    if name == 'and': return all(values)
    if name == 'or': return any(values)
    if name == 'not': return not values[0]
    if name == 'empty': return not values[0]
    if name == 'equals': return values[0] == values[1]
    if name == 'greater': return values[0] > values[1]
    if name == 'length': return len(values[0])
    if name == 'sub': return values[0]-values[1]
    if name == 'replace': return values[0].replace(values[1],values[2])
    if name == 'decodeUriComponent':
        from urllib.parse import unquote
        return unquote(values[0])
    if name == 'startsWith': return values[0].startswith(values[1])
    if name == 'endsWith': return values[0].endswith(values[1])
    if name == 'substring':
        start = values[1]; size = values[2] if len(values)>2 else len(values[0])-start
        if start<0 or size<0 or start+size>len(values[0]): raise ValueError('substring range')
        return values[0][start:start+size]
    raise ValueError(name)


@pytest.mark.parametrize('utc',[False,True])
def test_generated_date_lexical_guard_matches_original_pattern(utc):
    import re
    from scripts.f12_portable_definition import date_shape
    raw = configuration_schemas()[0]['properties']['event']['properties']
    schema = raw['start']['properties']['dateTime'] if utc else raw['originalStart']
    cases = ['2099-01-01T06:00:00'+tail for tail in ['', 'Z', '+00:00', '-00:00', '+10:00', '-03:30', '.1Z', '.1234567+00:00', '.123', '.Z', '.aZ', '+0:00', '+000:00', 'z', ' Z', 'ZZ', '+aa:bb', '+00:00Z']]
    cases += ['', '2099/01/01T06:00:00Z', '2099-01-01 06:00:00Z', '209a-01-01T06:00:00Z', '2099-1-01T06:00:00Z']
    expression = date_shape("item()?['value']",utc)
    for value in cases:
        try: actual = evaluate_shape(expression,value)
        except ValueError: actual = False
        assert actual == bool(re.fullmatch(schema['pattern'],value)), value


def test_generated_nonblank_guard_matches_original_unicode_rule():
    import re
    result, _ = guarded_definition(source())
    expression = result['actions']['Parse_configuration']['actions']['Text_validation_results']['inputs']['select']['valid']
    whitespace = ''.join(chr(i) for i in range(0x3001) if chr(i).isspace())
    for value in ['', whitespace, 'ordinary', ' x ', '🙂', "'", *whitespace]:
        assert evaluate_shape(expression,value) == (re.search(r'\S',value) is not None)


def test_projected_metadata_schema_rejects_missing_wrong_type_and_extra_keys():
    from scripts.f12_portable_definition import supported_schema, METADATA_FIELD
    original = configuration_schemas()[0]['properties']['agenda']
    lowered = supported_schema(configuration_schemas()[0])['properties']['agenda']
    raw = {key:'fictional' for key in original['properties']}
    raw.update(size=42,isInline=False,lastModifiedDateTime='2099-01-01T00:00:00Z')
    def accepted(value):
        if METADATA_FIELD in value: return False
        projected = deepcopy(value)
        projected[METADATA_FIELD] = projected.pop('@odata.type',None)
        return Draft7Validator(lowered).is_valid(projected)
    assert accepted(raw)
    for key in raw:
        missing = deepcopy(raw); del missing[key]; assert not accepted(missing)
    for value in [None,42,True,[],{},'']:
        bad = deepcopy(raw); bad['@odata.type']=value; assert not accepted(bad)
    for key in ['unknown',METADATA_FIELD,'@odataXtype']:
        bad=deepcopy(raw);bad[key]='fictional';assert not accepted(bad)


def test_metadata_transport_roundtrip_and_comparator_operands():
    from scripts.f12_portable_definition import baseline_transport, METADATA_FIELD
    from scripts.f12_configuration import AGENDA_KEYS
    raw = {'agenda': {key:'fictional' for key in AGENDA_KEYS}, 'event': {'unchanged':'value'}}
    before = deepcopy(raw)
    encoded = baseline_transport(raw)
    assert raw == before
    assert baseline_transport(encoded, decode=True) == raw
    assert encoded['agenda'][METADATA_FIELD] == raw['agenda']['@odata.type']
    for key in ['unknown', METADATA_FIELD]:
        bad = deepcopy(raw); bad['agenda'][key]='collision'
        with pytest.raises(ValueError): baseline_transport(bad)
    bad = deepcopy(raw); del bad['agenda']['@odata.type']
    with pytest.raises(ValueError): baseline_transport(bad)
    result, _ = guarded_definition(source())
    checks = result['actions']['Require_configuration']['actions']['Require_one_occurrence']['actions']['Require_one_agenda']['actions']['Observed_baseline']['inputs']['checks']
    assert checks['agenda_graph_type'] == "@equals(first(body('Find_issued_agenda'))?['@odata.type'],parameters('comeet_F12Baseline')?['agenda']?['F12MetadataType'])"
    assert len(checks) == 21


def test_validation_diagnostics_contain_only_aggregate_results():
    result, _ = guarded_definition(source())
    parse = result['actions']['Parse_configuration']['actions']
    for name in ['Text_validation_results','Date_validation_results']:
        assert set(parse[name]['inputs']['select']) == {'valid'}
        assert parse[name]['runtimeConfiguration']['secureData']['properties'] == ['inputs']
    for name, producer in [('Invalid_text_fields','Text_validation_results'),('Invalid_date_fields','Date_validation_results')]:
        assert parse[name]['inputs'] == {'from': "@body('"+producer+"')",'where':"@not(item()?['valid'])"}
    receipt = result['actions']['Require_configuration']['else']['actions']['Configuration_mismatch']['inputs']
    assert receipt['validation'] == {
        'invalid_text_count':"@length(body('Invalid_text_fields'))",
        'invalid_date_count':"@length(body('Invalid_date_fields'))",
        'subject_matches':"@equals(parameters('comeet_F12Selection')?['subject'],parameters('comeet_F12Baseline')?['event']?['subject'])"}
    assert receipt['write_proposed'] is False and receipt['content_equality_verified'] is False


def test_instant_repair_changes_only_two_checks_and_their_exact_repetitions():
    import hashlib
    from scripts.f12_portable_definition import compare_event_instants
    candidate, _ = repair_metadata()
    # The small fixture has fewer display fields than the native five-use graph.
    _, _, fixture_stable = metadata_guard_parts(candidate)
    fixture_inputs = fixture_stable['actions']['Observed_baseline']['inputs']
    repeats = []
    for key in ('event_start', 'event_end'):
        expression = fixture_inputs['checks'][key][1:]
        repeats.extend(['@' + expression] * (5 - json.dumps(fixture_inputs).count(expression)))
    fixture_inputs['fixture_repeated_displays'] = repeats
    original = deepcopy(candidate)
    pin = hashlib.sha256(json.dumps(candidate, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode()).hexdigest()
    result, review = compare_event_instants(candidate, expected_sha256=pin,
                                           baseline_parameter='comeet_F12Baseline')
    assert candidate == original
    assert review['replacement_counts'] == {'event_start': 5, 'event_end': 5}
    _, _, stable = metadata_guard_parts(result)
    checks = stable['actions']['Observed_baseline']['inputs']['checks']
    _, _, old_stable = metadata_guard_parts(original)
    old_checks = old_stable['actions']['Observed_baseline']['inputs']['checks']
    for key in set(checks) - {'event_start', 'event_end'}:
        assert checks[key] == old_checks[key]
    for field in ('start', 'end'):
        assert checks['event_' + field] == (
            f"@equals(ticks(body('Read_event_metadata')?['{field}']?['dateTime']),"
            f"ticks(parameters('comeet_F12Baseline')?['event']?['{field}']?['dateTime']))")
    # Reverse exactly the two selected expressions: the entire graph must match.
    raw = json.dumps(result, sort_keys=True)
    for key in ('event_start', 'event_end'):
        raw = raw.replace(checks[key][1:], old_checks[key][1:])
    assert json.loads(raw) == original
    with pytest.raises(ValueError):
        compare_event_instants(candidate, expected_sha256='changed')
    repin = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()
    with pytest.raises(ValueError):
        compare_event_instants(result, expected_sha256=repin,
                               baseline_parameter='comeet_F12Baseline')


def test_instant_comparison_keeps_exact_100ns_precision():
    import re
    from datetime import date
    # Exact integer oracle for the selected UTC forms; never float/microseconds.
    def ticks(text):
        match = re.fullmatch(r'(\d{4}-\d\d-\d\d)T(\d\d):(\d\d):(\d\d)(?:\.(\d{1,7}))?(?:Z|\+00:00)?', text)
        if not match: raise ValueError('Unsupported UTC instant')
        day, hour, minute, second, fraction = match.groups()
        if int(hour) > 23 or int(minute) > 59 or int(second) > 59:
            raise ValueError('Invalid time')
        seconds = ((date.fromisoformat(day).toordinal()-1)*86400
                   + int(hour)*3600 + int(minute)*60 + int(second))
        return seconds*10_000_000 + int((fraction or '').ljust(7, '0'))
    base = '2026-09-28T06:00:00'
    for suffix in ['', 'Z', '.0000000', '.0000000Z', '+00:00']:
        assert ticks(base+suffix) == ticks(base+'Z')
    assert ticks(base+'.0000001Z') - ticks(base+'Z') == 1
    assert ticks('2026-09-28T06:00:01Z') - ticks(base+'Z') == 10_000_000
    for invalid in [base+'+10:00', base+'.00000001Z', 'bad', '2026-02-30T06:00:00Z']:
        with pytest.raises(ValueError): ticks(invalid)
