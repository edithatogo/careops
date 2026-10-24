#!/usr/bin/env python3
"""Inspect/repair lost MC prefix declarations in a separate AVAC development copy.

No platform calls or body generation. Restore only aliases evidenced in the same
part of the maintained template; preserve all other member bytes and never replace
an existing output. A clean result is not Word runtime/editability verification.
"""
import argparse
from io import BytesIO
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from xml.sax.saxutils import quoteattr
from zipfile import ZipFile

MC = '{http://schemas.openxmlformats.org/markup-compatibility/2006}'
PREFIX_LISTS = {MC + 'Ignorable', MC + 'MustUnderstand'}
QNAME_LISTS = {MC + s for s in ('ProcessContent', 'PreserveElements', 'PreserveAttributes')}


def missing_prefixes(data):
    """Check MC token-valued attributes, which ordinary XML parsing overlooks."""
    scopes, pending, missing = [], {}, set()
    for event, value in ET.iterparse(BytesIO(data), events=('start-ns', 'start', 'end')):
        if event == 'start-ns':
            pending[value[0]] = value[1]
        elif event == 'start':
            scope = dict(scopes[-1]) if scopes else {'xml': 'http://www.w3.org/XML/1998/namespace'}
            scope.update(pending)
            pending = {}
            scopes.append(scope)
            for key, text in value.attrib.items():
                prefix_list = key in PREFIX_LISTS or (value.tag == MC + 'Choice' and key == 'Requires')
                if prefix_list or key in QNAME_LISTS:
                    for token in text.split():
                        # An unprefixed QName uses the default namespace, if any.
                        prefix = token.split(':', 1)[0] if prefix_list or ':' in token else ''
                        if prefix and prefix not in scope:
                            missing.add(prefix)
        else:
            scopes.pop()
    return sorted(missing)


def root_namespaces(data):
    result = {}
    for event, value in ET.iterparse(BytesIO(data), events=('start-ns', 'start')):
        if event == 'start':
            return result
        result[value[0]] = value[1]
    return result


def inspect(path):
    with ZipFile(path) as package:
        if package.testzip() is not None:
            raise ValueError('Package CRC failure')
        if len(package.namelist()) != len(set(package.namelist())):
            raise ValueError('Duplicate package members')
        return {name: missing for name in package.namelist() if name.endswith('.xml')
                and (missing := missing_prefixes(package.read(name)))}


def repair(source, template, output):
    source, template, output = map(Path, (source, template, output))
    if output.resolve() in {source.resolve(), template.resolve()}:
        raise ValueError('Output must be a separate file')
    if inspect(template):
        raise ValueError('Template itself has missing MC declarations')
    changed = {}
    with ZipFile(source) as original, ZipFile(template) as reference:
        if original.testzip() is not None or len(original.namelist()) != len(set(original.namelist())):
            raise ValueError('Invalid source package')
        members = []
        for entry in original.infolist():
            data = original.read(entry.filename)
            missing = missing_prefixes(data) if entry.filename.endswith('.xml') else []
            if missing:
                if entry.filename not in reference.namelist():
                    raise ValueError('Missing reference part: ' + entry.filename)
                bindings = root_namespaces(reference.read(entry.filename))
                if any(prefix not in bindings for prefix in missing):
                    raise ValueError('Prefix has no maintained-template evidence: ' + ','.join(missing))
                # Insert declarations without reserializing XML, text, drawings,
                # hyperlinks, compatibility token values or existing namespaces.
                root = re.search(rb'<(?![!?/])[^\s/>]+', data)
                if root is None:
                    raise ValueError('No XML root')
                addition = ''.join(' xmlns:' + p + '=' + quoteattr(bindings[p]) for p in missing).encode()
                data = data[:root.end()] + addition + data[root.end():]
                if missing_prefixes(data):
                    raise ValueError('Repair did not resolve missing aliases')
                changed[entry.filename] = {p: bindings[p] for p in missing}
            members.append((entry, data))
        # All validation happens before exclusive create; never overwrite drafts.
        with output.open('xb') as stream, ZipFile(stream, 'w') as repaired:
            repaired.comment = original.comment
            for entry, data in members:
                repaired.writestr(entry, data)
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--template', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if bool(args.template) != bool(args.output):
        parser.error('--template and --output must be supplied together')
    before = inspect(args.source)
    changes = repair(args.source, args.template, args.output) if args.output else None
    print(json.dumps({'missing_mc_prefixes': before, 'restored_declarations': changes,
                      'output': str(args.output) if args.output else None,
                      'limit': 'Local package check/repair only; no native Word editability proof.'}, indent=2))
