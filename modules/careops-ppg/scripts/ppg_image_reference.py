"""Create an offline reference proposal from a qualified visual witness.

The reviewer attests transcription and interpretation. No policy authority or
exact cited-edition claim follows from matching a documentary identifier.
"""
import hashlib
import json
from scripts.ppg_catalogue_relationships import digest, relationship_key
from scripts.ppg_retained_conflict import qualify_endpoint
from scripts.ppg_image_witness import validate_image_witness


def image_reference_proposal(source, target, witness, target_quote, rationale, catalogue):
    for endpoint in (source, target):
        if not isinstance(endpoint, dict):
            raise ValueError('Endpoint object required')
        original, text = endpoint.get('original_bytes'), endpoint.get('text_bytes')
        if not isinstance(original, bytes) or not isinstance(text, bytes):
            raise ValueError('Exact endpoint bytes required')
        sha = hashlib.sha256(original).hexdigest()
        if endpoint.get('originalSHA256') != sha or endpoint.get('textSHA256') != hashlib.sha256(text).hexdigest() or endpoint.get('sourceVersion') != 'retained-sha256:' + sha:
            raise ValueError('Endpoint version or byte hash mismatch')
        matches = [x for x in catalogue if x.get('DocumentUID') == endpoint.get('documentUID') and x.get('sourceDocumentId') == endpoint.get('sourceDocumentId')]
        if (len(matches) != 1 or sum(x.get('DocumentUID') == endpoint.get('documentUID') for x in catalogue) != 1
                or sum(x.get('sourceDocumentId') == endpoint.get('sourceDocumentId') for x in catalogue) != 1
                or not isinstance(endpoint.get('sourceDocumentId'), str) or not endpoint['sourceDocumentId'].strip()
                or endpoint.get('identityState') not in {'exact_register_identifier', 'qualified_edition_variant', 'verified_source_identity'} or endpoint.get('extractionError')):
            raise ValueError('Endpoint identity not qualified against catalogue')
        if endpoint.get('versionConflict') and not qualify_endpoint(endpoint, catalogue=catalogue):
            raise ValueError('Conflict endpoint must be family qualified')
    try:
        text = target['text_bytes'].decode('utf-8')
    except UnicodeDecodeError as error:
        raise ValueError('Target text must be UTF-8') from error
    if not isinstance(target_quote, str) or not target_quote.strip() or target_quote not in text:
        raise ValueError('Target passage not present in exact extracted text')
    validate_image_witness(witness, source['original_bytes'])
    identifier = witness['transcription']
    if identifier.casefold() not in target_quote.casefold():
        raise ValueError('Exact visually transcribed identifier required in target passage')
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError('Review rationale required')
    start = text.index(target_quote)
    evidence = {'source': {'documentUID': source['documentUID'], 'sourceVersion': source['sourceVersion'], 'originalSHA256': source['originalSHA256'], 'textSHA256': source['textSHA256'], 'quote': identifier, 'imageWitnessSHA256': digest(witness), 'page': witness['page']},
                'target': {'documentUID': target['documentUID'], 'sourceVersion': target['sourceVersion'], 'originalSHA256': target['originalSHA256'], 'textSHA256': target['textSHA256'], 'quote': target_quote, 'start': start, 'end': start + len(target_quote)},
                'method': 'Named visual-review witness and exact target passage; reviewer assesses document identity and any edition lineage.', 'currentAuthorityVerified': False, 'exactCitedEditionVerified': False, 'clinicalAcceptance': None, 'establishesCompliance': False}
    if source.get('versionConflict'):
        evidence['source']['retainedConflictQualification'] = source['retainedConflictQualification']
    if target.get('versionConflict'):
        evidence['target']['retainedConflictQualification'] = target['retainedConflictQualification']
    return {'Title':'Proposed retained-edition documentary relationship','RelationshipKey':relationship_key(source['documentUID'],source['sourceVersion'],target['documentUID'],target['sourceVersion'],'references'),
            'FromDocumentUID':source['documentUID'],'FromVersion':source['sourceVersion'],'ToDocumentUID':target['documentUID'],'ToVersion':target['sourceVersion'],'RelationshipType':'references','ReviewState':'Proposed','Rationale':rationale,'EvidenceRef':json.dumps(evidence,ensure_ascii=False,sort_keys=True)}
