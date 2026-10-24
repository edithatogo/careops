from copy import deepcopy
import json
from zipfile import ZipFile
import pytest
from scripts.f16_portability_candidates import build_candidate, build_package_candidates, digest, native_payload, write_outputs


def fixture():
    action = {'type': 'OpenApiConnection', 'runAfter': {'Human_review': ['Succeeded']},
              'inputs': {'host': {'connectionName': 'sp', 'operationId': 'HttpRequest',
                                 'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline'},
                         'parameters': {'dataset': 'https://example.invalid/site',
                                        'Uri': '/preserve-list-and-filter', 'Method': 'GET'}}}
    d = {'parameters': {}, 'triggers': {'manual': {'type': 'Request', 'kind': 'Button'}},
         'actions': {'Guard': {'type': 'If', 'expression': 'PRESERVE-GUARD',
                              'actions': {'Read': action}, 'else': {'actions': {}}},
                     'Literal': {'type': 'Compose', 'inputs': {'actions': {'fake': deepcopy(action)}}}}}
    p = {'definition': d, 'state': 'Stopped', 'owner': {'id': 'PRESERVE'},
         'connectionReferences': {'sp': {'api': {'name': 'shared_sharepointonline'},
                                       'runtimeSource': 'invoker',
                                       'connection': {'connectionReferenceLogicalName': 'PRESERVE'}}}}
    selection = {'path': ['actions', 'Guard', 'actions', 'Read', 'inputs', 'parameters', 'dataset'],
                 'expected_value': 'https://example.invalid/site',
                 'parameter_name': 'F06 source site URL (comeet_F06SourceSiteUrl)',
                 'parameter': {'type': 'String', 'defaultValue': 'https://example.invalid/site',
                               'metadata': {'schemaName': 'comeet_F06SourceSiteUrl'}}}
    return p, selection


def test_exact_scoped_delta_and_input_not_mutated():
    p, s = fixture(); before = deepcopy(p)
    result, review = build_candidate(p, digest(p), [s])
    assert p == before
    assert result['state'] == 'Stopped' and result['owner'] == p['owner']
    assert result['connectionReferences'] == p['connectionReferences']
    assert result['definition']['actions']['Literal'] == p['definition']['actions']['Literal']
    read = result['definition']['actions']['Guard']['actions']['Read']
    assert read['inputs']['parameters']['Uri'] == '/preserve-list-and-filter'
    assert read['runAfter'] == p['definition']['actions']['Guard']['actions']['Read']['runAfter']
    assert review['changes'] == [{'path': s['path'], 'before': s['expected_value'],
                                 'after': "@parameters('F06 source site URL (comeet_F06SourceSiteUrl)')"}]
    assert not review['native_deployment_ready']


@pytest.mark.parametrize('change', ['source', 'literal', 'path', 'duplicate', 'default', 'alias', 'binding'])
def test_drift_unsafe_rebinding_or_nonexecutable_paths_refused(change):
    p, s = fixture(); pin = digest(p)
    selections = [s]
    if change == 'source': p['definition']['actions']['Guard']['expression'] = 'NEW-GUARD'
    if change == 'literal': s['expected_value'] = 'https://other.invalid'
    if change == 'path': s['path'] = ['actions','Literal','inputs','actions','fake','inputs','parameters','dataset']
    if change == 'duplicate': selections.append(deepcopy(s))
    if change == 'default': s['parameter']['defaultValue'] = ''
    if change == 'alias':
        p['definition']['parameters']['other'] = deepcopy(s['parameter']); pin = digest(p)
    if change == 'binding':
        p['connectionReferences']['sp']['runtimeSource'] = 'Embedded'; pin = digest(p)
    before = deepcopy(p)
    with pytest.raises(ValueError): build_candidate(p, pin, selections)
    assert p == before


def test_each_distinct_site_needs_its_own_explicit_parameter():
    p, s = fixture()
    other = deepcopy(p['definition']['actions']['Guard']['actions']['Read'])
    other['inputs']['parameters']['dataset'] = 'https://personal.invalid'
    p['definition']['actions']['Other'] = other
    t = deepcopy(s); t['path'] = ['actions','Other','inputs','parameters','dataset']
    t['expected_value'] = 'https://personal.invalid'
    with pytest.raises(ValueError): build_candidate(p, digest(p), [s,t])
    t['parameter_name'] = 'F07 paper site URL (comeet_F07PaperSiteUrl)'
    t['parameter']['metadata']['schemaName'] = 'comeet_F07PaperSiteUrl'
    t['parameter']['defaultValue'] = t['expected_value']
    _, review = build_candidate(p, digest(p), [s,t])
    assert len(review['added_parameters']) == 2


def test_output_collision_preflight_and_idempotent_exact_rerun(tmp_path):
    outputs = {'a': {'candidate': {'preserve': True}}, 'b': {'candidate': {'other': True}}}
    (tmp_path/'b-candidate.json').write_text('EXISTING')
    with pytest.raises(ValueError): write_outputs(tmp_path, outputs)
    assert not (tmp_path/'a-candidate.json').exists()
    (tmp_path/'b-candidate.json').unlink()
    write_outputs(tmp_path, outputs); before = (tmp_path/'a-candidate.json').read_bytes()
    write_outputs(tmp_path, outputs)
    assert (tmp_path/'a-candidate.json').read_bytes() == before
    assert (tmp_path/'a-candidate.json').stat().st_mode & 0o777 == 0o600


def test_package_and_complete_properties_pins_required(tmp_path):
    import hashlib
    p, s = fixture(); fid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    package = tmp_path/'input.zip'
    with ZipFile(package, 'w') as z:
        z.writestr('Workflows/Example-' + fid.upper() + '.json', json.dumps({'properties': p}))
    plan = {'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
            'flows': [{'workflow_id': fid, 'expected_sha256': digest(p), 'selections': [s]}]}
    assert len(build_package_candidates(package, plan)) == 1
    plan['flows'][0]['expected_sha256'] = '0'*64
    with pytest.raises(ValueError, match='source_drift'): build_package_candidates(package, plan)
    plan['package_sha256'] = '0'*64
    with pytest.raises(ValueError, match='package_drift'): build_package_candidates(package, plan)


def test_switch_default_and_webhook_paths_preserved():
    p, s = fixture(); a = deepcopy(p['definition']['actions']['Guard']['actions']['Read'])
    a['type'] = 'OpenApiConnectionWebhook'
    p['definition']['actions']['Switch'] = {'type': 'Switch', 'expression': 'PRESERVE',
        'cases': {'x': {'case': 'x', 'actions': {'Hook': a}}}, 'default': {'actions': {'Fallback': deepcopy(a)}}}
    s['path'] = ['actions','Switch','cases','x','actions','Hook','inputs','parameters','dataset']
    t = deepcopy(s); t['path'] = ['actions','Switch','default','actions','Fallback','inputs','parameters','dataset']
    r, review = build_candidate(p, digest(p), [s,t])
    assert r['definition']['actions']['Switch']['expression'] == 'PRESERVE'
    assert len(review['changes']) == 2 and len(review['added_parameters']) == 1


def test_host_api_mismatch_is_not_fixed_by_a_sharepoint_reference():
    p, s = fixture()
    p['definition']['actions']['Guard']['actions']['Read']['inputs']['host']['apiId'] = '/wrong-api'
    with pytest.raises(ValueError, match='unqualified_sharepoint'): build_candidate(p, digest(p), [s])


def test_native_rebase_preserves_service_metadata_and_complete_connection_refs():
    p, s = fixture(); fid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    native = {'name': 'flow-cloud-id', 'properties': deepcopy(p)}
    native['properties']['workflowEntityId'] = fid
    native['properties']['definition']['metadata'] = {'native': 'PRESERVE'}
    read = native['properties']['definition']['actions']['Guard']['actions']['Read']
    read['inputs']['authentication'] = "@parameters('$authentication')"
    native['properties']['connectionReferences']['sp']['serviceMetadata'] = 'PRESERVE'
    payload = native_payload(native, digest(native), fid, p, [s])
    assert set(payload) == {'properties'}
    assert set(payload['properties']) == {'definition', 'connectionReferences'}
    assert payload['properties']['definition']['metadata'] == {'native': 'PRESERVE'}
    assert payload['properties']['connectionReferences'] == native['properties']['connectionReferences']
    r = payload['properties']['definition']['actions']['Guard']['actions']['Read']
    assert r['inputs']['authentication'] == "@parameters('$authentication')"


def test_proved_flat_flow_rp_invoker_shape_retained_verbatim():
    p, s = fixture(); fid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    native = {'name': 'flow-cloud-id', 'properties': deepcopy(p)}
    native['properties']['workflowEntityId'] = fid
    flat = {'apiName': 'sharepointonline', 'source': 'Invoker',
            'connectionReferenceLogicalName': 'PRESERVE', 'displayName': 'PRESERVE'}
    native['properties']['connectionReferences']['sp'] = flat
    payload = native_payload(native, digest(native), fid, p, [s])
    assert payload['properties']['connectionReferences']['sp'] == flat


@pytest.mark.parametrize('change', ['pin', 'guard', 'identity', 'state', 'reference'])
def test_native_rebase_refuses_intervening_change(change):
    p, s = fixture(); fid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    native = {'name': 'flow-cloud-id', 'properties': deepcopy(p)}
    native['properties']['workflowEntityId'] = fid
    if change == 'guard': native['properties']['definition']['actions']['Guard']['expression'] = 'CHANGED'
    if change == 'identity': native['properties']['workflowEntityId'] = 'other'
    if change == 'state': native['properties']['state'] = 'Started'
    if change == 'reference': native['properties']['connectionReferences']['sp']['runtimeSource'] = 'Embedded'
    pin = '0'*64 if change == 'pin' else digest(native)
    with pytest.raises(ValueError): native_payload(native, pin, fid, p, [s])


@pytest.mark.parametrize('has_parameters', [True, False])
def test_cli_native_output_matches_existing_helper_contract_and_refuses_overwrite(tmp_path, has_parameters):
    import hashlib
    import subprocess
    import sys
    from pathlib import Path
    p, s = fixture(); fid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    if not has_parameters: del p['definition']['parameters']
    package = tmp_path/'input.zip'
    with ZipFile(package, 'w') as z:
        z.writestr('Workflows/Example-' + fid.upper() + '.json', json.dumps({'properties': p}))
    plan = {'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
            'flows': [{'workflow_id': fid, 'expected_sha256': digest(p), 'selections': [s]}]}
    plan_path = tmp_path/'plan.json'; plan_path.write_text(json.dumps(plan))
    native = {'name': 'cloud-id', 'properties': deepcopy(p)}
    native['properties']['workflowEntityId'] = fid
    native['properties']['definition']['metadata'] = {'preserve': 'native-metadata'}
    native_path = tmp_path/'native.json'; native_path.write_text(json.dumps(native))
    output = tmp_path/'output'
    root = Path(__file__).resolve().parents[1]
    cmd = [sys.executable, str(root/'scripts/f16_portability_candidates.py'),
           '--package', str(package), '--plan', str(plan_path), '--output', str(output),
           '--native-preimage', str(native_path), '--native-sha256', digest(native), '--workflow-id', fid]
    run = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['flows'] == 1
    path = output/(fid+'-candidate.json'); payload = json.loads(path.read_text())
    assert set(payload) == {'properties'}
    assert set(payload['properties']) == {'definition', 'connectionReferences'}
    assert payload['properties']['definition']['metadata'] == {'preserve': 'native-metadata'}
    assert payload['properties']['connectionReferences'] == native['properties']['connectionReferences']
    # Managed/export JSON may reorder keys; read-only verification must preserve bytes.
    reordered = json.dumps(payload, sort_keys=True)
    path.write_text(reordered)
    run = subprocess.run(cmd + ['--verify-existing'], capture_output=True, text=True, cwd=root)
    assert run.returncode == 0 and path.read_text() == reordered
    path.write_text('EXISTING-NATIVE-EVIDENCE')
    run = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    assert run.returncode == 1 and path.read_text() == 'EXISTING-NATIVE-EVIDENCE'
    run = subprocess.run(cmd + ['--verify-existing'], capture_output=True, text=True, cwd=root)
    assert run.returncode == 1 and path.read_text() == 'EXISTING-NATIVE-EVIDENCE'
    assert 'example.sharepoint' not in run.stderr


def test_interrupted_write_does_not_publish_truncated_output(tmp_path, monkeypatch):
    import scripts.f16_portability_candidates as tool
    outputs = {'a': {'candidate': {'preserve': True}}}
    with monkeypatch.context() as patch:
        def failed_sync(fd):
            raise OSError('simulated disk failure before publication')
        patch.setattr(tool.os, 'fsync', failed_sync)
        with pytest.raises(OSError): write_outputs(tmp_path, outputs)
    assert not list(tmp_path.iterdir())
    write_outputs(tmp_path, outputs)
    assert json.loads((tmp_path/'a-candidate.json').read_text()) == outputs['a']


def test_partial_batch_keeps_complete_files_and_exact_retry_resumes(tmp_path, monkeypatch):
    import scripts.f16_portability_candidates as tool
    outputs = {'a': {'candidate': {'first': True}}, 'b': {'candidate': {'second': True}}}
    link = tool.os.link
    with monkeypatch.context() as patch:
        def fail_second(source, destination):
            if destination.name == 'b-candidate.json':
                raise OSError('simulated publication failure')
            return link(source, destination)
        patch.setattr(tool.os, 'link', fail_second)
        with pytest.raises(OSError): write_outputs(tmp_path, outputs)
    first = tmp_path/'a-candidate.json'
    before = (first.read_bytes(), first.stat().st_ino, first.stat().st_mtime_ns)
    assert not (tmp_path/'b-candidate.json').exists()
    assert not list(tmp_path.glob('.f16-*'))
    write_outputs(tmp_path, outputs)
    assert (first.read_bytes(), first.stat().st_ino, first.stat().st_mtime_ns) == before
    tool.verify_outputs(tmp_path, outputs)


def test_concurrent_publication_never_overwrites_competing_output(tmp_path, monkeypatch):
    import scripts.f16_portability_candidates as tool
    outputs = {'a': {'candidate': {'preserve': True}}}
    link = tool.os.link
    def competing_writer(source, destination):
        destination.write_text('COMPETING EVIDENCE')
        return link(source, destination)
    monkeypatch.setattr(tool.os, 'link', competing_writer)
    with pytest.raises(ValueError, match='output_conflict'): write_outputs(tmp_path, outputs)
    assert (tmp_path/'a-candidate.json').read_text() == 'COMPETING EVIDENCE'
    assert not list(tmp_path.glob('.f16-*'))


def settings_fixture(tmp_path, *, f12=False):
    import hashlib
    from scripts.f16_portability_candidates import validate_deployment_settings
    package = tmp_path/'settings.zip'
    variables = {'comeet_SourceSiteUrl': 100000000, 'comeet_SourceListId': 100000000,
                 'comeet_Baseline': 100000003}
    if f12:
        variables = {'comeet_F12Baseline': 100000003, 'comeet_F12Selection': 100000003}
    connectors = {'sp': 'shared_sharepointonline', 'mail': 'shared_office365'}
    with ZipFile(package, 'w') as z:
        z.writestr('solution.xml', '<ImportExportXml><SolutionManifest><UniqueName>CHHHSClinicalDirectorsMeeting</UniqueName></SolutionManifest></ImportExportXml>')
        z.writestr('customizations.xml', '<ImportExportXml><connectionreferences>' + ''.join(
            '<connectionreference connectionreferencelogicalname="'+name+'"><connectorid>/providers/Microsoft.PowerApps/apis/'+api+'</connectorid></connectionreference>'
            for name, api in connectors.items()) + '</connectionreferences></ImportExportXml>')
        for name, kind in variables.items():
            z.writestr('environmentvariabledefinitions/'+name+'/environmentvariabledefinition.xml',
                       '<environmentvariabledefinition schemaname="'+name+'"><type>'+str(kind)+'</type></environmentvariabledefinition>')
    values = ['https://fictional-example.sharepoint.com/sites/test',
              'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', '{"fixture":true}']
    if f12: values = list(map(json.dumps, f12_values()))
    target = {'EnvironmentVariables': [{'SchemaName': n, 'Value': v, 'TypeId': variables[n]}
                                      for n, v in zip(variables, values)],
              'ConnectionReferences': [{'LogicalName': n, 'ConnectorId': '/providers/Microsoft.PowerApps/apis/'+api,
                                        'ConnectionId': 'target-'+n} for n, api in connectors.items()],
              'CopilotAgents': []}
    source = deepcopy(target)
    for row in source['ConnectionReferences']: row['ConnectionId'] = 'source-'+row['LogicalName']
    pin = hashlib.sha256(package.read_bytes()).hexdigest()
    def check(t=target, s=source, **pins):
        return validate_deployment_settings(package, pins.get('package_pin', pin), t,
            pins.get('target_pin', digest(t)), s, pins.get('source_pin', digest(s)))
    return package, target, source, check


def test_settings_exact_contract_and_input_preservation(tmp_path):
    _, target, source, check = settings_fixture(tmp_path); before = deepcopy((target, source))
    report = check()
    assert report['variables'] == 3 and report['references'] == 2
    assert report['f12_configuration']['status'] == 'NOT_APPLICABLE'
    assert report['native_deployment_ready'] is False
    assert (target, source) == before
    # Shared site URLs across purposes are legal; duplicate rows/IDs are not.


@pytest.mark.parametrize('change', ['missing_variable','extra_variable','duplicate_variable',
    'missing_reference','extra_reference','duplicate_reference','wrong_connector','wrong_type',
    'blank','whitespace','malformed_url','url_credentials','url_query','malformed_guid',
    'malformed_json','empty_json','duplicate_json_key','json_nan','duplicate_connection',
    'source_connection','source_connection_path','wrong_connection_path','invalid_connection',
    'settings_drift','source_drift','package_drift','source_connector','source_missing','unsupported_root'])
def test_settings_invalid_or_drifted_configuration_refused(tmp_path, change):
    _, target, source, check = settings_fixture(tmp_path)
    variables = target['EnvironmentVariables']; refs = target['ConnectionReferences']; pins = {}
    if change == 'missing_variable': variables.pop()
    if change == 'extra_variable': variables.append({'SchemaName':'comeet_Extra','Value':'x'})
    if change == 'duplicate_variable': variables.append(deepcopy(variables[0]))
    if change == 'missing_reference': refs.pop()
    if change == 'extra_reference': refs.append(dict(refs[0], LogicalName='extra'))
    if change == 'duplicate_reference': refs.append(deepcopy(refs[0]))
    if change == 'wrong_connector': refs[0]['ConnectorId'] = refs[1]['ConnectorId']
    if change == 'wrong_type': variables[0]['TypeId'] = 100000003
    if change == 'blank': variables[0]['Value'] = ''
    if change == 'whitespace': variables[0]['Value'] = '  '
    if change == 'malformed_url': variables[0]['Value'] = 'http://fictional-example.sharepoint.com'
    if change == 'url_credentials': variables[0]['Value'] = 'https://user:secret@fictional.invalid'
    if change == 'url_query': variables[0]['Value'] += '?token=fictional'
    if change == 'malformed_guid': variables[1]['Value'] = 'not-a-guid'
    if change == 'malformed_json': variables[2]['Value'] = '{'
    if change == 'empty_json': variables[2]['Value'] = '{}'
    if change == 'duplicate_json_key': variables[2]['Value'] = '{"a":1,"a":2}'
    if change == 'json_nan': variables[2]['Value'] = '{"a":NaN}'
    if change == 'duplicate_connection': refs[1]['ConnectionId'] = refs[0]['ConnectionId']
    if change == 'source_connection': refs[0]['ConnectionId'] = source['ConnectionReferences'][0]['ConnectionId']
    if change == 'source_connection_path': refs[0]['ConnectionId'] = refs[0]['ConnectorId']+'/connections/source-sp'
    if change == 'wrong_connection_path': refs[0]['ConnectionId'] = refs[1]['ConnectorId']+'/connections/target-sp'
    if change == 'invalid_connection': refs[0]['ConnectionId'] = '../source-sp'
    if change == 'settings_drift': pins['target_pin'] = '0'*64
    if change == 'source_drift': pins['source_pin'] = '0'*64
    if change == 'package_drift': pins['package_pin'] = '0'*64
    if change == 'source_connector': source['ConnectionReferences'][0]['ConnectorId'] = 'wrong'
    if change == 'source_missing': source['ConnectionReferences'].pop()
    if change == 'unsupported_root': target['Unexpected'] = []
    with pytest.raises(ValueError): check(**pins)


def test_source_guid_reuse_detects_case_and_hyphen_variations(tmp_path):
    _, target, source, check = settings_fixture(tmp_path)
    source['ConnectionReferences'][0]['ConnectionId'] = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
    target['ConnectionReferences'][0]['ConnectionId'] = 'AAAAAAAABBBBCCCCDDDDEEEEEEEEEEEE'
    with pytest.raises(ValueError, match='source_connection_reused'): check()


@pytest.mark.parametrize('f12', [False, True, 'native_transport'])
def test_settings_cli_is_readonly_and_failure_output_is_sanitised(tmp_path, f12):
    import hashlib, subprocess, sys
    from pathlib import Path
    package, target, source, _ = settings_fixture(tmp_path, f12=f12)
    if f12 == 'native_transport':
        baseline = json.loads(target['EnvironmentVariables'][0]['Value'])
        baseline['agenda']['F12MetadataType'] = baseline['agenda'].pop('@odata.type')
        target['EnvironmentVariables'][0]['Value'] = json.dumps(baseline)
    root = Path(__file__).resolve().parents[1]
    target_path = tmp_path/'target.json'; source_path = tmp_path/'source.json'
    target_path.write_text(json.dumps(target)); source_path.write_text(json.dumps(source))
    command = [sys.executable, str(root/'scripts/f16_portability_candidates.py'), '--package',str(package),
        '--package-sha256',hashlib.sha256(package.read_bytes()).hexdigest(),
        '--validate-settings',str(target_path),'--settings-sha256',digest(target),
        '--source-settings',str(source_path),'--source-settings-sha256',digest(source)]
    before = {p:p.read_bytes() for p in [package,target_path,source_path]}
    run = subprocess.run(command,capture_output=True,text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)['status'] == 'PASS_LOCAL_ONLY'
    assert all(p.read_bytes()==data for p,data in before.items())
    if f12:
        selection = json.loads(target['EnvironmentVariables'][1]['Value'])
        selection['subject'] = 'PRIVATE-MISMATCH'
        target['EnvironmentVariables'][1]['Value'] = json.dumps(selection)
        target_path.write_text(json.dumps(target))
        changed_command = command[:]
        changed_command[changed_command.index('--settings-sha256')+1] = digest(target)
        run = subprocess.run(changed_command,capture_output=True,text=True)
        assert run.returncode == 1 and not run.stdout
        assert 'PRIVATE' not in run.stderr and str(tmp_path) not in run.stderr
    target['EnvironmentVariables'][0]['Value']='PRIVATE-INVALID-VALUE'
    target_path.write_text(json.dumps(target))
    run = subprocess.run(command,capture_output=True,text=True)
    assert run.returncode == 1 and not run.stdout
    assert 'PRIVATE' not in run.stderr and str(tmp_path) not in run.stderr
    # Repeated JSON keys must fail before semantic hashing hides the duplicate.
    target_path.write_text('{"EnvironmentVariables":[],"EnvironmentVariables":[]}')
    run = subprocess.run(command,capture_output=True,text=True)
    assert run.returncode == 1


def test_preparation_pin_detects_valid_value_change_but_ignores_json_formatting(tmp_path):
    from scripts.f16_portability_candidates import strict_json
    _, target, _, check = settings_fixture(tmp_path)
    pin = digest(target)
    reformatted = strict_json(json.dumps(target, sort_keys=True, indent=4))
    assert check(t=reformatted, target_pin=pin)['status'] == 'PASS_LOCAL_ONLY'
    target['EnvironmentVariables'][0]['Value'] = 'https://fictional-example.sharepoint.com/sites/other'
    with pytest.raises(ValueError, match='settings_preparation_drift'): check(target_pin=pin)


def test_resource_path_connections_and_distinct_source_ids_pass(tmp_path):
    _, target, _, check = settings_fixture(tmp_path)
    for row in target['ConnectionReferences']:
        row['ConnectionId'] = row['ConnectorId']+'/connections/'+row['ConnectionId']
    assert check()['references'] == 2


def f12_values():
    baseline = {'event': {'id':'fictional-event', 'originalStart':'2099-01-01T06:00:00Z',
        'seriesMasterId':'fictional-series', 'iCalUId':'fictional-uid', 'subject':'FICTIONAL meeting',
        'type':'occurrence', 'organizer':{'emailAddress':{'address':'fictional@example.invalid'}},
        'start':{'dateTime':'2099-01-01T06:00:00','timeZone':'UTC'},
        'end':{'dateTime':'2099-01-01T07:00:00','timeZone':'UTC'},
        'changeKey':'fictional-change', 'lastModifiedDateTime':'2098-12-01T00:00:00Z','isCancelled':False},
        'agenda':{'id':'fictional-agenda','name':'FICTIONAL.docx','size':123,
        'lastModifiedDateTime':'2098-12-01T00:00:00Z','contentType':'application/docx',
        '@odata.type':'#microsoft.graph.fileAttachment','isInline':False},
        'checked_at':'2098-12-01T00:00:00Z','baseline_run_id':'fictional-run'}
    selection = {'window_start':'2099-01-01T06:00:00Z','window_end':'2099-01-01T07:00:00Z',
                 'subject':'FICTIONAL meeting','organizer':'fictional@example.invalid','agenda_name':'FICTIONAL.docx'}
    return baseline, selection


def test_f12_pair_validation_preserves_stored_strings_and_reports_actual_shape(tmp_path):
    _, target, source, check = settings_fixture(tmp_path, f12=True)
    before = deepcopy((target, source))
    report = check()
    assert report['f12_configuration']['status'] == 'PASS'
    assert report['f12_configuration']['comparison_fields'] == 21
    assert report['f12_configuration']['baseline_characters'] == len(target['EnvironmentVariables'][0]['Value'])
    assert (target, source) == before and report['native_deployment_ready'] is False


@pytest.mark.parametrize('change',['subject','organizer','agenda','bad_date','naive_date',
    'window','reversed_interval','missing_field','extra_field','missing_event','invalid_boolean',
    'negative_size','inline','timezone','oversized_stored_text'])
def test_f12_pair_rejects_mismatch_incomplete_and_invalid_configuration(tmp_path, change):
    _, target, _, check = settings_fixture(tmp_path, f12=True)
    b, s = f12_values()
    if change in ['subject','organizer']: s[change] = 'different-fictional-value'
    if change == 'agenda': s['agenda_name']='DIFFERENT.docx'
    if change == 'bad_date': b['checked_at']='not-a-date'
    if change == 'naive_date': b['checked_at']='2098-12-01T00:00:00'
    if change == 'window': s['window_start']='2099-01-01T06:30:00Z'
    if change == 'reversed_interval': b['event']['end']['dateTime']='2099-01-01T05:00:00'
    if change == 'missing_field': s.pop('agenda_name')
    if change == 'extra_field': s['extra']='fictional'
    if change == 'missing_event': b.pop('event')
    if change == 'invalid_boolean': b['event']['isCancelled']='false'
    if change == 'negative_size': b['agenda']['size']=-1
    if change == 'inline': b['agenda']['isInline']=True
    if change == 'timezone': b['event']['start']['timeZone']='Australia/Brisbane'
    target['EnvironmentVariables'][0]['Value']=json.dumps(b)
    target['EnvironmentVariables'][1]['Value']=json.dumps(s)
    if change == 'oversized_stored_text':
        # Valid JSON whose original whitespace exceeds the storage limit.
        target['EnvironmentVariables'][0]['Value']='{'+(' '*2001)+json.dumps(b)[1:]
    with pytest.raises(ValueError, match='f12_configuration_invalid'): check()


def test_f12_pair_is_required_when_package_declares_only_one_member(tmp_path):
    import hashlib
    from scripts.f16_portability_candidates import validate_deployment_settings
    package, target, source, _ = settings_fixture(tmp_path, f12=True)
    with ZipFile(package) as z: entries = {n:z.read(n) for n in z.namelist() if 'comeet_F12Selection/' not in n}
    with ZipFile(package,'w') as z:
        for n,data in entries.items(): z.writestr(n,data)
    for document in [target,source]: document['EnvironmentVariables'].pop()
    with pytest.raises(ValueError, match='incomplete_or_invalid_f12_pair'):
        validate_deployment_settings(package,hashlib.sha256(package.read_bytes()).hexdigest(),
                                     target,digest(target),source,digest(source))

@pytest.mark.parametrize('change', ['valid', 'oversized', 'both_keys', 'extra', 'mismatch'])
def test_native_f12_transport_preserves_original_size_and_strict_contract(tmp_path, change):
    _, target, _, check = settings_fixture(tmp_path, f12=True)
    b, _ = f12_values()
    b['agenda']['F12MetadataType'] = b['agenda'].pop('@odata.type')
    if change == 'both_keys': b['agenda']['@odata.type'] = '#microsoft.graph.fileAttachment'
    if change == 'extra': b['agenda']['unexpected'] = 'x'
    if change == 'mismatch': b['event']['subject'] = 'different'
    raw = json.dumps(b)[:-1] + (' ' * 2000 if change == 'oversized' else '  ') + '}'
    target['EnvironmentVariables'][0]['Value'] = raw
    before = deepcopy(target)
    if change == 'valid':
        report = check()['f12_configuration']
        assert report['status'] == 'PASS'
        assert report['baseline_characters'] == len(raw.encode('utf-16-le')) // 2
        assert report['baseline_transport'] == 'F12MetadataType'
    else:
        with pytest.raises(ValueError, match='f12_configuration_invalid'): check()
    assert target == before


@pytest.mark.parametrize('value', ['aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', "bad')/Files", '{}', 'not-a-guid'])
def test_output_library_id_requires_guid_and_exact_package_membership(tmp_path, value):
    import hashlib
    package, target, source, check = settings_fixture(tmp_path)
    original = next(row['SchemaName'] for row in target['EnvironmentVariables'] if row['SchemaName'].endswith('ListId'))
    replacement = 'comeet_F06OutputLibraryId'
    with ZipFile(package) as z:
        entries = {n: z.read(n) for n in z.namelist()}
    with ZipFile(package, 'w') as z:
        for name, data in entries.items():
            z.writestr(name.replace(original, replacement), data.replace(original.encode(), replacement.encode()))
    for settings in [target, source]:
        next(row for row in settings['EnvironmentVariables'] if row['SchemaName'] == original)['SchemaName'] = replacement
    next(row for row in target['EnvironmentVariables'] if row['SchemaName'] == replacement)['Value'] = value
    before = deepcopy((target, source))
    pin = hashlib.sha256(package.read_bytes()).hexdigest()
    if value == 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee':
        assert check(package_pin=pin)['status'] == 'PASS_LOCAL_ONLY'
    else:
        with pytest.raises(ValueError, match='invalid_list_id'): check(package_pin=pin)
    assert (target, source) == before


@pytest.mark.parametrize('case', ['match', 'missing', 'wrong_type', 'builtin'])
def test_exported_flow_variable_declarations_require_definition_closure(tmp_path, case):
    import hashlib
    package, target, _, check = settings_fixture(tmp_path)
    schema = next(row['SchemaName'] for row in target['EnvironmentVariables'] if row['SchemaName'].endswith('SiteUrl'))
    parameter = {'type': 'String', 'metadata': {'schemaName': schema}}
    if case == 'missing': parameter['metadata']['schemaName'] = 'comeet_F06OutputLibraryId'
    if case == 'wrong_type': parameter['type'] = 'Object'
    if case == 'builtin': parameter = {'type': 'SecureObject', 'defaultValue': {}}
    payload = {'properties': {'definition': {'parameters': {'selected': parameter}}}}
    with ZipFile(package, 'a') as z:
        z.writestr('Workflows/fictional.json', json.dumps(payload))
    before = package.read_bytes()
    pin = hashlib.sha256(before).hexdigest()
    if case in {'match', 'builtin'}:
        assert check(package_pin=pin)['status'] == 'PASS_LOCAL_ONLY'
    else:
        reason = 'workflow_variable_definition_missing' if case == 'missing' else 'workflow_variable_type_mismatch'
        with pytest.raises(ValueError, match=reason): check(package_pin=pin)
    assert package.read_bytes() == before
