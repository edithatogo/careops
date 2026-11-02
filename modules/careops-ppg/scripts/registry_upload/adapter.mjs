// Apache-2.0. Reuse the enrolled Microsoft 365 CLI client and its own token cache.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { validateRenewalIdentity } from '../../tools/lifecycle/validate_renewal_identity.mjs';

export async function connect(settings, binding, receiptDirectory) {
  const sdk = file => import(pathToFileURL(path.join(binding.sdkDirectory, file)));
  const [{default: auth}, {default: transport}] = await Promise.all([sdk('Auth.js'), sdk('request.js')]);
  const log = {log: async () => {}, logToStderr: async () => {}};
  transport.logger = log;
  transport.debug = false;
  await auth.restoreAuth();
  const identity = binding.identity;
  if (auth.connection.name !== binding.connectionName || auth.connection.appId !== identity.appId ||
      auth.connection.tenant !== identity.tenantId || settings.environment !== 'Default-' + identity.tenantId ||
      binding.siteUrl?.replace(/\/$/, '') !== settings.site) throw Error('Saved client or destination mismatch');
  const app = await auth.getPublicClient(log, false);
  const accounts = (await app.getTokenCache().getAllAccounts()).filter(a =>
    a.localAccountId?.toLowerCase() === identity.objectId.toLowerCase() &&
    a.tenantId?.toLowerCase() === identity.tenantId.toLowerCase() &&
    a.username?.toLowerCase() === identity.username.toLowerCase());
  if (accounts.length !== 1) throw Error('Expected one enrolled operator account');
  const flowRoot = 'https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/environments/' + settings.environment;
  const siteOrigin = new URL(settings.site).origin;
  const tokenCache = new Map();
  async function token(resource) {
    let entry = tokenCache.get(resource);
    if (!entry || new Date(entry.expiresOn).getTime() < Date.now() + 60000) {
      entry = await app.acquireTokenSilent({account: accounts[0], scopes: [resource + '/.default']});
      validateRenewalIdentity(entry, identity);
      if (!entry.accessToken || new Date(entry.expiresOn).getTime() < Date.now() + 60000) throw Error('Renew the enrolled client');
      tokenCache.set(resource, entry);
    }
    return entry.accessToken;
  }
  const writes = [];
  const journal = path.join(receiptDirectory, 'pending.json');
  async function exchange(method, rawUrl, opts = {}, mutation = false) {
    const url = new URL(rawUrl);
    const sp = url.origin === siteOrigin && url.pathname.startsWith(new URL(settings.site).pathname + '/_api/');
    if (!sp && !url.href.startsWith(flowRoot + '/flows')) throw Error('Request outside deployment scope');
    const bearer = await token(sp ? siteOrigin : 'https://management.azure.com');
    const intent = {method, url: url.href, sha256: createHash('sha256').update(JSON.stringify(opts.data ?? null)).digest('hex')};
    if (mutation) fs.writeFileSync(journal, JSON.stringify(intent), {flag:'wx', mode:0o600});
    let response;
    try {
      response = await transport.req.request({method, url: url.href, family:4, timeout:60000,
        maxRedirects:0, signal:AbortSignal.timeout(60000), data:opts.data, responseType:opts.responseType || 'json',
        headers:{Accept:sp?'application/json;odata=nometadata':'application/json',
          'Content-Type':sp?'application/json;odata=nometadata':'application/json',...opts.headers, Authorization:'Bearer '+bearer}});
    } catch (cause) {
      // Do not print Axios objects, which may contain credentials. Preserve status for a scoped missing-resource test.
      const status = cause.response?.status;
      const message = cause.response?.data?.error?.message;
      const error = new Error(method+' '+url.pathname+' failed ('+(status ?? cause.code ?? 'transport')+')'+
        (typeof message === 'string' ? ': '+message.slice(0,250) : ''));
      error.status = status;
      error.response = {status};
      throw error;
    }
    if (mutation) {
      writes.push(intent);
      fs.appendFileSync(path.join(receiptDirectory,'history.jsonl'),JSON.stringify({...intent,at:new Date().toISOString()})+'\n',{mode:0o600});
      fs.unlinkSync(journal);
    }
    if (method === 'GET' && sp && response.headers?.etag && response.data && typeof response.data === 'object' && !ArrayBuffer.isView(response.data)) {
      Object.defineProperty(response.data, 'registryResponseETag', {value:response.headers.etag});
    }
    return response.data;
  }
  const read = async url => {
    const result = await exchange('GET',url);
    return typeof result === 'string' ? JSON.parse(result) : result;
  };
  return {read, writes, write:(_label,url,data,headers)=>exchange('POST',url,{data,headers},true),
    request:(method,url,opts)=> {
      if (method !== 'GET' && !(method === 'POST' && new URL(url).pathname.endsWith('/RenderListDataAsStream'))) throw Error('Read-only request expected');
      return exchange(method,url,opts);
    },
    flow:{get:route=>exchange('GET',flowRoot+route),send:(method,route,data)=>exchange(method,flowRoot+route,{data},true)}};
}
