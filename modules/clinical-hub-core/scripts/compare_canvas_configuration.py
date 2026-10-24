"""Compare maintained YAML with an observed export without treating omissions as parity.

Local inspection only: no authentication, native writes, or deployment. Reports can
contain private formulas/bindings and belong outside public source control.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently losing a property."""


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError('Configuration keys must be strings')
        if key in result:
            raise ValueError(f'Duplicate configuration key: {key}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor('tag:yaml.org,2002:map', _mapping)


def load_configuration(path):
    value = yaml.load(Path(path).read_text(), Loader=UniqueKeyLoader)
    if not isinstance(value, dict) or not value:
        raise ValueError('Expected a nonempty configuration mapping')
    return value


def _flatten(value, path=()):
    if isinstance(value, dict) and value:
        return {p: v for k, item in value.items()
                for p, v in _flatten(item, path + (k,)).items()}
    if isinstance(value, list) and value:
        return {p: v for i, item in enumerate(value)
                for p, v in _flatten(item, path + (i,)).items()}
    return {path: value}


def compare_configuration(maintained, observed):
    """Report exact differences, including absent defaults and reordered controls.

    No whitespace, quoted literal, case, expression or default normalization is
    inferred. An operator may separately explain a difference using native evidence.
    """
    left, right = _flatten(maintained), _flatten(observed)
    common = left.keys() & right.keys()
    sort = lambda paths: sorted(paths, key=lambda p: json.dumps(p))
    changed = [dict(path=list(p), maintained=left[p], observed=right[p])
               for p in sort(common)
               if type(left[p]) is not type(right[p]) or left[p] != right[p]]
    unobserved = [list(p) for p in sort(left.keys() - right.keys())]
    added = [list(p) for p in sort(right.keys() - left.keys())]
    status = ('differences' if changed or added else
              'incomplete' if unobserved else 'exact_match')
    return dict(status=status, common_properties=len(common), changed=changed,
                unobserved=unobserved, added=added)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('maintained', type=Path)
    parser.add_argument('observed', type=Path)
    parser.add_argument('--report', required=True, type=Path,
                        help='New private report path; never overwritten')
    args = parser.parse_args()
    report = compare_configuration(load_configuration(args.maintained),
                                   load_configuration(args.observed))
    with args.report.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({k: len(v) if isinstance(v, list) else v
                      for k, v in report.items()}))
    return {'exact_match': 0, 'differences': 1, 'incomplete': 2}[report['status']]


if __name__ == '__main__':
    raise SystemExit(main())
