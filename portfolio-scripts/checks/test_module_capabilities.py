# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Protect the suite selection contract; source state is not native readiness."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate(value):
    if value['defaultProfile'] != 'standard-m365' or value['enabledModules']:
        raise ValueError('Standard profile with no modules selected is required')
    profile = value['profiles']['standard-m365']
    if any(profile[key] is not False for key in ('requiresPremium', 'requiresCopilot', 'requiresCLIForDailyUse')):
        raise ValueError('Core must not require premium, Copilot or daily CLI use')
    modules = value['modules']
    ids = [module['id'] for module in modules]
    if len(ids) != len(set(ids)):
        raise ValueError('Module IDs must be unique')
    for module in modules:
        if module['optional'] is not True or module['standalone'] is not True or module['enabledByDefault'] is not False or module['requiredModules']:
            raise ValueError('Every module must be independently optional')
        if not module['standardRoute'].strip():
            raise ValueError('Explicit standard route or capability limitation required')
        if 'parent' in module and (module['parent'] not in ids or module['parent'] == module['id']):
            raise ValueError('Known independent parent relationship required')
        visited = {module['id']}
        parent = module.get('parent')
        while parent:
            if parent in visited:
                raise ValueError('Cyclic module hierarchy')
            visited.add(parent)
            parent = next(m for m in modules if m['id'] == parent).get('parent')


class CapabilityContractTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'portfolio/module-capabilities.json').read_text())

    def test_current_contract_and_hub_ownership(self):
        validate(self.manifest)
        hub = next(m for m in self.manifest['modules'] if m['id'] == 'clinical-hub-core')
        self.assertEqual(hub['parent'], 'careops-decisions')
        self.assertEqual(hub['path'], 'modules/clinical-hub-core')

    def test_implicit_install_and_premium_defaults_fail(self):
        for key in ('requiresPremium', 'requiresCopilot', 'requiresCLIForDailyUse'):
            value = copy.deepcopy(self.manifest)
            value['profiles']['standard-m365'][key] = True
            with self.assertRaises(ValueError):
                validate(value)
        for key, bad in (('optional', False), ('standalone', False), ('enabledByDefault', True), ('requiredModules', ['careops-decisions'])):
            value = copy.deepcopy(self.manifest)
            value['modules'][0][key] = bad
            with self.assertRaises(ValueError):
                validate(value)

    def test_parent_relationship_cannot_introduce_cycle(self):
        value = copy.deepcopy(self.manifest)
        parent = next(m for m in value['modules'] if m['id'] == 'careops-decisions')
        parent['parent'] = 'clinical-hub-core'
        with self.assertRaises(ValueError):
            validate(value)


if __name__ == '__main__':
    unittest.main()
