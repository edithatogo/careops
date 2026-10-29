"""Source-only profile selection; all identities and authority assertions fictional."""
import ast
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import pytest
from scripts.forum_configuration import resolve
from scripts.f12_configuration import validate_configuration
from scripts.preparation_cycle import validate
FIXTURE = Path(__file__).parent / 'fixtures/forum_profiles/two_forums.json'

def sample():
    x = json.loads(FIXTURE.read_text())
    return (x['profiles'], x['selections'])

def check(profiles, selection, observed=None):
    return resolve(profiles, selection, observed_sources={'state': 'complete', 'sources': deepcopy(selection['sources'])} if observed is None else observed)

def test_two_same_name_forums_resolve_separately_and_do_not_authorise():
    profiles, selections = sample()
    before = deepcopy((profiles, selections))
    a, b = [check(profiles, s) for s in selections]
    assert a['state'] == b['state'] == 'review_only'
    assert a['preparation_control_keys'] == ('papers', 'review')
    assert b['preparation_control_keys'] == ('returns', 'risks')
    assert a['references']['destination_ref'] != b['references']['destination_ref']
    for r in [a, b]:
        assert r['native_authority'] is False and r['write_proposed'] is False
        assert r['governance_state'] == 'unverified'
        assert r['blockers'] == []
        assert isinstance(r['snapshot_json'], str)
        assert hashlib.sha256(r['snapshot_json'].encode()).hexdigest() == r['snapshot_sha256']
    assert (profiles, selections) == before
    a['references']['destination_ref'] = 'CHANGED-LOCAL-RESULT'
    assert check(profiles, selections[0])['references']['destination_ref'] == 'FICTIONAL-DESTINATION-A'

def test_existing_preparation_input_shape_works_without_new_control_schema():
    profiles, selections = sample()
    r = check(profiles, selections[0])
    keys = r['preparation_control_keys']
    data = dict(cycle='FICTIONAL-CYCLE', meeting='FICTIONAL-OCCURRENCE-A', priorities='To confirm', pack='FICTIONAL-PACK', register='FICTIONAL-REGISTER-A', previous_cycle=None, controls={k: dict(state='Not started', note='To confirm', source='FICTIONAL-SOURCE') for k in keys})
    assert validate(data, control_keys=keys) == data

def test_f12_selection_still_satisfies_existing_strict_validator():
    profiles, selections = sample()
    s = selections[0]
    r = check(profiles, s)
    e = dict(id=s['event']['event_ref'], originalStart=s['start'], seriesMasterId='FICTIONAL-SERIES-A', iCalUId='FICTIONAL-ICAL-A', subject=s['event']['subject'], type='occurrence', organizer={'emailAddress': {'address': s['event']['organizer']}}, start={'dateTime': '2030-02-04T06:00:00Z', 'timeZone': 'UTC'}, end={'dateTime': '2030-02-04T07:00:00Z', 'timeZone': 'UTC'}, changeKey='FICTIONAL-CHANGE-A', lastModifiedDateTime='2030-02-01T00:00:00Z', isCancelled=False)
    baseline = dict(event=e, agenda={'id': 'FICTIONAL-AGENDA-A', 'name': s['sources'][0]['name'], 'size': 1, 'lastModifiedDateTime': '2030-02-01T00:00:00Z', 'contentType': 'application/docx', '@odata.type': '#fixture.attachment', 'isInline': False}, checked_at='2030-02-01T00:00:00Z', baseline_run_id='FICTIONAL-RUN')
    assert validate_configuration(json.dumps(baseline), r['f12_selection_json'])['status'] == 'PASS'

@pytest.mark.parametrize('edit,code', [(lambda p, s: p.append(deepcopy(p[0])), 'DUPLICATE_PROFILE'), (lambda p, s: s.update(forum_ref='UNKNOWN'), 'UNKNOWN_FORUM'), (lambda p, s: s.update(profile_revision='stale'), 'UNKNOWN_PROFILE_REVISION'), (lambda p, s: p[0].update(effective_until='2030-02-04T16:00:00+10:00'), 'PROFILE_NOT_EFFECTIVE'), (lambda p, s: s.update(approved=True), 'INVALID_SELECTION'), (lambda p, s: p[0].update(approved=True), 'INVALID_PROFILE'), (lambda p, s: s.update(capabilities=['issue']), 'CAPABILITY_NOT_ALLOWED'), (lambda p, s: p[0].update(capabilities=['send']), 'INVALID_PROFILE'), (lambda p, s: s['event'].update(cancelled=True), 'CANCELLED_OCCURRENCE'), (lambda p, s: s['event'].update(series_ref=None), 'INVALID_SELECTION'), (lambda p, s: s['event'].update(original_start=None), 'INVALID_SELECTION'), (lambda p, s: s.update(window_start='2030-02-05T00:00:00+10:00'), 'INVALID_SELECTION'), (lambda p, s: s.update(start='2030-02-04T16:00:00'), 'INVALID_SELECTION'), (lambda p, s: p[0]['governance'].update(state='approved'), 'INVALID_PROFILE'), (lambda p, s: p[0]['governance'].update(state='recorded', source_ref=None), 'INVALID_PROFILE'), (lambda p, s: p[0].update(control_keys=['one', 'one']), 'INVALID_PROFILE'), (lambda p, s: p[0].update(schema_version=True), 'INVALID_PROFILE'), (lambda p, s: s['sources'].append(deepcopy(s['sources'][0])), 'INVALID_SELECTION')])
def test_invalid_or_unqualified_inputs_never_return_adapters(edit, code):
    profiles, selections = sample()
    s = selections[0]
    edit(profiles, s)
    r = check(profiles, s)
    assert code in r['blockers'] and r['state'] == 'blocked'
    assert r['native_authority'] is False and r['write_proposed'] is False
    assert r['f12_selection'] is None and r['snapshot_json'] is None

def test_effective_revisions_have_exclusive_intervals_and_never_pick_latest():
    profiles, selections = sample()
    s = selections[0]
    future = deepcopy(profiles[0])
    future.update(profile_revision='r2', effective_from='2030-03-01T00:00:00+10:00')
    profiles.append(future)
    assert 'OVERLAPPING_PROFILE_INTERVALS' in check(profiles, s)['blockers']
    profiles[0]['effective_until'] = future['effective_from']
    assert check(profiles, s)['state'] == 'review_only'
    s['profile_revision'] = 'r2'
    assert 'PROFILE_NOT_EFFECTIVE' in check(profiles, s)['blockers']
    s.update(start='2030-03-01T00:00:00+10:00', end='2030-03-01T01:00:00+10:00', window_start='2030-03-01T00:00:00+10:00', window_end='2030-03-02T00:00:00+10:00')
    assert check(profiles, s)['state'] == 'review_only'

@pytest.mark.parametrize('change', ['revision', 'sha256', 'name', 'missing', 'duplicate', 'incomplete', 'wrong-forum-source'])
def test_source_drift_or_incomplete_observation_is_not_fresh_proof(change):
    profiles, selections = sample()
    s = selections[0]
    obs = {'state': 'complete', 'sources': deepcopy(s['sources'])}
    if change in {'revision', 'sha256', 'name'}:
        obs['sources'][0][change] = 'changed'
    if change == 'missing':
        obs['sources'] = []
    if change == 'duplicate':
        obs['sources'] *= 2
    if change == 'incomplete':
        obs['state'] = 'incomplete'
    if change == 'wrong-forum-source':
        obs['sources'] = selections[1]['sources']
    assert check(profiles, s, obs)['state'] == 'blocked'

def test_recorded_governance_and_role_claims_still_cannot_grant_native_authority():
    profiles, selections = sample()
    p = profiles[0]
    p['governance'] = {'state': 'recorded', 'source_ref': 'FICTIONAL-AUTHORITY-NOT-A-REAL-GRANT'}
    for r in p['roles'].values():
        r.update(state='recorded', source_ref='FICTIONAL-ROLE-RECORD')
    result = check(profiles, selections[0])
    assert result['state'] == 'review_only' and result['native_authority'] is False
    snap = json.loads(result['snapshot_json'])
    assert snap['profile']['roles']['chair']['role_ref'] != snap['selection']['event']['organizer']

def test_exception_lineage_and_requested_capability_subset_are_preserved():
    profiles, selections = sample()
    s = selections[0]
    s['event'].update(type='exception', original_start='2030-01-28T16:00:00+10:00')
    s['capabilities'] = ['prepare']
    r = check(profiles, s)
    assert r['state'] == 'review_only' and r['f12_selection'] is None
    assert json.loads(r['snapshot_json'])['selection']['event']['original_start'] == s['event']['original_start']
    s['event'].update(type='singleInstance', original_start=None, series_ref=None)
    assert check(profiles, s)['state'] == 'review_only'

def test_same_inputs_are_deterministic_and_parallel_forums_have_no_shared_state():
    profiles, selections = sample()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda s: check(profiles, s), selections * 8))
    assert len({x['snapshot_sha256'] for x in results[::2]}) == 1
    assert results[0]['snapshot_sha256'] != results[1]['snapshot_sha256']
    original = results[0]['snapshot_sha256']
    selections[0]['snapshot_revision'] = 's2'
    assert check(profiles, selections[0])['snapshot_sha256'] != original

@pytest.mark.parametrize('profiles,selection,observed', [(None, {}, {}), ([], {}, {}), ([None], {}, {}), ([], None, {}), ([], {}, None)])
def test_malformed_input_is_blocked(profiles, selection, observed):
    assert resolve(profiles, selection, observed_sources=observed)['state'] == 'blocked'

def test_module_has_no_io_authentication_or_persistence_imports():
    source = Path(__file__).parents[1] / 'scripts/forum_configuration.py'
    tree = ast.parse(source.read_text())
    imports = {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
    imports |= {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert imports <= {'copy', 'datetime', 'hashlib', 'json', 're', 'scripts'}
    assert {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module.startswith('scripts.')} == {'scripts.f12_configuration'}

@pytest.mark.parametrize('state', ['unverified', 'draft', 'conflicting', 'recorded'])
def test_each_evidence_state_is_review_only_not_approval(state):
    profiles, selections = sample()
    profiles[0]['governance'] = {'state': state, 'source_ref': 'FICTIONAL-SOURCE' if state == 'recorded' else None}
    r = check(profiles, selections[0])
    assert r['state'] == 'review_only' and r['governance_state'] == state
    assert r['native_authority'] is False and r['write_proposed'] is False

@pytest.mark.parametrize('mode', ['missing', 'multiple'])
def test_calendar_selection_requires_one_selected_agenda(mode):
    profiles, selections = sample()
    s = selections[0]
    if mode == 'missing':
        s['sources'][0]['kind'] = 'minutes'
    else:
        other = deepcopy(s['sources'][0])
        other['source_ref'] = 'FICTIONAL-SECOND-AGENDA'
        s['sources'].append(other)
    assert check(profiles, s)['blockers'] == ['AMBIGUOUS_AGENDA_SOURCE']

def test_disabled_profile_capability_and_selection_field_injection_are_blocked():
    profiles, selections = sample()
    s = selections[0]
    profiles[0]['capabilities'] = ['prepare']
    assert check(profiles, s)['blockers'] == ['CAPABILITY_NOT_ALLOWED']
    s['capabilities'] = ['prepare']
    s['destination_ref'] = 'FICTIONAL-DESTINATION-B'
    assert check(profiles, s)['blockers'] == ['INVALID_SELECTION']

def test_missing_explicit_snapshot_identity_is_not_reconstructed_from_title():
    profiles, selections = sample()
    s = selections[0]
    del s['occurrence_ref']
    assert check(profiles, s)['blockers'] == ['INVALID_SELECTION']

def test_profile_order_and_observation_order_cannot_select_another_profile():
    profiles, selections = sample()
    s = selections[0]
    source = deepcopy(s['sources'][0])
    source.update(source_ref='FICTIONAL-PAPER', kind='governance')
    s['sources'].append(source)
    expected = check(profiles, s)
    actual = check(list(reversed(profiles)), s, {'state': 'complete', 'sources': list(reversed(s['sources']))})
    assert actual == expected

def test_strict_shape_handles_arbitrary_nested_json_without_io_or_exception():
    from hypothesis import given, settings, strategies as st
    scalar = st.none() | st.booleans() | st.integers() | st.text(max_size=20)
    value = st.recursive(scalar, lambda child: st.lists(child, max_size=4) | st.dictionaries(st.text(max_size=12), child, max_size=4), max_leaves=12)

    @settings(max_examples=100, deadline=None)
    @given(value, value, value)
    def exercise(profiles, selection, observed):
        r = resolve(profiles, selection, observed_sources=observed)
        assert r['state'] == 'blocked' and (not r['native_authority'])
    exercise()

def test_f12_output_respects_existing_actual_utf16_limit():
    profiles, selections = sample()
    s = selections[0]
    s['event']['subject'] = 'x' * 1500
    s['sources'][0]['name'] = 'y' * 1500
    assert check(profiles, s)['blockers'] == ['F12_SELECTION_LIMIT']
    s['event']['subject'] = 'Fictional Unicode ' + chr(128512) * 300
    s['sources'][0]['name'] = 'Fictional agenda.docx'
    result = check(profiles, s)
    assert result['state'] == 'review_only'
    assert len(result['f12_selection_json'].encode('utf-16-le')) // 2 <= 2000
    assert json.loads(result['f12_selection_json']) == result['f12_selection']

def test_lone_surrogate_source_text_blocks_instead_of_crashing_canonical_snapshot():
    profiles, selections = sample()
    s = selections[0]
    s['event']['subject'] = 'bad' + chr(55296)
    assert check(profiles, s)['blockers'] == ['INVALID_SELECTION']
    s = sample()[1][0]
    profiles[0]['display_name'] = 'bad' + chr(57343)
    assert check(profiles, s)['blockers'] == ['INVALID_PROFILE']
