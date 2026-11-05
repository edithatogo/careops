"""Fictional offline qualification for retained endpoint label conflicts."""
import copy
import hashlib
import json
import unittest
from scripts.ppg_retained_conflict import qualify_endpoint
from scripts.ppg_completed_relationship_assessment import prepare_completion
from tests.test_completed_relationship_assessment import fixture


def conflicted_fixture():
    p = fixture(True)
    endpoint = p['endpoint_sources'][1]
    text = 'FIX-002 Fictional target procedure.\nVersion 8.0\nVersion 7.0'
    endpoint.update(text_bytes=text.encode(), textSHA256=hashlib.sha256(text.encode()).hexdigest(),
                    versionConflict=True, nativeCaptureIds=[7])
    assertions = []
    for edition in ['8.0', '7.0']:
        quote = 'Version ' + edition
        start = text.index(quote)
        assertions.append(dict(start=start, end=start+len(quote), quote=quote, edition=edition))
    prior = {k:copy.deepcopy(endpoint[k]) for k in ['documentUID', 'sourceVersion',
        'originalSHA256', 'textSHA256', 'versionConflict', 'nativeCaptureIds', 'identityState']}
    prior['versionAssertionReview'] = dict(currentLabelAssertions=copy.deepcopy(assertions))
    qualification = dict(kind='retained-family-only-v1', appliesToRequestedEdition=False,
        currentAuthorityVerified=False, clinicalAcceptance=None, sourceManifestRecord=prior,
        captureReadback=dict(byteParity=True, sha256=endpoint['originalSHA256'], fields=dict(
            Id=7, PPGDocumentUID=endpoint['documentUID'], PPGCaptureSHA256=endpoint['originalSHA256'])),
        versionAssertions=assertions)
    endpoint['retainedConflictQualification'] = qualification
    p['packet']['review']['endpointEvidence'][1].update(textSHA256=endpoint['textSHA256'],
        retainedConflictQualification=copy.deepcopy(qualification),
        passages=[dict(start=0, end=len(text), quote=text)])
    return p


class RetainedConflict(unittest.TestCase):
    def test_compiler_preserves_both_labels_and_no_authority(self):
        p = conflicted_fixture()
        self.assertTrue(qualify_endpoint(p['endpoint_sources'][1]))
        result = prepare_completion(**p)
        completed = json.loads(result['patch']['EvidenceManifest'])['completedAssessment']
        q = completed['review']['endpointEvidence'][1]['retainedConflictQualification']
        self.assertEqual(len(q['versionAssertions']), 2)
        self.assertFalse(q['appliesToRequestedEdition'])
        self.assertFalse(result['patch']['CurrentAuthorityVerified'])

    def test_missing_conflict_evidence_and_subject_conflict_stay_held(self):
        p = conflicted_fixture()
        p['packet']['review']['endpointEvidence'][1].pop('retainedConflictQualification')
        with self.assertRaisesRegex(ValueError, 'Conflict qualification'):
            prepare_completion(**p)
        p = conflicted_fixture()
        m = json.loads(p['base']['EvidenceManifest'])
        m['sources'][0]['versionConflict'] = True
        p['base']['EvidenceManifest'] = json.dumps(m)
        with self.assertRaisesRegex(ValueError, 'held in native preimage'):
            prepare_completion(**p)

    def test_identity_bytes_capture_and_authority_tampering_refused(self):
        changes = [
            lambda e:e.update(original_bytes=b'changed'),
            lambda e:e['retainedConflictQualification'].update(appliesToRequestedEdition=True),
            lambda e:e['retainedConflictQualification'].update(currentAuthorityVerified=True),
            lambda e:e['retainedConflictQualification']['captureReadback']['fields'].update(PPGDocumentUID='other'),
            lambda e:e['retainedConflictQualification']['sourceManifestRecord'].update(nativeCaptureIds=[8]),
            lambda e:e['retainedConflictQualification']['sourceManifestRecord'].update(identityState='retained_body_bound'),
            lambda e:e['retainedConflictQualification']['versionAssertions'].pop(),
            lambda e:e.update(sourceDocumentId='not printed'),
        ]
        for change in changes:
            e = conflicted_fixture()['endpoint_sources'][1]
            change(e)
            with self.subTest(change=change):
                self.assertFalse(qualify_endpoint(e))

    def test_normalization_cannot_invent_a_distinct_edition(self):
        e = conflicted_fixture()['endpoint_sources'][1]
        text = e['text_bytes'].decode().replace('Version 7.0', 'Version 8.0')
        e.update(text_bytes=text.encode(), textSHA256=hashlib.sha256(text.encode()).hexdigest())
        q = e['retainedConflictQualification']
        q['sourceManifestRecord']['textSHA256'] = e['textSHA256']
        q['versionAssertions'][1].update(quote='Version 8.0', edition='8.0', normalizedEdition='7.0')
        q['sourceManifestRecord']['versionAssertionReview']['currentLabelAssertions'] = copy.deepcopy(q['versionAssertions'])
        self.assertFalse(qualify_endpoint(e))

    def test_edition_substring_cannot_invent_a_version_assertion(self):
        e = conflicted_fixture()['endpoint_sources'][1]
        q = e['retainedConflictQualification']
        q['versionAssertions'][0]['edition'] = '8'
        q['sourceManifestRecord']['versionAssertionReview']['currentLabelAssertions'] = copy.deepcopy(q['versionAssertions'])
        self.assertFalse(qualify_endpoint(e))


if __name__ == '__main__':
    unittest.main()
