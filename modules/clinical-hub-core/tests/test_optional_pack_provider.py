from copy import deepcopy
import json
from pathlib import Path
import pytest
from scripts.optional_pack_provider import propose


def fixture():
    pack = json.loads(Path('tests/fixtures/pack_preflight.json').read_text())
    return pack, dict(contract_version=1, provider='fictional-provider', record_id='record-1',
                     revision='v1', operation_key='op1', pack=deepcopy(pack))


def test_standalone_works_without_any_provider():
    local, _ = fixture()
    assert propose(local)['status'] == 'standalone'


@pytest.mark.parametrize('change,status', [({'contract_version': 2}, 'incompatible_provider'),
    ({'contract_version': True}, 'incompatible_provider'), ({'pack': None}, 'invalid_payload'),
    ({'revision': 'v0'}, 'stale_or_unverified'), ({'record_id': ''}, 'invalid_identity')])
def test_incompatible_stale_or_missing_input_preserves_owner_edits(change, status):
    local, remote = fixture(); local['papers'][0]['title'] = 'Fictional human correction'
    remote.update(change); original = deepcopy((local, remote))
    out = propose(local, remote, expected_revision='v1')
    assert out['status'] == status and out['local_pack'] == local and out['write_proposed'] is False
    assert (local, remote) == original


def test_duplicate_and_changed_retry_preserve_local_work():
    local, remote = fixture(); local['papers'][0]['title'] = 'Fictional human correction'
    first = propose(local, remote, expected_revision='v1')
    assert first['local_pack'] == local and first['proposal'] == remote['pack']
    assert not first['preflight']['ready_for_manual_review']  # defects are retained, not approved
    assert propose(local, remote, expected_revision='v1', prior=first['receipt'])['status'] == 'duplicate'
    remote['pack']['papers'][0]['title'] = 'Changed remote retry'
    assert propose(local, remote, expected_revision='v1', prior=first['receipt'])['status'] == 'reconciliation_required'


def test_source_identity_is_qualified_by_provider():
    local, remote = fixture(); first = propose(local, remote, expected_revision='v1')
    remote['provider'] = 'another-fictional-provider'
    second = propose(local, remote, expected_revision='v1')
    assert first['receipt']['source_identity'] != second['receipt']['source_identity']
