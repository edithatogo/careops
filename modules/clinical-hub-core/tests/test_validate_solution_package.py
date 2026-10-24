import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

spec = importlib.util.spec_from_file_location('solution_check', Path(__file__).parents[1] / 'scripts/validate_solution_package.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
FLOW = '00000000-0000-0000-0000-000000000001'


def package(tmp_path, name='test.zip', *, reference=True, declared=True, value='fictional', metadata='one', nested_alias='sp', parameters=None, prompt="0", extra_reference=False):
    path = tmp_path / name
    root = f'<RootComponent type="29" id="{{{FLOW}}}"/>' if declared else ''
    refs = f'<connectionreference connectionreferencelogicalname="test_sp"><connectorid>/apis/shared_sharepointonline</connectorid><promptingbehavior>{prompt}</promptingbehavior></connectionreference>' if reference else ''
    if extra_reference:
        refs += '<connectionreference connectionreferencelogicalname="test_unused"><connectorid>/apis/shared_office365</connectorid></connectionreference>'
    data = {'properties': {'definition': {'metadata': metadata, 'parameters': parameters or {}, 'triggers': {'manual': {'type': 'Request'}}, 'actions': {'scope': {'type': 'Scope', 'actions': {'read': {'type': 'OpenApiConnection', 'inputs': {'host': {'connectionName': nested_alias}, 'parameters': {'value': value}}}}}}}, 'connectionReferences': {'sp': {'connection': {'connectionReferenceLogicalName': 'test_sp'}, 'api': {'name': 'shared_sharepointonline'}, 'runtimeSource': 'invoker'}}}}
    with ZipFile(path, 'w') as z:
        z.writestr('solution.xml', f'<ImportExportXml><SolutionManifest><UniqueName>test</UniqueName><Version>1.0.0.0</Version><Managed>0</Managed><RootComponents>{root}</RootComponents></SolutionManifest></ImportExportXml>')
        z.writestr('customizations.xml', f'<ImportExportXml><connectionreferences>{refs}</connectionreferences></ImportExportXml>')
        z.writestr(f'Workflows/Test-{FLOW}.json', json.dumps(data))
    return path


def test_solution_reference_is_valid_without_root_reference_component(tmp_path):
    result = check.inspect_package(package(tmp_path))
    assert result['status'] == 'PASS'
    assert result['reference_count'] == 1


def test_missing_reference_and_nested_host_fail(tmp_path):
    result = check.inspect_package(package(tmp_path, reference=False, nested_alias='other'))
    assert result['status'] == 'FAIL'
    assert any('unresolved_connection_reference' in x for x in result['errors'])
    assert any('unbound_connector_host' in x for x in result['errors'])


def test_incomplete_manifest_fails(tmp_path):
    assert check.inspect_package(package(tmp_path, declared=False))['status'] == 'FAIL'


def test_semantic_change_detected_but_export_metadata_ignored(tmp_path):
    baseline = check.inspect_package(package(tmp_path))
    metadata = check.inspect_package(package(tmp_path, 'metadata.zip', metadata='two'))
    changed = check.inspect_package(package(tmp_path, 'changed.zip', value='different'))
    assert check.compare_packages(metadata, baseline)['changed'] == []
    assert check.compare_packages(changed, baseline)['changed'] == [FLOW]
    assert 'fictional' not in json.dumps(baseline)


def test_legacy_or_malformed_package_fails_without_private_error(tmp_path):
    path = tmp_path / 'legacy.zip'
    with ZipFile(path, 'w') as z:
        z.writestr('manifest.json', '{"private": "do not print"}')
    result = check.inspect_package(path)
    assert result['status'] == 'FAIL'
    assert 'do not print' not in json.dumps(result)
    assert check.compare_packages(result, result)['status'] == 'NOT_COMPARED'


def test_literal_connector_shaped_payload_is_not_executable(tmp_path):
    payload = {'type': 'OpenApiConnection', 'inputs': {'host': {'connectionName': 'not-a-binding'}}}
    result = check.inspect_package(package(tmp_path, value=payload))
    assert result['status'] == 'PASS'


def test_configuration_findings_redact_values_and_labels():
    definition = {'triggers': {}, 'actions': {'private-action-label': {
        'type': 'Scope', 'actions': {'private-read-label': {
            'type': 'OpenApiConnection', 'inputs': {'parameters': {
                'dataset': 'https://private.example/site',
                'table': 'private-list-id',
                'siteAddress': 'private-address@example.invalid',
                'calendarId': "@parameters('test_calendar')",
                'Uri': "@concat('https://private.example/', variables('id'))",
                'body': {'dataset': 'not-executable'},
            }}}}}}}
    result = check.configuration_review(definition)
    assert result['status'] == 'REVIEW_REQUIRED'
    assert len(result['findings']) == 4
    assert result['parameter_reference_count'] == 1
    assert {f['form'] for f in result['findings']} == {'literal_requires_review', 'expression_requires_review'}
    text = json.dumps(result)
    for value in ['private.example', 'private-action-label', 'private-read-label', 'private-list-id', 'test_calendar', 'not-executable', 'private-address@example.invalid']:
        assert value not in text
    assert next(f for f in result['findings'] if f['kind'] == 'site' and f['location'].endswith('siteAddress'))['form'] == 'literal_requires_review'
    assert result['findings'][0]['location'] == 'actions/0/actions/0/inputs/parameters/dataset'


def test_configuration_scope_does_not_claim_clearance_for_other_payloads():
    definition = {'triggers': {}, 'actions': {'compose': {
        'type': 'Compose', 'inputs': {'dataset': 'private-site'}}}}
    result = check.configuration_review(definition)
    assert result['status'] == 'NO_CANDIDATES_IN_SCOPE'
    assert result['findings'] == []
    assert 'separate review' in result['limit']


def test_changed_default_parameter_is_detected_with_unchanged_actions(tmp_path):
    old = check.inspect_package(package(tmp_path, parameters={
        'destination': {'type': 'String', 'defaultValue': 'private-old-destination'}}))
    new = check.inspect_package(package(tmp_path, 'new.zip', parameters={
        'destination': {'type': 'String', 'defaultValue': 'private-new-destination'}}))
    assert old['flows'][FLOW]['graph_sha256'] == new['flows'][FLOW]['graph_sha256']
    assert old['flows'][FLOW]['bindings_sha256'] == new['flows'][FLOW]['bindings_sha256']
    assert check.compare_packages(new, old)['changed'] == [FLOW]
    output = json.dumps(new)
    assert 'private-new-destination' not in output
    assert 'destination' not in output


def test_parameter_key_order_does_not_create_a_change(tmp_path):
    first = check.inspect_package(package(tmp_path, parameters={
        'first': {'type': 'String'}, 'second': {'type': 'Object'}}))
    reordered = check.inspect_package(package(tmp_path, 'reordered.zip', parameters={
        'second': {'type': 'Object'}, 'first': {'type': 'String'}}))
    assert check.compare_packages(reordered, first)['changed'] == []


def test_changed_reference_component_detected_despite_unchanged_flow(tmp_path):
    old = check.inspect_package(package(tmp_path))
    new = check.inspect_package(package(tmp_path, 'prompt.zip', prompt='1'))
    comparison = check.compare_packages(new, old)
    assert old['status'] == new['status'] == 'PASS'
    assert comparison['changed'] == []
    assert comparison['references']['changed'] == ['test_sp']
    assert 'promptingbehavior' not in json.dumps(new)


def test_added_and_removed_unused_reference_are_visible(tmp_path):
    old = check.inspect_package(package(tmp_path))
    new = check.inspect_package(package(tmp_path, 'extra.zip', extra_reference=True))
    assert check.compare_packages(new, old)['references']['added'] == ['test_unused']
    assert check.compare_packages(old, new)['references']['removed'] == ['test_unused']
