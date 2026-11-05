"""Read-only, conservative resolver for retained multi-edition completion evidence.

A result is documentary evidence, not authority or clinical acceptance. Archive
reconstruction verifies each immutable archive and retains append-only later
history. Detecting removal of an unanchored final event requires an external head.
"""
import copy
import hashlib
import json
from scripts.ppg_catalogue_relationships import digest
from scripts.ppg_assessment_history_archive import prepare_archive, _parse


def _sealed(value, key):
    if not isinstance(value, dict) or not value.get(key):
        raise ValueError('missing_seal')
    payload = {k: v for k, v in value.items() if k != key}
    if digest(payload) != value[key]:
        raise ValueError('seal_mismatch')


def _multi(value, uid, assessment_key):
    _sealed(value, 'completionKey')
    if (value.get('kind') != 'multi-retained-edition-review'
            or value.get('subjectUID') != uid or value.get('assessmentKey') != assessment_key
            or value.get('currentAuthorityVerified') is not False
            or value.get('establishesCompliance') is not False
            or value.get('clinicalAcceptance') is not None):
        raise ValueError('invalid_multi_completion')
    editions = value.get('editions')
    if not isinstance(editions, list) or not editions:
        raise ValueError('missing_editions')
    seen = set()
    for e in editions:
        _sealed(e, 'completionKey')
        s = e.get('source', {})
        identity = tuple(s.get(k) for k in ('documentUID', 'sourceVersion', 'originalSHA256', 'textSHA256'))
        if (not all(identity) or identity[0] != uid or identity in seen
                or e.get('currentAuthorityVerified') is not False or e.get('establishesCompliance') is not False
                or e.get('clinicalAcceptance') is not None
                or e.get('result') not in ('relationships_identified', 'no_relationship_identified_within_scope')
                or e.get('scope', {}).get('relationshipsSHA256') != value.get('relationshipsSHA256')):
            raise ValueError('invalid_edition')
        seen.add(identity)
    return value


class ArchiveUnavailable(Exception):
    pass


def _history(text, fetch, visited):
    """Reconstruct archive history using the exact archive planner contract."""
    current = _parse(text)
    refs = current.get('assessmentHistoryArchives', [])
    if not refs:
        return {k: list(current.get(k, [])) for k in ('assessmentReviewAddenda', 'relationshipInventoryReconciliations')}
    ref = refs[-1]
    if not isinstance(ref, dict) or ref.get('archiveSHA256') in visited:
        raise ValueError('duplicate_or_invalid_archive_reference')
    if fetch is None:
        raise ArchiveUnavailable()
    data = fetch(ref)
    if data is None:
        raise ArchiveUnavailable()
    if not isinstance(data, bytes) or hashlib.sha256(data).hexdigest() != ref.get('archiveSHA256'):
        raise ValueError('archive_hash_mismatch')
    archived_text = data.decode('utf-8', errors='strict')
    plan = prepare_archive(archived_text, ref.get('archiveUrl'))
    if plan is None or plan.archive_reference != ref:
        raise ValueError('archive_reference_mismatch')
    compacted = _parse(plan.compacted_manifest)
    if current.get('assessmentHistoryArchives') != compacted.get('assessmentHistoryArchives'):
        raise ValueError('archive_sequence_mismatch')
    # A subsequent amendment can update graph-key inventories and append history;
    # all other manifest fields must remain identical to the compacted preimage.
    mutable = {'assessmentReviewAddenda', 'relationshipInventoryReconciliations', 'existingIncomingKeys', 'existingOutgoingKeys'}
    if {k:v for k,v in current.items() if k not in mutable} != {k:v for k,v in compacted.items() if k not in mutable}:
        raise ValueError('archive_preimage_changed')
    previous = _history(archived_text, fetch, visited | {ref['archiveSHA256']})
    for field in ('assessmentReviewAddenda', 'relationshipInventoryReconciliations'):
        prefix, now = compacted.get(field, []), current.get(field, [])
        if now[:len(prefix)] != prefix:
            raise ValueError('history_prefix_missing_or_reordered')
        previous[field].extend(now[len(prefix):])
    return previous


def resolve(manifest_text, uid, assessment_key, fetch_archive=None):
    """Return status and evidence; never interpret a missing archive as no addendum."""
    try:
        m = json.loads(manifest_text)
        original = _multi(m['completedAssessment'], uid, assessment_key)
        identities = lambda sources: {tuple(s.get(k) for k in ('documentUID', 'sourceVersion', 'originalSHA256', 'textSHA256')) for s in sources}
        source_identities = identities(m['sources'])
        if len(source_identities) != len(m['sources']) or source_identities != identities([e['source'] for e in original['editions']]):
            raise ValueError('source_membership_mismatch')
        try:
            addenda = _history(manifest_text, fetch_archive, set())['assessmentReviewAddenda']
        except ArchiveUnavailable:
            return {'status': 'archive_unavailable', 'original': original, 'effective': None}
        except (ValueError, TypeError, UnicodeError):
            return {'status': 'archive_unverifiable', 'original': original, 'effective': None}
        keys = [e.get('amendmentKey') for e in addenda if isinstance(e, dict)]
        if len(keys) != len(addenda) or len(set(keys)) != len(keys):
            raise ValueError('duplicate_or_invalid_addendum')
        # An archive seals ordering as stored, not whether that ordering follows
        # the exact native preimage chain. No sequential-preimage proof is
        # currently supplied, so every multi-entry history fails closed.
        order_unverified = len(addenda) > 1
        current = original
        for entry in addenda:
            if entry.get('kind') != 'multi-edition-revalidation':
                raise ValueError('unsupported_amendment')
            _sealed(entry, 'amendmentKey')
            if (entry.get('priorCompletionKey') != original['completionKey']
                    or entry.get('priorCompletionEvidenceSHA256') != digest(original)):
                raise ValueError('amendment_original_mismatch')
            transition = entry['transition']
            if (transition.get('documentUID') != uid or transition.get('assessmentKey') != assessment_key
                    or digest(transition['patch']) != transition.get('patchSHA256')):
                raise ValueError('amendment_transition_mismatch')
            current = _multi(json.loads(transition['patch']['EvidenceManifest'])['completedAssessment'], uid, assessment_key)
            if identities([e['source'] for e in current['editions']]) != source_identities:
                raise ValueError('amendment_source_membership_mismatch')
            if transition.get('completionKey') != current['completionKey']:
                raise ValueError('amendment_completion_mismatch')
            positive = any(e['result'] == 'relationships_identified' for e in current['editions'])
            expected = 'Assessed with candidates' if positive else 'Assessed with no finding'
            if transition['patch'].get('AssessmentState') != expected:
                raise ValueError('amendment_result_mismatch')
        if order_unverified:
            return {'status': 'history_order_unverified', 'original': copy.deepcopy(original), 'effective': None, 'appliedAddenda': len(addenda)}
        return {'status': 'resolved', 'original': copy.deepcopy(original), 'effective': copy.deepcopy(current), 'appliedAddenda': len(addenda)}
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return {'status': 'invalid', 'reason': str(exc), 'effective': None}
