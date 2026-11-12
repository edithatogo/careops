# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Prevent the required privacy context from omitting offline semantic checks."""
import copy
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def verify(document):
    if document.get('permissions') != {'contents': 'read'}:
        raise ValueError('Privacy job requires read-only repository scope')
    triggers = document.get('on', document.get(True, {}))
    if 'pull_request_target' in triggers or not {'push', 'pull_request'} <= set(triggers):
        raise ValueError('Ordinary source events required')
    job = document['jobs']['privacy']
    if job['name'] != 'Privacy and secrets' or job.get('continue-on-error') or job.get('if'):
        raise ValueError('Required context must execute and fail closed')
    steps = job['steps']
    for step in steps:
        if step.get('continue-on-error') or step.get('if'):
            raise ValueError('Required privacy stages must not be skipped or ignored')
    checkouts = [s for s in steps if s.get('uses', '').startswith('actions/checkout@')]
    if len(checkouts) != 1 or checkouts[0]['with'].get('persist-credentials') is not False or checkouts[0]['with'].get('fetch-depth') != 0:
        raise ValueError('Complete source history without persisted credentials required')
    commands = '\n'.join(s.get('run', '') for s in steps)
    required = ['--require-hashes --only-binary=:all:', 'requirements-presidio.lock',
                'qualify_presidio.py', 'test_presidio.py', 'check.py --base',
                '--ignore-gitleaks-allow', 'git merge-base --is-ancestor',
                'ci_public_privacy.py --ci-base "$BASE_REVISION" --ci-tip "$TIP_REVISION"']
    if any(value not in commands for value in required):
        raise ValueError('Missing privacy coverage or exact range gate')
    if 'pre_push.py --ci-base' in commands:
        raise ValueError('Private-destination guard must not be substituted for public-source privacy assurance')
    if any(s.get('uses', '').startswith('actions/upload-artifact@') for s in steps):
        raise ValueError('Raw privacy artifacts must not be uploaded')


class SemanticWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.safe_load((ROOT / '.github/workflows/privacy.yml').read_text())

    def test_required_context_covers_rules_secrets_and_semantic_privacy(self):
        verify(self.workflow)

    def test_omitting_model_qualification_is_rejected(self):
        value = copy.deepcopy(self.workflow)
        value['jobs']['privacy']['steps'] = [s for s in value['jobs']['privacy']['steps'] if 'qualify_presidio.py' not in s.get('run', '')]
        with self.assertRaises(ValueError):
            verify(value)

    def test_private_only_gate_cannot_replace_public_source_scan(self):
        value = copy.deepcopy(self.workflow)
        for step in value['jobs']['privacy']['steps']:
            if 'ci_public_privacy.py' in step.get('run', ''):
                step['run'] = step['run'].replace('ci_public_privacy.py', 'pre_push.py')
        with self.assertRaises(ValueError):
            verify(value)

    def test_soft_failure_or_credential_persistence_is_rejected(self):
        value = copy.deepcopy(self.workflow)
        value['jobs']['privacy']['continue-on-error'] = True
        with self.assertRaises(ValueError):
            verify(value)
        value = copy.deepcopy(self.workflow)
        value['jobs']['privacy']['steps'][0]['with']['persist-credentials'] = True
        with self.assertRaises(ValueError):
            verify(value)


if __name__ == '__main__':
    unittest.main()
