"""Pure source adapters for pinned H2 snapshots and unchanged legacy entry points.

Bindings/observations are caller assertions, never native access or authority.
No provider, persistence, authentication, native save or execution is performed.
"""
from copy import deepcopy
import hashlib
import json
from urllib.parse import urlsplit

from scripts.forum_configuration import resolve
from scripts.preparation_cycle import validate, next_cycle
from scripts.f07_operator_inputs import build_operator_inputs
from scripts.f12_configuration import validate_configuration, _instant


class CompatibilityError(ValueError):
    """A scoped compatibility boundary was not satisfied."""


def _require(condition, code):
    if not condition:
        raise CompatibilityError(code)


def _pairs(items):
    result = {}
    for key, value in items:
        _require(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _context(snapshot_json, expected_snapshot_sha256, observed_sources, capability):
    _require(isinstance(snapshot_json, str) and len(snapshot_json) <= 4_000_000, 'INVALID_SNAPSHOT')
    digest = hashlib.sha256(snapshot_json.encode()).hexdigest()
    _require(digest == expected_snapshot_sha256, 'SNAPSHOT_DIGEST_MISMATCH')
    snapshot = json.loads(snapshot_json, object_pairs_hook=_pairs)
    _require(isinstance(snapshot, dict) and set(snapshot) == {'profile', 'selection'}, 'INVALID_SNAPSHOT')
    r = resolve([snapshot['profile']], snapshot['selection'], observed_sources=observed_sources)
    _require(r['state'] == 'review_only', 'SNAPSHOT_REVALIDATION_FAILED')
    _require(r['snapshot_json'] == snapshot_json, 'NONCANONICAL_SNAPSHOT')
    _require(capability in snapshot['selection']['capabilities'], 'CAPABILITY_NOT_SELECTED')
    return snapshot['profile'], snapshot['selection'], r


def _shape(value, keys):
    _require(isinstance(value, dict) and set(value) == keys, 'INVALID_BINDING_SHAPE')


def _bound(binding, profile, selection):
    for key, expected in [('forum_ref', profile['forum_ref']),
                          ('occurrence_ref', selection['occurrence_ref']),
                          ('binding_ref', profile['binding_ref'])]:
        _require(binding[key] == expected, 'WRONG_BINDING_CONTEXT')


def _pin(selection, ref):
    pins = [p for p in selection['sources'] if p['source_ref'] == ref]
    _require(len(pins) == 1, 'UNKNOWN_SOURCE_REFERENCE')
    return pins[0]


def _result(payload=None, *, blocker=None, validation=None):
    return {'state': 'blocked' if blocker else 'review_only', 'preview_only': True,
            'native_authority': False, 'write_proposed': False, 'payload': payload,
            'blockers': [blocker] if blocker else [], 'legacy_validation': validation}


def _failure(error):
    return _result(blocker=str(error) if isinstance(error, CompatibilityError) else 'LEGACY_INPUT_INVALID')


def _preparation(profile, selection, r, data):
    copy = deepcopy(data)
    validate(copy, control_keys=r['preparation_control_keys'])
    _require(copy['meeting'] == selection['occurrence_ref'], 'WRONG_PREPARATION_OCCURRENCE')
    _require(copy['register'] == profile['register_ref'], 'WRONG_PREPARATION_REGISTER')
    agendas = {p['source_ref'] for p in selection['sources'] if p['kind'] == 'agenda'}
    _require(copy['pack'] in agendas, 'WRONG_PREPARATION_PACK')
    return copy


def preparation_inputs(*, snapshot_json, expected_snapshot_sha256, observed_sources, data):
    """Validate selected-source preparation using the original control contract."""
    try:
        p, s, r = _context(snapshot_json, expected_snapshot_sha256, observed_sources, 'prepare')
        return _result(_preparation(p, s, r, data))
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as error:
        return _failure(error)


def next_preparation_inputs(*, snapshot_json, expected_snapshot_sha256, observed_sources,
                            data, cycle, previous_ref):
    """Reuse carry-forward exactly; next meeting/authority remains unconfirmed."""
    try:
        p, s, r = _context(snapshot_json, expected_snapshot_sha256, observed_sources, 'prepare')
        current = _preparation(p, s, r, data)
        return _result(next_cycle(current, cycle, previous_ref,
                                  control_keys=r['preparation_control_keys']))
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as error:
        return _failure(error)


def paper_candidate(*, snapshot_json, expected_snapshot_sha256, observed_sources,
                    baseline, expected_baseline_sha256, binding):
    """Prepare the same F07 candidate as the legacy builder; never save/run it."""
    try:
        p, s, _ = _context(snapshot_json, expected_snapshot_sha256, observed_sources, 'prepare')
        _shape(binding, {'forum_ref', 'occurrence_ref', 'binding_ref', 'source_ref',
                         'site', 'path', 'name', 'version', 'etag', 'sha256'})
        _bound(binding, p, s)
        pin = _pin(s, binding['source_ref'])
        for key, field in [('name', 'name'), ('version', 'revision'), ('sha256', 'sha256')]:
            _require(binding[key] == pin[field], 'SOURCE_BINDING_DRIFT')
        _require(all(isinstance(binding[k], str) and binding[k].strip() for k in ('site', 'path', 'etag')),
                 'INVALID_SOURCE_BINDING')
        site = urlsplit(binding['site'])
        _require(site.scheme == 'https' and site.hostname is not None
                 and site.hostname.endswith('.sharepoint.com') and not site.username
                 and not site.password and site.port is None and not site.query
                 and not site.fragment, 'UNSUPPORTED_SOURCE_SITE')
        path = binding['path']
        _require(isinstance(path, str) and path.startswith('/')
                 and not any(c in path for c in '\\?#\r\n\x00')
                 and not any(part in {'.', '..', ''} for part in path[1:].split('/'))
                 and path.rsplit('/', 1)[-1] == pin['name'], 'UNSUPPORTED_SOURCE_PATH')
        _require(isinstance(binding['etag'], str) and bool(binding['etag'].strip()), 'MISSING_SOURCE_ETAG')
        _require(_digest(baseline) == expected_baseline_sha256, 'BASELINE_DIGEST_MISMATCH')
        _require(baseline['properties']['state'] == 'Stopped', 'STOPPED_BASELINE_REQUIRED')
        candidate = build_operator_inputs(baseline, **{k: binding[k] for k in
            ('site', 'path', 'name', 'version', 'etag')}, paper_ref=binding['source_ref'])
        _require({k: v for k, v in candidate.items() if k != 'properties'} ==
                 {k: v for k, v in baseline.items() if k != 'properties'}, 'FLOW_IDENTITY_DRIFT')
        _require({k: v for k, v in candidate['properties'].items() if k != 'definition'} ==
                 {k: v for k, v in baseline['properties'].items() if k != 'definition'}, 'FLOW_BINDING_DRIFT')
        return _result(candidate)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as error:
        return _failure(error)


def calendar_inputs(*, snapshot_json, expected_snapshot_sha256, observed_sources,
                    baseline_text, binding):
    """Bind the full existing F12 baseline without fabricating missing metadata."""
    try:
        p, s, r = _context(snapshot_json, expected_snapshot_sha256, observed_sources, 'compare_calendar')
        _shape(binding, {'forum_ref', 'occurrence_ref', 'binding_ref', 'event_ref', 'event_id',
                         'series_ref', 'series_id', 'agenda_ref', 'agenda_id',
                         'agenda_revision', 'agenda_sha256'})
        _bound(binding, p, s)
        event = s['event']
        _require(event['type'] != 'singleInstance', 'F12_LINEAGE_UNSUPPORTED')
        _require(binding['event_ref'] == event['event_ref']
                 and binding['series_ref'] == event['series_ref'], 'CALENDAR_REFERENCE_DRIFT')
        pin = _pin(s, binding['agenda_ref'])
        _require(pin['kind'] == 'agenda' and binding['agenda_revision'] == pin['revision']
                 and binding['agenda_sha256'] == pin['sha256'], 'AGENDA_BINDING_DRIFT')
        validation = validate_configuration(baseline_text, r['f12_selection_json'])
        baseline = json.loads(baseline_text)
        e, a = baseline['event'], baseline['agenda']
        _require(e['id'] == binding['event_id'] and e['seriesMasterId'] == binding['series_id']
                 and a['id'] == binding['agenda_id'], 'NATIVE_IDENTITY_DRIFT')
        _require(e['type'] == event['type'] and e['isCancelled'] == event['cancelled']
                 and _instant(e['originalStart'], 'original') == _instant(event['original_start'], 'selected'),
                 'OCCURRENCE_LINEAGE_DRIFT')
        for field in ('start', 'end'):
            _require(_instant(e[field]['dateTime'], field, utc_label=True) == _instant(s[field], field),
                     'OCCURRENCE_TIME_DRIFT')
        return _result({'baseline_text': baseline_text, 'selection_text': r['f12_selection_json']},
                       validation=validation)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as error:
        return _failure(error)
