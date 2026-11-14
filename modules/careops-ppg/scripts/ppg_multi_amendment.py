"""Compile a retained multi-edition amendment without native writes.

The pending baseline is synthetic and never sent to the native list. The original
completed preimage and history remain immutable; each supplied edition must pass
all ordinary completion checks against the current full graph and catalogue.
"""
import copy
import hashlib
import json

from scripts.ppg_catalogue_relationships import digest
from scripts.ppg_completed_relationship_assessment import BASE_FIELDS, relationship_snapshot
from scripts.ppg_multi_edition import prepare_multi_completion

_VOLATILE_NATIVE_FIELDS = {'__metadata', 'Modified', 'EditorId', 'OData__UIVersionString'}
_TEXT_FIELDS = {'Title', 'AssessmentKey', 'DocumentUID', 'SourceDocumentId', 'AssessmentState', 'SourceMembership', 'EvidenceManifest'}
_COUNT_FIELDS = {'SourceCount', 'ExistingOutgoingCount', 'ExistingIncomingCount'}
_DYNAMIC = {'completedAssessment', 'assessmentReviewAddenda', 'relationshipInventoryReconciliations',
            'assessmentHistoryArchives', 'existingIncomingKeys', 'existingOutgoingKeys'}


def _sha_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def prepare_multi_amendment(base, companions, catalogue, relationships, max_manifest_bytes):
    """Return a sealed schema-v2 amendment tied to the exact selected native fields.

    After lossless archive compaction call again with the new exact native preimage;
    never change only the old envelope's manifest hash. No writes are performed.
    """
    if not isinstance(base, dict) or not BASE_FIELDS <= base.keys() or type(base.get('Id')) is not int or base['Id'] < 1:
        raise ValueError('Complete assessment preimage required')
    extra = set(base) - BASE_FIELDS - {'Id'} - _VOLATILE_NATIVE_FIELDS
    if extra:
        raise ValueError('Project native record to assessment fields before compilation')
    if any(not isinstance(base[k], str) or not base[k].strip() for k in _TEXT_FIELDS):
        raise ValueError('Nonempty scalar text assessment fields required')
    if any(type(base[k]) is not int or base[k] < 0 for k in _COUNT_FIELDS):
        raise ValueError('Nonnegative scalar integer assessment counts required')
    if any(type(base[k]) is not bool for k in ('AssessmentComplete','CurrentAuthorityVerified')):
        raise ValueError('Boolean assessment flags required')
    if base['AssessmentComplete'] is not True or base['CurrentAuthorityVerified'] is not False or base['AssessmentState'] not in {'Assessed with candidates', 'Assessed with no finding'}:
        raise ValueError('Completed non-authoritative assessment required')
    if type(max_manifest_bytes) is not int or max_manifest_bytes < 1:
        raise ValueError('Positive known manifest byte limit required')
    manifest_text = base['EvidenceManifest']
    if not isinstance(manifest_text, str):
        raise ValueError('Exact manifest text required')
    manifest = json.loads(manifest_text)
    if not isinstance(manifest, dict):
        raise ValueError('Manifest object required')
    old = manifest.get('completedAssessment')
    if not isinstance(old, dict) or old.get('kind') != 'multi-retained-edition-review' or old.get('subjectUID') != base['DocumentUID'] or old.get('assessmentKey') != base['AssessmentKey']:
        raise ValueError('Original multi-edition completion required')
    original_key = old.get('completionKey')
    if not original_key or digest({k:v for k,v in old.items() if k != 'completionKey'}) != original_key:
        raise ValueError('Original multi-edition completion seal mismatch')
    if old.get('currentAuthorityVerified') is not False or old.get('establishesCompliance') is not False or old.get('clinicalAcceptance', 'missing') is not None:
        raise ValueError('Invalid original authority assertions')
    editions = old.get('editions')
    sources = manifest.get('sources')
    if not isinstance(editions, list) or not editions or not isinstance(sources, list):
        raise ValueError('Original editions and source list required')
    identity = lambda s: tuple(s.get(k) for k in ('documentUID','sourceVersion','originalSHA256','textSHA256'))
    source_ids = [identity(s) for s in sources]
    edition_ids = []
    for edition in editions:
        if not isinstance(edition, dict) or not isinstance(edition.get('source'), dict):
            raise ValueError('Invalid original edition')
        key = edition.get('completionKey')
        if not key or digest({k:v for k,v in edition.items() if k != 'completionKey'}) != key:
            raise ValueError('Original edition seal mismatch')
        edition_ids.append(identity(edition['source']))
    if len(set(source_ids)) != len(source_ids) or len(set(edition_ids)) != len(edition_ids) or set(source_ids) != set(edition_ids) or any(not all(x) or x[0] != base['DocumentUID'] for x in source_ids):
        raise ValueError('Original edition membership mismatch')
    for key in ('assessmentReviewAddenda', 'relationshipInventoryReconciliations', 'assessmentHistoryArchives'):
        if key in manifest and not isinstance(manifest[key], list):
            raise ValueError('Invalid history array: ' + key)
    pending = {k:copy.deepcopy(base[k]) for k in BASE_FIELDS | {'Id'}}
    pending['AssessmentComplete'] = False
    pending['AssessmentState'] = 'Needs relationship review'
    pending['EvidenceManifest'] = json.dumps({k:v for k,v in manifest.items() if k not in _DYNAMIC}, ensure_ascii=False, sort_keys=True)
    transition = prepare_multi_completion(pending, companions, catalogue, relationships)
    graph = relationship_snapshot(relationships)
    # ECMAScript Array.sort uses UTF-16 code units rather than Python code points.
    js_sort = lambda values: sorted(values, key=lambda s:s.encode('utf-16-be', errors='surrogatepass'))
    uid = base['DocumentUID']
    entry = dict(kind='multi-edition-revalidation', priorCompletionKey=original_key,
        priorCompletionEvidenceSHA256=digest(old), transition=transition,
        expectedEvidenceManifestSHA256=_sha_text(manifest_text),
        expectedAssessmentState=base['AssessmentState'], expectedIncomingCount=base['ExistingIncomingCount'],
        expectedOutgoingCount=base['ExistingOutgoingCount'],
        incomingKeys=js_sort([r['RelationshipKey'] for r in graph if r['ToDocumentUID']==uid]),
        outgoingKeys=js_sort([r['RelationshipKey'] for r in graph if r['FromDocumentUID']==uid]))
    entry['amendmentKey'] = digest(entry)
    before = {k:copy.deepcopy(base[k]) for k in sorted(BASE_FIELDS | {'Id'})}
    return dict(kind='assessment_evidence_amendment', schemaVersion=2, itemId=base['Id'],
        assessmentKey=base['AssessmentKey'], documentUID=uid, before=before,
        expectedEvidenceManifestSHA256=entry['expectedEvidenceManifestSHA256'],
        maxManifestBytes=max_manifest_bytes, amendment=entry)
