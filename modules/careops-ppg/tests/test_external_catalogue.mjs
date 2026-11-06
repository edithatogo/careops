import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {persist,checkRows} from '../tools/external-catalogue/records.mjs';
import {provisionViews,configureLinks,readOnlyRequest} from '../tools/external-catalogue/native.mjs';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,existsSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';

test('saved-session transport refuses mutations before calling the SDK',async()=>{
 let calls=0;const request={request:async options=>{calls++;return options;}};
 const options={method:'GET',url:'https://example.sharepoint.com/sites/test/_api/web/lists'};
 assert.equal(await readOnlyRequest(request,options),options);
 for(const method of ['POST','PATCH','PUT','DELETE','MERGE',undefined,'get'])
  await assert.rejects(readOnlyRequest(request,{...options,method}),/NATIVE_WRITE_QUALIFICATION_REQUIRED/);
 assert.equal(calls,1);
});

test('CLI mutation modes refuse before configuration, authentication or journals',()=>{
 const folder=mkdtempSync(join(tmpdir(),'catalogue-hold-'));
 try {
  for(const mode of ['bootstrap','persist','views','configure']) {
   const output=join(folder,mode+'.json'),journal=join(folder,mode+'.jsonl');
   const result=spawnSync(process.execPath,[fileURLToPath(new URL('../tools/external-catalogue/native.mjs',import.meta.url)),mode,join(folder,'missing-config'),join(folder,'missing-input'),output,journal],{encoding:'utf8',timeout:10000});
   assert.equal(result.error,undefined);
   assert.equal(result.status,1);
   assert.equal(result.stderr.trim(),'NATIVE_WRITE_QUALIFICATION_REQUIRED');
   assert.equal(existsSync(output),false);
   assert.equal(existsSync(journal),false);
  }
 } finally {rmSync(folder,{recursive:true,force:true});}
});
const row={Title:'Fictional',RecordKey:'pub:fixture',RecordKind:'Publication',PublicationKey:'pub:fixture',EditionKey:null,
 Issuer:'Fictional',SourceStatus:'Unknown',SourceRole:'Supporting',TrancheKey:'fictional',
 RecordJSON:JSON.stringify({key:'pub:fixture',kind:'Publication'}),PayloadSHA256:'',ReviewState:'Proposed',OfficialURL:'https://www.safetyandquality.gov.au/fixture',EvidenceURL:null,RelatedRecordsURL:null};
row.PayloadSHA256=createHash('sha256').update(row.RecordJSON).digest('hex');
test('create/readback and unchanged replay',async()=>{
 const stored=[],events=[];const options={rows:[row],read:async()=>structuredClone(stored),create:async x=>stored.push({...x,Id:1}),journal:async e=>events.push(e)};
 assert.equal((await persist(options)).created,1);assert.equal((await persist(options)).created,0);
 assert.equal(events.filter(e=>e.phase==='intent').length,1);
 assert.equal(events.filter(e=>e.phase==='verified').length,1);
});
test('human state conflict refuses every create',async()=>{
 let writes=0;await assert.rejects(persist({rows:[row],read:async()=>[{...row,ReviewState:'Accepted'}],create:async()=>writes++,journal:async()=>{}}),/PRESERVE_CHANGED/);assert.equal(writes,0);
});
test('uncertain creation is reconciled on next invocation without retry',async()=>{
 let stored=[],calls=0;const o={rows:[row],read:async()=>stored,create:async x=>{calls++;stored=[{...x,Id:1}];throw Error('response lost');},journal:async()=>{}};
 await assert.rejects(persist(o),/response lost/);assert.equal((await persist(o)).created,0);assert.equal(calls,1);
});
test('view creation uses modern string array and exact native query spelling',async()=>{
 const stored=[];let savedFields;const client={all:async()=>stored,call:async(method,route,data)=>{
  if(method==='GET')return {Items:savedFields};
  assert.equal(method,'POST');assert.ok(Array.isArray(data.parameters.ViewFields));
  assert.match(data.parameters.Query, /Name="RecordKind" \/>/);
  savedFields=data.parameters.ViewFields;
  stored.push({Title:data.parameters.Title,ViewQuery:data.parameters.Query,Id:String(stored.length+1),RowLimit:100,Paged:true,DefaultView:false,PersonalView:false});
 }};
 assert.equal((await provisionViews(client,'fictional',async()=>{})).length,5);
 assert.equal((await provisionViews(client,'fictional',async()=>{})).length,5);
 assert.equal(stored.length,5);
});
test('view conflict is preserved without a corrective mutation',async()=>{
 let calls=0;await assert.rejects(provisionViews({all:async()=>[{Title:'Publication catalogue',ViewQuery:'human query'}],call:async()=>calls++},'fictional',async()=>{}),/PRESERVE_CHANGED_VIEW/);assert.equal(calls,0);
});
test('link configuration supports absent direct capture and unchanged replay',async()=>{
 const formats=new Map(),columns=['LinkTitle'];let writes=0;
 const client={all:async()=>[{Id:'fixture',Title:'All Items'}],call:async(method,route,data)=>{
  const field=route.match(/getbyinternalnameortitle\('([^']+)'\)/)?.[1];
  if(field){if(method==='GET')return {CustomFormatter:formats.get(field)||''};formats.set(field,data.CustomFormatter);writes++;return {};}
  if(method==='GET')return {Items:[...columns]};
  columns.push(route.match(/AddViewField\('([^']+)'\)/)[1]);writes++;return {};
 }};
 assert.equal((await configureLinks(client,'fixture',async()=>{})).defaultFieldsVerified,11);
 assert.match(formats.get('EvidenceURL'),/Related evidence/);const count=writes;
 await configureLinks(client,'fixture',async()=>{});assert.equal(writes,count);
});
test('a human column formatter is never repaired implicitly',async()=>{
 let writes=0;await assert.rejects(configureLinks({call:async method=>{if(method==='GET')return {CustomFormatter:'human formatter'};writes++;},all:async()=>[]},'fixture',async()=>{}),/PRESERVE_CHANGED_COLUMN_FORMATTER/);assert.equal(writes,0);
});
test('native links cannot redirect to another site or executable scheme',async()=>{
 let creates=0;const o={site:'https://example.sharepoint.com/sites/fixture',read:async()=>[],create:async()=>creates++,journal:async()=>{}};
 await assert.rejects(persist({...o,rows:[{...row,EvidenceURL:'javascript:alert(1)'}]}),/STABLE_NATIVE_LINK/);
 await assert.rejects(persist({...o,rows:[{...row,EvidenceURL:'https://example.sharepoint.com/sites/other/file.pdf'}]}),/BOUND_NATIVE_LINK/);
 await assert.rejects(persist({...o,rows:[{...row,OfficialURL:'https://example.org/pretend-official'}]}),/OFFICIAL_SOURCE_URL/);
 assert.equal(creates,0);
});

test('METEOR catalogue origin is exact',()=>{checkRows([{...row,OfficialURL:'https://meteor.aihw.gov.au/content/123'}]);for(const url of ['https://meteor.aihw.gov.au.evil.test/content/123','https://user@meteor.aihw.gov.au/content/123'])assert.throws(()=>checkRows([{...row,OfficialURL:url}]));});

test('selected exact metadata origin reaches persistence and unchanged replay',async()=>{
 const selected={...row,OfficialURL:'https://updates.publisher.example/doc.pdf?record=A%2F1'};
 assert.throws(()=>checkRows([selected]),/OFFICIAL_SOURCE/);
 const stored=[],options={rows:[selected],officialHosts:['updates.publisher.example'],read:async()=>stored,
  create:async value=>stored.push({...value,Id:1}),journal:async()=>{}};
 assert.equal((await persist(options)).created,1);
 assert.equal((await persist(options)).created,0);
 for(const url of ['https://updates.publisher.example.evil.test/doc.pdf',
  'https://other.publisher.example/doc.pdf','https://user@updates.publisher.example/doc.pdf',
  'https://updates.publisher.example:444/doc.pdf','https://updates.publisher.example:0/doc.pdf','https://updates.publisher.example/doc.pdf#x',
  'https://updates.publisher.example/\\doc.pdf','https://updates.publisher.example/\tfile.pdf']){
  assert.throws(()=>checkRows([{...selected,OfficialURL:url}],undefined,['updates.publisher.example']));
 }
 assert.throws(()=>checkRows([selected],undefined,'updates.publisher.example'),/COLLECTION_REQUIRED/);
});

test('an explicitly written default HTTPS port preserves the original source URL',()=>{
 checkRows([{...row,OfficialURL:'https://updates.publisher.example:443/doc.pdf'}],undefined,['updates.publisher.example']);
});
