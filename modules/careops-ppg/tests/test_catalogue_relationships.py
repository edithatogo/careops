"""Synthetic catalogue accounting and retrieval refusal cases; no native/auth calls."""
import copy
import hashlib
import unittest
from scripts.ppg_catalogue_relationships import coverage, literal_leads, relationship_key, render
from scripts.ppg_relationship_context import review_context


def fixture():
    catalogue = [dict(Id=i, DocumentUID=uid, sourceDocumentId=code, sourceTitle=title,
                      OData__UIVersionString='1.0') for i,uid,code,title in [
        (1,'a','LOCAL-001-V1','Fictional local source policy'),
        (2,'b','LOCAL-002-V1','Fictional reference target procedure'),
        (3,'c','LOCAL-003-V1','Fictional unlocated third policy')]]
    text = 'This retained fictional policy refers to Fictional reference target procedure.\n' + 'Sample text. ' * 30
    source = dict(documentUID='a', originalSHA256='a'*64, textSHA256=hashlib.sha256(text.encode()).hexdigest(),
                  text=text, textChars=len(text), sourceVersion='retained:1', identityState='exact_register_identifier')
    return dict(catalogue=catalogue,source_rows=[dict(document_id=r['sourceDocumentId'],catalogue_item_id=r['Id'],status='matching_register_document') for r in catalogue],
                captures=[dict(Id=10,PPGDocumentUID='a',PPGCaptureSHA256='a'*64,PPGCaptureKind='Document')],sources=[source],relationships=[],observed_at='2026-10-24T00:00:00Z')


class CatalogueRelationships(unittest.TestCase):
    def test_all_rows_accounted_and_literal_screen_never_completes_assessment(self):
        pack=fixture();before=copy.deepcopy(pack);report=coverage(**pack)
        self.assertEqual(report['catalogueCount'],3)
        self.assertEqual(report['coverageCounts'],{'awaiting_relationship_review':1,'missing_qualified_text':2})
        self.assertEqual(report['completedAssessmentCount'],0)
        self.assertFalse(report['fullCoverageAchieved'])
        self.assertTrue(all(not r['noFindingEstablished'] for r in report['rows']))
        self.assertEqual(pack,before)

    def test_unbound_active_and_retained_native_identities_stay_distinct(self):
        pack=fixture();pack['source_rows']=pack['source_rows'][:2]+[dict(document_id='NEW-004',catalogue_item_id=None)]
        r=coverage(**pack)
        self.assertEqual(r['boundActiveCount'],2)
        self.assertEqual(len(r['unboundActiveSourceRows']),1)
        self.assertEqual(r['retainedOutsideSourceCount'],1)

    def test_identity_drift_duplicate_rows_and_text_tampering_refused(self):
        for change in ('duplicate','binding','text','capture','source_membership'):
            pack=fixture()
            if change=='duplicate':pack['catalogue'].append(pack['catalogue'][0])
            if change=='binding':pack['source_rows'][0]['document_id']='changed'
            if change=='text':pack['sources'][0]['text']='tampered'
            if change=='capture':pack['captures']=[]
            if change=='source_membership':pack['source_rows'][1]['catalogue_item_id']=1
            with self.subTest(change=change),self.assertRaises(ValueError):coverage(**pack)

    def test_literal_offsets_and_ambiguous_targets_not_guessed(self):
        p=fixture();p['catalogue'][2]['sourceTitle']=p['catalogue'][1]['sourceTitle']
        leads=literal_leads(p['catalogue'],p['sources'][0]);self.assertEqual(len(leads),1)
        lead=leads[0];self.assertEqual(lead['targetCandidates'],['b','c'])
        self.assertEqual(p['sources'][0]['text'][lead['start']:lead['end']],lead['quote'])
        self.assertFalse(lead['establishesDependency'])
        self.assertEqual(lead['reviewState'],'Unreviewed')

    def test_full_catalogue_scan_has_no_top_n_and_matches_punctuation_variants(self):
        p=fixture();text='Use LOCAL / 002 - V1.\fSee Fictional reference target procedure.'
        p['sources'][0].update(text=text,textSHA256=hashlib.sha256(text.encode()).hexdigest())
        leads=literal_leads(p['catalogue'],p['sources'][0])
        self.assertEqual(len(leads),2)
        self.assertTrue(leads[1]['locator'].startswith('page:2;'))

    def test_dependency_reverse_links_allow_operational_cycle_without_authority(self):
        def edge(key,a,b,kind='depends_on',av='1',bv='1'):
            return dict(relationshipId=key,fromDocumentUID=a,fromVersion=av,toDocumentUID=b,toVersion=bv,type=kind,status='proposed')
        rows=[edge('1','a','b'),edge('2','b','a')]
        ctx=review_context(rows,'a','1')
        self.assertEqual(len(ctx['outgoingDependencies']),1)
        self.assertEqual(len(ctx['incomingDependencies']),1)
        self.assertFalse(ctx['acceptedUpstream'])
        rows=[edge('1','a','b','governed_by'),edge('2','b','a','implements')]
        for row in rows:row['status']='accepted'
        with self.assertRaises(ValueError):review_context(rows,'a','1')
        rows[1]['fromVersion']='2'
        # Retain the established conservative governance-cycle refusal.
        with self.assertRaises(ValueError):review_context(rows,'a','1')

    def test_renderer_escapes_untrusted_text_and_rejects_unsafe_links(self):
        p=fixture();p['catalogue'][0]['sourceTitle']='<script>alert(1)</script>'
        r=coverage(**p);html=render(r,'https://example.test/catalogue','https://example.test/annotations')
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        with self.assertRaises(ValueError):render(r,'javascript:bad','https://example.test/annotations')

class AssessmentPersistence(unittest.TestCase):
    def test_payload_redacts_local_paths_and_refuses_completion_claim(self):
        from scripts.ppg_catalogue_relationships import assessment_payloads
        pack=fixture();pack['sources'][0]['originalPath']='/private/source.pdf'
        r=coverage(**pack);p=assessment_payloads(r)
        self.assertNotIn('/private',str(p))
        self.assertFalse(p[0]['AssessmentComplete'])
        r['completedAssessmentCount']=1
        with self.assertRaises(ValueError):assessment_payloads(r)

    def test_replay_and_changed_human_record_protection(self):
        from scripts.ppg_catalogue_relationships import assessment_payloads,plan_creates
        p=assessment_payloads(coverage(**fixture()))
        self.assertEqual(len(plan_creates(p,[])['creates']),3)
        native=[dict(x,Id=i) for i,x in enumerate(p)]
        self.assertEqual(plan_creates(p,native)['creates'],[])
        native[0]['AssessmentState']='Assessed with no finding'
        with self.assertRaises(ValueError):plan_creates(p,native)

class DependencyEvidence(unittest.TestCase):
    def test_relationship_key_binds_exact_versioned_endpoints_and_type(self):
        key=relationship_key('00000000-0000-4000-8000-000000000001',
            'retained-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            '00000000-0000-4000-8000-000000000002',
            'retained-sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'references')
        expected = 'b68bf17349a5d6553af4cbb22a5a17a6b714d64dc4cb493876ef1dc7b5e62865'
        self.assertEqual(key, expected)
        self.assertEqual(key,relationship_key('00000000-0000-4000-8000-000000000001',
            'retained-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            '00000000-0000-4000-8000-000000000002',
            'retained-sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'references'))
        self.assertNotEqual(key,relationship_key('00000000-0000-4000-8000-000000000001',
            'retained-sha256:different', '00000000-0000-4000-8000-000000000002',
            'retained-sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            'references'))
        for args in [('', 'v1', 'target', 'v1', 'references'),
                     ('same', 'v1', 'same', 'v2', 'references'),
                     ('source', 'v1', 'target', 'v1', 'invented')]:
            with self.subTest(args=args),self.assertRaises(ValueError):relationship_key(*args)

    def test_both_passages_required_and_current_authority_not_inferred(self):
        from scripts.ppg_catalogue_relationships import dependency_proposal
        p=fixture();a=p['sources'][0];b=copy.deepcopy(a);b['documentUID']='b'
        r=dependency_proposal(a,b,'refers to','Sample text.','Fictional dependency rationale','Recheck both endpoints on change')
        self.assertEqual(r['ReviewState'],'Proposed')
        self.assertEqual(r['RelationshipType'],'depends_on')
        self.assertIn('"currentAuthorityVerified": false',r['EvidenceRef'])
        with self.assertRaises(ValueError):dependency_proposal(a,b,'invented','Sample text.','why','impact')
        b['versionConflict']=True
        with self.assertRaises(ValueError):dependency_proposal(a,b,'refers to','Sample text.','why','impact')
