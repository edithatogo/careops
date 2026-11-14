import copy, hashlib, importlib.util, json, unittest
from scripts.ppg_multi_edition import prepare_multi_completion
spec=importlib.util.spec_from_file_location('fixtures', 'tests/test_completed_relationship_assessment.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def sample():
 p=f.fixture(); p2=copy.deepcopy(p); raw=p['original_bytes']+b' distinct original'; sha=hashlib.sha256(raw).hexdigest()
 p2['original_bytes']=raw; s=p2['packet']['source']; s['originalSHA256']=sha; s['sourceVersion']='retained-sha256:'+sha
 m=json.loads(p['base']['EvidenceManifest']); m['sources'].append(s | {'identityState':'exact_register_identifier'}); p['base']['EvidenceManifest']=json.dumps(m); p['base']['SourceCount']=2
 companions=[{k:x[k] for k in ('packet','original_bytes','text_bytes','endpoint_sources')} for x in (p,p2)]
 return dict(base=p['base'],companions=companions,catalogue=p['catalogue'],relationships=p['relationships'])

class Multi(unittest.TestCase):
 def test_two_editions_independently_sealed(self):
  p=sample(); old=copy.deepcopy(p); r=prepare_multi_completion(**p); self.assertEqual(p,old); self.assertTrue(r['patch']['AssessmentComplete']); self.assertFalse(r['patch']['CurrentAuthorityVerified']); m=json.loads(r['patch']['EvidenceManifest']); self.assertEqual(len(m['completedAssessment']['editions']),2); self.assertIsNone(m['completedAssessment']['clinicalAcceptance']); self.assertEqual(r,prepare_multi_completion(**p))
 def test_missing_duplicate_unqualified_and_mismatched_bytes_rejected(self):
  for mode in ('missing','duplicate','identity','bytes','graph'):
   p=sample()
   if mode=='missing':p['companions'].pop()
   if mode=='duplicate':p['companions'][1]=copy.deepcopy(p['companions'][0])
   if mode=='identity':p['companions'][1]['packet']['source']['documentUID']='other'
   if mode=='bytes':p['companions'][1]['text_bytes']=b'tampered'
   if mode=='graph':p['companions'][1]['packet']['scope']['relationshipsSHA256']='0'*64
   with self.subTest(mode=mode), self.assertRaises(ValueError):prepare_multi_completion(**p)
 def test_unreviewed_incident_rejected(self):
  p=sample(); p['relationships']=[dict(RelationshipKey='x',FromDocumentUID=p['base']['DocumentUID'],ToDocumentUID='fictional-target',FromVersion='unreviewed',ToVersion='other',RelationshipType='references',ReviewState='Accepted',Rationale='fixture',EvidenceRef='fixture')]
  from scripts.ppg_catalogue_relationships import digest
  from scripts.ppg_completed_relationship_assessment import relationship_snapshot
  for c in p['companions']:c['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(p['relationships']))
  with self.assertRaisesRegex(ValueError,'unreviewed edition'):prepare_multi_completion(**p)
if __name__=='__main__':unittest.main()
