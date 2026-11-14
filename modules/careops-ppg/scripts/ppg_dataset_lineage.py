"""Build a private dataset-use manifest from an extracted solution and catalogue receipt."""
if __package__:
    from .ppg_binding_resolution import action_binding
    from .ppg_run_read_evidence import apply_run_reads
else:
    from ppg_binding_resolution import action_binding
    from ppg_run_read_evidence import apply_run_reads
import argparse
import os
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

MAX_XML_BYTES = 16 * 1024 * 1024


class _RejectDeclarations(ET.TreeBuilder):
    def doctype(self, name, public_id, system_id):
        raise ValueError('XML DTD declarations are unsupported')


def _parse_xml(path):
    """Parse one bounded XML file while rejecting DTDs and entity declarations."""
    with Path(path).open('rb') as stream:
        data = stream.read(MAX_XML_BYTES + 1)
    if len(data) > MAX_XML_BYTES:
        raise ValueError(f'XML input exceeds {MAX_XML_BYTES} bytes')
    return ET.fromstring(data, parser=ET.XMLParser(target=_RejectDeclarations()))

GUID = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', re.I)
PARAM = re.compile(r"parameters\('([^']+)'\)")
REF = re.compile(r"(variables|outputs|body)\('([^']+)'\)")
ROLE_SOURCE = {
    'dataset-catalogue': ('Secondary', 'Site inventory and installation object bindings'),
    'source-update-leads': ('Secondary', 'Publisher feeds, routed newsletters and internal safety register'),
    'catalogue': ('Secondary', 'Source register and reviewed identity ledger'),
    'hospital-dataset-captures': ('Primary', 'Publisher hospital API responses and immutable response files'),
    'hospital-facilities': ('Secondary', 'Facilities API response in Hospital Dataset Captures'),
    'hospital-current-metrics': ('Secondary', 'Current metrics API response in Hospital Dataset Captures'),
    'hospital-busyness-trends': ('Secondary', 'Busyness API response in Hospital Dataset Captures'),
    'follow-up-digest-previews': ('Aggregate', 'Follow-up requests and context records'),
    'workspace-status': ('Aggregate', 'Workbench status projection from operational records'),
    'responsibility-snapshots': ('Secondary', 'Role appointments and responsibility assignments'),
    'review-queue': ('Secondary', 'Selected catalogue and review records'),
    'reconciled-guide-revisions': ('Secondary', 'Source guide revisions and reconciliation'),
}


def nodes(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, dict) and 'type' in child and 'inputs' in child:
                yield key, child
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def build(export, records, overrides, provenance=None, bindings=None):
    if bindings is not None and not (isinstance(bindings.get('site'), str) and
            all(isinstance(bindings.get(k), dict) for k in ('files', 'folders'))):
        raise ValueError('Binding evidence requires site, files and folders')
    variables = {}
    for xml in export.glob('environmentvariabledefinitions/*/environmentvariabledefinition.xml'):
        root = _parse_xml(xml)
        variables[root.get('schemaname')] = root.findtext('defaultvalue') or ''
    variables.update(overrides)
    names = {n.get('WorkflowId','').strip('{}').lower(): n.get('Name') for n in
             _parse_xml(export/'customizations.xml').iter('Workflow')}
    rows, gaps = {}, []
    for r in records:
        key, scope = r['ProductKey'], r['DatasetScope']
        if key in ROLE_SOURCE:
            role, source = ROLE_SOURCE[key]
        elif key in {
            'assurance-events', 'consultation-and-handoff-events', 'readiness-events',
            'follow-up-history', 'accreditation-request-events', 'accreditation-decision-events',
        }:
            role, source = 'Primary', 'Recorded workbench events and decisions'
        elif key in {
            'review-contexts','guide-review-contexts','review-annotations','review-section-proposals',
            'accreditation-assessment-narratives','accreditation-improvement-cases','accreditation-requests',
            'follow-up-requests','follow-up-contexts','review-criteria','review-decision-options',
            'accreditation-responsibilities','responsibility-assignments','responsibility-handovers',
            'role-appointments','organisational-roles','structured-content','change-and-impact',
        }:
            role, source = 'Primary', 'Workbench-authored ' + key.replace('-', ' ')
        elif key in {'requirement-assessments','relationship-assessments','standards-mappings','requirement-crosswalks','document-relationships'}:
            role, source = 'Primary', 'Reviewed judgements or links between identified records'
        elif key in {'framework-editions','standard-requirements','standard-indicator-definitions','accreditation-guidance-references','accreditation-expectations','external-publications','accreditation-external-decisions'}:
            role, source = 'Secondary', 'Publisher or scheme source identified by the individual record'
        elif key in {'evidence-versions','review-evidence','relationship-revision-evidence'}:
            role, source = 'Primary', 'Version-bound evidence submitted or captured for review'
        elif scope == 'Installation':
            role, source = 'Secondary', 'Isolated installation object. Content origin unresolved'
        elif scope == 'Recovery':
            role, source = 'Secondary', 'Recovery copy. Original dataset or sealed package unresolved'
        elif scope != 'Product':
            role, source = 'Unresolved', 'Fixture or supporting object. Origin unresolved'
        else:
            role, source = 'Unresolved', 'Original authority or derivation unresolved'
        source = (provenance or {}).get(r['DatasetId'].lower(), source)
        rows[r['DatasetId'].lower()] = dict(DataRole=role, DatasetSource=source, ReadFlows=set(), WriteFlows=set())
    resolved, observed = [], []
    flow_count = 0
    for path in sorted((export/'Workflows').glob('*.json')):
        flow_count += 1
        guids = GUID.findall(path.name)
        flow = names.get(guids[-1].lower()) if guids else None
        if not flow:
            raise ValueError(f'Cannot identify exported workflow {path.name}')
        actions = list(nodes(json.loads(path.read_text())['properties']['definition']))
        action_map = dict(actions)
        sources = defaultdict(list)
        for name, action in actions:
            inp = action['inputs']
            if action['type'] in ('Select','Compose'):
                sources['outputs',name].append(inp.get('select',inp) if isinstance(inp,dict) else inp)
                sources['body',name] = sources['outputs',name]
            if action['type'] == 'SetVariable':
                sources['variables',inp['name']].append(inp.get('value'))
            if action['type'] == 'InitializeVariable':
                for var in inp['variables']:
                    sources['variables',var['name']].append(var.get('value'))
        def expand(value, seen=None):
            if seen is None:
                seen = set()
            text = value if isinstance(value,str) else json.dumps(value)
            extra = [variables.get(k,'') for k in PARAM.findall(text)]
            for ref in set(REF.findall(text)) - seen:
                seen.add(ref)
                extra.extend(expand(v, seen) for v in sources.get(ref,[]))
            return text+' '+' '.join(extra)
        for name, action in actions:
            inp = action['inputs']
            if not isinstance(inp,dict):
                continue
            host = inp.get('host',{})
            if 'sharepointonline' not in str(host).lower():
                continue
            p, op = inp.get('parameters',{}), host.get('operationId','')
            route = p.get('parameters/uri','')
            method = p.get('parameters/method','').upper()
            target = route or p.get('table') or p.get('folderPath') or p.get('path') or ''
            if '$batch' in route:
                target = p.get('parameters/body','')
            text = unquote(expand(target)).lower()
            site_value = p.get('dataset','')
            parameter = re.fullmatch(r"@(?:\{)?parameters\('([^']+)'\)\}?", site_value)
            if parameter:
                site_value = variables.get(parameter[1], '')
            site = urlsplit(unquote(site_value).lower().rstrip('/'))
            direction = 'ReadFlows' if method=='GET' or op.startswith('Get') else 'WriteFlows' if method in ('POST','PUT','PATCH','DELETE','MERGE') or op in ('CreateNewFolder','CreateFile') else None
            titles = set(re.findall(r"getbytitle\('+([^']+)'+\)", text))
            ids = set(GUID.findall(text))
            matches = []
            for r in records:
                url = urlsplit(unquote(r['DatasetUrl']['Url']).lower())
                folder = url.path.rstrip('/').split('/')[-1]
                site_path = url.path.rsplit('/',2 if '/lists/' in url.path else 1)[0]
                same_site = (url.scheme, url.netloc, site_path) == (site.scheme, site.netloc, site.path)
                if r['DatasetId'].lower() in ids or (same_site and r['Title'].lower() in titles) or (
                    folder and re.search('/'+re.escape(folder)+r"(?:/|$|['\"])", text.strip())
                    and same_site):
                    matches.append(r['DatasetId'].lower())
            if direction and matches:
                for ident in matches:
                    rows[ident][direction].add(flow)
            else:
                result = action_binding(name, action_map, variables, bindings) if bindings else None
                if result:
                    ids, directions = result
                    for ident in ids & rows.keys():
                        for use in directions:
                            rows[ident][use].add(flow)
                    outside = ids - rows.keys()
                    external_targets = bindings.get('externalDatasets', {})
                    missing = outside - external_targets.keys()
                    if missing:
                        gaps.append(dict(flow=flow,action=name,operation=op,reason='Parent outside catalogue without verified external binding',missingDatasets=sorted(missing)))
                        continue
                    resolution = dict(flow=flow,action=name,datasets=sorted(ids),directions=directions)
                    if outside:
                        resolution['externalDatasets'] = {k:external_targets[k] for k in sorted(outside)}
                    resolved.append(resolution)
                    continue
                if bindings:
                    external = bindings.get('externalActions',{}).get(flow,{}).get(name)
                    if (external and method == 'GET' and external['parameters'] == p
                            and all(variables.get(k) == v for k,v in external.get('environment',{}).items())):
                        resolved.append(dict(flow=flow,action=name,external=external['source'],directions=['ReadFlows']))
                        continue
                    sample = bindings.get('runObservations',{}).get(flow,{}).get(name)
                    if sample and sample['parameters'] == p and sample['dataset'] in rows:
                        observed.append(dict(flow=flow,action=name,dataset=sample['dataset'],scope='Selected production run'))
                gaps.append({'flow':flow,'action':name,'operation':op,'reason':('Unclassified connector operation' if not direction else 'External, dynamic or uncatalogued target')})
    if not flow_count or not rows:
        raise ValueError('Empty solution or directory')
    for ident,row in rows.items():
        linked = bool(row['ReadFlows'] or row['WriteFlows'])
        row['BindingStatus'] = ('Export binding found' if linked else 'No exact solution flow binding') + ('; source unresolved' if 'unresolved' in row['DatasetSource'].lower() else '')
        note = (bindings or {}).get('productUse',{}).get(ident)
        if note:
            row['BindingStatus'] += '; ' + note
        for field in ('ReadFlows','WriteFlows'):
            row[field] = '\n'.join(sorted(row[field])) or None
    manifest = dict(flowCount=flow_count, rows=rows, unresolvedActions=gaps, resolvedActions=resolved, runObservations=observed)
    if bindings:
        apply_run_reads(manifest, names, bindings.get("fictionalRunReads", []), bindings.get("externalDatasets", {}))
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('export','catalogue','output'):
        p.add_argument(arg,type=Path)
    p.add_argument('--overrides', type=Path, help='Private effective parameter name/value map')
    p.add_argument('--provenance', type=Path, help='Private physical dataset ID to receipt-backed source description')
    p.add_argument('--bindings', type=Path, help='Private file-parent, external-source and product-use evidence')
    a = p.parse_args()
    result = build(a.export,json.loads(a.catalogue.read_text())['desired'],
                   json.loads(a.overrides.read_text()) if a.overrides else {},
                   json.loads(a.provenance.read_text()) if a.provenance else {},
                   json.loads(a.bindings.read_text()) if a.bindings else {})
    with open(a.output, 'x', opener=lambda path, flags: os.open(path, flags, 0o600)) as f:
        json.dump(result,f,indent=2)
