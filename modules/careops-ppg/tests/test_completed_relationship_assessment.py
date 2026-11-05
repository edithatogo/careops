"""Complete positive/negative review packets; synthetic, offline, no auth access."""
import copy
import hashlib
import json
import stat
import tempfile
import unittest
from pathlib import Path
from scripts.ppg_catalogue_relationships import digest,literal_leads
from scripts.ppg_completed_relationship_assessment import (
    prepare_completion,catalogue_snapshot,relationship_snapshot,DIMENSIONS,write_private_result)


def fixture(positive=False):
    text=('Fictional source: independent notice. This notice describes a self-contained filing label. '
          'It delegates no work, requires no other local procedure, and makes no policy authority claim. '
          'This is synthetic evidence for workflow qualification only.')
    if positive:text+=' Refer to Fictional target procedure for the handoff.'
    raw=text.encode();pin=hashlib.sha256(raw).hexdigest();uid='fictional-completion-source-positive' if positive else 'fictional-completion-source-negative'
    source=dict(documentUID=uid,sourceVersion='retained-sha256:'+pin,originalSHA256=pin,textSHA256=pin)
    catalogue=[dict(DocumentUID=uid,sourceDocumentId='FIX-001',sourceTitle='Fictional independent source notice'),
               dict(DocumentUID='fictional-target',sourceDocumentId='FIX-002',sourceTitle='Fictional target procedure')]
    base=dict(Id=1,Title='Fictional completion qualification',AssessmentKey='fictional-completion-positive' if positive else 'fictional-completion-negative',DocumentUID=uid,
        SourceDocumentId='FIX-001',AssessmentState='Needs relationship review',SourceMembership='Retained outside source snapshot',
        SourceCount=1,ExistingOutgoingCount=0,ExistingIncomingCount=0,
        EvidenceManifest=json.dumps(dict(schemaVersion=1,sources=[source | dict(identityState='exact_register_identifier')],fictionalQualification=True)),
        AssessmentComplete=False,CurrentAuthorityVerified=False)
    rels=[]
    endpoint_sources=[]
    endpoint_evidence=[]
    if positive:
        target_text='Fictional target procedure: receives the referred handoff.'
        target_original=b'fictional target original'
        target_text_bytes=target_text.encode()
        target_original_sha=hashlib.sha256(target_original).hexdigest()
        target_text_sha=hashlib.sha256(target_text_bytes).hexdigest()
        target_version='retained-sha256:'+target_original_sha
        rels=[dict(RelationshipKey='fictional-link',FromDocumentUID=uid,ToDocumentUID='fictional-target',FromVersion=source['sourceVersion'],
                   ToVersion=target_version,RelationshipType='references',ReviewState='Proposed',Rationale='Explicit fictional handoff reference',EvidenceRef='Fictional fixture only')]
        endpoint_sources=[dict(documentUID=uid,sourceDocumentId='FIX-001',sourceVersion=source['sourceVersion'],originalSHA256=pin,textSHA256=pin,
                               identityState='exact_register_identifier',original_bytes=raw,text_bytes=raw),
                          dict(documentUID='fictional-target',sourceDocumentId='FIX-002',sourceVersion=target_version,originalSHA256=target_original_sha,
                               textSHA256=target_text_sha,identityState='exact_register_identifier',
                               original_bytes=target_original,text_bytes=target_text_bytes)]
        endpoint_evidence=[dict(documentUID=uid,sourceDocumentId='FIX-001',sourceVersion=source['sourceVersion'],originalSHA256=pin,textSHA256=pin,
                                passages=[dict(start=0,end=len(text),quote=text)]),
                           dict(documentUID='fictional-target',sourceDocumentId='FIX-002',sourceVersion=target_version,originalSHA256=target_original_sha,
                                textSHA256=target_text_sha,passages=[dict(start=0,end=len(target_text),quote=target_text)])]
    passage=dict(start=0,end=len(text),quote=text)
    leads=literal_leads(catalogue,source|dict(text=text))
    packet=dict(schemaVersion=1,source=source,scope=dict(kind='fictional-qualification',catalogueSHA256=digest(catalogue_snapshot(catalogue)),
        relationshipsSHA256=digest(relationship_snapshot(rels)),comparisonDocumentUIDs=sorted(r['DocumentUID'] for r in catalogue),
        limitations=['Fictional source and two-record comparison cohort; not a real PPG assessment.'],
        exclusionsRationale='Real catalogue and external requirements excluded: technical qualification only.'),
        review=dict(reviewerRef='agent:codex:technical-fixture-review',reviewedAtUtc='2026-10-24T00:00:00Z',
            method='Full fictional text inspection with literal and operative review; no clinical decision.',basis='full-text-and-operative-review',
            sections=[dict(start=0,end=len(text),notes='Inspected the complete synthetic notice and its explicit scope.')],
            dimensions={k:dict(notes=('Explicit fictional target handoff retained.' if positive else 'No local relationship identified in the complete synthetic notice; scope remains explicit.'),passages=[passage]) for k in DIMENSIONS},
            leadDispositions=[dict(leadKey=digest(l),disposition='linked-finding',relationshipKeys=['fictional-link'],rationale='Exact fictional target title is a handoff reference.') for l in leads],
            existingRelationshipDispositions=[dict(relationshipKey='fictional-link',disposition='retained-as-finding',rationale='Preserve proposed reference for the exact fictional source version.')] if positive else [],
            endpointEvidence=endpoint_evidence),
        result='relationships_identified' if positive else 'no_relationship_identified_within_scope',
        findingRelationshipKeys=['fictional-link'] if positive else [],
        conclusion='Fictional retained reference identified.' if positive else 'No relationship identified within the stated synthetic text/cohort scope; no wider absence claim.')
    return dict(base=base,packet=packet,catalogue=catalogue,relationships=rels,original_bytes=raw,text_bytes=raw,
                endpoint_sources=endpoint_sources)


class CompletedAssessment(unittest.TestCase):
    def test_cli_result_is_created_private_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'review.json'
            write_private_result(output, {'synthetic': True})
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertEqual(json.loads(output.read_text()), {'synthetic': True})
            with self.assertRaises(FileExistsError):
                write_private_result(output, {'synthetic': False})
            self.assertEqual(json.loads(output.read_text()), {'synthetic': True})

    def test_negative_result_is_scoped_pinned_and_deterministic(self):
        p=fixture();before=copy.deepcopy(p);r=prepare_completion(**p)
        self.assertEqual(r['patch']['AssessmentState'],'Assessed with no finding')
        self.assertTrue(r['patch']['AssessmentComplete']);self.assertFalse(r['patch']['CurrentAuthorityVerified'])
        self.assertEqual(r,prepare_completion(**p));self.assertEqual(p,before)
        self.assertIn('clinicalAcceptance',r['patch']['EvidenceManifest'])

    def test_positive_requires_saved_exact_edition_findings_and_all_lead_dispositions(self):
        p=fixture(True);self.assertEqual(prepare_completion(**p)['patch']['AssessmentState'],'Assessed with candidates')
        p['packet']['review']['leadDispositions']=[]
        with self.assertRaisesRegex(ValueError,'Every generated lead'):prepare_completion(**p)

    def test_empty_scan_is_insufficient_without_full_review(self):
        for key in ['basis','sections','dimensions','reviewerRef','method']:
            p=fixture();p['packet']['review'].pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):prepare_completion(**p)

    def test_source_bytes_text_hash_and_native_source_bindings_refused_on_drift(self):
        for key in ['original_bytes','text_bytes','base']:
            p=fixture()
            if key=='base':p['base']['EvidenceManifest']=json.dumps(dict(sources=[]))
            else:p[key]=b'changed'
            with self.subTest(key=key),self.assertRaises(ValueError):prepare_completion(**p)

    def test_native_subject_identity_cannot_be_promoted_by_stale_endpoint(self):
        for state in ('retained_body_bound', 'unresolved_source_attribution', None):
            p = fixture(True)
            manifest = json.loads(p['base']['EvidenceManifest'])
            if state is None:
                del manifest['sources'][0]['identityState']
            else:
                manifest['sources'][0]['identityState'] = state
            p['base']['EvidenceManifest'] = json.dumps(manifest)
            self.assertEqual(p['endpoint_sources'][0]['identityState'], 'exact_register_identifier')
            with self.subTest(native_state=state), self.assertRaisesRegex(
                ValueError, 'Native subject source identity is not qualified'
            ):
                prepare_completion(**p)

    def test_native_subject_uid_cannot_be_rebound_by_caller(self):
        p = fixture(True)
        manifest = json.loads(p['base']['EvidenceManifest'])
        manifest['sources'][0]['documentUID'] = 'different-fictional-native-uid'
        p['base']['EvidenceManifest'] = json.dumps(manifest)
        with self.assertRaisesRegex(ValueError, 'Native subject source identity is not qualified'):
            prepare_completion(**p)

    def test_each_native_qualified_subject_identity_is_accepted(self):
        for state in ('exact_register_identifier', 'verified_source_identity', 'qualified_edition_variant'):
            p = fixture(True)
            manifest = json.loads(p['base']['EvidenceManifest'])
            manifest['sources'][0]['identityState'] = state
            p['base']['EvidenceManifest'] = json.dumps(manifest)
            with self.subTest(native_state=state):
                self.assertTrue(prepare_completion(**p)['patch']['AssessmentComplete'])

    def test_comparison_scope_and_relationship_snapshot_must_be_complete(self):
        for mutate in ['catalogue','scope','relationships']:
            p=fixture()
            if mutate=='catalogue':p['catalogue'][0]['sourceTitle']='Changed title'
            if mutate=='scope':p['packet']['scope']['comparisonDocumentUIDs']=[]
            if mutate=='relationships':p['packet']['scope']['relationshipsSHA256']='0'*64
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):prepare_completion(**p)

    def test_negative_refuses_existing_relationships_and_unresolved_leads(self):
        p=fixture(True);p['packet']['result']='no_relationship_identified_within_scope';p['packet']['findingRelationshipKeys']=[]
        with self.assertRaisesRegex(ValueError,'No-finding'):prepare_completion(**p)
        p=fixture(True);p['packet']['review']['leadDispositions'][0]['disposition']='unresolved'
        with self.assertRaisesRegex(ValueError,'Unresolved'):prepare_completion(**p)

    def test_gaps_overlaps_invented_passages_and_held_sources_refused(self):
        for mutate in ['gap','overlap','quote','held']:
            p=fixture()
            if mutate=='gap':p['packet']['review']['sections'][0]['end']-=1
            if mutate=='overlap':p['packet']['review']['sections']*=2
            if mutate=='quote':next(iter(p['packet']['review']['dimensions'].values()))['passages'][0]['quote']='invented'
            if mutate=='held':
                m=json.loads(p['base']['EvidenceManifest']);m['sources'][0]['versionConflict']=True;p['base']['EvidenceManifest']=json.dumps(m)
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):prepare_completion(**p)

    def test_missing_text_record_and_existing_completed_state_cannot_be_promoted(self):
        p=fixture();p['base']['AssessmentState']='Needs evidence'
        with self.assertRaises(ValueError):prepare_completion(**p)
        p=fixture();p['base']['AssessmentComplete']=True
        with self.assertRaises(ValueError):prepare_completion(**p)

    def test_source_identity_and_qualified_review_timestamp_required(self):
        for change in ['identity','future','timezone']:
            p=fixture()
            if change=='identity':p['packet']['source']['documentUID']='other'
            if change=='future':p['packet']['review']['reviewedAtUtc']='2999-01-01T00:00:00Z'
            if change=='timezone':p['packet']['review']['reviewedAtUtc']='2026-10-24T00:00:00'
            with self.subTest(change=change),self.assertRaises(ValueError):prepare_completion(**p)

    def test_missing_endpoint_edition_and_unknown_identity_refuse_completion(self):
        p=fixture(True);p['relationships'][0]['ToVersion']=''
        with self.assertRaisesRegex(ValueError,'ToVersion'):prepare_completion(**p)
        p=fixture(True);p['relationships'][0]['ToDocumentUID']='unresolved-target'
        p['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(p['relationships']))
        with self.assertRaisesRegex(ValueError,'identity is unresolved'):prepare_completion(**p)

    def test_positive_requires_both_endpoint_editions_and_source_passages(self):
        p=fixture(True)
        p['relationships'][0]['ToVersion']='unverified-nonempty-edition'
        p['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(p['relationships']))
        p['endpoint_sources']=[]
        p['packet']['review'].pop('endpointEvidence')
        with self.assertRaisesRegex(ValueError,'Subject endpoint evidence|lacks qualified source evidence'):
            prepare_completion(**p)

        p=fixture(True)
        p['relationships'][0]['ToVersion']='unverified-nonempty-edition'
        p['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(p['relationships']))
        with self.assertRaisesRegex(ValueError,'lacks qualified source evidence'):
            prepare_completion(**p)
        p=fixture(True)
        p['packet']['review']['endpointEvidence'][1]['documentUID']='wrong-endpoint'
        with self.assertRaisesRegex(ValueError,'lacks qualified source evidence'):
            prepare_completion(**p)
        p=fixture(True)
        p['endpoint_sources'][1]['versionConflict']=True
        with self.assertRaisesRegex(ValueError,'remains held'):
            prepare_completion(**p)

    def test_endpoint_edition_token_must_bind_to_original_bytes_and_catalogue_identity(self):
        p=fixture(True)
        p['endpoint_sources'][1]['sourceVersion']='unverified-nonempty-edition'
        p['relationships'][0]['ToVersion']='unverified-nonempty-edition'
        p['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(p['relationships']))
        p['packet']['review']['endpointEvidence'][1]['sourceVersion']='unverified-nonempty-edition'
        with self.assertRaisesRegex(ValueError,'not bound to original bytes'):
            prepare_completion(**p)

        p=fixture(True)
        p['endpoint_sources'][1]['sourceDocumentId']='FIX-001'
        with self.assertRaisesRegex(ValueError,'does not uniquely bind'):
            prepare_completion(**p)

    def test_subject_endpoint_bytes_cannot_diverge_from_reviewed_source(self):
        p=fixture(True)
        forged=b'other subject inspection text'
        p['endpoint_sources'][0]['text_bytes']=forged
        p['endpoint_sources'][0]['textSHA256']=hashlib.sha256(forged).hexdigest()
        p['packet']['review']['endpointEvidence'][0]['textSHA256']=p['endpoint_sources'][0]['textSHA256']
        with self.assertRaisesRegex(ValueError,'differs from the reviewed source bytes'):
            prepare_completion(**p)

    def test_incoming_relationship_is_edition_bound_on_both_sides(self):
        p=fixture(True)
        row=p['relationships'][0]
        row['FromDocumentUID'],row['ToDocumentUID']=row['ToDocumentUID'],row['FromDocumentUID']
        row['FromVersion'],row['ToVersion']=row['ToVersion'],row['FromVersion']
        p['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(p['relationships']))
        self.assertEqual(prepare_completion(**p)['patch']['AssessmentState'],'Assessed with candidates')
