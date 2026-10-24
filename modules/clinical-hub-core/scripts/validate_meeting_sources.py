#!/usr/bin/env python3
"""Classify meeting-source mapping gaps without selecting or approving sources."""
import argparse
from datetime import date, datetime
import json
from pathlib import Path
import re


FIELDS = {
    'candidate_id', 'document_meeting_date', 'folder_meeting_date',
    'stored_folder_key', 'expected_folder_key', 'source_state',
    'candidate_version_id', 'confirmation_state', 'confirmed_version_id',
    'source_ref', 'confirmation_ref', 'reviewer_alias', 'reviewed_at',
}
SOURCE_STATES = {'draft', 'unknown', 'reviewed_candidate'}
CONFIRMATION_STATES = {'blank', 'meeting_only', 'exact_version'}
OPS_REF = re.compile(r'^opsref:[A-Z0-9][A-Z0-9._#-]{1,63}$', re.I)
CONTEXT_ALIAS = re.compile(r'^ctx_[a-z0-9_]{2,24}$', re.I)
HOLD_GUIDANCE = {
    'hold_candidate_id_ambiguous': 'Replace surrounding whitespace only after confirming the stable local review key; retain the original declaration in the review record.',
    'hold_candidate_id_unknown': 'Assign a unique local review key without treating it as an issued meeting or action ID.',
    'hold_candidate_version_unknown': 'Identify the exact candidate file/version from the approved source route; do not infer it from a filename.',
    'hold_candidate_version_ambiguous': 'Re-read the candidate version identifier from the source and preserve its exact value.',
    'hold_confirmation_state_unknown': 'Classify the prior-minutes confirmation as blank, meeting-only, or exact-version using the evidence reference.',
    'hold_confirmation_version_unknown': 'Locate the exact version ID named by the confirmation, or leave the row held.',
    'hold_confirmation_version_ambiguous': 'Re-read the confirmed version identifier and preserve its exact value.',
    'hold_confirmation_version_mismatch': 'Compare the candidate and confirmed version IDs against the cited sources; do not select either version automatically.',
    'hold_confirmation_metadata_conflict': 'Reconcile why a version ID was supplied when confirmation is not exact-version.',
    'hold_confirmation_evidence_ref_unknown': 'Add an opaque reference to the existing private evidence record for the confirmation, or keep it unresolved.',
    'hold_confirmation_evidence_ref_conflict': 'Reconcile the supplied confirmation reference with the declared confirmation state.',
    'hold_reviewer_provenance_missing': 'Reconcile the reviewer declaration against the existing restricted review record; do not clear this hold by changing only the source-state label.',
    'hold_folder_identity_ambiguous': 'Recheck the stored and expected folder keys without trimming them into a match.',
    'hold_folder_identity_conflict': 'Compare the stored and expected folder references and resolve the mismatch against the source.',
    'hold_document_date_unknown': 'Read the document meeting date from the candidate source or retain it as unknown.',
    'hold_folder_date_unknown': 'Read the meeting date associated with the storage folder or retain it as unknown.',
    'hold_folder_date_conflict': 'Reconcile document and folder dates; do not choose one by precedence or filename.',
    'hold_source_state_unresolved': 'Determine whether the candidate is a draft or has been reviewed, using the referenced source record.',
    'hold_confirmation_blank': 'Locate version-bound confirmation evidence or leave prior-minutes confirmation blank.',
    'hold_confirmation_not_version_bound': 'Link the confirmation to the exact candidate version before treating it as reviewed.',
    'hold_duplicate_candidate_id': 'Give each candidate a unique local review key; retain and reconcile every row separately.',
}


def optional_date(value, label):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f'{label} must be an ISO date or null.')
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f'{label} must be an ISO date or null.') from error
    if parsed.isoformat() != value:
        raise ValueError(f'{label} must be an ISO date or null.')
    return parsed


def opaque_reference(value, label, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not OPS_REF.fullmatch(value) or not any(ch.isdigit() for ch in value):
        raise ValueError(f'{label} must be an opaque opsref identifier.')


def zoned_timestamp(value):
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None
    except (ValueError, TypeError, AttributeError):
        return False


def assess(candidate):
    optional_fields = {
        'candidate_version_id', 'confirmed_version_id', 'confirmation_ref',
        'reviewer_alias', 'reviewed_at',
    }
    required_fields = FIELDS - optional_fields
    if (not isinstance(candidate, dict) or not required_fields.issubset(candidate)
            or not set(candidate).issubset(FIELDS)):
        raise ValueError('Each candidate must contain exactly the documented source-review fields.')
    ident = candidate['candidate_id']
    if not isinstance(ident, str):
        raise ValueError('Candidate ID must be text.')
    document_date = optional_date(candidate['document_meeting_date'], 'Document meeting date')
    folder_date = optional_date(candidate['folder_meeting_date'], 'Folder meeting date')
    stored_folder = candidate['stored_folder_key']
    expected_folder = candidate['expected_folder_key']
    if not isinstance(stored_folder, str) or not stored_folder.strip():
        raise ValueError('Stored folder key must be explicit.')
    if not isinstance(expected_folder, str) or not expected_folder.strip():
        raise ValueError('Expected folder key must be explicit.')
    source_state = candidate['source_state']
    candidate_version = candidate.get('candidate_version_id')
    confirmation = candidate['confirmation_state']
    version_id = candidate.get('confirmed_version_id')
    source_ref = candidate['source_ref']
    confirmation_ref = candidate.get('confirmation_ref')
    reviewer_alias = candidate.get('reviewer_alias')
    reviewed_at = candidate.get('reviewed_at')
    if not isinstance(source_state, str):
        raise ValueError('Source state must be text.')
    if not isinstance(confirmation, str):
        raise ValueError('Confirmation state must be text.')
    if candidate_version is not None and not isinstance(candidate_version, str):
        raise ValueError('Candidate version ID must be text or null.')
    if version_id is not None and not isinstance(version_id, str):
        raise ValueError('Confirmed version ID must be text or null.')
    opaque_reference(source_ref, 'Source reference')
    opaque_reference(confirmation_ref, 'Confirmation reference', nullable=True)
    if reviewer_alias is not None and (not isinstance(reviewer_alias, str) or not CONTEXT_ALIAS.fullmatch(reviewer_alias)):
        raise ValueError('Reviewer alias must be a context alias or null.')
    if reviewed_at is not None and (not isinstance(reviewed_at, str) or not zoned_timestamp(reviewed_at)):
        raise ValueError('Review time must be an ISO timestamp with a timezone or null.')

    holds = []

    def hold(reason):
        if reason not in holds:
            holds.append(reason)

    if not ident.strip():
        hold('hold_candidate_id_unknown')
    elif ident != ident.strip():
        hold('hold_candidate_id_ambiguous')
    if candidate_version is None or not candidate_version.strip():
        hold('hold_candidate_version_unknown')
    elif candidate_version != candidate_version.strip():
        hold('hold_candidate_version_ambiguous')
    if confirmation not in CONFIRMATION_STATES:
        hold('hold_confirmation_state_unknown')
    elif confirmation == 'exact_version':
        if version_id is None or not version_id.strip():
            hold('hold_confirmation_version_unknown')
        elif version_id != version_id.strip():
            hold('hold_confirmation_version_ambiguous')
        elif candidate_version is not None and candidate_version == candidate_version.strip() and candidate_version != version_id:
            hold('hold_confirmation_version_mismatch')
    elif version_id is not None:
        hold('hold_confirmation_metadata_conflict')
    if confirmation in {'meeting_only', 'exact_version'} and confirmation_ref is None:
        hold('hold_confirmation_evidence_ref_unknown')
    elif confirmation == 'blank' and confirmation_ref is not None:
        hold('hold_confirmation_evidence_ref_conflict')

    if stored_folder != stored_folder.strip() or expected_folder != expected_folder.strip():
        hold('hold_folder_identity_ambiguous')
    elif stored_folder.casefold() != expected_folder.casefold():
        hold('hold_folder_identity_conflict')
    if document_date is None:
        hold('hold_document_date_unknown')
    if folder_date is None:
        hold('hold_folder_date_unknown')
    elif document_date is not None and folder_date != document_date:
        hold('hold_folder_date_conflict')
    if source_state not in SOURCE_STATES or source_state != 'reviewed_candidate':
        hold('hold_source_state_unresolved')
    elif reviewer_alias is None or reviewed_at is None:
        hold('hold_reviewer_provenance_missing')
    if confirmation == 'blank':
        hold('hold_confirmation_blank')
    elif confirmation == 'meeting_only':
        hold('hold_confirmation_not_version_bound')

    outcome = holds[0] if holds else 'structurally_consistent_human_review_required'
    return {
        'candidate_id': ident,
        'source_ref': source_ref,
        'confirmation_ref': confirmation_ref,
        'document_meeting_date': candidate['document_meeting_date'],
        'folder_meeting_date': candidate['folder_meeting_date'],
        'stored_folder_key': stored_folder,
        'expected_folder_key': expected_folder,
        'source_state': source_state,
        'reviewer_alias': reviewer_alias,
        'reviewed_at': reviewed_at,
        'candidate_version_id': candidate_version,
        'confirmation_state': confirmation,
        'confirmed_version_id': version_id,
        'outcome': outcome,
        'hold_reasons': holds,
        'next_checks': [HOLD_GUIDANCE[reason] for reason in holds],
        'selected': False,
        'approved': False,
    }


def validate(data):
    if not isinstance(data, dict) or set(data) != {'candidates'}:
        raise ValueError('Input must contain exactly the candidates array.')
    candidates = data['candidates']
    if not isinstance(candidates, list) or not candidates:
        raise ValueError('At least one candidate is required.')
    assessed = [assess(candidate) for candidate in candidates]
    counts = {}
    for result in assessed:
        key = result['candidate_id'].strip().casefold()
        counts[key] = counts.get(key, 0) + 1
    results = []
    for index, result in enumerate(assessed, start=1):
        key = result['candidate_id'].strip().casefold()
        result['candidate_index'] = index
        if counts[key] > 1:
            if 'hold_duplicate_candidate_id' not in result['hold_reasons']:
                result['hold_reasons'].append('hold_duplicate_candidate_id')
            if result['outcome'] == 'structurally_consistent_human_review_required':
                result['outcome'] = 'hold_duplicate_candidate_id'
            result['next_checks'] = [HOLD_GUIDANCE[reason] for reason in result['hold_reasons']]
        results.append(result)
    return {'status': 'REVIEW_REQUIRED', 'candidates': results,
            'selected': 0, 'approved': 0,
            'authority': 'Local structural classification only; evidence references, reviewer aliases/times, source/version IDs, folder keys, dates and confirmation states are supplied declarations, not authenticated sources, identity, authority, review or approval evidence.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_path', type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.json_path.read_text(encoding='utf-8'), object_pairs_hook=unique_object))
    except OSError:
        parser.error('Source review file-access error.')
    except UnicodeError:
        parser.error('Source review text encoding is invalid.')
    except json.JSONDecodeError:
        parser.error('Source review JSON is invalid.')
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key.')
        result[key] = value
    return result


if __name__ == '__main__':
    main()
