"""Local native-graph construction checks; no connector or tenant calls."""
from copy import deepcopy
import json
import re

import pytest

from scripts.f06_selected_agenda import build_selected_agenda


def baseline():
    def action(op='HttpRequest', **parameters):
        return {'type': 'OpenApiConnection', 'runAfter': {}, 'inputs': {
            'host': {'operationId': op}, 'parameters': parameters}}
    donors = {
        'Word_output_name': {'type': 'Compose', 'runAfter': {}, 'inputs': 'legacy-WORD.docx'},
        'Read_word_template_pin': action(),
        'Read_word_template_parts': action('GetFileContentByPath'),
        'Run_maintained_document_script': action('RunScriptProdV2', scriptId='OLD',
                                                  drive='EXISTING', file='EXISTING-HOST'),
        'Stage_word_binary': action('CreateFile', name="@concat('F06-stage-',workflow()?['run']?['name'],'.docx')"),
        'Move_word_stage_without_overwrite': action(**{'parameters/method': 'POST',
            'parameters/uri': "@concat(outputs('Word_output_name'),',flags=0)')"}),
        'Guard_word_assets': {'type': 'If', 'runAfter': {}, 'expression': {'and': [
            {'equals': ["@body('Read_word_template_pin')?['UniqueId']", 'TEMPLATE']},
            {'equals': ["@body('Read_word_template_pin')?['UIVersionLabel']", '1.0']},
            {'equals': ["@body('Read_word_template_pin')?['Length']", '100']}]},
            'actions': {}, 'else': {'actions': {}}},
    }
    return {'properties': {'state': 'Stopped', 'connectionReferences': {
        name: {'original': name} for name in ['shared_sharepointonline', 'shared_excelonlinebusiness']},
        'definition': {'parameters': {'existing': {'type': 'String', 'defaultValue': 'UNCHANGED'}},
            'triggers': {'manual': {'inputs': {'schema': {'properties': {'text_2': {'type': 'string'}}}}}},
            'actions': {'Check_trigger_inputs': {'type': 'If', 'actions': {}, 'runAfter': {}},
                'Confirm_meeting_date': {'type': 'Compose', 'inputs': '2031-03-10', 'runAfter': {}},
                'Fictional_successor_adapter': {'type': 'If',
                    'runAfter': {'Check_trigger_inputs': ['Succeeded']}, 'actions': donors,
                    'else': {'actions': {}}}}}}}


def binding():
    return dict(register_list_id='00000000-0000-0000-0000-000000000003',
                outlook_reference={'runtimeSource': 'invoker', 'api': {'name': 'shared_office365'},
                    'connection': {'connectionReferenceLogicalName': 'existing_Outlook'}},
                script_id='NEW-NATIVE-SCRIPT', script_unique_id='00000000-0000-0000-0000-000000000002',
                script_version='1.0', script_bytes=12345)


def test_keeps_legacy_graph_bindings_state_parameters_and_adds_one_ordered_branch():
    source = baseline(); original = deepcopy(source); result = build_selected_agenda(source, **binding())
    assert source == original
    p = result['properties']; d = p['definition']; root = d['actions']
    assert p['state'] == 'Stopped' and d['parameters'] == original['properties']['definition']['parameters']
    assert root['Fictional_successor_adapter']['actions'] == original['properties']['definition']['actions']['Fictional_successor_adapter']['actions']
    assert root['Fictional_successor_adapter']['runAfter'] == {'Selected_occurrence_adapter': ['Succeeded']}
    assert root['Selected_occurrence_adapter']['runAfter'] == {'Selected_initialise_register': ['Succeeded']}
    assert p['connectionReferences']['shared_office365'] == binding()['outlook_reference']
    for name in ['shared_sharepointonline', 'shared_excelonlinebusiness']:
        assert p['connectionReferences'][name] == original['properties']['connectionReferences'][name]


def test_native_reads_versions_calendar_and_link_targets_before_create_only_commit():
    branch = build_selected_agenda(baseline(), **binding())['properties']['definition']['actions']['Selected_occurrence_adapter']['actions']
    assert 'F06-selection-' in branch['Selected_selection_path']['inputs']
    assert 'base64' in branch['Selected_selection_path']['inputs']
    assert 'GetFileByServerRelativePath' in branch['Selected_read_source']['inputs']['parameters']['parameters/uri']
    assert branch['Selected_read_source_body']['inputs']['parameters']['path'] == "@outputs('Selected_selection_path')"
    assert 'changeKey' in branch['Selected_read_calendar']['inputs']['parameters']['Uri']
    assert 'isCancelled' in branch['Selected_guard_calendar']['expression']
    for name in ['Selected_files_initial', 'Selected_files_final']:
        loop = branch[name]
        guard = loop['actions'][name + '_validate_id']
        assert 'substring' in guard['expression'] and 'replace' in guard['expression']
        child = guard['actions'][name + '_check']['expression']
        assert 'UIVersionLabel' in child and 'Doc.aspx?sourcedoc=%7B' in child
        assert all(v['type'] != 'Terminate' for v in guard['actions'].values())
    final_source = branch['Selected_guard_source']['expression']
    assert all(v in final_source for v in ['UniqueId', 'TimeLastModified', 'ETag', 'Length', 'UIVersionLabel'])
    assert len(branch['Selected_guard_assets_final']['expression']['and']) == 6
    assert branch['Selected_word_name']['runAfter'] == {'Selected_guard_assets_final': ['Succeeded']}
    script = branch['Selected_run_script']['inputs']['parameters']
    assert script['scriptId'] == 'NEW-NATIVE-SCRIPT' and script['drive'] == 'EXISTING'
    assert branch['Selected_word_job']['inputs']['kind'] == 'clinical-agenda-selected-word-v2'
    assert "'records',variables('SelectedRegisterRecords')" in branch['Selected_contract']['inputs']
    assert branch['Selected_register_final']['runAfter'] == {'Selected_guard_files_final': ['Succeeded']}
    assert branch['Selected_template_final']['runAfter'] == {'Selected_guard_register_final': ['Succeeded']}
    register = branch['Selected_register_initial']['actions']
    assert 'LegacyactionID' in register['Selected_register_initial_match']['expression']
    assert 'Selected_guard_register_schema' in branch
    assert 'Sourcehistory' in branch['Selected_guard_register_schema']['expression']
    append = register['Selected_register_initial_match']['actions']['Selected_register_initial_match_collect']['inputs']['value']
    assert 'Sourcehistory' in append['history'] and 'Originalduelabel' in append['due_label']
    assert 'Currentstatus' in append['status'] and append['response_ref'] is None
    assert 'listform.aspx' in append['source_link']['url']
    assert 'flags=0' in branch['Selected_commit_word']['inputs']['parameters']['parameters/uri']
    assert branch['Selected_stage_uncertain']['runAfter'] == {'Selected_stage_word': ['Failed', 'TimedOut']}
    assert branch['Selected_uncertain_output']['runAfter'] == {'Selected_commit_word': ['Failed', 'TimedOut']}


def test_no_register_calendar_message_or_permission_mutations():
    result = build_selected_agenda(baseline(), **binding()); branch = result['properties']['definition']['actions']['Selected_occurrence_adapter']
    calls = []
    def visit(value):
        if isinstance(value, dict):
            if value.get('type') == 'OpenApiConnection': calls.append(value)
            for child in value.values(): visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
    visit(branch)
    mutations = []
    for call in calls:
        p = call['inputs']['parameters']; op = call['inputs']['host']['operationId']
        if op == 'HttpRequest':
            if p.get('Method', p.get('parameters/method', 'GET')) != 'GET':
                mutations.append(call)
                assert p['parameters/method'] == 'POST' and 'flags=0' in p['parameters/uri']
        assert op in {'HttpRequest', 'GetFileContentByPath', 'RunScriptProdV2', 'CreateFile'}
    assert 'CreateEvent' not in json.dumps(result) and 'SendEmail' not in json.dumps(result)
    assert len(mutations) == 1


@pytest.mark.parametrize('change', ['bad-folder', 'no-outlook', 'empty-script', 'existing-branch', 'order'])
def test_unqualified_or_changed_inputs_refused(change):
    source = baseline(); cfg = binding()
    if change == 'bad-folder': cfg['selection_folder_path'] = "/invalid'folder"
    if change == 'no-outlook': cfg['outlook_reference']['api']['name'] = 'other'
    if change == 'empty-script': cfg['script_id'] = ''
    if change == 'existing-branch': source['properties']['definition']['actions']['Selected_occurrence_adapter'] = {}
    if change == 'order': source['properties']['definition']['actions']['Fictional_successor_adapter']['runAfter'] = {}
    with pytest.raises(ValueError): build_selected_agenda(source, **cfg)


@pytest.mark.parametrize('change', ['delete-instead-of-stage', 'overwrite-move'])
def test_changed_write_donor_refused(change):
    source = baseline()
    donors = source['properties']['definition']['actions']['Fictional_successor_adapter']['actions']
    if change == 'delete-instead-of-stage':
        donors['Stage_word_binary']['inputs']['host']['operationId'] = 'DeleteFile'
    else:
        p = donors['Move_word_stage_without_overwrite']['inputs']['parameters']
        p['parameters/uri'] = p['parameters/uri'].replace('flags=0', 'flags=1')
    with pytest.raises(ValueError): build_selected_agenda(source, **binding())


def test_generated_expression_delimiters_and_action_references():
    graph = build_selected_agenda(baseline(), **binding())['properties']['definition']['actions']
    names = set(); expressions = []
    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, dict) and child.get('type') in {
                    'Compose', 'If', 'Foreach', 'InitializeVariable', 'Terminate',
                    'OpenApiConnection', 'AppendToArrayVariable', 'Select',
                }:
                    assert key not in names, key
                    names.add(key)
                visit(child)
        elif isinstance(value, list):
            for child in value: visit(child)
        elif isinstance(value, str) and value.startswith('@'):
            expressions.append(value)
    visit(graph)
    for expression in expressions:
        quoted = False; stack = []; i = 0
        while i < len(expression):
            char = expression[i]
            if char == "'":
                if quoted and i + 1 < len(expression) and expression[i + 1] == "'":
                    i += 2; continue
                quoted = not quoted
            elif not quoted and char in '([': stack.append(char)
            elif not quoted and char in ')]':
                assert stack and stack.pop() == {')': '(', ']': '['}[char], expression
            i += 1
        assert not quoted and not stack, expression
        for ref in re.findall(r"(?:body|outputs|items)\('([^']+)'\)", expression):
            assert ref in names, (ref, expression)


def test_preserves_actual_flat_native_outlook_reference():
    args = binding()
    args["outlook_reference"] = {"id": "/providers/Microsoft.PowerApps/apis/shared_office365", "connectionReferenceLogicalName": "comeet_sharedoffice365_b2331", "source": "Invoker"}
    result = build_selected_agenda(baseline(), **args)
    assert result["properties"]["connectionReferences"]["shared_office365"] == args["outlook_reference"]


def test_calendar_link_is_native_derived_and_rechecked():
    a = build_selected_agenda(baseline(), **binding())["properties"]["definition"]["actions"]["Selected_occurrence_adapter"]["actions"]
    assert "not(empty(body('Selected_read_calendar')?['webLink']))" in a["Selected_guard_calendar"]["expression"]
    assert "body('Selected_read_calendar')?['webLink']" in a["Selected_contract"]["inputs"]
    assert "Selected_reread_calendar" in a["Selected_guard_calendar_final"]["expression"]


def test_native_register_reads_explicitly_project_nullable_fields():
    a = build_selected_agenda(baseline(), **binding())["properties"]["definition"]["actions"]["Selected_occurrence_adapter"]["actions"]
    for prefix in ["Selected_register_initial", "Selected_register_final"]:
        uri = a[prefix]["actions"][prefix + "_read"]["inputs"]["parameters"]["parameters/uri"]
        assert "?$select=Id,GUID,Title,LegacyactionID" in uri
        for field in ["Duedate", "Reviewdate", "Commissioningclassification", "Issuereadiness", "Originmeetingdate", "Closurereviewstate", "Acceptedclosuredate", "OData__UIVersionString"]:
            assert field in uri


def test_schema_guard_is_independent_of_nullable_connector_projection():
    a = build_selected_agenda(baseline(), **binding())["properties"]["definition"]["actions"]["Selected_occurrence_adapter"]["actions"]
    assert a["Selected_register_initial"]["runAfter"] == {"Selected_guard_register_schema": ["Succeeded"]}
    assert "/fields?$select=InternalName" in a["Selected_register_schema"]["inputs"]["parameters"]["parameters/uri"]
    for field in ["Duedate", "Reviewdate", "Sourcehistory", "_UIVersionString"]:
        assert field in a["Selected_guard_register_schema"]["expression"]
    condition = a["Selected_register_initial"]["actions"]["Selected_register_initial_match"]["expression"]
    assert "contains(body(" not in condition
    assert "native_version" in condition and "native_guid" in condition and "legacy_id" in condition


def test_file_links_accept_only_same_native_doc_identity_with_optional_view_action():
    a = build_selected_agenda(baseline(), **binding())["properties"]["definition"]["actions"]["Selected_occurrence_adapter"]["actions"]
    for prefix in ["Selected_files_initial", "Selected_files_final"]:
        guard = a[prefix]["actions"][prefix + "_validate_id"]["actions"][prefix + "_check"]["expression"]
        assert "or(equals(items(" in guard
        assert "'%7D'))" in guard and "'%7D&action=view'))" in guard
        assert "UIVersionLabel" in guard and "UniqueId" in guard and "Name" in guard
