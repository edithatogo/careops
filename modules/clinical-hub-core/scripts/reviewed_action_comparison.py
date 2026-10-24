"""Finite source comparison; no semantic authority, register write or document output."""

def action_discrepancies(expected, proposed):
    """Compare structured candidates to a separately reviewed fixture oracle, not free prose."""
    for name, rows in [('expected', expected), ('proposed', proposed)]:
        if (not isinstance(rows, list) or any(not isinstance(row, dict)
                or not isinstance(row.get('id'), str) or not row['id'].strip() for row in rows)):
            raise ValueError('Structured action lists with nonempty IDs are required.')
    if len({row['id'] for row in expected}) != len(expected):
        raise ValueError('The independently reviewed source contains duplicate IDs.')
    issues = []
    truth = {x['id']: x for x in expected}
    ids = [x.get('id') for x in proposed]
    for key in sorted(set(truth) - set(ids)):
        issues.append('omitted:' + key)
    for key in sorted(set(ids) - set(truth)):
        issues.append('invented:' + str(key))
    for key in sorted(set(ids)):
        if ids.count(key) > 1:
            issues.append('duplicate:' + str(key))
    for item in proposed:
        key = item.get('id')
        if key in truth:
            for field in sorted(item.keys() - truth[key].keys()):
                issues.append('unexpected:' + key + ':' + field)
            for field, value in truth[key].items():
                if item.get(field) != value:
                    issues.append('incorrect:' + key + ':' + field)
    return issues
