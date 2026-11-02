"""Read-only external catalogue reconciliation; no applicability or native writes."""
from __future__ import annotations
import hashlib
import re
from collections import Counter
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit
from zipfile import BadZipFile, ZipFile
from zlib import error as ZlibError
from bs4 import BeautifulSoup


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


DEFAULT_REFERENCE_HOSTS = frozenset({'www.safetyandquality.gov.au', 'safetyandquality.gov.au'})


def verified_original_capsule(source, original, read_bytes):
    """Bind a historical source to its exact, byte-preserving ZIP member.

    Read only; never extract files or treat a container/version as an edition.
    The caller still qualifies the logical document identity independently.
    """
    capsule = source.get('originalCapsule')
    if (not original or not isinstance(capsule, dict)
            or not isinstance(capsule.get('path'), str) or not capsule['path']
            or not isinstance(capsule.get('member'), str) or not capsule['member']
            or not isinstance(capsule.get('sha256'), str)
            or not re.fullmatch(r'[a-f0-9]{64}', capsule.get('sha256') or '')):
        return None
    try:
        raw = read_bytes(capsule['path'])
        if (not isinstance(raw, (bytes, bytearray)) or len(raw) > 128 * 1024 * 1024
                or sha(raw) != capsule['sha256']):
            return None
        with ZipFile(BytesIO(raw)) as archive:
            members = [i for i in archive.infolist() if i.filename == capsule['member']]
            if (len(members) != 1 or members[0].file_size != len(original)
                    or archive.read(members[0]) != original):
                return None
    except (OSError, KeyError, ValueError, RuntimeError, NotImplementedError, BadZipFile, EOFError, ZlibError):
        return None
    return {'sourceIdentityState': 'verified_source_identity',
            'originalCapsuleSHA256': capsule['sha256'],
            'originalCapsuleMember': capsule['member']}


def pdf_link_label_inspection(xml_bytes, original_sha256):
    """Inspect bounded Poppler XML link labels/boxes; never join or adopt them."""
    import math
    import xml.etree.ElementTree as ET
    if (not isinstance(xml_bytes, bytes) or len(xml_bytes) > 8 * 1024 * 1024
            or not isinstance(original_sha256, str)
            or not re.fullmatch(r'[a-f0-9]{64}', original_sha256)):
        raise ValueError('Bound XML bytes and original SHA256 required')
    # Poppler emits this fixed external DTD declaration. No entities or other DTD.
    try:
        xml_text = xml_bytes.decode('utf-8')
    except UnicodeError as error:
        raise ValueError('UTF-8 Poppler XML required') from error
    if '\x00' in xml_text:
        raise ValueError('Unsupported XML encoding')
    safe = xml_text.replace('<!DOCTYPE pdf2xml SYSTEM "pdf2xml.dtd">', '')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)', safe, re.I):
        raise ValueError('Unsupported XML declaration')
    try:
        root = ET.fromstring(safe)
    except ET.ParseError as error:
        raise ValueError('Malformed PDF link XML') from error
    if root.tag != 'pdf2xml':
        raise ValueError('Expected Poppler pdf2xml root')
    entries, ignored, seen = [], [], set()
    ordinal = 0
    for page in root.findall('page'):
        try:
            number = int(page.attrib['number'])
        except (KeyError, ValueError) as error:
            raise ValueError('PDF page number required') from error
        if not 1 <= number <= 10000 or number in seen:
            raise ValueError('Ambiguous PDF page number')
        seen.add(number)
        for node in page.findall('text'):
            anchors = node.findall('.//a')
            if not anchors:
                continue
            try:
                box = {k: float(node.attrib[k]) for k in ('top', 'left', 'width', 'height')}
            except (KeyError, ValueError) as error:
                raise ValueError('Link text box required') from error
            if (any(not math.isfinite(v) or abs(v) > 10000000 for v in box.values())
                    or box['width'] < 0 or box['height'] < 0):
                raise ValueError('Invalid link text box')
            for anchor in anchors:
                if anchor.findall('.//a'):
                    raise ValueError('Nested link labels are ambiguous')
                href, label = anchor.get('href', ''), ''.join(anchor.itertext())
                try:
                    target = urlsplit(href)
                    valid = (target.scheme in {'http', 'https'} and target.hostname
                        and not target.username and not target.password
                        and target.port in (None, 80, 443) and not re.search(r'[\s\\]', href))
                except ValueError:
                    valid = False
                row = dict(ordinal=ordinal, page=number, rawURL=href, label=label, textBox=box)
                (entries if valid else ignored).append(row if valid else dict(
                    row, reason='unsupported_or_malformed_URI'))
                ordinal += 1
    return dict(kind='ppg-pdf-link-label-inspection-v1', originalSHA256=original_sha256,
                xmlSHA256=sha(xml_bytes), inspectedPages=sorted(seen), entries=entries, ignoredLinks=ignored,
                originalBindingVerified=False, fullTextReview=False, editionVerified=False,
                nativeWrites=0, retrievals=0)


def pdf_link_labels_main(argv=None):
    """Capture one page's link labels from an immutable private original copy."""
    import argparse
    import json
    import os
    import shutil
    import subprocess
    import tempfile
    import threading
    parser = argparse.ArgumentParser(description=pdf_link_labels_main.__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--original-sha256', required=True)
    parser.add_argument('--page', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists() or not 1 <= args.page <= 10000:
        raise ValueError('New private output and bounded page required')
    with args.original.open('rb') as source:
        original = source.read(128 * 1024 * 1024 + 1)
    if len(original) > 128 * 1024 * 1024:
        raise ValueError('Original PDF exceeds bound')
    if not original.startswith(b'%PDF-') or sha(original) != args.original_sha256:
        raise ValueError('Original PDF differs from expected hash')
    executable = shutil.which('pdftohtml')
    if not executable:
        raise ValueError('Installed Poppler pdftohtml required')
    with tempfile.TemporaryDirectory(prefix='ppg-pdf-links-') as temp:
        frozen = Path(temp) / 'source.pdf'
        fd = os.open(frozen, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(original)
        command = [executable, '-f', str(args.page), '-l', str(args.page),
                   '-xml', '-hidden', '-i', '-stdout', str(frozen)]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
            timer = threading.Timer(60, process.kill)
            timer.daemon = True
            try:
                timer.start()
                xml_bytes = process.stdout.read(8 * 1024 * 1024 + 1)
                if len(xml_bytes) > 8 * 1024 * 1024:
                    raise ValueError('PDF link XML exceeds bound')
                if process.wait() != 0:
                    raise ValueError('PDF link extraction failed or timed out')
            finally:
                if process.poll() is None:
                    process.kill()
                timer.cancel()
                timer.join()

    result = pdf_link_label_inspection(xml_bytes, args.original_sha256)
    if result['inspectedPages'] != [args.page]:
        raise ValueError('Processor returned an unselected page')
    result.update(originalBindingVerified=True, selectedPage=args.page,
                  processor='Poppler pdftohtml; immutable original copy; images excluded')
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
    except BaseException:
        args.output.unlink(missing_ok=True)
        raise
    print(json.dumps(dict(linkLabels=len(result['entries']), nativeWrites=0,
                          fullTextReview=False, originalBindingVerified=True)))


def pdf_uri_inspection(annotation_output, original_sha256, *, decode_url_wrappers=False):
    """Render retained ``pdfinfo -url`` evidence without fetching any URI.

    The caller must bind the dump to the original PDF. This representation is
    annotation metadata, never a full-body review or publication/edition proof.
    """
    if (not isinstance(annotation_output, str) or len(annotation_output) > 8 * 1024 * 1024
            or not re.fullmatch(r'[a-f0-9]{64}', original_sha256 or '')
            or type(decode_url_wrappers) is not bool):
        raise ValueError('Bound PDF annotation dump and explicit decoding flag required')
    lines = annotation_output.splitlines()
    if not lines or not re.fullmatch(r'\s*Page\s+Type\s+URL\s*', lines[0]):
        raise ValueError('Expected pdfinfo URL header')
    entries, ignored, pages = [], [], {}
    for ordinal, line in enumerate(lines[1:]):
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*([0-9]+)\s+Annotation\s+(.+?)\s*', line)
        if not match or not 1 <= int(match[1]) <= 10000:
            raise ValueError('Unsupported PDF annotation row; preserve dump for reconciliation')
        page, raw_url = int(match[1]), match[2]
        try:
            parsed = urlsplit(raw_url)
            valid = (parsed.scheme in {'http', 'https'} and parsed.hostname and not parsed.username
                and not parsed.password and not re.search(r'[\s\\]', raw_url))
            parsed.port
        except ValueError:
            valid = False
        if not valid:
            ignored.append({'ordinal': ordinal, 'page': page, 'rawURL': raw_url,
                            'reason': 'unsupported_or_malformed_URI'})
            continue
        entry = {'ordinal': ordinal, 'page': page, 'rawURL': raw_url, 'decodedTarget': None}
        pages.setdefault(page, []).append('PDF URI ' + str(ordinal) + ': ' + raw_url)
        if (decode_url_wrappers and parsed.scheme == 'https' and parsed.hostname == 'www.google.com'
                and parsed.path == '/url' and parsed.port in (None, 443)):
            values = parse_qs(parsed.query).get('url', [])
            if len(values) == 1:
                try:
                    target = urlsplit(values[0])
                    allowed = (target.scheme in {'http', 'https'} and target.hostname
                        and not target.username and not target.password and target.port in (None, 80, 443)
                        and not re.search(r'[\s\\]', values[0]))
                except ValueError:
                    allowed = False
                if allowed:
                    entry['decodedTarget'] = values[0]
                    pages[page].append('Encoded URL target ' + str(ordinal) + ': ' + values[0])
        entries.append(entry)
    rendered = ['PDF URI annotation inspection; not a body-text review.\nOriginal SHA256: ' + original_sha256]
    for page in range(1, max(pages, default=0) + 1):
        content = '\n'.join(pages.get(page, []))
        if page == 1:
            rendered[0] += '\n' + content
        else:
            rendered.append(content)
    text = '\f'.join(rendered)
    return {'inspectionKind': 'pdf-uri-annotations', 'text': text,
            'textSHA256': sha(text.encode()), 'annotationOutputSHA256': sha(annotation_output.encode()),
            'entries': entries, 'ignoredURIs': ignored, 'retrievals': 0,
            'fullTextReview': False, 'editionVerified': False}


def reference_scope(catalogue, sources, publications, *, read_bytes,
                    publisher_hosts=None, include_nsqhs_names=True):
    """Inspect retained, hash-bound text for literal NSQHS references and URLs.

    This is an explicit retrieval scope, not extraction of every bibliographic
    reference, current-policy verification or substantive dependency assessment.
    """
    if publisher_hosts is not None and not isinstance(publisher_hosts, (list, tuple, set, frozenset)):
        raise ValueError('Explicit publisher host collection required')
    hosts = DEFAULT_REFERENCE_HOSTS if publisher_hosts is None else frozenset(publisher_hosts)
    if (not hosts or type(include_nsqhs_names) is not bool or any(
            not isinstance(host, str) or len(host) > 253 or not re.fullmatch(
                r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}', host) for host in hosts)):
        raise ValueError('Exact publisher hostnames and name-selection flag required')
    ids = [r['DocumentUID'] for r in catalogue]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate local catalogue identity')
    by_uid = {uid: [] for uid in ids}
    occurrences, held, seen = [], [], set()
    urls, url_records = {}, {}
    nsqhs = []
    publication_keys = {p['key'] for p in publications if p['kind'] == 'Publication'}
    for p in publications:
        if p['kind'] == 'Publication':
            publication = p['key']
            if publication == 'acsqhc:nsqhs':
                nsqhs.append(publication)
        elif p['kind'] in {'Edition', 'Capture'} and p.get('publicationKey') in publication_keys:
            publication = p['publicationKey']
        else:
            continue
        source_urls = {a['sourceURL'] for a in p.get('assertions', [])}
        if p.get('data', {}).get('sourceURL'):
            source_urls.add(p['data']['sourceURL'])
        for source_url in source_urls:
            urls.setdefault(source_url, set()).add(publication)
            url_records.setdefault(source_url, set()).add(p['key'])
    pattern = re.compile(r'https?://[^\s<>"\x00-\x1f]+|\b(?:NSQHS(?:\s+Standards)?|National\s+Safety\s+and\s+Quality\s+Health\s+Service\s+Standards)\b', re.I)
    for s in sources:
        uid = s['documentUID']
        if uid not in by_uid:
            raise ValueError('Retained source outside catalogue scope')
        identity = (uid, s['originalSHA256'], s['textSHA256'])
        if identity in seen:
            raise ValueError('Duplicate retained source association')
        seen.add(identity)
        reason, capsule_evidence = None, None
        try:
            original = read_bytes(s['originalPath'])
            text_raw = read_bytes(s['textPath'])
            text = text_raw.decode('utf-8')
            if sha(original) != s['originalSHA256'] or sha(text_raw) != s['textSHA256'] or text != s['text']:
                reason = 'original_or_text_hash_binding_differs'
            elif s['extractionError'] or len(text.strip()) < 100:
                reason = 'extraction_error_or_insufficient_text'
            elif s['identityState'] == 'verified_source_identity':
                capsule_evidence = verified_original_capsule(s, original, read_bytes)
                if capsule_evidence is None:
                    reason = 'original_capsule_binding_unqualified'
            elif s['identityState'] not in {'exact_register_identifier', 'qualified_edition_variant'}:
                reason = 'identity_association_unqualified'
        except (OSError, UnicodeError):
            reason = 'retained_original_or_text_unavailable'
        if reason:
            held.append({'documentUID': uid, 'originalSHA256': s['originalSHA256'], 'reason': reason})
            by_uid[uid].append('held')
            continue
        by_uid[uid].append('inspected')
        for m in pattern.finditer(text):
            literal = m.group()
            is_url = literal.lower().startswith(('https://', 'http://'))
            locator = literal if is_url else None
            if is_url and locator not in urls and s.get('inspectionKind') != 'pdf-uri-annotations':
                while True:
                    prior = locator
                    locator = locator.rstrip('.,;:')
                    if locator.endswith(')') and locator.count(')') > locator.count('('):
                        locator = locator[:-1]
                    if locator == prior:
                        break
            # Literal occurrences are retrieval candidates, never fetched or edition-adopted.
            if not is_url and not include_nsqhs_names:
                continue
            if is_url:
                try:
                    target = urlsplit(locator)
                    selected = (target.scheme in {'http', 'https'} and target.hostname in hosts
                        and not target.username and not target.password and target.port in (None, 80, 443))
                except ValueError:
                    selected = False
                if not selected:
                    continue
            candidates = sorted(urls.get(locator, set()) if is_url else nsqhs)
            start, end = m.span()
            key = sha((uid+'\0'+s['originalSHA256']+'\0'+s['textSHA256']+'\0'+str(start)+'\0'+str(end)).encode())
            occurrences.append({'key': 'reference:'+key, 'documentUID': uid,
                'sourceVersion': s['sourceVersion'], 'originalSHA256': s['originalSHA256'],
                'textSHA256': s['textSHA256'], 'start': start, 'end': end,
                'page': text.count('\f', 0, start)+1, 'line': text.count('\n', 0, start)+1,
                'literal': literal, 'context': text[max(0,start-120):min(len(text),end+200)],
                'method': 'literal-official-URL' if is_url else 'literal-NSQHS-name',
                'candidatePublicationKeys': candidates,
                'resolution': 'publication-only' if len(candidates)==1 else 'ambiguous' if candidates else 'unresolved',
                'editionKey': None, 'editionResolution': 'not-established-by-literal-match',
                'versionConflict': s['versionConflict'], 'clinicalApplicabilityAccepted': False})
            if is_url:
                occurrences[-1]['urlMatchRecordKeys'] = sorted(url_records.get(locator, set()))
            if capsule_evidence:
                occurrences[-1].update(capsule_evidence)
            if s.get('inspectionKind') == 'pdf-uri-annotations':
                occurrences[-1].update(inspectionKind='pdf-uri-annotations',
                    annotationOutputSHA256=s['annotationOutputSHA256'],
                    method='literal-PDF-URI-annotation')
    states = []
    for uid, values in by_uid.items():
        state = 'no-retained-source' if not values else 'all-retained-texts-inspected' if set(values)=={'inspected'} else 'some-retained-text-held'
        states.append({'documentUID': uid, 'state': state, 'inspectedSources': values.count('inspected'), 'heldSources': values.count('held')})
    return {'kind': 'ppg-local-external-reference-scope-v1', 'scope': ('Retained NSQHS names and Commission URLs; not every external citation'
            if hosts == DEFAULT_REFERENCE_HOSTS and include_nsqhs_names else
            'Retained literal URLs for selected publishers; not every external citation'),
        'publisherHosts': sorted(hosts), 'includeNSQHSNames': include_nsqhs_names,
        'catalogueIdentities':len(ids), 'retainedAssociations':len(sources),
        'sourceStates':dict(Counter(x['state'] for x in states)), 'identityLedger':states,
        'heldSources':held, 'occurrenceCount':len(occurrences), 'occurrences':occurrences,
        'resolutionCounts':dict(Counter(x['resolution'] for x in occurrences)),
        'nativeWrites':0, 'completeExternalReferenceCoverage':False, 'clinicalApplicabilityAccepted':False}


def group_pdf_uri_occurrences(scope):
    """Group repeated annotation objects, retaining every original occurrence key."""
    if scope.get('occurrenceCount') != len(scope.get('occurrences', [])):
        raise ValueError('PDF annotation occurrence denominator mismatch')
    groups, keys = {}, set()
    for row in scope['occurrences']:
        if row.get('inspectionKind') != 'pdf-uri-annotations' or row['key'] in keys:
            raise ValueError('Unique PDF annotation occurrences required')
        keys.add(row['key'])
        identity = tuple(row[k] for k in ('documentUID','originalSHA256','textSHA256','sourceVersion','literal'))
        if identity not in groups:
            groups[identity] = {**row, 'annotationOccurrences': []}
        group = groups[identity]
        if any(group.get(k) != row.get(k) for k in (
                'candidatePublicationKeys','resolution','editionKey','versionConflict',
                'annotationOutputSHA256','urlMatchRecordKeys')):
            raise ValueError('Inconsistent annotation resolution/source provenance')
        group['annotationOccurrences'].append({k: row[k] for k in ('key','start','end','page','line')})
    rows = list(groups.values())
    if sum(len(row['annotationOccurrences']) for row in rows) != len(keys):
        raise ValueError('PDF annotation grouping lost an occurrence')
    return {**scope, 'occurrences': rows, 'occurrenceCount': len(rows),
            'annotationOccurrenceCount': len(keys),
            'grouping': 'one URI per retained source representation; all annotation locations retained',
            'resolutionCounts': dict(Counter(row['resolution'] for row in rows))}


def representation_scope(bundle, root):
    """Enumerate literal PDF links in every selected publication HTML capture.

    Links remain candidates until identity/edition relevance is checked. Their
    absence among captures is a gap, not an exclusion or withdrawal decision.
    """
    records = bundle['records']; captures = [r for r in records if r['kind']=='Capture']
    inventory, gaps, malformed = [], [], []
    for p in records:
        if p['kind']!='Publication' or not p['requiredCapture']:
            continue
        pages = [c for c in captures if c['publicationKey']==p['key'] and c['data']['mimeType']=='text/html']
        if not pages:
            gaps.append({'publicationKey':p['key'], 'reason':'selected_publication_has_no_retained_HTML'})
        for page in pages:
            d=page['data']; path=Path(root)/d['file']
            if Path(d['file']).name != d['file'] or path.is_symlink():
                raise ValueError('Unsafe retained source path')
            raw=path.read_bytes()
            if sha(raw)!=d['sha256'] or len(raw)!=d['bytes']:
                raise ValueError('Retained representation bytes differ')
            main=BeautifulSoup(raw,'html.parser').find('main')
            if main is None:
                raise ValueError('Publication main content absent')
            for ordinal,link in enumerate(main.find_all('a',href=True)):
                try:
                    target=urljoin(d['sourceURL'],link['href']); u=urlsplit(target)
                    port=u.port
                except ValueError:
                    malformed.append({'publicationKey':p['key'],'sourceCaptureKey':page['key'],
                        'ordinal':ordinal,'rawHref':link['href'],'reason':'malformed_link_authority'})
                    continue
                if not u.path.lower().endswith('.pdf'):
                    continue
                same_origin=u.scheme=='https' and u.hostname=='www.safetyandquality.gov.au' and not u.username and not u.password and port in (None,443)
                matches=[c for c in captures if c['publicationKey']==p['key'] and c['data']['sourceURL']==target]
                inventory.append({'publicationKey':p['key'],'sourceCaptureKey':page['key'],
                    'sourceSHA256':d['sha256'],'ordinal':ordinal,'rawHref':link['href'],
                    'sourceURL':d['sourceURL'],'url':target,'label':link.get_text(' ',strip=True),
                    'samePublisherOrigin':same_origin,'captureKeys':[c['key'] for c in matches],
                    'exactEditionKeys':sorted({c['editionKey'] for c in matches if c['editionKey']}),
                    'disposition':'retained-candidate' if matches else 'not-retained-candidate',
                    'requiredRepresentationAccepted':False})
    return {'kind':'ppg-required-representation-candidates-v1','candidates':inventory,
        'candidateOccurrences':len(inventory),'uniquePublicationURLs':len({(x['publicationKey'],x['url']) for x in inventory}),
        'notRetainedOccurrences':sum(not x['captureKeys'] for x in inventory),'pageGaps':gaps,
        'malformedLinks':malformed,
        'requiredRepresentationDenominatorDeclared':False,'nativeWrites':0,'milestoneAccepted':False}


def main(argv=None):
    """Create new private audit outputs; never write catalogue/native state."""
    import argparse
    import json
    import os
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--local-inputs',type=Path,required=True)
    parser.add_argument('--capture-root',type=Path,required=True)
    parser.add_argument('--source-root',type=Path,default=Path.cwd())
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--publisher-host', action='append', metavar='HOST',
                        help='Explicit qualified URL host; repeat for a bounded source family')
    parser.add_argument('--no-nsqhs-names', action='store_true')
    parser.add_argument('--group-pdf-uris', action='store_true',
                        help='Group repeated PDF URI objects while retaining all occurrence locators')
    args=parser.parse_args(argv)
    if args.output_dir.exists():
        raise ValueError('New private output directory required')
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result:raise ValueError('Duplicate JSON member')
            result[k]=v
        return result
    def load(path):
        raw=path.read_bytes()
        if len(raw)>128*1024*1024:raise ValueError('Input exceeds bound')
        return raw,json.loads(raw,object_pairs_hook=unique)
    bundle_raw,bundle=load(args.bundle);local_raw,local=load(args.local_inputs)
    root=args.source_root.resolve()
    def read(path):
        p=Path(path).resolve()
        if root not in p.parents or not p.is_file() or p.stat().st_size>128*1024*1024:
            raise OSError('Retained source outside approved root or bound')
        return p.read_bytes()
    refs=reference_scope(local['catalogue'],local['sources'],bundle['records'],read_bytes=read,
        publisher_hosts=args.publisher_host,include_nsqhs_names=not args.no_nsqhs_names)
    if args.group_pdf_uris:
        refs=group_pdf_uri_occurrences(refs)
    reps=representation_scope(bundle,args.capture_root)
    outputs={'references.json':refs,'representations.json':reps}
    args.output_dir.mkdir(mode=0o700)
    hashes={}
    for name,value in outputs.items():
        raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        fd=os.open(args.output_dir/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw)
        hashes[name]=sha(raw)
    manifest={'bundleSHA256':sha(bundle_raw),'localInputsSHA256':sha(local_raw),
        'outputs':hashes,'nativeWrites':0,'completeExternalReferenceCoverage':False}
    fd=os.open(args.output_dir/'manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(manifest,f,indent=2)
    print(json.dumps({'referenceOccurrences':refs['occurrenceCount'],'catalogueIdentities':refs['catalogueIdentities'],
        'representationCandidates':reps['candidateOccurrences'],'nativeWrites':0}))


if __name__=='__main__':
    import sys
    if sys.argv[1:2] == ['pdf-link-labels']:
        pdf_link_labels_main(sys.argv[2:])
    else:
        main()
