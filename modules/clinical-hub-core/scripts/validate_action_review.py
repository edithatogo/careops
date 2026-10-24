#!/usr/bin/env python3
"""Validate a local historical-action review CSV without promoting records."""
import argparse
import csv
import json
from pathlib import Path


REQUIRED = {
    'Review ID', 'Follow-up', 'Evidence classification',
    'People described in source (not assignments)', 'Timing as recorded',
    'Evidence', 'Outstanding qualification', 'Commissioning status',
    'Issue readiness',
}
CANONICAL_HEADERS = {name.casefold(): name for name in REQUIRED}


def validate(path):
    path = Path(path)
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, restkey='__extra__', restval=None, strict=True)
        if reader.fieldnames is None:
            raise ValueError('CSV header is required.')
        if any(not (name or '').strip() for name in reader.fieldnames):
            raise ValueError('CSV column names must not be blank.')
        normalized_headers = [name.strip().casefold() for name in reader.fieldnames]
        if len(normalized_headers) != len(set(normalized_headers)):
            raise ValueError('CSV column names must be unique.')
        reader.fieldnames = [CANONICAL_HEADERS.get(normalized, original.strip())
                             for normalized, original in zip(normalized_headers, reader.fieldnames)]
        missing = REQUIRED - set(reader.fieldnames)
        if missing:
            raise ValueError(f'Missing required columns: {", ".join(sorted(missing))}')
        rows = list(reader)

    if not rows:
        raise ValueError('At least one review row is required.')
    seen = set()
    for line, row in enumerate(rows, start=2):
        if row.get('__extra__'):
            raise ValueError(f'Row {line}: extra CSV fields; quote embedded commas and reconcile the row.')
        for column in REQUIRED:
            if not isinstance(row.get(column), str) or not row[column].strip():
                raise ValueError(f'Row {line}: {column} must not be blank.')
        ident = row['Review ID'].strip().casefold()
        if ident in seen:
            raise ValueError(f'Row {line}: duplicate local review ID; reconcile before drafting.')
        seen.add(ident)
        readiness = row['Issue readiness'].strip().casefold()
        if readiness not in {'hold', 'hold; no live issue or assignment'}:
            raise ValueError(f'Row {line}: keep issue readiness held pending chair/secretariat classification; validator cannot set readiness.')
        status = row['Commissioning status'].strip().casefold()
        if status not in {'unresolved', 'unresolved; chair classification required'}:
            raise ValueError(f'Row {line}: keep commissioning unresolved pending chair classification; validator cannot set commission.')
    return {'status': 'STRUCTURE_VALID', 'rows': len(rows), 'promoted': 0,
            'authority': 'Structural local validation only; no source truth, approval or issue readiness established.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.csv_path)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
