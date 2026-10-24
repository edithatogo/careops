from copy import deepcopy
import pytest
from scripts.ddms_reviewed_contribution import *

def fixture():
 e={'Id':101,'GUID':'11111111-1111-4111-8111-111111111111','OData__UIVersionString':'1.0','received':'2026-01-01T00:00:00Z','clinical_narrative':'DO NOT COPY'}
 a={'GUID':'22222222-2222-4222-8222-222222222222','odata.etag':'"1"','OData__UIVersionString':'1.0','Ryan_x0020_call_x0020__x002d__x0Id':101,PERFORMER_REFERENCE_FIELD:'worker:opaque-123',WORK[0]:'2025-12-31T14:00:00Z',WORK[1]:'2026-01-01T13:30:00Z',WORK[2]:'2026-01-01T14:30:00Z',**dict.fromkeys(FLAGS,False),'Coordination_x0020_note_x0020__x':'Human edited note','AVAC_x0020_status':'Not entered'}
 return e,a

def prepare(e,a,**kwargs):
 args=dict(event_version='1.0',target_etag='"1"',actual_work_confirmed=True,flags_confirmed=True,worker_confirmed=True,performer_reference='worker:opaque-123');args.update(kwargs)
 return prepare_review(e,a,**args)

def test_review_is_narrow_and_replay_reconciles_without_erasing_work_or_human_edits():
 e,a=fixture();p=prepare(e,a);assert p['action']=='review'
 assert set(p['patch']) == {CONTRIBUTION_FIELD, EVENT_FIELD, EPISODE_FIELD,
                            SOURCE_FIELD, MAPPING_FIELD, REVIEW_FIELD,
                            REVIEW_TARGET_VERSION_FIELD}
 assert p['patch'][REVIEW_TARGET_VERSION_FIELD]=='2.0'
 assert p['expected_post_version']=='2.0'
 assert not set(p['patch']) & set(WORK+FLAGS+('clinical_narrative','Coordination_x0020_note_x0020__x','AVAC_x0020_status'))
 b={**a,**p['patch'],'odata.etag':'"2"','OData__UIVersionString':'2.0'}
 assert reconcile_review(e,b,p,performer_reference='worker:opaque-123')=='applied'
 assert prepare(e,b,target_etag='"2"')['action']=='already_applied'
 assert b['Coordination_x0020_note_x0020__x']=='Human edited note'

@pytest.mark.parametrize('field', [CONTRIBUTION_FIELD, EVENT_FIELD, EPISODE_FIELD,
                                 SOURCE_FIELD, MAPPING_FIELD, REVIEW_FIELD,
                                 REVIEW_TARGET_VERSION_FIELD])
def test_saved_receipt_requires_every_metadata_pin_not_only_state_and_versions(field):
 e,a=fixture();proposal=prepare(e,a)
 current={**a,**proposal['patch'],'odata.etag':'"2"','OData__UIVersionString':'2.0'}
 current[field]='33333333-3333-4333-8333-333333333333'
 before=deepcopy(current)
 assert reconcile_review(e,current,proposal,performer_reference='worker:opaque-123')!='applied'
 assert current==before

@pytest.mark.parametrize('field,value',[('Certification_x0020_name_x0020__','fictional certification reference'),('Certification_x0020_date','2026-01-01T00:00:00Z'),('AVAC_x0020_status','Pending form'),('AVAC_x0020_status','Entered'),('AVAC_x0020_status','Submitted'),('AVAC_x0020_status','Certified'),('AVAC_x0020_status','Unknown')])
def test_certified_or_submitted_history_is_never_automatically_changed(field,value):
 e,a=fixture();a[field]=value
 with pytest.raises(ValueError,match='amendment'):prepare(e,a)

@pytest.mark.parametrize('arg',['actual_work_confirmed','flags_confirmed','worker_confirmed'])
def test_each_explicit_review_is_required(arg):
 e,a=fixture()
 with pytest.raises(ValueError,match='Explicit'):prepare(e,a,**{arg:False})

def test_event_times_do_not_fill_missing_actual_work_or_unknown_flag():
 e,a=fixture();a[WORK[1]]=None
 with pytest.raises(ValueError,match='Incomplete'):prepare(e,a)
 e,a=fixture();a[FLAGS[0]]=None
 with pytest.raises(ValueError,match='Unknown'):prepare(e,a)

def test_source_correction_and_partial_save_remain_reviewable():
 e,a=fixture();p=prepare(e,a)
 assert reconcile_review(e,a,p,performer_reference='worker:opaque-123')=='not_applied_review_before_retry'
 b={**a,**p['patch'],'odata.etag':'"2"','OData__UIVersionString':'2.0'};e['OData__UIVersionString']='2.0'
 assert reconcile_review(e,b,p,performer_reference='worker:opaque-123')=='source_changed_review_required'
 with pytest.raises(ValueError,match='Source revision'):prepare(e,a)
 with pytest.raises(ValueError,match='Review required'):prepare(e,b,event_version='2.0',target_etag='"2"')
 b[REVIEW_FIELD]='Review required'
 assert prepare(e,b,event_version='2.0',target_etag='"2"')['action']=='review'

def test_stale_target_uncertain_conflict_and_identity_change_refuse():
 e,a=fixture();p=prepare(e,a);b={**a,'odata.etag':'"2"'}
 assert reconcile_review(e,b,p,performer_reference='worker:opaque-123')=='conflict_reconcile_manually'
 with pytest.raises(ValueError,match='Target revision'):prepare(e,b)
 a[CONTRIBUTION_FIELD]='different'
 with pytest.raises(ValueError,match='identity'):prepare(e,a)

@pytest.mark.parametrize('state',['Retracted','Correction pending'])
def test_retracted_or_correction_pending_source_requires_manual_review(state):
 e,a=fixture();e[EVENT_STATE_FIELD]=state
 with pytest.raises(ValueError,match='requires manual review'):prepare(e,a)

def test_overlap_and_explicit_clear_never_cascade():
 e,a=fixture();other={**a,'GUID':'33333333-3333-4333-8333-333333333333'}
 with pytest.raises(ValueError,match='Overlapping'):prepare(e,a,other_episodes=[other])
 assert prepare(e,a,other_episodes=[other],overlap_reviewed=True)['action']=='review'
 p=prepare(e,a);assert not set(WORK) & p['patch'].keys()
 a[WORK[2]]=a[WORK[1]]
 with pytest.raises(ValueError,match='End must'):prepare(e,a)


def test_recall_date_uses_brisbane_start_day_across_midnight():
 e,a=fixture();a[WORK[0]]='2026-01-01T14:00:00Z'
 with pytest.raises(ValueError,match='Recall date'):prepare(e,a)

def test_replay_reconciliation_still_checks_identity_and_saved_values():
 e,a=fixture();first=prepare(e,a);a.update(first['patch']);a['OData__UIVersionString']='2.0'
 replay=prepare(e,a)
 assert replay['action']=='already_applied'
 changed={**a,REVIEW_FIELD:'Review required','odata.etag':'"2"'}
 assert reconcile_review(e,changed,replay,performer_reference='worker:opaque-123')=='conflict_reconcile_manually'
 wrong_event={**e,'GUID':'33333333-3333-4333-8333-333333333333'}
 assert reconcile_review(wrong_event,a,replay,performer_reference='worker:opaque-123')=='identity_conflict_reconcile_manually'

def test_uncertain_save_does_not_attest_changed_work_or_retracted_native_source():
 e,a=fixture();proposal=prepare(e,a);current={**a,**proposal['patch'],'OData__UIVersionString':'2.0',WORK[2]:'2026-01-01T15:00:00Z'}
 assert reconcile_review(e,current,proposal,performer_reference='worker:opaque-123')=='target_work_changed_review_required'
 current[WORK[2]]=a[WORK[2]]
 for state in ('Retracted','Correction pending'):
  e[EVENT_STATE_FIELD]=state
  assert reconcile_review(e,current,proposal,performer_reference='worker:opaque-123')=='source_changed_review_required'

@pytest.mark.parametrize(('field,value'),[
 ('Coordination_x0020_note_x0020__x','Concurrent human note edit'),
 ('AVAC_x0020_status','Pending form'),
 ('Certification_x0020_name_x0020__','Concurrent certification'),
 ('Certification_x0020_date','2026-01-02T00:00:00Z'),
])
def test_uncertain_save_reconciliation_refuses_changed_preserved_avac_content(field,value):
 e,a=fixture();proposal=prepare(e,a)
 current={**a,**proposal['patch'],'OData__UIVersionString':'2.0',field:value}
 assert field in proposal['work_snapshot']
 assert reconcile_review(e,current,proposal,performer_reference='worker:opaque-123')=='target_work_changed_review_required'

def test_event_episode_link_and_existing_identity_must_match():
 e,a=fixture();a['Ryan_x0020_call_x0020__x002d__x0Id']=202
 with pytest.raises(ValueError,match='not linked'):prepare(e,a)
 e,a=fixture();a[EVENT_FIELD]='33333333-3333-4333-8333-333333333333'
 with pytest.raises(ValueError,match='event identity'):prepare(e,a)
 e,a=fixture();a[EPISODE_FIELD]='33333333-3333-4333-8333-333333333333'
 with pytest.raises(ValueError,match='episode identity'):prepare(e,a)

def test_performer_reference_is_required_pinned_and_rechecked():
 e,a=fixture()
 with pytest.raises(ValueError,match='opaque performer'):
  prepare(e,a,performer_reference='')
 with pytest.raises(ValueError,match='opaque performer'):
  prepare(e,a,performer_reference='Alex Example')
 p=prepare(e,a)
 assert p['performer_reference']=='worker:opaque-123'
 assert reconcile_review(e,a,p,performer_reference='worker:other-opaque')=='performer_changed_review_required'

def test_canonical_uuid_performer_reference_is_accepted_when_native_value_matches():
 e,a=fixture();reference='33333333-3333-4333-8333-333333333333'
 a[PERFORMER_REFERENCE_FIELD]=reference
 proposal=prepare(e,a,performer_reference=reference)
 assert proposal['action']=='review'
 assert proposal['performer_reference']==reference

@pytest.mark.parametrize('value',[
 '11111111111141118111111111111111',
 '{11111111-1111-4111-8111-111111111111}',
 'urn:uuid:11111111-1111-4111-8111-111111111111',
])
def test_performer_uuid_must_match_native_canonical_shape(value):
 e,a=fixture()
 with pytest.raises(ValueError,match='opaque performer'):
  prepare(e,a,performer_reference=value)

def test_native_performer_reference_must_exist_and_match_explicit_review():
 e,a=fixture();a.pop(PERFORMER_REFERENCE_FIELD)
 with pytest.raises(ValueError,match='Native verified performer'):
  prepare(e,a)
 e,a=fixture();a[PERFORMER_REFERENCE_FIELD]='worker:different'
 with pytest.raises(ValueError,match='Native verified performer'):
  prepare(e,a)

def test_changed_native_performer_reference_requires_review_reconciliation():
 e,a=fixture();proposal=prepare(e,a)
 current={**a,**proposal['patch'],'odata.etag':'"2"',PERFORMER_REFERENCE_FIELD:'worker:changed'}
 assert PERFORMER_REFERENCE_FIELD in proposal['work_snapshot']
 assert reconcile_review(e,current,proposal,performer_reference='worker:opaque-123')=='performer_changed_review_required'

@pytest.mark.parametrize('bad_id',[0,-1,101.5,'101','101.5',True])
def test_native_link_ids_must_be_positive_native_integers(bad_id):
 e,a=fixture();a['Ryan_x0020_call_x0020__x002d__x0Id']=bad_id
 with pytest.raises(ValueError,match='not linked'):
  prepare(e,a)

@pytest.mark.parametrize('arg,value',[('actual_work_confirmed','yes'),('flags_confirmed',1),('worker_confirmed','true')])
def test_review_confirmations_require_real_booleans(arg,value):
 e,a=fixture()
 with pytest.raises(ValueError,match='Explicit'):
  prepare(e,a,**{arg:value})

def test_reconciliation_refuses_changed_native_event_lookup():
 e,a=fixture();proposal=prepare(e,a)
 current={**a,**proposal['patch'],'odata.etag':'"2"','OData__UIVersionString':'2.0','Ryan_x0020_call_x0020__x002d__x0Id':202}
 assert reconcile_review(e,current,proposal,performer_reference='worker:opaque-123')=='identity_conflict_reconcile_manually'

@pytest.mark.parametrize('version',['1.1','0.0','v1.0',1.0,None])
def test_target_minor_or_invalid_revision_is_not_advanced(version):
 e,a=fixture();a['OData__UIVersionString']=version
 with pytest.raises(ValueError,match='major revision'):
  prepare(e,a)

@pytest.mark.parametrize('version',[None,'',0,1.0,'unknown','0.0'])
def test_source_revision_must_be_a_native_nonempty_version_string(version):
 e,a=fixture();e['OData__UIVersionString']=version
 with pytest.raises(ValueError,match='Source revision'):
  prepare(e,a,event_version=version)

@pytest.mark.parametrize('etag',[None,'','*',1,' "1" '])
def test_target_etag_must_be_an_exact_nonempty_string(etag):
 e,a=fixture();a['odata.etag']=etag
 with pytest.raises(ValueError,match='Target revision'):
  prepare(e,a,target_etag=etag)

def test_reviewed_target_with_changed_work_or_human_edit_requires_re_review():
 e,a=fixture();proposal=prepare(e,a)
 saved={**a,**proposal['patch'],'OData__UIVersionString':'2.0','odata.etag':'"2"'}
 changed_work={**saved,WORK[2]:'2026-01-01T15:00:00Z','OData__UIVersionString':'3.0','odata.etag':'"3"'}
 with pytest.raises(ValueError,match='Review required'):
  prepare(e,changed_work,event_version='1.0',target_etag='"3"')
 changed_note={**saved,'Coordination_x0020_note_x0020__x':'New manual edit','OData__UIVersionString':'3.0','odata.etag':'"3"'}
 with pytest.raises(ValueError,match='Review required'):
  prepare(e,changed_note,event_version='1.0',target_etag='"3"')

def test_reconciliation_does_not_report_concurrent_postwrite_revision_as_applied():
 e,a=fixture();proposal=prepare(e,a)
 concurrent={**a,**proposal['patch'],'OData__UIVersionString':'3.0','odata.etag':'"3"'}
 assert reconcile_review(e,concurrent,proposal,performer_reference='worker:opaque-123')=='conflict_reconcile_manually'


def create_recovery_fixture():
 request = {
  'url': DDMS_SITE + "/_api/web/lists(guid'00000000-0000-4000-8000-000000000107')/items",
  'method': 'post',
  'body': {'Title': 'DDMS episode 11111111-1111-4111-8111-111111111111',
           EVENT_LOOKUP_ID_FIELD: 101,
           'Coordination_x0020_note_x0020__x': 'Fictional preserved manual note'},
 }
 row = {**request['body'], 'Id': 17, 'GUID': '22222222-2222-4222-8222-222222222222',
        'OData__UIVersionString': '1.0',
        'odata.id': DDMS_SITE + "/_api/Web/Lists(guid'00000000-0000-4000-8000-000000000107')/Items(17)"}
 return request, row


def test_cli_create_recovery_survives_process_restart_without_another_write(tmp_path):
 import json
 import subprocess
 import sys
 request, row = create_recovery_fixture()
 for name, value in [('request', request), ('matches', {'value': [row]}), ('same-id', row)]:
  (tmp_path / (name + '.json')).write_text(json.dumps(value))
 # The first process may have died after sending: restart from durable inputs.
 run = subprocess.run([sys.executable, '-m', 'scripts.ddms_reviewed_contribution',
  '--request', str(tmp_path / 'request.json'), '--matches', str(tmp_path / 'matches.json'),
  '--same-id-readback', str(tmp_path / 'same-id.json'), '--correlation-field', 'Title'],
  capture_output=True, text=True, check=True)
 outcome = json.loads(run.stdout)
 assert outcome['outcome'] == 'saved_same_id'
 assert outcome['item_id'] == 17 and outcome['retry_allowed'] is False
 assert json.loads((tmp_path / 'same-id.json').read_text()) == row


@pytest.mark.parametrize('rows,expected', [([], 'unresolved_no_retry'),
                                        ([{}, {}], 'multiple_matches_reconcile_manually')])
def test_create_zero_or_multiple_matches_never_authorise_retry(rows, expected):
 request, row = create_recovery_fixture()
 outcome = reconcile_create(request, {'value': rows}, correlation_field='Title')
 assert outcome == {'outcome': expected, 'retry_allowed': False}


def test_create_single_match_still_requires_independent_same_id_readback():
 request, row = create_recovery_fixture()
 assert reconcile_create(request, {'value': [row]}, correlation_field='Title') == {
  'outcome': 'same_id_read_required', 'item_id': 17, 'retry_allowed': False}


@pytest.mark.parametrize('field,value', [
 (EVENT_LOOKUP_ID_FIELD, 202), ('Coordination_x0020_note_x0020__x', 'Later human edit'),
 ('Title', 'Another correlation')])
def test_create_recovery_preserves_changed_payload_and_refuses_recreation(field, value):
 request, row = create_recovery_fixture()
 current = {**row, field: value, 'OData__UIVersionString': '2.0'}
 outcome = reconcile_create(request, {'value': [row]}, correlation_field='Title',
                            same_id_readback=current)
 assert outcome['outcome'] == 'saved_with_changes_review_required'
 assert outcome['retry_allowed'] is False and current[field] == value


@pytest.mark.parametrize('field,value', [
 ('Id', True), ('GUID', 'not-a-guid'), ('OData__UIVersionString', ''),
 ('odata.id', DDMS_SITE + "/_api/Web/Lists(guid'00000000-0000-4000-8000-000000000106')/Items(17)")])
def test_create_recovery_rejects_foreign_or_invalid_native_identity(field, value):
 request, row = create_recovery_fixture()
 outcome = reconcile_create(request, {'value': [{**row, field: value}]}, correlation_field='Title')
 assert outcome['outcome'] == 'invalid_native_identity_reconcile_manually'
 assert outcome['retry_allowed'] is False


def test_create_recovery_refuses_item_substitution_between_query_and_readback():
 request, row = create_recovery_fixture()
 current = {**row, 'GUID': '33333333-3333-4333-8333-333333333333'}
 outcome = reconcile_create(request, {'value': [row]}, correlation_field='Title',
                            same_id_readback=current)
 assert outcome['outcome'] == 'identity_conflict_reconcile_manually'


def test_create_query_must_be_complete_and_correlated():
 request, row = create_recovery_fixture()
 outcome = reconcile_create(request, {'value': [row], 'odata.nextLink': 'another-page'},
                            correlation_field='Title', same_id_readback=row)
 assert outcome['outcome'] == 'incomplete_query_reconcile_manually'
 outcome = reconcile_create(request, {'value': [{**row, 'Title': 'other'}]}, correlation_field='Title')
 assert outcome['outcome'] == 'correlation_mismatch_reconcile_manually'


def test_create_recovery_does_not_certify_a_later_unposted_human_edit():
 request, row = create_recovery_fixture()
 current = {**row, 'AVAC_x0020_status': 'Pending form', 'OData__UIVersionString': '2.0'}
 outcome = reconcile_create(request, {'value': [row]}, correlation_field='Title',
                            same_id_readback=current)
 assert outcome['outcome'] == 'created_then_changed_review_required'
 assert outcome['retry_allowed'] is False and current['AVAC_x0020_status'] == 'Pending form'


@pytest.mark.parametrize('posted,native', [(None, 'missing'), (False, 0), (101, 101.0)])
def test_create_recovery_needs_explicit_values_with_native_json_types(posted, native):
 request, row = create_recovery_fixture()
 request['body']['RequiredSnapshot'] = posted
 if native != 'missing':
  row['RequiredSnapshot'] = native
 outcome = reconcile_create(request, {'value': [row]}, correlation_field='Title', same_id_readback=row)
 assert outcome['outcome'] == 'saved_with_changes_review_required'


@pytest.mark.parametrize('change', [
 {'url': 'https://example.org/items'}, {'method': 'get'}, {'headers': {'if-match': '*'}},
 {'url': DDMS_SITE + "/_api/web/lists(guid'00000000-0000-4000-8000-000000000107')/items?other=true"}])
def test_create_recovery_cannot_be_repurposed_for_another_target_or_operation(change):
 request, row = create_recovery_fixture()
 with pytest.raises(ValueError, match='Exact DDMS'):
  reconcile_create({**request, **change}, {'value': [row]}, correlation_field='Title')


@pytest.mark.parametrize('snapshot', [None, [], {'url': 17}])
def test_create_recovery_rejects_malformed_request_snapshot(snapshot):
 with pytest.raises(ValueError, match='Durable DDMS create request'):
  reconcile_create(snapshot, {'value': []}, correlation_field='Title')
