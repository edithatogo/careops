#!/usr/bin/env node
// Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
// Read-only adapter around the installed M365 CLI SDK; no token export or login.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';

const same = (a, b) => typeof a === 'string' && typeof b === 'string' && a.toLowerCase() === b.toLowerCase();
const requireThat = (condition, message) => { if (!condition) throw new Error(message); };

export function selectRead(pin, name) {
  for (const key of ['sdkRoot', 'sdkVersion', 'connectionName', 'appId', 'tenantId', 'username', 'objectId'])
    requireThat(typeof pin[key] === 'string' && pin[key], `Missing pin: ${key}`);
  requireThat(Array.isArray(pin.resources) && pin.resources.length, 'Missing resource pins');
  requireThat(name && Object.hasOwn(pin.reads ?? {}, name), 'Unknown named read');
  const read = pin.reads[name];
  requireThat(read.method === 'GET', 'Only GET permitted');
  const url = new URL(read.url);
  requireThat(url.protocol === 'https:' && !url.username && !url.password && !url.hash, 'Unsafe URL');
  requireThat(pin.resources.includes(read.resource) && url.origin === read.resource, 'Resource mismatch');
  requireThat(/^https:\/\/graph\.microsoft\.com$|^https:\/\/api\.flow\.microsoft\.com$|^https:\/\/[a-z0-9-]+\.sharepoint\.com$/.test(url.origin), 'Unsupported resource');
  requireThat(!/\/runs\/|\/triggers\/|\/invoke|\/callback|\/sendmail|\$batch|\/scopes\/admin\//i.test(url.pathname), 'Execution/admin endpoint forbidden');
  return read;
}

export function assertConnection(auth, pin) {
  const c = auth.connection;
  requireThat(c?.name === pin.connectionName && c.active && c.authType === 'browser' &&
    same(c.appId, pin.appId) && same(c.tenant, pin.tenantId), 'Connection drift; stop without login');
}

export function installAuthGuard(auth, pin) {
  const deny = async () => { throw new Error('INTERACTIVE_AUTH_BLOCKED: use the owned qualified renewal route'); };
  for (const key of ['ensureAccessTokenWithBrowser', 'ensureAccessTokenWithDeviceCode',
    'ensureAccessTokenWithPassword', 'retrieveAuthCodeWithBrowser', 'ensureAccessTokenWithCertificate',
    'ensureAccessTokenWithIdentity', 'ensureAccessTokenWithFederatedIdentity', 'ensureAccessTokenWithSecret']) auth[key] = deny;
  const silent = auth.ensureAccessTokenSilent.bind(auth);
  auth.ensureAccessTokenSilent = async (...args) => {
    assertConnection(auth, pin);
    const r = await silent(...args), a = r?.account, c = r?.idTokenClaims;
    const users = [a?.username, c?.preferred_username, c?.upn].filter(v => v !== undefined);
    const tenants = [r?.tenantId, a?.tenantId, c?.tid].filter(Boolean);
    const objects = [a?.localAccountId, c?.oid].filter(Boolean);
    requireThat(users.length && users.every(v => same(v, pin.username)) &&
      tenants.length && tenants.every(v => same(v, pin.tenantId)) &&
      objects.length && objects.every(v => same(v, pin.objectId)) &&
      (c?.aud === undefined || same(c.aud, pin.appId)) && r.accessToken &&
      new Date(r.expiresOn) > new Date(), 'Silent identity/expiry validation failed');
    return r;
  };
  const ensure = auth.ensureAccessToken.bind(auth);
  Reflect.set(auth, 'ensureAccessToken', async (resource, ...args) => {
    assertConnection(auth, pin);
    requireThat(pin.resources.includes(resource), 'Unpinned auth resource');
    return ensure(resource, ...args);
  });
}

export function guardTransport(config, read, state) {
  requireThat(config.method?.toUpperCase() === 'GET' && config.url === read.url &&
    config.data === undefined && !config.params && !config.auth, 'Transport outside exact GET');
  requireThat(state.attempts++ === 0, 'Second transport attempt blocked');
  config.maxRedirects = 0;
  config.timeout = 30000;
  return config;
}

export async function executeRead(auth, request, pin, name) {
  const read = selectRead(pin, name);
  assertConnection(auth, pin);
  const state = {attempts: 0};
  const id = request.req.interceptors.request.use(c => guardTransport(c, read, state));
  try {
    return await request.get({url: read.url, headers: {accept: 'application/json'},
      responseType: 'json', maxRedirects: 0, timeout: 30000});
  } finally { request.req.interceptors.request.eject(id); }
}

export async function main(argv) {
  requireThat(argv.length === 3, 'Usage: node correspondence_cli_read.mjs PRIVATE_BINDING READ_NAME NEW_PRIVATE_OUTPUT');
  const [bindingArg, name, outputArg] = argv;
  const binding = fs.realpathSync(bindingArg), output = path.resolve(outputArg);
  // Bindings/evidence must remain under this module's ignored private workspace.
  const moduleRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
  const privateRoot = fs.realpathSync(path.join(moduleRoot, '.private-workspace'));
  const isPrivate = p => p.startsWith(privateRoot + path.sep);
  requireThat(isPrivate(binding) && isPrivate(fs.realpathSync(path.dirname(output))) && !fs.existsSync(output), 'Private binding and fresh private output required');
  execFileSync('git', ['check-ignore', '-q', '.private-workspace'], {cwd: moduleRoot});
  const pin = JSON.parse(fs.readFileSync(binding, 'utf8'));
  selectRead(pin, name);
  const pkg = JSON.parse(fs.readFileSync(path.join(pin.sdkRoot, 'package.json'), 'utf8'));
  requireThat(pkg.name === '@pnp/cli-microsoft365' && pkg.version === pin.sdkVersion, 'SDK drift; requalify');
  const lock = path.join(path.dirname(binding), '.correspondence-read.lock');
  fs.mkdirSync(lock, {mode: 0o700});
  try {
    fs.writeFileSync(path.join(lock, 'owner.json'), JSON.stringify({pid: process.pid, at: new Date().toISOString()}), {mode: 0o600});
    const {default: auth} = await import(pathToFileURL(path.join(pin.sdkRoot, 'dist/Auth.js')));
    const {default: request} = await import(pathToFileURL(path.join(pin.sdkRoot, 'dist/request.js')));
    const quiet = {log: async () => {}, logToStderr: async () => {}};
    request.logger = quiet; request.debug = false;
    installAuthGuard(auth, pin); // Before restore or any authentication operation.
    await auth.restoreAuth();
    assertConnection(auth, pin);
    const client = await auth.getPublicClient(quiet, false);
    const account = auth.connection.identityId ? await client.getTokenCache().getAccountByLocalId(auth.connection.identityId) : null;
    requireThat(same(account?.username, pin.username) && same(account?.tenantId, pin.tenantId) &&
      same(account?.localAccountId, pin.objectId), 'Selected cached identity mismatch');
    try {
      const response = await executeRead(auth, request, pin, name);
      fs.writeFileSync(output, JSON.stringify({at: new Date().toISOString(), name, status: 'read-succeeded', response}, null, 2), {flag: 'wx', mode: 0o600});
      console.log(JSON.stringify({name, status: 'read-succeeded', evidence: output}));
    } catch (error) {
      // Do not persist raw request/error objects: they can contain bearer headers.
      const status = error.response?.status ?? null;
      const guardMessages = ['Unpinned auth resource', 'Connection drift; stop without login',
        'Transport outside exact GET', 'Second transport attempt blocked', 'Silent identity/expiry validation failed'];
      const code = error.response?.data?.error?.code ??
        (guardMessages.includes(error.message) ? error.message :
          error.message?.startsWith('INTERACTIVE_AUTH_BLOCKED') ? 'INTERACTIVE_AUTH_BLOCKED' : null);
      fs.writeFileSync(output, JSON.stringify({at: new Date().toISOString(), name, status: 'read-failed', httpStatus: status, code}, null, 2), {flag: 'wx', mode: 0o600});
      console.error(JSON.stringify({name, status: 'read-failed', httpStatus: status, code}));
      process.exitCode = 1;
    }
  } finally { fs.rmSync(lock, {recursive: true}); }
}

if (process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url)
  main(process.argv.slice(2)).catch(() => { console.error('Guard/auth preflight failed; no interactive recovery attempted.'); process.exitCode = 1; });
