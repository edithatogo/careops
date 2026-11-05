"""Private proposal: compose independently validated retained-edition reviews."""
import copy
import hashlib
import json
from scripts.ppg_catalogue_relationships import digest
from scripts.ppg_completed_relationship_assessment import prepare_completion, relationship_snapshot


def prepare_multi_completion(base, companions, catalogue, relationships):
    """Each companion contains packet, original_bytes, text_bytes, endpoint_sources.

    All native manifest source editions must be reviewed, and every active subject
    incident must belong to one of them. No mutation or authority assertion.
    """
    manifest = json.loads(base['EvidenceManifest'])
    sources = manifest.get('sources')
    if not isinstance(sources, list) or not sources or not isinstance(companions, list):
        raise ValueError('Nonempty manifest sources and companion list required')
    identities = [(s.get('documentUID'), s.get('sourceVersion'), s.get('originalSHA256'), s.get('textSHA256')) for s in sources]
    if len(set(identities)) != len(identities) or any(x[0] != base['DocumentUID'] or not all(x) for x in identities):
        raise ValueError('Manifest source identities must be unique and belong to subject')
    supplied = []
    outputs = []
    for c in companions:
        packet = c['packet']
        s = packet['source']
        identity = (s.get('documentUID'), s.get('sourceVersion'), s.get('originalSHA256'), s.get('textSHA256'))
        if identity in supplied or identity not in identities:
            raise ValueError('Duplicate or unrecognised companion edition')
        supplied.append(identity)
        outputs.append(prepare_completion(base, packet, catalogue, relationships,
            c['original_bytes'], c['text_bytes'], endpoint_sources=c.get('endpoint_sources')))
    if set(supplied) != set(identities):
        raise ValueError('Every manifest edition requires exactly one companion')
    versions = {x[1] for x in identities}
    uid = base['DocumentUID']
    for row in relationship_snapshot(relationships):
        if row['ReviewState'] not in {'Proposed', 'Accepted'}:
            continue
        for side in ('From', 'To'):
            if row[side+'DocumentUID'] == uid and row[side+'Version'] not in versions:
                raise ValueError('Active subject incident has an unreviewed edition')
    # Keep full independently validated evidence and the original preimage.
    evidence = {'schemaVersion': 1, 'kind': 'multi-retained-edition-review',
        'subjectUID': uid, 'assessmentKey': base['AssessmentKey'],
        'priorEvidenceManifestSHA256': hashlib.sha256(base['EvidenceManifest'].encode()).hexdigest(),
        'relationshipsSHA256': digest(relationship_snapshot(relationships)),
        'editions': [json.loads(o['patch']['EvidenceManifest'])['completedAssessment'] for o in outputs],
        'currentAuthorityVerified': False, 'establishesCompliance': False, 'clinicalAcceptance': None,
        'limitations': ['Retained-edition review only; no publisher currency, clinical acceptance or current authority established.']}
    evidence['completionKey'] = digest(evidence)
    final_manifest = copy.deepcopy(manifest)
    final_manifest['completedAssessment'] = evidence
    first = outputs[0]
    patch = copy.deepcopy(first['patch'])
    patch['AssessmentState'] = ('Assessed with candidates' if any(o['patch']['AssessmentState'] == 'Assessed with candidates' for o in outputs) else 'Assessed with no finding')
    patch['EvidenceManifest'] = json.dumps(final_manifest, ensure_ascii=False, sort_keys=True)
    return dict(schemaVersion=2, kind='validated_relationship_assessment_completion', itemId=base['Id'],
        assessmentKey=base['AssessmentKey'], documentUID=uid, completionKey=evidence['completionKey'],
        before=first['before'], patch=patch, after=first['before'] | patch, patchSHA256=digest(patch),
        validation={'allManifestEditionsIndependentlyValidated': True, 'allActiveSubjectIncidentsAccounted': True,
                    'editionCount': len(outputs)}, nativeWrites=0)
