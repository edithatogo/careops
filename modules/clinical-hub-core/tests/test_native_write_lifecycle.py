"""Local browser-JS lifecycle proof with a deferred fake fetch; no network."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.native_write_lifecycle import native_write_lifecycle_scripts


def test_one_pending_request_survives_observation_and_never_reissues():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node required for the native-page JavaScript lifecycle check')
    scripts = native_write_lifecycle_scripts()
    program = "import assert from 'node:assert/strict';\n"
    for name, source in scripts.items():
        program += f'const {name} = ({source});\n'
    program += r"""
globalThis.window = {};
globalThis.location = {origin:'https://native.invalid'};
const calls = [];
let resolve, reject;
globalThis.fetch = (path, options) => {
  calls.push({path, options});
  return new Promise((yes, no) => {resolve=yes; reject=no;});
};
const first = {id:'f12_local_request_01', origin:location.origin,
  path:'/api/data/v9.2/environmentvariablevalues(00000000-0000-0000-0000-000000000001)',
  etag:'W/"1"', payload:{value:'{}'}};
assert.equal(start(first).state, 'pending');
const promise = window.__clinicalHubConditionalWritesV1[first.id].promise;
for(let i=0; i<5; i++) assert.equal(observe(first).state, 'pending');
assert.equal(start(first).state, 'pending');
assert.equal(calls.length, 1);
assert.equal(calls[0].options.method, 'PATCH');
assert.equal(calls[0].options.headers['If-Match'], first.etag);
assert.equal(calls[0].options.signal, undefined);
assert.equal(calls[0].options.headers.Authorization, undefined);
const second = {...first, id:'f12_local_request_02'};
assert.throws(()=>start(second), /Previous native request/);
assert.throws(()=>reconcile({...first,evidence:'pending'}), /terminal HTTP/);
resolve({status:204, text:async()=>''});
await promise;
assert.equal(observe(first).state, 'http_terminal');
assert.equal(observe(first).status, 204);
assert.ok(observe(first).startedAt && observe(first).endedAt);
assert.equal(start(first).status, 204);
assert.equal(calls.length, 1);
assert.throws(()=>reconcile(first), /effect evidence/);
assert.equal(reconcile({...first,evidence:'independent exact readback'}).reconciled, true);
assert.equal(start(second).state, 'pending');
assert.equal(calls.length, 2);
reject(new Error('transport failure; effects unknown'));
await window.__clinicalHubConditionalWritesV1[second.id].promise;
assert.equal(observe(second).state, 'transport_error');
assert.throws(()=>start({...first,id:'f12_local_request_03'}), /Previous native request/);
assert.throws(()=>reconcile({...second,evidence:'not an HTTP result'}), /terminal HTTP/);
assert.throws(()=>observe({...first,origin:'https://other.invalid'}), /origin/);
assert.throws(()=>observe({...first,id:'missing_request'}), /handle missing/);
assert.throws(()=>start({...first,path:'/other'}), /target/);
assert.throws(()=>start({...first,etag:'*'}), /ETag/);
assert.throws(()=>start({...first,payload:{value:'{}',other:true}}), /payload/);
assert.equal(calls.length, 2);
assert.equal(window.__clinicalHubConditionalWritesV1[first.id].promise, promise);
console.log(JSON.stringify({result:'PASS', issued:2, observed_without_reissue:true,
  terminal_and_effect_reconciliation_required:true, transport_error_stops:true}));
"""
    result = subprocess.run([node, '--input-type=module'], input=program,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['result'] == 'PASS'
