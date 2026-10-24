"""Actual register schema recovery contracts; no network or tenant mutation."""
from copy import deepcopy
import json

import pytest

from scripts.f09_isolated_writer import (
    REGISTER_FIELD_TYPES, REGISTER_RECOVERY_FIELDS,
    plan_action_register_recovery, reconcile_selective_recovery,
)


def config(field='Currentstatus'):
    row = {name: None for name in REGISTER_FIELD_TYPES}
    row.update(Id=5, GUID='00000000-0000-4000-8000-000000000108',
               Title='FICTIONAL register action', LegacyactionID='FICTIONAL-A31-01',
               Sourcereference='FICTIONAL-MINUTES#A31-01', Sourcehistory='Original history',
               Currentstatus='Unverified — not issued', Originalduelabel='As recorded',
               Duedate='2030-02-18T00:00:00Z', Reviewdate='2030-02-19T00:00:00Z',
               Recordedrole_x2014_unverified='Fictional source role — not assignment',
               **{'odata.etag': '"1"'})
    erroneous = dict(row, **{field: '2030-02-20T00:00:00Z'
                            if REGISTER_FIELD_TYPES[field] == 'DateTime' else 'Incorrect value',
                            'odata.etag': '"2"'})
    current = dict(erroneous, Sourcehistory='Original history | retained later note',
                   HumanNote='Independent edit', **{'odata.etag': '"3"'})
    return dict(baseline=row, erroneous=erroneous, current=current, field=field,
                site='https://example.invalid/technical',
                list_id='00000000-0000-0000-0000-000000000001',
                recovery_reference='FICTIONAL selected correction #1', schema={
                    'Id': '00000000-0000-0000-0000-000000000001',
                    'EnableVersioning': True, 'ListItemEntityTypeFullName': 'SP.Data.FixtureListItem',
                    'Fields': [{'InternalName': n, 'TypeAsString': t, 'ReadOnlyField': False}
                               for n, t in REGISTER_FIELD_TYPES.items()]})


@pytest.mark.parametrize('field', sorted(REGISTER_RECOVERY_FIELDS))
def test_exact_single_field_native_mapping_and_preserved_history(field):
    cfg = config(field); original = deepcopy(cfg)
    plan = plan_action_register_recovery(**cfg)
    assert cfg == original and plan['execution_authorized'] is False
    assert plan['state'] == 'RECOVERY_PLANNED'
    params = plan['request']['inputs']['parameters']
    assert params['parameters/headers']['IF-MATCH'] == '"3"'
    assert json.loads(params['parameters/body']) == {
        '__metadata': {'type': cfg['schema']['ListItemEntityTypeFullName']},
        field: cfg['baseline'][field]}
    assert plan['request']['inputs']['retryPolicy'] == {'type': 'none'}
    observed = dict(cfg['current'], **{field: cfg['baseline'][field], 'odata.etag': '"4"'})
    assert reconcile_selective_recovery(plan, observed) == 'RESTORED_READBACK'
    replay = plan_action_register_recovery(**(cfg | {'current': observed}))
    assert replay['state'] == 'ALREADY_RESTORED' and replay['request'] is None
    observed['HumanNote'] = 'Lost edit'
    assert reconcile_selective_recovery(plan, observed) == 'READBACK_DRIFT_REQUIRES_RECONCILIATION'


def test_independent_selected_field_change_refuses_write():
    cfg = config(); cfg['current']['Currentstatus'] = 'Independent later status'
    plan = plan_action_register_recovery(**cfg)
    assert plan['state'] == 'SELECTED_FIELD_CONFLICT' and plan['request'] is None


@pytest.mark.parametrize('field', sorted(set(REGISTER_FIELD_TYPES) - REGISTER_RECOVERY_FIELDS))
def test_identity_history_approval_and_closure_are_not_rollback_fields(field):
    cfg = config(); cfg['field'] = field
    with pytest.raises(ValueError): plan_action_register_recovery(**cfg)


@pytest.mark.parametrize('kind', ['field_missing', 'wrong_type', 'readonly', 'duplicate',
                                  'wrong_list', 'no_versions', 'missing_snapshot',
                                  'identity', 'source', 'history', 'wildcard', 'date'])
def test_drift_and_incomplete_snapshots_refused(kind):
    cfg = config()
    if kind == 'field_missing': cfg['schema']['Fields'].pop()
    if kind == 'wrong_type': cfg['schema']['Fields'][0]['TypeAsString'] = 'Note'
    if kind == 'readonly': cfg['schema']['Fields'][0]['ReadOnlyField'] = True
    if kind == 'duplicate': cfg['schema']['Fields'].append(cfg['schema']['Fields'][0])
    if kind == 'wrong_list': cfg['schema']['Id'] = 'other'
    if kind == 'no_versions': cfg['schema']['EnableVersioning'] = False
    if kind == 'missing_snapshot': del cfg['current']['Reviewdate']
    if kind == 'identity': cfg['current']['LegacyactionID'] = 'replacement'
    if kind == 'source': cfg['current']['Sourcereference'] = 'other'
    if kind == 'history': cfg['current']['Sourcehistory'] = 'History lost'
    if kind == 'wildcard': cfg['current']['odata.etag'] = '*'
    if kind == 'date': cfg['current']['Duedate'] = '2030-02-18'
    with pytest.raises(ValueError): plan_action_register_recovery(**cfg)


def test_uncertain_acknowledgement_never_implies_success_or_retry():
    cfg = config(); plan = plan_action_register_recovery(**cfg)
    assert reconcile_selective_recovery(plan, cfg['current']) == 'NOT_RESTORED_REPLAN_REQUIRED'


def test_explicit_native_collision_mapping_preserves_existing_technical_source():
    cfg = config()
    mapping = {k: k for k in REGISTER_FIELD_TYPES}
    mapping['Sourcereference'] = 'Sourcereference0'
    for row in (cfg['baseline'], cfg['erroneous'], cfg['current']):
        row['Sourcereference0'] = row.pop('Sourcereference')
        row['SourceReference'] = 'FICTIONAL original technical reference'
    next(f for f in cfg['schema']['Fields'] if f['InternalName'] == 'Sourcereference')['InternalName'] = 'Sourcereference0'
    with pytest.raises(ValueError): plan_action_register_recovery(**cfg)
    plan = plan_action_register_recovery(**cfg, field_map=mapping)
    assert plan['state'] == 'RECOVERY_PLANNED'
    assert plan['current']['SourceReference'] == 'FICTIONAL original technical reference'
    assert 'SourceReference' not in json.loads(plan['request']['inputs']['parameters']['parameters/body'])
