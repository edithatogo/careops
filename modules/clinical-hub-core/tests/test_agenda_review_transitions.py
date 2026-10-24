"""Synthetic F11 transition cases; no storage, network or tenant access."""
import copy
import ast
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from agenda_review_transitions import propose_transition


def item(**changes):
    value = {
        'meeting_id': 'MEETING-SYN-01',
        'item_id': 'AGENDA-SYN-01',
        'item_revision': 'item-r1',
        'paper_id': 'PAPER-SYN-01',
        'paper_revision': 'paper-r1',
        'audience_revision': 'audience-r1',
        'permission_revision': 'policy-r1',
        'has_paper': True,
        'has_solution': True,
        'is_concern': False,
        'urgent': False,
        'restricted': False,
        'concern_text': '',
        'dissent': [],
    }
    value.update(changes)
    return value


def policy(**changes):
    value = {
        'revision': 'policy-r1',
        'actions_by_role': {
            'secretariat': ['mark_ready', 'return_for_change', 'defer'],
            'chair': ['approve_for_pack', 'return_for_change', 'defer', 'revoke_approval'],
        },
    }
    value.update(changes)
    return value


def state(status='draft', version=0, binding=None, history=None):
    return {
        'status': status,
        'state_version': version,
        'binding': copy.deepcopy(binding),
        'history': copy.deepcopy(history or []),
    }


def request(action, role='secretariat', version=0, request_id='REQ-SYN-01', reason=''):
    return {
        'expected_state_version': version,
        'actor_role': role,
        'action': action,
        'request_id': request_id,
        'reason': reason,
    }


def ready_state():
    result = propose_transition(item(), state(), request('mark_ready'), policy())
    assert result['ok']
    return result['proposal']


def approved_state():
    ready = ready_state()
    result = propose_transition(item(), ready, request('approve_for_pack', 'chair', 1, 'REQ-SYN-02'), policy())
    assert result['ok']
    return result['proposal']


def test_synthetic_role_matrix_separates_readiness_from_pack_approval():
    ready = propose_transition(item(), state(), request('mark_ready'), policy())
    assert ready['ok']
    assert ready['proposal']['status'] == 'ready_for_review'
    assert ready['substantive_decision_authority'] is False

    approved = propose_transition(item(), ready['proposal'], request('approve_for_pack', 'chair', 1, 'REQ-SYN-02'), policy())
    assert approved['ok']
    assert approved['proposal']['status'] == 'approved_for_pack'
    assert approved['substantive_decision_authority'] is False
    assert approved['external_write'] is False
    assert 'decision' not in approved['message'].casefold() or 'no decision' in approved['message'].casefold()


@pytest.mark.parametrize('role,action', [
    ('unknown-role', 'mark_ready'),
    ('secretariat', 'approve_for_pack'),
    ('chair', 'mark_ready'),
    ('chair', 'invent_action'),
])
def test_unknown_or_ungranted_role_action_is_blocked(role, action):
    result = propose_transition(item(), state(), request(action, role), policy())
    assert not result['ok']
    assert result['code'] == 'NOT_AUTHORIZED_BY_SUPPLIED_POLICY'
    assert result['proposal'] is None


def test_caller_supplied_policy_is_not_treated_as_authority():
    custom = policy(actions_by_role={'synthetic-role': ['mark_ready']})
    result = propose_transition(item(), state(), request('mark_ready', 'synthetic-role'), custom)
    assert result['ok']
    assert result['substantive_decision_authority'] is False
    assert result['proposal']['status'] == 'ready_for_review'


@pytest.mark.parametrize('field,value', [
    ('item_revision', 'item-r2'),
    ('paper_id', 'PAPER-SYN-02'),
    ('paper_revision', 'paper-r2'),
    ('audience_revision', 'audience-r2'),
    ('permission_revision', 'policy-r2'),
])
def test_revision_drift_invalidates_current_readiness_and_preserves_history(field, value):
    prior = approved_state()
    old_history = copy.deepcopy(prior['history'])
    changed_item = item(**{field: value})
    changed_policy = policy(revision='policy-r2') if field == 'permission_revision' else policy()
    result = propose_transition(changed_item, prior, None, changed_policy)
    assert not result['ok']
    assert result['code'] == 'STALE_BINDING'
    assert result['proposal']['status'] == 'review_required'
    assert result['proposal']['state_version'] == prior['state_version'] + 1
    assert result['proposal']['history'][:len(old_history)] == old_history
    invalidation = result['proposal']['history'][-1]
    assert invalidation['event'] == 'stale_binding_invalidation_proposed'
    assert invalidation['prior_approval_retained'] is True
    assert field in invalidation['changed_binding_fields']
    assert result['substantive_decision_authority'] is False


@pytest.mark.parametrize('field,value', [
    ('item_id', 'AGENDA-SYN-02'),
    ('meeting_id', 'MEETING-SYN-02'),
])
def test_substituted_item_or_meeting_does_not_inherit_old_history(field, value):
    prior = approved_state()
    result = propose_transition(item(**{field: value}), prior, None, policy())
    assert result['code'] == 'ITEM_OR_MEETING_SUBSTITUTED'
    assert result['proposal'] is None


def test_stale_competing_proposal_is_rejected_after_current_version_moves():
    base = state()
    first = propose_transition(item(), base, request('mark_ready', version=0), policy())
    assert first['ok']
    # Model an independently persisted proposal for the next read. The helper
    # itself neither persists nor provides atomic compare-and-swap semantics.
    current = first['proposal']
    stale = propose_transition(item(), current, request('defer', version=0, request_id='REQ-SYN-02', reason='Synthetic deferral'), policy())
    assert stale['code'] == 'STALE_STATE_VERSION'
    assert stale['proposal'] is None
    assert current['status'] == 'ready_for_review'
    assert len(current['history']) == 1


def test_restricted_item_returns_content_free_blocker():
    value = item(restricted=True, concern_text='SYNTHETIC-SECRET-CONCERN', dissent=['SYNTHETIC-SECRET-DISSENT'])
    result = propose_transition(value, state(), request('mark_ready'), policy())
    rendered = repr(result)
    assert result['code'] == 'RESTRICTED'
    assert result['proposal'] is None
    assert 'SYNTHETIC-SECRET' not in rendered
    assert value['concern_text'] == 'SYNTHETIC-SECRET-CONCERN'


def test_incomplete_urgent_concern_remains_reviewable_without_claiming_delivery():
    concern = item(
        paper_id=None, paper_revision=None, has_paper=False, has_solution=False,
        is_concern=True, urgent=True, concern_text='Synthetic urgent concern',
    )
    result = propose_transition(concern, state(), None, policy())
    assert result['ok']
    assert result['code'] == 'REVIEW_CONTEXT_ONLY'
    assert result['concern_review']['status'] == 'retained_for_human_review'
    assert result['concern_review']['paper_required'] is False
    assert result['concern_review']['manual_route_reference'] == 'existing manual urgent concern route'
    assert result['concern_review']['delivery_claim'] is False
    assert result['proposal'] is None


def test_missing_paper_blocks_pack_readiness_but_keeps_concern_visible():
    concern = item(
        paper_id=None, paper_revision=None, has_paper=False, has_solution=False,
        is_concern=True, urgent=False, concern_text='Synthetic concern without a paper',
    )
    result = propose_transition(concern, state(), request('mark_ready'), policy())
    assert result['code'] == 'PAPER_REQUIRED_FOR_PACK_STATE'
    assert result['concern_review']['text'] == concern['concern_text']
    assert result['concern_review']['paper_required'] is False
    assert result['proposal'] is None


def test_return_for_change_preserves_dissent_and_prior_approval_history():
    ready = ready_state()
    ready['history'].append({'event': 'prior_review', 'request_id': 'OLD-REVIEW', 'reason': 'Synthetic earlier review'})
    source = item(dissent=['Synthetic dissent remains unresolved'])
    before_history = copy.deepcopy(ready['history'])
    result = propose_transition(source, ready, request('return_for_change', version=1, request_id='REQ-RETURN', reason='Clarify synthetic source'), policy())
    assert result['ok']
    assert result['proposal']['status'] == 'returned_for_change'
    assert result['proposal']['history'][:len(before_history)] == before_history
    assert result['retained_dissent'] == source['dissent']
    assert result['proposal']['history'][-1]['reason'] == 'Clarify synthetic source'
    assert result['substantive_decision_authority'] is False


def test_revocation_keeps_prior_approval_event_and_records_revocation():
    approved = approved_state()
    before = copy.deepcopy(approved['history'])
    result = propose_transition(item(), approved, request('revoke_approval', 'chair', 2, 'REQ-REVOKE'), policy())
    assert result['ok']
    assert result['proposal']['status'] == 'revoked'
    assert result['proposal']['history'][:len(before)] == before
    assert result['proposal']['history'][-1]['prior_approval_retained'] is True
    assert result['substantive_decision_authority'] is False


@pytest.mark.parametrize('change', ['wrong_policy_revision', 'duplicate_request', 'invalid_state_transition', 'missing_return_reason', 'bad_shape'])
def test_invalid_proposals_fail_closed_without_mutating_input(change):
    source = item()
    current = state()
    req = request('mark_ready')
    supplied_policy = policy()
    if change == 'wrong_policy_revision':
        supplied_policy['revision'] = 'policy-r2'
    elif change == 'duplicate_request':
        current['history'] = [{'request_id': req['request_id']}]
    elif change == 'invalid_state_transition':
        req['action'] = 'approve_for_pack'
        req['actor_role'] = 'chair'
    elif change == 'missing_return_reason':
        current['status'] = 'ready_for_review'
        current['binding'] = {key: source[key] for key in (
            'meeting_id', 'item_id', 'item_revision', 'paper_id', 'paper_revision', 'audience_revision', 'permission_revision')}
        req = request('return_for_change', version=0)
    else:
        source.pop('dissent')
    before = copy.deepcopy((source, current, req, supplied_policy))
    result = propose_transition(source, current, req, supplied_policy)
    assert not result['ok']
    assert (source, current, req, supplied_policy) == before


def test_results_are_proposals_without_storage_or_external_side_effects():
    result = propose_transition(item(), state(), request('mark_ready'), policy())
    assert result['ok']
    assert result['code'] == 'TRANSITION_PROPOSAL'
    assert result['external_write'] is False
    assert result['delivery_claim'] is False
    assert result['substantive_decision_authority'] is False


def test_validator_has_no_storage_network_or_microsoft_connector_imports():
    tree = ast.parse((ROOT / 'scripts/agenda_review_transitions.py').read_text(encoding='utf-8'))
    imported = {
        alias.name.split('.')[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module.split('.')[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported <= {'copy'}
