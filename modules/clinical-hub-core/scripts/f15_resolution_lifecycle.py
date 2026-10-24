"""F15 fictional lifecycle contract; native persistence is a separate adapter.

Role, evidence and authority references here are explicit commissioning claims,
never authentication or substantive clinical/business approval.
"""
from copy import deepcopy
from datetime import date

STATES = {'open', 'referred', 'held', 'returned', 'resolved', 'superseded', 'reopened'}
ACTIONS = {'record_response', 'report_complete', 'refer', 'hold', 'return', 'resolve', 'supersede', 'reopen'}
OPEN_STATES = {'open', 'referred', 'held', 'returned', 'reopened'}


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _date_valid(value):
    if value.get('date_state') in {'unknown', 'ambiguous'}:
        return value.get('date_value') is None
    if value.get('date_state') != 'known' or not isinstance(value.get('date_value'), str):
        return False
    try:
        return date.fromisoformat(value['date_value']).isoformat() == value['date_value']
    except ValueError:
        return False


def propose_lifecycle(state, request):
    """Return a full next-state proposal, preserving input/history without writes."""
    def stop(code):
        return {'ok': False, 'code': code, 'proposal': None, 'business_approval': False}
    if not isinstance(state, dict) or state.get('synthetic_only') is not True:
        return stop('FICTIONAL_SCOPE_REQUIRED')
    if (state.get('schema') != 'f15-lifecycle-v1' or not isinstance(state.get('status'), str) or state['status'] not in STATES
            or type(state.get('state_version')) is not int or state['state_version'] < 0
            or not isinstance(state.get('history'), list) or not isinstance(state.get('responses'), list)
            or not isinstance(state.get('binding'), dict) or not isinstance(state.get('current_binding'), dict)
            or not isinstance(state.get('policy'), dict)
            or not isinstance(state.get('required_components'), list)
            or not all(_text(c) for c in state['required_components'])
            or not all(isinstance(e, dict) and _text(e.get('request_id')) for e in state['history'])
            or not all(isinstance(r, dict) and _text(r.get('response_id')) for r in state['responses'])):
        return stop('INVALID_STATE')
    if not isinstance(request, dict) or not all(_text(request.get(k)) for k in ('request_id', 'actor_role', 'action')):
        return stop('INVALID_REQUEST')
    if type(request.get('expected_version')) is not int or request['expected_version'] != state['state_version']:
        return stop('STALE_STATE')
    if any(e.get('request_id') == request['request_id'] for e in state['history']):
        return stop('DUPLICATE_REQUEST')
    action = request['action']
    if action not in ACTIONS or action not in state['policy'].get('actions_by_role', {}).get(request['actor_role'], []):
        return stop('ROLE_REFUSED')
    binding = state['binding']; current = state['current_binding']
    if binding != current:
        return stop('SOURCE_BINDING_CHANGED')
    if state['policy'].get('revision') != binding.get('permission_revision'):
        return stop('POLICY_CHANGED')
    if not all(_text(binding.get(k)) for k in ('action_id', 'register_revision', 'minutes_record_id', 'minutes_revision', 'permission_revision')):
        return stop('SOURCE_BINDING_INCOMPLETE')
    s = deepcopy(state); before = s['status']; evidence = request.get('evidence_ref')
    reason = request.get('reason')
    if action in {'refer', 'hold', 'return', 'supersede', 'reopen', 'resolve'} and not _text(reason):
        return stop('REASON_REQUIRED')
    if action in {'refer', 'hold', 'return', 'report_complete', 'resolve', 'supersede'} and before not in OPEN_STATES:
        return stop('INVALID_TRANSITION')
    if action == 'report_complete':
        s['reported_completion'] = 'complete'
    elif action == 'record_response':
        response = request.get('response')
        if (not isinstance(response, dict) or not all(_text(response.get(k)) for k in
                ('response_id', 'evidence_ref', 'evidence_revision'))
                or response.get('action_id') != binding['action_id']
                or not isinstance(response.get('state'), str)
                or response['state'] not in {'partial', 'complete', 'disputed', 'withdrawn', 'delayed'}
                or not isinstance(response.get('relevance'), str)
                or response['relevance'] not in {'not_reviewed', 'relevant', 'partial', 'irrelevant', 'disputed'}
                or not _date_valid(response) or not isinstance(response.get('components'), list)
                or not all(_text(c) for c in response['components'])):
            return stop('INVALID_RESPONSE')
        if any(r.get('response_id') == response['response_id'] for r in s['responses']):
            return stop('DUPLICATE_RESPONSE')
        supersedes = response.get('supersedes', [])
        if (not isinstance(supersedes, list) or not all(_text(x) for x in supersedes)
                or not set(supersedes) <= {r['response_id'] for r in s['responses']}):
            return stop('RESPONSE_SUPERSESSION_INVALID')
        if before == 'resolved' and response['state'] in {'disputed', 'withdrawn'}:
            s['status'] = 'reopened'
        elif before not in OPEN_STATES:
            return stop('INVALID_TRANSITION')
        s['responses'].append(deepcopy(response))
    elif action == 'resolve':
        closure = request.get('closure')
        if (not isinstance(closure, dict) or not all(_text(closure.get(k)) for k in
                ('authority_ref', 'decision_ref', 'decision_revision', 'evidence_ref'))
                or closure['decision_ref'] != binding['minutes_record_id']
                or closure['decision_revision'] != binding['minutes_revision'] or not _date_valid(closure)):
            return stop('CLOSURE_EVIDENCE_REQUIRED')
        superseded = {key for r in s['responses'] for key in r.get('supersedes', [])}
        responses = [r for r in s['responses'] if r['response_id'] not in superseded]
        if not responses or any(r.get('state') != 'complete' or r.get('relevance') != 'relevant' for r in responses):
            return stop('RESPONSE_REVIEW_REQUIRED')
        covered = {c for r in responses for c in r.get('components', [])}
        if not set(s['required_components']) <= covered:
            return stop('RESPONSE_COMPONENTS_UNCOVERED')
        s['status'] = 'resolved'; s['closure'] = deepcopy(closure)
    elif action == 'supersede':
        if not _text(evidence) or not _text(request.get('successor_ref')):
            return stop('SUCCESSOR_EVIDENCE_REQUIRED')
        s['status'] = 'superseded'; s['successor_ref'] = request['successor_ref']
    elif action == 'reopen':
        if before not in {'resolved', 'superseded'} or not _text(evidence):
            return stop('REOPEN_EVIDENCE_REQUIRED')
        s['status'] = 'reopened'
    else:
        s['status'] = {'refer': 'referred', 'hold': 'held', 'return': 'returned'}[action]
    s['state_version'] += 1
    s['history'].append({'request_id': request['request_id'], 'event': action,
        'from': before, 'to': s['status'], 'actor_role_claim': request['actor_role'],
        'reason': reason, 'evidence_ref': evidence, 'prior_closure': deepcopy(state.get('closure')),
        'prior_event_id': state['history'][-1]['request_id'] if state['history'] else None,
        'fictional_only': True})
    return {'ok': True, 'code': 'FICTIONAL_TRANSITION_PROPOSAL', 'proposal': s, 'business_approval': False}
