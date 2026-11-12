"""Sanitised, offline field_N usage index for Power Automate ZIP exports.

Only physical column codes and action counts are emitted; never record values,
source URLs, connection parameters, action expressions, or private identifiers.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import zipfile

FIELD = re.compile(r"(?<![A-Za-z0-9_])field_([0-9]+)(?![A-Za-z0-9_])", re.I)
UUID = re.compile(
    r"-[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-"
    r"[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"
)


def action_groups(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "actions" and isinstance(value, dict):
                yield value
            yield from action_groups(value)
    elif isinstance(node, list):
        for value in node:
            yield from action_groups(value)


def field_codes(node):
    found = set()
    if isinstance(node, dict):
        for key, value in node.items():
            found.update("field_" + match for match in FIELD.findall(str(key)))
            found.update(field_codes(value))
    elif isinstance(node, list):
        for value in node:
            found.update(field_codes(value))
    elif isinstance(node, str):
        found.update("field_" + match for match in FIELD.findall(node))
    return found


def usage(path):
    rows = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.startswith("Workflows/") and name.endswith(".json")
        )
        if not names or len(names) > 256:
            raise ValueError("unexpected export flow count")
        for name in names:
            if archive.getinfo(name).file_size > 12_000_000:
                raise ValueError("oversized workflow definition")
            obj = json.loads(archive.read(name))
            definition = obj["properties"]["definition"]
            counts, roles, action_count = Counter(), defaultdict(set), 0
            for group in action_groups(definition):
                for action in group.values():
                    if not isinstance(action, dict):
                        continue
                    action_count += 1
                    inputs = action.get("inputs", {})
                    for field in field_codes(inputs):
                        counts[field] += 1
                        role = (
                            "writes_or_projections"
                            if isinstance(inputs, dict) and "parameters" in inputs
                            else "reads_or_transformations"
                        )
                        roles[field].add(role)
            clean = UUID.sub("", Path(name).stem)
            rows.append({
                "flow": clean, "nested_action_count": action_count,
                "physical_field_codes": [
                    {"field": field, "action_refs": counts[field],
                     "roles": sorted(roles[field])}
                    for field in sorted(counts, key=lambda key: int(key[6:]))
                ],
            })
    all_fields = sorted({
        field["field"] for row in rows for field in row["physical_field_codes"]
    }, key=lambda item: int(item[6:]))
    return {
        "schema": "careops-rims.exported-physical-field-usage/1",
        "source_only": True, "native_parity_verified": False,
        "flow_count": len(rows), "distinct_field_codes": len(all_fields),
        "fields": all_fields, "flows": rows,
        "notice": "Field codes do not prove full upstream capture or rendered use.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("solution_zip")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    Path(args.out).write_text(
        json.dumps(usage(args.solution_zip), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
