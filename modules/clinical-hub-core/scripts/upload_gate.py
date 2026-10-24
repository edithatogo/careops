#!/usr/bin/env python3
"""Fail-closed local check of agent-created meeting document upload artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from docx import Document
from lxml.etree import XMLSyntaxError
from xml.etree import ElementTree as ET
from ddms_word_namespace_repair import inspect as inspect_mc_namespaces

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
MAXIMA = {'accuracy': 300, 'purpose_status': 200, 'format': 200, 'readability': 150, 'release': 150}

def inspect_docx(path, plain=True):
    errors = []
    if path.suffix.lower() != '.docx':
        return ['Word .docx required; text files are local sources only']
    try:
        with ZipFile(path) as z:
            names = z.namelist()
            for part, prefixes in inspect_mc_namespaces(path).items():
                errors.append('Undeclared markup-compatibility prefixes in ' + part + ': ' + ', '.join(prefixes))
            Document(path)
            styles = ET.fromstring(z.read('word/styles.xml'))
            body = ET.fromstring(z.read('word/document.xml'))
            if any('embeddings/' in n or 'vbaProject' in n or 'comments' in n for n in names):
                errors.append('Embedded objects, macros or comments are not permitted')
            for tag in ('ins', 'del', 'object', 'drawing', 'altChunk'):
                if body.find('.//' + W + tag) is not None:
                    errors.append('Unsupported document content: ' + tag)
            if plain:
                for props in styles.findall('.//' + W + 'docDefaults/' + W + 'rPrDefault/' + W + 'rPr'):
                    if any(c.tag not in {W+k for k in ('rFonts','sz','szCs','lang')} for c in props):
                        errors.append('Decorative document-default run formatting is not plain')
                for props in styles.findall('.//' + W + 'docDefaults/' + W + 'pPrDefault/' + W + 'pPr'):
                    if any(c.tag not in {W+k for k in ('spacing','widowControl')} for c in props):
                        errors.append('Decorative document-default paragraph formatting is not plain')
                for node in styles.findall('.//' + W + 'style'):
                    if node.get(W+'styleId') == 'Normal' or node.get(W+'default') in ('1', 'true'):
                        for props in node:
                            if props.tag == W+'rPr' and any(c.tag not in {W+k for k in ('rFonts','sz','szCs','lang')} for c in props):
                                errors.append('Decorative default or Normal run style is not plain')
                            if props.tag == W+'pPr' and any(c.tag not in {W+k for k in ('spacing','widowControl')} for c in props):
                                errors.append('Decorative default or Normal paragraph style is not plain')
                            if props.tag in {W+'basedOn', W+'link'}:
                                errors.append('Normal/default style inheritance needs explicit review')
                for props in body.findall('.//' + W + 'pPr'):
                    if any(c.tag not in {W+k for k in ('pStyle','pageBreakBefore','keepNext','keepLines','widowControl')} for c in props):
                        errors.append('Direct paragraph decoration is not plain')
                if body.find('.//' + W + 'tbl') is not None:
                    errors.append('Plain route cannot contain styled tables')
                for style in body.findall('.//' + W + 'pStyle'):
                    if style.get(W+'val') != 'Normal': errors.append('Plain route requires Normal style only')
                if body.find('.//' + W + 'rPr') is not None:
                    errors.append('Direct run formatting is not permitted in plain route')
                if any(n.startswith(('word/header', 'word/footer')) for n in names):
                    errors.append('Plain route cannot contain headers or footers')
    except (OSError, BadZipFile, KeyError, ET.ParseError, XMLSyntaxError, ValueError, TypeError, AttributeError):
        errors.append('Unreadable or invalid DOCX package')
    return errors

def validate_manifest(manifest, root):
    errors = []
    if not isinstance(manifest, dict) or not isinstance(manifest.get('artifacts'), list) or not manifest['artifacts']:
        return ['Exact upload manifest required']
    seen = set()
    for entry in manifest['artifacts']:
        if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
            errors.append('Malformed artifact entry'); continue
        path = (root / entry.get('path', '')).resolve()
        label = entry.get('path', 'missing path')
        if path in seen: errors.append(label+': duplicate artifact')
        seen.add(path)
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            errors.append(label+': artifact unavailable'); continue
        route=entry.get('format_route')
        if route not in ('plain_docx', 'organisational_docx'):
            errors.append(label+': explicit DOCX format route required')
        errors.extend(label+': '+e for e in inspect_docx(path, route != 'organisational_docx'))
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry.get('sha256'): errors.append(label+': reviewed bytes changed')
        receipt=entry.get('review', {})
        if not isinstance(receipt, dict):
            errors.append(label+': malformed review'); continue
        if receipt.get('sha256') != digest: errors.append(label+': review is missing or stale')
        for field in ('visual_pages_evidence', 'source_fidelity_evidence', 'release_evidence', 'independent_reviewer'):
            if not isinstance(receipt.get(field), str) or not receipt[field].strip(): errors.append(label+': '+field+' required')
        scores=receipt.get('scores', {})
        if not isinstance(scores, dict):
            errors.append(label+': malformed scores'); continue
        if set(scores) != set(MAXIMA) or any(type(scores.get(k)) is not int or not 0 <= scores[k] <= v for k,v in MAXIMA.items()):
            errors.append(label+': five valid category scores required')
        elif sum(scores.values()) < 999: errors.append(label+': score below 999/1000')
        if receipt.get('hard_stops') != []: errors.append(label+': unresolved or unreviewed hard stops')
        if route == 'organisational_docx' and (not isinstance(receipt.get('template_source_version_evidence'), str) or not receipt['template_source_version_evidence'].strip()):
            errors.append(label+': verified applicable organisational template required')
    return errors

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    data=json.loads(args.manifest.read_text())
    errors=validate_manifest(data,args.root)
    print(json.dumps({'status':'FAIL' if errors else 'PASS','errors':errors,'limit':'Local artifact gate; does not grant tenant authority.'},indent=2))
    raise SystemExit(bool(errors))
