"""Validate a scoped relationship review and prepare a conditional native transition.

Offline only. Full-text review is an attributable assertion with pinned evidence,
not inferred from literal-search results. Clinical acceptance remains separate.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppg_catalogue_relationships import digest, literal_leads, unique
from scripts.ppg_review_intelligence import validate_relationships
from scripts.ppg_retained_conflict import qualify_endpoint
from scripts.ppg_image_witness import validate_image_witness

DIMENSIONS = {'references', 'operative_dependencies', 'governance_and_handoffs', 'contradictions'}
BASE_FIELDS = {'Title', 'AssessmentKey', 'DocumentUID', 'SourceDocumentId', 'AssessmentState',
               'SourceMembership', 'SourceCount', 'ExistingOutgoingCount', 'ExistingIncomingCount',
               'EvidenceManifest', 'AssessmentComplete', 'CurrentAuthorityVerified'}
REL_FIELDS = ('RelationshipKey', 'FromDocumentUID', 'ToDocumentUID', 'FromVersion',
              'ToVersion', 'RelationshipType', 'ReviewState', 'Rationale', 'EvidenceRef')


def require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' required')
    return value


def relationship_snapshot(rows):
    unique(rows, 'RelationshipKey')
    projected = [{k: row[k] for k in REL_FIELDS} for row in rows]
    for row in projected:
        for field in ('FromDocumentUID', 'ToDocumentUID', 'FromVersion', 'ToVersion', 'Rationale'):
            require_text(row[field], field)
    validate_relationships([dict(relationshipId=r['RelationshipKey'], fromDocumentUID=r['FromDocumentUID'],
        toDocumentUID=r['ToDocumentUID'], fromVersion=r['FromVersion'], toVersion=r['ToVersion'],
        type=r['RelationshipType'], status=r['ReviewState'].lower()) for r in projected])
    return sorted(projected, key=lambda r: r['RelationshipKey'])


def catalogue_snapshot(rows):
    unique(rows, 'DocumentUID')
    return sorted([{k: row[k] for k in ('DocumentUID', 'sourceDocumentId', 'sourceTitle')}
                   for row in rows], key=lambda r: r['DocumentUID'])


def relevant_relationships(rows, uid, version):
    return [r for r in rows if (r['FromDocumentUID'], r['FromVersion']) == (uid, version)
            or (r['ToDocumentUID'], r['ToVersion']) == (uid, version)]


def validate_passage(passage, text):
    start, end = passage.get('start'), passage.get('end')
    if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text)
            or text[start:end] != passage.get('quote')):
        raise ValueError('Passage offsets/text mismatch')


def prepare_completion(base, packet, catalogue, relationships, original_bytes, text_bytes,
                      endpoint_sources=None):
    """Return one sealed, replayable patch; no native or source writes."""
    if packet.get('schemaVersion') != 1:
        raise ValueError('Supported review packet version required')
    if not isinstance(base, dict) or not BASE_FIELDS <= base.keys() or type(base.get('Id')) is not int:
        raise ValueError('Complete native assessment preimage required')
    if base['AssessmentComplete'] is not False or base['AssessmentState'] != 'Needs relationship review':
        raise ValueError('Only an evidence-ready progress record can be completed')
    if base['CurrentAuthorityVerified'] is not False:
        raise ValueError('This transition cannot alter or infer authority')
    before = {k: copy.deepcopy(base[k]) for k in sorted(BASE_FIELDS)}
    manifest = json.loads(base['EvidenceManifest'])
    if not isinstance(manifest, dict) or manifest.get('completedAssessment'):
        raise ValueError('Existing completed evidence must be preserved')
    uid = base['DocumentUID']
    source = packet['source']
    if source.get('documentUID') != uid:
        raise ValueError('Subject identity mismatch')
    sha = hashlib.sha256(original_bytes).hexdigest()
    text_sha = hashlib.sha256(text_bytes).hexdigest()
    if source.get('originalSHA256') != sha or source.get('textSHA256') != text_sha:
        raise ValueError('Original/text bytes differ from review pins')
    version = require_text(source.get('sourceVersion'), 'Source version')
    matches = [s for s in manifest.get('sources', []) if s.get('originalSHA256') == sha
               and s.get('textSHA256') == text_sha and s.get('sourceVersion') == version]
    if len(matches) != 1 or matches[0].get('versionConflict') or matches[0].get('extractionError'):
        raise ValueError('Source absent, ambiguous or held in native preimage')
    if matches[0].get('documentUID') != uid or matches[0].get('identityState') not in {
        'exact_register_identifier', 'verified_source_identity', 'qualified_edition_variant'
    }:
        raise ValueError('Native subject source identity is not qualified')
    text = text_bytes.decode('utf-8')
    if not text.strip():
        raise ValueError('Empty source text')
    snapshot = catalogue_snapshot(catalogue)
    rels = relationship_snapshot(relationships)
    scope = packet['scope']
    if scope.get('kind') not in {'retained-edition-text-review', 'fictional-qualification'}:
        raise ValueError('Explicit supported review scope required')
    if (scope['kind'] == 'fictional-qualification') != (manifest.get('fictionalQualification') is True):
        raise ValueError('Fictional/real assessment boundary mismatch')
    if scope.get('catalogueSHA256') != digest(snapshot) or scope.get('relationshipsSHA256') != digest(rels):
        raise ValueError('Comparison/relationship snapshot changed')
    expected_uids = sorted(r['DocumentUID'] for r in snapshot)
    if sorted(scope.get('comparisonDocumentUIDs', [])) != expected_uids:
        raise ValueError('Comparison scope must account for every catalogue identity exactly once')
    if uid not in expected_uids:
        raise ValueError('Subject missing from comparison catalogue')
    limitations = scope.get('limitations')
    if not isinstance(limitations, list) or not limitations or any(not isinstance(s, str) or not s.strip() for s in limitations):
        raise ValueError('Explicit scope limitations required')
    require_text(scope.get('exclusionsRationale'), 'Comparison exclusions rationale')
    review = packet['review']
    require_text(review.get('reviewerRef'), 'Attributable reviewer/method actor')
    require_text(review.get('method'), 'Review method')
    when = datetime.fromisoformat(require_text(review.get('reviewedAtUtc'), 'Review timestamp').replace('Z', '+00:00'))
    if when.utcoffset() is None or when.utcoffset().total_seconds() != 0 or when > datetime.now(timezone.utc):
        raise ValueError('Valid non-future UTC review time required')
    if review.get('basis') != 'full-text-and-operative-review':
        raise ValueError('A literal scan alone cannot complete a review')
    # Ranges are the recorded inspection scope, not automatic proof of human judgement.
    cursor = 0
    for section in review.get('sections', []):
        if type(section.get('start')) is not int or section['start'] != cursor or type(section.get('end')) is not int or not cursor < section['end'] <= len(text):
            raise ValueError('Full-text inspection ranges have a gap/overlap')
        require_text(section.get('notes'), 'Section review note')
        cursor = section['end']
    if cursor != len(text):
        raise ValueError('Full source text was not accounted for')
    dimensions = review.get('dimensions', {})
    if set(dimensions) != DIMENSIONS:
        raise ValueError('All reference/operative/governance/contradiction dimensions required')
    for dimension in dimensions.values():
        require_text(dimension.get('notes'), 'Dimension review rationale')
        passages = dimension.get('passages')
        if not isinstance(passages, list) or not passages:
            raise ValueError('Each review dimension needs inspected source passages')
        for passage in passages:
            validate_passage(passage, text)
    computed = literal_leads(catalogue, dict(documentUID=uid, text=text, textSHA256=text_sha,
                                            originalSHA256=sha, sourceVersion=version))
    expected_leads = {digest(lead): lead for lead in computed}
    reviewed = unique(review.get('leadDispositions', []), 'leadKey')
    if set(reviewed) != set(expected_leads):
        raise ValueError('Every generated lead needs exactly one recorded disposition')
    live = {r['RelationshipKey']: r for r in relevant_relationships(rels, uid, version)
            if r['ReviewState'] in {'Proposed', 'Accepted'}}
    if packet.get('result') == 'no_relationship_identified_within_scope' and live:
        raise ValueError('No-finding conflicts with existing exact-edition relationships')
    reviewed_existing = unique(review.get('existingRelationshipDispositions', []), 'relationshipKey')
    if set(reviewed_existing) != set(live):
        raise ValueError('Every existing active exact-edition link must be accounted for')
    for entry in reviewed_existing.values():
        require_text(entry.get('rationale'), 'Existing relationship rationale')
        if entry.get('disposition') != 'retained-as-finding':
            raise ValueError('This route cannot reject or supersede existing relationship decisions')
    findings = packet.get('findingRelationshipKeys')
    if not isinstance(findings, list) or len(set(findings)) != len(findings) or any(k not in live for k in findings):
        raise ValueError('Findings must be saved exact-edition relationship records')
    for key in findings:
        row = live[key]
        if any(row[field] not in expected_uids for field in ('FromDocumentUID', 'ToDocumentUID')):
            raise ValueError('Finding endpoint identity is unresolved')
    if findings:
        # Version strings in relationship rows are assertions, not proof. Bind
        # each side to a uniquely identified retained source and cited text.
        # In this route a retained edition token is the SHA256 of the original
        # bytes; other version schemes must first be normalized by a qualified
        # source adapter rather than accepted as caller-supplied labels.
        endpoint_sources = endpoint_sources or []
        if not isinstance(endpoint_sources, list):
            raise ValueError('Endpoint sources must be a qualified record list')
        catalogue_by_uid = {row['DocumentUID']: row for row in snapshot}
        source_document_ids = [row['sourceDocumentId'] for row in snapshot]
        source_index = {}
        for endpoint in endpoint_sources:
            if not isinstance(endpoint, dict):
                raise ValueError('Endpoint source record must be an object')
            identity = (endpoint.get('documentUID'), endpoint.get('sourceVersion'))
            if (not all(isinstance(value, str) and value.strip() for value in identity)
                    or endpoint['documentUID'] not in catalogue_by_uid):
                raise ValueError('Endpoint catalogue identity/edition required')
            if identity in source_index:
                raise ValueError('Endpoint source identity/edition is ambiguous')
            original = endpoint.get('original_bytes')
            endpoint_text_bytes = endpoint.get('text_bytes')
            if not isinstance(original, bytes) or not isinstance(endpoint_text_bytes, bytes):
                raise ValueError('Endpoint original/text bytes required')
            if not original or not endpoint_text_bytes:
                raise ValueError('Endpoint original and inspection text must be nonempty')
            original_sha = hashlib.sha256(original).hexdigest()
            endpoint_text_sha = hashlib.sha256(endpoint_text_bytes).hexdigest()
            if (endpoint.get('originalSHA256') != original_sha
                    or endpoint.get('textSHA256') != endpoint_text_sha):
                raise ValueError('Endpoint original/text bytes differ from qualified pins')
            if endpoint['sourceVersion'] != 'retained-sha256:' + original_sha:
                raise ValueError('Endpoint edition token is not bound to original bytes')
            catalogue_identity = catalogue_by_uid[endpoint['documentUID']]
            require_text(catalogue_identity['sourceDocumentId'], 'Endpoint catalogue source identifier')
            if (endpoint.get('sourceDocumentId') != catalogue_identity['sourceDocumentId']
                    or source_document_ids.count(endpoint['sourceDocumentId']) != 1):
                raise ValueError('Endpoint source identifier does not uniquely bind to catalogue UID')
            if endpoint.get('extractionError') or (endpoint.get('versionConflict') and not qualify_endpoint(endpoint, catalogue=catalogue)):
                raise ValueError('Endpoint edition/source remains held')
            if endpoint.get('identityState') not in {
                    'exact_register_identifier', 'qualified_edition_variant', 'verified_source_identity'}:
                raise ValueError('Endpoint identity is not qualified')
            source_index[identity] = endpoint
        subject_endpoint = source_index.get((uid, version))
        if findings and (subject_endpoint is None
                or subject_endpoint.get('originalSHA256') != sha
                or subject_endpoint.get('textSHA256') != text_sha
                or subject_endpoint.get('original_bytes') != original_bytes
                or subject_endpoint.get('text_bytes') != text_bytes):
            raise ValueError('Subject endpoint evidence differs from the reviewed source bytes')
        endpoint_reviews = {}
        endpoint_evidence = review.get('endpointEvidence', [])
        if not isinstance(endpoint_evidence, list):
            raise ValueError('Endpoint evidence must be a passage record list')
        for entry in endpoint_evidence:
            if not isinstance(entry, dict):
                raise ValueError('Endpoint evidence record must be an object')
            identity = (entry.get('documentUID'), entry.get('sourceVersion'))
            if not all(isinstance(value, str) and value.strip() for value in identity) or identity in endpoint_reviews:
                raise ValueError('Missing or duplicate endpoint evidence identity/edition')
            endpoint_reviews[identity] = entry
        for key in findings:
            row = live[key]
            for uid_field, version_field in (('FromDocumentUID', 'FromVersion'), ('ToDocumentUID', 'ToVersion')):
                identity = (row[uid_field], row[version_field])
                evidence = endpoint_reviews.get(identity)
                source_evidence = source_index.get(identity)
                if evidence is None or source_evidence is None:
                    raise ValueError('Finding endpoint UID/edition lacks qualified source evidence')
                if (evidence.get('sourceDocumentId') != source_evidence['sourceDocumentId']
                        or evidence.get('originalSHA256') != source_evidence['originalSHA256']
                        or evidence.get('textSHA256') != source_evidence['textSHA256']):
                    raise ValueError('Finding endpoint evidence does not match qualified edition bytes')
                if source_evidence.get('versionConflict') and evidence.get('retainedConflictQualification') != source_evidence.get('retainedConflictQualification'):
                    raise ValueError('Conflict qualification must be retained in endpoint evidence')
                try:
                    endpoint_text = source_evidence['text_bytes'].decode('utf-8')
                except UnicodeDecodeError as error:
                    raise ValueError('Endpoint inspection text must be UTF-8') from error
                passages = evidence.get('passages', [])
                visuals = evidence.get('visualWitnesses', [])
                if not isinstance(passages, list) or not isinstance(visuals, list) or not (passages or visuals):
                    raise ValueError('Finding endpoint requires cited passages or visual witnesses')
                for passage in passages:
                    validate_passage(passage, endpoint_text)
                for witness in visuals:
                    validate_image_witness(witness, source_evidence['original_bytes'])
                if visuals:
                    try:
                        ref = json.loads(row['EvidenceRef'])
                        side = 'source' if uid_field == 'FromDocumentUID' else 'target'
                        citation = ref[side]
                        matches = [w for w in visuals if citation.get('imageWitnessSHA256') == digest(w)
                                   and citation.get('quote') == w['transcription']]
                    except (ValueError, KeyError, TypeError, AttributeError):
                        matches = []
                    if not matches:
                        raise ValueError('Relationship must bind exact visual witness and transcription')
    for entry in reviewed.values():
        require_text(entry.get('rationale'), 'Lead disposition rationale')
        if entry.get('disposition') not in {'not-a-relationship', 'linked-finding'}:
            raise ValueError('Unresolved retrieval leads prevent completion')
        if entry['disposition'] == 'linked-finding':
            keys = entry.get('relationshipKeys', [])
            if not keys or any(k not in findings for k in keys):
                raise ValueError('Lead finding must resolve to saved relationship evidence')
            lead = expected_leads[entry['leadKey']]
            if any((live[k]['ToDocumentUID'] if live[k]['FromDocumentUID'] == uid else live[k]['FromDocumentUID']) not in lead['targetCandidates'] for k in keys):
                raise ValueError('Lead relationship target mismatch')
    result = packet.get('result')
    if result == 'no_relationship_identified_within_scope':
        if findings or live or any(e['disposition'] != 'not-a-relationship' for e in reviewed.values()):
            raise ValueError('No-finding conflicts with existing or reviewed relationships')
        state = 'Assessed with no finding'
    elif result == 'relationships_identified':
        if not findings or set(findings) != set(live):
            raise ValueError('Positive assessment must retain all active exact-edition findings')
        state = 'Assessed with candidates'
    else:
        raise ValueError('Explicit scoped assessment result required')
    require_text(packet.get('conclusion'), 'Assessment conclusion')
    evidence = copy.deepcopy(packet)
    evidence.update(schemaVersion=1, literalLeadCount=len(computed), currentAuthorityVerified=False,
                    establishesCompliance=False, clinicalAcceptance=None,
                    priorEvidenceManifestSHA256=hashlib.sha256(base['EvidenceManifest'].encode()).hexdigest())
    key = digest(evidence)
    evidence['completionKey'] = key
    manifest['completedAssessment'] = evidence
    patch = dict(AssessmentState=state, AssessmentComplete=True, CurrentAuthorityVerified=False,
                 EvidenceManifest=json.dumps(manifest, ensure_ascii=False, sort_keys=True),
                 ExistingOutgoingCount=sum(r['FromDocumentUID'] == uid for r in rels),
                 ExistingIncomingCount=sum(r['ToDocumentUID'] == uid for r in rels))
    after = before | patch
    return dict(schemaVersion=2, kind='validated_relationship_assessment_completion',
                itemId=base['Id'], assessmentKey=base['AssessmentKey'], documentUID=uid,
                completionKey=key, before=before, patch=patch, after=after,
                patchSHA256=digest(patch), validation=dict(sourceBytesVerified=True,
                textBytesVerified=True, fullTextAccounted=True, allLeadsDisposed=True,
                allExistingLinksAccounted=True, endpointEditionsVerified=bool(findings),
                fictionalQualification=scope['kind']=='fictional-qualification'),
                nativeWrites=0)


def write_private_result(path, result):
    """Create a new local review artifact with owner-only permissions."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'packet', 'catalogue', 'relationships', 'original', 'text', 'output'):
        parser.add_argument('--'+name, required=True, type=Path)
    parser.add_argument('--endpoint-sources', type=Path,
                        help='JSON qualified endpoint sources with documentUID, unique sourceDocumentId, retained-sha256 sourceVersion, original/text paths, hashes and identity state')
    args = parser.parse_args()
    load = lambda path: json.loads(path.read_text())
    endpoint_sources = []
    if args.endpoint_sources:
        for endpoint in load(args.endpoint_sources):
            endpoint_sources.append({**{k: v for k, v in endpoint.items() if k not in {'original', 'text'}},
                                     'original_bytes': Path(endpoint['original']).read_bytes(),
                                     'text_bytes': Path(endpoint['text']).read_bytes()})
    result = prepare_completion(load(args.base), load(args.packet), load(args.catalogue),
                                load(args.relationships), args.original.read_bytes(), args.text.read_bytes(),
                                endpoint_sources=endpoint_sources)
    write_private_result(args.output, result)
    print(json.dumps({'validated': True, 'state': result['patch']['AssessmentState'],
                      'fictionalQualification': result['validation']['fictionalQualification'], 'nativeWrites': 0}))


if __name__ == '__main__':
    main()
