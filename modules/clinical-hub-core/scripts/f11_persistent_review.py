"""Build the Standard SharePoint F11 fictional state writer; no local runtime."""
from copy import deepcopy
from uuid import UUID

FIELD = 'Agenda_x0020_review_x0020_bindin'
TRANSITIONS = {
    'mark_ready': (['draft', 'returned_for_change', 'deferred', 'review_required'], 'ready_for_review'),
    'approve_for_pack': (['ready_for_review'], 'approved_for_pack'),
    'return_for_change': (['ready_for_review'], 'returned_for_change'),
    'defer': (['draft', 'ready_for_review', 'returned_for_change', 'review_required'], 'deferred'),
    'revoke_approval': (['approved_for_pack'], 'revoked'),
}

SOURCE_FIELDS = ('Title', 'Question_x0020_or_x0020_help_x00', 'Meeting_x0020_date',
                 'Purpose', 'Disposition')


def envelope_schema():
    """Fail closed before expressions consume persisted commissioning data."""
    binding = {'type': 'object', 'required': ['meeting_id', 'item_id', 'item_revision',
        'paper_id', 'paper_revision', 'audience_revision', 'permission_revision'],
        'properties': {k: {'type': 'string', 'minLength': 1} for k in
            ('meeting_id', 'item_id', 'item_revision', 'audience_revision', 'permission_revision')}}
    binding['properties'].update({k: {'type': ['string', 'null']} for k in ('paper_id', 'paper_revision')})
    props = {'schema': {'type': 'string', 'enum': ['f11-review-v1']},
        'synthetic_only': {'type': 'boolean', 'enum': [True]}, 'item_id': {'type': 'integer'},
        'item_guid': {'type': 'string'}, 'state_version': {'type': 'integer', 'minimum': 0},
        'status': {'type': 'string', 'enum': ['draft', 'ready_for_review', 'returned_for_change',
            'deferred', 'approved_for_pack', 'review_required', 'revoked']},
        'binding': deepcopy(binding), 'current_binding': deepcopy(binding),
        'restricted': {'type': 'boolean'}, 'has_paper': {'type': 'boolean'},
        'concern_text': {'type': 'string'}, 'urgent': {'type': 'boolean'},
        'dissent': {'type': 'array', 'items': {'type': 'string'}},
        'history': {'type': 'array', 'items': {'type': 'object'}},
        'source_snapshot': {'type': 'object', 'required': list(SOURCE_FIELDS)},
        'policy': {'type': 'object', 'required': ['revision', 'actions_by_role'], 'properties': {
            'revision': {'type': 'string', 'minLength': 1},
            'actions_by_role': {'type': 'object', 'properties': {role: {
                'type': 'array', 'items': {'type': 'string', 'enum': list(TRANSITIONS)}}
                for role in ('chair', 'secretariat', 'preparer')},
                'required': ['chair', 'secretariat', 'preparer']}}}}
    return {'type': 'object', 'properties': props, 'required': list(props)}


def build_persistent_review(baseline, *, site, list_id, item_id, item_guid, title, entity_type):
    """Exact fictional target; owner-operated role simulation, no role grants.

    State envelope is initialized separately with native identity, versioned item
    and paper bindings, policy, concerns/dissent and append-only history. Request
    inputs cannot supply or replace that envelope. One conditional field write.
    """
    if (str(UUID(list_id)) != list_id or str(UUID(item_guid)) != item_guid
            or type(item_id) is not int or item_id < 1
            or not title.startswith('FICTIONAL ') or not entity_type.startswith('SP.Data.')
            or not site.startswith('https://fictional-example.sharepoint.com/teams/')):
        raise ValueError('Qualified exact fictional target required')
    if baseline['properties'].get('state') != 'Stopped':
        raise ValueError('Stopped canonical preimage required')
    result = deepcopy(baseline)
    d = result['properties']['definition']
    fields = {'request_id': {'type': 'string', 'minLength': 1},
              'expected_version': {'type': 'integer', 'minimum': 0},
              'actor_role': {'type': 'string', 'enum': ['chair', 'secretariat', 'preparer']},
              'action': {'type': 'string', 'enum': list(TRANSITIONS)},
              'reason': {'type': 'string'}, 'expected_etag': {'type': 'string', 'minLength': 1}}
    d['triggers'] = {'manual': {'type': 'Request', 'kind': 'Button', 'inputs': {
        'schema': {'type': 'object', 'properties': fields, 'required': list(fields)}}}}
    uri = f"_api/web/lists(guid'{list_id}')/items({item_id})"
    def after(name): return {name: ['Succeeded']}
    def compose(value, predecessor):
        return {'type': 'Compose', 'inputs': value, 'runAfter': after(predecessor)}
    def stop(code):
        return {'type': 'Terminate', 'inputs': {'runStatus': 'Failed', 'runError': {
            'code': code, 'message': 'No retry: reread source, state and native history; preserve human edits.'}}, 'runAfter': {}}
    def guard(expr, predecessor, code):
        return {'type': 'If', 'expression': expr, 'runAfter': after(predecessor),
                'actions': {}, 'else': {'actions': {code: stop(code)}}}
    def sp(method, predecessor=None, body=None, headers=None):
        params = {'dataset': site, 'parameters/method': method, 'parameters/uri': uri,
                  'parameters/headers': headers or {'Accept': 'application/json;odata=minimalmetadata'}}
        if body is not None: params['parameters/body'] = body
        return {'type': 'OpenApiConnection', 'inputs': {'host': {
            'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
            'connectionName': 'shared_sharepointonline', 'operationId': 'HttpRequest'}, 'parameters': params,
            'retryPolicy': {'type': 'none'}}, 'runAfter': after(predecessor) if predecessor else {}}
    a = {'Read_review_item': sp('GET')}
    a['Identity_guard'] = guard("@and(equals(body('Read_review_item')?['Id']," + str(item_id) +
        "),equals(toLower(body('Read_review_item')?['GUID']),'" + item_guid +
        "'),equals(body('Read_review_item')?['Title'],'" + title.replace("'", "''") +
        "'),equals(coalesce(outputs('Read_review_item')?['headers']?['ETag'],outputs('Read_review_item')?['headers']?['etag'],body('Read_review_item')?['odata.etag']),triggerBody()?['expected_etag']))", 'Read_review_item', 'IDENTITY_OR_ETAG_STOP')
    a['Parse_envelope'] = {'type': 'ParseJson', 'runAfter': after('Identity_guard'),
        'inputs': {'content': "@json(body('Read_review_item')?['" + FIELD + "'])", 'schema': envelope_schema()}}
    a['State'] = compose("@body('Parse_envelope')", 'Parse_envelope')
    a['Scope_guard'] = guard("@and(equals(outputs('State')?['synthetic_only'],true),equals(outputs('State')?['schema'],'f11-review-v1'),equals(outputs('State')?['state_version'],triggerBody()?['expected_version']),equals(outputs('State')?['item_id']," + str(item_id) + "),equals(outputs('State')?['item_guid'],'" + item_guid + "'),not(equals(outputs('State')?['restricted'],true)))", 'State', 'SCOPE_OR_VERSION_STOP')
    a['Duplicate_requests'] = {'type': 'Query', 'runAfter': after('Scope_guard'), 'inputs': {
        'from': "@outputs('State')?['history']", 'where': "@equals(item()?['request_id'],triggerBody()?['request_id'])"}}
    a['Request_guard'] = guard("@and(empty(body('Duplicate_requests')),contains(outputs('State')?['policy']?['actions_by_role']?[triggerBody()?['actor_role']],triggerBody()?['action']))", 'Duplicate_requests', 'ROLE_OR_REPLAY_STOP')
    a['Policy_guard'] = guard("@equals(outputs('State')?['policy']?['revision'],outputs('State')?['current_binding']?['permission_revision'])", 'Request_guard', 'POLICY_REVISION_STOP')
    a['Native_source'] = compose({k: "@body('Read_review_item')?['" + k + "']" for k in SOURCE_FIELDS}, 'Policy_guard')
    a['Binding_changed'] = compose("@or(not(equals(outputs('State')?['binding'],outputs('State')?['current_binding'])),not(equals(outputs('State')?['source_snapshot'],outputs('Native_source'))))", 'Native_source')
    valid = []
    for action, (sources, _) in TRANSITIONS.items():
        arr = ','.join("'" + s + "'" for s in sources)
        valid.append("and(equals(triggerBody()?['action'],'" + action + "'),contains(createArray(" + arr + "),outputs('State')?['status']))")
    a['Transition_guard'] = guard("@or(and(outputs('Binding_changed'),not(equals(outputs('State')?['status'],'draft')))," + ','.join(valid) + ")", 'Binding_changed', 'INVALID_TRANSITION_STOP')
    a['Content_guard'] = guard("@and(equals(outputs('State')?['binding']?['meeting_id'],outputs('State')?['current_binding']?['meeting_id']),equals(outputs('State')?['binding']?['item_id'],outputs('State')?['current_binding']?['item_id']),or(outputs('Binding_changed'),not(contains(createArray('mark_ready','approve_for_pack'),triggerBody()?['action'])),equals(outputs('State')?['has_paper'],true)),or(outputs('Binding_changed'),not(contains(createArray('return_for_change','defer'),triggerBody()?['action'])),not(empty(trim(triggerBody()?['reason'])))))", 'Transition_guard', 'CONTENT_OR_SUBSTITUTION_STOP')
    target = "'revoked'"
    for action, (_, status) in reversed(list(TRANSITIONS.items())[:-1]):
        target = "if(equals(triggerBody()?['action'],'" + action + "'),'" + status + "'," + target + ")"
    a['Target_state'] = compose("@if(and(outputs('Binding_changed'),not(equals(outputs('State')?['status'],'draft'))),'review_required'," + target + ")", 'Content_guard')
    event = {'request_id': "@triggerBody()?['request_id']", 'event': "@if(outputs('Binding_changed'),'binding_invalidation',triggerBody()?['action'])", 'from': "@outputs('State')?['status']", 'to': "@outputs('Target_state')", 'actor_role_claim': "@triggerBody()?['actor_role']", 'reason': "@triggerBody()?['reason']", 'prior_binding': "@outputs('State')?['binding']", 'at': '@utcNow()', 'fictional_only': True}
    a['Event'] = compose(event, 'Target_state')
    event.update({
        'prior_source_snapshot': "@outputs('State')?['source_snapshot']",
        'prior_approval_retained': "@equals(outputs('State')?['status'],'approved_for_pack')",
        'permission_revision': "@outputs('State')?['policy']?['revision']",
    })
    a['Next_state'] = compose("@setProperty(setProperty(setProperty(setProperty(outputs('State'),'status',outputs('Target_state')),'state_version',add(outputs('State')?['state_version'],1)),'binding',outputs('State')?['current_binding']),'history',union(outputs('State')?['history'],createArray(outputs('Event'))))", 'Event')
    a['Next_state']['inputs'] = "@setProperty(" + a['Next_state']['inputs'][1:] + ",'source_snapshot',outputs('Native_source'))"
    a['Save_review_state'] = sp('POST', 'Next_state', {'__metadata': {'type': entity_type}, FIELD: "@string(outputs('Next_state'))"}, {
        'Accept': 'application/json;odata=nometadata', 'Content-Type': 'application/json;odata=verbose',
        'IF-MATCH': "@triggerBody()?['expected_etag']", 'X-HTTP-Method': 'MERGE'})
    a['Read_saved_state'] = sp('GET', 'Save_review_state')
    a['Saved_state_guard'] = guard("@equals(json(body('Read_saved_state')?['" + FIELD + "']),outputs('Next_state'))", 'Read_saved_state', 'UNCERTAIN_SAVE_RECONCILE')
    a['Result'] = compose({'status': 'FICTIONAL_REVIEW_STATE_SAVED', 'state': "@outputs('Target_state')", 'substantive_approval': False, 'notified': False}, 'Saved_state_guard')
    d['actions'] = a
    return result
