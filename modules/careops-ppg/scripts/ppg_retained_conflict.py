"""Qualify immutable documentary endpoints while preserving conflicting edition labels."""
import hashlib
import json
import re

def _versioned_family(code):
    if not isinstance(code, str):
        return None
    match = re.fullmatch(r'(.+)-V[0-9]+(?:\.[0-9]+)*(?:-.+)?', code, re.IGNORECASE)
    return match[1].casefold() if match else None


def _qualified_variant(endpoint, prior, decoded, catalogue, readback, qualification):
    """Reuse an already native-qualified family, without choosing its edition."""
    if prior.get('identityState') != 'qualified_edition_variant' or endpoint.get('identityState') != 'qualified_edition_variant':
        return False
    canonical = endpoint.get('sourceDocumentId')
    printed = qualification.get('printedSourceDocumentId')
    family = _versioned_family(canonical)
    if not family or _versioned_family(printed) != family:
        return False
    if printed.casefold() not in decoded[:1500].casefold():
        return False
    binding = prior.get('nativeCaptureBinding')
    if binding is not None:
        if not isinstance(binding, dict):
            return False
        association = binding.get('associationQualification')
        if not isinstance(association, dict):
            return False
        if (printed not in association.get('sourceIdentifiers', [])
                or printed not in binding.get('sourceIdentifiers', [])
                or binding.get('documentUID') != endpoint.get('documentUID')
                or binding.get('captureId') != readback['fields'].get('Id')
                or binding.get('nativeBytesVerified') is not True
                or binding.get('originalBytesVerified') is not True
                or binding.get('nativeSHA256') != endpoint.get('originalSHA256')
                or binding.get('originalSHA256') != endpoint.get('originalSHA256')):
            return False
    else:
        # Older captures retain their qualification on the native library item.
        try:
            metadata = json.loads(readback['fields']['PPGCaptureEditionEvidence'])
        except (KeyError, TypeError, ValueError):
            return False
        if not isinstance(metadata, dict) or metadata.get('sourceEditionIsNotNativeVersion') is not True:
            return False
        associations = metadata.get('associations')
        if not isinstance(associations, list) or printed not in metadata.get('sourceIdentifiers', []):
            return False
        candidates = [a for a in associations if isinstance(a, dict) and a.get('registerId') == canonical]
        if len(candidates) != 1 or candidates[0].get('versionConflict') is not True:
            return False
        association = candidates[0]
    if association.get('state') != 'qualified_edition_variant' or association.get('registerId') != canonical:
        return False
    if not isinstance(catalogue, list):
        return False
    matches = [row for row in catalogue if _versioned_family(row.get('sourceDocumentId')) == family]
    title = association.get('registerTitle')
    return (len(matches) == 1
            and matches[0].get('DocumentUID') == endpoint.get('documentUID')
            and matches[0].get('sourceDocumentId') == canonical
            and (title is None or (isinstance(title, str) and title.strip()
                 and str(matches[0].get('sourceTitle', '')).strip() == title.strip())))


def qualify_endpoint(endpoint, catalogue=None):
    """Allow conflicting *labels* only for explicitly evidenced, immutable bytes.

    This cannot qualify a subject, select an edition, or establish authority.
    The caller must also perform the compiler's ordinary UID/catalogue and byte checks.
    """
    q=endpoint.get('retainedConflictQualification')
    if not isinstance(q,dict) or q.get('kind') not in {'retained-family-only-v1', 'retained-qualified-variant-family-only-v2'}: return False
    if endpoint.get('versionConflict') is not True or endpoint.get('extractionError'): return False
    if q.get('appliesToRequestedEdition') is not False or q.get('currentAuthorityVerified') is not False or q.get('clinicalAcceptance','missing') is not None: return False
    data=endpoint.get('original_bytes'); text=endpoint.get('text_bytes')
    if not isinstance(data,bytes) or not isinstance(text,bytes): return False
    sha=hashlib.sha256(data).hexdigest(); th=hashlib.sha256(text).hexdigest()
    if (sha,th,endpoint.get('sourceVersion'))!=(endpoint.get('originalSHA256'),endpoint.get('textSHA256'),'retained-sha256:'+sha): return False
    readback=q.get('captureReadback'); prior=q.get('sourceManifestRecord');
    if not isinstance(readback,dict) or not isinstance(prior,dict): return False
    fields=readback.get('fields') or {}
    if readback.get('byteParity') is not True or readback.get('sha256')!=sha: return False
    if fields.get('PPGDocumentUID')!=endpoint.get('documentUID') or fields.get('PPGCaptureSHA256')!=sha: return False
    if fields.get('Id') not in prior.get('nativeCaptureIds',[]): return False
    if prior.get('versionConflict') is not True or prior.get('extractionError'): return False
    if any(prior.get(k)!=endpoint.get(k) for k in ('documentUID','sourceVersion','originalSHA256','textSHA256')): return False
    claims=q.get('versionAssertions');
    if not isinstance(claims,list) or len(claims)<2: return False
    if claims != (prior.get('versionAssertionReview') or {}).get('currentLabelAssertions'): return False
    try: decoded=text.decode('utf-8')
    except UnicodeError: return False
    if q['kind'] == 'retained-family-only-v1':
        if prior.get('identityState') != 'exact_register_identifier': return False
        code=endpoint.get('sourceDocumentId')
        if not isinstance(code,str) or not code or code.casefold() not in decoded[:1500].casefold(): return False
    elif not _qualified_variant(endpoint, prior, decoded, catalogue, readback, q):
        return False
    editions=set()
    for a in claims:
        if not isinstance(a,dict) or type(a.get('start')) is not int or type(a.get('end')) is not int: return False
        start,end=a['start'],a['end'];quote=a.get('quote');edition=a.get('edition')
        if not isinstance(quote,str) or not quote or not isinstance(edition,str) or not edition: return False
        if start<0 or end<=start or end>len(decoded) or decoded[start:end]!=quote: return False
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)*', edition): return False
        # The period in "No.3.0" belongs to the label, not a prior version part.
        # Other numeric/version prefixes must still prevent substring matches.
        if not re.search(r'(?:(?<![0-9.])|(?<=\bNo\.))'+re.escape(edition)+r'(?![0-9.])',quote,re.IGNORECASE): return False
        normalized=tuple(int(part) for part in edition.split('.'))
        while len(normalized)>1 and normalized[-1]==0: normalized=normalized[:-1]
        editions.add(normalized)
    return len(editions)>=2
