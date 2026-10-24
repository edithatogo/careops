"""Local selective recovery contracts; no tenant operations."""
from copy import deepcopy
import json

import pytest

from scripts.f09_isolated_writer import plan_selective_recovery, reconcile_selective_recovery


def inputs():
    baseline = dict(Id=5, Title='FICTIONAL F09 CR row 5', OperationKey='F09-CR-5',
                    SourceReference='FICTIONAL-F09-CR#row5', SourceRevision='FICTIONAL-BASE',
                    AuthorityReference='FICTIONAL-TECHNICAL', ReviewedWording='FICTIONAL baseline',
                    HistoryText='FICTIONAL history', **{'odata.etag': '"1"'})
    erroneous = dict(baseline, SourceRevision='FICTIONAL-ERROR',
                     HistoryText=baseline['HistoryText'] + ' | error', **{'odata.etag': '"2"'})
    current = dict(erroneous, ReviewedWording="FICTIONAL human's retained edit",
                   HistoryText=erroneous['HistoryText'] + ' | human edit', **{'odata.etag': '"3"'})
    return dict(baseline=baseline, erroneous=erroneous, current=current, field='SourceRevision',
                site='https://example.invalid/technical',
                list_id='00000000-0000-0000-0000-000000000001',
                description='Synthetic technical commissioning only.', entity_type='SP.Data.FixtureListItem')


def test_one_field_merge_uses_current_etag_and_preserves_inputs_and_history():
    cfg = inputs(); original = deepcopy(cfg)
    plan = plan_selective_recovery(**cfg)
    assert cfg == original
    assert plan['state'] == 'RECOVERY_PLANNED'
    request = plan['request']; p = request['inputs']['parameters']
    assert p['parameters/method'] == 'POST' and p['parameters/uri'].endswith('/items(5)')
    assert p['parameters/headers']['IF-MATCH'] == '"3"'
    assert p['parameters/headers']['X-HTTP-Method'] == 'MERGE'
    assert json.loads(p['parameters/body']) == {'__metadata': {'type': cfg['entity_type']},
                                              'SourceRevision': 'FICTIONAL-BASE'}
    assert request['inputs']['retryPolicy'] == {'type': 'none'}
    restored = dict(cfg['current'], SourceRevision='FICTIONAL-BASE', **{'odata.etag': '"4"'})
    assert reconcile_selective_recovery(plan, restored) == 'RESTORED_READBACK'
    assert restored['HistoryText'] == cfg['current']['HistoryText']
    plan['current']['Title'] = 'changed locally'
    assert cfg == original


@pytest.mark.parametrize('field', ['SourceRevision', 'ReviewedWording'])
def test_allowlisted_fields_restore_and_replay_without_write(field):
    cfg = inputs(); cfg['field'] = field
    cfg['erroneous'][field] = 'FICTIONAL incorrect'
    cfg['current'][field] = 'FICTIONAL incorrect'
    plan = plan_selective_recovery(**cfg)
    assert plan['state'] == 'RECOVERY_PLANNED'
    cfg['current'][field] = cfg['baseline'][field]
    replay = plan_selective_recovery(**cfg)
    assert replay['state'] == 'ALREADY_RESTORED' and replay['request'] is None
    assert reconcile_selective_recovery(replay, cfg['current']) == 'RESTORED_READBACK'


def test_independent_selected_edit_refused():
    cfg = inputs(); cfg['current']['SourceRevision'] = 'FICTIONAL independent revision'
    plan = plan_selective_recovery(**cfg)
    assert plan['state'] == 'SELECTED_FIELD_CONFLICT' and plan['request'] is None
    assert reconcile_selective_recovery(plan, cfg['current']) == 'RECOVERY_REFUSED'


def test_native_modified_and_version_change_but_custom_human_field_is_preserved():
    cfg = inputs()
    cfg['current'].update(Modified='2031-03-08T10:00:00Z',
                          OData__UIVersionString='3.0', EditorId=7,
                          HumanNote='Existing independent human edit')
    plan = plan_selective_recovery(**cfg)
    observed = dict(cfg['current'], SourceRevision=cfg['baseline']['SourceRevision'],
                    Modified='2031-03-08T10:01:00Z', OData__UIVersionString='4.0',
                    EditorId=8, **{'odata.etag': '"4"'})
    assert reconcile_selective_recovery(plan, observed) == 'RESTORED_READBACK'
    observed['HumanNote'] = 'Unexpected loss or change'
    assert reconcile_selective_recovery(plan, observed) == 'READBACK_DRIFT_REQUIRES_RECONCILIATION'


def test_single_item_metadata_omitted_by_collection_projection_is_not_content_loss():
    cfg = inputs()
    cfg['current']['odata.metadata'] = 'Native single-item projection annotation'
    plan = plan_selective_recovery(**cfg)
    observed = dict(cfg['current'], SourceRevision=cfg['baseline']['SourceRevision'],
                    **{'odata.etag': '"4"'})
    del observed['odata.metadata']
    assert reconcile_selective_recovery(plan, observed) == 'RESTORED_READBACK'
    del observed['HistoryText']
    assert reconcile_selective_recovery(plan, observed) == 'READBACK_DRIFT_REQUIRES_RECONCILIATION'


@pytest.mark.parametrize('key,value', [('Id', 6), ('Id', True), ('OperationKey', 'F09-CR-other'),
                                      ('SourceReference', 'FICTIONAL-F09-CR#other'),
                                      ('Title', 'FICTIONAL F09 CR other')])
@pytest.mark.parametrize('snapshot', ['erroneous', 'current'])
def test_identity_drift_refused(snapshot, key, value):
    cfg = inputs(); cfg[snapshot][key] = value
    with pytest.raises(ValueError): plan_selective_recovery(**cfg)


@pytest.mark.parametrize('etag', ['', '*', ' * ', '"3"\r\nInjected', None, ' "3"'])
@pytest.mark.parametrize('snapshot', ['baseline', 'erroneous', 'current'])
def test_missing_or_unsafe_snapshot_etag_refused(snapshot, etag):
    cfg = inputs(); cfg[snapshot]['odata.etag'] = etag
    with pytest.raises(ValueError): plan_selective_recovery(**cfg)


@pytest.mark.parametrize('field', ['Title', 'Id', 'HistoryText', 'AuthorityReference', 'Status', 'OperationKey'])
def test_authority_history_identity_and_business_fields_excluded(field):
    cfg = inputs(); cfg['field'] = field
    with pytest.raises(ValueError): plan_selective_recovery(**cfg)


@pytest.mark.parametrize('change', ['missing', 'real', 'history', 'no_error', 'target'])
def test_unqualified_snapshots_refused(change):
    cfg = inputs()
    if change == 'missing': del cfg['baseline']['ReviewedWording']
    if change == 'real': cfg['current']['ReviewedWording'] = 'real business wording'
    if change == 'history': cfg['current']['HistoryText'] = 'FICTIONAL replaced history'
    if change == 'no_error': cfg['erroneous']['SourceRevision'] = cfg['baseline']['SourceRevision']
    if change == 'target': cfg['description'] = 'Live register'
    with pytest.raises(ValueError): plan_selective_recovery(**cfg)


def test_uncertain_save_and_conflict_readback_never_automatically_retry():
    cfg = inputs(); plan = plan_selective_recovery(**cfg)
    assert reconcile_selective_recovery(plan, cfg['current']) == 'NOT_RESTORED_REPLAN_REQUIRED'
    changed = dict(cfg['current'], SourceRevision='FICTIONAL independent')
    assert reconcile_selective_recovery(plan, changed) == 'SELECTED_FIELD_CONFLICT'
    for field, value in [('HistoryText', 'FICTIONAL lost history'), ('Id', True),
                         ('ReviewedWording', 'FICTIONAL later edit'), ('odata.etag', '*')]:
        observed = dict(cfg['current'], **{field: value})
        assert reconcile_selective_recovery(plan, observed) == 'READBACK_DRIFT_REQUIRES_RECONCILIATION'
    unchanged_etag = dict(cfg['current'], SourceRevision=cfg['baseline']['SourceRevision'])
    assert reconcile_selective_recovery(plan, unchanged_etag) == 'READBACK_DRIFT_REQUIRES_RECONCILIATION'


def test_fresh_replan_after_concurrent_unrelated_edit_preserves_new_human_state():
    cfg = inputs(); old_plan = plan_selective_recovery(**cfg)
    fresh = dict(cfg['current'], ReviewedWording='FICTIONAL newest human wording',
                 HistoryText=cfg['current']['HistoryText'] + ' | later', **{'odata.etag': '"9"'})
    assert reconcile_selective_recovery(old_plan, fresh) == 'READBACK_DRIFT_REQUIRES_RECONCILIATION'
    cfg['current'] = fresh
    new_plan = plan_selective_recovery(**cfg)
    params = new_plan['request']['inputs']['parameters']
    assert params['parameters/headers']['IF-MATCH'] == '"9"'
    restored = dict(fresh, SourceRevision=cfg['baseline']['SourceRevision'], **{'odata.etag': '"10"'})
    assert reconcile_selective_recovery(new_plan, restored) == 'RESTORED_READBACK'
    assert restored['HistoryText'].endswith(' | later')
    assert restored['ReviewedWording'] == 'FICTIONAL newest human wording'
