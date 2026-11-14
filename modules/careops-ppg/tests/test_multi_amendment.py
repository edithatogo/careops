import copy, hashlib, json, os, subprocess, sys, unittest
from pathlib import Path
from scripts.ppg_multi_edition import prepare_multi_completion
from scripts.ppg_assessment_history_archive import prepare_archive, restore_original
from tests.test_multi_edition import sample
from scripts.ppg_multi_amendment import prepare_multi_amendment

class AmendmentCompiler(unittest.TestCase):
 def setUp(self):
  self.p=sample(); self.t=prepare_multi_completion(**self.p); self.base={'Id':self.t['itemId'],**self.t['after']}; self.saved=copy.deepcopy(self.base)
  self.companions=copy.deepcopy(self.p['companions'])
  for c in self.companions:c['packet']['review']['method']='Fictional corrected reinspection of complete retained edition.'
 def compile(self,base=None):return prepare_multi_amendment(base or self.base,self.companions,self.p['catalogue'],self.p['relationships'],1000000)
 def test_independent_review_and_writer_validation(self):
  a=self.compile();self.assertEqual(self.base,self.saved);self.assertNotEqual(a['amendment']['transition']['completionKey'],self.t['completionKey']);self.assertEqual(a['before']['EvidenceManifest'],self.base['EvidenceManifest']);self.assertTrue(a['amendment']['transition']['validation']['allManifestEditionsIndependentlyValidated']);self.assertEqual(self.compile(),a)
  script='''import fs from 'node:fs';import{appendAssessmentEvidenceAmendment}from './tools/review-intelligence/complete-assessment.mjs';let {a,context}=JSON.parse(fs.readFileSync(0));let f=structuredClone(a.before),n=0;let read=async()=>({fields:structuredClone(f),etag:'"1"'});const o={amendment:a,read,readContext:async()=>context,assertGraphOwnership:async()=>{},journal:async()=>{},merge:async(i,p)=>{n++;f={...f,...p}}};if(!(await appendAssessmentEvidenceAmendment(o)).updated)throw Error('not saved');if(!(await appendAssessmentEvidenceAmendment(o)).replay||n!==1)throw Error('replay failed');'''
  from scripts.ppg_completed_relationship_assessment import catalogue_snapshot,relationship_snapshot
  ctx={'catalogue':catalogue_snapshot(self.p['catalogue']),'relationships':relationship_snapshot(self.p['relationships'])}
  subprocess.run(['node','--input-type=module','-e',script],input=json.dumps({'a':a,'context':ctx}),text=True,check=True)
 def test_reject_unreviewed_source_or_graph(self):
  self.companions.pop()
  with self.assertRaises(ValueError):self.compile()
 def test_reject_human_identity_and_invalid_root(self):
  base=copy.deepcopy(self.base);m=json.loads(base['EvidenceManifest']);m['completedAssessment']['subjectUID']='other';base['EvidenceManifest']=json.dumps(m)
  with self.assertRaises(ValueError):self.compile(base)
 def test_exact_projection_and_scalar_fields(self):
  base={**self.base,'__metadata':{'etag':'"4"'},'Modified':'fictional','EditorId':7,'OData__UIVersionString':'4.0'};a=self.compile(base);self.assertNotIn('__metadata',a['before']);self.assertNotIn('Modified',a['before']);self.assertEqual(set(a['before']),set(self.base))
  for field,value in [('Title',{'nested':'no'}),('SourceCount',True),('ExistingIncomingCount',-1),('CurrentAuthorityVerified',0)]:
   altered=copy.deepcopy(self.base);altered[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):self.compile(altered)
  with self.assertRaisesRegex(ValueError,'Project native record') :self.compile({**self.base,'FictionalUnownedField':{'value':'x'}})
 def test_changed_human_field_is_rejected_without_send(self):
  a=self.compile();script="import fs from 'node:fs';import{appendAssessmentEvidenceAmendment}from './tools/review-intelligence/complete-assessment.mjs';let a=JSON.parse(fs.readFileSync(0)),f={...a.before,Title:'Fictional human edit'},n=0;try{await appendAssessmentEvidenceAmendment({amendment:a,read:async()=>({fields:f,etag:'\"1\"'}),readContext:async()=>{throw Error('must not read graph')},assertGraphOwnership:async()=>{},journal:async()=>{},merge:async()=>{n++}});throw Error('unexpected acceptance')}catch(e){if(e.message!=='MULTI_AMENDMENT_PREIMAGE_MISMATCH'||n)throw e}";subprocess.run(['node','--input-type=module','-e',script],input=json.dumps(a),text=True,check=True)
 def test_new_graph_finding_changes_outcome_using_compiled_packets(self):
  from scripts.ppg_catalogue_relationships import digest
  from scripts.ppg_completed_relationship_assessment import relationship_snapshot
  first=self.companions[0];source=first['packet']['source'];uid=self.base['DocumentUID'];target_raw=b'fictional target original';target_text=b'Fictional target procedure: receives the referred handoff.';oh=hashlib.sha256(target_raw).hexdigest();th=hashlib.sha256(target_text).hexdigest();version='retained-sha256:'+oh
  graph=[dict(RelationshipKey='fictional-new-link',FromDocumentUID=uid,ToDocumentUID='fictional-target',FromVersion=source['sourceVersion'],ToVersion=version,RelationshipType='references',ReviewState='Proposed',Rationale='Fictional reviewed relationship',EvidenceRef='Fictional only')]
  for c in self.companions:c['packet']['scope']['relationshipsSHA256']=digest(relationship_snapshot(graph))
  packet=first['packet'];packet['result']='relationships_identified';packet['findingRelationshipKeys']=['fictional-new-link'];packet['conclusion']='Fictional retained relationship identified.';packet['review']['existingRelationshipDispositions']=[dict(relationshipKey='fictional-new-link',disposition='retained-as-finding',rationale='Fictional retained graph link.')]
  subject=source|dict(sourceDocumentId='FIX-001',identityState='exact_register_identifier',original_bytes=first['original_bytes'],text_bytes=first['text_bytes'])
  target=dict(documentUID='fictional-target',sourceDocumentId='FIX-002',sourceVersion=version,originalSHA256=oh,textSHA256=th,identityState='exact_register_identifier',original_bytes=target_raw,text_bytes=target_text)
  first['endpoint_sources']=[subject,target]
  def evidence(e):
   text=e['text_bytes'].decode();return {k:e[k] for k in ('documentUID','sourceDocumentId','sourceVersion','originalSHA256','textSHA256')}|dict(passages=[dict(start=0,end=len(text),quote=text)])
  packet['review']['endpointEvidence']=[evidence(subject),evidence(target)]
  a=prepare_multi_amendment(self.base,self.companions,self.p['catalogue'],graph,1000000)
  self.assertEqual(a['amendment']['transition']['patch']['AssessmentState'],'Assessed with candidates');self.assertEqual(a['amendment']['transition']['patch']['ExistingOutgoingCount'],1);self.assertEqual(a['amendment']['outgoingKeys'],['fictional-new-link'])
  from scripts.ppg_completed_relationship_assessment import catalogue_snapshot
  script="import fs from 'node:fs';import{appendAssessmentEvidenceAmendment}from './tools/review-intelligence/complete-assessment.mjs';let{a,c}=JSON.parse(fs.readFileSync(0)),f=structuredClone(a.before),n=0;let options={amendment:a,read:async()=>({fields:structuredClone(f),etag:'\"1\"'}),readContext:async()=>c,assertGraphOwnership:async()=>{},journal:async()=>{},merge:async(i,p)=>{n++;f={...f,...p}}};await appendAssessmentEvidenceAmendment(options);if(f.AssessmentState!=='Assessed with candidates'||f.ExistingOutgoingCount!==1)throw Error('wrong outcome');if(!(await appendAssessmentEvidenceAmendment(options)).replay||n!==1)throw Error('wrong replay');"
  subprocess.run(['node','--input-type=module','-e',script],input=json.dumps({'a':a,'c':{'relationships':relationship_snapshot(graph),'catalogue':catalogue_snapshot(self.p['catalogue'])}}),text=True,check=True)
 def test_archive_rebind(self):
  a=self.compile();m=json.loads(self.base['EvidenceManifest']);m['assessmentReviewAddenda']=[a['amendment']];first={**self.base,'EvidenceManifest':json.dumps(m,ensure_ascii=False)};b=self.compile(first);m['assessmentReviewAddenda'].append(b['amendment']);old=json.dumps(m,ensure_ascii=False);plan=prepare_archive(old,'https://example.invalid/archive');self.assertEqual(restore_original(plan.compacted_manifest,plan.archive_bytes),old)
  compacted={**self.base,'EvidenceManifest':plan.compacted_manifest};rebound=self.compile(compacted);self.assertEqual(rebound['before']['EvidenceManifest'],plan.compacted_manifest);self.assertNotEqual(rebound['amendment']['amendmentKey'],a['amendment']['amendmentKey']);self.assertEqual(rebound['expectedEvidenceManifestSHA256'],hashlib.sha256(plan.compacted_manifest.encode()).hexdigest());self.assertEqual(rebound['amendment']['priorCompletionKey'],a['amendment']['priorCompletionKey'])
if __name__=='__main__':unittest.main()
