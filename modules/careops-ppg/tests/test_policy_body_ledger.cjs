const test = require('node:test');
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const path = require('node:path');
const os = require('node:os');
const script = path.resolve(__dirname, '../scripts/ppg_policy_body_ledger.mjs');

test('a valid list UUID cannot bypass either private-path guard', () => {
  const local = path.join(os.tmpdir(), '.local');
  const uuid = '11111111-2222-3333-4444-555555555555';
  for (const args of [
    [path.join(os.tmpdir(), 'outside.mjs'), path.join(local, 'receipt.json'), uuid],
    [path.join(local, 'adapter.mjs'), path.join(os.tmpdir(), 'outside.json'), uuid],
    [path.join(local, 'adapter.mjs'), path.join(local, 'receipt.json'), 'invalid-list-id'],
  ]) {
    const result = spawnSync(process.execPath, [script, ...args], {encoding: 'utf8'});
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Supply private adapter\/new receipt paths/);
    assert.doesNotMatch(result.stderr, /ERR_MODULE_NOT_FOUND/);
  }
});

 test('view readback rejects filters that hide unresolved identities', () => {
  const fs = require('node:fs');
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ppg-ledger-'));
  const local = path.join(root, '.local'); fs.mkdirSync(local);
  const query = '<GroupBy Collapse="TRUE"><FieldRef Name="BodyIdentityState" /></GroupBy><OrderBy><FieldRef Name="Title" /></OrderBy>';
  try {
    for (const [name, viewQuery, succeeds] of [
      ['complete', query, true],
      ['filtered', query + '<Where><Eq><FieldRef Name="BodyIdentityState"/><Value Type="Text">Retained body bound</Value></Eq></Where>', false],
    ]) {
      const adapter = path.join(local, name + '.mjs'), receipt = path.join(local, name + '.json');
      fs.writeFileSync(adapter, `export async function connect() { return {
        all: async route => route.includes('/fields?') ? [
          {InternalName:'BodyIdentityState',TypeAsString:'Text'},
          {InternalName:'BodyIdentityEvidence',TypeAsString:'Note'},
          {InternalName:'BodyIdentityJSON',TypeAsString:'Note'}] : [{Title:'Policy body identities'}],
        get: async route => route.endsWith('/ViewFields') ? {Items:['LinkTitle','DocumentUID','sourceDocumentId','BodyIdentityState','BodyIdentityEvidence','BodyIdentityJSON']} : {ViewQuery:${JSON.stringify(viewQuery)},ServerRelativeUrl:'/example'},
        send: async () => { throw Error('Unexpected mutation'); }
      }; }`);
      const result = spawnSync(process.execPath, [script, adapter, receipt], {encoding:'utf8'});
      assert.equal(result.status === 0, succeeds, result.stderr);
      assert.equal(fs.existsSync(receipt), succeeds);
      if (!succeeds) assert.match(result.stderr, /Ledger view differs/);
    }
  } finally { fs.rmSync(root, {recursive:true, force:true}); }
});
