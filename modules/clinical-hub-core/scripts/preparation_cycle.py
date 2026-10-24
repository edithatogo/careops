"""Pure preparation carry-forward; caller supplies the maintained control contract.

No document generator or tenant runtime. Use the existing maintained Word/manual
route for output. Ready controls reset for review; unresolved inputs are retained.
"""
from copy import deepcopy

STATES = {'Not started', 'This meeting', 'Waiting for input', 'Ready for chair review'}

def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} needs text; use To confirm for an unresolved input.')
    if any(ord(c) < 32 and c not in '\n\r\t' for c in value):
        raise ValueError(f'{field} contains an unsupported control character.')

def validate(data, *, control_keys):
    if (not isinstance(control_keys, (list, tuple)) or not control_keys
            or any(not isinstance(k, str) or not k.strip() for k in control_keys)
            or len(set(control_keys)) != len(control_keys)):
        raise ValueError('A unique nonempty maintained control contract is required.')
    fields = {'cycle', 'meeting', 'priorities', 'pack', 'register', 'controls', 'previous_cycle'}
    if not isinstance(data, dict) or set(data) != fields:
        raise ValueError('Use the preparation input fields only; assignments and clinical actions are not supported.')
    for key in fields - {'controls', 'previous_cycle'}:
        text(data[key], key)
    if data['previous_cycle'] is not None:
        text(data['previous_cycle'], 'previous_cycle')
    if not isinstance(data['controls'], dict) or set(data['controls']) != set(control_keys):
        raise ValueError('Exactly the explicitly configured preparation controls are required.')
    for key, control in data['controls'].items():
        if not isinstance(control, dict) or set(control) != {'state', 'note', 'source'}:
            raise ValueError(f'{key} requires state, note and source only.')
        if not isinstance(control['state'], str) or control['state'] not in STATES:
            raise ValueError(f'{key}: unsupported preparation state.')
        text(control['note'], key + ' note')
        text(control['source'], key + ' source')
    return data

def next_cycle(data, cycle, previous_ref, *, control_keys):
    """Keep unresolved preparation intact; retain the previous input by reference."""
    validate(data, control_keys=control_keys)
    text(cycle, 'new cycle')
    text(previous_ref, 'previous input reference')
    if cycle.strip().casefold() == data['cycle'].strip().casefold():
        raise ValueError('The next cycle needs a different identifier.')
    result = deepcopy(data)
    result.update(cycle=cycle, meeting='To confirm', priorities='To confirm',
                  pack='To confirm the selected versions for this cycle', previous_cycle=previous_ref)
    for key, control in result['controls'].items():
        if control['state'] == 'Ready for chair review':
            control.update(state='Not started',
                           note='Recheck for this cycle. Earlier preparation remains in the previous input.',
                           source=previous_ref + ' / ' + key)
    return validate(result, control_keys=control_keys)
