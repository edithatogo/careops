"""Bound retained source aliases/capsules and distinguish source edition assertions.

These guards do not amend documents, establish currency, or complete an assessment.
Actual native/original byte verification precedes the attestations consumed here.
"""
import hashlib
import re

from scripts.ppg_catalogue_relationships import digest


def family(identifier):
    value = re.sub(r'\s+', '', identifier or '').casefold().replace('–', '-').replace('—', '-')
    value = re.split(r'-v(?=\d)|(?<=\d)v(?=\d)', value, maxsplit=1)[0]
    return re.sub(r'-\d{2}/\d{2,4}$', '', value).rstrip('-')


def label(value):
    return ' '.join((value or '').casefold().split())


def propose_membership_binding(source, catalogue):
    matches = [r for r in catalogue if family(r['sourceDocumentId']) == family(source['document_id'])
               and label(r['sourceTitle']) == label(source['title'])
               and label(r.get('sourceCustodian')) == label(source.get('custodian'))]
    if len(matches) != 1 or not family(source['document_id']):
        raise ValueError('Source alias absent or ambiguous')
    row = matches[0]
    if source.get('catalogue_item_id') not in (None, row['Id']):
        raise ValueError('Existing source binding differs')
    return dict(sourceDocumentId=source['document_id'], catalogueItemId=row['Id'],
                documentUID=row['DocumentUID'], catalogueSourceDocumentId=row['sourceDocumentId'],
                sourceRowSHA256=digest(source), catalogueIdentitySHA256=digest({k: row[k] for k in
                    ('Id', 'DocumentUID', 'sourceDocumentId', 'sourceTitle', 'sourceCustodian')}),
                state='qualified_edition_identity_binding',
                basis='Unique identifier family, complete title and custodian agree; editions retained separately',
                currentAuthorityVerified=False)


def validate_membership_binding(binding, source, catalogue):
    if binding != propose_membership_binding(source, catalogue):
        raise ValueError('Membership evidence changed')


def validate_capture_binding(binding, catalogue, captures):
    uid, capture_id = binding.get('documentUID'), binding.get('captureId')
    capture = captures.get(capture_id)
    if uid not in catalogue or not capture or capture.get('PPGCaptureKind') != 'Document':
        raise ValueError('Unknown capture binding endpoint')
    if binding.get('nativeSHA256') != capture.get('PPGCaptureSHA256'):
        raise ValueError('Native capture hash differs')
    for key in ('originalSHA256', 'nativeSHA256', 'verificationReceiptSHA256'):
        if not re.fullmatch('[0-9a-f]{64}', binding.get(key, '')):
            raise ValueError('Capture binding hash required')
    if (binding.get('nativeBytesVerified') is not True or binding.get('originalBytesVerified') is not True
            or binding.get('currentAuthorityVerified') is not False or not binding.get('basis')):
        raise ValueError('Explicit byte verification and retained scope required')
    if binding['originalSHA256'] != binding['nativeSHA256']:
        if binding.get('capsuleMemberSHA256') != binding['originalSHA256']:
            raise ValueError('Original capsule member was not verified')
    expected = family(catalogue[uid]['sourceDocumentId'])
    if not expected or not any(family(x) == expected for x in binding.get('sourceIdentifiers', [])):
        # Reuse an existing pinned qualification for a documented code variant;
        # family similarity alone must not invent a new identity association.
        qualification = binding.get('associationQualification', {})
        row = catalogue[uid]
        if (binding.get('qualificationSHA256') != digest(qualification)
                or qualification.get('state') not in {'qualified_edition_variant', 'verified_source_identity'}
                or qualification.get('catalogueItemId') != row['Id']
                or qualification.get('registerId', '').strip() != row['sourceDocumentId'].strip()
                or label(qualification.get('registerTitle')) != label(row['sourceTitle'])
                or qualification.get('sourceIdentifiers') != binding.get('sourceIdentifiers')
                or not (qualification.get('basis') or qualification.get('qualification'))):
            raise ValueError('Capture identifier family differs without pinned prior qualification')


def numeric_version(value):
    parts = [int(v) for v in value.split('.')]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return '.'.join(map(str, parts))


def edition_review(source):
    text = source['text']
    if hashlib.sha256(text.encode()).hexdigest() != source['textSHA256']:
        raise ValueError('Edition text hash mismatch')
    version = r'Version\s*(?:No\.?|Number)?\s*[:.;]*\s*(?:No\s*)?V?(\d+(?:\.\d+)*)'
    rx = re.compile(version, re.I)
    own = []
    offset = 0
    for page, page_text in enumerate(text.split('\f'), 1):
        for line in page_text.splitlines(keepends=True):
            match = rx.search(line)
            standalone = re.fullmatch(r'\s*(?:(?:Procedure|Policy|Guideline|Protocol|Clinical Practice)\s+)?'
                                      + version + r'\s*', line, re.I)
            if match and (re.search(r'Effective\s*From', line, re.I) or page == 1 and standalone):
                quote = line.rstrip('\r\n')
                own.append(dict(page=page, start=offset, end=offset+len(quote), quote=quote,
                                edition=match[1], normalizedEdition=numeric_version(match[1])))
            offset += len(line)
        offset += 1  # Preserve form-feed offsets, including blank trailing pages.
    editions = sorted({a['normalizedEdition'] for a in own})
    stable = len(editions) == 1 and len(own) >= 2
    return dict(kind='retained_source_edition_assertion_review',
                originalSHA256=source['originalSHA256'], textSHA256=source['textSHA256'],
                currentLabelAssertions=own, normalizedCurrentEditions=editions,
                state='consistent_body_edition' if stable else 'conflicting_or_insufficient_body_editions',
                retainedBodyEdition=editions[0] if stable else None,
                currentAuthorityVerified=False, sourceDocumentAmended=False,
                limitation='A consistent body edition does not repair a different edition encoded in an identifier.')
