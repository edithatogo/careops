from copy import deepcopy
import pytest
from scripts.f12_comparator_binding import FIELDS, bind_comparator, _inputs


def fixture():
    checks = {}
    for name, path in FIELDS.items():
        selector = 'Find_exact_occurrence' if path[0] == 'event' else 'Find_issued_agenda'
        observed = f"first(body('{selector}'))" + ''.join(f"?['{p}']" for p in path[1:])
        if name == 'event_organizer':
            observed = f"toLower(coalesce({observed},''))"
        literal = 'false' if name in {'agenda_inline', 'event_cancelled'} else '42' if name == 'agenda_size' else "'FICTIONAL''value'"
        checks[name] = f'@equals({observed},{literal})'
    inputs = {'checks': checks, 'state': '@and(' + ','.join(v[1:] for v in checks.values()) + ')',
              'content_equality_verified': False, 'write_proposed': False}
    return {'parameters': {'existing': {}}, 'actions': {'Read_approved_window': {'runAfter': {}, 'inputs': 'FICTIONAL'},
        'Require_one_occurrence': {'expression': 'EXISTING_GUARD', 'actions': {'Require_one_agenda': {
            'expression': 'EXISTING_ATTACHMENT_GUARD', 'actions': {'Observed_baseline': {'inputs': inputs},
            'Other_action': {'inputs': 'PRESERVE'}}}}}}}


def test_every_binding_and_graph_preservation():
    source = fixture(); before = deepcopy(source)
    result, receipt = bind_comparator(source)
    assert source == before
    assert receipt['deployment_ready'] is False
    assert set(receipt['replacement_counts'].values()) == {2}
    for name, path in FIELDS.items():
        expected = "parameters('comeet_F12Baseline')" + ''.join(f"?['{p}']" for p in path)
        assert expected in _inputs(result)['checks'][name]
        assert _inputs(result)['checks'][name].split(',')[0] == _inputs(source)['checks'][name].split(',')[0]
    assert "FICTIONAL''value" not in str(_inputs(result))
    _inputs(result).clear(); _inputs(result).update(_inputs(source))
    assert result == source


@pytest.mark.parametrize('name', FIELDS)
def test_missing_check_refused(name):
    source = fixture(); del _inputs(source)['checks'][name]
    with pytest.raises(ValueError, match='exact 21'):
        bind_comparator(source)


@pytest.mark.parametrize('bad', ["@equals(wrong(),'secret')", "@equals(first(body('Find_exact_occurrence'))?['id'],parameters('secret'))"])
def test_drift_refused_without_value_disclosure(bad):
    source = fixture(); _inputs(source)['checks']['event_id'] = bad
    before = deepcopy(source)
    with pytest.raises(ValueError) as error:
        bind_comparator(source)
    assert 'secret' not in str(error.value)
    assert source == before


def test_missing_repeated_comparisons_refused():
    source = fixture(); _inputs(source)['state'] = 'NO_COMPARISONS'
    with pytest.raises(ValueError, match='repeated'):
        bind_comparator(source)


def test_second_transform_refused():
    result, _ = bind_comparator(fixture())
    with pytest.raises(ValueError):
        bind_comparator(result)


def test_drift_in_repeated_output_refused():
    source = fixture()
    original = _inputs(source)['checks']['event_id'][1:]
    _inputs(source)['state'] = _inputs(source)['state'].replace(original, original.replace("FICTIONAL''value", "DRIFTED"))
    with pytest.raises(ValueError, match='inconsistent'):
        bind_comparator(source)


def test_existing_null_presence_guards_preserved():
    source = fixture()
    observed = _inputs(source)['checks']['event_id'][1:].split(',')[0]
    guard = '@not(' + observed + ',null))'
    _inputs(source)['missing_guard'] = guard
    result, _ = bind_comparator(source)
    assert _inputs(result)['missing_guard'] == guard
