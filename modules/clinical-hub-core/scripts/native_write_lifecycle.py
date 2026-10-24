"""Maker-only lifecycle templates and definition summaries; no request is executed.

The caller must independently qualify native origin, exact bindings, authority,
current preimage and effect readback. Importing this module never authenticates,
writes, activates or invokes a service. Tests use a deferred fictional fetch.
"""
import copy
import json
from collections import Counter

from scripts.flow_definition import definition

def native_write_lifecycle_scripts():
    """Native page PATCH lifecycle: observation expiry never cancels/reissues it.

    Evaluate these functions only on the already-qualified native origin. Keep
    that page alive until terminal response AND independent effect readback.
    The start template is async and must be awaited. Exact payload digests bind
    retries without retaining another body copy.
    No credentials, authorization headers, request body or response headers are
    retained in the page registry. A transport error still needs reconciliation.
    """
    start = r"""async (request) => {
      request = {...request};
      const key = '__clinicalHubConditionalWritesV1';
      if (location.origin !== request.origin) throw Error('Native origin drift');
      if (!/^[A-Za-z0-9_-]{8,160}$/.test(request.id)) throw Error('Request ID required');
      if (!/^\/api\/data\/v9\.2\/(workflows|environmentvariablevalues)\([0-9a-f-]{36}\)$/.test(request.path))
        throw Error('Unexpected native target');
      if (!/^W\/"[0-9]+"$/.test(request.etag)) throw Error('Exact ETag required');
      const fields = Object.keys(request.payload || {});
      const environment = request.path.includes('/environmentvariablevalues(');
      if (environment ? fields.length !== 1 || fields[0] !== 'value' || typeof request.payload.value !== 'string'
          : !fields.length || fields.some(k => !['clientdata', 'statecode', 'statuscode'].includes(k)))
        throw Error('Unexpected native payload');
      const registry = window[key] || (window[key] = Object.create(null));
      const receipt = r => ({id:r.id, origin:r.origin, path:r.path, etag:r.etag,
        state:r.state, startedAt:r.startedAt, endedAt:r.endedAt, status:r.status,
        result:r.result, error:r.error, reconciled:r.reconciled});
      const payloadText = JSON.stringify(request.payload);
      const payloadBytes = new TextEncoder().encode(payloadText);
      const payloadDigest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', payloadBytes)))
        .map(byte => byte.toString(16).padStart(2, '0')).join('');
      if (location.origin !== request.origin) throw Error('Native origin drift');
      if (registry[request.id]) {
        const prior = registry[request.id];
        if (prior.origin !== request.origin || prior.path !== request.path
            || prior.etag !== request.etag || prior.payloadDigest !== payloadDigest)
          throw Error('Request ID was reused with changed target, version or payload; reconcile');
        return receipt(prior);
      }
      if (Object.values(registry).some(r => !r.reconciled))
        throw Error('Previous native request needs terminal result and effect reconciliation');
      const record = {id:request.id, origin:request.origin, path:request.path,
        etag:request.etag, payloadDigest, state:'pending', startedAt:new Date().toISOString(),
        endedAt:null, status:null, result:null, error:null, reconciled:false};
      registry[request.id] = record;
      // No AbortSignal/deadline: the caller observes this same retained Promise.
      record.promise = fetch(request.path, {method:'PATCH',
        headers:{'Content-Type':'application/json','If-Match':request.etag},
        body:payloadText}).then(async response => {
          record.status = response.status;
          record.result = await response.text();
          record.state = 'http_terminal';
          record.endedAt = new Date().toISOString();
        }).catch(error => {
          record.state = 'transport_error';
          record.error = String(error);
          record.endedAt = new Date().toISOString();
        });
      return receipt(record);
    }"""
    observe = r"""(request) => {
      const record = window.__clinicalHubConditionalWritesV1?.[request.id];
      if (location.origin !== request.origin || !record || record.origin !== request.origin)
        throw Error('Native request handle missing/origin changed; reconcile, never restart');
      return {id:record.id, origin:record.origin, path:record.path, etag:record.etag,
        state:record.state, startedAt:record.startedAt, endedAt:record.endedAt,
        status:record.status, result:record.result, error:record.error,
        reconciled:record.reconciled};
    }"""
    reconcile = r"""(request) => {
      const record = window.__clinicalHubConditionalWritesV1?.[request.id];
      if (location.origin !== request.origin || !record || record.origin !== request.origin
          || record.state !== 'http_terminal' || !request.evidence)
        throw Error('Actual terminal HTTP result and independent effect evidence required');
      record.reconciled = true;
      record.evidence = request.evidence;
      return {id:record.id, state:record.state, reconciled:true, evidence:record.evidence};
    }"""
    return {'start': start, 'observe': observe, 'reconcile': reconcile}

def summary_entry_multisets(value):
    """Preserve every summary entry and its count, ignoring only group order."""
    if not isinstance(value, dict) or set(value) != {'actions', 'triggers'}:
        return None
    groups = {}
    for group in ('actions', 'triggers'):
        entries = value[group]
        if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
            return None
        groups[group] = Counter(json.dumps(entry, sort_keys=True, separators=(',', ':'))
                                for entry in entries)
    return groups

def definition_summary(value):
    """Project the observed flat Compose/Select and Button Request summary.

    None means unknown: nested graphs, other node types/fields and unfamiliar
    metadata must not authorise a summary change.
    """
    if not isinstance(value, dict) or set(value) - {
            '$schema', 'contentVersion', 'parameters', 'triggers', 'actions',
            'outputs', 'metadata'}:
        return None
    summary = {}
    for group in ('actions', 'triggers'):
        nodes = value.get(group)
        if not isinstance(nodes, dict):
            return None
        summary[group] = []
        for node in nodes.values():
            if not isinstance(node, dict) or set(node) - {
                    'type', 'kind', 'inputs', 'runAfter', 'metadata'}:
                return None
            if group == 'actions':
                if node.get('type') not in ('Compose', 'Select') or 'kind' in node:
                    return None
            elif node.get('type') != 'Request' or node.get('kind') != 'Button':
                return None
            item = {'type': node['type']}
            if 'kind' in node:
                item['kind'] = node['kind']
            if 'metadata' in node:
                metadata = node['metadata']
                if (not isinstance(metadata, dict) or
                        set(metadata) != {'operationMetadataId'} or
                        not isinstance(metadata['operationMetadataId'], str)):
                    return None
                item['metadata'] = copy.deepcopy(metadata)
            summary[group].append(item)
    return summary
