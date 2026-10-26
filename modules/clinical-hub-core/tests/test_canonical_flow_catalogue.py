import hashlib
import json
from pathlib import Path


def test_one_canonical_entry_per_flow_and_exact_source_artifacts():
    root = Path(__file__).resolve().parents[1]
    catalogue = json.loads((root/'.careops/flows.json').read_text())
    flows = catalogue['flows']
    assert len(flows) == 11
    assert {f['id'] for f in flows} == {
        'F06', 'F07', 'F08', 'F09', 'F10', 'F11', 'F12', 'F14', 'F15',
        'COR-CAPTURE', 'COR-LINKED'}
    assert len({f['canonicalBindingKey'] for f in flows}) == len(flows)
    for flow in flows:
        assert flow['canonicalRole'] in {'source', 'qualified-development'}
        assert flow['implementationArtifacts']
        for artifact in flow['implementationArtifacts']:
            path = root/artifact['path']
            assert path.resolve().is_relative_to(root.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact['sha256']
