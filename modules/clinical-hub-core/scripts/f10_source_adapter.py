"""Build guarded coherent-source F10 commissioning graphs from private bindings."""
from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime
from urllib.parse import quote, unquote, urlsplit

BASELINE_ACTIONS = {
    'Fixed_Fictional_Cases', 'Evaluate_Supplied_Claims', 'Classify_For_Review',
    'Proposed_Review_Items', 'Excluded_Review_Items', 'Blocking_Exceptions',
    'Review_Preview',
}
CLASSIFIER_ACTIONS = {
    'Evaluate_Supplied_Claims', 'Classify_For_Review',
    'Proposed_Review_Items', 'Excluded_Review_Items', 'Blocking_Exceptions',
}
CONNECTOR = '/providers/Microsoft.PowerApps/apis/shared_sharepointonline'

AGENDA_CARRY_FIELDS = {'Title', 'Question_x0020_or_x0020_help_x00', 'Meeting_x0020_date'}


def carry_identity_key(source_id: str, record_id: str | int, meeting_id: str) -> str:
    """Reference for the native concat/string/uriComponent key; no runtime host.

    Only the native List GUID is canonicalised. Native integer item IDs become
    decimal; historical action and opaque meeting identifiers retain case.
    A SharePoint collation collision must be refused, never merged or rewritten.
    """
    source = str(uuid.UUID(source_id))
    if type(record_id) is int and record_id > 0:
        record_id = str(record_id)
    if any(not isinstance(x, str) or not x.strip() for x in (record_id, meeting_id)):
        raise ValueError('Nonempty stable action and meeting identities are required')
    safe = "~!*'().-_"
    key = 'f10:native1|' + source + '|' + quote(record_id, safe=safe) + '|' + quote(meeting_id, safe=safe)
    if len(key) > 255:
        raise ValueError('Carry identity exceeds native Text limit; do not truncate or change identity')
    return key


def agenda_identity_field() -> dict:
    """Return maker configuration only; no creation, backfill or permission grant.

    Existing rows retain null keys. Native multiple-null compatibility must be
    established before deployment; failure must not prompt historical backfill.
    Bind the actual saved internal name after native schema readback.
    """
    return {'parameters': {'SchemaXml': (
        '<Field Type="Text" Name="CarryForwardKey" StaticName="CarryForwardKey" '
        'DisplayName="CarryForwardKey" Required="FALSE" Indexed="TRUE" '
        'EnforceUniqueValues="TRUE" MaxLength="255" '
        'ShowInNewForm="FALSE" ShowInEditForm="FALSE" ShowInDisplayForm="FALSE" />'),
        'Options': 0}}


def reconcile_agenda_identity(rows: list, *, key: str, expected_fields: dict,
                              field_name: str = 'CarryForwardKey') -> dict:
    """Resolve an exact scoped native read without changing text or F11 state.

    The caller must separately establish scope, access, schema/uniqueness and
    current readback. NOT_FOUND is not permission to create. Unique-constraint
    conflicts/uncertain creates require one new read, never blind POST retry.
    """
    parts = key.split('|') if isinstance(key, str) else []
    if len(parts) != 4 or parts[0] != 'f10:native1':
        raise ValueError('A canonical production carry identity is required')
    if carry_identity_key(parts[1], unquote(parts[2]), unquote(parts[3])) != key:
        raise ValueError('A canonical production carry identity is required')
    if (not isinstance(rows, list) or any(not isinstance(x, dict) for x in rows)
            or not isinstance(expected_fields, dict) or set(expected_fields) != AGENDA_CARRY_FIELDS
            or any(not isinstance(v, str) or not v.strip() for v in expected_fields.values())):
        raise ValueError('Complete scoped rows and the three existing carry fields are required')
    if (not isinstance(field_name, str) or not field_name.isascii()
            or not field_name or not field_name[0].isalpha()
            or not field_name.replace('_', '').isalnum()
            or field_name in AGENDA_CARRY_FIELDS
            or field_name == 'Agenda_x0020_review_x0020_bindin'):
        raise ValueError('A separate native carry-key field binding is required')
    matches = [r for r in rows if isinstance(r.get(field_name), str)
               and r[field_name].casefold() == key.casefold()]
    base = {'external_write': False, 'operational_acceptance': False}
    if not matches:
        return {**base, 'status': 'NOT_FOUND'}
    if len(matches) != 1:
        return {**base, 'status': 'AMBIGUOUS_IDENTITY'}
    row = matches[0]
    if row[field_name] != key or any(row.get(k) != v for k, v in expected_fields.items()):
        return {**base, 'status': 'HUMAN_EDIT_OR_SOURCE_CHANGE'}
    item_id = row.get('Id')
    version = row.get('OData__UIVersionString')
    etag = row.get('odata.etag', row.get('@odata.etag'))
    if (type(item_id) is not int or item_id < 1 or not isinstance(version, str) or not version
            or not isinstance(etag, str) or not etag or etag == '*'):
        return {**base, 'status': 'UNVERIFIED_NATIVE_IDENTITY'}
    return {**base, 'status': 'EXISTING_MATCH', 'item_id': item_id,
            'item_revision': version, 'etag': etag}


def _check_bindings(*, site: str, list_id: str, description: str,
                    row_id: str | int, reference: str) -> tuple[str, str]:
    parsed = urlsplit(site)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('A site origin is required')
    try:
        canonical_list_id = str(uuid.UUID(list_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValueError('A valid fixed List ID is required') from exc
    if not isinstance(description, str) or 'Synthetic technical commissioning only.' not in description or not reference or not isinstance(reference, str):
        raise ValueError('A fixed List description and connection reference are required')
    row = str(row_id)
    if not row.isdigit() or int(row) < 1:
        raise ValueError('A positive fixed source row ID is required')
    return parsed.geturl().rstrip('/'), canonical_list_id


def build_trial(baseline: dict, *, site: str, list_id: str, description: str,
                row_id: str | int, reference: str,
                expected_operation_key: str = 'F10-COHERENT-SNAPSHOT1',
                expected_source_revision: str = 'fictional-v7') -> dict:
    """Return a complete cloned clientdata object with guarded GET-only reads."""
    for name, value in (('expected operation key', expected_operation_key),
                        ('expected source revision', expected_source_revision)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'A nonempty {name} is required')
    site, list_id = _check_bindings(site=site, list_id=list_id, description=description,
                                    row_id=row_id, reference=reference)
    result = copy.deepcopy(baseline)
    props = result['properties']
    definition = props['definition']
    definition.setdefault('parameters', {}).setdefault('$connections', {'defaultValue': {}, 'type': 'Object'})
    actions = definition['actions']
    if set(actions) != BASELINE_ACTIONS or props.get('connectionReferences'):
        raise ValueError('Unexpected F10 baseline actions or connector references')
    if set(definition.get('triggers', {})) != {'manual'}:
        raise ValueError('Expected the F10 manual trigger')
    original_preview = copy.deepcopy(actions['Review_Preview']['inputs'])
    classifier = {name: copy.deepcopy(actions[name]) for name in CLASSIFIER_ACTIONS}
    fixed = copy.deepcopy(actions['Fixed_Fictional_Cases'])
    fixed['inputs'] = "@json(body('Read_snapshot')?['SnapshotJson'])?['records']"
    classifier['Evaluate_Supplied_Claims']['runAfter'] = {'Fixed_Fictional_Cases': ['Succeeded']}

    props['connectionReferences'] = {
        'shared_sharepointonline': {
            'runtimeSource': 'invoker',
            'connection': {'connectionReferenceLogicalName': reference},
            'api': {'name': 'shared_sharepointonline'},
        }
    }
    target = f"_api/web/lists(guid'{list_id}')"

    def get(name: str, uri: str, after: dict | None = None) -> dict:
        return {
            'type': 'OpenApiConnection',
            'inputs': {
                'host': {'apiId': f'/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                         'connectionName': 'shared_sharepointonline', 'operationId': 'HttpRequest'},
                'parameters': {'dataset': site, 'parameters/method': 'GET',
                               'parameters/uri': uri,
                               'parameters/headers': {'Accept': 'application/json;odata=nometadata'}},
                'authentication': "@parameters('$authentication')",
                'retryPolicy': {'type': 'none'},
            },
            'runAfter': after or {},
        }

    list_guard = "@and(equals(body('Read_fixture_identity')?['Id'],'" + list_id + "'),equals(body('Read_fixture_identity')?['Description'],'" + description.replace("'", "''") + "'),equals(body('Read_fixture_identity')?['EnableVersioning'],true))"
    row_uri = target + f"/items({int(row_id)})?$select=Id,OperationKey,SourceRevision,SnapshotJson,OData__UIVersionString"
    snapshot_read = get('Read_snapshot', row_uri)
    parsed_read = {
        'type': 'Compose', 'inputs': "@json(body('Read_snapshot')?['SnapshotJson'])",
        'runAfter': {'Read_snapshot': ['Succeeded']},
    }
    ids = {
        'type': 'Select', 'inputs': {'from': "@outputs('Parsed_snapshot')?['records']", 'select': "@item()?['record_id']"},
        'runAfter': {'Parsed_snapshot': ['Succeeded']},
    }
    operation_key_literal = "'" + expected_operation_key.replace("'", "''") + "'"
    source_revision_literal = "'" + expected_source_revision.replace("'", "''") + "'"
    source_check = "@and(equals(body('Read_snapshot')?['Id']," + str(int(row_id)) + "),equals(body('Read_snapshot')?['OperationKey']," + operation_key_literal + "),equals(body('Read_snapshot')?['SourceRevision']," + source_revision_literal + "),not(empty(body('Read_snapshot')?['OData__UIVersionString'])),equals(outputs('Parsed_snapshot')?['synthetic_only'],true),not(empty(outputs('Parsed_snapshot')?['meeting_id'])),equals(outputs('Parsed_snapshot')?['source_revision'],body('Read_snapshot')?['SourceRevision']),equals(length(outputs('Parsed_snapshot')?['records']),3),not(contains(body('Snapshot_IDs'),null)),not(contains(body('Snapshot_IDs'),'')),equals(length(union(body('Snapshot_IDs'),body('Snapshot_IDs'))),3))"

    after_read = get('Read_snapshot_after_classification', row_uri,
                     after={'Proposed_Review_Items': ['Succeeded'], 'Excluded_Review_Items': ['Succeeded'],
                            'Blocking_Exceptions': ['Succeeded']})
    stable = "@and(equals(body('Read_snapshot_after_classification')?['OData__UIVersionString'],body('Read_snapshot')?['OData__UIVersionString']),equals(body('Read_snapshot_after_classification')?['SnapshotJson'],body('Read_snapshot')?['SnapshotJson']))"
    preview = copy.deepcopy(original_preview)
    preview.update({
        'meeting': "@outputs('Parsed_snapshot')?['meeting_id']",
        'meeting_id': "@outputs('Parsed_snapshot')?['meeting_id']",
        'source': 'Isolated coherent synthetic native snapshot; no live register read',
        'source_id': "@outputs('Parsed_snapshot')?['source_id']",
        'source_row_version': "@body('Read_snapshot')?['OData__UIVersionString']",
        'source_revision': "@body('Read_snapshot')?['SourceRevision']",
        'source_row_id': "@body('Read_snapshot')?['Id']",
        'status': 'PROPOSAL_ONLY',
        'claims_status': 'UNVERIFIED_FICTIONAL_INPUT',
        'readonly_replay': True,
        'not_persisted': True,
        'idempotency': 'readonlyreplaynotpersistedidempotency',
    })
    preview_action = {
        'type': 'If', 'expression': stable,
        'runAfter': {'Read_snapshot_after_classification': ['Succeeded']},
        'actions': {'Stable_source_proposal': {'type': 'Compose', 'inputs': preview, 'runAfter': {}}},
        'else': {'actions': {'SOURCE_CHANGED_REFUSED': {
            'type': 'Compose', 'inputs': {'status': 'SOURCE_CHANGED_REFUSED', 'review_suppressed': True,
                                          'register_updated': False, 'notified': False}, 'runAfter': {}}}},
    }
    source_actions = {'Fixed_Fictional_Cases': fixed, **classifier,
                      'Read_snapshot_after_classification': after_read,
                      'Review_Preview': preview_action}
    guarded_source = {
        'type': 'If', 'expression': source_check,
        'runAfter': {'Snapshot_IDs': ['Succeeded']},
        'actions': source_actions,
        'else': {'actions': {'Invalid_snapshot_refused': {
            'type': 'Compose', 'inputs': {'status': 'SOURCE_INVALID_REFUSED', 'review_suppressed': True}, 'runAfter': {}}}},
    }
    list_guard_action = {
        'type': 'If', 'expression': list_guard,
        'runAfter': {'Read_fixture_identity': ['Succeeded']},
        'actions': {'Read_snapshot': snapshot_read, 'Parsed_snapshot': parsed_read,
                    'Snapshot_IDs': ids, 'Source_qualified': guarded_source},
        'else': {'actions': {'Target_unqualified_refused': {
            'type': 'Compose', 'inputs': {'status': 'TARGET_UNQUALIFIED', 'review_suppressed': True}, 'runAfter': {}}}},
    }
    definition['actions'] = {
        'Read_fixture_identity': get('Read_fixture_identity', target + '?$select=Id,Description,EnableVersioning'),
        'Fixture_identity_matches': list_guard_action,
    }
    return result


def build_changed_source_trial(baseline: dict, *, observed_row: dict, **bindings) -> dict:
    """Simulate only the second read's version change; never edit the source row."""
    snapshot = json.loads(observed_row['SnapshotJson'])
    if (snapshot.get('synthetic_only') is not True
            or observed_row.get('Id') != int(bindings['row_id'])
            or observed_row.get('OperationKey') != 'F10-COHERENT-SNAPSHOT1'
            or not observed_row.get('OData__UIVersionString')):
        raise ValueError('Exact observed synthetic source row required')
    result = build_trial(baseline, **bindings)
    definition = result['properties']['definition']
    branch = definition['actions']['Fixture_identity_matches']['actions']['Source_qualified']['actions']
    simulated = copy.deepcopy(observed_row)
    simulated['OData__UIVersionString'] = ('2.0' if observed_row['OData__UIVersionString'] != '2.0' else '3.0')
    name = 'F10_controlled_second_read_version_change'
    definition['staticResults'] = {name: {'status': 'Succeeded', 'outputs': {
        'statusCode': 'OK', 'headers': {'Content-Type': 'application/json'}, 'body': simulated}}}
    branch['Read_snapshot_after_classification']['runtimeConfiguration'] = {
        'staticResult': {'name': name, 'staticResultOptions': 'Enabled'}}
    branch['Review_Preview']['else']['actions']['SOURCE_CHANGED_REFUSED']['inputs'].update({
        'simulation': True, 'case': 'CONTROLLED_SECOND_READ_VERSION_CHANGE'})
    return result


def build_carry_forward_trial(baseline: dict, *, site: str, list_id: str,
                              description: str, row_id: str | int,
                              reference: str, entity_type: str, source_url: str,
                              selected_record_id: str,
                              expected_operation_key: str = 'F10-COHERENT-SNAPSHOT1',
                              expected_source_revision: str = 'fictional-v7',
                              choice_field: str = 'CarryChoice',
                              date_field: str = 'CarryMeetingDate') -> dict:
    """Build a guarded, choice-driven fictional carry-forward persistence trial."""
    site, list_id = _check_bindings(site=site, list_id=list_id, description=description,
                                    row_id=row_id, reference=reference)
    for name, value in (('entity type', entity_type), ('source URL', source_url),
                        ('selected record ID', selected_record_id)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'A nonempty {name} is required')
    if len(selected_record_id) > 255 or len(source_url) > 255:
        raise ValueError('Carry-forward references must be bounded text')
    if "'" in entity_type or len(entity_type) > 255:
        raise ValueError('A bounded native entity type is required')
    for field in (choice_field, date_field):
        if (not isinstance(field, str) or not field or not field.isascii()
                or not field[0].isalpha() or not field.replace('_', '').isalnum()):
            raise ValueError('Native field bindings must be safe internal names')
    if urlsplit(source_url).scheme != 'https':
        raise ValueError('A source URL is required')

    result = build_trial(baseline, site=site, list_id=list_id, description=description,
                         row_id=row_id, reference=reference,
                         expected_operation_key=expected_operation_key,
                         expected_source_revision=expected_source_revision)
    definition = result['properties']['definition']
    root = definition['actions']['Fixture_identity_matches']['actions']
    source = root['Source_qualified']['actions']
    row_uri = (f"_api/web/lists(guid'{list_id}')/items({int(row_id)})"
               f'?$select=Id,OperationKey,SourceRevision,SnapshotJson,OData__UIVersionString,{choice_field},{date_field}')
    root['Read_snapshot']['inputs']['parameters']['parameters/uri'] = row_uri
    source['Read_snapshot_after_classification']['inputs']['parameters']['parameters/uri'] = row_uri

    stable_branch = source['Review_Preview']['actions']['Stable_source_proposal']
    preview = stable_branch['inputs']
    selected = f"first(body('Carry_selected_record'))?['source_snapshot']"
    operation_key = "@concat('F10|',uriComponent(outputs('Parsed_snapshot')?['source_id']),'|',uriComponent('" + selected_record_id.replace("'", "''") + "'), '|', uriComponent(outputs('Parsed_snapshot')?['meeting_id']))"
    target = f"_api/web/lists(guid'{list_id}')"
    fields = ('Title', 'OperationKey', 'SourceReference', 'SourceRevision',
              'AuthorityReference', 'ReviewedWording', 'HistoryText', date_field)

    def wdl_literal(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def http(method: str, uri: str, *, after: dict | None = None, body: str | None = None) -> dict:
        params = {'dataset': site, 'parameters/method': method, 'parameters/uri': uri,
                  'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}
        if body is not None:
            params['parameters/headers']['Content-Type'] = 'application/json;odata=verbose'
            params['parameters/body'] = body
        return {'type': 'OpenApiConnection', 'inputs': {
            'host': {'apiId': CONNECTOR, 'connectionName': 'shared_sharepointonline',
                     'operationId': 'HttpRequest'},
            'parameters': params, 'authentication': "@parameters('$authentication')",
            'retryPolicy': {'type': 'none'}}, 'runAfter': after or {}}

    def receipt(status: str, *, after: dict | None = None) -> dict:
        return {'type': 'Compose', 'inputs': {
            'status': status, 'operation_key': "@outputs('Carry_operation_key')",
            'synthetic_only': True, 'independent_native_verification_required': True,
            'action_issued': False, 'notified': False}, 'runAfter': after or {}}

    key_action = {'type': 'Compose', 'inputs': operation_key, 'runAfter': {}}
    read_uri = ("@concat(" + wdl_literal(target + "/items?$filter=OperationKey%20eq%20%27")
                + ",uriComponent(outputs('Carry_operation_key')),"
                + wdl_literal("%27&$select=Id," + ','.join(fields)) + ")")
    match_fields = {
        'Title': "@concat('FICTIONAL carry-forward draft: '," + selected + "?['source_text'])",
        'OperationKey': "@outputs('Carry_operation_key')",
        'SourceReference': "@concat('" + source_url.replace("'", "''") + "#',uriComponent('" + selected_record_id.replace("'", "''") + "'))",
        'SourceRevision': "@body('Read_snapshot')?['SourceRevision']",
        'AuthorityReference': 'FICTIONAL CARRY CHOICE - NOT ACTION AUTHORITY',
        'ReviewedWording': '@' + selected + "?['source_text']",
        'HistoryText': 'Source history retained at source link; draft only; no action issued.',
        date_field: f"@body('Read_snapshot')?['{date_field}']",
    }
    # Compose a valid WDL object expression so dynamic source values remain data, not JSON text.
    obj = "json('{}')"
    metadata_json = json.dumps({'type': entity_type}, separators=(',', ':')).replace("'", "''")
    obj = f"setProperty({obj},'__metadata',json('{metadata_json}'))"
    for field, value in match_fields.items():
        val = value if value.startswith('@') else wdl_literal(value)
        if val.startswith('@'):
            val = val[1:]
        obj = f"setProperty({obj},'{field}',{val})"
    body_expr = '@string(' + obj + ')'

    existing_match = '@and(' + ','.join(
        f"equals(first(body('Read_carry_operation')?['value'])?['{field}'],{value[1:] if value.startswith('@') else wdl_literal(value)})"
        for field, value in match_fields.items()) + ')'
    exact_one = {'type': 'If', 'expression': "@equals(length(body('Read_carry_operation')?['value']),1)",
        'runAfter': {'Read_carry_operation': ['Succeeded']},
        'actions': {'Existing_fields_match': {'type': 'If', 'expression': existing_match, 'runAfter': {},
            'actions': {'Carry_forward_already_present': receipt('CARRY_FORWARD_ALREADY_PRESENT')},
            'else': {'actions': {'Existing_operation_mismatch_refused': receipt('EXISTING_OPERATION_MISMATCH_PRESERVE_HUMAN_EDIT')}}}},
        'else': {'actions': {'Zero_existing_operation': {'type': 'If',
            'expression': "@equals(length(body('Read_carry_operation')?['value']),0)", 'runAfter': {},
            'actions': {'Create_fictional_carry_draft': http('POST', target + '/items', body=body_expr),
                'Read_created_carry_draft': http('GET', read_uri,
                    after={'Create_fictional_carry_draft': ['Succeeded']}),
                'Created_draft_requires_independent_verification': receipt(
                    'CARRY_FORWARD_CREATED_READBACK_REQUIRES_INDEPENDENT_VERIFICATION',
                    after={'Read_created_carry_draft': ['Succeeded']})},
            'else': {'actions': {'Multiple_operations_refused': receipt('MULTIPLE_OPERATIONS_REFUSED_PRESERVE_HUMAN_EDIT')}}}}}}
    persist = {
        'Carry_operation_key': key_action,
        'Read_carry_operation': http('GET', read_uri, after={'Carry_operation_key': ['Succeeded']}),
        'Route_existing_or_create': exact_one,
    }
    safe_record_id = selected_record_id.replace("'", "''")
    eligible = ("@and(equals(body('Read_snapshot')?['" + choice_field + "'],'Carry'),"
                "not(empty(body('Read_snapshot')?['" + date_field + "'])),"
                "equals(length(body('Carry_selected_record')),1),"
                "equals(first(body('Carry_selected_record'))?['source_snapshot']?['record_id'],'" + safe_record_id + "'),"
                "equals(first(body('Carry_selected_record'))?['source_snapshot']?['status'],'open'))")
    selected_action = {'type': 'Query', 'inputs': {'from': '@body(\'Proposed_Review_Items\')',
        'where': "@equals(item()?['source_snapshot']?['record_id'],'" + selected_record_id.replace("'", "''") + "')"},
        'runAfter': {}}
    carry = {'type': 'If', 'expression': eligible,
        'runAfter': {'Carry_selected_record': ['Succeeded']},
        'actions': persist,
        'else': {'actions': {'Carry_choice_or_selection_held': {
            'type': 'Compose', 'inputs': {'status': 'CARRY_FORWARD_HELD_NO_WRITE',
                'write_performed': False, 'notified': False, 'action_issued': False}, 'runAfter': {}}}}}
    stable_branch.pop('inputs', None)
    stable_branch.update({'type': 'Scope', 'runAfter': {}, 'actions': {
        'Retained_review_preview': {'type': 'Compose', 'inputs': preview, 'runAfter': {}},
        'Carry_selected_record': {**selected_action, 'runAfter': {'Retained_review_preview': ['Succeeded']}},
        'Carry_choice_gate': carry}})
    return result


def build_agenda_carry_integration(baseline: dict, *, agenda_list_id: str,
                                  expected_meeting_id: str, expected_meeting_date: str,
                                  key_field: str = 'CarryForwardKey', **source_bindings) -> dict:
    """Prepare the complete existing controlled-source -> agenda integration.

    Reuses the qualified source guard/classifier/native selection; does not
    qualify a real register/meeting or change source schema. The caller supplies
    registered source/agenda bindings. Deployment remains gated by consumer
    evidence and native key-column qualification. No Python host is invoked.
    """
    agenda_id = str(uuid.UUID(agenda_list_id))
    source_id = str(uuid.UUID(source_bindings['list_id']))
    if agenda_id == source_id:
        raise ValueError('Use the existing distinct agenda destination, not the source fixture')
    if any(not isinstance(v, str) or not v.strip() for v in (expected_meeting_id, expected_meeting_date)):
        raise ValueError('Bind the qualified selected meeting identity and exact native date together')
    date = datetime.fromisoformat(expected_meeting_date.replace('Z', '+00:00'))
    if date.tzinfo is None or date.utcoffset().total_seconds() != 0:
        raise ValueError('Expected native meeting date must be explicit UTC')
    if (not key_field or not key_field.isascii() or not key_field[0].isalpha()
            or not key_field.replace('_', '').isalnum() or key_field in AGENDA_CARRY_FIELDS
            or key_field == 'Agenda_x0020_review_x0020_bindin'):
        raise ValueError('A separate qualified native key-field binding is required')
    result = build_carry_forward_trial(baseline, **source_bindings)
    actions = result['properties']['definition']['actions']
    source = actions['Fixture_identity_matches']['actions']['Source_qualified']['actions']
    stable = source['Review_Preview']['actions']['Stable_source_proposal']['actions']
    preview = stable['Retained_review_preview']['inputs']
    for field in ('agenda_updated', 'register_updated', 'planner_updated', 'notified',
                  'readonly_replay', 'not_persisted', 'idempotency'):
        preview.pop(field, None)
    preview['stage'] = 'Source classification before optional agenda persistence; use final receipt for effects'
    gate = stable['Carry_choice_gate']
    target = f"_api/web/lists(guid'{agenda_id}')"
    selected_id = source_bindings['selected_record_id']
    selected = "first(body('Carry_selected_record'))?['source_snapshot']"
    fields = ['Id', 'OData__UIVersionString', key_field, *sorted(AGENDA_CARRY_FIELDS)]
    key_expr = ("@concat('f10:native1|" + source_id + "|',uriComponent('"
                + selected_id.replace("'", "''")
                + "'),'|',uriComponent(outputs('Parsed_snapshot')?['meeting_id']))")

    def literal(text):
        return "'" + text.replace("'", "''") + "'"

    def call(method, uri, *, after=None, body=None):
        params = {'dataset': source_bindings['site'], 'parameters/method': method,
                  'parameters/uri': uri,
                  'parameters/headers': {'Accept': 'application/json;odata=minimalmetadata'}}
        if body is not None:
            params['parameters/headers']['Content-Type'] = 'application/json;odata=verbose'
            params['parameters/body'] = body
        return {'type': 'OpenApiConnection', 'inputs': {
            'host': {'apiId': CONNECTOR, 'connectionName': 'shared_sharepointonline',
                     'operationId': 'HttpRequest'}, 'parameters': params,
            'authentication': "@parameters('$authentication')", 'retryPolicy': {'type': 'none'}},
            'runAfter': after or {}}

    def row(read):
        return "first(body('" + read + "')?['value'])"

    def same_fields(read):
        # contains(array, string) is case-sensitive: never fold opaque IDs/text.
        return '@and(' + ','.join(
            "contains(createArray(outputs('Expected_agenda_fields')?['" + f + "']),"
            + row(read) + "?['" + f + "'])" for f in [key_field, *sorted(AGENDA_CARRY_FIELDS)]) + ')'

    def native_identity_valid(read):
        r = row(read)
        etag = f"coalesce({r}?['odata.etag'],{r}?['@odata.etag'],'')"
        return (f"@and(greater(coalesce({r}?['Id'],0),0),not(empty({r}?['OData__UIVersionString'])),"
                f"not(empty({etag})),not(equals({etag},'*')))")

    def receipt(status, read=None):
        data = {'status': status, 'action_issued': False, 'notified': False,
                'operational_acceptance': False, 'independent_native_verification_required': True}
        data['agenda_effect'] = ('created' if status == 'CREATED_REQUIRES_INDEPENDENT_VERIFICATION'
            else 'uncertain_stop' if read == 'Read_created_agenda' or status.startswith('CREATE')
            else 'none')
        if read:
            data.update(item_id='@' + row(read) + "?['Id']",
                        item_revision='@' + row(read) + "?['OData__UIVersionString']",
                        etag="@coalesce(" + row(read) + "?['odata.etag'],"
                             + row(read) + "?['@odata.etag'],'')")
        return {'type': 'Compose', 'inputs': data, 'runAfter': {}}

    def verify_match(read, status):
        identity = native_identity_valid(read)[1:]
        resolved = receipt(status, read)['inputs']
        for key in ('item_id', 'item_revision', 'etag'):
            value = resolved[key]
            resolved[key] = f"@if({identity},{value[1:]},null)"
        if read == 'Read_created_agenda':
            resolved['agenda_effect'] = f"@if({identity},'created','uncertain_stop')"
        else:
            resolved['agenda_effect'] = 'none'
        resolved['status'] = f"@if({identity},'{status}','NATIVE_IDENTITY_UNVERIFIED_STOP')"
        return {'type': 'If', 'expression': same_fields(read), 'runAfter': {},
            'actions': {'Resolved_' + read: {'type': 'Compose', 'inputs': resolved, 'runAfter': {}}},
            'else': {'actions': {'Mismatch_' + read:
                receipt('HUMAN_EDIT_SOURCE_CHANGE_OR_COLLATION_COLLISION_STOP')}}}

    actions['Read_agenda_identity'] = call('GET', target + '?$select=Id,EnableVersioning,ListItemEntityTypeFullName')
    actions['Read_agenda_key_schema'] = call('GET', target + "/fields/getbyinternalnameortitle('"
        + key_field + "')?$select=InternalName,TypeAsString,Required,Indexed,EnforceUniqueValues,MaxLength,DefaultValue",
        after={'Read_agenda_identity': ['Succeeded']})
    actions['Fixture_identity_matches']['runAfter'].update(
        Read_agenda_identity=['Succeeded'], Read_agenda_key_schema=['Succeeded'])
    schema = "body('Read_agenda_key_schema')"
    guard = ("contains(createArray(" + literal(expected_meeting_id) + "),outputs('Parsed_snapshot')?['meeting_id']),"
             "contains(createArray(" + literal(expected_meeting_date) + "),body('Read_snapshot')?['"
             + source_bindings.get('date_field', 'CarryMeetingDate') + "']),"
             "equals(body('Read_agenda_identity')?['Id']," + literal(agenda_id) + "),"
             "equals(body('Read_agenda_identity')?['EnableVersioning'],true),"
             "not(empty(body('Read_agenda_identity')?['ListItemEntityTypeFullName'])),"
             f"equals({schema}?['InternalName'],{literal(key_field)}),"
             f"equals({schema}?['TypeAsString'],'Text'),equals({schema}?['Required'],false),"
             f"equals({schema}?['Indexed'],true),equals({schema}?['EnforceUniqueValues'],true),"
             f"equals({schema}?['MaxLength'],255),empty({schema}?['DefaultValue'])")
    gate['expression'] = '@and(' + gate['expression'][1:] + ',' + guard + ')'
    expected = {
        key_field: "@outputs('Carry_operation_key')",
        'Title': "@concat('FICTIONAL carry-forward draft: '," + selected + "?['source_text'])",
        'Question_x0020_or_x0020_help_x00': "@concat(" + selected + "?['source_text'],"
            "decodeUriComponent('%0A%0A'),'Carried source: '," + literal(source_bindings['source_url'] + '#' + selected_id) + ","
            "decodeUriComponent('%0A'),'Source revision: ',body('Read_snapshot')?['SourceRevision'],"
            "decodeUriComponent('%0A'),'Source history: ',join(" + selected + "?['history'],'; '),"
            "decodeUriComponent('%0A'),'Draft only; no new action or approval.')",
        'Meeting_x0020_date': "@body('Read_snapshot')?['" + source_bindings.get('date_field', 'CarryMeetingDate') + "']"}
    query = ("@concat(" + literal(target + "/items?$filter=" + key_field + "%20eq%20%27")
             + ",uriComponent(replace(outputs('Carry_operation_key'),'''','''''')),"
             + literal('%27&$select=' + ','.join(fields)) + ')')
    body = ("@string(setProperty(outputs('Expected_agenda_fields'),'__metadata',"
            "setProperty(json('{}'),'type',body('Read_agenda_identity')?['ListItemEntityTypeFullName'])))")
    created_count = "equals(length(body('Read_created_agenda')?['value']),1)"
    created_fields = same_fields('Read_created_agenda')[1:]
    created_identity = native_identity_valid('Read_created_agenda')[1:]
    created_verified = f"and({created_count},{created_fields},{created_identity})"
    created_status = (f"@if(not({created_count}),'CREATED_STATE_UNVERIFIED_STOP',"
        f"if(not({created_fields}),'HUMAN_EDIT_SOURCE_CHANGE_OR_COLLATION_COLLISION_STOP',"
        f"if({created_identity},'CREATED_REQUIRES_INDEPENDENT_VERIFICATION','NATIVE_IDENTITY_UNVERIFIED_STOP')))" )
    created_result = {
        'status': created_status, 'action_issued': False, 'notified': False,
        'operational_acceptance': False, 'independent_native_verification_required': True,
        'agenda_effect': f"@if({created_verified},'created','uncertain_stop')",
        'item_id': f"@if({created_verified},{row('Read_created_agenda')}?['Id'],null)",
        'item_revision': f"@if({created_verified},{row('Read_created_agenda')}?['OData__UIVersionString'],null)",
        'etag': f"@if({created_verified},coalesce({row('Read_created_agenda')}?['odata.etag'],{row('Read_created_agenda')}?['@odata.etag'],''),'')"}
    create = {
        'Create_agenda_carry_draft': call('POST', target + '/items', body=body),
        'Read_created_agenda': call('GET', query, after={'Create_agenda_carry_draft': ['Succeeded']}),
        'Created_count_verified': {'type': 'Compose', 'runAfter': {'Read_created_agenda': ['Succeeded']},
                                   'inputs': created_result},
        'Create_failed_or_uncertain_STOP': {**receipt('CREATE_FAILED_OR_UNCERTAIN_STOP_NO_RETRY'),
            'runAfter': {'Create_agenda_carry_draft': ['Failed', 'TimedOut']}}}
    route = {'type': 'If', 'runAfter': {'Read_carry_operation': ['Succeeded']},
        'expression': "@and(outputs('Carry_key_and_title_fit'),equals(length(body('Read_carry_operation')?['value']),1))",
        'actions': {'Existing_agenda_fields_match': verify_match('Read_carry_operation', 'EXISTING_MATCH')},
        'else': {'actions': {'No_existing_agenda': {
            'type': 'If', 'runAfter': {}, 'expression': "@and(outputs('Carry_key_and_title_fit'),equals(length(body('Read_carry_operation')?['value']),0))",
            'actions': create, 'else': {'actions': {'Ambiguous_STOP': {
                **receipt('AMBIGUOUS_IDENTITY_STOP'),
                'inputs': {**receipt('AMBIGUOUS_IDENTITY_STOP')['inputs'],
                    'status': "@if(outputs('Carry_key_and_title_fit'),'AMBIGUOUS_IDENTITY_STOP','IDENTITY_OR_TITLE_TOO_LONG_NO_WRITE')"}}}}}}}}
    fits = {'type': 'Compose', 'runAfter': {'Expected_agenda_fields': ['Succeeded']},
        'inputs': "@and(lessOrEquals(length(outputs('Carry_operation_key')),255),lessOrEquals(length(outputs('Expected_agenda_fields')?['Title']),255))"}
    gate['actions'] = {'Carry_operation_key': {'type': 'Compose', 'inputs': key_expr, 'runAfter': {}},
        'Expected_agenda_fields': {'type': 'Compose', 'inputs': expected,
                                  'runAfter': {'Carry_operation_key': ['Succeeded']}},
        'Carry_key_and_title_fit': fits,
        'Read_carry_operation': call('GET', query, after={'Carry_key_and_title_fit': ['Succeeded']}),
        'Resolve_or_create_agenda': route}
    return result


def build_agenda_operator_integration(baseline: dict, *, source_choices: list[str],
                                      meeting_time_zone: str,
                                      **bindings) -> dict:
    """Build an owner-operated, fictional entrypoint over the reviewed F10 fixture.

    The picker is intentionally a finite list of fictional source IDs. It is not a
    production source adapter or a grant of run-only access.
    """
    if (not isinstance(source_choices, list) or len(source_choices) < 2
            or any(not isinstance(x, str)
                   or not (x.startswith('FICTIONAL-') or x.startswith('SYN-'))
                   for x in source_choices)
            or len(set(source_choices)) != len(source_choices)):
        raise ValueError('A unique finite list of fictional source IDs is required')
    # The underlying persistence builder supplies the already-qualified native
    # identity, lookup, schema and no-overwrite graph; runtime controls replace
    # only its fixed commissioning values.
    graph = build_agenda_carry_integration(baseline, **bindings)
    definition = graph['properties']['definition']
    schema = definition['triggers']['manual']['inputs']['schema']
    schema['properties'] = {
        'selected_record_id': {
            'type': 'string', 'enum': source_choices,
            'description': 'Select one exact source ID from the fictional review list.'},
        'carry_choice': {
            'type': 'string', 'enum': ['Carry', 'Do not carry'],
            'description': 'Carry creates only an unapproved agenda draft; Do not carry records no write.'},
        'meeting_id': {
            'type': 'string', 'minLength': 1, 'maxLength': 255,
            'description': 'Enter the stable identity of the meeting for this fictional draft.'},
        'meeting_date': {
            'type': 'string', 'format': 'date',
            'description': 'Select the meeting date in YYYY-MM-DD format.'}}
    schema['required'] = ['selected_record_id', 'carry_choice', 'meeting_id', 'meeting_date']

    actions = definition['actions']
    stable = actions['Fixture_identity_matches']['actions']['Source_qualified']['actions'][
        'Review_Preview']['actions']['Stable_source_proposal']['actions']
    selected_action = stable['Carry_selected_record']
    selected_action['inputs']['where'] = (
        "@equals(item()?['source_snapshot']?['record_id'],triggerBody()?['selected_record_id'])")
    gate = stable['Carry_choice_gate']
    expression = gate['expression']
    selected_id = bindings['selected_record_id']
    meeting_id = bindings['expected_meeting_id']
    meeting_date = bindings['expected_meeting_date']
    choice_field = bindings.get('choice_field', 'CarryChoice')
    date_field = bindings.get('date_field', 'CarryMeetingDate')
    for before, after in (
        ("equals(body('Read_snapshot')?['" + choice_field + "'],'Carry')",
         "equals(triggerBody()?['carry_choice'],'Carry')"),
        ("not(empty(body('Read_snapshot')?['" + date_field + "']))",
         "not(empty(triggerBody()?['meeting_date']))"),
        ("equals(first(body('Carry_selected_record'))?['source_snapshot']?['record_id'],"
         + "'" + selected_id.replace("'", "''") + "')",
         "equals(first(body('Carry_selected_record'))?['source_snapshot']?['record_id'],"
         "triggerBody()?['selected_record_id'])"),
        ("contains(createArray('" + meeting_id.replace("'", "''")
         + "'),outputs('Parsed_snapshot')?['meeting_id'])",
         "equals(triggerBody()?['meeting_id'],outputs('Parsed_snapshot')?['meeting_id'])"),
        ("contains(createArray('" + meeting_date.replace("'", "''")
         + "'),body('Read_snapshot')?['" + date_field + "'])",
         "and(equals(formatDateTime(triggerBody()?['meeting_date'],'yyyy-MM-dd'),triggerBody()?['meeting_date']),"
         "equals(triggerBody()?['meeting_date'],convertTimeZone(body('Read_snapshot')?['"
         + date_field + "'],'UTC','" + meeting_time_zone.replace("'", "''") + "','yyyy-MM-dd')))")):
        if before not in expression:
            raise ValueError('The fixed-value carry guard changed; do not perform an unsafe textual repair')
        expression = expression.replace(before, after)
    gate['expression'] = expression
    operation = gate['actions']['Carry_operation_key']
    operation['inputs'] = (
        "@concat('f10:native1|" + str(uuid.UUID(bindings['list_id'])) + "|',"
        "uriComponent(triggerBody()?['selected_record_id']),'|',"
        "uriComponent(triggerBody()?['meeting_id']))")
    expected_action = gate['actions']['Expected_agenda_fields']
    expected = expected_action['inputs']
    selected = "first(body('Carry_selected_record'))?['source_snapshot']"
    expected['Title'] = "@concat('FICTIONAL carry-forward draft: '," + selected + "?['source_text'])"
    expected['Question_x0020_or_x0020_help_x00'] = (
        "@concat(" + selected + "?['source_text'],decodeUriComponent('%0A%0A'),"
        "'Source link: ',concat('" + bindings['source_url'] + "','#',"
        "uriComponent(triggerBody()?['selected_record_id'])),"
        "decodeUriComponent('%0A'),'Source ID: '," + selected + "?['record_id'],"
        "decodeUriComponent('%0A'),'Source revision: '," + selected + "?['snapshot_version'],"
        "decodeUriComponent('%0A'),'Reviewed revision: '," + selected + "?['reviewed_version'],"
        "decodeUriComponent('%0A'),'Snapshot time: '," + selected + "?['snapshot_time'],"
        "decodeUriComponent('%0A'),'Supplied status: '," + selected + "?['status'],"
        "decodeUriComponent('%0A'),'Commissioned claim: ',string(" + selected + "?['commissioned_claim']),"
        "decodeUriComponent('%0A'),'Issued claim: ',string(" + selected + "?['issued_claim']),"
        "decodeUriComponent('%0A'),'Responsible role supplied: ',coalesce(" + selected + "?['owner_claim'],'Not supplied'),"
        "decodeUriComponent('%0A'),'Due date supplied: ',coalesce(" + selected + "?['due_date'],'Not supplied'),"
        "decodeUriComponent('%0A'),'Review date supplied: ',coalesce(" + selected + "?['review_date'],'Not supplied'),"
        "decodeUriComponent('%0A'),'Closure evidence: ',coalesce(" + selected + "?['closure_evidence_ref'],'Not supplied'),"
        "decodeUriComponent('%0A'),'Conditions: ',string(coalesce(" + selected + "?['conditions'],'Not supplied in snapshot')),"
        "decodeUriComponent('%0A'),'Dissent: ',string(coalesce(" + selected + "?['dissent'],'Not supplied in snapshot')),"
        "decodeUriComponent('%0A'),'Source history: ',join(coalesce(" + selected + "?['history'],createArray()),'; '),"
        "decodeUriComponent('%0A'),'Draft only; carry-forward does not renew authority, change dates, issue work or approve the agenda.')")
    expected['Meeting_x0020_date'] = agenda_meeting_date_expression(meeting_time_zone)
    held = gate['else']['actions']['Carry_choice_or_selection_held']['inputs']
    held.clear()
    held.update({
        'status': "@if(equals(triggerBody()?['carry_choice'],'Do not carry'),'NOT_CARRIED_BY_REVIEWER','CARRY_FORWARD_HELD_NO_WRITE')",
        'selected_record_id': "@triggerBody()?['selected_record_id']",
        'eligible_proposals': "@body('Proposed_Review_Items')",
        'excluded_proposals': "@body('Excluded_Review_Items')",
        'blocking_reasons': "@body('Blocking_Exceptions')",
        'write_performed': False, 'notified': False, 'action_issued': False,
        'operational_acceptance': False})
    stable['Retained_review_preview']['inputs']['stage'] = (
        'Fictional operator selection; includes eligible, excluded and blocking classifications for reviewer context')
    # The persistence branch adds nine native action levels when it sits inside
    # the extra Scope produced by the fixed-value integration builder. Flatten
    # that scope into the same guarded Review_Preview branch: scopes provide no
    # output used by the graph, while Power Automate rejects nesting beyond 8.
    review_actions = actions['Fixture_identity_matches']['actions']['Source_qualified']['actions'][
        'Review_Preview']['actions']
    proposal_scope = review_actions.pop('Stable_source_proposal')
    if proposal_scope.get('type') != 'Scope':
        raise ValueError('Expected the stable proposal Scope before flattening the operator graph')
    for name, action in proposal_scope['actions'].items():
        if name in review_actions:
            raise ValueError(f'Operator action collides while flattening proposal Scope: {name}')
        review_actions[name] = action
    return graph


def agenda_meeting_date_expression(meeting_time_zone: str) -> str:
    """Bind date-only operator input to the independently checked site's zone.

    SharePoint returns DateOnly fields as UTC timestamps. Write that exact
    representation so full-field reconciliation keeps its strict comparison.
    This maker binding must be requalified if site regional settings change.
    """
    if not isinstance(meeting_time_zone, str) or not meeting_time_zone.strip():
        raise ValueError('An independently verified site Windows time zone is required')
    zone = meeting_time_zone.replace("'", "''")
    return ("@convertTimeZone(concat(triggerBody()?['meeting_date'],'T00:00:00'),'"
            + zone + "','UTC','yyyy-MM-ddTHH:mm:ssZ')")
