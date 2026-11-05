/* One conditional transition of an existing assessment. Caller owns auth/transport.
   Supported packets are compiled by ppg_completed_relationship_assessment first. */
import {createHash} from 'node:crypto';
const canonical=x=>Array.isArray(x)?'['+x.map(canonical).join(',')+']':x&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}':JSON.stringify(x);
const sha=x=>createHash('sha256').update(canonical(x)).digest('hex');
const equal=(actual,expected)=>Object.entries(expected).every(([k,v])=>actual[k]===v);
export function validateTransition(t) {
 if(t?.kind!=='validated_relationship_assessment_completion'||t.schemaVersion!==2||!Number.isSafeInteger(t.itemId)||t.itemId<1||!t.assessmentKey||!t.documentUID)throw Error('VALIDATED_TRANSITION_REQUIRED');
 const v=t.validation;
 const isMulti = v?.allManifestEditionsIndependentlyValidated===true;
 if(!isMulti && (!v||['sourceBytesVerified','textBytesVerified','fullTextAccounted','allLeadsDisposed','allExistingLinksAccounted'].some(k=>v[k]!==true)||typeof v.fictionalQualification!=='boolean'))throw Error('INCOMPLETE_EVIDENCE_VALIDATION');
 if(!isMulti && t.patch?.AssessmentState==='Assessed with candidates'&&v.endpointEditionsVerified!==true)throw Error('ENDPOINT_EDITION_EVIDENCE_REQUIRED');
 if(t.before?.AssessmentComplete!==false||t.before?.AssessmentState!=='Needs relationship review'||t.before?.AssessmentKey!==t.assessmentKey||t.before?.DocumentUID!==t.documentUID||t.before?.CurrentAuthorityVerified!==false)throw Error('INVALID_PROGRESS_PREIMAGE');
 const patch=t.patch;
 if(!patch||Object.keys(patch).sort().join(',')!==['AssessmentComplete','AssessmentState','CurrentAuthorityVerified','EvidenceManifest','ExistingOutgoingCount','ExistingIncomingCount'].sort().join(',')||patch.AssessmentComplete!==true||patch.CurrentAuthorityVerified!==false||!['Assessed with candidates','Assessed with no finding'].includes(patch.AssessmentState)||['ExistingOutgoingCount','ExistingIncomingCount'].some(k=>!Number.isSafeInteger(patch[k])||patch[k]<0)||sha(patch)!==t.patchSHA256)throw Error('INVALID_COMPLETION_PATCH');
 const manifest=JSON.parse(patch.EvidenceManifest),e=manifest.completedAssessment;
 if(isMulti) {
  if(e?.kind!=='multi-retained-edition-review'||e.subjectUID!==t.documentUID||e.assessmentKey!==t.assessmentKey||e.completionKey!==t.completionKey||e.currentAuthorityVerified!==false||e.establishesCompliance!==false||e.clinicalAcceptance!==null||v.allActiveSubjectIncidentsAccounted!==true||!Array.isArray(e.editions)||!e.editions.length||v.editionCount!==e.editions.length)throw Error('INVALID_MULTI_EVIDENCE');
  const {completionKey,...aggregate}=e;
  if(sha(aggregate)!==completionKey||e.priorEvidenceManifestSHA256!==createHash('sha256').update(t.before.EvidenceManifest).digest('hex'))throw Error('MULTI_EVIDENCE_HASH_MISMATCH');
  const prior=JSON.parse(t.before.EvidenceManifest), sources=prior.sources;
  const identity=s=>canonical([s.documentUID,s.sourceVersion,s.originalSHA256,s.textSHA256]);
  if(!Array.isArray(sources)||sources.length!==e.editions.length||!Array.isArray(manifest.sources)||canonical(manifest.sources)!==canonical(sources))throw Error('MULTI_SOURCE_MEMBERSHIP_MISMATCH');
  const {completedAssessment:ignored,...remaining}=manifest;
  if(canonical(remaining)!==canonical(prior))throw Error('MULTI_PREIMAGE_CHANGED');
  if(sources.some(s=>s.documentUID!==t.documentUID||typeof s.originalSHA256!=='string'||! /^[0-9a-f]{64}$/.test(s.originalSHA256)||s.sourceVersion!=='retained-sha256:'+s.originalSHA256||typeof s.textSHA256!=='string'||! /^[0-9a-f]{64}$/.test(s.textSHA256)))throw Error('INVALID_MULTI_SOURCE');
  const expected=sources.map(identity), seen=[]; let outcome=false, cat=null;
  for(const x of e.editions) {
   const {completionKey:k,...body}=x, s=x.source, scope=x.scope;
   if(!k||sha(body)!==k||s?.documentUID!==t.documentUID||x.priorEvidenceManifestSHA256!==e.priorEvidenceManifestSHA256||x.currentAuthorityVerified!==false||x.establishesCompliance!==false||x.clinicalAcceptance!==null||scope?.relationshipsSHA256!==e.relationshipsSHA256||!scope?.catalogueSHA256||!['fictional-qualification','retained-edition-text-review'].includes(scope.kind)||((scope.kind==='fictional-qualification')!==(prior.fictionalQualification===true)))throw Error('INVALID_MULTI_COMPANION');
   if(cat!==null&&cat!==scope.catalogueSHA256)throw Error('MULTI_CATALOGUE_MISMATCH'); cat=scope.catalogueSHA256;
   if(!['relationships_identified','no_relationship_identified_within_scope'].includes(x.result))throw Error('INVALID_MULTI_OUTCOME');
   if(x.result==='relationships_identified')outcome=true;
   seen.push(identity(s));
  }
  if(new Set(expected).size!==expected.length||new Set(seen).size!==seen.length||canonical([...expected].sort())!==canonical([...seen].sort()))throw Error('MULTI_SOURCE_MEMBERSHIP_MISMATCH');
  if((patch.AssessmentState==='Assessed with candidates')!==outcome)throw Error('OUTCOME_MISMATCH');
 } else {
  if(!e||e.completionKey!==t.completionKey||e.source?.documentUID!==t.documentUID||e.currentAuthorityVerified!==false||e.establishesCompliance!==false||e.clinicalAcceptance!==null)throw Error('INVALID_COMPLETION_EVIDENCE');
  if(v.fictionalQualification!==(e.scope?.kind==='fictional-qualification')||v.fictionalQualification!==(manifest.fictionalQualification===true))throw Error('FICTIONAL_SCOPE_MISMATCH');
  const {completionKey,...payload}=e;
  if(sha(payload)!==completionKey)throw Error('COMPLETION_EVIDENCE_HASH_MISMATCH');
  if(e.priorEvidenceManifestSHA256!==createHash('sha256').update(t.before.EvidenceManifest).digest('hex'))throw Error('EVIDENCE_PREIMAGE_MISMATCH');
  if((patch.AssessmentState==='Assessed with no finding')!==(e.result==='no_relationship_identified_within_scope'))throw Error('OUTCOME_MISMATCH');
 }
 const after={...t.before,...patch};
 if(canonical(after)!==canonical(t.after))throw Error('AFTER_IMAGE_MISMATCH');
 return t;
}
export async function completeAssessment({transition,read,merge,journal}) {
 const t=validateTransition(transition);
 const initial=await read(t.itemId);
 if(initial?.fields?.Id!==t.itemId||initial.fields.AssessmentKey!==t.assessmentKey||initial.fields.DocumentUID!==t.documentUID)throw Error('NATIVE_IDENTITY_MISMATCH');
 if(equal(initial.fields,t.after))return {updated:false,replay:true,itemId:t.itemId,completionKey:t.completionKey};
 if(!equal(initial.fields,t.before))throw Error('PRESERVE_CHANGED_ASSESSMENT');
 if(typeof initial.etag!=='string'||!initial.etag.trim()||initial.etag==='*')throw Error('EXACT_ETAG_REQUIRED');
 await journal({phase:'intent',itemId:t.itemId,completionKey:t.completionKey,expectedETag:initial.etag,patchSHA256:t.patchSHA256});
 // No retries here. An uncertain response leaves intent only; resume by read/reconcile.
 await merge(t.itemId,t.patch,initial.etag);
 const observed=await read(t.itemId);
 if(observed?.fields?.Id!==t.itemId||!equal(observed.fields,t.after))throw Error('COMPLETION_READBACK_MISMATCH');
 await journal({phase:'verified',itemId:t.itemId,completionKey:t.completionKey,observedETag:observed.etag});
 return {updated:true,replay:false,itemId:t.itemId,completionKey:t.completionKey};
}

/* Append a reviewed evidence correction while preserving the original completion,
   assessment state, counts, membership and any human-edited fields. */
export function validateEvidenceAmendment(a) {
 if(a?.schemaVersion===2)return validateMultiAmendment(a);
 if(a?.kind!=='assessment_evidence_amendment'||a.schemaVersion!==1||!Number.isSafeInteger(a.itemId)||a.itemId<1||!a.assessmentKey||!a.documentUID||!a.expectedEvidenceManifestSHA256||!a.amendment||typeof a.amendment!=='object')throw Error('VALIDATED_EVIDENCE_AMENDMENT_REQUIRED');
 const {amendmentKey,...payload}=a.amendment;
 if(!amendmentKey||sha(payload)!==amendmentKey)throw Error('EVIDENCE_AMENDMENT_HASH_MISMATCH');
 const x=a.amendment;
 if(x.kind!=='scope-revalidation'||!x.priorCompletionKey||!x.priorCompletionEvidenceSHA256||!x.correctedCompletionEvidence||!x.correctedCompletionKey||!x.packetSHA256||!x.batchSHA256||x.batchSHA256!==x.replaySHA256||!x.catalogueSHA256||!x.relationshipsSHA256||!x.reviewedAtUtc)throw Error('INCOMPLETE_EVIDENCE_AMENDMENT');
 const {completionKey,...completionPayload}=x.correctedCompletionEvidence;
 if(completionKey!==x.correctedCompletionKey||sha(completionPayload)!==completionKey||completionPayload.currentAuthorityVerified!==false||completionPayload.establishesCompliance!==false||completionPayload.clinicalAcceptance!==null||completionPayload.source?.documentUID!==a.documentUID)throw Error('INVALID_CORRECTED_COMPLETION_EVIDENCE');
 const scope=completionPayload.scope;
 if(scope?.catalogueSHA256!==x.catalogueSHA256||scope?.relationshipsSHA256!==x.relationshipsSHA256)throw Error('CORRECTED_SCOPE_DIGEST_MISMATCH');
 return a;
}
export async function appendAssessmentEvidenceAmendment({amendment,read,merge,journal,readContext,assertGraphOwnership}) {
 const a=validateEvidenceAmendment(amendment);
 if(a.schemaVersion===2)return appendMulti(a,{read,merge,journal,readContext,assertGraphOwnership});
 const initial=await read(a.itemId), f=initial?.fields;
 if(f?.Id!==a.itemId||f.AssessmentKey!==a.assessmentKey||f.DocumentUID!==a.documentUID)throw Error('NATIVE_IDENTITY_MISMATCH');
 if(f.AssessmentComplete!==true||!['Assessed with candidates','Assessed with no finding'].includes(f.AssessmentState)||f.CurrentAuthorityVerified!==false)throw Error('INVALID_AMENDMENT_PREIMAGE');
 // Guard before replay as well as before an append; multi amendments are not supported.
 if(typeof f.EvidenceManifest==='string'&&JSON.parse(f.EvidenceManifest)?.completedAssessment?.kind==='multi-retained-edition-review')throw Error('MULTI_AMENDMENT_NOT_SUPPORTED');
 if(typeof f.EvidenceManifest!=='string'||createHash('sha256').update(f.EvidenceManifest).digest('hex')!==a.expectedEvidenceManifestSHA256) {
  // An exact append replay is accepted only if the persisted amendment bytes match.
  if(typeof f.EvidenceManifest==='string') {
   const existing=JSON.parse(f.EvidenceManifest).assessmentReviewAddenda||[];
   const prior=existing.find(x=>x.amendmentKey===a.amendment.amendmentKey);
   if(prior&&canonical(prior)===canonical(a.amendment))return {updated:false,replay:true,itemId:a.itemId,amendmentKey:a.amendment.amendmentKey};
  }
  throw Error('EVIDENCE_AMENDMENT_PREIMAGE_MISMATCH');
 }
 const manifest=JSON.parse(f.EvidenceManifest), prior=manifest.completedAssessment;
 if(!prior||prior.completionKey!==a.amendment.priorCompletionKey||sha(prior)!==a.amendment.priorCompletionEvidenceSHA256||prior.source?.documentUID!==a.documentUID)throw Error('PRIOR_COMPLETION_EVIDENCE_MISMATCH');
 const addenda=Array.isArray(manifest.assessmentReviewAddenda)?manifest.assessmentReviewAddenda:[];
 if(addenda.some(x=>x.amendmentKey===a.amendment.amendmentKey))throw Error('AMENDMENT_PREIMAGE_HAS_DUPLICATE');
 const nextManifest={...manifest,assessmentReviewAddenda:[...addenda,a.amendment]};
 const patch={EvidenceManifest:JSON.stringify(nextManifest)};
 if(typeof initial.etag!=='string'||!initial.etag.trim()||initial.etag==='*')throw Error('EXACT_ETAG_REQUIRED');
 await journal({phase:'intent',itemId:a.itemId,amendmentKey:a.amendment.amendmentKey,expectedETag:initial.etag,expectedEvidenceManifestSHA256:a.expectedEvidenceManifestSHA256});
 await merge(a.itemId,patch,initial.etag);
 const observed=await read(a.itemId);
 if(observed?.fields?.Id!==a.itemId||observed.fields.AssessmentKey!==a.assessmentKey||observed.fields.DocumentUID!==a.documentUID||observed.fields.AssessmentState!==f.AssessmentState||observed.fields.AssessmentComplete!==true||observed.fields.CurrentAuthorityVerified!==false||observed.fields.EvidenceManifest!==patch.EvidenceManifest)throw Error('EVIDENCE_AMENDMENT_READBACK_MISMATCH');
 await journal({phase:'verified',itemId:a.itemId,amendmentKey:a.amendment.amendmentKey,observedETag:observed.etag});
 return {updated:true,replay:false,itemId:a.itemId,amendmentKey:a.amendment.amendmentKey};
}

/* Multi-edition amendment uses the same adapter and journals as the single-edition
   writer. readContext returns complete, compiler-normalized graph and catalogue;
   assertGraphOwnership asserts a caller-held exclusion through final readback. */
function validateMultiAmendment(a) {
 if(a?.kind!=='assessment_evidence_amendment'||!a.before||!a.amendment||!Number.isSafeInteger(a.maxManifestBytes)||a.maxManifestBytes<1)throw Error('INVALID_MULTI_AMENDMENT');
 const {amendmentKey,...body}=a.amendment;
 if(a.amendment.kind!=='multi-edition-revalidation'||sha(body)!==amendmentKey)throw Error('INVALID_MULTI_AMENDMENT_KEY');
 const t=validateTransition(a.amendment.transition), f=a.before;
 if(t.validation.allManifestEditionsIndependentlyValidated!==true||a.itemId!==t.itemId||a.documentUID!==t.documentUID||a.assessmentKey!==t.assessmentKey||f.Id!==a.itemId||f.DocumentUID!==a.documentUID||f.AssessmentKey!==a.assessmentKey||f.AssessmentComplete!==true||f.CurrentAuthorityVerified!==false||!['Assessed with candidates','Assessed with no finding'].includes(f.AssessmentState))throw Error('INVALID_MULTI_AMENDMENT_IDENTITY');
 if(typeof f.EvidenceManifest!=='string'||createHash('sha256').update(f.EvidenceManifest).digest('hex')!==a.expectedEvidenceManifestSHA256)throw Error('MULTI_EXPECTED_MANIFEST_MISMATCH');
 if(a.amendment.expectedEvidenceManifestSHA256!==a.expectedEvidenceManifestSHA256||a.amendment.expectedAssessmentState!==f.AssessmentState||a.amendment.expectedIncomingCount!==f.ExistingIncomingCount||a.amendment.expectedOutgoingCount!==f.ExistingOutgoingCount)throw Error('MULTI_UNBOUND_PREIMAGE');
 const m=JSON.parse(f.EvidenceManifest), old=m.completedAssessment;
 if(old?.kind!=='multi-retained-edition-review'||old.completionKey!==a.amendment.priorCompletionKey||sha(old)!==a.amendment.priorCompletionEvidenceSHA256)throw Error('MULTI_PRIOR_COMPLETION_MISMATCH');
 for(const name of ['assessmentReviewAddenda','relationshipInventoryReconciliations','assessmentHistoryArchives'])if(m[name]!==undefined&&!Array.isArray(m[name]))throw Error('INVALID_MULTI_HISTORY');
 if((m.assessmentReviewAddenda||[]).some(x=>x.amendmentKey===amendmentKey))throw Error('MULTI_DUPLICATE_PREIMAGE');
 const strip=x=>{x={...x};for(const k of ['completedAssessment','assessmentReviewAddenda','relationshipInventoryReconciliations','assessmentHistoryArchives','existingIncomingKeys','existingOutgoingKeys'])delete x[k];return x};
 if(canonical(strip(m))!==canonical(strip(JSON.parse(t.before.EvidenceManifest))))throw Error('MULTI_SOURCE_HISTORY_MISMATCH');
 for(const [k,v] of Object.entries(t.before))if(!['EvidenceManifest','AssessmentState','AssessmentComplete','ExistingOutgoingCount','ExistingIncomingCount'].includes(k)&&f[k]!==v)throw Error('MULTI_FIELDS_CHANGED');
 for(const k of ['incomingKeys','outgoingKeys'])if(!Array.isArray(a.amendment[k])||new Set(a.amendment[k]).size!==a.amendment[k].length||a.amendment[k].some(x=>typeof x!=='string'||!x))throw Error('INVALID_MULTI_GRAPH_KEYS');
 return a;
}
async function appendMulti(a,{read,merge,journal,readContext,assertGraphOwnership}) {
 if(typeof readContext!=='function'||typeof assertGraphOwnership!=='function')throw Error('MULTI_CONTEXT_AND_GRAPH_OWNERSHIP_REQUIRED');
 const t=a.amendment.transition, current=await read(a.itemId), f=a.before, m=JSON.parse(f.EvidenceManifest);
 const patch={EvidenceManifest:JSON.stringify({...m,existingIncomingKeys:a.amendment.incomingKeys,existingOutgoingKeys:a.amendment.outgoingKeys,assessmentReviewAddenda:[...(m.assessmentReviewAddenda||[]),a.amendment]}),AssessmentState:t.patch.AssessmentState,ExistingIncomingCount:t.patch.ExistingIncomingCount,ExistingOutgoingCount:t.patch.ExistingOutgoingCount};
 const after={...f,...patch};
 if(Buffer.byteLength(patch.EvidenceManifest,'utf8')>a.maxManifestBytes)throw Error('MANIFEST_SIZE_LIMIT_ARCHIVE_AND_RECOMPILE');
 if(!equal(current?.fields||{},f)&&!equal(current?.fields||{},after))throw Error('MULTI_AMENDMENT_PREIMAGE_MISMATCH');
 await assertGraphOwnership();
 async function checkContext(){
  const c=await readContext(), e=JSON.parse(t.patch.EvidenceManifest).completedAssessment;
  if(!c||!Array.isArray(c.relationships)||!Array.isArray(c.catalogue)||sha(c.relationships)!==e.relationshipsSHA256||sha(c.catalogue)!==e.editions[0].scope.catalogueSHA256)throw Error('MULTI_CONTEXT_CHANGED');
  const incoming=c.relationships.filter(r=>r.ToDocumentUID===a.documentUID).map(r=>r.RelationshipKey).sort(), outgoing=c.relationships.filter(r=>r.FromDocumentUID===a.documentUID).map(r=>r.RelationshipKey).sort();
  if(canonical(incoming)!==canonical(a.amendment.incomingKeys)||canonical(outgoing)!==canonical(a.amendment.outgoingKeys)||incoming.length!==patch.ExistingIncomingCount||outgoing.length!==patch.ExistingOutgoingCount)throw Error('MULTI_GRAPH_COUNTS_MISMATCH');
 }
 await checkContext();
 if(equal(current.fields,after))return {updated:false,replay:true,itemId:a.itemId,amendmentKey:a.amendment.amendmentKey};
 if(typeof current.etag!=='string'||!current.etag.trim()||current.etag==='*')throw Error('EXACT_ETAG_REQUIRED');
 await journal({phase:'intent',itemId:a.itemId,amendmentKey:a.amendment.amendmentKey,expectedETag:current.etag,expectedEvidenceManifestSHA256:a.expectedEvidenceManifestSHA256,patchSHA256:sha(patch)});
 await merge(a.itemId,patch,current.etag);
 const observed=await read(a.itemId);
 if(!equal(observed?.fields||{},after))throw Error('MULTI_AMENDMENT_READBACK_MISMATCH');
 await assertGraphOwnership();await checkContext();
 await journal({phase:'verified',itemId:a.itemId,amendmentKey:a.amendment.amendmentKey,observedETag:observed.etag});
 return {updated:true,replay:false,itemId:a.itemId,amendmentKey:a.amendment.amendmentKey};
}
