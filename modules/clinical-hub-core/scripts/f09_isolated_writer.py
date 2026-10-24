"""Build a same-flow fictional writer trial; never targets the live register.

This is maker tooling. Bindings are supplied privately; normal operators use
native choices. A trial result does not establish authority or accepted cutover.
"""
from __future__ import annotations

import copy
import json
import uuid

FIELDS = ('Title', 'OperationKey', 'SourceReference', 'SourceRevision',
          'AuthorityReference', 'ReviewedWording', 'HistoryText')
CASES = ('create', 'repeat', 'stale', 'recover', 'missing_review', 'catalogue')



# Authority and history are deliberately excluded from selective rollback.
SELECTIVE_RECOVERY_FIELDS = ('SourceRevision', 'ReviewedWording')
# These fields are maintained by SharePoint on a successful native versioned
# update. They are evidence to retain, not user content to send back or restore.
RECOVERY_SERVICE_FIELDS = {
    'odata.etag', '@odata.etag', 'OData__UIVersionString', 'Modified',
    'EditorId', 'Editor', 'odata.id', 'odata.editLink', 'odata.metadata',
    '@odata.context',
}

# Native Clinical Directors register columns. These names/types are shared by
# source selection and recovery; labels are never substituted for internal names.
REGISTER_FIELD_TYPES = {
    'Title': 'Text', 'LegacyactionID': 'Text', 'Sourcereference': 'Text',
    'Originalduelabel': 'Text', 'Currentstatus': 'Text',
    'Recordedrole_x2014_unverified': 'Text', 'Sourcehistory': 'Note',
    'Duedate': 'DateTime', 'Reviewdate': 'DateTime',
    'Commissioningclassification': 'Choice', 'Issuereadiness': 'Choice',
    'Originmeetingdate': 'DateTime', 'Closurereviewstate': 'Choice',
    'Acceptedclosuredate': 'DateTime',
}
REGISTER_RECOVERY_FIELDS = {
    'Title', 'Originalduelabel', 'Currentstatus',
    'Recordedrole_x2014_unverified', 'Duedate', 'Reviewdate',
}


def plan_action_register_recovery(*, baseline: dict, erroneous: dict,
                                  current: dict, field: str, site: str,
                                  list_id: str, schema: dict,
                                  recovery_reference: str,
                                  field_map: dict | None = None) -> dict:
    """Plan one native register-field repair from three complete snapshots.

    Pure development tooling, not permission to execute the returned request.
    The caller must qualify the target, authority and effects before a send.
    No assignment, issue/closure classification, identity or history is restored.
    A current independent change of the selected field always refuses recovery.
    """
    from urllib.parse import urlsplit
    from datetime import datetime

    uuid.UUID(list_id)
    url = urlsplit(site)
    if (url.scheme != 'https' or not url.hostname or url.username or url.password
            or url.query or url.fragment or not isinstance(recovery_reference, str)
            or not recovery_reference.strip()):
        raise ValueError('Exact qualified site and recovery evidence required')
    if (not isinstance(schema, dict) or schema.get('Id', '').lower() != list_id.lower()
            or schema.get('EnableVersioning') is not True):
        raise ValueError('Exact versioned native register schema required')
    entity = schema.get('ListItemEntityTypeFullName', '')
    if not entity.startswith('SP.Data.') or not entity.endswith('ListItem'):
        raise ValueError('Native entity type required')
    fields = schema.get('Fields', [])
    if not isinstance(fields, list) or any(not isinstance(f, dict) for f in fields):
        raise ValueError('Native field metadata required')
    names = [f.get('InternalName') for f in fields]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate native field metadata')
    lookup = {f.get('InternalName'): f for f in fields}
    mapping = dict(field_map) if field_map is not None else {k: k for k in REGISTER_FIELD_TYPES}
    if (set(mapping) != set(REGISTER_FIELD_TYPES)
            or any(not isinstance(n, str) or not n or not n.replace('_', '').isalnum()
                   for n in mapping.values())
            or len({n.casefold() for n in mapping.values()}) != len(mapping)):
        raise ValueError('Complete unambiguous native column mapping required')
    for name, kind in REGISTER_FIELD_TYPES.items():
        native = mapping[name]
        if (native not in lookup or lookup[native].get('TypeAsString') != kind
                or lookup[native].get('ReadOnlyField') is not False):
            raise ValueError('Register schema drift: ' + name)
    if field not in REGISTER_RECOVERY_FIELDS:
        raise ValueError('Identity, source/history and issue/closure fields cannot be restored')
    identity = ('Id', 'GUID', 'LegacyactionID', 'Sourcereference')
    canonical = []
    for native_row in (baseline, erroneous, current):
        if (not isinstance(native_row, dict)
                or not set(mapping.values()) | {'Id', 'GUID', 'odata.etag'} <= native_row.keys()):
            raise ValueError('Complete mapped native register snapshots required')
        row = {name: native_row[native] for name, native in mapping.items()}
        row.update({k: native_row[k] for k in ('Id', 'GUID', 'odata.etag')})
        canonical.append(row)
        if (not isinstance(row, dict)
                or not set(REGISTER_FIELD_TYPES) | set(identity) | {'odata.etag'} <= row.keys()
                or type(row['Id']) is not int or row['Id'] <= 0):
            raise ValueError('Complete native register snapshots required')
        uuid.UUID(row['GUID'])
        if any(not isinstance(row[k], str) or not row[k].strip()
               for k in ('LegacyactionID', 'Sourcereference', 'Title')):
            raise ValueError('Stable source identity and wording required')
        for name, kind in REGISTER_FIELD_TYPES.items():
            value = row[name]
            if value is not None and not isinstance(value, str):
                raise ValueError('Native scalar column value required: ' + name)
            if kind == 'Text' and value is not None and len(value) > 255:
                raise ValueError('Native text column limit: ' + name)
            if kind == 'DateTime' and value is not None:
                try:
                    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError as exc:
                    raise ValueError('Native zoned date required: ' + name) from exc
                if parsed.tzinfo is None:
                    raise ValueError('Native zoned date required: ' + name)
        etag = row['odata.etag']
        if (not isinstance(etag, str) or not etag or etag != etag.strip()
                or any(c in etag for c in ('*', '\r', '\n'))):
            raise ValueError('Exact native non-wildcard ETag required')
    base_view, error_view, current_view = canonical
    if any(row[k] != base_view[k] for row in (error_view, current_view) for k in identity):
        raise ValueError('Register identity/source drift')
    if base_view[field] == error_view[field]:
        raise ValueError('No erroneous field difference to recover')
    for earlier, later in ((base_view, error_view), (error_view, current_view)):
        if not (later['Sourcehistory'] or '').startswith(earlier['Sourcehistory'] or ''):
            raise ValueError('Source history lost; manual reconciliation required')
    state = ('ALREADY_RESTORED' if current_view[field] == base_view[field] else
             'RECOVERY_PLANNED' if current_view[field] == error_view[field] else
             'SELECTED_FIELD_CONFLICT')
    request = None
    if state == 'RECOVERY_PLANNED':
        request = _technical_request(site, 'POST',
            f"_api/web/lists(guid'{list_id}')/items({current['Id']})",
            body=json.dumps({'__metadata': {'type': entity}, mapping[field]: base_view[field]}),
            etag=current['odata.etag'])
    return {'state': state, 'request': request, 'field': mapping[field],
            'current': copy.deepcopy(current), 'restore_value': base_view[field],
            'field_map': mapping,
            'recovery_reference': recovery_reference, 'execution_authorized': False,
            'scope': 'Native register schema; selective repair only, no business approval/cutover'}

def _technical_request(site, method, uri, *, after=None, body=None, etag=None):
    headers = {'Accept': 'application/json;odata=minimalmetadata'}
    parameters = {'dataset': site, 'parameters/method': method, 'parameters/uri': uri,
                  'parameters/headers': headers}
    if body is not None:
        headers.update({'Content-Type': 'application/json;odata=verbose',
                        'X-HTTP-Method': 'MERGE', 'IF-MATCH': etag})
        parameters['parameters/body'] = body
    return {'type': 'OpenApiConnection', 'runAfter': after or {}, 'inputs': {
        'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                 'connectionName': 'shared_sharepointonline', 'operationId': 'HttpRequest'},
        'parameters': parameters, 'authentication': "@parameters('$authentication')",
        'retryPolicy': {'type': 'none'}}}


def plan_selective_recovery(*, baseline: dict, erroneous: dict, current: dict,
                            field: str, site: str, list_id: str,
                            description: str, entity_type: str) -> dict:
    """Pure, one-field recovery plan for the existing fictional CR namespace.

    Each snapshot includes Id, all FIELDS and odata.etag. The caller supplies a
    fresh native current read; freshness cannot be established by local tooling.
    Never replay a planned request after a conflict or uncertain acknowledgement:
    read again and re-plan. No history or unrelated field is sent in the MERGE.
    """
    from urllib.parse import urlsplit

    uuid.UUID(list_id)
    url = urlsplit(site)
    if (url.scheme != 'https' or not url.hostname or url.username or url.password
            or url.query or url.fragment
            or 'Synthetic technical commissioning only.' not in description
            or not entity_type.startswith('SP.Data.') or not entity_type.endswith('ListItem')):
        raise ValueError('Qualified synthetic target and native entity type required')
    if field not in SELECTIVE_RECOVERY_FIELDS:
        raise ValueError('Only technical revision or fictional wording recovery is allowed')
    for row in (baseline, erroneous, current):
        if (not isinstance(row, dict) or not set(('Id', 'odata.etag') + FIELDS) <= row.keys()
                or type(row['Id']) is not int or row['Id'] <= 4
                or any(not isinstance(row[k], str) or not row[k].strip()
                       or len(row[k]) > 255 for k in FIELDS)
                or not row['Title'].startswith('FICTIONAL F09 CR ')
                or not row['OperationKey'].startswith('F09-CR-')
                or not row['SourceReference'].startswith('FICTIONAL-F09-CR#')
                or any(not row[k].startswith('FICTIONAL') for k in
                       ('SourceRevision', 'AuthorityReference', 'ReviewedWording', 'HistoryText'))):
            raise ValueError('Complete bounded fictional CR snapshots required')
        etag = row['odata.etag']
        if (not isinstance(etag, str) or etag != etag.strip() or not etag
                or '*' in etag or '\r' in etag or '\n' in etag):
            raise ValueError('Exact non-wildcard snapshot ETag required')
    identity = ('Id', 'Title', 'OperationKey', 'SourceReference')
    if any(row[k] != baseline[k] for row in (erroneous, current) for k in identity):
        raise ValueError('Stable row identity mismatch')
    if baseline[field] == erroneous[field]:
        raise ValueError('Selected erroneous value must differ from baseline')
    if not erroneous['HistoryText'].startswith(baseline['HistoryText']):
        raise ValueError('Erroneous snapshot lost baseline history')
    if not current['HistoryText'].startswith(erroneous['HistoryText']):
        raise ValueError('Current snapshot lost erroneous history')
    if current[field] == baseline[field]:
        state = 'ALREADY_RESTORED'
    elif current[field] == erroneous[field]:
        state = 'RECOVERY_PLANNED'
    else:
        state = 'SELECTED_FIELD_CONFLICT'
    request = None
    if state == 'RECOVERY_PLANNED':
        request = _technical_request(site, 'POST',
            f"_api/web/lists(guid'{list_id}')/items({current['Id']})",
            body=json.dumps({'__metadata': {'type': entity_type}, field: baseline[field]}),
            etag=current['odata.etag'])
    return {'state': state, 'request': request, 'field': field,
            'restore_value': baseline[field], 'current': copy.deepcopy(current),
            'synthetic_only': True, 'native_deployment_ready': False}


def reconcile_selective_recovery(plan: dict, observed: dict) -> str:
    """Classify actual readback after success, 412, timeout or lost response.

    Changes outside the selected field require fresh reconciliation; never infer
    preservation from an HTTP success or automatically retry a stored request.
    """
    if plan['state'] not in ('RECOVERY_PLANNED', 'ALREADY_RESTORED'):
        return 'RECOVERY_REFUSED'
    previous = plan['current']
    if (not isinstance(observed, dict)
            or type(observed.get('Id')) is not int
            or any(k not in observed for k in previous if k not in RECOVERY_SERVICE_FIELDS)
            or any(observed[k] != v for k, v in previous.items()
                   if k != plan['field'] and k not in RECOVERY_SERVICE_FIELDS)):
        return 'READBACK_DRIFT_REQUIRES_RECONCILIATION'
    etag = observed.get('odata.etag')
    if (not isinstance(etag, str) or not etag or etag != etag.strip()
            or any(c in etag for c in ('*', '\r', '\n'))):
        return 'READBACK_DRIFT_REQUIRES_RECONCILIATION'
    value = observed[plan['field']]
    if value == plan['restore_value']:
        if (plan['state'] == 'RECOVERY_PLANNED' and etag == previous['odata.etag']):
            return 'READBACK_DRIFT_REQUIRES_RECONCILIATION'
        return 'RESTORED_READBACK'
    if value == previous[plan['field']]:
        return 'NOT_RESTORED_REPLAN_REQUIRED'
    return 'SELECTED_FIELD_CONFLICT'


def build_trial(baseline: dict, *, site: str, list_id: str, description: str,
                entity_type: str, reference: str) -> dict:
    """Return an isolated trial graph while retaining the legacy preview branch."""
    uuid.UUID(list_id)
    if not site.startswith('https://') or not reference or 'Synthetic technical commissioning only.' not in description:
        raise ValueError('Verified synthetic target and existing reference required')
    result = copy.deepcopy(baseline)
    props = result['properties']
    if props.get('connectionReferences'):
        raise ValueError('Expected the exact connector-free F09 baseline')
    definition = props['definition']
    old = copy.deepcopy(definition['actions'])
    if set(old) != {'Fixed_Fictional_Cases', 'Initialize_Date_Results',
                    'Validate_Case_Dates', 'Evaluate_Claims', 'Outcome_Previews'}:
        raise ValueError('Baseline changed; review before building')
    init = old.pop('Initialize_Date_Results')
    init['runAfter'] = {}
    old['Validate_Case_Dates']['runAfter'] = {'Fixed_Fictional_Cases': ['Succeeded']}
    definition['triggers']['manual']['inputs']['schema'] = {
        'type': 'object', 'properties': {
            'text': {'type': 'string', 'title': 'Fictional commissioning case',
                     'description': 'Fictional maker case: create, repeat, stale, recover or missing_review.',
                     'default': 'create', 'x-ms-content-hint': 'TEXT',
                     'x-ms-dynamically-added': True},
        }, 'required': ['text'], 'additionalProperties': False,
    }
    props['connectionReferences'] = {
        'shared_sharepointonline': {'runtimeSource': 'invoker',
                                   'connection': {'connectionReferenceLogicalName': reference},
                                   'api': {'name': 'shared_sharepointonline'}}}
    target = f"_api/web/lists(guid'{list_id}')"
    op = 'F09-FICTIONAL-OP1'
    row = {'Title': 'FICTIONAL reviewed outcome - not commissioned work',
           'OperationKey': op, 'SourceReference': 'FICTIONAL-MINUTES#P1',
           'SourceRevision': 'FICTIONAL-REV1',
           'AuthorityReference': 'FICTIONAL-OWNER-REVIEW1',
           'ReviewedWording': 'Fictional review approved this technical fixture only.',
           'HistoryText': 'FICTIONAL-REVIEW1: source REV1 retained; no live action issued.'}

    def http(method: str, uri: str, *, after=None, body=None):
        params = {'dataset': site, 'parameters/method': method,
                  'parameters/uri': uri,
                  'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}
        if body is not None:
            params['parameters/headers']['Content-Type'] = 'application/json;odata=verbose'
            params['parameters/body'] = json.dumps({'__metadata': {'type': entity_type}, **body})
        return {'type': 'OpenApiConnection',
                'inputs': {'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                                    'connectionName': 'shared_sharepointonline', 'operationId': 'HttpRequest'},
                           'parameters': params, 'authentication': "@parameters('$authentication')",
                           'retryPolicy': {'type': 'none'}},
                'runAfter': after or {}}

    def receipt(code: str, *, after=None):
        return {'type': 'Compose', 'inputs': {
            'result': code, 'synthetic_only': True, 'operation_key': op,
            'live_register_write': False, 'action_issued': False,
            'authority_verified': False, 'operational_acceptance': False,
            'notification_action_performed': False,
        }, 'runAfter': after or {}}

    # All stored fields, rather than just the key, must agree for reconciliation.
    same = '@and(' + ','.join(
        f"equals(first(body('Read_fixture_operation')?['value'])?['{k}'], '{v.replace(chr(39), chr(39)*2)}')"
        for k, v in row.items()) + ')'
    existing = {
        'Stored_operation_matches': {
            'type': 'If', 'expression': same, 'runAfter': {},
            'actions': {
                'Expected_revision_matches': {
                    'type': 'If', 'expression': "@equals(first(body('Read_fixture_operation')?['value'])?['SourceRevision'],if(equals(triggerBody()?['text'],'stale'),'FICTIONAL-REV2','FICTIONAL-REV1'))",
                    'runAfter': {},
                    'actions': {'Reconciled_existing_write': receipt('EXISTING_WRITE_RECONCILED')},
                    'else': {'actions': {'Stale_source_refused': receipt('STALE_SOURCE_REFUSED')}},
                }},
            'else': {'actions': {'Conflicting_operation_refused': receipt('OPERATION_CONFLICT')}},
        }}
    absent = {
        'Create_case_only': {
            'type': 'If', 'expression': "@equals(triggerBody()?['text'],'create')", 'runAfter': {},
            'actions': {
                'Create_reviewed_fixture': http('POST', target + '/items', body=row),
                'Read_written_fixture': http('GET', target + f"/items?$filter=OperationKey eq '{op}'&$select=" + ','.join(('Id',) + FIELDS),
                                             after={'Create_reviewed_fixture': ['Succeeded']}),
                'Write_receipt': receipt('WRITE_READBACK_REQUIRES_INDEPENDENT_VERIFICATION',
                                         after={'Read_written_fixture': ['Succeeded']}),
            },
            'else': {'actions': {'Absent_operation_held': receipt('OPERATION_ABSENT_NO_WRITE')}},
        }}
    writer = {
        'Read_fixture_identity': http('GET', target + '?$select=Id,Description,EnableVersioning'),
        'Fixture_identity_matches': {
            'type': 'If', 'runAfter': {'Read_fixture_identity': ['Succeeded']},
            'expression': "@and(equals(body('Read_fixture_identity')?['Id'],'" + list_id + "'),equals(body('Read_fixture_identity')?['Description'],'" + description.replace("'", "''") + "'),equals(body('Read_fixture_identity')?['EnableVersioning'],true))",
            'actions': {
                'Read_fixture_operation': http('GET', target + f"/items?$filter=OperationKey eq '{op}'&$select=" + ','.join(('Id',) + FIELDS)),
                'One_existing_operation': {
                    'type': 'If', 'runAfter': {'Read_fixture_operation': ['Succeeded']},
                    'expression': "@equals(length(body('Read_fixture_operation')?['value']),1)",
                    'actions': existing,
                    'else': {'actions': {
                        'No_existing_operation': {
                            'type': 'If', 'runAfter': {},
                            'expression': "@equals(length(body('Read_fixture_operation')?['value']),0)",
                            'actions': absent,
                            'else': {'actions': {'Ambiguous_operation_refused': receipt('MULTIPLE_OPERATIONS_REFUSED')}},
                        }}},
                }},
            'else': {'actions': {'Unqualified_target_refused': receipt('TARGET_UNQUALIFIED')}},
        }}
    definition['actions'] = {
        'Initialize_Date_Results': init,
        'Commissioning_or_legacy_preview': {
            'type': 'If', 'runAfter': {'Initialize_Date_Results': ['Succeeded']},
            'expression': "@equals(triggerBody()?['text'],'catalogue')",
            'actions': old,
            'else': {'actions': {
                'Explicit_fictional_review': {
                    'type': 'If', 'runAfter': {},
                    'expression': "@contains(createArray('create','repeat','stale','recover'),triggerBody()?['text'])",
                    'actions': writer,
                    'else': {'actions': {'Missing_review_refused': receipt('REVIEW_NOT_CONFIRMED')}},
                }}},
        }}
    return result


def build_amendment_trial(baseline: dict, *, site: str, list_id: str, description: str,
                          entity_type: str, reference: str, row_id: int,
                          before: dict, after: dict, original_etag: str) -> dict:
    """Build a fictional, exact-row amendment trial on the isolated F09 fixture."""
    if not isinstance(row_id, int) or isinstance(row_id, bool) or row_id <= 0:
        raise ValueError('A positive exact synthetic row ID is required')
    if not isinstance(original_etag, str) or not original_etag.strip() or original_etag.strip() == '*':
        raise ValueError('A captured, specific original ETag is required')
    if not isinstance(before, dict) or not isinstance(after, dict) or set(before) != set(FIELDS) or set(after) != set(FIELDS):
        raise ValueError('Before and after must contain exactly the seven F09 fields')
    for record in (before, after):
        if any(not isinstance(v, str) or not v or len(v) > 255 for v in record.values()):
            raise ValueError('F09 field values must be nonempty bounded text')
    for key in ('Title', 'OperationKey', 'SourceReference'):
        if before[key] != after[key]:
            raise ValueError(f'{key} is immutable for an amendment')
    if (not after['HistoryText'].startswith(before['HistoryText'])
            or after['HistoryText'] == before['HistoryText']):
        raise ValueError('HistoryText must preserve the prior history as a prefix')

    result = build_trial(baseline, site=site, list_id=list_id, description=description,
                         entity_type=entity_type, reference=reference)
    definition = result['properties']['definition']
    definition['triggers']['manual']['inputs']['schema']['properties']['text'].update({
        'description': 'Fictional amendment case: amend, stale_etag or replay.',
        'default': 'amend'})
    gate = definition['actions']['Commissioning_or_legacy_preview']['else']['actions']['Explicit_fictional_review']
    gate['expression'] = "@contains(createArray('amend','stale_etag','replay'),triggerBody()?['text'])"
    target = f"_api/web/lists(guid'{list_id}')"
    row_uri = target + f"/items({row_id})?$select=" + ','.join(('Id',) + FIELDS + ('OData__UIVersionString',))
    before_expr = '@and(' + ','.join(
        f"equals(body('Read_amendment_row')?['{k}'], '{v.replace(chr(39), chr(39)*2)}')" for k, v in before.items()) + ')'
    after_expr = '@and(' + ','.join(
        f"equals(body('Read_amendment_row')?['{k}'], '{v.replace(chr(39), chr(39)*2)}')" for k, v in after.items()) + ')'

    def req(method, uri, *, after_run=None, body=None, headers=None):
        p = {'dataset': site, 'parameters/method': method, 'parameters/uri': uri,
             'parameters/headers': {'Accept': 'application/json;odata=minimalmetadata'}}
        if headers:
            p['parameters/headers'].update(headers)
        if body is not None:
            p['parameters/headers']['Content-Type'] = 'application/json;odata=verbose'
            p['parameters/body'] = json.dumps({'__metadata': {'type': entity_type}, **body})
        return {'type': 'OpenApiConnection', 'inputs': {
            'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                     'connectionName': 'shared_sharepointonline', 'operationId': 'HttpRequest'},
            'parameters': p, 'authentication': "@parameters('$authentication')",
            'retryPolicy': {'type': 'none'}}, 'runAfter': after_run or {}}

    receipt = lambda code, run: {'type': 'Compose', 'inputs': {'result': code, 'synthetic_only': True,
        'live_register_write': False, 'action_issued': False, 'operational_acceptance': False}, 'runAfter': run}
    payload = dict(after)
    merge_headers = {'X-HTTP-Method': 'MERGE', 'IF-MATCH': "@body('Read_amendment_row')?['odata.etag']"}
    amend_actions = {
        'Amend_row': req('POST', target + f'/items({row_id})', body=payload, headers=merge_headers),
        'Read_amended_row': req('GET', row_uri, after_run={'Amend_row': ['Succeeded']}),
        'Amendment_receipt': receipt('AMENDMENT_READBACK_REQUIRES_INDEPENDENT_VERIFICATION', {'Read_amended_row': ['Succeeded']})}
    stale_actions = {
        'Stale_etag_merge': req('POST', target + f'/items({row_id})', body=payload,
                                headers={'X-HTTP-Method': 'MERGE', 'IF-MATCH': original_etag}),
        'Unexpected_stale_merge_success': receipt('STALE_ETAG_UNEXPECTED_SUCCESS_STOP', {'Stale_etag_merge': ['Succeeded']}),
        'Unexpected_stale_success_stop': {'type': 'Terminate',
            'inputs': {'runStatus': 'Failed', 'runError': {'code': 'STALE_IF_MATCH_UNEXPECTEDLY_ACCEPTED',
                'message': 'Reconcile the source effect; do not retry.'}},
            'runAfter': {'Unexpected_stale_merge_success': ['Succeeded']}},
        'Classify_stale_etag_failure': {'type': 'If',
            'runAfter': {'Stale_etag_merge': ['Failed', 'TimedOut']},
            'expression': "@equals(outputs('Stale_etag_merge')?['statusCode'],412)",
            'actions': {
                'Stale_etag_native_412_required': receipt('STALE_ETAG_REFUSED', {}),
                'Expected_stale_conflict_complete': {'type': 'Terminate',
                    'inputs': {'runStatus': 'Succeeded'},
                    'runAfter': {'Stale_etag_native_412_required': ['Succeeded']}}},
            'else': {'actions': {'Unexpected_stale_failure_stop': {
                'type': 'Terminate', 'inputs': {'runStatus': 'Failed',
                    'runError': {'code': 'UNEXPECTED_STALE_CASE_FAILURE',
                                 'message': 'Only verified HTTP412 is an expected conflict; reconcile before retry.'}},
                'runAfter': {}}}}}}
    read_and_route = {
        'Read_amendment_row': req('GET', row_uri),
        'Exact_row_guard': {'type': 'If', 'runAfter': {'Read_amendment_row': ['Succeeded']},
            'expression': f"@and(equals(body('Read_amendment_row')?['Id'],{row_id}),equals(body('Read_amendment_row')?['OperationKey'],'{before['OperationKey']}'),not(empty(body('Read_amendment_row')?['odata.etag'])),not(equals(body('Read_amendment_row')?['odata.etag'],'*')))",
            'actions': {'Select_case': {'type': 'Switch', 'expression': "@triggerBody()?['text']", 'runAfter': {},
                'cases': {
                    'amend': {'case': 'amend', 'actions': {'Before_state_guard': {'type': 'If', 'expression': before_expr, 'runAfter': {}, 'actions': amend_actions,
                        'else': {'actions': {'Before_state_refused': receipt('BEFORE_STATE_MISMATCH_NO_WRITE', {})}}}}},
                    'stale_etag': {'case': 'stale_etag', 'actions': {'After_state_guard': {'type': 'If', 'expression': after_expr, 'runAfter': {}, 'actions': stale_actions,
                        'else': {'actions': {'Stale_state_refused': receipt('STALE_CASE_REQUIRES_ALL_AFTER_FIELDS', {})}}}}},
                    'replay': {'case': 'replay', 'actions': {'Replay_after_guard': {'type': 'If', 'expression': after_expr, 'runAfter': {}, 'actions': {'Replay_reconciled': receipt('AMENDMENT_RECONCILED', {})},
                        'else': {'actions': {'Replay_refused': receipt('REPLAY_STATE_MISMATCH_NO_WRITE', {})}}}}}},
                'default': {'actions': {'Unknown_case_refused': receipt('UNKNOWN_CASE_NO_WRITE', {})}}}},
            'else': {'actions': {'Wrong_row_refused': receipt('ROW_ID_OR_OPERATION_KEY_MISMATCH', {})}}}}
    identity = {
        'Read_amendment_fixture_identity': req('GET', target + '?$select=Id,Description,EnableVersioning'),
        'Amendment_fixture_guard': {'type': 'If', 'runAfter': {'Read_amendment_fixture_identity': ['Succeeded']},
            'expression': "@and(equals(body('Read_amendment_fixture_identity')?['Id'],'" + list_id + "'),equals(body('Read_amendment_fixture_identity')?['Description'],'" + description.replace("'", "''") + "'),equals(body('Read_amendment_fixture_identity')?['EnableVersioning'],true))",
            'actions': read_and_route,
            'else': {'actions': {'Wrong_fixture_refused': receipt('TARGET_UNQUALIFIED', {})}}}}
    gate['actions'] = identity
    return result


def build_concurrency_recovery_trial(baseline: dict, *, expected_baseline_sha256: str,
                                     site: str, list_id: str, description: str,
                                     entity_type: str, reference: str,
                                     rows: list[dict]) -> dict:
    """Prepare a pinned two-row trial, never an assertion of native qualification.

    Sequence: race -> uncertain_save/reconcile -> partial_save/reconcile/resume.
    The two intentional failed runs model withheld acknowledgement and a stopped
    multi-row operation; they do not simulate a real network or service failure.
    Only the existing four mutable technical fields are ever sent in a MERGE.
    """
    import hashlib
    from urllib.parse import urlsplit

    pin = hashlib.sha256(json.dumps(baseline, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode()).hexdigest()
    if pin != expected_baseline_sha256:
        raise ValueError('Complete canonical baseline drift')
    native_baseline = baseline
    dataverse = 'clientdata' in baseline
    if dataverse:
        if (baseline.get('workflowid') != '00000000-0000-4000-8000-000000000101'
                or baseline.get('statecode') != 0 or baseline.get('statuscode') != 1
                or baseline.get('ismanaged') is not False):
            raise ValueError('Exact stopped unmanaged canonical F09 Dataverse record required')
        baseline = json.loads(baseline['clientdata'])
        if 'state' in baseline.get('properties', {}):
            raise ValueError('Unexpected state projection in Dataverse clientdata')
        baseline['properties']['state'] = 'Stopped'
    props = baseline.get('properties', {})
    if props.get('state') != 'Stopped' or props.get('isManaged'):
        raise ValueError('A stopped unmanaged baseline is required')
    parsed = urlsplit(site)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or not entity_type.startswith('SP.Data.')
            or not entity_type.endswith('ListItem')):
        raise ValueError('Exact HTTPS site and native list item entity type required')
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError('Exactly two selected technical rows required')
    ids = []
    before = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'before'}:
            raise ValueError('Exact row ID and complete seven-field before image required')
        rid, fields = row['id'], row['before']
        if not isinstance(rid, int) or isinstance(rid, bool) or rid <= 4:
            raise ValueError('Preserve existing rows 1-4; select technical row IDs above 4')
        if (not isinstance(fields, dict) or set(fields) != set(FIELDS)
                or any(not isinstance(v, str) or not v.strip() or len(v) > 255 for v in fields.values())
                or not fields['Title'].startswith('FICTIONAL F09 CR ')
                or not fields['OperationKey'].startswith('F09-CR-')
                or not fields['SourceReference'].startswith('FICTIONAL-F09-CR#')
                or any(not fields[k].startswith('FICTIONAL') for k in
                       ('SourceRevision', 'AuthorityReference', 'ReviewedWording', 'HistoryText'))):
            raise ValueError('Pinned bounded fictional F09 CR namespace required')
        ids.append(rid); before.append(copy.deepcopy(fields))
    if len(set(ids)) != 2 or len({r['OperationKey'] for r in before}) != 2:
        raise ValueError('Distinct row IDs and operation keys required')

    def advance(record, stage):
        value = dict(record, SourceRevision='FICTIONAL-' + stage,
                     AuthorityReference='FICTIONAL-TECHNICAL-' + stage,
                     ReviewedWording='FICTIONAL technical state ' + stage + '; no work issued.',
                     HistoryText=record['HistoryText'] + ' | ' + stage)
        if any(len(v) > 255 for v in value.values()):
            raise ValueError('Every staged field/history must fit existing Text(255)')
        return value

    race_a, race_b = [advance(before[0], 'RACE-' + s) for s in ('A', 'B')]
    unknown_a, unknown_b = [advance(r, 'UNKNOWN-' + s) for r, s in ((race_a, 'A'), (race_b, 'B'))]
    partial_a, partial_b = [advance(r, 'PARTIAL-' + s) for r, s in ((unknown_a, 'A'), (unknown_b, 'B'))]
    second_after = advance(before[1], 'SECOND-COMPLETED')
    candidate = build_trial(baseline, site=site, list_id=list_id, description=description,
                            entity_type=entity_type, reference=reference)
    definition = candidate['properties']['definition']
    cases = ('race', 'race_reconcile', 'uncertain_save', 'uncertain_reconcile',
             'partial_save', 'partial_reconcile', 'partial_resume')
    definition['triggers']['manual']['inputs']['schema']['properties']['text'].update(
        default='race_reconcile', description='Technical two-row cases: ' + ', '.join(cases))
    gate = definition['actions']['Commissioning_or_legacy_preview']['else']['actions']['Explicit_fictional_review']
    gate['expression'] = '@contains(createArray(' + ','.join("'" + c + "'" for c in cases) + "),triggerBody()?['text'])"
    target = f"_api/web/lists(guid'{list_id}')"

    def literal(value):
        return "'" + value.replace("'", "''") + "'"

    def equals_record(action, record):
        return 'and(' + ','.join("equals(body('" + action + "')?['" + k + "']," + literal(v) + ')'
                                 for k, v in record.items()) + ')'

    def both(first_states, second_states, first_action='Read_first', second_action='Read_second'):
        def any_state(action, states):
            matches = [equals_record(action, s) for s in states]
            return matches[0] if len(matches) == 1 else 'or(' + ','.join(matches) + ')'
        return '@and(' + any_state(first_action, first_states) + ',' + any_state(second_action, second_states) + ')'

    def request(method, uri, *, after=None, body=None, etag=None):
        return _technical_request(site, method, uri, after=after, body=body, etag=etag)

    def row_get(index, after=None):
        return request('GET', target + f'/items({ids[index]})?$select=' +
                       ','.join(('Id',) + FIELDS + ('OData__UIVersionString',)), after=after)

    def payload(record):
        return json.dumps({'__metadata': {'type': entity_type}, **{k: record[k] for k in
                          ('SourceRevision', 'AuthorityReference', 'ReviewedWording', 'HistoryText')}},
                          separators=(',', ':'))

    def choose_payload(condition, a, b):
        return '@if(' + condition + ',' + literal(payload(a)) + ',' + literal(payload(b)) + ')'

    def merge(index, body, after=None):
        read = ('Read_first', 'Read_second')[index]
        return request('POST', target + f'/items({ids[index]})', body=body,
                       etag="@body('" + read + "')?['odata.etag']", after=after)

    def stop(code, after=None):
        return {'type': 'Terminate', 'runAfter': after or {}, 'inputs': {'runStatus': 'Failed',
                'runError': {'code': code, 'message': 'Stop; reconcile both rows and histories before any further write.'}}}

    def result(code):
        return {'type': 'Compose', 'runAfter': {}, 'inputs': {
            'result': code, 'synthetic_only': True, 'live_register_write': False,
            'action_issued': False, 'assigned': False, 'notification_action_performed': False,
            'operational_acceptance': False, 'requires_independent_readback': True}}

    def guarded(name, expression, actions):
        return {name: {'type': 'If', 'runAfter': {}, 'expression': expression,
                       'actions': actions, 'else': {'actions': {name + '_refused': stop('STATE_CONFLICT_NO_WRITE')}}}}

    race_condition = "@or(and(equals(outputs('Race_A')?['statusCode'],204),equals(outputs('Race_B')?['statusCode'],412)),and(equals(outputs('Race_A')?['statusCode'],412),equals(outputs('Race_B')?['statusCode'],204)))"
    settled = ['Succeeded', 'Failed', 'TimedOut', 'Skipped']
    winner_condition = "@if(equals(outputs('Race_A')?['statusCode'],204)," + equals_record('Read_race_winner', race_a) + ',' + equals_record('Read_race_winner', race_b) + ')'
    race = guarded('Race_before_guard', both([before[0]], [before[1]]), {
        'Race_A': merge(0, payload(race_a)), 'Race_B': merge(0, payload(race_b)),
        'Race_status_guard': {'type': 'If', 'expression': race_condition,
            'runAfter': {'Race_A': settled, 'Race_B': settled}, 'actions': {
                'Read_race_winner': row_get(0),
                'Race_winner_guard': {'type': 'If', 'expression': winner_condition,
                    'runAfter': {'Read_race_winner': ['Succeeded']},
                    'actions': {'Race_observed': result('ONE_204_ONE_412_REQUIRES_NATIVE_OVERLAP_AND_HISTORY_PROOF'),
                        'Race_narrow_complete': {'type': 'Terminate',
                            'runAfter': {'Race_observed': ['Succeeded']}, 'inputs': {'runStatus': 'Succeeded'}}},
                    'else': {'actions': {'Race_winner_conflict': stop('RACE_WINNER_MISMATCH')}}}},
            'else': {'actions': {'Race_status_conflict': stop('RACE_OUTCOME_UNCERTAIN')}}}})
    unknown = guarded('Unknown_before_guard', both([race_a, race_b], [before[1]]), {
        'Unknown_merge': merge(0, choose_payload(equals_record('Read_first', race_a), unknown_a, unknown_b)),
        'Unknown_state': {'type': 'Compose', 'runAfter': {'Unknown_merge': ['Succeeded']},
            'inputs': {'state': 'UNKNOWN', 'simulated_ack_loss': True,
                       'note': 'Caller receipt deliberately withheld after connector success; not a network timeout. Reconcile, never resubmit.'}},
        'Unknown_ack_fault': stop('SIMULATED_ACK_LOSS_UNKNOWN_RECONCILE', {'Unknown_state': ['Succeeded']})})
    partial = guarded('Partial_before_guard', both([unknown_a, unknown_b], [before[1]]), {
        'Partial_first_merge': merge(0, choose_payload(equals_record('Read_first', unknown_a), partial_a, partial_b)),
        'Partial_stop_before_second': stop('FIRST_SAVED_SECOND_NOT_ATTEMPTED_RECONCILE', {'Partial_first_merge': ['Succeeded']})})
    # Resume is an explicit separate invocation. It never repeats the first write.
    resume = guarded('Resume_first_guard', both([partial_a, partial_b], [before[1], second_after]), {
        'Resume_already_complete': {'type': 'If', 'runAfter': {},
            'expression': '@' + equals_record('Read_second', second_after),
            'actions': {'Resume_readonly_complete': result('BOTH_STATES_RECONCILED_NO_WRITE')},
            'else': {'actions': {
                'Resume_second_merge': merge(1, payload(second_after)),
                'Read_resume_second': row_get(1, {'Resume_second_merge': ['Succeeded']}),
                'Read_resume_first': row_get(0, {'Read_resume_second': ['Succeeded']}),
                'Resume_second_guard': {'type': 'If',
                    'expression': both([partial_a, partial_b], [second_after],
                                       'Read_resume_first', 'Read_resume_second'),
                    'runAfter': {'Read_resume_first': ['Succeeded']},
                    'actions': {'Resume_second_observed': result('SECOND_SAVED_REQUIRES_INDEPENDENT_HISTORY_PROOF')},
                    'else': {'actions': {'Resume_second_conflict': stop('SECOND_SAVE_RECONCILIATION_REQUIRED')}}}}}}})
    branches = {
        'race': race,
        'race_reconcile': guarded('Race_reconcile_guard', both([race_a, race_b], [before[1]]),
                                  {'Race_readonly': result('RACE_READONLY_RECONCILIATION')}),
        'uncertain_save': unknown,
        'uncertain_reconcile': guarded('Unknown_reconcile_guard', both([unknown_a, unknown_b], [before[1]]),
                                       {'Unknown_readonly': result('SIMULATED_LOST_ACK_COMMITTED_RECONCILED_NO_WRITE')}),
        'partial_save': partial,
        'partial_reconcile': guarded('Partial_reconcile_guard', both([partial_a, partial_b], [before[1]]),
                                     {'Partial_readonly': result('FIRST_COMMITTED_SECOND_ABSENT_NO_WRITE')}),
        'partial_resume': resume}
    read_identity = request('GET', target + '?$select=Id,Description,EnableVersioning')
    identity_expr = '@and(equals(body(\'Read_CR_fixture\')?[\'Id\'],' + literal(list_id) + "),equals(body('Read_CR_fixture')?['Description']," + literal(description) + "),equals(body('Read_CR_fixture')?['EnableVersioning'],true))"
    read_guard = '@and(' + ','.join(
        f"equals(body('{name}')?['Id'],{rid}),not(empty(body('{name}')?['odata.etag'])),not(equals(body('{name}')?['odata.etag'],'*'))"
        for name, rid in zip(('Read_first', 'Read_second'), ids)) + ')'
    gate['actions'] = {'Read_CR_fixture': read_identity,
        'CR_fixture_guard': {'type': 'If', 'runAfter': {'Read_CR_fixture': ['Succeeded']},
            'expression': identity_expr, 'actions': {
                'Read_first': row_get(0), 'Read_second': row_get(1),
                'CR_rows_guard': {'type': 'If', 'runAfter': {'Read_first': ['Succeeded'], 'Read_second': ['Succeeded']},
                    'expression': read_guard, 'actions': {'CR_case': {'type': 'Switch', 'runAfter': {},
                        'expression': "@triggerBody()?['text']",
                        'cases': {name: {'case': name, 'actions': actions} for name, actions in branches.items()},
                        'default': {'actions': {'CR_unknown_case': stop('UNKNOWN_CASE_NO_WRITE')}}}},
                    'else': {'actions': {'CR_row_identity_conflict': stop('ROW_ID_OR_ETAG_INVALID')}}}},
            'else': {'actions': {'CR_fixture_identity_conflict': stop('TARGET_UNQUALIFIED')}}}}
    if dataverse:
        # State/owner are retained evidence, not fabricated clientdata columns.
        del candidate['properties']['state']
    return {'candidate': candidate, 'review': {
        'baseline_sha256': pin, 'native_deployment_ready': False,
        'baseline_kind': 'Dataverse workflow record' if dataverse else 'Flow RP object',
        'baseline_identity': {k: native_baseline[k] for k in
                              ('workflowid', 'workflowidunique', 'name', '_ownerid_value',
                               'statecode', 'statuscode', 'ismanaged') if k in native_baseline},
        'qualification_required': ['fixture effects', 'exact row bindings and before images',
                                   'existing Invoker reference', 'native schema validation', 'feature/journal gate'],
        'row_ids': ids, 'before': before,
        'states': {'race_a': race_a, 'race_b': race_b, 'unknown_a': unknown_a,
                   'unknown_b': unknown_b, 'partial_a': partial_a, 'partial_b': partial_b,
                   'second_after': second_after},
        'uncertainty_model': 'Deliberate post-success fault; simulated lost acknowledgement, not network timeout.',
        'race_proof_required': 'Exactly one204/one412 AND overlapping native action intervals AND one version increment/full winner/history.',
        'final_required': 'Independent both-row fields/ETags/history and untouched rows1-4; restore original full graph/refs/owner/Off.'}}


def bindings_from_workspace(workspace: dict, binding: dict) -> dict:
    """Resolve the recorded target; this checks drift, not permission or authority."""
    from urllib.parse import unquote, urlsplit

    active = workspace['feature_control']['active_feature']
    if active != 'F09-reviewed-outcome-commit':
        raise ValueError('F09 is not the selected feature')
    assets = [a for a in workspace['assets'] if a['key'] == 'f09_commissioning_fixture']
    if len(assets) != 1 or assets[0]['status'] != 'found':
        raise ValueError('One confirmed commissioning fixture is required')
    asset = assets[0]
    receipt = workspace['runtime_readbacks']['f09_isolated_fixture_created_20261011']
    observation = receipt['result']['list']
    if observation['status'] != 200:
        raise ValueError('Native fixture readback is unavailable')
    native = observation['data']
    created = receipt['creation_identity']
    if asset['resource_id'] != native['Id'] or created['id'] != native['Id']:
        raise ValueError('Fixture identity drift; no candidate generated')
    if not native['EnableVersioning'] or native['EnableAttachments'] or native['OnQuickLaunch']:
        raise ValueError('Fixture defaults changed; review before generating')
    site = workspace['target']['site_url'].rstrip('/')
    site_url, asset_url = urlsplit(site), urlsplit(asset['url'])
    folder = native['RootFolder']['ServerRelativeUrl']
    if (site_url.scheme != 'https' or asset_url.scheme != 'https'
            or site_url.netloc != asset_url.netloc
            or not folder.startswith(site_url.path.rstrip('/') + '/Lists/')
            or unquote(asset_url.path) != folder + '/AllItems.aspx'):
        raise ValueError('Fixture site/path drift; no candidate generated')
    if (binding['statecode'] != 0 or not binding.get('connectionid')
            or binding['connectorid'] != '/providers/Microsoft.PowerApps/apis/shared_sharepointonline'):
        raise ValueError('Expected the qualified active SharePoint reference')
    entity = created['list_item_entity_type']
    if not entity.startswith('SP.Data.') or not entity.endswith('ListItem'):
        raise ValueError('Native item entity type is missing; do not derive it from a title')
    return dict(site=site, list_id=native['Id'], description=native['Description'],
                entity_type=entity, reference=binding['connectionreferencelogicalname'])


def main() -> None:
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Build the isolated F09 trial from existing private bindings; no tenant calls.')
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--binding', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    workspace_path = args.workspace.resolve()
    if workspace_path.parent.name != 'ops' or workspace_path.parent.parent.name != 'private':
        parser.error('Use the existing private/ops/workspace.json')
    private_working = workspace_path.parent.parent / 'working'
    if not args.output.resolve().is_relative_to(private_working.resolve()):
        parser.error('Generated tenant bindings must remain in private/working')
    workspace = json.loads(workspace_path.read_text())
    binding = json.loads(args.binding.read_text())
    baseline = json.loads(args.baseline.read_text())
    candidate = build_trial(json.loads(baseline['clientdata']),
                            **bindings_from_workspace(workspace, binding))
    # Creation-only prevents a retry from replacing a reviewed candidate/evidence.
    with args.output.open('x') as stream:
        json.dump({'clientdata': json.dumps(candidate, separators=(',', ':'))}, stream)
    print('Private F09 candidate generated. No tenant operation performed.')


if __name__ == '__main__':
    main()
