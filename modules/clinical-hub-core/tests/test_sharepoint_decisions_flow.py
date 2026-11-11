"""Source-only regression contract for the native Standard SharePoint connector flow."""
from copy import deepcopy
import pytest
from scripts.sharepoint_decisions_flow import build

CONFIG = {
    'site_url': 'https://fictional-example.sharepoint.com/sites/governance',
    'list_id': '11111111-1111-4111-8111-111111111111',
    'view_id': '22222222-2222-4222-8222-222222222222',
    'connection_name': 'shared-sharepoint-connection-1',
    'fields': {name: name for name in (
        'ForumRef', 'RecordRef', 'OccurrenceRef', 'Kind', 'Status',
        'SourceRef', 'SourceRevision', 'OwnerRef', 'DueDate',
        'CompletionEvidenceRef', 'OData__UIVersionString')},
    'max_items': 5000,
}


def test_generates_stopped_standard_getitems_with_native_pagination():
    before = deepcopy(CONFIG)
    result = build(CONFIG)
    assert CONFIG == before
    assert result['properties']['state'] == 'Stopped'
    assert result['properties']['definition']['parameters']['ReadEnabled']['defaultValue'] is False
    a = result['properties']['definition']['actions']
    assert a['Get_items']['inputs']['host']['operationId'] == 'GetItems'
    assert a['Get_items']['inputs']['host']['connectionName'] == 'shared_sharepointonline'
    assert a['Get_items']['runtimeConfiguration']['paginationPolicy']['minimumItemCount'] == 5000
    assert a['Get_items']['inputs']['parameters']['view'] == CONFIG['view_id']
    assert a['Read_complete']['else']['actions']['Unqualified']['type'] == 'Terminate'
    assert a['Require_valid_rows']['actions']['Review_only']['inputs']['native_write_authorised'] is False
    assert result['preparation']['activationHeld']


def test_explicit_core_column_projection_and_no_writers_or_ai():
    result = build(CONFIG)
    definition = result['properties']['definition']
    text = repr(definition)
    assert "'type': 'Select'" in text
    assert "'type': 'Query'" in text
    assert "'type': 'Terminate'" in text
    assert all(x not in text for x in ["CreateItem", "UpdateItem", "HttpRequest", "shared_commondataservice",
                                     "shared_openai", "shared_copilot", "SendEmail"])
    assert definition['actions']['Require_valid_rows']['actions']['Review_only']['inputs']['source_authenticated'] is False


@pytest.mark.parametrize('change', [
    {'max_items': 10001}, {'max_items': True},
    {'list_id': 'not-a-list'}, {'view_id': 'not-a-view'},
    {'site_url': 'https://invalid.example/meeting'},
    {'connection_name': ''},
])
def test_invalid_binding_refused(change):
    config = deepcopy(CONFIG)
    config.update(change)
    with pytest.raises(ValueError):
        build(config)


def test_missing_native_column_or_overlapping_column_binding_refused():
    config = deepcopy(CONFIG)
    del config['fields']['Status']
    with pytest.raises(ValueError):
        build(config)
    config = deepcopy(CONFIG)
    config['fields']['Status'] = 'ForumRef'
    with pytest.raises(ValueError):
        build(config)
    config = deepcopy(CONFIG)
    config['fields']['Status'] = 'Bad Column!'
    with pytest.raises(ValueError):
        build(config)


def test_no_automatic_schedule_or_native_record_mutation():
    result = build(CONFIG)
    definition = result['properties']['definition']
    assert set(definition['triggers']) == {'manual'}
    assert 'recurrence' not in repr(definition)
    assert definition['actions']['Get_items']['inputs']['retryPolicy'] == {'type': 'none'}
