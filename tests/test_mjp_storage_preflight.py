"""Offline, read-only storage-layout review: not an installer or ACL check."""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

SRC = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "storage_preflight.py"
SPEC = spec_from_file_location("mjp_storage_preflight", SRC)
assert SPEC and SPEC.loader
M = module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def contract():
    return {
        'status': 'source-inventory-only:not-deployed',
        'lists': [{'name': 'JP_PlanHeads', 'key': 'Key',
                   'logical_boundary': 'practitioner-restricted',
                   'required_source_fields': ['Title', 'Payload', 'OwnerUPN']}],
        'libraries': [{'name': 'JP_ApprovedPlanRecords',
                       'logical_boundary': 'practitioner-restricted'}],
        'delivery': {'authorisation_required': True},
    }


def native():
    return {'lists': [{'name': 'JP_PlanHeads', 'columns': ['Title', 'Payload', 'OwnerUPN'],
                       'key_unique': True, 'permission_scopes': 25}],
            'libraries': [{'name': 'JP_ApprovedPlanRecords',
                           'permission_scopes': 1}]}


class Preflight(unittest.TestCase):
    def test_exact_structure_never_grants_acl_or_installs(self):
        result = M.assess_layout(contract(), native())
        self.assertEqual(result['readiness'], 'structural_match_only')
        self.assertEqual(result['findings'], [])
        self.assertFalse(result['permission_qualified'])
        self.assertFalse(result['provisioning_authorised'])
        self.assertEqual(result['write_operations'], [])

    def test_missing_objects_are_blocked_without_provisioning(self):
        result = M.assess_layout(contract(), {'lists': [], 'libraries': []})
        self.assertEqual(result['readiness'], 'blocked')
        self.assertEqual({x['code'] for x in result['findings']}, {'missing_list', 'missing_library'})
        self.assertEqual(result['write_operations'], [])

    def test_column_or_uniqueness_mismatch_is_blocked(self):
        readback = native()
        readback['lists'][0]['columns'].remove('OwnerUPN')
        readback['lists'][0]['key_unique'] = False
        result = M.assess_layout(contract(), readback)
        self.assertEqual(result['readiness'], 'blocked')
        self.assertIn('required_columns_missing', {x['code'] for x in result['findings']})
        self.assertIn('unique_key_unverified', {x['code'] for x in result['findings']})

    def test_permissions_scale_is_review_not_automatic_approval(self):
        readback = native()
        readback['lists'][0]['permission_scopes'] = 5500
        result = M.assess_layout(contract(), readback)
        self.assertEqual(result['readiness'], 'blocked')
        self.assertIn('permission_scope_growth_risk', {x['code'] for x in result['findings']})

    def test_unknown_existing_objects_are_not_deleted(self):
        readback = native()
        readback['lists'].append({'name': 'JP_Unmanaged', 'columns': ['Title'],
                                  'key_unique': True, 'permission_scopes': 0})
        result = M.assess_layout(contract(), readback)
        self.assertEqual(result['readiness'], 'blocked')
        self.assertIn('unmanaged_existing_list', {x['code'] for x in result['findings']})
        self.assertEqual(result['write_operations'], [])

    def test_untrusted_or_ambiguous_readback_rejected(self):
        for input in (None, {}, {'lists': [{'name': 'JP_PlanHeads'}], 'libraries': []},
                      {'lists': [native()['lists'][0]] * 2, 'libraries': native()['libraries']}):
            with self.subTest(input=input), self.assertRaises(M.PreflightError):
                M.assess_layout(contract(), input)


if __name__ == '__main__':
    unittest.main()
