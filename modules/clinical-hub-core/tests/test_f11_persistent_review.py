"""Local graph checks; native runtime commissioning remains separate."""
from copy import deepcopy
import pytest
from scripts.f11_persistent_review import build_persistent_review, FIELD, TRANSITIONS


def build(**changes):
    cfg = dict(site='https://fictional-example.sharepoint.com/teams/Fictional',
               list_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', item_id=8,
               item_guid='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
               title='FICTIONAL review workflow', entity_type='SP.Data.FictionalListItem')
    cfg.update(changes)
    return build_persistent_review({'properties': {'state': 'Stopped', 'definition': {},
        'connectionReferences': {'shared_sharepointonline': {'existing': True}}}}, **cfg)


def test_one_conditional_single_field_write_and_no_retries():
    graph = build(); a = graph['properties']['definition']['actions']
    writes = [x for x in a.values() if x['type'] == 'OpenApiConnection' and x['inputs']['parameters']['parameters/method'] == 'POST']
    assert len(writes) == 1
    write = writes[0]['inputs']
    assert write['retryPolicy'] == {'type': 'none'}
    assert write['parameters']['parameters/headers']['IF-MATCH'] == "@triggerBody()?['expected_etag']"
    assert set(write['parameters']['parameters/body']) == {'__metadata', FIELD}
    assert graph['properties']['state'] == 'Stopped'
    assert graph['properties']['connectionReferences'] == {'shared_sharepointonline': {'existing': True}}


def test_persistence_uses_saved_state_not_caller_envelope():
    d = build()['properties']['definition']; a = d['actions']
    assert FIELD in a['Parse_envelope']['inputs']['content']
    assert 'state' not in d['triggers']['manual']['inputs']['schema']['properties']
    assert 'union(' in a['Next_state']['inputs']
    assert 'current_binding' in a['Next_state']['inputs']
    assert 'review_required' in a['Target_state']['inputs']
    for name in ('Identity_guard', 'Scope_guard', 'Request_guard', 'Transition_guard', 'Content_guard', 'Saved_state_guard'):
        assert next(iter(a[name]['else']['actions'].values()))['type'] == 'Terminate'
    for name, action in a.items():
        assert set(action.get('runAfter', {})) <= a.keys(), name
    assert set(d['triggers']['manual']['inputs']['schema']['properties']['action']['enum']) == set(TRANSITIONS)


def test_native_content_changes_and_policy_revision_are_checked():
    from scripts.f11_persistent_review import SOURCE_FIELDS, envelope_schema
    a = build()['properties']['definition']['actions']
    assert set(a['Native_source']['inputs']) == set(SOURCE_FIELDS)
    assert "outputs('Native_source')" in a['Binding_changed']['inputs']
    assert 'permission_revision' in a['Policy_guard']['expression']
    assert 'prior_source_snapshot' in a['Event']['inputs']
    assert 'prior_approval_retained' in a['Event']['inputs']
    assert 'source_snapshot' in a['Next_state']['inputs']
    schema = envelope_schema()
    assert set(schema['required']) == set(schema['properties'])
    assert schema['properties']['synthetic_only']['enum'] == [True]
    assert schema['properties']['source_snapshot']['required'] == list(SOURCE_FIELDS)


@pytest.mark.parametrize('changes', [{'title': 'Real item'}, {'item_id': True}, {'site': 'http://example.test'}])
def test_unqualified_target_refused(changes):
    with pytest.raises(ValueError): build(**changes)
