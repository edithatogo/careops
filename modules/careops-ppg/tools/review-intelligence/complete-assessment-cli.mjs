#!/usr/bin/env node
/* Apply a validated private transition using the existing qualified CLI client. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {completeAssessment,validateTransition,appendAssessmentEvidenceAmendment,validateEvidenceAmendment} from './complete-assessment.mjs';
import {validateAssessmentEffects,socketRoute,effectsDigest} from './assessment-effects.mjs';
const root=process.cwd();
if(process.argv.includes('--help')){
 console.log('node tools/review-intelligence/complete-assessment-cli.mjs --binding PRIVATE_BINDING.json --transition PRIVATE_TRANSITION.json|--amendment PRIVATE_AMENDMENT.json --receipts NEW_PRIVATE_DIRECTORY [--transport-module EXISTING_QUALIFIED_NATIVE.mjs] [--effects-qualification PRIVATE.json] [--mode check|save|amend] [--context-binding PRIVATE.json --coordination PRIVATE.json] [--recovery-receipts PRIOR_PRIVATE_DIRECTORY]');
 process.exit(0);
}
const options={};const allowed=new Set(['binding','transition','amendment','receipts','transport-module','effects-qualification','mode','context-binding','coordination','recovery-receipts']);
for(let i=2;i<process.argv.length;i+=2){const key=process.argv[i]?.replace(/^--/,'');if(!allowed.has(key)||!process.argv[i+1]||options[key])throw Error('INVALID_ARGUMENTS');options[key]=process.argv[i+1];}
const mode=options.mode||'save';
if(!['save','check','amend'].includes(mode))throw Error('INVALID_MODE');
for(const key of ['binding','receipts',...(mode==='save'?['transition']:[]),...(mode==='amend'?['amendment']:[])])if(!options[key])throw Error('REQUIRED_'+key.toUpperCase());
function privatePath(value){const p=path.resolve(value);if(!p.startsWith(path.join(root,'.local')+path.sep))throw Error('PRIVATE_REPOSITORY_PATH_REQUIRED');return p;}
const binding=JSON.parse(fs.readFileSync(privatePath(options.binding))),transition=options.transition?validateTransition(JSON.parse(fs.readFileSync(privatePath(options.transition)))):null,amendment=options.amendment?validateEvidenceAmendment(JSON.parse(fs.readFileSync(privatePath(options.amendment)))):null;
const multiAmend=mode==='amend'&&amendment?.schemaVersion===2;
const multiCompletion=mode==='save'&&transition?.validation?.allManifestEditionsIndependentlyValidated===true;
const multi=multiAmend||multiCompletion;
if(multi&&(!options['context-binding']||!options.coordination))throw Error('MULTI_CONTEXT_AND_COORDINATION_REQUIRED');
const contextBinding=multi?JSON.parse(fs.readFileSync(privatePath(options['context-binding']))):null;
const coordinationPath=multi?privatePath(options.coordination):null;
const siteURL=new URL(binding.site);
if(siteURL.protocol!=='https:'||siteURL.username||siteURL.password||siteURL.search||siteURL.hash||!/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/i.test(binding.list?.Id||''))throw Error('EXACT_NATIVE_BINDING_REQUIRED');
if(multi){
 const id=/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/i;
 if(contextBinding.site!==binding.site||!id.test(contextBinding.relationshipList?.Id||'')||!id.test(contextBinding.catalogueList?.Id||'')||!contextBinding.relationshipList?.Title||!contextBinding.catalogueList?.Title||contextBinding.relationshipList.Id===contextBinding.catalogueList.Id||contextBinding.relationshipList.Id===binding.list.Id||contextBinding.catalogueList.Id===binding.list.Id)throw Error('EXACT_CONTEXT_BINDING_REQUIRED');
}
// This is an explicit caller coordination assertion, not a distributed lock.
function checkCoordination(){
 if(!multi)return;
 const c=JSON.parse(fs.readFileSync(coordinationPath));
 if(c.kind!=='ppg-graph-coordination-v1'||c.site!==binding.site||c.relationshipListId!==contextBinding.relationshipList.Id||c.catalogueListId!==contextBinding.catalogueList.Id||c.assessmentListId!==binding.list.Id||c.itemId!==(multiAmend?amendment.itemId:transition.itemId)||(multiAmend?c.amendmentKey!==amendment.amendment.amendmentKey:c.completionKey!==transition.completionKey)||typeof c.owner!=='string'||!c.owner.trim()||c.singleWriterConfirmed!==true||!Number.isFinite(Date.parse(c.expiresAtUtc))||Date.parse(c.expiresAtUtc)<=Date.now())throw Error('MULTI_COORDINATION_REQUIRED');
}
checkCoordination();
const receipts=privatePath(options.receipts);fs.mkdirSync(receipts,{mode:0o700});
const transport=privatePath(options['transport-module']||'.local/onedrive-workbench-import-20261023/native.mjs');
const {connect}=await import(pathToFileURL(transport));const {call}=await connect();
const base=binding.site+"/_api/web/lists(guid'"+binding.list.Id+"')";
const decode=r=>typeof r.data==='string'&&r.data?JSON.parse(r.data):r.data;
const meta=decode(await call('GET',base+'?$select=Id,Title,EnableVersioning'));
if(meta.Id!==binding.list.Id||meta.Title!==binding.list.Title||!meta.Title.startsWith('PPG Relationship Assessments')||meta.EnableVersioning!==true)throw Error('NATIVE_ASSESSMENT_LIST_REQUIRED');
const save=(name,data)=>fs.writeFileSync(path.join(receipts,name+'.json'),JSON.stringify(data,null,2),{flag:'wx',mode:0o600});
const qualification=options['effects-qualification']?JSON.parse(fs.readFileSync(privatePath(options['effects-qualification']))):null;
async function all(url){let rows=[],seen=new Set();while(url){if(seen.has(url)||seen.size>100||new URL(url).origin!==siteURL.origin)throw Error('EFFECTS_PAGE_BOUNDARY');seen.add(url);const x=decode(await call('GET',url));if(!Array.isArray(x.value))throw Error('EFFECTS_COLLECTION_REQUIRED');rows.push(...x.value);url=x['odata.nextLink']||x['@odata.nextLink'];}return rows;}
let checks=0;
async function checkEffects(){
 const effects={subscriptions:await all(base+'/subscriptions'),receivers:await all(base+'/EventReceivers'),rules:decode(await call('POST',base+'/GetAllRules()',{data:{includeQuicksteps:true,includeAutomaticRules:true},headers:{'Content-Type':'application/json;odata=nometadata'}})).value};
 let socket=null,alerts=[];
 if(qualification){
  if(qualification.site!==binding.site||qualification.listId!==binding.list.Id)throw Error('QUALIFICATION_TARGET_DIFFERS');
  socket=decode(await call('GET',socketRoute(binding,qualification.socketRoute)));
  if(effectsDigest(await all(base+'/subscriptions'))!==effectsDigest(effects.subscriptions))throw Error('SOCKET_REGISTRATION_CHANGED_REQUALIFY');
  for(const a of await all(binding.site+'/_api/web/Alerts')){
   if(!/^[a-f0-9-]{36}$/i.test(a.ID||a.Id||''))throw Error('ALERT_ID_REQUIRED');
   const id=a.ID||a.Id,list=decode(await call('GET',binding.site+"/_api/web/Alerts(guid'"+id+"')/List?$select=Id,Title"));alerts.push({alertId:id,listId:list.Id});
  }
  alerts.sort((a,b)=>a.alertId.localeCompare(b.alertId));
 }
 const result=validateAssessmentEffects({binding,effects,qualification,socket,alerts});
 save('effects-'+(++checks),{observedAt:new Date().toISOString(),result});return result;
}
const cmp=(a,b)=>{const x=Array.from(a,c=>c.codePointAt(0)),y=Array.from(b,c=>c.codePointAt(0));for(let i=0;i<Math.min(x.length,y.length);i++)if(x[i]!==y[i])return x[i]-y[i];return x.length-y.length};
const fields=['RelationshipKey','FromDocumentUID','ToDocumentUID','FromVersion','ToVersion','RelationshipType','ReviewState','Rationale','EvidenceRef'],catFields=['DocumentUID','sourceDocumentId','sourceTitle'];
function normalize(rows,keys,id){const seen=new Set();return rows.map(x=>{if(!x||keys.some(k=>!Object.hasOwn(x,k)||x[k]===undefined)||typeof x[id]!=='string'||!x[id]||seen.has(x[id]))throw Error('INVALID_CONTEXT_COLLECTION');seen.add(x[id]);return Object.fromEntries(keys.map(k=>[k,x[k]]))}).sort((a,b)=>cmp(a[id],b[id]));}
let relBase,catBase;
if(multi){
 relBase=binding.site+"/_api/web/lists(guid'"+contextBinding.relationshipList.Id+"')";
 catBase=binding.site+"/_api/web/lists(guid'"+contextBinding.catalogueList.Id+"')";
 for(const [url,expected] of [[relBase,contextBinding.relationshipList],[catBase,contextBinding.catalogueList]]){const got=decode(await call('GET',url+'?$select=Id,Title'));if(got.Id!==expected.Id||got.Title!==expected.Title)throw Error('CONTEXT_NATIVE_BINDING_MISMATCH');}
}
const readContext=async()=>({relationships:normalize(await all(relBase+'/items?$top=500'),fields,'RelationshipKey'),catalogue:normalize(await all(catBase+'/items?$select=DocumentUID,sourceDocumentId,sourceTitle&$top=500'),catFields,'DocumentUID')});
const assertGraphOwnership=async()=>{checkCoordination()};
async function checkCompletionContext(){
 if(!multiCompletion)return;
 checkCoordination();const current=await readContext(), e=JSON.parse(transition.patch.EvidenceManifest).completedAssessment;
 if(effectsDigest(current.relationships)!==e.relationshipsSHA256||e.editions.some(x=>effectsDigest(current.catalogue)!==x.scope.catalogueSHA256))throw Error('MULTI_COMPLETION_CONTEXT_CHANGED');
 if(current.relationships.filter(r=>r.ToDocumentUID===transition.documentUID).length!==transition.patch.ExistingIncomingCount||current.relationships.filter(r=>r.FromDocumentUID===transition.documentUID).length!==transition.patch.ExistingOutgoingCount)throw Error('MULTI_COMPLETION_GRAPH_COUNTS_MISMATCH');
 checkCoordination();
}
async function checkAmendmentContext(){
 if(!multiAmend)return;
 checkCoordination();const current=await readContext(), t=amendment.amendment.transition, e=JSON.parse(t.patch.EvidenceManifest).completedAssessment;
 if(effectsDigest(current.relationships)!==e.relationshipsSHA256||e.editions.some(x=>effectsDigest(current.catalogue)!==x.scope.catalogueSHA256))throw Error('MULTI_CONTEXT_CHANGED');
 const incoming=current.relationships.filter(r=>r.ToDocumentUID===t.documentUID).map(r=>r.RelationshipKey).sort(),outgoing=current.relationships.filter(r=>r.FromDocumentUID===t.documentUID).map(r=>r.RelationshipKey).sort();
 if(effectsDigest(incoming)!==effectsDigest(amendment.amendment.incomingKeys)||effectsDigest(outgoing)!==effectsDigest(amendment.amendment.outgoingKeys)||incoming.length!==t.patch.ExistingIncomingCount||outgoing.length!==t.patch.ExistingOutgoingCount)throw Error('MULTI_GRAPH_COUNTS_MISMATCH');
 checkCoordination();
}
const qualifiedEffects=await checkEffects();
if(mode==='check'){const result={mode:'check',effects:qualifiedEffects,mutationSends:0,itemWrites:0};save('result',result);console.log(JSON.stringify(result));process.exit(0);}
if(mode==='amend'&&transition||mode==='save'&&amendment)throw Error('MUTUALLY_EXCLUSIVE_TRANSITION_OR_AMENDMENT');
let reads=0,sends=0,firstRead=null;
const owned=new Set(['__metadata','Modified','EditorId','OData__UIVersionString',...(mode==='amend'&&multiAmend?['EvidenceManifest','AssessmentState','ExistingIncomingCount','ExistingOutgoingCount']:mode==='amend'?['EvidenceManifest']:Object.keys(transition?.patch||{}))]);
const targetId=mode==='amend'?amendment.itemId:transition?.itemId;
let recoveryBefore=null;
if(options['recovery-receipts']){
 if(!(multiAmend||mode==='save'))throw Error('RECOVERY_RECEIPT_UNSUPPORTED');
 const dir=privatePath(options['recovery-receipts']);
 recoveryBefore=JSON.parse(fs.readFileSync(path.join(dir,'read-1.json')));
 const records=fs.readFileSync(path.join(dir,'journal.jsonl'),'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
 const expected=multiAmend?amendment.before:transition.before, key=multiAmend?amendment.amendment.amendmentKey:transition.completionKey;
 const intents=records.filter(x=>x.phase==='intent'&&x.itemId===targetId&&(multiAmend?x.amendmentKey===key:x.completionKey===key));
 if(intents.length!==1||!recoveryBefore||recoveryBefore.Id!==targetId||typeof recoveryBefore.__metadata?.etag!=='string'||recoveryBefore.__metadata.etag!==intents[0].expectedETag||Object.entries(expected).some(([k,v])=>recoveryBefore[k]!==v))throw Error('RECOVERY_RECEIPT_MISMATCH');
}
function checkPreserved(before,after){
 for(const k of new Set([...Object.keys(before),...Object.keys(after)]))if(!owned.has(k)&&(!Object.hasOwn(before,k)||!Object.hasOwn(after,k)||effectsDigest(before[k])!==effectsDigest(after[k])))throw Error('UNOWNED_FIELD_CHANGED_'+k);
}
const read=async id=>{if(id!==targetId)throw Error('BOUND_ITEM_REQUIRED');const x=decode(await call('GET',base+'/items('+id+')',{headers:{Accept:'application/json;odata=verbose'}})).d;save('read-'+(++reads),x);
 if(firstRead===null){firstRead=structuredClone(x);if(recoveryBefore)checkPreserved(recoveryBefore,x);}
 else if(sends>0)checkPreserved(firstRead,x);
 return {fields:x,etag:x.__metadata?.etag};};
const merge=async(id,patch,etag)=>{if(recoveryBefore)throw Error('RECOVERY_READ_ONLY_NO_RESEND');if(id!==targetId||etag==='*'||!etag||sends!==0)throw Error('ONE_BOUND_CONDITIONAL_MUTATION_REQUIRED');await checkEffects();checkCoordination();await checkCompletionContext();await checkAmendmentContext();++sends;await call('POST',base+'/items('+id+')',{data:patch,headers:{'Content-Type':'application/json;odata=nometadata','X-HTTP-Method':'MERGE','IF-MATCH':etag}});};
let pendingVerified=null;
const appendJournal=entry=>fs.appendFileSync(path.join(receipts,'journal.jsonl'),JSON.stringify({...entry,at:new Date().toISOString()})+'\n',{mode:0o600});
const journal=async entry=>{if(multiCompletion&&entry.phase==='verified'){pendingVerified=entry;return;}appendJournal(entry);};
try{await checkCompletionContext();const result=mode==='amend'?await appendAssessmentEvidenceAmendment({amendment,read,merge,journal,...(multiAmend?{readContext,assertGraphOwnership}: {})}):await completeAssessment({transition,read,merge,journal});await checkCompletionContext();if(pendingVerified)appendJournal(pendingVerified);const unownedFieldsPreserved=result.replay?Boolean(recoveryBefore):result.updated===true;save('result',{...result,unownedFieldsPreserved,mutationSends:sends,reads});console.log(JSON.stringify({...result,unownedFieldsPreserved,mutationSends:sends}));}
catch(error){save('failure',{code:error.isAxiosError?'NATIVE_OPERATION_FAILED':error.message,status:error.response?.status??null,mutationSends:sends,requiresReadBeforeResume:sends>0});throw Error('Assessment transition stopped; inspect private receipts before resuming.');}
