"""Local guarded F12 definition preparation; native qualification remains required."""
from copy import deepcopy
from urllib.parse import urlsplit, parse_qs
import re
from scripts.f12_comparator_binding import bind_comparator, _inputs, FIELDS
from scripts.f12_configuration import EVENT_KEYS, AGENDA_KEYS

BASELINE = 'comeet_F12Baseline'
SELECTION = 'comeet_F12Selection'
METADATA_FIELD = 'F12MetadataType'

EVENT_METADATA_FIELDS = (
    'id', 'subject', 'start', 'end', 'organizer', 'type', 'seriesMasterId',
    'iCalUId', 'originalStart', 'isCancelled', 'lastModifiedDateTime', 'changeKey',
)


def repair_calendar_metadata_reads(baseline, *, expected_sha256):
    """Prepare a pinned local candidate; never fetch, save, or accept a baseline.

    Resolve the occurrence, read its required event metadata, read attachments,
    then re-read the event. Only a stable event snapshot reaches the existing
    comparator. Native connector/API compatibility remains unqualified.
    """
    import hashlib
    import json
    import uuid

    pin = hashlib.sha256(json.dumps(baseline, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode()).hexdigest()
    if pin != expected_sha256:
        raise ValueError('F12 complete baseline drift')
    if baseline.get('properties', {}).get('state') != 'Stopped':
        raise ValueError('Stopped F12 baseline required')
    result = deepcopy(baseline)
    definition = result['properties']['definition']
    graph = definition['actions']['Require_configuration']['actions']
    if set(graph) != {'Read_approved_window', 'Find_exact_occurrence',
                      'Require_one_occurrence', 'Calendar_read_unverified'}:
        raise ValueError('F12 source graph drift')
    occurrence = graph['Require_one_occurrence']
    unique = "@and(equals(length(body('Find_exact_occurrence')),1),empty(body('Read_approved_window')?['@odata.nextLink']))"
    if occurrence.get('expression') != unique:
        raise ValueError('F12 unique occurrence/pagination guard drift')
    nested = occurrence['actions']
    if set(nested) != {'Read_agenda_metadata', 'Find_issued_agenda',
                       'Require_one_agenda', 'Attachment_read_unverified'}:
        raise ValueError('F12 attachment graph drift')
    agenda = nested['Require_one_agenda']
    if agenda.get('expression') != "@and(equals(length(body('Find_issued_agenda')),1),empty(body('Read_agenda_metadata')?['@odata.nextLink']))":
        raise ValueError('F12 unique attachment/pagination guard drift')
    if set(agenda['actions']) != {'Observed_baseline'}:
        raise ValueError('F12 comparator graph drift')

    window = graph['Read_approved_window']['inputs']['parameters']
    uri = window['Uri']
    match = re.search(r'&%24select=([A-Za-z0-9_%]+)&%24top=10', uri)
    if (not uri.startswith("@concat('https://graph.microsoft.com/v1.0/me/calendar/calendarView?")
            or not match or len(re.findall('&%24select=', uri)) != 1
            or window.get('Method') != 'GET'):
        raise ValueError('F12 bounded calendar query drift')
    from urllib.parse import unquote
    selected = unquote(match.group(1)).split(',')
    if {s.casefold() for s in selected} != {s.casefold() for s in EVENT_METADATA_FIELDS}:
        raise ValueError('F12 selected calendar metadata drift')
    permitted = [s for s in selected if s.casefold() != 'lastmodifieddatetime']
    window['Uri'] = uri[:match.start(1)] + '%2C'.join(permitted) + uri[match.end(1):]

    original_read = nested['Read_agenda_metadata']
    inputs = original_read['inputs']
    parameters = inputs['parameters']
    expected_attachment_uri = "@concat('https://graph.microsoft.com/v1.0/me/events/',uriComponent(first(body('Find_exact_occurrence'))?['id']),'/attachments?$select=id,name,size,lastModifiedDateTime,contentType,isInline&$top=10')"
    if (parameters.get('Uri') != expected_attachment_uri or parameters.get('Method') != 'GET'
            or parameters.get('CustomHeader1') != 'Prefer: outlook.timezone="UTC"'
            or inputs.get('retryPolicy', {}).get('type', '').lower() != 'none'
            or inputs.get('host', {}).get('operationId') != 'HttpRequest'
            or original_read.get('runAfter') != {}):
        raise ValueError('F12 attachment request contract drift')
    event_paths = [path[1:] for path in FIELDS.values() if path[0] == 'event']

    def value(action, path):
        return "body('" + action + "')" + ''.join("?['" + p + "']" for p in path)

    def present(action):
        conditions = []
        for path in event_paths:
            v = value(action, path)
            conditions.append(f'not(equals({v},null))' if path == ('isCancelled',)
                              else f'not(empty({v}))')
        modified = value(action, ('lastModifiedDateTime',))
        conditions += [f'greaterOrEquals(ticks({modified}),0)',
                       f'lessOrEquals(ticks({modified}),ticks(utcNow()))']
        return conditions

    def event_read(name, id_expression, after):
        action = deepcopy(original_read)
        action['inputs']['parameters']['Uri'] = (
            "@concat('https://graph.microsoft.com/v1.0/me/events/',uriComponent("
            + id_expression + "),'?$select=" + ','.join(EVENT_METADATA_FIELDS) + "')")
        action['runAfter'] = after
        action['metadata'] = {'operationMetadataId': str(uuid.uuid5(uuid.NAMESPACE_URL, 'F12/' + name))}
        return action

    def refusal(code, after=None):
        return {'type': 'Compose', 'runAfter': after or {}, 'inputs': {
            'state': 'unable_to_verify', 'code': code, 'write_proposed': False,
            'content_equality_verified': False,
            'next': 'Review the existing invitation and issued agenda manually.'}}

    # Compare every field actually selected in calendarView, including recurring
    # exception identity and changeKey. The modified timestamp comes from GET.
    before_conditions = present('Read_event_metadata')
    for path in event_paths:
        if path == ('lastModifiedDateTime',):
            continue
        observed = "first(body('Find_exact_occurrence'))" + ''.join("?['" + p + "']" for p in path)
        before_conditions.append(f"equals({value('Read_event_metadata', path)},{observed})")
    parameters['Uri'] = expected_attachment_uri.replace(
        "first(body('Find_exact_occurrence'))", "body('Read_event_metadata')")

    observed = agenda['actions']['Observed_baseline']
    def bind_exact_event(v):
        if isinstance(v, dict): return {k: bind_exact_event(x) for k, x in v.items()}
        if isinstance(v, list): return [bind_exact_event(x) for x in v]
        if isinstance(v, str): return v.replace("first(body('Find_exact_occurrence'))", "body('Read_event_metadata')")
        return v
    rewritten = bind_exact_event(observed)
    if rewritten == observed:
        raise ValueError('F12 observed event operands missing')
    stable = present('Read_event_after_agenda') + [
        f"equals({value('Read_event_after_agenda', path)},{value('Read_event_metadata', path)})"
        for path in event_paths]
    agenda['actions'] = {
        'Read_event_after_agenda': event_read('Read_event_after_agenda', "body('Read_event_metadata')?['id']", {}),
        'Event_after_agenda_unverified': refusal('EVENT_AFTER_AGENDA_READ_FAILED', {'Read_event_after_agenda': ['Failed', 'TimedOut']}),
        'Require_stable_event': {'type': 'If', 'runAfter': {'Read_event_after_agenda': ['Succeeded']},
            'expression': '@and(' + ','.join(stable) + ')',
            'actions': {'Observed_baseline': rewritten},
            'else': {'actions': {'Event_snapshot_changed': refusal('EVENT_CHANGED_DURING_ATTACHMENT_READ')}}}}
    occurrence['actions'] = {
        'Read_event_metadata': event_read('Read_event_metadata', "first(body('Find_exact_occurrence'))?['id']", {}),
        'Event_metadata_unverified': refusal('EVENT_METADATA_READ_FAILED', {'Read_event_metadata': ['Failed', 'TimedOut']}),
        'Require_event_metadata': {'type': 'If', 'runAfter': {'Read_event_metadata': ['Succeeded']},
            'expression': '@and(' + ','.join(before_conditions) + ')', 'actions': nested,
            'else': {'actions': {'Event_metadata_changed': refusal('EVENT_MISSING_FUTURE_OR_CHANGED')}}}}
    return result, {'baseline_sha256': pin, 'deployment_ready': False,
                    'request_order': ['calendarView', 'exact event', 'attachment metadata', 'exact event again'],
                    'remaining': 'Exact API/connector access, field compatibility, native save/run and output qualification; Graph403 remains separate.'}


def exact_source_qualification(baseline, *, expected_sha256, event_id, attachment_id,
                               baseline_parameter='F12 accepted metadata baseline (comeet_F12Baseline)'):
    """Prepare a metadata-only original-connection trial using retained API IDs.

    This is a bounded qualification candidate, not a replacement for the general
    selector. Neither URL tokens nor identifiers are decoded. The saved accepted
    baseline must already identify these sources; this helper never adopts one.
    """
    for identifier in (event_id, attachment_id):
        if (not isinstance(identifier, str) or not identifier.strip()
                or len(identifier) > 2048 or any(ord(c) < 32 for c in identifier)):
            raise ValueError('Exact retained service identifiers required')
    result, review = repair_calendar_metadata_reads(baseline, expected_sha256=expected_sha256)
    definition = result['properties']['definition']
    if baseline_parameter not in definition.get('parameters', {}):
        raise ValueError('Existing accepted baseline parameter missing')
    guard = definition['actions']['Require_configuration']
    expected = "parameters(" + literal(baseline_parameter) + ")"
    guard['expression'] = ('@and(' + guard['expression'][1:]
        + ',equals(' + expected + "?['event']?['id']," + literal(event_id) + ')'
        + ',equals(' + expected + "?['agenda']?['id']," + literal(attachment_id) + '))')
    graph = guard['actions']
    graph['Read_approved_window']['inputs']['parameters']['Uri'] = (
        "@concat('https://graph.microsoft.com/v1.0/me/events/',uriComponent("
        + literal(event_id) + "),'?$select=" + ','.join(EVENT_METADATA_FIELDS) + "')")
    graph['Find_exact_occurrence']['inputs']['from'] = "@createArray(body('Read_approved_window'))"
    nested = graph['Require_one_occurrence']['actions']['Require_event_metadata']['actions']
    nested['Read_agenda_metadata']['inputs']['parameters']['Uri'] = (
        "@concat('https://graph.microsoft.com/v1.0/me/events/',uriComponent("
        + literal(event_id) + "),'/attachments/',uriComponent(" + literal(attachment_id)
        + "),'?$select=id,name,size,lastModifiedDateTime,contentType,isInline')")
    nested['Find_issued_agenda']['inputs']['from'] = "@createArray(body('Read_agenda_metadata'))"
    return result, {**review, 'deployment_ready': False,
        'request_order': ['exact event', 'exact event again', 'exact attachment metadata', 'exact event after attachment'],
        'scope': 'Only retained exact source IDs through the original connection; no calendar search or baseline adoption.',
        'remaining': 'Fresh original binding/account, feature/journal preflight, native access/field/output proof and original Off restoration.'}


def compare_event_instants(candidate, *, expected_sha256,
                           baseline_parameter='F12 accepted metadata baseline (comeet_F12Baseline)'):
    """Repair only start/end lexical equality after native JSON normalization.

    Existing configuration/date/UTC/identity guards remain prerequisites. ticks()
    preserves WDL's 100 ns precision; neither timestamps nor zones are rewritten.
    """
    import hashlib
    import json
    pin = hashlib.sha256(json.dumps(candidate, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode()).hexdigest()
    if pin != expected_sha256:
        raise ValueError('F12 instant comparator source drift')
    result = deepcopy(candidate)
    actions = result['properties']['definition']['actions']
    stable = (actions['Require_configuration']['actions']['Require_one_occurrence']
              ['actions']['Require_event_metadata']['actions']['Require_one_agenda']
              ['actions']['Require_stable_event'])
    inputs = stable['actions']['Observed_baseline']['inputs']
    if set(inputs['checks']) != set(FIELDS):
        raise ValueError('Exact 21 comparator checks required')
    replacements = {}
    for field in ('start', 'end'):
        observed = f"body('Read_event_metadata')?['{field}']?['dateTime']"
        expected = f"parameters('{baseline_parameter}')?['event']?['{field}']?['dateTime']"
        old = f'equals({observed},{expected})'
        if inputs['checks'][f'event_{field}'] != '@' + old:
            raise ValueError('F12 instant comparator operand drift')
        replacements[old] = f'equals(ticks({observed}),ticks({expected}))'
    counts = {old: 0 for old in replacements}

    def rewrite(value):
        if isinstance(value, dict): return {k: rewrite(v) for k, v in value.items()}
        if isinstance(value, list): return [rewrite(v) for v in value]
        if isinstance(value, str):
            for old, new in replacements.items():
                counts[old] += value.count(old)
                value = value.replace(old, new)
        return value

    rewritten = rewrite(inputs)
    if any(count != 5 for count in counts.values()):
        raise ValueError('F12 repeated instant comparator count drift')
    stable['actions']['Observed_baseline']['inputs'] = rewritten
    return result, {'source_sha256': pin, 'replacement_counts': dict(zip(
        ('event_start', 'event_end'), counts.values())),
        'scope': 'Only start/end equality and its five repeated displays; all guards and 19 other checks unchanged.',
        'native_binding_qualification': 'Still required; no source values, zones or provenance changed.'}


def historical_commissioning_inputs(candidate, baseline, selection):
    """Bind supplied historical inputs for a reversible trial, never adopt them.

    Distinct parameter names without schemaName prevent solution environment
    resolution from replacing these inputs. The caller retains/restores the
    complete native preimage; this pure transformation performs no tenant I/O.
    """
    import json
    from scripts.f12_configuration import validate_configuration
    from scripts.f12_operator_inputs import FIELDS as OPERATOR_FIELDS

    validate_configuration(json.dumps(baseline, separators=(',', ':')),
                           json.dumps(selection, separators=(',', ':')))
    result = deepcopy(candidate)
    properties = result['properties']
    if properties.get('parameters'):
        raise ValueError('Unexpected runtime parameter overrides')
    definition = properties['definition']
    controls = definition['triggers']['manual']['inputs']['schema']['properties']
    if set(controls) != {'configuration_mode', *OPERATOR_FIELDS}:
        raise ValueError('Existing five-field operator contract required')
    names = {
        'F12 accepted metadata baseline (comeet_F12Baseline)':
            ('F12 historical commissioning baseline', 'comeet_F12Baseline', baseline_transport(baseline)),
        'F12 metadata selection (comeet_F12Selection)':
            ('F12 historical commissioning selection', 'comeet_F12Selection', selection),
    }
    parameters = definition['parameters']
    for old, (new, schema, value) in names.items():
        current = parameters.get(old, {})
        if (new in parameters or current.get('type') != 'Object'
                or current.get('defaultValue') != {}
                or current.get('metadata', {}).get('schemaName') != schema):
            raise ValueError('Historical commissioning parameter contract drift')
        del parameters[old]
        parameters[new] = {'type': 'Object', 'defaultValue': deepcopy(value)}

    def rewrite(value):
        if isinstance(value, dict): return {k: rewrite(v) for k, v in value.items()}
        if isinstance(value, list): return [rewrite(v) for v in value]
        if isinstance(value, str):
            for old, (new, _, _) in names.items():
                value = value.replace("parameters('" + old + "')", "parameters('" + new + "')")
        return value

    definition['actions'] = rewrite(definition['actions'])
    return result


def baseline_transport(value, *, decode=False):
    """Lossless annotation-name transport; does not validate or accept a baseline."""
    result = deepcopy(value)
    source, target = (METADATA_FIELD, '@odata.type') if decode else ('@odata.type', METADATA_FIELD)
    agenda = result.get('agenda') if isinstance(result, dict) else None
    expected = (AGENDA_KEYS - {'@odata.type'}) | ({METADATA_FIELD} if decode else {'@odata.type'})
    if not isinstance(agenda, dict) or set(agenda) != expected:
        raise ValueError('agenda: exact transport keys required')
    agenda[target] = agenda.pop(source)
    return result


def digitless(value):
    for digit in '0123456789':
        value = f"replace({value},'{digit}','')"
    return value


def date_shape(value, utc=False):
    """Lexical ISO shape only; calendar validity remains checked by ticks()."""
    prefix = f'substring({value},0,19)'
    tail = f'substring({value},19)'
    offset = f'substring({value},sub(length({value}),6),6)'
    signed = f"or(startsWith({offset},'+'),startsWith({offset},'-'))"
    fraction = f"if(endsWith({value},'Z'),substring({tail},0,sub(length({tail}),1)),if({signed},substring({tail},0,sub(length({tail}),6)),{tail}))"
    offset_digits = f"replace(substring({offset},1),':','')"
    zone = f"or(endsWith({value},'Z'),and({signed},equals(substring({offset},3,1),':'),empty({digitless(offset_digits)})))"
    if utc:
        zone = f"or(endsWith({value},'Z'),endsWith({value},'+00:00'),and(not({signed}),not(endsWith({value},'Z'))))"
    parts = [f"equals(substring({prefix},{i},1),'{c}')" for i,c in [(4,'-'),(7,'-'),(10,'T'),(13,':'),(16,':')]]
    digits = prefix
    for c in ['-',':','T']:
        digits = f"replace({digits},'{c}','')"
    parts += [f'empty({digitless(digits)})', zone,
              f"if(empty({fraction}),true,and(startsWith({fraction},'.'),greater(length({fraction}),1),empty({digitless(f'substring({fraction},1)')})))"]
    return 'and(' + ','.join(parts) + ')'


def supported_schema(schema):
    """Preserve types/shape while moving unsupported patterns to explicit guards."""
    result = deepcopy(schema)
    def strip(value):
        if isinstance(value, dict):
            value.pop('pattern', None)
            for child in value.values(): strip(child)
        elif isinstance(value, list):
            for child in value: strip(child)
    strip(result)
    if 'agenda' in result['properties']:
        agenda = result['properties']['agenda']
        agenda['properties'][METADATA_FIELD] = agenda['properties'].pop('@odata.type')
        agenda['required'][agenda['required'].index('@odata.type')] = METADATA_FIELD
    return result


def object_schema(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def configuration_schemas():
    text = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
    instant = {**text, 'format': 'date-time', 'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$'}
    event = {k: deepcopy(text) for k in sorted(EVENT_KEYS)}
    utc_time = {**text, 'minLength': 19, 'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)?$'}
    event.update(organizer=object_schema({'emailAddress': object_schema({'address': text})}),
                 start=object_schema({'dateTime': utc_time, 'timeZone': {'enum': ['UTC'], 'type': 'string'}}),
                 end=object_schema({'dateTime': utc_time, 'timeZone': {'enum': ['UTC'], 'type': 'string'}}),
                 isCancelled={'type': 'boolean'})
    for k in ['originalStart', 'lastModifiedDateTime']:
        event[k] = instant
    agenda = {k: deepcopy(text) for k in sorted(AGENDA_KEYS)}
    agenda.update(size={'type': 'integer', 'minimum': 0}, isInline={'type': 'boolean', 'enum': [False]}, lastModifiedDateTime=instant)
    return (object_schema({'event': object_schema(event), 'agenda': object_schema(agenda),
                           'checked_at': instant, 'baseline_run_id': text}),
            object_schema({'window_start': instant, 'window_end': instant, 'subject': text,
                           'organizer': text, 'agenda_name': text}))


def b(*path):
    path = tuple(METADATA_FIELD if p == '@odata.type' else p for p in path)
    return f"parameters('{BASELINE}')" + ''.join(f"?['{p}']" for p in path)


def s(key):
    return f"parameters('{SELECTION}')?['{key}']"


def literal(value):
    return "'" + value.replace("'", "''") + "'"


def guarded_definition(definition):
    if set(definition['actions']) != {'Read_approved_window', 'Find_exact_occurrence', 'Require_one_occurrence', 'Calendar_read_unverified'}:
        raise ValueError('definition: unexpected root actions')
    result, receipt = bind_comparator(definition)
    graph = result['actions']
    if graph['Read_approved_window'].get('runAfter') != {}:
        raise ValueError('calendar read: unexpected dependency')
    params = graph['Read_approved_window']['inputs']['parameters']
    uri = urlsplit(params['Uri']); query = parse_qs(uri.query)
    if uri.scheme != 'https' or uri.netloc != 'graph.microsoft.com' or uri.path != '/v1.0/me/calendar/calendarView' or set(query) != {'startDateTime','endDateTime','$filter','$select','$top'} or query['$top'] != ['10']:
        raise ValueError('calendar read: unexpected query contract')
    # Graph calendarView does not support selecting these event properties.
    # Do not silently drop them: the comparator still requires event provenance.
    selected = {field.strip().casefold() for field in query['$select'][0].split(',')}
    if selected & {'createddatetime', 'lastmodifieddatetime'}:
        raise ValueError(
            'calendar read: createdDateTime/lastModifiedDateTime cannot be selected '
            'in calendarView; resolve one event, then qualify its exact metadata read')
    quote = "decodeUriComponent('%27')"
    escaped = f"replace({s('subject')},{quote},concat({quote},{quote}))"
    query_filter = f"concat('subject eq ',{quote},{escaped},{quote})"
    params['Uri'] = ("@concat('https://graph.microsoft.com/v1.0/me/calendar/calendarView?startDateTime=',"
                     f"uriComponent({s('window_start')}),'&endDateTime=',uriComponent({s('window_end')}),"
                     f"'&%24filter=',uriComponent({query_filter}),"
                     + literal('&%24select=' + query['$select'][0].replace(',', '%2C') + '&%24top=10') + ')')
    # Refuse unknown selector operators instead of treating an arbitrary filter as replaceable.
    event_filter = graph['Find_exact_occurrence']['inputs']['where']
    skeleton = re.sub(r",'(?:[^']|'')*'(?=\))", ",'X'", event_filter)
    expected = "@and(equals(item()?['subject'],'X'),equals(toLower(coalesce(item()?['organizer']?['emailAddress']?['address'],'X')),'X'),startsWith(coalesce(item()?['start']?['dateTime'],'X'),'X'),startsWith(coalesce(item()?['end']?['dateTime'],'X'),'X'),equals(item()?['start']?['timeZone'],'X'),equals(item()?['end']?['timeZone'],'X'),not(empty(item()?['id'])))"
    if skeleton != expected:
        raise ValueError('event selector: unexpected expression')
    # Existing source uses whole-second prefixes and UTC zones; preserve these semantics.
    filters = [f"equals(item()?['subject'],{s('subject')})",
               f"equals(toLower(coalesce(item()?['organizer']?['emailAddress']?['address'],'')),toLower({s('organizer')}))"]
    for key in ['start','end']:
        filters += [f"startsWith(coalesce(item()?['{key}']?['dateTime'],''),substring({b('event',key,'dateTime')},0,19))",
                    f"equals(item()?['{key}']?['timeZone'],{b('event',key,'timeZone')})"]
    filters.append("not(empty(item()?['id']))")
    graph['Find_exact_occurrence']['inputs']['where'] = '@and(' + ','.join(filters) + ')'
    nested = graph['Require_one_occurrence']['actions']
    agenda_filter = nested['Find_issued_agenda']['inputs']['where']
    if re.sub(r",'(?:[^']|'')*'(?=\))", ",'X'", agenda_filter) != "@and(equals(item()?['name'],'X'),equals(item()?['isInline'],false))":
        raise ValueError('agenda selector: unexpected expression')
    nested['Find_issued_agenda']['inputs']['where'] = f"@and(equals(item()?['name'],{s('agenda_name')}),equals(item()?['isInline'],false))"
    inputs = _inputs(result)
    # Rewrite only expected baseline access; observed Graph operands retain @odata.type.
    old = f"parameters('{BASELINE}')?['agenda']?['@odata.type']"
    new = b('agenda', '@odata.type')
    def transport_expected(value):
        if isinstance(value, dict): return {k: transport_expected(v) for k,v in value.items()}
        if isinstance(value, list): return [transport_expected(v) for v in value]
        if isinstance(value, str): return value.replace(old, new)
        return value
    transported = transport_expected(inputs)
    inputs.clear()
    inputs.update(transported)
    inputs['baseline_run_id'] = '@' + b('baseline_run_id')
    inputs['baseline_checked_at'] = '@' + b('checked_at')
    inputs['scope'] = 'Selected event and issued agenda metadata only; content equality is unverified.'
    inputs['meeting_checked'] = f"@concat({b('event','subject')},' / ',{b('event','start','dateTime')})"
    for key in [BASELINE,SELECTION]:
        if key in result['parameters']:
            raise ValueError('parameters: configuration already declared')
        result['parameters'][key] = {'type': 'Object', 'defaultValue': {}}
    baseline_schema, selection_schema = configuration_schemas()
    baseline_schema, selection_schema = supported_schema(baseline_schema), supported_schema(selection_schema)
    # ParseJson supports Secure Inputs only; this also hides its outputs.
    secure = {'secureData': {'properties': ['inputs']}}
    parse = {
        'Parse_baseline': {'type':'ParseJson','inputs':{'content':f"@parameters('{BASELINE}')",'schema':baseline_schema},'runAfter':{},'runtimeConfiguration':secure},
        'Parse_selection': {'type':'ParseJson','inputs':{'content':f"@parameters('{SELECTION}')",'schema':selection_schema},'runAfter':{'Parse_baseline':['Succeeded']},'runtimeConfiguration':secure}}
    texts = [b('event', key) for key in sorted(EVENT_KEYS - {'organizer','start','end','isCancelled'})]
    texts += [b('agenda', key) for key in sorted(AGENDA_KEYS - {'size','isInline'})]
    texts += [b('baseline_run_id'), b('checked_at'), b('event','organizer','emailAddress','address')]
    texts += [s(key) for key in ['window_start','window_end','subject','organizer','agenda_name']]
    texts += [b('event', key, 'dateTime') for key in ['start','end']]
    nonblank = 'item()'
    # Python JSON-schema \S and the local validator share this whitespace set.
    from urllib.parse import quote
    for character in ''.join(chr(i) for i in range(0x3001) if chr(i).isspace()):
        nonblank = f"replace({nonblank},decodeUriComponent('{quote(character, safe='')}'),'')"
    parse['Text_validation_results'] = {'type':'Select','inputs':{'from':['@'+value for value in texts], 'select':{'valid':'@not(empty('+nonblank+'))'}},'runAfter':{'Parse_selection':['Succeeded']},'runtimeConfiguration':secure}
    parse['Invalid_text_fields'] = {'type':'Query','inputs':{'from':"@body('Text_validation_results')", 'where':"@not(item()?['valid'])"},'runAfter':{'Text_validation_results':['Succeeded']}}
    dates = [(b(*path),False) for path in [('checked_at',),('event','originalStart'),('event','lastModifiedDateTime'),('agenda','lastModifiedDateTime')]]
    dates += [(s(key),False) for key in ['window_start','window_end']]
    dates += [(b('event',key,'dateTime'),True) for key in ['start','end']]
    date_value = "item()?['value']"
    date_guard = f"@if(item()?['utc'],{date_shape(date_value, True)},{date_shape(date_value)})"
    parse['Date_validation_results'] = {'type':'Select','inputs':{'from':[{'value':'@'+value,'utc':utc} for value,utc in dates], 'select':{'valid':date_guard}},'runAfter':{'Invalid_text_fields':['Succeeded']},'runtimeConfiguration':secure}
    parse['Invalid_date_fields'] = {'type':'Query','inputs':{'from':"@body('Date_validation_results')", 'where':"@not(item()?['valid'])"},'runAfter':{'Date_validation_results':['Succeeded']}}
    conditions = [f"lessOrEquals(length(string(parameters('{key}'))),2000)" for key in [BASELINE,SELECTION]]
    conditions += ["equals(length(body('Invalid_text_fields')),0)", "equals(length(body('Invalid_date_fields')),0)",
                   f"not(contains({b('agenda')},'@odata.type'))"]
    conditions += [f"equals({s('subject')},{b('event','subject')})",
                   f"equals(toLower({s('organizer')}),toLower({b('event','organizer','emailAddress','address')}))",
                   f"equals({s('agenda_name')},{b('agenda','name')})",
                   f"lessOrEquals(ticks({s('window_start')}),ticks({b('event','start','dateTime')}))",
                   f"less(ticks({b('event','start','dateTime')}),ticks({b('event','end','dateTime')}))",
                   f"lessOrEquals(ticks({b('event','end','dateTime')}),ticks({s('window_end')}))"]
    for path in [('checked_at',),('event','originalStart'),('event','lastModifiedDateTime'),('agenda','lastModifiedDateTime')]:
        conditions.append(f"greaterOrEquals(ticks({b(*path)}),0)")
    invalid = {'type':'Compose','inputs':{'state':'unable_to_verify','reason':'CONFIGURATION_INVALID','write_proposed':False,'content_equality_verified':False,'next':'Check supplied configuration and compare invitation/agenda manually.'},'runAfter':{}}
    mismatch = deepcopy(invalid)
    mismatch['inputs']['validation'] = {
        'invalid_text_count': "@length(body('Invalid_text_fields'))",
        'invalid_date_count': "@length(body('Invalid_date_fields'))",
        'subject_matches': '@equals('+s('subject')+','+b('event','subject')+')'}
    result['actions'] = {
        'Parse_configuration': {'type':'Scope','actions':parse,'runAfter':{}},
        'Require_configuration': {'type':'If','expression':'@and('+','.join(conditions)+')','actions':graph,
                                   'else':{'actions':{'Configuration_mismatch':mismatch}},
                                   'runAfter':{'Parse_configuration':['Succeeded']}},
        'Configuration_unverified': {**deepcopy(invalid),'runAfter':{'Parse_configuration':['Failed','TimedOut']}},
        'Guard_or_execution_unverified': {**deepcopy(invalid), 'inputs': {**invalid['inputs'], 'reason': 'CONFIGURATION_OR_EXECUTION_UNVERIFIED', 'next': 'Inspect configuration and source-read outcomes; compare invitation/agenda manually.'}, 'runAfter':{'Require_configuration':['Failed','TimedOut']}}}
    return result, {**receipt,'configuration_guard':'Invalid configuration blocks reads; guard or execution failures return an unverified outcome.',
                    'remaining':'Native schema/expression, environment-variable binding and runtime qualification.'}
