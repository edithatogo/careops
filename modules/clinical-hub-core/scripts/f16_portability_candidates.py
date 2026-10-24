"""Local site-binding candidates and pinned deployment-settings checks. No tenant calls.

The proposal preserves source defaults; it is not target/disclosure qualification.
Do not patch solution ZIPs or submit an exported document as a native preimage.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from zipfile import BadZipFile, ZipFile
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def action_paths(definition):
    """Only executable action containers; never recurse into literal payloads."""
    found = {}

    def walk(graph, path):
        require(isinstance(graph, dict), 'invalid_action_graph')
        for name, action in graph.items():
            require(isinstance(action, dict), 'invalid_action')
            here = path + (name,)
            found[here] = action
            for key in ('actions',):
                if key in action:
                    walk(action[key], here + (key,))
            for key in ('else', 'default'):
                if key in action:
                    walk(action[key].get('actions', {}), here + (key, 'actions'))
            for case, branch in action.get('cases', {}).items():
                walk(branch.get('actions', {}), here + ('cases', case, 'actions'))

    walk(definition.get('triggers', {}), ('triggers',))
    walk(definition.get('actions', {}), ('actions',))
    return found


def site_paths(definition):
    return {path + ('inputs', 'parameters', 'dataset'): action
            for path, action in action_paths(definition).items()
            if action.get('type') in ('OpenApiConnection', 'OpenApiConnectionWebhook')
            and 'dataset' in action.get('inputs', {}).get('parameters', {})}


def append_url_paths(definition):
    return {path + ('inputs', 'value', 'source_url'): action
            for path, action in action_paths(definition).items()
            if action.get('type') == 'AppendToArrayVariable'
            and isinstance(action.get('inputs', {}).get('value'), dict)
            and isinstance(action['inputs']['value'].get('source_url'), str)}


def locate(value, path):
    for part in path:
        value = value[part]
    return value


def binding_identity(binding):
    """Qualified export and Flow RP shapes; preserve the original record verbatim."""
    if 'api' in binding or 'connection' in binding or 'runtimeSource' in binding:
        require(not any(k in binding for k in ('apiName', 'source', 'connectionReferenceLogicalName')),
                'ambiguous_connection_shape')
        return (binding.get('api', {}).get('name'),
                binding.get('connection', {}).get('connectionReferenceLogicalName'),
                binding.get('runtimeSource', '').lower())
    api = binding.get('apiName', '')
    return ('shared_' + api if api and not api.startswith('shared_') else api,
            binding.get('connectionReferenceLogicalName'), binding.get('source', '').lower())


def build_candidate(properties, expected_sha256, selections, link_selections=None):
    """Pin complete properties, edit selected datasets, prove exact inverse parity."""
    require(digest(properties) == expected_sha256, 'source_drift')
    require(isinstance(selections, list) and selections, 'empty_selection')
    result = deepcopy(properties)
    definition = result['definition']
    original = properties['definition']
    paths = site_paths(original)
    changed, added, seen = [], {}, set()
    declarations = definition.setdefault('parameters', {})
    for selected in selections:
        path = tuple(selected['path'])
        require(path in paths and path not in seen, 'invalid_or_duplicate_selected_path')
        seen.add(path)
        action = paths[path]
        host = action['inputs']['host']
        alias = host.get('connectionName') or host.get('connectionReferenceName')
        binding = properties.get('connectionReferences', {}).get(alias, {})
        api, logical, runtime = binding_identity(binding)
        require(host.get('apiId') == '/providers/Microsoft.PowerApps/apis/shared_sharepointonline'
                and api == 'shared_sharepointonline' and runtime == 'invoker' and logical,
                'unqualified_sharepoint_invoker_binding')
        literal = locate(original, path)
        require(isinstance(literal, str) and literal.startswith('https://')
                and '@' not in literal and literal == selected['expected_value'], 'selected_value_drift')
        name, declaration = selected['parameter_name'], selected['parameter']
        schema = declaration.get('metadata', {}).get('schemaName', '')
        require(re.fullmatch(r'comeet_[A-Za-z0-9_]+', schema) is not None
                and name.endswith(' (' + schema + ')')
                and "'" not in name and '\n' not in name, 'invalid_environment_parameter_name')
        require(declaration.get('type') == 'String'
                and declaration.get('defaultValue') == literal, 'source_default_must_match')
        require(not any(k != name and v.get('metadata', {}).get('schemaName') == schema
                        for k, v in declarations.items()), 'duplicate_schema_alias')
        if name in declarations:
            require(declarations[name] == declaration, 'parameter_collision')
        else:
            declarations[name] = deepcopy(declaration)
            added[name] = deepcopy(declaration)
        expression = "@parameters('" + name + "')"
        locate(definition, path[:-1])[path[-1]] = expression
        changed.append({'path': list(path), 'before': literal, 'after': expression})

    if link_selections is not None:
        require(isinstance(link_selections, list) and link_selections, 'empty_link_selection')
        allowed = append_url_paths(original)
        selected_names = {x['parameter_name'] for x in selections}
        link_seen, required = set(), set()
        for selected in link_selections:
            path, name = tuple(selected['path']), selected['parameter_name']
            require(path in allowed and path not in link_seen and name in selected_names,
                    'invalid_or_duplicate_link_path')
            link_seen.add(path)
            base = declarations[name]['defaultValue']
            require(base == selected['expected_base'] and "'" not in base, 'link_base_drift')
            expression = locate(original, path)
            prefix = "@concat('" + base + "',"
            require(expression == selected['expected_value'] and expression.startswith(prefix),
                    'link_expression_drift')
            replacement = "@concat(parameters('" + name + "')," + expression[len(prefix):]
            locate(definition, path[:-1])[path[-1]] = replacement
            changed.append({'path': list(path), 'before': expression, 'after': replacement})
            required.update(p for p in allowed if base in locate(original, p))
        require(link_seen == required, 'incomplete_link_coverage')

    inverse = deepcopy(result)
    for change in changed:
        locate(inverse['definition'], change['path'][:-1])[change['path'][-1]] = change['before']
    for name in added:
        del inverse['definition']['parameters'][name]
    if 'parameters' not in original:
        del inverse['definition']['parameters']
    require(inverse == properties, 'unexpected_preservation_delta')
    return result, {'source_sha256': expected_sha256, 'candidate_sha256': digest(result),
                    'changes': changed, 'added_parameters': added,
                    'preservation': 'Exact inverse equals complete source properties',
                    'native_deployment_ready': False,
                    'limits': 'Selected site binding proposal only; source defaults retained. '
                              'Native schema/preimage/state/access, remaining URI/list/payload '
                              'configuration, import and recovery acceptance unverified.'}


def build_package_candidates(package, plan):
    package_bytes = Path(package).read_bytes()
    require(hashlib.sha256(package_bytes).hexdigest() == plan['package_sha256'],
            'package_drift')
    outputs = {}
    with ZipFile(BytesIO(package_bytes)) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())) and archive.testzip() is None,
                'invalid_archive')
        for item in plan['flows']:
            fid = item['workflow_id']
            require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', fid) is not None
                    and fid not in outputs, 'invalid_or_duplicate_workflow')
            names = [n for n in archive.namelist() if n.startswith('Workflows/')
                     and n.lower().endswith('-' + fid + '.json')]
            require(len(names) == 1, 'workflow_not_unique')
            document = json.loads(archive.read(names[0]))
            candidate, changes = build_candidate(document['properties'], item['expected_sha256'],
                                                 item['selections'], item.get('link_selections'))
            output = deepcopy(document)
            output['properties'] = candidate
            outputs[fid] = {'candidate': output, 'review': changes}
    require(outputs, 'empty_flow_selection')
    return outputs


def native_payload(native, expected_native_sha256, workflow_id, source_properties, selections,
                   link_selections=None):
    """Rebase selected edits on a pinned complete native preimage, preserving metadata."""
    # The shared native helper uses sibling imports when launched as a script.
    # Support that existing contract for package callers without changing the
    # helper or leaving a search-path mutation behind.
    previous_path = sys.path[:]
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        if __package__:
            from .flow_definition import definition as normalise
        else:
            from flow_definition import definition as normalise
    finally:
        sys.path[:] = previous_path
    require(digest(native) == expected_native_sha256, 'native_preimage_drift')
    require(isinstance(native.get('properties'), dict), 'not_a_native_flow_object')
    props = native['properties']
    require(props.get('state') == 'Stopped' and not props.get('isManaged')
            and props.get('workflowEntityId', '').lower() == workflow_id,
            'native_identity_or_state_mismatch')
    require(normalise(props['definition']) == normalise(source_properties['definition']),
            'native_definition_drift')
    for alias, source in source_properties.get('connectionReferences', {}).items():
        current = props.get('connectionReferences', {}).get(alias, {})
        require(binding_identity(current) == binding_identity(source),
                'native_reference_drift')
    require(set(props.get('connectionReferences', {})) == set(source_properties.get('connectionReferences', {})),
            'native_reference_drift')
    candidate, _ = build_candidate(props, digest(props), selections, link_selections)
    return {'properties': {k: candidate[k] for k in ('definition', 'connectionReferences')}}


def write_outputs(folder, outputs):
    """Preflight every collision before writing; exact reruns reuse existing bytes."""
    folder = Path(folder)
    encoded = {folder / (fid + '-candidate.json'): json.dumps(result, indent=2) + '\n'
               for fid, result in outputs.items()}
    for path, data in encoded.items():
        require(not path.exists() or path.read_text() == data, 'output_conflict')
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    for path, data in encoded.items():
        # Recheck after preflight: another writer may have published meanwhile.
        if path.exists():
            require(path.read_text() == data, 'output_conflict')
            continue
        temporary = None
        try:
            # Write on the same filesystem, then publish without replacing a name.
            # A failed write leaves no truncated final file; completed siblings are
            # retained and an exact retry can finish the remainder of the batch.
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=folder, prefix='.f16-',
                                             suffix='.tmp', delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                require(path.read_text() == data, 'output_conflict')
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def verify_outputs(folder, outputs):
    """Read-only semantic parity across package modes; never rewrite retained bytes."""
    for fid, result in outputs.items():
        path = Path(folder) / (fid + '-candidate.json')
        require(path.is_file() and json.loads(path.read_text()) == result, 'existing_candidate_drift')



def strict_json(text):
    """Reject duplicate object keys and non-JSON constants instead of losing data."""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('invalid_json_constant')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def connection_token(value, connector):
    require(isinstance(value, str) and value and value == value.strip(), 'invalid_connection_id')
    if value.startswith('/'):
        prefix = '/providers/Microsoft.PowerApps/apis/' + connector + '/connections/'
        require(value.startswith(prefix), 'connection_id_connector_mismatch')
        value = value[len(prefix):]
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,199}', value) is not None,
            'invalid_connection_id')
    # GUIDs may be represented with or without hyphens; compare both consistently.
    compact = value.replace('-', '').lower()
    return compact if re.fullmatch(r'[0-9a-f]{32}', compact) else value.lower()


def validate_deployment_settings(package, package_sha256, settings, settings_sha256,
                                 source_settings, source_settings_sha256):
    """Read-only local target preflight; never establishes live ownership/access."""
    raw = Path(package).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == package_sha256, 'package_drift')
    require(digest(settings) == settings_sha256, 'settings_preparation_drift')
    require(digest(source_settings) == source_settings_sha256, 'source_settings_drift')
    definitions, references = {}, {}
    with ZipFile(BytesIO(raw)) as z:
        names = z.namelist()
        require(len(names) == len(set(names)) and z.testzip() is None, 'invalid_archive')
        manifest = ET.fromstring(z.read('solution.xml')).find('SolutionManifest')
        require(manifest is not None and manifest.findtext('UniqueName') == 'CHHHSClinicalDirectorsMeeting',
                'unexpected_solution')
        custom = ET.fromstring(z.read('customizations.xml'))
        for node in custom.findall('.//connectionreference'):
            name, connector = node.get('connectionreferencelogicalname'), node.findtext('connectorid')
            require(name and name not in references and isinstance(connector, str)
                    and re.fullmatch(r'/providers/Microsoft.PowerApps/apis/shared_[A-Za-z0-9_]+', connector),
                    'invalid_package_reference')
            references[name] = connector
        for name in names:
            if name.startswith('environmentvariabledefinitions/') and name.endswith('/environmentvariabledefinition.xml'):
                node = ET.fromstring(z.read(name)); schema = node.get('schemaname')
                require(node.tag == 'environmentvariabledefinition' and schema and schema not in definitions
                        and name == 'environmentvariabledefinitions/' + schema + '/environmentvariabledefinition.xml',
                        'invalid_package_variable')
                definitions[schema] = int(node.findtext('type'))
        for name in names:
            if name.startswith('Workflows/') and name.endswith('.json'):
                workflow = strict_json(z.read(name).decode('utf-8-sig'))
                parameters = workflow.get('properties', {}).get('definition', {}).get('parameters', {})
                require(isinstance(parameters, dict), 'invalid_workflow_parameters')
                for parameter in parameters.values():
                    require(isinstance(parameter, dict), 'invalid_workflow_parameters')
                    metadata = parameter.get('metadata', {})
                    require(isinstance(metadata, dict), 'invalid_workflow_parameters')
                    schema = metadata.get('schemaName')
                    if schema is None:
                        continue
                    require(isinstance(schema, str) and schema in definitions,
                            'workflow_variable_definition_missing')
                    expected_type = {100000000: 'String', 100000003: 'Object'}.get(definitions[schema])
                    require(expected_type is not None and parameter.get('type') == expected_type,
                            'workflow_variable_type_mismatch')
    require(definitions and references, 'missing_package_settings_contract')

    def rows(document, section, key, expected):
        require(isinstance(document, dict) and set(document) <= {'EnvironmentVariables', 'ConnectionReferences', 'CopilotAgents'}
                and document.get('CopilotAgents', []) == [], 'unsupported_settings_shape')
        values = document.get(section)
        require(isinstance(values, list), 'invalid_settings_section')
        result = {}
        for row in values:
            require(isinstance(row, dict) and isinstance(row.get(key), str)
                    and row[key] not in result, 'duplicate_or_invalid_setting')
            result[row[key]] = row
        require(set(result) == set(expected), 'settings_membership_mismatch')
        return result

    target_vars = rows(settings, 'EnvironmentVariables', 'SchemaName', definitions)
    target_refs = rows(settings, 'ConnectionReferences', 'LogicalName', references)
    rows(source_settings, 'EnvironmentVariables', 'SchemaName', definitions)
    source_refs = rows(source_settings, 'ConnectionReferences', 'LogicalName', references)
    source_ids, target_ids = set(), set()
    for name, connector in references.items():
        source = source_refs[name]
        require(source.get('ConnectorId') == connector, 'source_connector_mismatch')
        source_ids.add(connection_token(source.get('ConnectionId'), connector.rsplit('/', 1)[-1]))
    for name, connector in references.items():
        row = target_refs[name]
        require(row.get('ConnectorId') == connector, 'target_connector_mismatch')
        token = connection_token(row.get('ConnectionId'), connector.rsplit('/', 1)[-1])
        require(token not in source_ids, 'source_connection_reused')
        require(token not in target_ids, 'duplicate_target_connection')
        target_ids.add(token)
    for schema, kind in definitions.items():
        row = target_vars[schema]; value = row.get('Value')
        require('TypeId' not in row or type(row['TypeId']) is int and row['TypeId'] == kind,
                'variable_type_mismatch')
        require(isinstance(value, str) and value.strip() and value == value.strip(), 'blank_or_invalid_value')
        if kind == 100000003:
            parsed = strict_json(value)
            require(isinstance(parsed, dict) and parsed, 'empty_or_invalid_json_value')
        elif kind == 100000000:
            if schema.endswith('SiteUrl'):
                url = urlsplit(value)
                require(url.scheme == 'https' and url.hostname and url.hostname.endswith('.sharepoint.com')
                        and not url.username and not url.password and not url.query and not url.fragment
                        and url.port in (None, 443) and not any(c.isspace() for c in value), 'invalid_site_url')
            elif schema.endswith(('ListId', 'LibraryId')):
                require(re.fullmatch(r'[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}', value),
                        'invalid_list_id')
            else:
                raise ValueError('unsupported_variable_validation')
        else:
            raise ValueError('unsupported_variable_type')
    f12_names = {'comeet_F12Baseline', 'comeet_F12Selection'}
    f12_check = {'status': 'NOT_APPLICABLE'}
    if f12_names & definitions.keys():
        require(f12_names <= definitions.keys() and
                all(definitions[name] == 100000003 for name in f12_names),
                'incomplete_or_invalid_f12_pair')
        if __package__:
            from .f12_configuration import validate_configuration, LIMIT
        else:
            from f12_configuration import validate_configuration, LIMIT
        try:
            baseline_raw = target_vars['comeet_F12Baseline']['Value']
            selection_raw = target_vars['comeet_F12Selection']['Value']
            baseline = json.loads(baseline_raw)
            if isinstance(baseline, dict) and isinstance(baseline.get('agenda'), dict) and 'F12MetadataType' in baseline['agenda']:
                # Native transport renames the annotation key. Measure ORIGINAL
                # stored text before lossless decoding; never hide whitespace.
                units = len(baseline_raw.encode('utf-16-le')) // 2
                require(units <= LIMIT, 'f12_configuration_invalid')
                if not __package__:
                    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                from scripts.f12_portable_definition import baseline_transport
                decoded = baseline_transport(baseline, decode=True)
                f12_check = validate_configuration(json.dumps(decoded, separators=(',', ':')), selection_raw)
                f12_check['baseline_characters'] = units
                f12_check['baseline_transport'] = 'F12MetadataType'
            else:
                f12_check = validate_configuration(baseline_raw, selection_raw)
        except ValueError:
            raise ValueError('f12_configuration_invalid') from None
    return {'status': 'PASS_LOCAL_ONLY', 'variables': len(definitions), 'references': len(references),
            'f12_configuration': f12_check,
            'settings_sha256': settings_sha256, 'package_sha256': package_sha256,
            'native_deployment_ready': False,
            'limits': 'Pinned local contract/format checks only; live connector identity/owner/status, '
                      'target resource authority, F12 source fidelity/native binding, layers and recovery require native qualification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--native-preimage', type=Path)
    parser.add_argument('--native-sha256')
    parser.add_argument('--workflow-id')
    parser.add_argument('--verify-existing', action='store_true',
                        help='Compare retained JSON semantically without writing or changing its formatting')
    parser.add_argument('--validate-settings', type=Path)
    parser.add_argument('--package-sha256')
    parser.add_argument('--settings-sha256', help='Semantic digest recorded at recovery preparation, not a newly accepted replacement')
    parser.add_argument('--source-settings', type=Path)
    parser.add_argument('--source-settings-sha256')
    args = parser.parse_args()
    try:
        if args.validate_settings:
            require(all((args.package_sha256, args.settings_sha256, args.source_settings,
                         args.source_settings_sha256)), 'settings_pins_required')
            require(not any((args.plan, args.output, args.native_preimage, args.native_sha256,
                             args.workflow_id, args.verify_existing)), 'mixed_operation_modes')
            result = validate_deployment_settings(args.package, args.package_sha256,
                strict_json(args.validate_settings.read_text()), args.settings_sha256,
                strict_json(args.source_settings.read_text()), args.source_settings_sha256)
            print(json.dumps(result))
            return
        require(args.plan and args.output and not any((args.package_sha256, args.settings_sha256,
                args.source_settings, args.source_settings_sha256)), 'candidate_inputs_required')
        plan = json.loads(args.plan.read_text())
        outputs = build_package_candidates(args.package, plan)
        count = len(outputs)
        selected_count = sum(len(item['selections']) for item in plan['flows'])
        link_count = sum(len(item.get('link_selections', [])) for item in plan['flows'])
        if any((args.native_preimage, args.native_sha256, args.workflow_id)):
            require(all((args.native_preimage, args.native_sha256, args.workflow_id)), 'native_inputs_incomplete')
            item = next(x for x in plan['flows'] if x['workflow_id'] == args.workflow_id)
            # Reconstruct the original selected properties by reversing the recorded delta.
            source = deepcopy(outputs[args.workflow_id]['candidate']['properties'])
            review = outputs[args.workflow_id]['review']
            for change in review['changes']:
                locate(source['definition'], change['path'][:-1])[change['path'][-1]] = change['before']
            for name in review['added_parameters']:
                del source['definition']['parameters'][name]
            if digest(source) != item['expected_sha256'] and not source['definition']['parameters']:
                del source['definition']['parameters']
            require(digest(source) == item['expected_sha256'], 'source_reconstruction_drift')
            payload = native_payload(json.loads(args.native_preimage.read_text()), args.native_sha256,
                                     args.workflow_id, source, item['selections'], item.get('link_selections'))
            selected_outputs = {args.workflow_id: payload}
            count, selected_count = 1, len(item['selections'])
            link_count = len(item.get('link_selections', []))
        else:
            selected_outputs = outputs
        if args.verify_existing:
            verify_outputs(args.output, selected_outputs)
        else:
            write_outputs(args.output, selected_outputs)
    except (ValueError, KeyError, TypeError, OSError, BadZipFile, StopIteration, RuntimeError, ET.ParseError):
        # Never emit input values, private paths, server responses or credentials.
        parser.exit(1, 'Local operation refused; inspect private inputs/pins/collisions.\n')
    print(json.dumps({'status': 'PASS_LOCAL_ONLY', 'flows': count,
                      'selected_site_arguments': selected_count,
                      'selected_link_bases': link_count,
                      'native_deployment_ready': False}))


if __name__ == '__main__':
    main()
