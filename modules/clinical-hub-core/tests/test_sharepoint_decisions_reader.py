"""Fictional tests for read-only Standard SharePoint page admission."""
from copy import deepcopy
from scripts.sharepoint_decisions_reader import qualify_pages

SITE = 'https://example.sharepoint.com/sites/governance'
LIST = '11111111-1111-4111-8111-111111111111'


def row(forum='medication', record='a1', etag='"1"'):
    return {'ForumRef': forum, 'RecordRef': record, 'OccurrenceRef': 'meeting-1',
            'Kind': 'action', 'Status': 'open', 'SourceRef': 'minutes-1',
            'SourceRevision': 'v1', 'OwnerRef': None, 'DueDate': None,
            'CompletionEvidenceRef': None, 'ID': 17, 'OData__UIVersionString': '1.0',
            '@odata.etag': etag}


def page(items, cursor=None, next_cursor=None, *, complete=False, list_id=LIST):
    return {'site_url': SITE, 'list_id': list_id, 'scope_ref': 'authorized-source-inventory',
            'cursor': cursor, 'next_cursor': next_cursor, 'complete': complete,
            'items': items}


def test_paginated_two_forum_read_is_source_only():
    pages = [page([row()], next_cursor='opaque-next'),
             page([dict(row('quality', 'a1'), ID=18)], cursor='opaque-next', complete=True)]
    saved = deepcopy(pages)
    result = qualify_pages(pages, site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')
    assert result['state'] == 'read_candidate'
    assert result['pagination_complete'] is True
    assert result['native_write_authorised'] is False
    assert result['permissions_verified'] is False
    assert len(result['records']) == 2
    assert result['records'][0]['forum_ref'] == 'medication'
    assert result['records'][1]['forum_ref'] == 'quality'
    assert pages == saved


def test_partial_or_divergent_pagination_refused():
    assert qualify_pages([page([row()], next_cursor='next')], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([row()], next_cursor='next'), page([], cursor='wrong', complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([row()], complete=True, next_cursor='unexpected')], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([row()], next_cursor='next'), page([], cursor='next', next_cursor='next'), page([], cursor='next', complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'


def test_scope_drift_duplicates_and_unknown_fields_refused():
    assert qualify_pages([page([row()], complete=True, list_id='22222222-2222-4222-8222-222222222222')], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([row(), row()], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([dict(row(), ClinicalNarrative='secret')], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'


def test_version_etag_and_state_validation():
    assert qualify_pages([page([row(etag='')], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([dict(row(), Status='resolved')], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
    assert qualify_pages([page([dict(row(), DueDate='2026-02-30')], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'


def test_empty_complete_read_is_not_permissions_proof():
    result = qualify_pages([page([], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')
    assert result['state'] == 'read_candidate' and result['records'] == []
    assert result['permissions_verified'] is False


def test_malformed_page_list_id_fails_closed():
    supplied = page([row()], complete=True)
    supplied['list_id'] = None
    assert qualify_pages([supplied], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'


def test_duplicate_native_item_id_across_forums_refused():
    assert qualify_pages([page([row('medication', 'a1'), row('quality', 'a1')], complete=True)], site_url=SITE, list_id=LIST, scope_ref='authorized-source-inventory')['state'] == 'blocked'
