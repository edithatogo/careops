"""Static, tenant-free Power Automate solution admission audit.

Never publishes raw workflow JSON, connector parameter values, endpoints,
credentials, tenant identifiers, or personal paths. An audit is not native ALM
qualification. Core admission refuses premium/unknown connector dependencies.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile

SCHEMA = "careops-rims.flow-admission/1"
STANDARD_CONNECTORS = frozenset({
    "shared_sharepointonline", "shared_onedriveforbusiness",
    "shared_excelonlinebusiness", "shared_office365",
})
PREMIUM_CONNECTORS = frozenset({
    "shared_commondataserviceforapps", "shared_commondataservice",
    "shared_http", "shared_httpwithazuread", "shared_azureblob",
})
REVIEW_ACTION_TYPES = frozenset({
    "Http", "HttpWebhook", "ApiConnection", "ApiConnectionWebhook",
})
PERSONAL_PATTERN = re.compile(r"(?:https?://[^\s/]+)?/personal/", re.I)


class AdmissionError(ValueError):
    """Invalid, unqualified or unsafe source flow."""


def _no_duplicate_keys(items):
    result = {}
    for key, value in items:
        if key in result:
            raise AdmissionError("duplicate JSON object key")
        result[key] = value
    return result


def _safe_name(filename):
    stem = Path(filename).stem
    stem = re.sub(r"-[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}", "", stem)
    return re.sub(r"[^A-Za-z0-9_-]", "_", stem)[:96]


def _walk_groups(node, prefix="definition"):
    """Yield WDL action groups exactly once, including nested branches."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = prefix + "/" + str(key)
            if key == "actions" and isinstance(value, dict):
                yield child, value
            yield from _walk_groups(value, child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk_groups(value, prefix + "/" + str(index))


def _check_group(groups, errors):
    for _prefix, actions in groups:
        for name, action in actions.items():
            if not isinstance(action, dict):
                errors.append("INVALID_ACTION_OBJECT")
                continue
            if not isinstance(action.get("type"), str) or not action["type"]:
                errors.append("INVALID_ACTION_TYPE")
            dependencies = action.get("runAfter", {})
            if not isinstance(dependencies, dict):
                errors.append("INVALID_RUNAFTER")
                continue
            for previous, states in dependencies.items():
                if previous not in actions or previous == name:
                    errors.append("DANGLING_RUNAFTER")
                if not isinstance(states, list) or not states or any(
                    state not in {"Succeeded", "Failed", "Skipped", "TimedOut"}
                    for state in states
                ):
                    errors.append("INVALID_RUNAFTER_STATUS")
        visiting, done = set(), set()

        def visit(key):
            if key in visiting:
                errors.append("RUNAFTER_CYCLE")
                return
            if key in done or key not in actions:
                return
            visiting.add(key)
            item = actions[key]
            parents = item.get("runAfter", {}) if isinstance(item, dict) else {}
            for previous in parents if isinstance(parents, dict) else ():
                visit(previous)
            visiting.remove(key)
            done.add(key)

        for key in actions:
            visit(key)


def audit_flow(raw: bytes, filename: str) -> dict:
    obj = json.loads(raw, object_pairs_hook=_no_duplicate_keys)
    if not isinstance(obj, dict) or not isinstance(obj.get("properties"), dict):
        raise AdmissionError("invalid workflow root")
    definition = obj["properties"].get("definition")
    if not isinstance(definition, dict) or not isinstance(definition.get("triggers"), dict):
        raise AdmissionError("missing definition/triggers")
    groups = list(_walk_groups(definition))
    actions = [
        action for _, group in groups for action in group.values()
        if isinstance(action, dict)
    ]
    errors = []
    _check_group(groups, errors)
    connectors, premium, unqualified = set(), set(), set()
    included = 0
    for action in actions:
        if action.get("type") in REVIEW_ACTION_TYPES:
            premium.add("ACTION_" + action["type"])
        inputs = action.get("inputs")
        if isinstance(inputs, dict):
            host = inputs.get("host")
            if isinstance(host, dict):
                for ref in (host.get("apiId"), host.get("connectionName")):
                    if isinstance(ref, str):
                        connectors.update(re.findall(r"shared_[A-Za-z0-9_]+", ref, re.I))
            parameters = inputs.get("parameters", {})
            if isinstance(parameters, dict):
                included += sum(
                    1 for key, value in parameters.items()
                    if key.startswith("item/") and value == "Included"
                )
    personal = bool(PERSONAL_PATTERN.search(raw.decode("utf-8", "replace")))
    declared = obj["properties"].get("connectionReferences", {})
    if not isinstance(declared, dict):
        errors.append("INVALID_CONNECTION_REFERENCES")
    else:
        for refname, reference in declared.items():
            if refname.startswith("shared_"):
                connectors.add(refname)
            if isinstance(reference, dict):
                api_name = reference.get("api", {}).get("name")
                if isinstance(api_name, str) and api_name.startswith("shared_"):
                    connectors.add(api_name)
    for connector in connectors:
        if connector in PREMIUM_CONNECTORS:
            premium.add("CONNECTOR_" + connector)
        elif connector not in STANDARD_CONNECTORS:
            unqualified.add(connector)
    return {
        "name": _safe_name(filename),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "nested_actions": len(actions),
        "action_groups": len(groups),
        "connectors": sorted(connectors),
        "premium_candidates": sorted(premium),
        "unqualified_connectors": sorted(unqualified),
        "source_included_writes": included,
        "personal_path_candidate": personal,
        "errors": sorted(set(errors)),
        "source_only": True,
        "native_verified": False,
    }


def audit_zip(path, *, core_flows=()):
    core = set(core_flows)
    rows = []
    with zipfile.ZipFile(path) as archive:
        files = sorted(
            n for n in archive.namelist()
            if n.startswith("Workflows/") and n.endswith(".json")
        )
        if not files or len(files) != len(set(files)):
            raise AdmissionError("missing or duplicate workflow members")
        seen = set()
        for member in files:
            info = archive.getinfo(member)
            if info.file_size > 12_000_000 or info.compress_size > 12_000_000:
                raise AdmissionError("oversized workflow payload")
            row = audit_flow(archive.read(member), member)
            if row["name"] in seen:
                raise AdmissionError("duplicate normalized workflow name")
            seen.add(row["name"])
            if row["name"] in core and (
                row["premium_candidates"] or row["unqualified_connectors"]
            ):
                row["errors"].append("UNQUALIFIED_CORE_DEPENDENCY")
            rows.append(row)
    summary = Counter()
    for row in rows:
        summary["nested_actions"] += row["nested_actions"]
        summary["included_writes"] += row["source_included_writes"]
        summary["premium_candidate_flows"] += bool(row["premium_candidates"])
        summary["unqualified_flows"] += bool(row["unqualified_connectors"])
        summary["personal_path_candidate_flows"] += row["personal_path_candidate"]
        summary["invalid_flows"] += bool(row["errors"])
    return {
        "schema": SCHEMA,
        "source_archive_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "flows": rows,
        "summary": {"flow_count": len(rows), **dict(sorted(summary.items()))},
        "core_scope": sorted(core),
        "source_only": True,
        "native_verified": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sanitised, source-only RIMS Power Automate admission audit"
    )
    parser.add_argument("source_zip")
    parser.add_argument("--core-flow", action="append", default=[])
    parser.add_argument("--fail-on-errors", action="store_true")
    args = parser.parse_args(argv)
    report = audit_zip(args.source_zip, core_flows=args.core_flow)
    print(json.dumps(report, indent=2, sort_keys=True))
    return int(args.fail_on_errors and report["summary"]["invalid_flows"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
