"""Same-flow selected-register graph: native guard and persistence boundaries."""
from copy import deepcopy
import re

import pytest

from scripts.f10_source_adapter import build_agenda_operator_integration, build_selected_register_flow
from scripts.f09_isolated_writer import REGISTER_FIELD_TYPES
from tests.test_f10_source_adapter import BINDINGS, fictional_baseline, walk_actions


def config():
    old = build_agenda_operator_integration(fictional_baseline(), **(BINDINGS | {
        'entity_type': 'SP.Data.FictionalListItem', 'source_url': 'https://example.test/source',
        'selected_record_id': 'FICTIONAL-F10-A1'}),
        meeting_time_zone='E. Australia Standard Time',
        source_choices=['FICTIONAL-F10-A1', 'FICTIONAL-F10-A2', 'FICTIONAL-F10-A3'],
        expected_meeting_id='FICTIONAL-MEETING-2099-02-01',
        expected_meeting_date='2099-01-31T14:00:00Z',
        agenda_list_id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb')
    cfg = dict(site=BINDINGS['site'], selection_files={'Fictional meeting':
        '/sites/fictional/Shared Documents/F10-selection.json'}, register_configs={
            BINDINGS['list_id']: {'field_map': {k: k for k in REGISTER_FIELD_TYPES},
                'description': BINDINGS['description'], 'synthetic_only': True}},
        calendar_action={'type': 'OpenApiConnection', 'runAfter': {}, 'inputs': {
            'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_office365',
                     'connectionName': 'shared_office365', 'operationId': 'HttpRequest'},
            'parameters': {'Method': 'GET', 'Uri': 'https://graph.microsoft.com/v1.0/me/events/example'}}},
        calendar_reference={'runtimeSource': 'invoker', 'connection': {'connectionReferenceLogicalName': 'existing_outlook'},
                            'api': {'name': 'shared_office365'}},
        meeting_time_zone='E. Australia Standard Time')
    return old, cfg


def build():
    baseline, cfg = config()
    return build_selected_register_flow(baseline, **cfg)


def test_connected_preview_distinguishes_native_source_and_unverified_claims():
    actions = dict(walk_actions(build()['properties']['definition']['actions']))
    preview = actions['Retained_review_preview']['inputs']
    assert preview['source'] == 'Selected native register rows; identity and versions rechecked'
    assert 'UNVERIFIED_SUPPLIED_INPUT' in preview['claims_status']
    assert 'UNVERIFIED_FICTIONAL_INPUT' in preview['claims_status']
    assert preview['synthetic_only'] == "@body('Selected_parse')?['synthetic_only']"
    assert 'Selection file version' in preview['source_version_scope']
    assert 'business approval' in preview['stage']


def test_same_operator_preserves_classifier_and_unique_destination_graph():
    baseline, cfg = config(); original = deepcopy(baseline); bindings = deepcopy(cfg)
    new = build_selected_register_flow(baseline, **cfg)
    assert baseline == original and cfg == bindings
    a = new['properties']['definition']['actions']; all_a = dict(walk_actions(a))
    old_a = dict(walk_actions(baseline['properties']['definition']['actions']))
    for name in ('Evaluate_Supplied_Claims', 'Classify_For_Review', 'Proposed_Review_Items',
                 'Excluded_Review_Items', 'Blocking_Exceptions', 'Create_agenda_carry_draft',
                 'Create_failed_or_uncertain_STOP', 'Read_carry_operation', 'Resolve_or_create_agenda'):
        assert all_a[name] == old_a[name]
    assert 'Selected_register_initial' in a and 'Selected_register_final' in a
    assert set(new['properties']['connectionReferences']) == {'shared_sharepointonline', 'shared_office365'}
    assert 'source_selection' in new['properties']['definition']['triggers']['manual']['inputs']['schema']['required']


def test_all_action_names_unique_runafter_siblings_and_expression_references_exist():
    a = build()['properties']['definition']['actions']
    pairs = list(walk_actions(a)); names = [n for n, _ in pairs]
    assert len(names) == len(set(names))
    def check(actions, depth=1, in_loop=False):
        assert depth <= 8
        for name, action in actions.items():
            assert set(action.get('runAfter', {})) <= actions.keys(), name
            assert not (in_loop and action['type'] == 'Terminate'), name
            for branch in ('actions',):
                if branch in action: check(action[branch], depth+1, in_loop or action['type']=='Foreach')
            if 'else' in action: check(action['else'].get('actions', {}), depth+1, in_loop)
    check(a)
    def texts(value):
        if isinstance(value, str): yield value
        elif isinstance(value, dict):
            for v in value.values(): yield from texts(v)
        elif isinstance(value, list):
            for v in value: yield from texts(v)
    for text in texts(a):
        for ref in re.findall(r"(?:outputs|body|actions)\('([^']+)'\)", text):
            assert ref in names, ref


def test_source_guards_and_only_one_no_retry_agenda_write():
    a = build()['properties']['definition']['actions']; actions = dict(walk_actions(a))
    calls = [v for v in actions.values() if v.get('type')=='OpenApiConnection'
             and v['inputs']['host']['connectionName']=='shared_sharepointonline']
    writes = [c for c in calls if c['inputs']['host']['operationId']!='GetFileContentByPath'
              and c['inputs']['parameters']['parameters/method']!='GET']
    assert len(writes)==1 and writes[0]==actions['Create_agenda_carry_draft']
    assert writes[0]['inputs']['retryPolicy']=={'type':'none'}
    assert 'synthetic_only' in actions['Carry_choice_gate']['expression']
    for token in ('Indexed','EnforceUniqueValues','MaxLength','Required','DefaultValue'):
        assert token in actions['Carry_choice_gate']['expression']
    assert 'Sourcehistory' in actions['Selected_collect']['inputs']['value']['source_text']
    assert 'LegacyactionID' in actions['Selected_row_guard']['expression']
    assert 'OData__UIVersionString' in actions['Selected_final_guard']['expression']
    assert 'UniqueId' in a['Selected_source_stable']['expression']
    assert 'Selected_errors' in a['Selected_source_stable']['expression']
    assert 'native_business_fields' in actions['Expected_agenda_fields']['inputs']['Title']
    assert 'listform.aspx' in actions['Expected_agenda_fields']['inputs']['Question_x0020_or_x0020_help_x00']
    assert actions['Selected_read_calendar']['inputs']['parameters']['Method']=='GET'
    assert 'meeting_revision' in actions['Selected_calendar_final_guard']['expression']
    assert a['Selected_content']['inputs']['host']['operationId']=='GetFileContentByPath'
    assert a['Selected_content']['inputs']['parameters']['inferContentType'] is True
    assert a['Selected_content']['inputs']['parameters']['path']=="@substring(outputs('Selected_path'),16)"
    assert "outputs('Selected_path')" in a['Selected_file_initial']['inputs']['parameters']['parameters/uri']


def test_parse_json_uses_supported_schema_without_weakening_identity_guards():
    a=build()['properties']['definition']['actions']
    def check(value):
        if isinstance(value,dict):
            assert 'pattern' not in value and 'patternProperties' not in value
            for child in value.values():check(child)
        elif isinstance(value,list):
            for child in value:check(child)
    check(a['Selected_parse']['inputs']['schema'])
    assert 'formatDateTime' in a['Selected_identity_guard']['expression']
    assert "['GUID']" in a['Selected_register_initial']['actions']['Selected_row_guard']['expression']


@pytest.mark.parametrize('fault', ['source_path','mapping','scope','baseline','calendar'])
def test_unqualified_or_changed_builder_inputs_refused(fault):
    base,cfg=config()
    if fault=='source_path':cfg['selection_files']['Fictional meeting']='/sites/other/file.json'
    if fault=='mapping':cfg['register_configs'][BINDINGS['list_id']]['field_map']['Title']='Sourcehistory'
    if fault=='scope':cfg['register_configs'][BINDINGS['list_id']]['description']='Live register'
    if fault=='baseline':base['properties']['state']='Started'
    if fault=='calendar':cfg['calendar_action']['inputs']['host']['connectionName']='other'
    with pytest.raises(ValueError):build_selected_register_flow(base,**cfg)
