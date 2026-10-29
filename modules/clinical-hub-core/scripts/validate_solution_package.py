#!/usr/bin/env python3
"""Read-only checks for the cloud-flow subset of a Power Platform solution ZIP.

No extraction, credentials, tenant calls or raw definition values in output.
PASS means scoped package consistency, never deployment or runtime acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import sys
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from powerplatform_validation import loads as strict_loads, validate_members, inspect_zip


FLOW_FILE = re.compile(r"^Workflows/.*-([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})\.json$", re.I)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()



# Connector parameter keys only: this is a configuration review aid, not a
# content/secrets scanner. Numeric action positions avoid leaking action labels.
CONFIG_KEYS = {'dataset': 'site', 'table': 'list_or_table', 'folderPath': 'folder',
               'calendarId': 'calendar', 'siteAddress': 'site', 'Uri': 'endpoint'}
PARAMETER_EXPRESSION = re.compile(r"^@parameters\('[^']+'\)$")


def configuration_review(definition: dict) -> dict:
    findings, parameter_references = [], 0

    def walk(graph, location):
        nonlocal parameter_references
        for index, node in enumerate(graph.values()):
            here = f'{location}/{index}'
            if node.get('type') in {'OpenApiConnection', 'OpenApiConnectionWebhook'}:
                parameters = node.get('inputs', {}).get('parameters', {})
                for key, kind in CONFIG_KEYS.items():
                    value = parameters.get(key)
                    if not isinstance(value, str) or not value.strip():
                        continue
                    if PARAMETER_EXPRESSION.fullmatch(value):
                        parameter_references += 1
                        continue
                    findings.append({'location': f'{here}/inputs/parameters/{key}',
                                     'kind': kind,
                                     'form': 'expression_requires_review' if value.startswith('@') or '@{' in value else 'literal_requires_review'})
            walk(node.get('actions', {}), f'{here}/actions')
            walk(node.get('else', {}).get('actions', {}), f'{here}/else/actions')
            for branch_index, branch in enumerate(node.get('cases', {}).values()):
                walk(branch.get('actions', {}), f'{here}/cases/{branch_index}/actions')
            walk(node.get('default', {}).get('actions', {}), f'{here}/default/actions')

    walk(definition['triggers'], 'triggers')
    walk(definition['actions'], 'actions')
    return {'status': 'REVIEW_REQUIRED' if findings else 'NO_CANDIDATES_IN_SCOPE',
            'findings': findings, 'parameter_reference_count': parameter_references,
            'limit': 'Selected executable connector parameter keys only. Values omitted. Numeric locations refer to action order in this exact package, not stable IDs. Parameter references are not verified environment variables; expressions, defaults, other keys and payloads require separate review. No automatic substitution or disclosure clearance.'}


def inspect_package(path: Path) -> dict:
    errors, flows = [], {}
    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError('duplicate_archive_entries')
            if archive.testzip() is not None:
                raise ValueError('archive_crc_failure')
            if not {'solution.xml', 'customizations.xml'}.issubset(names):
                raise ValueError('not_a_solution_package')
            manifest = ET.fromstring(archive.read('solution.xml')).find('SolutionManifest')
            if manifest is None:
                raise ValueError('missing_solution_manifest')
            custom = ET.fromstring(archive.read('customizations.xml'))
            assurance = validate_members({name: archive.read(name) for name in names})
            if assurance['status'] == 'FAIL':
                return {'status': 'FAIL', 'errors': sorted({c['check'] for c in assurance['checks'] if c['outcome'] == 'fail'}), 'flows': {}, 'assurance': assurance}
            references, reference_hashes = {}, {}
            for node in custom.findall('.//connectionreference'):
                logical = node.get('connectionreferencelogicalname')
                if not logical or logical in references:
                    raise ValueError('missing_or_duplicate_reference_name')
                references[logical] = node.findtext('connectorid', '')
                reference_hashes[logical] = digest({field: node.findtext(field) for field in
                    ('connectorid', 'connectionid', 'promptingbehavior', 'iscustomizable', 'statecode', 'statuscode')})
            roots = [n.get('id', '').strip('{}').lower() for n in manifest.findall('.//RootComponent') if n.get('type') == '29']
            if len(roots) != len(set(roots)):
                errors.append('duplicate_declared_workflow')
            for name in names:
                if not name.startswith('Workflows/') or not name.endswith('.json'):
                    continue
                match = FLOW_FILE.match(name)
                if not match:
                    raise ValueError('unrecognised_workflow_filename')
                flow_id = match[1].lower()
                if flow_id in flows:
                    raise ValueError('duplicate_workflow_definition')
                properties = strict_loads(archive.read(name))['properties']
                definition = properties['definition']
                if not isinstance(definition.get('triggers'), dict) or not definition['triggers'] or not isinstance(definition.get('actions'), dict):
                    raise ValueError('invalid_trigger_action_graph')
                bindings = properties.get('connectionReferences', {})
                if not isinstance(bindings, dict):
                    raise ValueError('invalid_connection_references')
                for alias, binding in bindings.items():
                    logical = binding.get('connection', {}).get('connectionReferenceLogicalName')
                    api = binding.get('api', {}).get('name')
                    if not logical or logical not in references:
                        errors.append(f'{flow_id}:unresolved_connection_reference')
                    elif not api or references[logical].rsplit('/', 1)[-1] != api:
                        errors.append(f'{flow_id}:connector_mismatch')
                # Walk executable containers only, never literal action inputs.
                def visit_graph(graph):
                    for node in graph.values():
                        if node.get('type') in {'OpenApiConnection', 'OpenApiConnectionWebhook'}:
                            host = node.get('inputs', {}).get('host', {})
                            alias = host.get('connectionName') or host.get('connectionReferenceName')
                            if alias not in bindings:
                                errors.append(f'{flow_id}:unbound_connector_host')
                        visit_graph(node.get('actions', {}))
                        visit_graph(node.get('else', {}).get('actions', {}))
                        for branch in node.get('cases', {}).values():
                            visit_graph(branch.get('actions', {}))
                        visit_graph(node.get('default', {}).get('actions', {}))
                visit_graph(definition['triggers'])
                visit_graph(definition['actions'])
                flows[flow_id] = {'graph_sha256': digest({'triggers': definition['triggers'], 'actions': definition['actions']}), 'bindings_sha256': digest(bindings), 'parameters_sha256': digest(definition.get('parameters', {})), 'configuration_review': configuration_review(definition)}
            if set(roots) != set(flows):
                errors.append('declared_workflow_definition_mismatch')
            if not flows:
                errors.append('no_cloud_flow_definitions')
            return {'status': 'FAIL' if errors else 'PASS', 'assurance': assurance, 'deploymentReady': False, 'solution': manifest.findtext('UniqueName'), 'version': manifest.findtext('Version'), 'managed': manifest.findtext('Managed'), 'flows': flows, 'reference_count': len(references), 'reference_hashes': reference_hashes, 'errors': sorted(set(errors)), 'limit': 'Cloud-flow package consistency only; other components, disclosure, target bindings, state, access, runtime, recovery and acceptance not verified.'}
    except (OSError, BadZipFile, ET.ParseError, json.JSONDecodeError, KeyError, TypeError, AttributeError, ValueError):
        # Avoid echoing archive content or exceptions containing private values.
        return {'status': 'FAIL', 'errors': ['invalid_or_unsupported_package'], 'flows': {}, 'limit': 'No tenant or runtime verification.'}


def compare_packages(current: dict, baseline: dict) -> dict:
    if current['status'] != 'PASS' or baseline['status'] != 'PASS':
        return {'status': 'NOT_COMPARED', 'reason': 'both_packages_must_pass'}
    old, new = baseline['flows'], current['flows']
    old_refs, new_refs = baseline['reference_hashes'], current['reference_hashes']
    return {'status': 'COMPARED', 'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys()), 'changed': sorted(k for k in old.keys() & new.keys() if any(old[k][field] != new[k][field] for field in ('graph_sha256', 'bindings_sha256', 'parameters_sha256'))), 'references': {'added': sorted(new_refs.keys() - old_refs.keys()), 'removed': sorted(old_refs.keys() - new_refs.keys()), 'changed': sorted(k for k in old_refs.keys() & new_refs.keys() if old_refs[k] != new_refs[k])}, 'limit': 'Trigger/action, definition-parameter, binding and selected exported connection-reference field hashes only; other package metadata and non-flow components excluded. Differences require review.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--deployment-settings', type=Path)
    args = parser.parse_args()
    result = inspect_package(args.package)
    if args.deployment_settings:
        result['assurance'] = inspect_zip(args.package, args.deployment_settings)
        if result['assurance']['status'] == 'FAIL':
            result['status'] = 'FAIL'
    if args.baseline:
        result['comparison'] = compare_packages(result, inspect_package(args.baseline))
    print(json.dumps(result, indent=2))
    return int(result['status'] != 'PASS' or result.get('comparison', {}).get('status') == 'NOT_COMPARED')


if __name__ == '__main__':
    raise SystemExit(main())
