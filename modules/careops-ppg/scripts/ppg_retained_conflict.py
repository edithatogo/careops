"""Qualify immutable documentary endpoints while preserving conflicting edition labels."""
import hashlib
import re

def qualify_endpoint(endpoint):
    """Allow conflicting *labels* only for explicitly evidenced, immutable bytes.

    This cannot qualify a subject, select an edition, or establish authority.
    The caller must also perform the compiler's ordinary UID/catalogue and byte checks.
    """
    q=endpoint.get('retainedConflictQualification')
    if not isinstance(q,dict) or q.get('kind')!='retained-family-only-v1': return False
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
    if prior.get('identityState') != 'exact_register_identifier': return False
    code=endpoint.get('sourceDocumentId')
    if not isinstance(code,str) or not code or code.casefold() not in decoded[:1500].casefold(): return False
    editions=set()
    for a in claims:
        if not isinstance(a,dict) or type(a.get('start')) is not int or type(a.get('end')) is not int: return False
        start,end=a['start'],a['end'];quote=a.get('quote');edition=a.get('edition')
        if not isinstance(quote,str) or not quote or not isinstance(edition,str) or not edition: return False
        if start<0 or end<=start or end>len(decoded) or decoded[start:end]!=quote: return False
        if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)*', edition): return False
        if not re.search(r'(?<![0-9.])'+re.escape(edition)+r'(?![0-9.])',quote): return False
        normalized=tuple(int(part) for part in edition.split('.'))
        while len(normalized)>1 and normalized[-1]==0: normalized=normalized[:-1]
        editions.add(normalized)
    return len(editions)>=2
