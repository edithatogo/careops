# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Compile selected SharePoint resources offline; no credentials or tenant calls."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from html import escape

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'https://developer.microsoft.com/json-schemas/sp/site-design-script-actions.schema.json'
MANIFESTS = {'careops-catalogue': 'portfolio/careops-catalogue-sharepoint.v1.json'}
TYPES = frozenset({'Text', 'Note', 'Number', 'Boolean', 'DateTime', 'Choice', 'URL'})
NAME = re.compile(r'[A-Za-z][A-Za-z0-9_]{0,31}\Z')
TITLE_ID = 'fa564e0f-0c70-4ab9-b863-0177e6ddd247'


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + '\n'


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON property')
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    if path.is_symlink() or path.stat().st_size > 1024 * 1024:
        raise ValueError('A regular, bounded JSON input is required')
    value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise TypeError('JSON object required')
    return value


def text(value: object, *, limit: int = 2048) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError('Nonempty bounded text required')
    if any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError('Control characters are not supported')
    return value


def identifier(value: object) -> str:
    name = text(value, limit=32)
    if not NAME.fullmatch(name):
        raise ValueError('Portable SharePoint internal name required')
    return name


def identity(module: str, scope: str, name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f'https://careops.example.invalid/schema/{module}/{scope}/{name}'))


def field(module: str, scope: str, source: dict, indexed: set[str]) -> tuple[dict, str]:
    name = identifier(source['name'])
    kind = source['type']
    if kind not in TYPES:
        raise ValueError('Unsupported field type; explicit adapter required')
    for flag in ('required', 'unique', 'indexed'):
        if flag in source and type(source[flag]) is not bool:
            raise ValueError('Field flags must be JSON booleans')
    row = {
        'name': name, 'type': kind,
        'id': TITLE_ID if name == 'Title' else identity(module, scope, name),
        'required': source.get('required', False),
        'unique': source.get('unique', False),
        'indexed': source.get('indexed', False) or name in indexed or source.get('unique', False),
    }
    if row['unique'] and kind not in {'Text', 'Number', 'DateTime', 'Choice'}:
        raise ValueError('Unsupported unique field type')
    attrs = {
        'ID': '{' + row['id'] + '}', 'Name': name, 'StaticName': name,
        'DisplayName': name, 'Type': kind,
        'Required': str(row['required']).upper(),
        'Indexed': str(row['indexed']).upper(),
        'EnforceUniqueValues': str(row['unique']).upper(),
    }
    children = []
    if kind == 'Choice':
        values = source.get('options')
        if not isinstance(values, list) or not values or len(values) > 100:
            raise ValueError('Bounded nonempty choice list required')
        options = [text(v, limit=255) for v in values]
        if len(options) != len(set(options)):
            raise ValueError('Duplicate choices')
        row['options'] = options
        attrs['Format'] = 'Dropdown'
        attrs['FillInChoice'] = 'FALSE'
        children.append('<CHOICES>' + ''.join('<CHOICE>' + escape(option)
                                              + '</CHOICE>' for option in options) + '</CHOICES>')
    elif 'options' in source:
        raise ValueError('Only Choice fields may contain options')
    if 'default' in source:
        default = text(source['default'], limit=255)
        if kind == 'Choice' and default not in row['options']:
            raise ValueError('Default must be an allowed choice')
        row['default'] = default
        children.append('<Default>' + escape(default) + '</Default>')
    opening = '<Field ' + ' '.join(key + '="' + escape(value, quote=True) + '"'
                                  for key, value in attrs.items())
    xml = opening + ('>' + ''.join(children) + '</Field>' if children else '/>')
    return row, xml


def validate_existing(desired: dict, observed: dict | None) -> None:
    """Refuse field drift; do not infer or repair existing identities or data."""
    if observed is None:
        return
    if observed.get('schemaVersion') != 1 or not isinstance(observed.get('resources'), list):
        raise ValueError('Expected an explicit versioned resource inventory')
    for scope in ('siteColumns', 'contentTypes'):
        if scope not in observed:
            raise ValueError('Shared site schema readback is required')
        if not isinstance(observed.get(scope), list):
            raise TypeError('Shared site schema readback must contain lists')
        shared = {}
        for item in observed[scope]:
            key = text(item['name']).casefold()
            if key in shared:
                raise ValueError('Duplicate shared site schema name')
            shared[key] = item
        for item in desired[scope]:
            current = shared.get(item['name'].casefold())
            if current is not None and current != item:
                raise ValueError('Existing shared site schema differs; reconcile explicitly')
    actual = {}
    for resource in observed['resources']:
        key = text(resource['name']).casefold()
        if key in actual or not isinstance(resource.get('fields'), list):
            raise ValueError('Duplicate resource or missing fields in inventory')
        fields = {}
        for column in resource['fields']:
            column_key = identifier(column['name']).casefold()
            if column_key in fields:
                raise ValueError('Duplicate observed field')
            fields[column_key] = column
        actual[key] = (resource, fields)
    for resource in desired['resources']:
        current = actual.get(resource['name'].casefold())
        if current is None:
            continue
        native, columns = current
        if native.get('templateType') != resource['templateType']:
            raise ValueError('Existing resource type conflicts with requested resource')
        for column in resource['fields']:
            old = columns.get(column['name'].casefold())
            if old is not None and old != column:
                raise ValueError('Existing field differs; reconcile explicitly before applying')


def compile_plan(modules: list[str], *, root: Path = ROOT, existing: dict | None = None) -> dict:
    if len(modules) != len(set(modules)):
        raise ValueError('Select each module once')
    if any(module not in MANIFESTS for module in modules):
        raise ValueError('Module has no admitted SharePoint bootstrap adapter')
    actions, resources, inputs, builtins, remaining = [], [], [], [], []
    site_columns, content_types = [], []
    names = set()
    for module in sorted(modules):
        source_path = MANIFESTS[module]
        manifest = read_json(root / source_path)
        core = manifest['core']
        inputs.append({'module': module, 'path': source_path,
                       'sha256': hashlib.sha256((root / source_path).read_bytes()).hexdigest()})
        shared = {}
        for column in core.get('sharedSiteColumns', []):
            row, xml = field(module, 'site', column, set())
            if row['name'] in shared:
                raise ValueError('Duplicate site column')
            shared[row['name']] = row
            site_columns.append(row)
            actions.append({'verb': 'createSiteColumnXml', 'schemaXml': xml, 'pushChanges': False})
        for library in core.get('libraries', []):
            for label in library.get('contentTypes', []):
                label = text(label, limit=128)
                content_types.append({'name': label,
                                      'id': '0x010100' + identity(module, 'content-type', label).replace('-', ''),
                                      'columns': list(library['columns'])})
                actions.append({
                    'verb': 'createContentType', 'name': label,
                    'id': '0x010100' + identity(module, 'content-type', label).replace('-', ''),
                    'hidden': False, 'group': 'CareOps',
                    'subactions': [{'verb': 'addSiteColumn', 'internalName': name}
                                   for name in library['columns']],
                })
        for kind, items in ((100, core.get('lists', [])), (101, core.get('libraries', []))):
            for item in items:
                name = identifier(item['name'])
                if name.casefold() in names:
                    raise ValueError('Duplicate resource name')
                names.add(name.casefold())
                subs = [{'verb': 'setDescription', 'description': text(item['purpose'])}]
                columns = []
                for column in item['columns']:
                    if kind == 101:
                        row = dict(shared[identifier(column)])
                        subs.append({'verb': 'addSiteColumn', 'internalName': row['name'],
                                     'addToDefaultView': False})
                    else:
                        row, xml = field(module, name, column, set(item.get('indexed', [])))
                        if row['name'] == 'Title':
                            if row['type'] != 'Text':
                                raise ValueError('Built-in Title must remain Text')
                            builtins.append({'resource': name, 'field': row,
                                             'action': 'verify built-in settings; never recreate'})
                        else:
                            subs.append({'verb': 'addSPFieldXml', 'schemaXml': xml,
                                         'addToDefaultView': False})
                    if any(c['name'].casefold() == row['name'].casefold() for c in columns):
                        raise ValueError('Duplicate field name')
                    columns.append(row)
                for label in item.get('contentTypes', []):
                    subs.append({'verb': 'addContentType', 'name': label})
                view = ['ID', 'Title'] + [c['name'] for c in columns if c['name'] != 'Title'][:6]
                subs.append({'verb': 'addSPView', 'name': 'CareOps metadata', 'viewFields': view,
                             'query': '', 'rowLimit': 100, 'isPaged': True, 'makeDefault': False})
                actions.append({'verb': 'createSPList', 'listName': name,
                                'templateType': kind, 'subactions': subs})
                resources.append({'module': module, 'name': name, 'templateType': kind, 'fields': columns})
        remaining.extend([{'module': module, 'viewsToQualify': core.get('views', []),
                           'formsToConfigure': core.get('forms', []),
                           'pagesToConfigure': core.get('sitePage', [])}])
    inventory = {'schemaVersion': 1, 'resources': resources,
                 'siteColumns': site_columns, 'contentTypes': content_types}
    validate_existing(inventory, existing)
    return {
        'siteScript': {'$schema': SCHEMA, 'actions': actions},
        'inventory': inventory,
        'plan': {'schemaVersion': 1, 'profile': 'standard-m365', 'selectedModules': sorted(modules),
                 'nativeExecution': 'not-executed', 'sourceInputs': inputs,
                 'applicationScope': 'reconcile-observed-scope' if existing is not None else 'new-empty-scope-only',
                 'builtInFieldsToVerify': builtins, 'moduleFollowUp': remaining,
                 'nativeChecksRemaining': [
                     'Verify current permission, classification and retention boundary before applying.',
                     'Read back IDs, types, choices, required/unique settings, indexes and content types.',
                     'Configure versioning, native forms and filtered views; test permissions directly.',
                     'Qualify UUID allocation and cross-list links; column types do not enforce these.',
                     'Test partial apply, reapply, denied access, export and restore with fictional records.',
                     'Do not widen access or delete user records during recovery.',
                 ]},
    }


def csv_dictionary(inventory: dict) -> str:
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['Resource', 'InternalName', 'Type', 'Required', 'Unique', 'Indexed', 'Choices', 'Default', 'FieldID'])
    for resource in inventory['resources']:
        for column in resource['fields']:
            cells = [resource['name'], column['name'], column['type'], column['required'],
                     column['unique'], column['indexed'], '|'.join(column.get('options', [])),
                     column.get('default', ''), column['id']]
            # Dictionary exports may be opened in Excel; do not emit active formulas.
            writer.writerow(["'" + v if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@')) else v for v in cells])
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', action='append', choices=sorted(MANIFESTS), default=[])
    parser.add_argument('--profile', choices=['standard-m365'], default='standard-m365')
    parser.add_argument('--existing-inventory', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='New local output directory; never overwritten')
    args = parser.parse_args()
    try:
        existing = read_json(args.existing_inventory) if args.existing_inventory else None
        package = compile_plan(args.module, existing=existing)
        args.output.mkdir(parents=True, exist_ok=False)
        for name, key in [('site-script.json', 'siteScript'), ('desired-inventory.json', 'inventory'), ('plan.json', 'plan')]:
            (args.output / name).write_text(canonical(package[key]), encoding='utf-8')
        (args.output / 'columns.csv').write_text(csv_dictionary(package['inventory']), encoding='utf-8')
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f'Bootstrap refused ({type(error).__name__}); inspect the selected local input and output paths.\n')
    print('Offline setup package generated. Native application and readback remain separate.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
