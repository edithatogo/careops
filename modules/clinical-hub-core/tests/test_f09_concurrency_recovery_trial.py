"""Graph/guard checks for the bounded two-row F09 native trial preparation."""
from copy import deepcopy
import hashlib
import json

import pytest

from scripts.f09_isolated_writer import FIELDS, build_concurrency_recovery_trial


def baseline():
    return {'name': 'fictional-same-flow', 'properties': {'state': 'Stopped', 'isManaged': False,
        'connectionReferences': {}, 'owner': {'id': 'PRESERVE'}, 'definition': {
            'parameters': {}, 'triggers': {'manual': {'type': 'Request', 'kind': 'Button', 'inputs': {'schema': {}}}},
            'actions': {
                'Fixed_Fictional_Cases': {'type': 'Compose', 'runAfter': {}, 'inputs': []},
                'Initialize_Date_Results': {'type': 'InitializeVariable', 'runAfter': {}, 'inputs': {'variables': []}},
                'Validate_Case_Dates': {'type': 'Foreach', 'runAfter': {}, 'actions': {}},
                'Evaluate_Claims': {'type': 'Select', 'runAfter': {}, 'inputs': {}},
                'Outcome_Previews': {'type': 'Select', 'runAfter': {}, 'inputs': {}},
            }}}}


def pin(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def config():
    return dict(site='https://example.invalid/technical', list_id='00000000-0000-0000-0000-000000000001',
                description='Synthetic technical commissioning only. F09 CR fixture.',
                entity_type='SP.Data.FixtureListItem', reference='existing_invoker', rows=[
                    {'id': i, 'before': dict(zip(FIELDS, [f'FICTIONAL F09 CR row {i}', f'F09-CR-{i}',
                        f'FICTIONAL-F09-CR#row{i}', 'FICTIONAL-BASE', 'FICTIONAL-REVIEW',
                        'FICTIONAL baseline wording', 'FICTIONAL baseline history']))} for i in (5, 6)])


def build(**overrides):
    b = baseline()
    return build_concurrency_recovery_trial(b, expected_baseline_sha256=pin(b), **(config() | overrides))


def actions(graph):
    found = {}
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == 'actions' and isinstance(child, dict):
                    for name, action in child.items():
                        assert name not in found, name
                        found[name] = action
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(graph)
    return found


def test_complete_candidate_preserves_baseline_owner_legacy_and_invoker():
    b = baseline(); original = deepcopy(b); cfg = config(); before = deepcopy(cfg)
    result = build_concurrency_recovery_trial(b, expected_baseline_sha256=pin(b), **cfg)
    assert b == original and cfg == before
    candidate = result['candidate']; a = actions(candidate)
    assert candidate['name'] == b['name']
    assert candidate['properties']['state'] == 'Stopped'
    assert candidate['properties']['owner'] == b['properties']['owner']
    assert a['Outcome_Previews'] == b['properties']['definition']['actions']['Outcome_Previews']
    assert candidate['properties']['connectionReferences']['shared_sharepointonline'] == {
        'runtimeSource': 'invoker', 'connection': {'connectionReferenceLogicalName': 'existing_invoker'},
        'api': {'name': 'shared_sharepointonline'}}
    assert result['review']['native_deployment_ready'] is False
    assert 'not network timeout' in result['review']['uncertainty_model']


def test_race_is_two_distinct_parallel_merges_with_same_fresh_etag_and_no_retry():
    a = actions(build()['candidate'])
    left, right = a['Race_A'], a['Race_B']
    assert left['runAfter'] == right['runAfter'] == {}
    lp, rp = [v['inputs']['parameters'] for v in (left, right)]
    assert lp['parameters/headers']['IF-MATCH'] == rp['parameters/headers']['IF-MATCH'] == "@body('Read_first')?['odata.etag']"
    assert lp['parameters/body'] != rp['parameters/body']
    for p in (lp, rp):
        assert set(json.loads(p['parameters/body'])) == {
            '__metadata', 'SourceRevision', 'AuthorityReference', 'ReviewedWording', 'HistoryText'}
        assert p['parameters/headers']['X-HTTP-Method'] == 'MERGE'
    assert set(a['Race_status_guard']['runAfter']) == {'Race_A', 'Race_B'}
    assert a['Race_status_guard']['expression'].count('204') == 2
    assert a['Race_status_guard']['expression'].count('412') == 2
    assert 'Read_race_winner' in a and 'Race_winner_guard' in a
    assert 'overlapping native action intervals' in build()['review']['race_proof_required']


def test_uncertainty_and_partial_failure_are_explicit_not_retried_or_marked_complete():
    a = actions(build()['candidate'])
    for name, predecessor in [('Unknown_ack_fault', 'Unknown_state'),
                              ('Partial_stop_before_second', 'Partial_first_merge')]:
        assert a[name]['inputs']['runStatus'] == 'Failed'
        assert a[name]['runAfter'] == {predecessor: ['Succeeded']}
    assert 'SIMULATED_ACK_LOSS' in a['Unknown_ack_fault']['inputs']['runError']['code']
    assert a['Unknown_state']['inputs']['state'] == 'UNKNOWN'
    assert a['Unknown_state']['runAfter'] == {'Unknown_merge': ['Succeeded']}
    cases = a['CR_case']['cases']
    for name in ('race_reconcile', 'uncertain_reconcile', 'partial_reconcile'):
        assert not any(v['inputs']['parameters']['parameters/method'] != 'GET'
                       for v in actions(cases[name]).values() if v.get('type') == 'OpenApiConnection')
    partial = actions(cases['partial_save'])
    assert [n for n, v in partial.items() if v.get('type') == 'OpenApiConnection'] == ['Partial_first_merge']
    resume = actions(cases['partial_resume'])
    writes = [v for v in resume.values() if v.get('type') == 'OpenApiConnection'
              and v['inputs']['parameters']['parameters/method'] == 'POST']
    assert len(writes) == 1 and '/items(6)' in writes[0]['inputs']['parameters']['parameters/uri']
    assert 'Resume_readonly_complete' in resume
    assert 'First' not in str(writes[0]['inputs']['parameters']['parameters/headers'])


def test_all_http_calls_fixed_two_rows_guarded_no_notifications_and_all_history_preserved():
    out = build(); a = actions(out['candidate'])
    for action in a.values():
        if action.get('type') != 'OpenApiConnection':
            continue
        assert action['inputs']['host']['operationId'] == 'HttpRequest'
        assert action['inputs']['retryPolicy'] == {'type': 'none'}
        p = action['inputs']['parameters']; uri = p['parameters/uri']
        assert all('/items(' + str(i) + ')' not in uri for i in range(1, 5))
        if p['parameters/method'] == 'POST':
            assert p['parameters/headers']['IF-MATCH'] in (
                "@body('Read_first')?['odata.etag']", "@body('Read_second')?['odata.etag']")
    states = out['review']['states']; first, second = out['review']['before']
    for name, state in states.items():
        before = second if name == 'second_after' else first
        for key in ('Title', 'OperationKey', 'SourceReference'):
            assert state[key] == before[key]
        assert state['HistoryText'].startswith(before['HistoryText'] + ' | ')
        assert all(len(v) <= 255 for v in state.values())
    assert set(a['CR_case']['cases']) == {'race', 'race_reconcile', 'uncertain_save',
        'uncertain_reconcile', 'partial_save', 'partial_reconcile', 'partial_resume'}
    assert set(a['Resume_second_guard']['runAfter']) == {'Read_resume_first'}
    assert 'Read_resume_first' in a['Resume_second_guard']['expression']
    assert 'Read_resume_second' in a['Resume_second_guard']['expression']


def test_pinned_dataverse_source_preserves_clientdata_shape_and_native_identity_evidence():
    original = baseline()
    clientdata = {'properties': {k: v for k, v in original['properties'].items()
                                if k in ('definition', 'connectionReferences')}, 'schemaVersion': '1.0'}
    record = dict(clientdata=json.dumps(clientdata), workflowid='00000000-0000-4000-8000-000000000101',
                  statecode=0, statuscode=1, ismanaged=False, _ownerid_value='original-owner', name='F09 canonical')
    before = deepcopy(record)
    out = build_concurrency_recovery_trial(record, expected_baseline_sha256=pin(record), **config())
    assert record == before
    assert set(out['candidate']['properties']) == {'definition', 'connectionReferences'}
    assert out['review']['baseline_identity']['_ownerid_value'] == 'original-owner'
    assert out['review']['baseline_identity']['name'] == 'F09 canonical'
    record['workflowid'] = '00000000-0000-0000-0000-000000000099'
    with pytest.raises(ValueError):
        build_concurrency_recovery_trial(record, expected_baseline_sha256=pin(record), **config())


@pytest.mark.parametrize('change', ['pin', 'active', 'managed', 'duplicate', 'old_id', 'bool_id',
                                  'real_title', 'opkey', 'source', 'history_length', 'partial_fields',
                                  'site_query', 'entity', 'description'])
def test_unqualified_or_drifted_inputs_refused(change):
    b = baseline(); cfg = config(); expected = pin(b)
    if change == 'pin': expected = '0' * 64
    if change == 'active': b['properties']['state'] = 'Started'; expected = pin(b)
    if change == 'managed': b['properties']['isManaged'] = True; expected = pin(b)
    if change == 'duplicate': cfg['rows'][1]['id'] = 5
    if change == 'old_id': cfg['rows'][0]['id'] = 4
    if change == 'bool_id': cfg['rows'][0]['id'] = True
    if change == 'real_title': cfg['rows'][0]['before']['Title'] = 'Real action'
    if change == 'opkey': cfg['rows'][0]['before']['OperationKey'] = 'LIVE-1'
    if change == 'source': cfg['rows'][0]['before']['SourceReference'] = 'approved-real-minutes'
    if change == 'history_length': cfg['rows'][0]['before']['HistoryText'] = 'FICTIONAL' + 'x' * 240
    if change == 'partial_fields': del cfg['rows'][0]['before']['HistoryText']
    if change == 'site_query': cfg['site'] += '?wrong=1'
    if change == 'entity': cfg['entity_type'] = 'Guessed'
    if change == 'description': cfg['description'] = 'Real work register'
    with pytest.raises(ValueError):
        build_concurrency_recovery_trial(b, expected_baseline_sha256=expected, **cfg)
