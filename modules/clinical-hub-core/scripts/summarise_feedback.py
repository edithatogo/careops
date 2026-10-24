#!/usr/bin/env -S .venv-ci/bin/python
"""Summarise one meeting's feedback locally. No service calls or publication."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

CALCULATION_VERSION = '1'

FIELDS = {'meeting_id', 'question_version', 'response_id', 'recommendation', 'usefulness', 'comment'}


def score(value, low, high):
    value = value.strip()
    if not value:
        return None, 'missing'
    if not value.isascii() or not value.isdigit() or not low <= int(value) <= high:
        return None, 'invalid'
    return int(value), 'valid'


def summarise(rows, meeting, version):
    if not meeting.strip() or not version.strip():
        raise ValueError('Select one meeting identifier and question version.')
    counts = {name: {'valid': 0, 'missing': 0, 'invalid': 0, 'distribution': {str(i): 0 for i in range(lo, hi + 1)}}
              for name, lo, hi in [('recommendation', 0, 10), ('usefulness', 1, 5)]}
    seen = set()
    comments = 0
    for row in rows:
        if set(row) != FIELDS or any(not isinstance(v, str) for v in row.values()):
            raise ValueError('Use exactly the six documented CSV columns; malformed rows are not scored.')
        if row['meeting_id'] != meeting or row['question_version'] != version:
            raise ValueError('Mixed or mismatched meetings/versions: separate the input before scoring.')
        identity = row['response_id'].strip()
        if not identity or identity in seen:
            raise ValueError('Missing or duplicate response ID: reconcile against the retained raw export.')
        seen.add(identity)
        comments += bool(row['comment'].strip())
        for name, lo, hi in [('recommendation', 0, 10), ('usefulness', 1, 5)]:
            value, status = score(row[name], lo, hi)
            counts[name][status] += 1
            if value is not None:
                counts[name]['distribution'][str(value)] += 1
    rec = counts['recommendation']
    n = rec['valid']
    promoters = sum(rec['distribution'][str(i)] for i in (9, 10))
    detractors = sum(rec['distribution'][str(i)] for i in range(7))
    use = counts['usefulness']
    return {'status': 'Draft local summary; human review required', 'meeting_id': meeting,
            'question_version': version, 'response_count': len(seen),
            'recommendation': {**rec, 'nps': round(100 * (promoters - detractors) / n, 2) if n else None},
            'usefulness': {**use, 'mean': round(sum(int(k) * v for k, v in use['distribution'].items()) / use['valid'], 2) if use['valid'] else None},
            'comments_answered': comments,
            'limits': ['No responses or no valid scores produces null, not zero.',
                       'Response IDs detect repeated export rows, not multiple submissions by one person.',
                       'No respondent identities or comments are reproduced. Raw input remains unchanged.',
                       'Usefulness is primary; NPS is complementary. No attendance denominator or representativeness is inferred.']}


def run(source, destination, meeting, version):
    raw = Path(source).read_bytes()
    with io.StringIO(raw.decode('utf-8-sig'), newline='') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or len(reader.fieldnames) != len(FIELDS) or set(reader.fieldnames) != FIELDS:
            raise ValueError('CSV header must contain the six documented columns exactly once.')
        result = summarise(reader, meeting, version)
    result['provenance'] = {'input_sha256': hashlib.sha256(raw).hexdigest(),
                            'calculation_version': CALCULATION_VERSION,
                            'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if Path(destination).suffix.lower() != '.json':
        raise ValueError('Use a local .json output file.')
    with Path(destination).open('x', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--meeting', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    try:
        run(args.input, args.output, args.meeting, args.version)
    except (ValueError, OSError, csv.Error, UnicodeError):
        parser.exit(2, 'Cannot summarise: check the documented schema, meeting/version, response IDs and unused output path. No source content is printed.\n')
    print('Local draft summary created. Review before use.')


if __name__ == '__main__':
    main()
