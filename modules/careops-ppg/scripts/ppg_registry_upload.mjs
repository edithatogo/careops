#!/usr/bin/env node
// Apache-2.0. Deploy and read back the Registry upload extension on an existing workbench.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { connect } from './registry_upload/adapter.mjs';
import { buildFlow, ensureFlow } from './registry_upload/flow.mjs';
import { applySharePoint } from './registry_upload/sharepoint.mjs';
import { ensureListAccess } from './registry_upload/access.mjs';

const usage = 'node scripts/ppg_registry_upload.mjs <private-settings.json> [--verify-only]';
async function main() {
  const [file, option, ...extra] = process.argv.slice(2);
  if (file === '--help') return console.log(usage);
  if (!file || extra.length || (option && option !== '--verify-only')) throw Error(usage);
  const verifyOnly = option === '--verify-only';
  const fromSettings = p => path.resolve(path.dirname(path.resolve(file)), p);
  const load = file => JSON.parse(fs.readFileSync(file));
  const settings = load(file);
  const output = fromSettings(settings.receiptDirectory);
  fs.mkdirSync(output, {recursive:true, mode:0o700});
  const lock = path.join(output,'deploy.lock');
  const fd = fs.openSync(lock,'wx',0o600);
  try {
    fs.writeFileSync(fd, JSON.stringify({pid:process.pid,started:new Date().toISOString()}));
    if (fs.existsSync(path.join(output,'pending.json')) && !verifyOnly)
      throw Error('Pending write: reconcile against native state before another deployment');
    const binding = load(fromSettings(settings.binding));
    const adapter = await connect(settings,binding,output);
    const api = settings.site + '/_api/web';
    const current = await adapter.read(api+'/currentuser?$select=Email');
    assert.equal(current.Email?.toLowerCase(),binding.identity.username.toLowerCase(),'Unexpected site operator');
    const list = id => {
      if (!/^[\da-f]{8}(-[\da-f]{4}){3}-[\da-f]{12}$/i.test(id)) throw Error('Invalid destination list ID');
      return api + "/lists(guid'" + id + "')";
    };
    const surfaces = [
      ['catalogueId',0,['DocumentUID','sourceTitle','sourceDocumentId']],
      ['queueId',0,['CaseUID','linkedDocumentUIDs','caseStatus','evidenceDraftLink','sourceBaselineRef','nextAction']],
      ['libraryId',1,['PPGDocumentUID','PPGOriginalFilename','PPGPolicyEdition','PPGCurrency','PPGCaptureKind','PPGCaptureEditionEvidence','PPGCaptureSHA256']]
    ];
    for (const [key,type,fields] of surfaces) {
      const target=list(settings[key]);
      const [meta, schema]=await Promise.all([adapter.read(target+'?$select=Id,BaseType,EnableVersioning,EnableAttachments,RootFolder/ServerRelativeUrl&$expand=RootFolder'),
        adapter.read(target+'/fields?$select=InternalName&$top=5000')]);
      assert.equal(meta.Id.toLowerCase(),settings[key].toLowerCase());
      assert.equal(meta.BaseType,type);
      for (const field of fields) assert(schema.value.some(x=>x.InternalName===field),'Missing '+key+' field '+field);
      if (key==='queueId') {
        assert(meta.EnableAttachments,'Review Queue requires attachments');
        settings.queueRoot=meta.RootFolder.ServerRelativeUrl;
      }
      if (key==='libraryId') {
        assert(meta.EnableVersioning,'Evidence library requires versioning');
        settings.libraryRoot=meta.RootFolder.ServerRelativeUrl;
      }
    }
    buildFlow(settings); // validate every workflow binding before the first write
    const snapshot = settings.preservationRecordId ? (await import('./registry_upload/preservation.mjs')) : undefined;
    const capture = () => snapshot.capturePreservation({adapter,settings,recordId:settings.preservationRecordId});
    const before = snapshot ? await capture() : null;
    const sp = phase => applySharePoint({settings,read:adapter.read,write:adapter.write,phase,verifyOnly});
    const prerequisites = await sp('prerequisites');
    const flow = await ensureFlow(adapter,settings,{verifyOnly});
    settings.flowId=flow.flowId;
    const access=await ensureListAccess(adapter,settings,flow.flowId,verifyOnly);
    const registry=await sp('registry');
    const preservation = snapshot ? snapshot.comparePreservation(before, await capture()) : null;
    const receipt={site:settings.site,environment:settings.environment,flowId:flow.flowId,verifiedAt:new Date().toISOString(),
      mode:verifyOnly?'verify':'deploy',prerequisites,flow,access,registry,writes:adapter.writes.length,
      preservationRecordId:settings.preservationRecordId??null,preservation,
      nonOwnerProductionSubmission:'requires actual staff submission'};
    const receiptFile=path.join(output,'verification-'+randomUUID()+'.json');
    fs.writeFileSync(receiptFile,JSON.stringify(receipt,null,2),{flag:'wx',mode:0o600});
    console.log(JSON.stringify({verified:true, writes:receipt.writes, access, receiptFile}));
  } finally {fs.closeSync(fd);fs.unlinkSync(lock);}
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
