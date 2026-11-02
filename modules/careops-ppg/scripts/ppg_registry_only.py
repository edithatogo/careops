"""Compile an installation-specific, versioned Registry-only manifest into QW3."""
import argparse
import copy
import json
from pathlib import Path
from uuid import UUID


def validate(manifest):
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("entries"), list):
        raise ValueError("unsupported registry-only manifest")
    seen = set()
    ids = set()
    identifiers = set()
    for row in manifest["entries"]:
        uid = row["documentUID"]
        item = row["itemId"]
        identifier = row["printedIdentifier"]
        if (str(UUID(uid)) != uid or uid in seen or type(item) is not int or item < 1
                or item in ids or not identifier.strip() or identifier in identifiers
                or not row["evidenceRef"].strip()):
            raise ValueError("invalid or duplicate registry-only identity")
        seen.add(uid)
        ids.add(item)
        identifiers.add(identifier)
    return manifest["entries"]


def transform(document, manifest):
    entries = validate(manifest)
    result = copy.deepcopy(document)

    def visit(node):
        if isinstance(node, dict):
            if "Guard_input" in node and "Read_current_after" in node:
                yield node
            for child in node.values():
                yield from visit(child)
        elif isinstance(node, list):
            for child in node:
                yield from visit(child)
    matches = list(visit(result))
    if len(matches) != 1:
        raise ValueError(f"expected one QW3 reconciliation action group, found {len(matches)}")
    actions = matches[0]
    def replace(node, old, new):
        for key, value in node.items():
            if isinstance(value, dict):
                replace(value, old, new)
            elif isinstance(value, str):
                node[key] = value.replace(old, new)
    def action(kind, inputs, previous):
        return {"type": kind, "inputs": inputs, "runAfter": {previous: ["Succeeded"]}}
    def query(name, source, predicate, previous):
        actions[name] = action("Query", {"from": "@"+source, "where": "@"+predicate}, previous)
    uid = "item()?['DocumentUID']"
    raw = "body('Read_current')?['d']?['results']"
    final = raw.replace("Read_current", "Read_current_after")
    # Apply to the existing importer, preserving its comparisons, concurrency and writer.
    date = "first(body('Find_native'))?['sourceNextReviewDateRaw']"
    scalar = f"float(json({date}))"
    guarded = f"if(empty(string({date})),null,{scalar})"
    if guarded not in json.dumps(actions["Guard_input"]):
        replace(actions["Guard_input"], scalar, guarded)
    if "Registry_manifest" in actions:
        if actions["Registry_manifest"]["inputs"] == manifest:
            return result
        # The only installation-specific values in the compiled definition.
        actions["Registry_manifest"]["inputs"] = copy.deepcopy(manifest)
        actions["Registry_pins"]["inputs"] = {e["documentUID"]: e for e in entries}
        actions["Registry_identifiers"]["inputs"] = {e["printedIdentifier"]: e["documentUID"] for e in entries}
        return result
    replace(actions, raw, "body('Workbook_before')")
    replace(actions, final, "body('Workbook_after')")
    actions["Registry_manifest"] = action("Compose", copy.deepcopy(manifest), "Read_current")
    actions["Registry_pins"] = action("Compose", {e["documentUID"]: e for e in entries}, "Registry_manifest")
    actions["Registry_identifiers"] = action("Compose", {e["printedIdentifier"]: e["documentUID"] for e in entries}, "Registry_pins")
    base = "body('Extract_copy')?['result']?['identityContract']?['baseUIDs']"
    new = "coalesce(body('Extract_copy')?['result']?['identityApplication']?['newUIDs'],json('[]'))"
    entry_uid = "item()?['documentUID']"
    query("Registry_remaining", "outputs('Registry_manifest')?['entries']",
          f"and(not(contains({base},{entry_uid})),not(contains({new},{entry_uid})))", "Registry_identifiers")
    actions["Registry_remaining_UIDs"] = action("Select", {"from":"@body('Registry_remaining')","select":"@"+entry_uid}, "Registry_remaining")
    remaining = f"contains(body('Registry_remaining_UIDs'),{uid})"
    pin = f"outputs('Registry_pins')?[{uid}]"
    query("Registry_pinned_rows", raw, f"contains(outputs('Registry_pins'),{uid})", "Registry_remaining_UIDs")
    query("Invalid_registry_pins", "body('Registry_pinned_rows')",
          f"or(not(equals(item()?['Id'],{pin}?['itemId'])),and({remaining},or(not(equals(item()?['sourceDocumentId'],{pin}?['printedIdentifier'])),not(equals(item()?['sourceSnapshotRef'],{pin}?['evidenceRef'])))))", "Registry_pinned_rows")
    alias = "item()?['fields']?['sourceDocumentId']"
    query("Registry_alias_collisions", "outputs('Parse_candidate')?['operations']",
          f"and(contains(outputs('Registry_identifiers'),{alias}),not(equals(outputs('Registry_identifiers')?[{alias}],{uid})))", "Invalid_registry_pins")
    query("Registry_before", raw, remaining, "Registry_alias_collisions")
    query("Workbook_before", raw, f"not({remaining})", "Registry_before")
    actions["Candidate_UIDs"]["runAfter"] = {"Workbook_before":["Succeeded"]}
    query("Registry_after", final, remaining, "Read_current_after")
    query("Workbook_after", final, f"not({remaining})", "Registry_after")
    actions["Active_current_after"]["runAfter"] = {"Workbook_after":["Succeeded"]}
    guard = actions["Guard_input"]
    guard["expression"] = ("@and("+guard["expression"][1:]+",empty(body('Invalid_registry_pins')),"
        "empty(body('Registry_alias_collisions')),equals(length(body('Registry_pinned_rows')),length(outputs('Registry_manifest')?['entries'])),"
        "equals(length(body('Registry_before')),length(body('Registry_remaining_UIDs'))))")
    # Explicit adoption is the existing reviewed new-UID application, using the pinned
    # UID of a row already present. It is always a conditional update to the same item.
    unqualified = actions["Unqualified_new_identities"]["inputs"]
    unqualified["where"] = "@and("+unqualified["where"][1:]+f",not(and(contains(outputs('Registry_pins'),{uid}),contains({new},{uid}))))"
    # A prospective adoption may have blank workbook dates until its first patch.
    current = guard["actions"]["Canonical_current"]["inputs"]["select"]
    current["sourceNextReviewDateRaw"] = "@if(empty(string(item()?['sourceNextReviewDateRaw'])),null,"+current["sourceNextReviewDateRaw"][1:]+")"
    # SharePoint regenerates __metadata.id on GET. Keep its ETag and all item fields.
    for side in ("before", "after"):
        source = "Registry_" + side
        stable = "Stable_registry_" + side
        actions[stable] = action("Select", {
            "from": "@body('" + source + "')",
            "select": "@setProperty(item(),'__metadata',removeProperty(item()?['__metadata'],'id'))"
        }, source)
        actions["Workbook_" + side]["runAfter"] = {stable: ["Succeeded"]}
    end = actions["Guard_readback"]
    same = ("and(equals(length(body('Registry_before')),length(body('Registry_after'))),"
            "equals(length(union(body('Stable_registry_before'),body('Stable_registry_after'))),length(body('Registry_before'))))")
    end["expression"] = "@and("+end["expression"][1:]+","+same+")"
    end["actions"]["Completed_summary"]["inputs"].update(
        catalogueReadbackCount="@length("+final+")", registryOnlyManifestVersion=1,
        registryOnlyEntries="@body('Registry_remaining')", registryOnlyUnchanged="@"+same)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("definition", "manifest", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    with args.output.open("x") as output:
        json.dump(transform(json.loads(args.definition.read_text()), json.loads(args.manifest.read_text())), output, indent=2)
        output.write("\n")


def checkpoint_registry_only(checkpoint, workbook_uids, catalogue=None):
    """Return eligible locally registered identities from a verified checkpoint."""
    entries = checkpoint.get("registryOnlyEntries", [])
    if not entries:
        return set()
    if checkpoint.get("registryOnlyUnchanged") is not True:
        raise ValueError("registry-only readback required")
    validate({"schemaVersion": checkpoint.get("registryOnlyManifestVersion"), "entries": entries})
    indexed = {entry["documentUID"]: entry for entry in entries}
    if set(indexed) & workbook_uids:
        raise ValueError("overlapping registry-only and source identities")
    if catalogue is not None:
        for uid, entry in indexed.items():
            matches = [row for row in catalogue if row["DocumentUID"] == uid]
            if len(matches) != 1 or matches[0].get("Id") != entry["itemId"]:
                raise ValueError("registry-only item identity mismatch")
            for native, pinned in (("sourceDocumentId", "printedIdentifier"), ("sourceSnapshotRef", "evidenceRef")):
                if matches[0].get(native) != entry[pinned]:
                    raise ValueError("registry-only provenance mismatch")
    return set(indexed)
