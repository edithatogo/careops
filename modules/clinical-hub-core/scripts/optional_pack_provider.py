"""Pure optional-provider proposal adapter; local pack and human edits stay authoritative."""
from copy import deepcopy
import hashlib
import json
import re
from scripts.preflight_pack import validate


def propose(local_pack, envelope=None, *, expected_revision=None, prior=None):
    """Validate a versioned external pack proposal; never update or authenticate records."""
    validate(local_pack)
    result = {'status': 'standalone', 'local_pack': deepcopy(local_pack),
              'proposal': None, 'write_proposed': False}
    if envelope is None:
        return result
    keys = {'contract_version', 'provider', 'record_id', 'revision', 'operation_key', 'pack'}
    if not isinstance(envelope, dict) or set(envelope) != keys or type(envelope['contract_version']) is not int or envelope['contract_version'] != 1:
        return dict(result, status='incompatible_provider')
    if any(not isinstance(envelope[k], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', envelope[k])
           for k in ('provider', 'record_id', 'revision', 'operation_key')):
        return dict(result, status='invalid_identity')
    if expected_revision is None or envelope['revision'] != expected_revision:
        return dict(result, status='stale_or_unverified')
    try:
        checks = validate(envelope['pack'])
    except (ValueError, TypeError):
        return dict(result, status='invalid_payload')
    if checks['meeting_id'] != local_pack['meeting_id']:
        return dict(result, status='wrong_meeting')
    identity = (envelope['provider'], envelope['record_id'])
    digest = hashlib.sha256(json.dumps(envelope, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    receipt = {'source_identity': list(identity), 'operation_key': envelope['operation_key'], 'digest': digest}
    if prior is not None:
        if prior == receipt:
            return dict(result, status='duplicate', receipt=deepcopy(prior))
        return dict(result, status='reconciliation_required')
    return dict(result, status='proposal_for_review', proposal=deepcopy(envelope['pack']),
                receipt=receipt, preflight=checks)
