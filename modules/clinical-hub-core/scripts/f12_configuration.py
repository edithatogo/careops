"""Local F12 configuration validation; no provider, storage or flow mutation."""
from __future__ import annotations

import json
from datetime import datetime, timezone

LIMIT = 2000
EVENT_KEYS = {'id', 'originalStart', 'seriesMasterId', 'iCalUId', 'subject',
              'type', 'organizer', 'start', 'end', 'changeKey',
              'lastModifiedDateTime', 'isCancelled'}
AGENDA_KEYS = {'id', 'name', 'size', 'lastModifiedDateTime', 'contentType',
               '@odata.type', 'isInline'}


def _shape(value, keys, field):
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f'{field}: required keys do not match')


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field}: nonempty text required')


def _instant(value, field, *, utc_label=False):
    _text(value, field)
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None:
            if not utc_label:
                raise ValueError()
            result = result.replace(tzinfo=timezone.utc)
        if utc_label and result.utcoffset().total_seconds() != 0:
            raise ValueError()
        return result
    except (ValueError, OverflowError):
        raise ValueError(f'{field}: valid explicit timezone required') from None


def _characters(raw):
    # Conservatively count UTF-16 units for Dataverse text, including supplementary Unicode.
    try:
        return len(raw.encode('utf-16-le')) // 2
    except (AttributeError, UnicodeEncodeError):
        raise ValueError('configuration: invalid text encoding') from None


def _decode(raw, field):
    # Measure the actual text supplied for storage, including whitespace and escapes.
    if not isinstance(raw, str) or _characters(raw) > LIMIT:
        raise ValueError(f'{field}: JSON text exceeds character limit or is not text')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'{field}: duplicate JSON key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except json.JSONDecodeError:
        raise ValueError(f'{field}: malformed JSON') from None


def validate_configuration(baseline_text: str, selection_text: str) -> dict:
    """Reject incomplete configuration; return shape proof, never supplied values."""
    b, s = _decode(baseline_text, 'baseline'), _decode(selection_text, 'selection')
    _shape(b, {'event', 'agenda', 'checked_at', 'baseline_run_id'}, 'baseline')
    _shape(s, {'window_start', 'window_end', 'subject', 'organizer', 'agenda_name'}, 'selection')
    e, a = b['event'], b['agenda']
    _shape(e, EVENT_KEYS, 'event')
    _shape(a, AGENDA_KEYS, 'agenda')
    for key in EVENT_KEYS - {'organizer', 'start', 'end', 'isCancelled'}:
        _text(e[key], f'event.{key}')
    for key in AGENDA_KEYS - {'size', 'isInline'}:
        _text(a[key], f'agenda.{key}')
    for key in s:
        _text(s[key], f'selection.{key}')
    for field, value in [('event.isCancelled', e['isCancelled']), ('agenda.isInline', a['isInline'])]:
        if type(value) is not bool:
            raise ValueError(f'{field}: boolean required')
    if type(a['size']) is not int or a['size'] < 0:
        raise ValueError('agenda.size: nonnegative integer required')
    _shape(e['organizer'], {'emailAddress'}, 'event.organizer')
    _shape(e['organizer']['emailAddress'], {'address'}, 'event.organizer.emailAddress')
    address = e['organizer']['emailAddress']['address']
    _text(address, 'event.organizer.address')
    times = {}
    for key in ['start', 'end']:
        _shape(e[key], {'dateTime', 'timeZone'}, f'event.{key}')
        # Current F12 reads explicitly request UTC. Other timezone routes are unqualified.
        if e[key]['timeZone'] != 'UTC':
            raise ValueError(f'event.{key}.timeZone: current F12 contract requires UTC')
        times[key] = _instant(e[key]['dateTime'], f'event.{key}.dateTime', utc_label=True)
    ws, we = (_instant(s[key], f'selection.{key}') for key in ['window_start', 'window_end'])
    if not ws <= times['start'] < times['end'] <= we:
        raise ValueError('selection.window: ordered window must contain baseline interval')
    for field, value in [('checked_at', b['checked_at']), ('event.originalStart', e['originalStart']),
                         ('event.lastModifiedDateTime', e['lastModifiedDateTime']),
                         ('agenda.lastModifiedDateTime', a['lastModifiedDateTime'])]:
        _instant(value, field)
    _text(b['baseline_run_id'], 'baseline_run_id')
    if s['subject'] != e['subject'] or s['organizer'].lower() != address.lower() or s['agenda_name'] != a['name']:
        raise ValueError('selection: selectors differ from baseline')
    if a['isInline']:
        raise ValueError('agenda.isInline: current F12 selector requires non-inline attachment')
    return {'status': 'PASS', 'comparison_fields': 21,
            'baseline_characters': _characters(baseline_text), 'selection_characters': _characters(selection_text),
            'measurement': 'Conservative UTF-16 units of actual stored JSON text',
            'limit': 'Local configuration shape only; no native binding, source accuracy or acceptance proof.'}
