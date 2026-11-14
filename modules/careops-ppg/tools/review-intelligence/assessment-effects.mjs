/* Exact, short-lived qualification of a first-party list realtime subscription.
   No native mutation, subscription removal, mail allowance or credential handling. */
import {createHash} from 'node:crypto';
const canonical=x=>Array.isArray(x)?'['+x.map(canonical).join(',')+']':x&&typeof x==='object'?'{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}':JSON.stringify(x);
export const effectsDigest=x=>createHash('sha256').update(canonical(x)).digest('hex');
// Opt-in v2 excludes only volatile OData response identity annotations. Native
// subscription/receiver IDs, destinations, tokens, expiry and all other fields
// remain pinned. V1 receipts and existing writers retain their exact digest.
function stableODataIdentity(value, metadata=false){
 if(Array.isArray(value))return value.map(item=>stableODataIdentity(item));
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value)
  .filter(([key])=>!metadata||!['id','uri'].includes(key))
  .map(([key,item])=>[key,stableODataIdentity(item,key==='__metadata')]));
 return value;
}
export const effectsDigestV2=x=>effectsDigest(stableODataIdentity(x));
const marker='system-managed:8082D436-D8DA-458D-96AD-34C902B73F37';
const assembly='Microsoft.SharePoint.Core, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c';
const receiverClass='Microsoft.SharePoint.Webhooks.SPWebhookItemEventReceiver';
const guid='[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}';
export function socketRoute(binding,route){
 if(!new RegExp('^'+guid+'$','i').test(binding.list?.Id||''))throw Error('BOUND_LIST_REQUIRED');
 const u=new URL(route),site=new URL(binding.site);
 const pattern=new RegExp('^/_api/v2\\.0/sites/'+site.hostname.replaceAll('.','\\.')+','+guid+','+guid+'/lists/'+binding.list.Id+'/subscriptions/socketIo$','i');
 if(u.origin!==site.origin||u.username||u.password||u.search||u.hash||!pattern.test(u.pathname))throw Error('BOUND_LIST_SOCKET_ROUTE_REQUIRED');
 return u.href;
}
function destination(raw){
 const u=new URL(raw);
 if(u.protocol!=='https:'||u.username||u.password||u.hash||u.port||!/^[a-z0-9-]+\.pushnp\.svc\.ms$/i.test(u.hostname)||u.pathname!=='/notifications')throw Error('UNKNOWN_NOTIFICATION_DESTINATION');
 const token=u.searchParams.get('token');if(!token||token.length>512||/[\u0000-\u001f\u007f]/.test(token))throw Error('EXPECTED_NATIVE_SOCKET_TOKEN');
 return u;
}
export function validateAssessmentEffects({binding,effects,qualification=null,socket=null,alerts=[],now=Date.now()}){
 if(!effects||['subscriptions','receivers','rules'].some(k=>!Array.isArray(effects[k])))throw Error('COMPLETE_EFFECTS_COLLECTIONS_REQUIRED');
 if(!Array.isArray(alerts)||(alerts.length&&typeof binding?.list?.Id!=='string')
  ||alerts.some(a=>typeof a?.alertId!=='string'||!a.alertId||typeof a.listId!=='string'||!a.listId||a.listId.toLowerCase()===binding.list.Id.toLowerCase())
  ||new Set(alerts.map(a=>a.alertId)).size!==alerts.length)throw Error('ALERT_TARGET_UNQUALIFIED');
 if(!effects.subscriptions.length&&!effects.receivers.length&&!effects.rules.length)return {qualified:true,kind:'empty-effects',emailAllowed:false};
 if(!qualification)throw Error('RECONCILE_NATIVE_EFFECTS');
 const q=qualification,age=now-Date.parse(q.observedAt);
 if(q.schemaVersion!==1||q.kind!=='sharepoint-list-realtime-effects'||!Number.isFinite(age)||age<0||age>3600000)throw Error('FRESH_EFFECTS_QUALIFICATION_REQUIRED');
 if(q.site!==binding.site||q.listId!==binding.list.Id||q.listTitle!==binding.list.Title)throw Error('QUALIFICATION_TARGET_DIFFERS');
 socketRoute(binding,q.socketRoute);
 if(q.effectsDigestVersion!==undefined&&q.effectsDigestVersion!==1&&q.effectsDigestVersion!==2)throw Error('UNSUPPORTED_EFFECTS_DIGEST_VERSION');
 const digest=q.effectsDigestVersion===2?effectsDigestV2:effectsDigest;
 if(digest(effects)!==q.nativeEffectsSHA256||digest(alerts)!==q.alertTargetsSHA256)throw Error('EFFECTS_CHANGED_REQUALIFY');
 if(effects.rules.length||effects.subscriptions.length!==1||effects.receivers.length!==11)throw Error('UNKNOWN_EFFECTS_SURFACE');
 const sub=effects.subscriptions[0],url=destination(sub.notificationUrl);
 if(sub.resource!==binding.list.Id||sub.clientState!==marker||!(Date.parse(sub.expirationDateTime)>now))throw Error('UNQUALIFIED_SUBSCRIPTION');
 if([...url.searchParams.keys()].join(',')!=='token')throw Error('UNKNOWN_SUBSCRIPTION_PARAMETERS');
 const endpoint=destination(socket?.notificationUrl);
 if(socket.id!==sub.id||socket.clientState!==sub.clientState||socket.expirationDateTime!==sub.expirationDateTime||endpoint.origin!==url.origin||endpoint.pathname!==url.pathname||endpoint.searchParams.get('token')!==url.searchParams.get('token'))throw Error('LIVE_SOCKET_BINDING_DIFFERS');
 if([...endpoint.searchParams.keys()].sort().join(',')!=='applicationId,token'||endpoint.searchParams.get('applicationId')!==q.applicationId)throw Error('SOCKET_CLIENT_DIFFERS');
 const events=new Set(),ids=new Set();
 for(const r of effects.receivers){
  if(r.ReceiverAssembly!==assembly||r.ReceiverClass!==receiverClass||r.ReceiverName!==receiverClass||r.ReceiverUrl!==sub.notificationUrl||r.Synchronization!==2||r.SequenceNumber!==10000||!Number.isInteger(r.EventType)||r.EventType<10001||r.EventType>10011||!new RegExp('^'+guid+'$','i').test(r.ReceiverId||'')||ids.has(r.ReceiverId)||events.has(r.EventType))throw Error('UNKNOWN_OR_CHANGED_RECEIVER');
  events.add(r.EventType);ids.add(r.ReceiverId);
 }
 if(q.flowInspection?.relevantFileTriggers?.length!==0||!Number.isInteger(q.flowInspection?.activeFlowsInspected)||q.flowInspection.activeFlowsInspected<1||q.flowInspection?.nativeWrites!==0||q.flowInspection?.scope!=='Current accessible Default personal/team solution/non-solution flows; not tenant-wide or all-environment coverage'||!/^[a-f0-9]{64}$/.test(q.officialClientPackageSHA256||''))throw Error('CORROBORATING_EVIDENCE_REQUIRED');
 return {qualified:true,kind:'first-party-list-realtime',effectsSHA256:q.nativeEffectsSHA256,
  expiry:new Date(Date.parse(q.observedAt)+3600000).toISOString(),
  emailAllowed:false,subscriptionChanged:false,scope:'Exact current list, service binding and recorded accessible automation scope; no tenant-wide guarantee'};
}
