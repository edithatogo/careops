"""Pure partial F12 transformation; output is not qualified for deployment."""
from copy import deepcopy
import re

FIELDS = dict(zip(
    'event_id event_original_start event_series event_ical_uid event_subject event_type event_organizer event_start event_start_zone event_end event_end_zone event_change_key event_modified event_cancelled agenda_id agenda_name agenda_size agenda_modified agenda_content_type agenda_graph_type agenda_inline'.split(),
    [('event', *p.split('.')) for p in 'id originalStart seriesMasterId iCalUId subject type organizer.emailAddress.address start.dateTime start.timeZone end.dateTime end.timeZone changeKey lastModifiedDateTime isCancelled'.split()] +
    [('agenda', p) for p in 'id name size lastModifiedDateTime contentType @odata.type isInline'.split()]))


def _inputs(definition):
    try:
        return definition['actions']['Require_one_occurrence']['actions']['Require_one_agenda']['actions']['Observed_baseline']['inputs']
    except (KeyError, TypeError):
        raise ValueError('comparator: required action path missing') from None


def bind_comparator(definition):
    """Bind comparisons; declarations, selectors and pre-read guards remain required."""
    inputs = _inputs(definition)
    checks = inputs.get('checks')
    if not isinstance(checks, dict) or set(checks) != set(FIELDS):
        raise ValueError('comparator: exact 21 checks required')
    replacements = {}
    prefixes = {}
    for name, path in FIELDS.items():
        selector = 'Find_exact_occurrence' if path[0] == 'event' else 'Find_issued_agenda'
        observed = f"first(body('{selector}'))" + ''.join(f"?['{p}']" for p in path[1:])
        if name == 'event_organizer':
            observed = f"toLower(coalesce({observed},''))"
        prefix = f'@equals({observed},'
        expression = checks[name]
        if not isinstance(expression, str) or not expression.startswith(prefix) or not expression.endswith(')'):
            raise ValueError(f'{name}: observed comparator drift')
        prefixes[name] = prefix[1:]
        literal = expression[len(prefix):-1]
        if not re.fullmatch(r"'(?:[^']|'')*'|true|false|[0-9]+", literal):
            raise ValueError(f'{name}: expected literal required')
        expected = "parameters('comeet_F12Baseline')" + ''.join(f"?['{p}']" for p in path)
        if name == 'event_organizer':
            expected = f"toLower(coalesce({expected},''))"
        replacements[expression[1:]] = (name, f'equals({observed},{expected})')
    counts = {name: 0 for name in FIELDS}

    def rewrite(value):
        if isinstance(value, dict):
            return {k: rewrite(v) for k, v in value.items()}
        if isinstance(value, list):
            return [rewrite(v) for v in value]
        if isinstance(value, str):
            for old, (name, new) in replacements.items():
                if value.count(prefixes[name]) != value.count(old) + value.count(prefixes[name] + 'null)'):
                    raise ValueError(f'{name}: inconsistent repeated comparison')
                counts[name] += value.count(old)
                value = value.replace(old, new)
        return value

    result = deepcopy(definition)
    rewritten = rewrite(inputs)
    target = _inputs(result)
    target.clear()
    target.update(rewritten)
    if any(count < 2 for count in counts.values()):
        raise ValueError('comparator: repeated result comparisons missing')
    return result, {'comparison_fields': 21, 'replacement_counts': counts,
                    'deployment_ready': False,
                    'remaining': 'Declarations, selectors, pre-read validation, native binding/runtime.'}
