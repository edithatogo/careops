"""Pure review-only H2 selection; no native authority, I/O or mutable global state.

Inputs assert metadata; they do not authenticate access/approval. Preserve the
canonical snapshot digest when binding a future operation. F12's existing strict
baseline validator and any native adapter remain separate qualifications.
"""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import re
from scripts.f12_configuration import LIMIT
PROFILE = frozenset({'schema_version', 'forum_ref', 'profile_revision', 'effective_from', 'effective_until', 'display_name', 'purpose', 'control_keys', 'agenda_sections', 'capabilities', 'governance', 'roles', 'binding_ref', 'template_ref', 'destination_ref', 'register_ref'})
SELECTION = frozenset({'schema_version', 'forum_ref', 'profile_revision', 'occurrence_ref', 'snapshot_revision', 'start', 'end', 'window_start', 'window_end', 'event', 'capabilities', 'sources'})
EVENT = frozenset({'event_ref', 'series_ref', 'original_start', 'type', 'subject', 'organizer', 'cancelled'})
SOURCE = frozenset({'source_ref', 'kind', 'name', 'revision', 'sha256'})
CAPABILITIES = frozenset({'prepare', 'compare_calendar'})
REFERENCES = ('binding_ref', 'template_ref', 'destination_ref', 'register_ref')

def _shape(v, keys):
    if not isinstance(v, dict) or set(v) != keys:
        raise ValueError('Unexpected fields')

def _text(v):
    if not isinstance(v, str) or not v.strip() or len(v) > 2000 or any((ord(c) < 32 or 55296 <= ord(c) <= 57343 for c in v)):
        raise ValueError('Nonempty bounded text required')

def _ref(v):
    if not isinstance(v, str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}', v):
        raise ValueError('Opaque reference required')

def _version(v):
    if type(v) is not int or v != 1:
        raise ValueError('Unsupported schema version')

def _time(v):
    _text(v)
    d = datetime.fromisoformat(v.replace('Z', '+00:00'))
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError('Explicit timezone required')
    return d

def _texts(v):
    if not isinstance(v, list) or not v or len(v) > 256:
        raise ValueError('Nonempty bounded list required')
    for x in v:
        _text(x)
    if len(set(v)) != len(v):
        raise ValueError('Duplicate value')

def _evidence(v, role=False):
    _shape(v, {'state', 'source_ref'} | ({'role_ref'} if role else set()))
    if v['state'] not in {'unverified', 'draft', 'conflicting', 'recorded'}:
        raise ValueError('Unknown evidence state')
    if role:
        _ref(v['role_ref'])
    if v['source_ref'] is not None:
        _ref(v['source_ref'])
    elif v['state'] == 'recorded':
        raise ValueError('Recorded evidence needs a source')

def _profile(p):
    _shape(p, PROFILE)
    _version(p['schema_version'])
    for k in ('forum_ref', 'profile_revision', *REFERENCES):
        _ref(p[k])
    for k in ('display_name', 'purpose'):
        _text(p[k])
    for k in ('control_keys', 'agenda_sections', 'capabilities'):
        _texts(p[k])
    if not set(p['capabilities']) <= CAPABILITIES:
        raise ValueError('Only review capabilities supported')
    start = _time(p['effective_from'])
    end = None if p['effective_until'] is None else _time(p['effective_until'])
    if end is not None and end <= start:
        raise ValueError('Invalid effective interval')
    _evidence(p['governance'])
    _shape(p['roles'], {'chair', 'delegate', 'secretariat'})
    for r in p['roles'].values():
        _evidence(r, True)
    return (start, end)

def _sources(rows):
    if not isinstance(rows, list) or not rows or len(rows) > 256:
        raise ValueError('Bounded selected source pins required')
    refs = []
    for s in rows:
        _shape(s, SOURCE)
        _ref(s['source_ref'])
        _ref(s['revision'])
        _text(s['name'])
        if s['kind'] not in {'agenda', 'minutes', 'register', 'governance', 'template'}:
            raise ValueError('Unsupported source kind')
        if not isinstance(s['sha256'], str) or not re.fullmatch('[a-fA-F0-9]{64}', s['sha256']):
            raise ValueError('Source hash required')
        refs.append(s['source_ref'])
    if len(set(refs)) != len(refs):
        raise ValueError('Duplicate source pin')

def _selection(s):
    _shape(s, SELECTION)
    _version(s['schema_version'])
    for k in ('forum_ref', 'profile_revision', 'occurrence_ref', 'snapshot_revision'):
        _ref(s[k])
    start, end, ws, we = (_time(s[k]) for k in ('start', 'end', 'window_start', 'window_end'))
    if not ws <= start < end <= we:
        raise ValueError('Window must contain ordered interval')
    _shape(s['event'], EVENT)
    e = s['event']
    _ref(e['event_ref'])
    _text(e['subject'])
    _text(e['organizer'])
    if type(e['cancelled']) is not bool:
        raise ValueError('Cancellation must be Boolean')
    if e['type'] not in {'singleInstance', 'occurrence', 'exception'}:
        raise ValueError('Occurrence type required')
    if e['type'] == 'singleInstance':
        if e['series_ref'] is not None or e['original_start'] is not None:
            raise ValueError('Do not invent single-instance lineage')
    else:
        _ref(e['series_ref'])
        _time(e['original_start'])
    _texts(s['capabilities'])
    _sources(s['sources'])
    return start

def _result(*codes):
    return dict(state='blocked', preview_only=True, native_authority=False, write_proposed=False, blockers=list(codes), governance_state=None, preparation_control_keys=None, agenda_sections=None, references=None, f12_selection=None, f12_selection_json=None, snapshot_json=None, snapshot_sha256=None)

def resolve(profiles, selection, *, observed_sources):
    """Select an explicitly pinned effective revision; return review-only arguments.

    Recorded sources and complete observations are caller assertions, not proven
    approval/access. Inputs are unchanged. Returned canonical JSON is immutable;
    derived argument copies cannot change its digest or another invocation.
    No persistent current-profile or operation/replay ledger is introduced.
    """
    try:
        start = _selection(selection)
    except (ValueError, TypeError, OverflowError):
        return _result('INVALID_SELECTION')
    if not isinstance(profiles, list) or not profiles or len(profiles) > 256:
        return _result('INVALID_PROFILE')
    try:
        intervals = [_profile(p) for p in profiles]
    except (ValueError, TypeError, OverflowError):
        return _result('INVALID_PROFILE')
    ids = [(p['forum_ref'], p['profile_revision']) for p in profiles]
    if len(set(ids)) != len(ids):
        return _result('DUPLICATE_PROFILE')
    for i, p in enumerate(profiles):
        a, b = intervals[i]
        for j in range(i):
            c, d = intervals[j]
            if p['forum_ref'] == profiles[j]['forum_ref'] and (d is None or a < d) and (b is None or c < b):
                return _result('OVERLAPPING_PROFILE_INTERVALS')
    matches = [(p, span) for p, span in zip(profiles, intervals) if p['forum_ref'] == selection['forum_ref']]
    if not matches:
        return _result('UNKNOWN_FORUM')
    matches = [(p, span) for p, span in matches if p['profile_revision'] == selection['profile_revision']]
    if not matches:
        return _result('UNKNOWN_PROFILE_REVISION')
    p, (begin, end) = matches[0]
    if start < begin or (end is not None and start >= end):
        return _result('PROFILE_NOT_EFFECTIVE')
    if not set(selection['capabilities']) <= set(p['capabilities']):
        return _result('CAPABILITY_NOT_ALLOWED')
    if selection['event']['cancelled']:
        return _result('CANCELLED_OCCURRENCE')
    try:
        _shape(observed_sources, {'state', 'sources'})
        if observed_sources['state'] != 'complete':
            return _result('SOURCE_READ_UNVERIFIED')
        _sources(observed_sources['sources'])
    except (ValueError, TypeError):
        return _result('SOURCE_READ_UNVERIFIED')
    pins = sorted(selection['sources'], key=lambda s: s['source_ref'])
    if sorted(observed_sources['sources'], key=lambda s: s['source_ref']) != pins:
        return _result('SOURCE_DRIFT')
    f12 = None
    f12_json = None
    if 'compare_calendar' in selection['capabilities']:
        agendas = [s for s in pins if s['kind'] == 'agenda']
        if len(agendas) != 1:
            return _result('AMBIGUOUS_AGENDA_SOURCE')
        f12 = dict(window_start=selection['window_start'], window_end=selection['window_end'], subject=selection['event']['subject'], organizer=selection['event']['organizer'], agenda_name=agendas[0]['name'])
        f12_json = json.dumps(f12, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        if len(f12_json.encode('utf-16-le')) // 2 > LIMIT:
            return _result('F12_SELECTION_LIMIT')
    snapshot = json.dumps(dict(profile=p, selection=selection), sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    return {**_result(), 'state': 'review_only', 'governance_state': p['governance']['state'], 'preparation_control_keys': tuple(p['control_keys']) if 'prepare' in selection['capabilities'] else None, 'agenda_sections': tuple(p['agenda_sections']), 'references': {k: deepcopy(p[k]) for k in REFERENCES}, 'f12_selection': f12, 'f12_selection_json': f12_json, 'snapshot_json': snapshot, 'snapshot_sha256': hashlib.sha256(snapshot.encode()).hexdigest()}
