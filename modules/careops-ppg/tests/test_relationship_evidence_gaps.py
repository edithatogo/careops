"""Synthetic evidence-gap refusals; no native, source or authentication calls."""
import copy
import hashlib
import unittest

from scripts.ppg_catalogue_relationships import coverage, digest
from scripts.ppg_relationship_evidence_gaps import (
    edition_review, family, propose_membership_binding, validate_capture_binding,
    validate_membership_binding,
)
from tests.test_catalogue_relationships import fixture


class EvidenceGaps(unittest.TestCase):
    def membership(self):
        p = fixture()
        for row in p['catalogue']:
            row['sourceCustodian'] = 'Fictional custodian'
        source = p['source_rows'][0]
        source.update(document_id='LOCAL-001-V2', catalogue_item_id=None,
                      title=p['catalogue'][0]['sourceTitle'], custodian='Fictional custodian')
        return p, source

    def binding(self):
        p = fixture()
        p['captures'][0]['PPGDocumentUID'] = None
        b = dict(documentUID='a', captureId=10, originalSHA256='a'*64, nativeSHA256='a'*64,
                 verificationReceiptSHA256='b'*64, sourceIdentifiers=['LOCAL-001-V1'],
                 nativeBytesVerified=True, originalBytesVerified=True,
                 currentAuthorityVerified=False, basis='Fictional exact header and verified bytes')
        return p, b

    def test_edition_alias_binds_existing_identity_without_changing_source(self):
        p, row = self.membership()
        before = copy.deepcopy(p)
        binding = propose_membership_binding(row, p['catalogue'])
        result = coverage(**p, membership_bindings=[binding])
        self.assertEqual(result['boundActiveCount'], 3)
        self.assertEqual(result['unboundActiveSourceRows'], [])
        self.assertEqual(result['rows'][0]['sourceDocumentId'], 'LOCAL-001-V1')
        self.assertEqual(result['rows'][0]['activeSourceDocumentId'], 'LOCAL-001-V2')
        self.assertEqual(p, before)
        self.assertEqual(result['nativeWrites'], 0)

    def test_ambiguous_or_changed_membership_refused(self):
        p, row = self.membership()
        binding = propose_membership_binding(row, p['catalogue'])
        row['custodian'] = 'Different custodian'
        with self.assertRaises(ValueError): validate_membership_binding(binding, row, p['catalogue'])
        p, row = self.membership()
        p['catalogue'].append(dict(p['catalogue'][0], Id=44, DocumentUID='duplicate-family'))
        with self.assertRaises(ValueError): propose_membership_binding(row, p['catalogue'])

    def test_unlinked_capture_requires_explicit_qualified_binding(self):
        p, binding = self.binding()
        with self.assertRaises(ValueError): coverage(**p)
        result = coverage(**p, capture_bindings=[binding])
        self.assertEqual(result['rows'][0]['sources'][0]['nativeCaptureIds'], [10])
        self.assertIsNone(p['captures'][0]['PPGDocumentUID'])
        with self.assertRaises(ValueError): coverage(**p, capture_bindings=[binding, binding])

    def test_capsule_member_and_actual_native_hash_required(self):
        p, binding = self.binding()
        binding.update(nativeSHA256='c'*64)
        p['captures'][0]['PPGCaptureSHA256'] = 'c'*64
        with self.assertRaises(ValueError): coverage(**p, capture_bindings=[binding])
        binding['capsuleMemberSHA256'] = 'a'*64
        self.assertEqual(coverage(**p, capture_bindings=[binding])['catalogueCount'], 3)
        binding['nativeBytesVerified'] = False
        with self.assertRaises(ValueError): coverage(**p, capture_bindings=[binding])

    def test_different_family_needs_pinned_prior_qualification(self):
        p, binding = self.binding()
        binding['sourceIdentifiers'] = ['DIFFERENT-100-V1']
        catalogue = {r['DocumentUID']: r for r in p['catalogue']}
        captures = {r['Id']: r for r in p['captures']}
        with self.assertRaises(ValueError): validate_capture_binding(binding, catalogue, captures)
        qualification = dict(state='qualified_edition_variant', catalogueItemId=1,
                             registerId='LOCAL-001-V1', registerTitle=p['catalogue'][0]['sourceTitle'],
                             sourceIdentifiers=binding['sourceIdentifiers'], basis='Fictional recorded code discrepancy')
        binding.update(associationQualification=qualification, qualificationSHA256=digest(qualification))
        validate_capture_binding(binding, catalogue, captures)
        qualification['catalogueItemId'] = 2
        with self.assertRaises(ValueError): validate_capture_binding(binding, catalogue, captures)

    def source(self, text):
        return dict(text=text, textSHA256=hashlib.sha256(text.encode()).hexdigest(), originalSHA256='a'*64)

    def test_numeric_equivalence_foreign_reference_and_offsets(self):
        text = ('Version No.: 4.0\nRefer to External Manual Version No: 2 2018\n'
                'Version No.: 4; Effective From: 01/01/2020\n\f'
                'Body\nVersion No.: 4.0; Effective From: 01/01/2020\n')
        result = edition_review(self.source(text))
        self.assertEqual(result['state'], 'consistent_body_edition')
        self.assertEqual(result['retainedBodyEdition'], '4')
        for passage in result['currentLabelAssertions']:
            self.assertEqual(text[passage['start']:passage['end']], passage['quote'])
        self.assertFalse(result['currentAuthorityVerified'])

    def test_conflicting_header_footer_and_tampered_text_hold(self):
        source = self.source('Version No.: 4.0\nVersion No.: 3.0; Effective From: 01/01/2020\n')
        result = edition_review(source)
        self.assertEqual(result['state'], 'conflicting_or_insufficient_body_editions')
        self.assertIsNone(result['retainedBodyEdition'])
        source['text'] += 'Changed'
        with self.assertRaises(ValueError): edition_review(source)
        compressed = self.source('Version No.: 4.0\nVersion No.: 4.0; Effective From: 01/01/2020\n'
                                 '\fVersion No.: 3.0; EffectiveFrom: 01/01/2020\n')
        self.assertEqual(edition_review(compressed)['state'], 'conflicting_or_insufficient_body_editions')

    def test_identifier_punctuation_and_missing_version_keep_family(self):
        self.assertEqual(family('LOCAL-100 – V3.0'), family('LOCAL-100 V4'))
        self.assertEqual(family('LOCAL-100-06/28'), family('LOCAL-100-V1-0628'))
        self.assertNotEqual(family('LOCAL-100-V1'), family('LOCAL-101-V1'))


if __name__ == '__main__':
    unittest.main()
