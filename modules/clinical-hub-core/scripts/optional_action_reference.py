"""Offline optional action-reference proposals using the existing F10 carry contract.

The caller supplies an expected source revision and a complete scoped row snapshot.
Neither is independently authenticated here. NOT_FOUND never authorises creation.
No provider connection, persistence, native write or semantic approval is performed.
"""
from copy import deepcopy
import hashlib
import json

from scripts.f10_source_adapter import carry_identity_key, reconcile_agenda_identity


FIELDS = {'contract_version', 'source_id', 'record_id', 'meeting_id',
          'revision', 'operation_key', 'fields'}


def propose(local_rows, envelope=None, *, expected_revision=None, prior=None):
    """Return a detached review proposal; preserve human edits and uncertain retries.

    Source identity is the F10 List GUID / action ID / meeting ID key. Only GUIDs
    are canonicalised; opaque IDs and revisions retain case. A prior receipt is
    caller-retained reconciliation context, not proof of a completed native write.
    Even exact retries recheck the current row snapshot before returning duplicate.
    """
    if not isinstance(local_rows, list) or any(not isinstance(row, dict) for row in local_rows):
        raise ValueError('A complete scoped row snapshot is required')
    result = {'status': 'standalone', 'local_rows': deepcopy(local_rows),
              'proposal': None, 'write_proposed': False}
    if envelope is None:
        return result
    try:
        if (not isinstance(envelope, dict) or set(envelope) != FIELDS
                or type(envelope['contract_version']) is not int
                or envelope['contract_version'] != 1
                or any(not isinstance(envelope[k], str) or not envelope[k].strip()
                       for k in ('source_id', 'revision', 'operation_key'))):
            raise ValueError('Invalid versioned envelope')
        key = carry_identity_key(envelope['source_id'], envelope['record_id'], envelope['meeting_id'])
        reconciled = reconcile_agenda_identity(local_rows, key=key, expected_fields=envelope['fields'])
        digest = hashlib.sha256(json.dumps(envelope, sort_keys=True, separators=(',', ':'),
                                          allow_nan=False).encode()).hexdigest()
    except (ValueError, TypeError, AttributeError):
        return dict(result, status='invalid_envelope')
    if not isinstance(expected_revision, str) or envelope['revision'] != expected_revision:
        return dict(result, status='stale_or_unverified')
    receipt = {'source_identity': key, 'source_revision': envelope['revision'],
               'operation_key': envelope['operation_key'], 'digest': digest}
    result.update(status=reconciled['status'], receipt=receipt, reconciliation=reconciled)
    if reconciled['status'] != 'EXISTING_MATCH':
        return result
    if prior is not None:
        return dict(result, status='duplicate' if prior == receipt else 'reconciliation_required')
    return dict(result, proposal=deepcopy(envelope['fields']))
