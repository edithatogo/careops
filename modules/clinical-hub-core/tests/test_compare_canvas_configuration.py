from copy import deepcopy

import pytest

from scripts.compare_canvas_configuration import compare_configuration, load_configuration, main


def configuration():
    return {'Screens': {'Example': {'Properties': {'Width': '=App.Width'},
            'Children': [{'Save': {'Properties': {
                'OnSelect': '=Patch(Records, selected, {Note: "Keep two  spaces"})',
                'DisplayMode': '=If(pending,DisplayMode.Disabled,DisplayMode.Edit)'
            }}}]}}}


def test_sparse_export_does_not_prove_an_omitted_guard_matches():
    maintained = configuration()
    observed = deepcopy(maintained)
    del observed['Screens']['Example']['Children'][0]['Save']['Properties']['DisplayMode']
    report = compare_configuration(maintained, observed)
    assert report['status'] == 'incomplete'
    assert report['changed'] == []
    assert report['unobserved'] == [['Screens', 'Example', 'Children', 0,
                                      'Save', 'Properties', 'DisplayMode']]


@pytest.mark.parametrize('change', [
    lambda p: p.update(OnSelect='=Patch(OtherRecords, selected, {Note: "Keep two  spaces"})'),
    lambda p: p.update(OnSelect='=Patch(Records, selected, {Note: "Keep two spaces"})'),
    lambda p: p.update(DisplayMode='=DisplayMode.Edit'),
])
def test_changed_binding_literal_or_pending_guard_is_visible(change):
    maintained = configuration()
    observed = deepcopy(maintained)
    change(observed['Screens']['Example']['Children'][0]['Save']['Properties'])
    report = compare_configuration(maintained, observed)
    assert report['status'] == 'differences'
    assert len(report['changed']) == 1


def test_added_properties_and_control_reordering_are_not_hidden():
    maintained = configuration()
    maintained['Screens']['Example']['Children'].append({'Cancel': {'Control': 'Button'}})
    observed = deepcopy(maintained)
    observed['Screens']['Example']['Children'].reverse()
    assert compare_configuration(maintained, observed)['status'] == 'differences'
    observed = deepcopy(maintained)
    observed['Screens']['Example']['Properties']['OnVisible'] = '=Refresh(Records)'
    assert compare_configuration(maintained, observed)['added']


def test_exact_match_and_scalar_types_are_distinct():
    assert compare_configuration(configuration(), configuration())['status'] == 'exact_match'
    assert compare_configuration({'Value': 1}, {'Value': True})['status'] == 'differences'


def test_duplicate_yaml_properties_are_rejected(tmp_path):
    path = tmp_path / 'example.pa.yaml'
    path.write_text('Screen:\n  Width: =App.Width\n  Width: =0\n')
    with pytest.raises(ValueError, match='Duplicate configuration key'):
        load_configuration(path)


@pytest.mark.parametrize(('observed', 'expected'), [
    ('Screen: {Width: "=App.Width", Height: "=App.Height"}\n', 0),
    ('Screen: {Width: "=App.Width"}\n', 2),
    ('Screen: {Width: "=0", Height: "=App.Height"}\n', 1),
])
def test_cli_exit_codes_and_report_collision_preserve_existing_evidence(
        tmp_path, monkeypatch, observed, expected):
    maintained = tmp_path / 'source.pa.yaml'
    current = tmp_path / 'observed.pa.yaml'
    report = tmp_path / 'report.json'
    maintained.write_text('Screen: {Width: "=App.Width", Height: "=App.Height"}\n')
    current.write_text(observed)
    monkeypatch.setattr('sys.argv', ['compare', str(maintained), str(current),
                                   '--report', str(report)])
    assert main() == expected
    original = report.read_bytes()
    with pytest.raises(FileExistsError):
        main()
    assert report.read_bytes() == original
