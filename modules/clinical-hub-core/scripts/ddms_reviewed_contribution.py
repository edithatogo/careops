"""Pure maker qualification for the native, explicitly reviewed DDMS handoff.

No authentication, transport or unattended runtime. The operator enters actual
work once in Recall records and links the Ryan call; clinical data is never copied.
A caller must re-read the event around an exact-ETag update and reconcile uncertain
results before retrying. Native owner edits remain possible and versioned.
"""
from __future__ import annotations
from datetime import datetime
import re
from uuid import UUID
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

MAPPING_VERSION = 'DDMS-RR-20261022-R3'
REVIEW_FIELD = 'Contribution_x0020_review_x0020_'
SOURCE_FIELD = 'Contribution_x0020_source_x0020_'
MAPPING_FIELD = 'Contribution_x0020_mapping_x0020'
EVENT_FIELD = 'Ryan_x0020_event_x0020_reference'
EPISODE_FIELD = 'Actual_x0020_work_x0020_episode_'
CONTRIBUTION_FIELD = 'Contribution_x0020_reference'
WORK = ('Recall_x0020_date', 'Time_x0020_started', 'Time_x0020_finished')
FLAGS = ('Staff_x0020_issue', 'Facility_x0020_issue', 'Clinical_x0020_issue', 'Phone_x0020_call')
EVENT_STATE_FIELD = 'Coordination_x0020_state'
EVENT_LOOKUP_ID_FIELD = 'Ryan_x0020_call_x0020__x002d__x0Id'
PERFORMER_REFERENCE_FIELD = 'Verified_x0020_performer_x0020_r'
REVIEW_TARGET_VERSION_FIELD = 'DDMSReviewTargetVersion'
ALLOWED_DRAFT_STATUSES = {'Not entered'}
BLOCKED_SOURCE_STATES = {'Correction pending', 'Retracted'}
PRESERVED_REVIEW_FIELDS = WORK + FLAGS + (
    PERFORMER_REFERENCE_FIELD,
    'Coordination_x0020_note_x0020__x',
    'AVAC_x0020_status',
    'Certification_x0020_name_x0020__',
    'Certification_x0020_date',
)
OPAQUE_PERFORMER_PATTERN = re.compile(
    r'(?:[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
    r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|worker:[A-Za-z0-9_-]{1,96})'
)
ITEM_VERSION_PATTERN = re.compile(r'[1-9][0-9]*\.[0-9]+')
DDMS_SITE = 'https://fictional-example.sharepoint.com/teams/Fictional-DDMS'
CREATE_CORRELATION_FIELDS = {
    '00000000-0000-4000-8000-000000000106': {'Opaque_x0020_event_x0020_referen'},
    '00000000-0000-4000-8000-000000000107': {'Title', CONTRIBUTION_FIELD},
}

def _guid(value):
    return str(UUID(str(value)))

def _time(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('Actual work requires explicit timezone')
    return date

def _same_native_id(left, right):
    """Compare positive SharePoint item IDs, which must be native integers."""
    return (type(left) is int and type(right) is int
            and left > 0 and right > 0 and left == right)

def _opaque_performer_reference(value):
    # Performer references are deliberately opaque tokens, never display names.
    return (isinstance(value, str) and value == value.strip()
            and OPAQUE_PERFORMER_PATTERN.fullmatch(value) is not None)

def _native_item_version(value):
    return (isinstance(value, str)
            and ITEM_VERSION_PATTERN.fullmatch(value) is not None)

def _next_major_version(value):
    if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]*\.0', value):
        raise ValueError('Target requires a supported major revision such as 1.0')
    major = int(value[:-2])
    return f'{major + 1}.0'

def prepare_review(event, episode, *, event_version, target_etag,
                   actual_work_confirmed, flags_confirmed, worker_confirmed,
                   performer_reference,
                   overlap_reviewed=False, other_episodes=()):
    """Return a narrow metadata-only patch; preserve manually entered work/notes.

    Review pins are explicit, not a claim that two lists form an atomic transaction.
    The separate actual-work intervals are never inferred from received/review time.
    """
    event_guid, episode_guid = _guid(event['GUID']), _guid(episode['GUID'])
    if not _same_native_id(episode.get(EVENT_LOOKUP_ID_FIELD), event.get('Id')):
        raise ValueError('Episode is not linked to this Ryan call event')
    if episode.get(EVENT_FIELD) not in (None, '', event_guid):
        raise ValueError('Existing event identity disagrees; reconcile manually')
    if episode.get(EPISODE_FIELD) not in (None, '', episode_guid):
        raise ValueError('Existing episode identity disagrees; reconcile manually')
    if episode.get(CONTRIBUTION_FIELD) not in (None, '', f'{event_guid}:{episode_guid}'):
        raise ValueError('Existing contribution identity disagrees; reconcile manually')
    if (not _native_item_version(event_version)
            or event.get('OData__UIVersionString') != event_version):
        raise ValueError('Source revision changed; review again')
    if (not isinstance(target_etag, str) or not target_etag
            or target_etag != target_etag.strip() or target_etag == '*'
            or episode.get('odata.etag') != target_etag):
        raise ValueError('Target revision changed; review again')
    if event.get(EVENT_STATE_FIELD) in BLOCKED_SOURCE_STATES:
        raise ValueError('Retracted or correction-pending source requires manual review')
    if (episode.get('Certification_x0020_name_x0020__')
            or episode.get('Certification_x0020_date')
            or episode.get('AVAC_x0020_status') not in ALLOWED_DRAFT_STATUSES):
        raise ValueError('Certified/submitted history requires an amendment')
    confirmations = (actual_work_confirmed, flags_confirmed, worker_confirmed)
    if any(value is not True for value in confirmations):
        raise ValueError('Explicit actual-work, issue/phone and performer review required')
    if not _opaque_performer_reference(performer_reference):
        raise ValueError('Explicit opaque performer reference required')
    if episode.get(PERFORMER_REFERENCE_FIELD) != performer_reference:
        raise ValueError('Native verified performer reference must match explicit review')
    if any(type(episode.get(k)) is not bool for k in FLAGS):
        raise ValueError('Unknown flags must not become attested false')
    if any(not episode.get(k) for k in WORK):
        raise ValueError('Incomplete actual-work episode')
    start, end = _time(episode[WORK[1]]), _time(episode[WORK[2]])
    if _time(episode[WORK[0]]).astimezone(ZoneInfo('Australia/Brisbane')).date() != start.astimezone(ZoneInfo('Australia/Brisbane')).date():
        raise ValueError('Recall date must match actual work start date in Brisbane')
    if end <= start:
        raise ValueError('End must follow start, using both dates for overnight work')
    overlapping = any(_time(x[WORK[1]]) < end and _time(x[WORK[2]]) > start for x in other_episodes if x.get('GUID') != episode.get('GUID'))
    if type(overlap_reviewed) is not bool:
        raise ValueError('Overlap review must be an explicit boolean')
    if overlapping and overlap_reviewed is not True:
        raise ValueError('Overlapping actual-work periods require human reconciliation')
    cid = f'{event_guid}:{episode_guid}'
    if episode.get(CONTRIBUTION_FIELD) not in (None, '', cid):
        raise ValueError('Contribution identity cannot be replaced')
    current_target_version = episode.get('OData__UIVersionString')
    next_target_version = _next_major_version(current_target_version)
    patch = {CONTRIBUTION_FIELD:cid, EVENT_FIELD:event_guid,
             EPISODE_FIELD:episode_guid, SOURCE_FIELD:event_version,
             MAPPING_FIELD:MAPPING_VERSION, REVIEW_FIELD:'Reviewed draft',
             REVIEW_TARGET_VERSION_FIELD:next_target_version}
    if episode.get(REVIEW_FIELD) == 'Reviewed draft':
        current_revision_patch = {**patch, REVIEW_TARGET_VERSION_FIELD:current_target_version}
        if (episode.get(REVIEW_TARGET_VERSION_FIELD) == current_target_version
                and all(episode.get(k) == v for k, v in current_revision_patch.items())):
            patch = current_revision_patch
            next_target_version = current_target_version
            action = 'already_applied'
        else:
            raise ValueError('Reviewed contribution requires explicit Review required state')
    else:
        action = 'review'
    pins = {'etag': target_etag, 'source_version': event_version,
            'event_guid': event_guid, 'episode_guid': episode_guid,
            'performer_reference': performer_reference,
            'expected_post_version': next_target_version,
            'expected': patch,
            'work_snapshot': {k: episode.get(k) for k in PRESERVED_REVIEW_FIELDS}}
    if action == 'already_applied':
        return {'action':action, 'patch':{}, **pins}
    return {'action':action, 'patch':patch, **pins}

def reconcile_review(event, current, proposal, *, performer_reference):
    """Classify a one-sided/uncertain save without another mutation."""
    if (_guid(event['GUID']) != proposal['event_guid']
            or _guid(current['GUID']) != proposal['episode_guid']):
        return 'identity_conflict_reconcile_manually'
    if performer_reference != proposal['performer_reference']:
        return 'performer_changed_review_required'
    if current.get(PERFORMER_REFERENCE_FIELD) != proposal['performer_reference']:
        return 'performer_changed_review_required'
    if not _same_native_id(current.get(EVENT_LOOKUP_ID_FIELD), event.get('Id')):
        return 'identity_conflict_reconcile_manually'
    if (current.get(EVENT_FIELD) not in (None, '', proposal['event_guid'])
            or current.get(EPISODE_FIELD) not in (None, '', proposal['episode_guid'])):
        return 'identity_conflict_reconcile_manually'
    if (event.get('OData__UIVersionString') != proposal['source_version']
            or event.get(EVENT_STATE_FIELD) in BLOCKED_SOURCE_STATES):
        return 'source_changed_review_required'
    if any(current.get(k) != v for k, v in proposal['work_snapshot'].items()):
        return 'target_work_changed_review_required'
    if (current.get('OData__UIVersionString') == proposal['expected_post_version']
            and current.get(REVIEW_TARGET_VERSION_FIELD) == proposal['expected_post_version']
            and all(current.get(k)==v for k,v in proposal['expected'].items())):
        return 'applied'
    if (current.get('odata.etag') == proposal['etag']
            and current.get('OData__UIVersionString') != proposal['expected_post_version']):
        return 'not_applied_review_before_retry'
    return 'conflict_reconcile_manually'


def reconcile_create(request, query_result, *, correlation_field,
                     same_id_readback=None):
    """Reconcile a durable CLI create request without submitting another write.

    Read the request saved before the original send, query its exact correlation
    in the pinned list, then read the matched native ID independently. A zero
    match never authorises recreation: the original outcome may still be unknown.
    This is the manual CLI fallback, not persistence for Canvas app variables.
    """
    result = {'retry_allowed': False}
    if not isinstance(request, dict):
        raise ValueError('Durable DDMS create request must be an object')
    request_url = request.get('url')
    if not isinstance(request_url, str):
        raise ValueError('Durable DDMS create request URL must be text')
    path = urlsplit(request_url)
    site = urlsplit(DDMS_SITE)
    match = re.fullmatch(
        re.escape(site.path) + r"/_api/web/lists\(guid'([0-9a-f-]{36})'\)/items",
        path.path, re.IGNORECASE)
    if (request.get('method') != 'post' or path.scheme != site.scheme
            or path.netloc != site.netloc or path.query or path.fragment
            or not match or request.get('headers', {})):
        raise ValueError('Exact DDMS create request required')
    list_id = match.group(1).lower()
    if correlation_field not in CREATE_CORRELATION_FIELDS.get(list_id, set()):
        raise ValueError('Unsupported create correlation field')
    payload = request.get('body')
    if (not isinstance(payload, dict)
            or not isinstance(payload.get(correlation_field), str)
            or not payload[correlation_field].strip()):
        raise ValueError('Durable request must retain its create correlation')
    if (not isinstance(query_result, dict)
            or not isinstance(query_result.get('value'), list)
            or any(k in query_result for k in ('odata.nextLink', '@odata.nextLink', '__next'))):
        return {**result, 'outcome': 'incomplete_query_reconcile_manually'}
    rows = query_result['value']
    if not rows:
        return {**result, 'outcome': 'unresolved_no_retry'}
    if len(rows) != 1:
        return {**result, 'outcome': 'multiple_matches_reconcile_manually'}
    row = rows[0]
    if not isinstance(row, dict) or row.get(correlation_field) != payload[correlation_field]:
        return {**result, 'outcome': 'correlation_mismatch_reconcile_manually'}

    def identity(item):
        if not isinstance(item, dict):
            return None
        item_id = item.get('Id')
        if type(item_id) is not int or item_id <= 0:
            return None
        try:
            guid = _guid(item.get('GUID'))
        except (ValueError, TypeError, AttributeError):
            return None
        # Bind native readback to the exact site/list as well as its numeric ID.
        expected = (DDMS_SITE + "/_api/Web/Lists(guid'" + list_id
                    + "')/Items(" + str(item_id) + ")")
        if str(item.get('odata.id', '')).lower() != expected.lower():
            return None
        if not _native_item_version(item.get('OData__UIVersionString')):
            return None
        return item_id, guid

    row_identity = identity(row)
    if row_identity is None:
        return {**result, 'outcome': 'invalid_native_identity_reconcile_manually'}
    if same_id_readback is None:
        return {**result, 'outcome': 'same_id_read_required', 'item_id': row_identity[0]}
    if identity(same_id_readback) != row_identity:
        return {**result, 'outcome': 'identity_conflict_reconcile_manually'}
    if any(k not in same_id_readback or type(same_id_readback[k]) is not type(v)
           or same_id_readback[k] != v for k, v in payload.items()):
        return {**result, 'outcome': 'saved_with_changes_review_required',
                'item_id': row_identity[0]}
    if same_id_readback['OData__UIVersionString'] != '1.0':
        # An edit to an unposted field is still material to recovery. Never
        # upgrade a later version into a claim of an untouched create result.
        return {**result, 'outcome': 'created_then_changed_review_required',
                'item_id': row_identity[0],
                'native_version': same_id_readback['OData__UIVersionString']}
    return {**result, 'outcome': 'saved_same_id', 'item_id': row_identity[0],
            'item_guid': row_identity[1],
            'native_version': same_id_readback['OData__UIVersionString']}


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Read-only DDMS create recovery from supplied CLI snapshots; caller verifies freshness')
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--matches', required=True, type=Path)
    parser.add_argument('--correlation-field', required=True)
    parser.add_argument('--same-id-readback', type=Path)
    args = parser.parse_args()
    try:
        outcome = reconcile_create(
            json.loads(args.request.read_text()), json.loads(args.matches.read_text()),
            correlation_field=args.correlation_field,
            same_id_readback=(json.loads(args.same_id_readback.read_text())
                              if args.same_id_readback else None))
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps(outcome, indent=2))
