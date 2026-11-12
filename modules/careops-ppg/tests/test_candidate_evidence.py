# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Exercise trusted-build binding and partial evidence outcomes without native I/O."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location('candidate_evidence', Path(__file__).resolve().parents[1] / 'scripts/ppg_candidate_evidence.py')
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)

class FakeRelease:
    def __init__(self, metadata):
        self.metadata = copy.deepcopy(metadata)
        self.uploads = []
        self.uncertain = False
        self.private = True

    def __call__(self, args):
        if args[0] == 'api':
            return json.dumps(self.private).encode()
        if args[:2] == ['release', 'view']:
            return json.dumps(self.metadata).encode()
        if args[:2] == ['release', 'upload']:
            path = Path(args[3])
            if any(a['name'] == path.name for a in self.metadata['assets']):
                raise ValueError('NO_OVERWRITE')
            self.uploads.append(path.name)
            self.metadata['assets'].append({'name': path.name, 'id': 'fictional-' + str(len(self.metadata['assets']) + 1), 'digest': 'sha256:' + E.digest(path)})
            if self.uncertain:
                self.uncertain = False
                raise ValueError('RESPONSE_LOST_AFTER_UPLOAD')
            return b''
        raise AssertionError('Unexpected native operation')

class CandidateEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.source = 'a' * 40
        self.env = {'GITHUB_SHA': self.source, 'GITHUB_REF': 'refs/heads/main', 'GITHUB_REPOSITORY': E.REPOSITORY,
            'GITHUB_RUN_ID': '1', 'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_OUTPUT': str(self.folder / 'outputs')}
        self.tag = 'careops-ppg-candidate-' + self.source + '-1-1'
        self.make_package(b'Fictional source')
        self.hashes = E.freeze(self.folder, self.env)
        self.env['BUILT_HASHES'] = json.dumps(self.hashes)
        self.remote = FakeRelease({'apiUrl': 'https://api.github.com/repos/edithatogo/careops/releases/1', 'isDraft': True, 'targetCommitish': self.source,
            'assets': [{'name': name, 'id': 'fictional-' + str(i), 'digest': 'sha256:' + self.hashes[name]} for i, name in enumerate(E.PRIMARY, 1)]})
        self.original = E.capture(self.folder, self.env, self.tag, self.remote)
        self.env['BUILT_ASSETS'] = json.dumps(self.original)

    def make_package(self, body):
        files = {'README.md': body, E.PRIMARY[3]: b'<p>Fictional assembler</p>'}
        with zipfile.ZipFile(self.folder / E.PRIMARY[0], 'w') as archive:
            for name, data in files.items(): archive.writestr(name, data)
        (self.folder / E.PRIMARY[3]).write_bytes(files[E.PRIMARY[3]])
        sha = lambda value: hashlib.sha256(value).hexdigest()
        package_hash = E.digest(self.folder / E.PRIMARY[0])
        manifest = {'sourceCommit': self.source, 'nativeWrites': False, 'archiveSha256': package_hash, 'assemblerSha256': sha(files[E.PRIMARY[3]])}
        (self.folder / E.PRIMARY[2]).write_text(json.dumps(manifest))
        spdx = {'packages': [{'sourceInfo': 'Source commit: ' + self.source, 'licenseDeclared': 'Apache-2.0', 'checksums': [{'checksumValue': package_hash}]}],
            'files': [{'fileName': name, 'checksums': [{'algorithm': 'SHA256', 'checksumValue': sha(data)}]} for name, data in files.items()]}
        (self.folder / E.PRIMARY[1]).write_text(json.dumps(spdx))

    def verify(self):
        return E.verify(self.folder, self.env, self.tag, self.remote)

    def test_original_build_hashes_and_source_limits(self):
        receipt = self.verify()
        self.assertTrue(receipt['trustedBuildHashesVerified'])
        self.assertFalse(receipt['signedReleaseQualified'])
        self.assertFalse(receipt['nativeAttestationExecuted'])
        self.assertEqual(receipt['assets'], self.original)

    def test_declared_job_output_names_match_frozen_values(self):
        values = dict(line.split('=', 1) for line in (self.folder / 'outputs').read_text().splitlines())
        self.assertEqual(set(values), {'built_hashes', 'built_assets'})
        self.assertEqual(json.loads(values['built_hashes']), self.hashes)
        self.assertEqual(json.loads(values['built_assets']), self.original)

    def test_wrong_ref_or_run_cannot_retain_evidence(self):
        self.env['GITHUB_REF'] = 'refs/heads/fictional-other'
        with self.assertRaisesRegex(ValueError, 'MAIN_PRIVATE_SOURCE_REQUIRED'):
            E.retain(self.folder, self.env, self.tag, run=self.remote)
        self.assertEqual(self.remote.uploads, [])
        self.env['GITHUB_REF'] = 'refs/heads/main'
        with self.assertRaisesRegex(ValueError, 'EXACT_RUN_CANDIDATE_REQUIRED'):
            E.retain(self.folder, self.env, self.tag + '-other', run=self.remote)
        self.assertEqual(self.remote.uploads, [])

    def test_jointly_consistent_substitution_is_refused(self):
        self.make_package(b'Different fictional source')
        for asset in self.remote.metadata['assets']:
            asset['digest'] = 'sha256:' + E.digest(self.folder / asset['name'])
        with self.assertRaisesRegex(ValueError, 'BUILD_OUTPUT_BYTES_DIFFER'):
            self.verify()

    def test_byte_identical_native_asset_replacement_is_refused(self):
        self.remote.metadata['assets'][0]['id'] = 'fictional-replacement'
        with self.assertRaisesRegex(ValueError, 'PUBLISHED_ASSET_IDENTITY_CHANGED'):
            self.verify()

    def test_missing_trusted_build_output_fails_closed(self):
        self.env['BUILT_HASHES'] = '{}'
        with self.assertRaisesRegex(ValueError, 'BUILD_HASH_SCOPE'):
            self.verify()

    def test_private_source_and_primary_digest_are_required(self):
        self.remote.private = False
        with self.assertRaisesRegex(ValueError, 'PRIVATE_DESTINATION_REQUIRED'):
            self.verify()
        self.remote.private = True
        self.remote.metadata['assets'][0]['digest'] = 'sha256:' + '0' * 64
        with self.assertRaisesRegex(ValueError, 'PRIMARY_ASSET_DIFFERS_FROM_BUILD'):
            self.verify()

    def test_evidence_create_and_zero_write_replay(self):
        self.verify()
        self.assertEqual(E.retain(self.folder, self.env, self.tag, run=self.remote), {'created': 2, 'preserved': 0})
        self.verify()  # Extra named evidence does not change canonical receipt bytes.
        self.assertEqual(E.retain(self.folder, self.env, self.tag, run=self.remote), {'created': 0, 'preserved': 2})
        self.assertEqual(len(self.remote.uploads), 2)

    def test_partial_upload_response_loss_is_reconciled_without_retry(self):
        self.verify(); self.remote.uncertain = True
        with self.assertRaisesRegex(ValueError, 'RESPONSE_LOST_AFTER_UPLOAD'):
            E.retain(self.folder, self.env, self.tag, run=self.remote)
        self.assertEqual(len(self.remote.uploads), 1)
        self.verify()
        self.assertEqual(E.retain(self.folder, self.env, self.tag, run=self.remote), {'created': 1, 'preserved': 1})
        self.assertEqual(len(self.remote.uploads), 2)

    def test_later_attempt_preserves_old_partial_evidence(self):
        self.verify(); self.remote.uncertain = True
        with self.assertRaises(ValueError): E.retain(self.folder, self.env, self.tag, run=self.remote)
        old = copy.deepcopy(self.remote.metadata['assets'][-1])
        self.env['GITHUB_RUN_ATTEMPT'] = '2'; self.verify()
        self.assertEqual(E.retain(self.folder, self.env, self.tag, run=self.remote)['created'], 2)
        self.assertIn(old, self.remote.metadata['assets'])

    def test_changed_second_evidence_refuses_all_writes(self):
        self.verify()
        name = 'attempt-1-' + E.BYTE_EVIDENCE[1]
        self.remote.metadata['assets'].append({'name': name, 'id': 'fictional-changed', 'digest': 'sha256:' + '0' * 64})
        with self.assertRaisesRegex(ValueError, 'PRESERVE_CHANGED_EVIDENCE_ASSET'):
            E.retain(self.folder, self.env, self.tag, run=self.remote)
        self.assertEqual(self.remote.uploads, [])

    def test_unknown_auxiliary_asset_is_not_accepted(self):
        self.remote.metadata['assets'].append({'name': 'unqualified.json', 'id': 'fictional-other', 'digest': 'sha256:' + '0' * 64})
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_ASSET_IDENTITY'):
            self.verify()

    def test_signature_retention_reconciles_existing_names(self):
        for name in E.SIGNATURES: (self.folder / name).write_text('Fictional evidence')
        self.assertEqual(E.retain(self.folder, self.env, self.tag, 'signatures', self.remote)['created'], 4)
        self.assertEqual(E.retain(self.folder, self.env, self.tag, 'signatures', self.remote)['preserved'], 4)

if __name__ == '__main__':
    unittest.main()
