# SPDX-License-Identifier: Apache-2.0
"""Compile Standard SharePoint connector read pages without cloud I/O.

Native permissions, complete connector traversal, current-source authenticity and
governance authority must be independently qualified in a supported native runtime.
"""
from __future__ import annotations
from hashlib import sha256
import json
import re
from urllib.parse import urlsplit
from uuid import UUID
from scripts.meeting_register_projection import project_register

PAGE = frozenset({'site_url', 'list_id', 'scope_ref', 'cursor', 'next_cursor', 'complete', 'items'})
FIELDS = frozenset({'ForumRef', 'RecordRef', 'OccurrenceRef', 'Kind', 'Status',
                    'SourceRef', 'SourceRevision', 'OwnerRef', 'DueDate',
                    'CompletionEvidenceRef', 'ID', 'OData__UIVersionString', '@odata.etag'})
REF = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z')
ETAG = re.compile(r'(?:W/)?"[^"\r\n]{1,100}"\Z')
VERSION = re.compile(r'[1-9][0-9]{0,7}\.[0-9]{1,8}\Z')
MAX_PAGES = 100
MAX_ITEMS = 10000


def _ref(value):
    return isinstance(value, str) and REF.fullmatch(value) is not None


def _site(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == 'https' and parsed.hostname is not None
                and parsed.hostname.endswith('.sharepoint.com')
                and parsed.username is None and parsed.password is None
                and not parsed.query and not parsed.fragment
                and not value.endswith('/'))
    except ValueError:
        return False


def _list_id(value):
    if not isinstance(value, str):
        return False
    try:
        return str(UUID(value)) == value.lower() and UUID(value).int != 0
    except ValueError:
        return False


def _blocked(reason):
    return {'state': 'blocked', 'reason': reason, 'native_write_authorised': False}


def qualify_pages(pages, *, site_url, list_id, scope_ref):
    """Validate caller-supplied page chain and project a read-only snapshot.

    A complete claimed page chain is not proof of native source completeness,
    permissions or a trustworthy collection boundary.
    """
    if not (_site(site_url) and _list_id(list_id) and _ref(scope_ref)):
        return _blocked('INVALID_SCOPE')
    if not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES:
        return _blocked('INCOMPLETE_PAGES')
    expected = None
    seen_cursors = set()
    rows = []
    identities = set()
    for index, page in enumerate(pages):
        if not isinstance(page, dict) or set(page) != PAGE:
            return _blocked('INVALID_PAGE')
        if (page['site_url'] != site_url or page['list_id'].lower() != list_id.lower()
                or page['scope_ref'] != scope_ref):
            return _blocked('SOURCE_SCOPE_DRIFT')
        cursor, following = page['cursor'], page['next_cursor']
        if cursor != expected or (cursor is not None and not _ref(cursor)):
            return _blocked('BROKEN_PAGINATION')
        if cursor is not None:
            if cursor in seen_cursors:
                return _blocked('CYCLIC_PAGINATION')
            seen_cursors.add(cursor)
        if type(page['complete']) is not bool or not isinstance(page['items'], list):
            return _blocked('INVALID_PAGE')
        final = index == len(pages) - 1
        if final != page['complete'] or (final and following is not None):
            return _blocked('INCOMPLETE_PAGES')
        if not final and (not _ref(following) or following in seen_cursors or following == cursor):
            return _blocked('BROKEN_PAGINATION')
        expected = following
        for item in page['items']:
            if not isinstance(item, dict) or set(item) != FIELDS:
                return _blocked('UNEXPECTED_FIELD_SET')
            native_id, native_version, etag = item['ID'], item['OData__UIVersionString'], item['@odata.etag']
            if (type(native_id) is not int or native_id <= 0
                    or not isinstance(native_version, str) or VERSION.fullmatch(native_version) is None
                    or not isinstance(etag, str) or ETAG.fullmatch(etag) is None):
                return _blocked('INVALID_NATIVE_VERSION')
            identity = (item['ForumRef'], item['RecordRef'])
            if identity in identities:
                return _blocked('DUPLICATE_REGISTER_IDENTITY')
            identities.add(identity)
            rows.append({
                'forum_ref': item['ForumRef'], 'record_id': item['RecordRef'],
                'occurrence_ref': item['OccurrenceRef'], 'kind': item['Kind'],
                'status': item['Status'], 'version': native_version,
                'source_ref': item['SourceRef'], 'source_revision': item['SourceRevision'],
                'owner_ref': item['OwnerRef'], 'due_date': item['DueDate'],
                'completion_evidence_ref': item['CompletionEvidenceRef'],
                'native_item_id': native_id, 'native_etag': etag,
            })
            if len(rows) > MAX_ITEMS:
                return _blocked('ITEM_LIMIT_EXCEEDED')
    forums = sorted({row['forum_ref'] for row in rows})
    projection = project_register(forums, [{key: value for key, value in row.items()
                                           if key not in {'native_item_id', 'native_etag'}} for row in rows]) if forums else None
    if projection is not None and projection['state'] != 'review_only':
        return _blocked('INVALID_REGISTER_RECORD')
    ordered = sorted(rows, key=lambda r: (r['forum_ref'], r['record_id']))
    canonical = json.dumps(ordered, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return {'state': 'read_candidate', 'schema_version': 1, 'records': ordered,
            'sha256': sha256(canonical.encode()).hexdigest(),
            'page_count': len(pages), 'pagination_complete': True,
            'native_write_authorised': False, 'permissions_verified': False,
            'source_authenticated': False, 'snapshot_freshness_verified': False,
            'governance_authority_verified': False}
