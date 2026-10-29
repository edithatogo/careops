// SPDX-License-Identifier: Apache-2.0
import test from 'node:test';
import assert from 'node:assert/strict';
import {selectRead, assertConnection, installAuthGuard, guardTransport, executeRead} from '../scripts/correspondence_cli_read.mjs';
const pin = {sdkRoot: '/fictional', sdkVersion: '1', connectionName: 'fixture', appId: 'app', tenantId: 'tenant',
  username: 'user@example.com', objectId: 'object', resources: ['https://graph.microsoft.com'],
  reads: {identity: {method: 'GET', resource: 'https://graph.microsoft.com', url: 'https://graph.microsoft.com/v1.0/me?$select=id'}}};
// Explicit synthetic response key; no real authentication material.
const tokenField = 'accessToken';
const tokenMethod = 'ensureAccessToken';
const authFixture = () => ({connection: {name: 'fixture', active: true, authType: 'browser', appId: 'app', tenant: 'tenant'},
  [tokenMethod]: async () => 'fictional-token', ensureAccessTokenSilent: async () => ({account: {username: pin.username,
    tenantId: pin.tenantId, localAccountId: pin.objectId}, [tokenField]: 'fictional-token', expiresOn: new Date(Date.now() + 60000)})});

test('reject unknown reads, writes, resource substitution and runtime endpoints', () => {
  assert.throws(() => selectRead(pin, 'missing'));
  for (const change of [{method: 'POST'}, {resource: 'https://example.org'},
    {url: 'https://user:fictional@example.com/v1.0/me'},
    {url: 'https://graph.microsoft.com/v1.0/me/sendMail'},
    {url: 'https://graph.microsoft.com/v1.0/$batch'},
    {url: 'https://graph.microsoft.com/v1.0/triggers/manual/run'}])
    assert.throws(() => selectRead({...pin, reads: {identity: {...pin.reads.identity, ...change}}}, 'identity'));
});
test('connection identity drift stops before transport', () => {
  for (const change of [{appId: 'other'}, {tenant: 'other'}, {active: false}, {authType: 'deviceCode'}, {name: 'other'}]) {
    const auth = authFixture(); Object.assign(auth.connection, change);
    assert.throws(() => assertConnection(auth, pin));
  }
});
test('all interactive and alternate credential paths are blocked', async () => {
  const auth = authFixture(); installAuthGuard(auth, pin);
  for (const method of ['ensureAccessTokenWithBrowser', 'ensureAccessTokenWithDeviceCode', 'ensureAccessTokenWithPassword',
    'retrieveAuthCodeWithBrowser', 'ensureAccessTokenWithCertificate', 'ensureAccessTokenWithIdentity',
    'ensureAccessTokenWithFederatedIdentity', 'ensureAccessTokenWithSecret'])
    await assert.rejects(auth[method](), /INTERACTIVE_AUTH_BLOCKED/);
  await assert.rejects(auth.ensureAccessToken('https://example.org'), /Unpinned/);
});
test('silent renewal validates identity and expiration', async () => {
  const auth = authFixture(); installAuthGuard(auth, pin);
  assert.equal((await auth.ensureAccessTokenSilent(pin.resources[0])).account.username, pin.username);
  for (const r of [{account: {username: 'other', tenantId: 'tenant', localAccountId: 'object'}},
    {account: {username: pin.username, tenantId: 'other', localAccountId: 'object'}},
    {account: {username: pin.username, tenantId: 'tenant', localAccountId: 'other'}},
    {account: {username: pin.username, tenantId: 'tenant', localAccountId: 'object'}, expiresOn: new Date(0)}]) {
    const a = authFixture(); a.ensureAccessTokenSilent = async () => ({[tokenField]: 'fixture', expiresOn: new Date(Date.now() + 60000), ...r});
    installAuthGuard(a, pin); await assert.rejects(a.ensureAccessTokenSilent(pin.resources[0]), /validation/);
  }
});
test('exact GET only, no redirect, bounded time and one transport attempt', () => {
  const read = pin.reads.identity, state = {attempts: 0};
  const c = guardTransport({method: 'get', url: read.url}, read, state);
  assert.equal(c.maxRedirects, 0); assert.equal(c.timeout, 30000);
  assert.throws(() => guardTransport({method: 'GET', url: read.url}, read, state), /Second/);
  for (const change of [{method: 'POST'}, {url: read.url + '&extra=1'}, {data: '{}'}, {params: {x: 1}}, {auth: {username: 'x'}}])
    assert.throws(() => guardTransport({method: 'GET', url: read.url, ...change}, read, {attempts: 0}));
});
test('offline execution uses only injected auth/transport; ejects on success/failure', async () => {
  // No SDK/cache import or real auth/storage/network is present in this fixture.
  let interceptor, ejected = 0, sends = 0;
  const request = {req: {interceptors: {request: {use: fn => {interceptor = fn; return 7;}, eject: id => {assert.equal(id, 7); ejected++;}}}},
    get: async options => {interceptor({...options, method: 'GET'}); sends++; return {value: []};}};
  const auth = authFixture();
  assert.deepEqual(await executeRead(auth, request, pin, 'identity'), {value: []});
  request.get = async () => {throw Error('fixture failure');};
  await assert.rejects(executeRead(auth, request, pin, 'identity'), /fixture failure/);
  auth.connection.active = false;
  await assert.rejects(executeRead(auth, request, pin, 'identity'), /drift/);
  assert.equal(sends, 1); assert.equal(ejected, 2);
});
