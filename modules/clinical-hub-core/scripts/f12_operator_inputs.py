"""Prepare native F12 meeting-selector controls; never execute a flow."""
from copy import deepcopy

SELECTION_PARAMETER = 'F12 metadata selection (comeet_F12Selection)'
FIELDS = {
    'window_start': ('Search from', 'Date and time with timezone, for example 2026-09-28T00:00:00+10:00.'),
    'window_end': ('Search until', 'Date and time with timezone after the meeting ends.'),
    'subject': ('Meeting title', 'Exact title of the already identified meeting.'),
    'organizer': ('Organiser email', 'Existing organiser; this does not create or change an invitation.'),
    'agenda_name': ('Agenda filename', 'Exact accepted attachment filename; this does not approve a paper.'),
}
SAVED = 'Saved configuration'
ENTER = 'Enter meeting details'


def build_operator_inputs(baseline):
    """Keep the accepted baseline and every existing guard/source/comparator."""
    result = deepcopy(baseline)
    definition = result['properties']['definition']
    triggers = definition['triggers']
    if len(triggers) != 1 or 'manual' not in triggers:
        raise ValueError('Expected the existing manual trigger')
    trigger = triggers['manual']
    if (trigger['type'], trigger['kind']) != ('Request', 'Button'):
        raise ValueError('Expected the owner-operated manual button')
    schema = trigger['inputs']['schema']
    if schema.get('properties') or schema.get('required'):
        raise ValueError('Existing operator inputs changed; reconcile before replacing')
    if SELECTION_PARAMETER not in definition['parameters']:
        raise ValueError('Existing maker selection binding is missing')
    actions = definition['actions']
    if any(name in actions for name in ('Meeting_details', 'Operator_selection')):
        raise ValueError('Operator actions already exist')
    parse = actions['Parse_configuration']
    if parse.get('runAfter'):
        raise ValueError('Configuration prerequisites changed')
    old = "parameters('" + SELECTION_PARAMETER + "')"
    replacements = 0

    def rewrite(value):
        nonlocal replacements
        if isinstance(value, dict):
            return {k: rewrite(v) for k, v in value.items()}
        if isinstance(value, list):
            return [rewrite(v) for v in value]
        if isinstance(value, str):
            replacements += value.count(old)
            return value.replace(old, "outputs('Operator_selection')")
        return value

    # Rewrite only existing actions, leaving technical parameters intact.
    definition['actions'] = actions = rewrite(actions)
    if replacements == 0:
        raise ValueError('No existing selection consumers found')
    schema['properties'] = {
        'configuration_mode': {
            'type': 'string', 'title': 'Configure using',
            'enum': [SAVED, ENTER], 'default': SAVED,
            'description': 'Use the saved settings or complete all meeting details below.'},
        **{key: {'type': 'string', 'title': title, 'description': description}
           for key, (title, description) in FIELDS.items()},
    }
    # Conditional completeness is enforced by the unchanged Parse_selection.
    schema['required'] = []
    actions['Meeting_details'] = {
        'type': 'Compose', 'runAfter': {},
        'inputs': {key: "@coalesce(triggerBody()?['" + key + "'],'')" for key in FIELDS},
    }
    mode = "triggerBody()?['configuration_mode']"
    actions['Operator_selection'] = {
        'type': 'Compose', 'runAfter': {'Meeting_details': ['Succeeded']},
        'inputs': (f"@if(or(empty({mode}),equals({mode},'{SAVED}')),{old},"
                   f"if(equals({mode},'{ENTER}'),outputs('Meeting_details'),json('{{}}')))"),
    }
    actions['Parse_configuration']['runAfter'] = {'Operator_selection': ['Succeeded']}
    return result
