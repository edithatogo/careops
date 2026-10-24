"""Selected native register reference mapping; no live operations."""
from copy import deepcopy

import pytest

from scripts.f10_source_adapter import register_source_snapshot
from tests.test_f09_register_recovery import config as register_config


def config():
    cfg = register_config()
    row = dict(cfg['baseline'], OData__UIVersionString='1.0',
               Modified='2030-02-10T12:00:00Z')
    schema = cfg['schema'] | {'Description': 'Synthetic technical commissioning only.'}
    return dict(schema=schema, rows=[row], meeting={
        'meeting_id': 'FICTIONAL-MEETING-20300218', 'meeting_date': '2030-02-18',
        'revision': 'event-1', 'cancelled': False}, selection={
            'meeting_id': 'FICTIONAL-MEETING-20300218', 'meeting_date': '2030-02-18',
            'meeting_revision': 'event-1', 'source_id': schema['Id'],
            'source_revision': 'selection-1', 'synthetic_only': True,
            'rows': [{'Id': row['Id'], 'GUID': row['GUID'],
                      'OData__UIVersionString': '1.0', 'LegacyactionID': row['LegacyactionID']}]})


def test_exact_source_fields_dates_ids_history_and_unknown_holds_are_preserved():
    cfg = config(); original = deepcopy(cfg)
    result = register_source_snapshot(**cfg); row = result['records'][0]
    assert cfg == original and result['synthetic_only'] is True
    assert row['record_id'] == cfg['rows'][0]['LegacyactionID']
    assert row['native_guid'] == cfg['rows'][0]['GUID']
    assert row['status'] == 'unknown'
    assert row['commissioned_claim'] is False and row['issued_claim'] is False
    assert row['owner_claim'] is None
    assert row['history'] == [cfg['rows'][0]['Sourcehistory']]
    assert row['native_business_fields']['Currentstatus'] == 'Unverified — not issued'
    assert row['due_date'] == cfg['rows'][0]['Duedate']
    assert 'Originalduelabel: As recorded' in row['source_text']


def test_status_readiness_and_recorded_role_never_infer_business_authority():
    cfg = config(); cfg['rows'][0].update(Currentstatus='open',
        Issuereadiness='Ready to issue', Commissioningclassification='Commissioned')
    row = register_source_snapshot(**cfg)['records'][0]
    assert row['status'] == 'open' and row['commissioned_claim'] is False
    assert row['issued_claim'] is False and row['owner_claim'] is None


def test_explicit_review_is_version_pinned_and_retained_separately():
    cfg = config(); legacy = cfg['rows'][0]['LegacyactionID']
    cfg['reviews'] = {legacy: {'native_version': '1.0', 'evidence_ref': 'FICTIONAL-REVIEW#1',
        'commissioned_claim': True, 'issued_claim': True, 'closure_acceptance': False,
        'owner_claim': 'FICTIONAL owner claim'}}
    row = register_source_snapshot(**cfg)['records'][0]
    assert row['commissioned_claim'] and row['issued_claim']
    assert row['review_evidence_ref'] == 'FICTIONAL-REVIEW#1'
    cfg['reviews'][legacy]['native_version'] = '2.0'
    with pytest.raises(ValueError): register_source_snapshot(**cfg)


@pytest.mark.parametrize('problem', ['meeting', 'date', 'cancelled', 'revision', 'schema',
    'missing_field', 'duplicate', 'missing_row', 'unselected', 'legacy', 'native_version',
    'guid', 'real_as_fictional', 'source', 'modified'])
def test_changed_or_incomplete_native_selection_is_refused(problem):
    cfg = config()
    if problem == 'meeting': cfg['meeting']['meeting_id'] = 'OTHER'
    if problem == 'date': cfg['meeting']['meeting_date'] = '2030-02-19'
    if problem == 'cancelled': cfg['meeting']['cancelled'] = True
    if problem == 'revision': cfg['meeting']['revision'] = 'event-2'
    if problem == 'schema': cfg['schema']['Fields'][0]['TypeAsString'] = 'Note'
    if problem == 'missing_field': del cfg['rows'][0]['Reviewdate']
    if problem == 'duplicate': cfg['selection']['rows'] *= 2
    if problem == 'missing_row': cfg['rows'] = []
    if problem == 'unselected': cfg['rows'][0]['Id'] = 6
    if problem == 'legacy': cfg['rows'][0]['LegacyactionID'] = 'replacement'
    if problem == 'native_version': cfg['rows'][0]['OData__UIVersionString'] = '2.0'
    if problem == 'guid': cfg['rows'][0]['GUID'] = '00000000-0000-0000-0000-000000000099'
    if problem == 'real_as_fictional': cfg['schema']['Description'] = 'Real register'
    if problem == 'source': cfg['schema']['Id'] = 'OTHER'
    if problem == 'modified': cfg['rows'][0]['Modified'] = '2030-02-10'
    with pytest.raises(ValueError): register_source_snapshot(**cfg)


def test_explicit_native_source_name_alias_preserves_both_source_fields():
    cfg = config(); mapping = {f['InternalName']: f['InternalName'] for f in cfg['schema']['Fields']}
    mapping['Sourcereference'] = 'Sourcereference0'; cfg['field_map'] = mapping
    for field in cfg['schema']['Fields']:
        if field['InternalName'] == 'Sourcereference': field['InternalName'] = 'Sourcereference0'
    cfg['rows'][0]['Sourcereference0'] = cfg['rows'][0].pop('Sourcereference')
    cfg['rows'][0]['SourceReference'] = 'FICTIONAL original technical source'
    result = register_source_snapshot(**cfg)
    assert result['records'][0]['native_business_fields']['Sourcereference'] == 'FICTIONAL-MINUTES#A31-01'
    assert cfg['rows'][0]['SourceReference'] == 'FICTIONAL original technical source'
