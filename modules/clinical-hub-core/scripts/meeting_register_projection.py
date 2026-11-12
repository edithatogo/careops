# SPDX-License-Identifier: Apache-2.0
"""Read-only, deterministic forum projections over caller-supplied register metadata.

No SharePoint access, authenticity assertions, AI, scheduling, task creation, or
record mutations. Source authority and completion acceptance belong to the native
Decisions/local provider, not this metadata projection.
"""
from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
import re

FIELDS = frozenset({'forum_ref', 'record_id', 'occurrence_ref', 'kind', 'status', 'version',
                    'source_ref', 'source_revision', 'owner_ref', 'due_date',
                    'completion_evidence_ref'})
STATES = frozenset({'open', 'held', 'referred', 'returned', 'reported_complete',
                    'resolved', 'superseded', 'reopened'})
KINDS = frozenset({'action', 'decision'})
REF = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z')
DATE = re.compile(r'\d{4}-\d{2}-\d{2}\Z')


def _ref(value: object) -> bool:
    return isinstance(value, str) and REF.fullmatch(value) is not None


def _optional_ref(value: object) -> bool:
    return value is None or _ref(value)


def _date(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or DATE.fullmatch(value) is None:
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def project_register(forums: object, records: object) -> dict:
    """Project a complete caller-scoped snapshot, never an editable authority.

    Returned count fields describe caller-supplied states, not current or
    independently verified governance truth. Consumers must enforce access
    controls and prove snapshot completeness/freshness separately.
    """
    blocked = {'state': 'blocked', 'code': 'INVALID_REGISTER_SNAPSHOT',
               'native_write_authorised': False}
    if (not isinstance(forums, list) or not 1 <= len(forums) <= 64
            or any(not _ref(f) for f in forums) or len(set(forums)) != len(forums)
            or not isinstance(records, list) or len(records) > 10000):
        return blocked
    rows = {forum: [] for forum in forums}
    identities = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            return blocked
        if (any(not _ref(record[k]) for k in ('forum_ref', 'record_id', 'occurrence_ref',
                                             'version', 'source_ref', 'source_revision'))
                or not _optional_ref(record['owner_ref'])
                or not _optional_ref(record['completion_evidence_ref'])
                or record['kind'] not in KINDS or record['status'] not in STATES
                or not _date(record['due_date'])
                or record['forum_ref'] not in rows):
            return blocked
        key = (record['forum_ref'], record['record_id'])
        if key in identities:
            return blocked
        if record['status'] in {'resolved', 'reported_complete'} and not _ref(record['completion_evidence_ref']):
            return blocked
        identities.add(key)
        rows[record['forum_ref']].append({
            'key': list(key), 'record_id': record['record_id'],
            'occurrence_ref': record['occurrence_ref'],
            'kind': record['kind'], 'status': record['status'],
            'version': record['version'], 'source_ref': record['source_ref'],
            'source_revision': record['source_revision'],
            'owner_ref': record['owner_ref'], 'due_date': record['due_date'],
            'completion_evidence_ref': record['completion_evidence_ref'],
        })
    output = []
    for forum in sorted(forums):
        current = sorted(rows[forum], key=lambda r: r['record_id'])
        output.append({
            'forum_ref': forum, 'records': current,
            **{state: sum(r['status'] == state for r in current) for state in sorted(STATES)},
        })
    canonical = json.dumps(output, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return {'state': 'review_only', 'schema_version': 1, 'sha256': sha256(canonical.encode()).hexdigest(),
            'forums': output, 'native_write_authorised': False,
            'snapshot_authenticated': False, 'snapshot_complete_verified': False,
            'governance_authority_verified': False}
