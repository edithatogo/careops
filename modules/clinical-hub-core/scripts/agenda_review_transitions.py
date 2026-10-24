"""Pure proposal validator for synthetic agenda-preparation review states.

The permission matrix and source bindings are caller-supplied test claims. This
module authenticates no person, persists no state, and makes no decision about
the substance of an agenda item.
"""
from copy import deepcopy


STATES = {
    'draft', 'ready_for_review', 'returned_for_change', 'deferred',
    'approved_for_pack', 'review_required', 'revoked',
}
ACTIONS = {
    'mark_ready', 'approve_for_pack', 'return_for_change', 'defer',
    'revoke_approval',
}
BINDING_FIELDS = {
    'meeting_id', 'item_id', 'item_revision', 'paper_id', 'paper_revision',
    'audience_revision', 'permission_revision',
}
ITEM_FIELDS = BINDING_FIELDS | {
    'has_paper', 'has_solution', 'is_concern', 'urgent', 'restricted',
    'concern_text', 'dissent',
}
STATE_FIELDS = {'status', 'state_version', 'binding', 'history'}
REQUEST_FIELDS = {'expected_state_version', 'actor_role', 'action', 'request_id', 'reason'}
POLICY_FIELDS = {'revision', 'actions_by_role'}


def _blocked(code, message):
    """Return static diagnostics; never echo caller-provided text."""
    return {
        'ok': False,
        'code': code,
        'message': message,
        'proposal': None,
        'substantive_decision_authority': False,
        'delivery_claim': False,
        'external_write': False,
    }


def _valid_text(value):
    return isinstance(value, str) and bool(value.strip())


def _binding(item):
    return {key: item[key] for key in BINDING_FIELDS}


def _valid_item(item):
    if not isinstance(item, dict) or set(item) != ITEM_FIELDS:
        return False
    if not all(_valid_text(item[k]) for k in ('meeting_id', 'item_id', 'item_revision', 'audience_revision', 'permission_revision')):
        return False
    if type(item['has_paper']) is not bool or type(item['has_solution']) is not bool:
        return False
    if type(item['is_concern']) is not bool or type(item['urgent']) is not bool or type(item['restricted']) is not bool:
        return False
    if item['has_paper']:
        if not _valid_text(item['paper_id']) or not _valid_text(item['paper_revision']):
            return False
    elif item['paper_id'] is not None or item['paper_revision'] is not None:
        return False
    if not isinstance(item['concern_text'], str) or not isinstance(item['dissent'], list):
        return False
    return all(isinstance(value, str) for value in item['dissent'])


def _valid_state(state):
    binding = state.get('binding') if isinstance(state, dict) else None
    binding_valid = binding is None or (
        isinstance(binding, dict)
        and set(binding) == BINDING_FIELDS
        and all(_valid_text(binding[k]) for k in BINDING_FIELDS - {'paper_id', 'paper_revision'})
        and ((binding['paper_id'] is None and binding['paper_revision'] is None)
             or (_valid_text(binding['paper_id']) and _valid_text(binding['paper_revision'])))
    )
    return (
        isinstance(state, dict)
        and set(state) == STATE_FIELDS
        and isinstance(state['status'], str)
        and state['status'] in STATES
        and type(state['state_version']) is int
        and state['state_version'] >= 0
        and binding_valid
        and isinstance(state['history'], list)
        and all(isinstance(event, dict) for event in state['history'])
    )


def _valid_policy(policy):
    if not isinstance(policy, dict) or set(policy) != POLICY_FIELDS or not _valid_text(policy['revision']):
        return False
    grants = policy['actions_by_role']
    if not isinstance(grants, dict):
        return False
    for role, actions in grants.items():
        if not _valid_text(role) or not isinstance(actions, list):
            return False
        if any(not isinstance(action, str) or action not in ACTIONS for action in actions):
            return False
    return True


def _review_context(item, current_state):
    concern = None
    if item['is_concern']:
        concern = {
            'status': 'retained_for_human_review',
            'text': item['concern_text'],
            'paper_required': False,
            'urgent': item['urgent'],
            'manual_route_reference': 'existing manual urgent concern route' if item['urgent'] else None,
            'delivery_claim': False,
        }
    return {
        'concern_review': concern,
        'retained_dissent': list(item['dissent']),
        'current_preparation_state': current_state['status'],
        'substantive_decision_authority': False,
        'delivery_claim': False,
        'external_write': False,
    }


def propose_transition(item, current_state, request, policy):
    """Validate one local transition proposal without persisting it.

    A non-null result proposal is still only a value returned to the caller.
    Any future adapter must independently re-read and atomically compare the
    persisted state version before saving it.
    """
    # Restricted items are rejected before validating or copying any content.
    if isinstance(item, dict) and item.get('restricted') is True:
        return _blocked('RESTRICTED', 'Restricted item is not available through this review path.')
    if not _valid_item(item) or not _valid_state(current_state) or not _valid_policy(policy):
        return _blocked('INVALID_INPUT', 'Review input is incomplete or malformed.')
    if policy['revision'] != item['permission_revision']:
        return _blocked('POLICY_BINDING_MISMATCH', 'Permission policy revision does not match the item binding.')

    if request is not None:
        if not isinstance(request, dict) or set(request) != REQUEST_FIELDS:
            return _blocked('INVALID_REQUEST', 'Transition request is incomplete or malformed.')
        if (type(request['expected_state_version']) is not int or request['expected_state_version'] < 0
                or request['expected_state_version'] != current_state['state_version']):
            return _blocked('STALE_STATE_VERSION', 'Current state changed; reread and reconcile before proposing a transition.')

    binding = _binding(item)
    state = deepcopy(current_state)
    if state['binding'] is not None and state['binding'] != binding and state['status'] != 'draft':
        old_binding = state['binding']
        changed = sorted(key for key in BINDING_FIELDS if old_binding[key] != binding[key])
        if {'meeting_id', 'item_id'} & set(changed):
            return _blocked('ITEM_OR_MEETING_SUBSTITUTED', 'This review history belongs to a different meeting or item; reconcile it separately.')
        before = state['status']
        state.update(status='review_required', state_version=state['state_version'] + 1, binding=binding)
        state['history'].append({
            'event': 'stale_binding_invalidation_proposed',
            'from': before,
            'to': 'review_required',
            'changed_binding_fields': changed,
            'prior_approval_retained': before == 'approved_for_pack',
        })
        return {
            'ok': False,
            'code': 'STALE_BINDING',
            'message': 'A bound item, paper, meeting, audience, or permission revision changed; review is required.',
            'proposal': state,
            **_review_context(item, current_state),
        }

    if request is None:
        return {
            'ok': True,
            'code': 'REVIEW_CONTEXT_ONLY',
            'message': 'Review context is available for human review; no transition was proposed.',
            'proposal': None,
            **_review_context(item, current_state),
        }
    if not all(_valid_text(request[k]) for k in ('actor_role', 'action', 'request_id')):
        return _blocked('INVALID_REQUEST', 'Transition request is incomplete or malformed.')
    if request['action'] not in ACTIONS or request['action'] not in policy['actions_by_role'].get(request['actor_role'], []):
        return _blocked('NOT_AUTHORIZED_BY_SUPPLIED_POLICY', 'The supplied synthetic policy does not permit this role/action.')
    if any(event.get('request_id') == request['request_id'] for event in state['history']):
        return _blocked('DUPLICATE_REQUEST', 'This request identifier is already present in the supplied history.')

    action = request['action']
    transitions = {
        'mark_ready': {'draft', 'returned_for_change', 'deferred', 'review_required'},
        'approve_for_pack': {'ready_for_review'},
        'return_for_change': {'ready_for_review'},
        'defer': {'draft', 'ready_for_review', 'returned_for_change', 'review_required'},
        'revoke_approval': {'approved_for_pack'},
    }
    if state['status'] not in transitions[action]:
        return _blocked('INVALID_TRANSITION', 'The proposed transition is not valid from the current preparation state.')
    if action in {'mark_ready', 'approve_for_pack'} and not item['has_paper']:
        # An incomplete concern remains visible in review_context; it is not
        # converted into a ready or approved agenda item.
        return {
            'ok': False,
            'code': 'PAPER_REQUIRED_FOR_PACK_STATE',
            'message': 'A paper is required for pack readiness; any concern remains available for separate human review.',
            'proposal': None,
            **_review_context(item, current_state),
        }
    if action in {'return_for_change', 'defer'} and not _valid_text(request['reason']):
        return _blocked('REASON_REQUIRED', 'Return or deferral needs a concise reason.')

    target = {
        'mark_ready': 'ready_for_review',
        'approve_for_pack': 'approved_for_pack',
        'return_for_change': 'returned_for_change',
        'defer': 'deferred',
        'revoke_approval': 'revoked',
    }[action]
    before = state['status']
    state.update(status=target, state_version=state['state_version'] + 1, binding=binding)
    state['history'].append({
        'request_id': request['request_id'],
        'event': action,
        'from': before,
        'to': target,
        'actor_role': request['actor_role'],
        'permission_revision': policy['revision'],
        'reason': request['reason'] if action in {'return_for_change', 'defer'} else None,
        'prior_approval_retained': action == 'revoke_approval',
    })
    return {
        'ok': True,
        'code': 'TRANSITION_PROPOSAL',
        'message': 'Preparation transition proposed for a separate current-state check; no decision or write occurred.',
        'proposal': state,
        **_review_context(item, current_state),
    }
