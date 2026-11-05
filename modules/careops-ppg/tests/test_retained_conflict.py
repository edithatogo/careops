"""Fictional offline qualification for retained endpoint label conflicts."""
import copy
import hashlib
import json
import unittest
from scripts.ppg_retained_conflict import qualify_endpoint
from scripts.ppg_completed_relationship_assessment import prepare_completion, catalogue_snapshot
from scripts.ppg_catalogue_relationships import digest, literal_leads
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


def qualified_variant_fixture():
    p = conflicted_fixture()
    endpoint = p['endpoint_sources'][1]
    canonical = 'EXAMPLE-Proc-123-V2-01/27'
    printed = 'EXAMPLE-Proc-123-V1-01/26'
    text = printed + ' Fictional target procedure.\nVersion 8.0\nVersion 7.0'
    endpoint.update(sourceDocumentId=canonical, identityState='qualified_edition_variant',
                    text_bytes=text.encode(), textSHA256=hashlib.sha256(text.encode()).hexdigest())
    q = endpoint['retainedConflictQualification']
    q.update(kind='retained-qualified-variant-family-only-v2', printedSourceDocumentId=printed)
    assertions = []
    for edition in ['8.0', '7.0']:
        quote = 'Version ' + edition
        start = text.index(quote)
        assertions.append(dict(start=start, end=start+len(quote), quote=quote, edition=edition))
    q['versionAssertions'] = assertions
    prior = q['sourceManifestRecord']
    prior.update(identityState=endpoint['identityState'], textSHA256=endpoint['textSHA256'],
                 versionAssertionReview=dict(currentLabelAssertions=copy.deepcopy(assertions)))
    prior['nativeCaptureBinding'] = dict(documentUID=endpoint['documentUID'], captureId=7,
        nativeBytesVerified=True, originalBytesVerified=True,
        nativeSHA256=endpoint['originalSHA256'], originalSHA256=endpoint['originalSHA256'],
        sourceIdentifiers=[printed], associationQualification=dict(state='qualified_edition_variant',
            registerId=canonical, registerTitle='Fictional target procedure', sourceIdentifiers=[printed]))
    p['catalogue'][1]['sourceDocumentId'] = canonical
    p['packet']['scope']['catalogueSHA256'] = digest(catalogue_snapshot(p['catalogue']))
    review = p['packet']['review']
    review['endpointEvidence'][1].update(sourceDocumentId=canonical,
        textSHA256=endpoint['textSHA256'], retainedConflictQualification=copy.deepcopy(q),
        passages=[dict(start=0, end=len(text), quote=text)])
    leads = literal_leads(p['catalogue'], p['packet']['source'] | dict(text=p['text_bytes'].decode()))
    review['leadDispositions'] = [dict(leadKey=digest(lead), disposition='linked-finding',
        relationshipKeys=['fictional-link'], rationale='Explicit fictional handoff.') for lead in leads]
    return p


class RetainedConflict(unittest.TestCase):
    def test_qualified_variant_retains_conflicting_labels_in_compiler(self):
        p = qualified_variant_fixture()
        self.assertTrue(qualify_endpoint(p['endpoint_sources'][1], catalogue=p['catalogue']))
        result = prepare_completion(**p)
        completed = json.loads(result['patch']['EvidenceManifest'])['completedAssessment']
        q = completed['review']['endpointEvidence'][1]['retainedConflictQualification']
        self.assertEqual(q['printedSourceDocumentId'], 'EXAMPLE-Proc-123-V1-01/26')
        self.assertEqual([a['edition'] for a in q['versionAssertions']], ['8.0', '7.0'])
        self.assertFalse(q['currentAuthorityVerified'])

    def test_variant_needs_unique_catalogue_and_existing_native_family(self):
        p = qualified_variant_fixture()
        endpoint = p['endpoint_sources'][1]
        self.assertFalse(qualify_endpoint(endpoint))
        duplicate = p['catalogue'] + [dict(DocumentUID='other',
            sourceDocumentId='EXAMPLE-Proc-123-V3-02/28', sourceTitle='Other edition identity')]
        self.assertFalse(qualify_endpoint(endpoint, catalogue=duplicate))
        for key, value in [('state', 'unresolved_candidate'), ('registerId', 'OTHER-V2'),
                           ('sourceIdentifiers', []), ('registerTitle', 'Different procedure')]:
            changed = copy.deepcopy(endpoint)
            changed['retainedConflictQualification']['sourceManifestRecord']['nativeCaptureBinding'][
                'associationQualification'][key] = value
            with self.subTest(key=key):
                self.assertFalse(qualify_endpoint(changed, catalogue=p['catalogue']))

    def test_variant_cannot_qualify_unbound_bytes_or_a_conflicted_subject(self):
        p = qualified_variant_fixture()
        endpoint = copy.deepcopy(p['endpoint_sources'][1])
        endpoint['retainedConflictQualification']['sourceManifestRecord']['nativeCaptureBinding'][
            'nativeSHA256'] = '0' * 64
        self.assertFalse(qualify_endpoint(endpoint, catalogue=p['catalogue']))
        m = json.loads(p['base']['EvidenceManifest'])
        m['sources'][0]['versionConflict'] = True
        p['base']['EvidenceManifest'] = json.dumps(m)
        with self.assertRaisesRegex(ValueError, 'held in native preimage'):
            prepare_completion(**p)

    def test_older_native_capture_metadata_requires_existing_variant_qualification(self):
        p = qualified_variant_fixture()
        endpoint = p['endpoint_sources'][1]
        q = endpoint['retainedConflictQualification']
        binding = q['sourceManifestRecord'].pop('nativeCaptureBinding')
        association = copy.deepcopy(binding['associationQualification'])
        association.pop('registerTitle')
        association.update(versionConflict=True)
        metadata = dict(sourceIdentifiers=binding['sourceIdentifiers'],
            associations=[association], sourceEditionIsNotNativeVersion=True)
        q['captureReadback']['fields']['PPGCaptureEditionEvidence'] = json.dumps(metadata)
        self.assertTrue(qualify_endpoint(endpoint, catalogue=p['catalogue']))
        p['packet']['review']['endpointEvidence'][1]['retainedConflictQualification'] = copy.deepcopy(q)
        prepare_completion(**p)
        for changes in [dict(associations=[association, association]), dict(sourceIdentifiers=[]),
                        dict(sourceEditionIsNotNativeVersion=False),
                        dict(associations=[association | dict(state='unresolved_candidate')])]:
            q['captureReadback']['fields']['PPGCaptureEditionEvidence'] = json.dumps(metadata | changes)
            self.assertFalse(qualify_endpoint(endpoint, catalogue=p['catalogue']))

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
