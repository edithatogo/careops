const test=require('node:test');const assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process');
function fixture(positive=false){return JSON.parse(execFileSync(process.env.PPG_PYTHON || '.venv/bin/python',['-c',
 'import json;from tests.test_completed_relationship_assessment import fixture;from scripts.ppg_completed_relationship_assessment import prepare_completion;print(json.dumps(prepare_completion(**fixture('+ (positive?'True':'False') +'))))'],{encoding:'utf8'}));}
test('sealed positive and no-finding transitions both validate',async()=>{
 const {validateTransition}=await import('../tools/review-intelligence/complete-assessment.mjs');
 for(const positive of [false,true])assert.equal(validateTransition(fixture(positive)).patch.AssessmentComplete,true);
});
test('tampered patch, validation, identity, and unsealed evidence are refused',async()=>{
 const {validateTransition}=await import('../tools/review-intelligence/complete-assessment.mjs');
 for(const change of ['patch','validation','identity','evidence']){const t=fixture();
  if(change==='patch')t.patch.AssessmentState='Assessed with candidates';
  if(change==='validation')t.validation.fullTextAccounted=false;
  if(change==='identity')t.documentUID='other';
  if(change==='evidence')t.patch.EvidenceManifest='{}';
  assert.throws(()=>validateTransition(t),change);
 }
});
test('legacy transitions and positive transitions without endpoint edition validation are refused',async()=>{
 const {validateTransition}=await import('../tools/review-intelligence/complete-assessment.mjs');
 const legacy=fixture(true);legacy.schemaVersion=1;
 assert.throws(()=>validateTransition(legacy),/VALIDATED_TRANSITION_REQUIRED/);
 const unbound=fixture(true);unbound.validation.endpointEditionsVerified=false;
 assert.throws(()=>validateTransition(unbound),/ENDPOINT_EDITION_EVIDENCE_REQUIRED/);
});
test('conditional save requires exact readback and replay never writes',async()=>{
 const {completeAssessment}=await import('../tools/review-intelligence/complete-assessment.mjs');const t=fixture();let fields={Id:t.itemId,...t.before},sends=0;const journal=[];
 const options={transition:t,read:async()=>({fields,etag:'"1"'}),merge:async(id,patch,etag)=>{assert.equal(etag,'"1"');sends++;fields={...fields,...patch};},journal:async x=>journal.push(x)};
 assert.equal((await completeAssessment(options)).updated,true);assert.equal(sends,1);
 assert.equal((await completeAssessment(options)).replay,true);assert.equal(sends,1);assert.deepEqual(journal.map(x=>x.phase),['intent','verified']);
});
test('human change, wrong target and wildcard ETag stop before mutation',async()=>{
 const {completeAssessment}=await import('../tools/review-intelligence/complete-assessment.mjs');const t=fixture();let sends=0;
 for(const change of ['title','identity','etag']){const fields={Id:t.itemId,...t.before};if(change==='title')fields.Title='Human edit';if(change==='identity')fields.Id=99;
  await assert.rejects(completeAssessment({transition:t,read:async()=>({fields,etag:change==='etag'?'*':'"1"'}),merge:async()=>{sends++;},journal:async()=>{}}));
 }assert.equal(sends,0);
});
test('lost acknowledgement leaves intent only; resume reads committed state without resend',async()=>{
 const {completeAssessment}=await import('../tools/review-intelligence/complete-assessment.mjs');const t=fixture(true);let fields={Id:t.itemId,...t.before},sends=0;const journal=[];
 const options={transition:t,read:async()=>({fields,etag:'"1"'}),merge:async(id,patch)=>{sends++;fields={...fields,...patch};throw Error('lost acknowledgement');},journal:async x=>journal.push(x)};
 await assert.rejects(completeAssessment(options),/lost acknowledgement/);assert.equal(sends,1);assert.deepEqual(journal.map(x=>x.phase),['intent']);
 assert.equal((await completeAssessment(options)).replay,true);assert.equal(sends,1);
});
test('success without actual persisted bytes is not accepted',async()=>{
 const {completeAssessment}=await import('../tools/review-intelligence/complete-assessment.mjs');const t=fixture();const journal=[];
 await assert.rejects(completeAssessment({transition:t,read:async()=>({fields:{Id:t.itemId,...t.before},etag:'"1"'}),merge:async()=>{},journal:async x=>journal.push(x)}),/READBACK/);
 assert.deepEqual(journal.map(x=>x.phase),['intent']);
});
test('evidence correction is append-only, conditional, and duplicate-free on replay',async()=>{
 const {appendAssessmentEvidenceAmendment}=await import('../tools/review-intelligence/complete-assessment.mjs');
 const canonical=x=>Array.isArray(x)?'['+x.map(canonical).join(',')+']':x&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}':JSON.stringify(x);
 const hash=x=>require('node:crypto').createHash('sha256').update(canonical(x)).digest('hex');
 const prior={completionKey:'prior-completion-key',conclusion:'original completion retained',source:{documentUID:'document-41'}};
 const completed={conclusion:'corrected scope was fully re-reviewed',currentAuthorityVerified:false,establishesCompliance:false,clinicalAcceptance:null,scope:{catalogueSHA256:'catalogue-r4',relationshipsSHA256:'relationships-r4'},source:{documentUID:'document-41'}};
 completed.completionKey=hash(completed);
 const payload={kind:'scope-revalidation',reviewedAtUtc:'2026-10-25T08:00:00Z',priorCompletionKey:prior.completionKey,priorCompletionEvidenceSHA256:hash(prior),correctedCompletionEvidence:completed,correctedCompletionKey:completed.completionKey,packetSHA256:'packet-sha',batchSHA256:'batch-sha',replaySHA256:'batch-sha',catalogueSHA256:'catalogue-r4',relationshipsSHA256:'relationships-r4'};
 payload.amendmentKey=hash(payload);
 const fields={Id:41,AssessmentKey:'assessment-41',DocumentUID:'document-41',AssessmentComplete:true,AssessmentState:'Assessed with no finding',CurrentAuthorityVerified:false,Title:'Human-edited title',ExistingIncomingCount:3,SourceMembership:'Human-reviewed membership',EvidenceManifest:JSON.stringify({completedAssessment:prior,other:'preserve'})};
 const originalManifest=fields.EvidenceManifest, amendment={kind:'assessment_evidence_amendment',schemaVersion:1,itemId:41,assessmentKey:fields.AssessmentKey,documentUID:fields.DocumentUID,expectedEvidenceManifestSHA256:require('node:crypto').createHash('sha256').update(originalManifest).digest('hex'),amendment:payload};
 let sends=0;const journal=[];const options={amendment,read:async()=>({fields,etag:'"4"'}),merge:async(id,patch,etag)=>{assert.equal(id,41);assert.equal(etag,'"4"');assert.deepEqual(Object.keys(patch),['EvidenceManifest']);sends++;Object.assign(fields,patch);},journal:async x=>journal.push(x)};
 assert.equal((await appendAssessmentEvidenceAmendment(options)).updated,true);assert.equal(sends,1);
 assert.equal(fields.Title,'Human-edited title');assert.equal(fields.ExistingIncomingCount,3);assert.equal(fields.SourceMembership,'Human-reviewed membership');
 const after=JSON.parse(fields.EvidenceManifest);assert.deepEqual(after.completedAssessment,prior);assert.equal(after.other,'preserve');assert.equal(after.assessmentReviewAddenda.length,1);assert.deepEqual(after.assessmentReviewAddenda[0],payload);
 assert.equal((await appendAssessmentEvidenceAmendment(options)).replay,true);assert.equal(sends,1);assert.deepEqual(journal.map(x=>x.phase),['intent','verified']);
});
