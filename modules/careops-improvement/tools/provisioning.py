"""Build offline SharePoint and Teams provisioning plans; never performs I/O."""

from __future__ import annotations

import argparse
import copy
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit


MODULE = Path(__file__).resolve().parents[1]
DEFAULT_SP_SCHEMA = MODULE / "platform/sharepoint/schema.json"
DEFAULT_TEAMS_REQUEST = MODULE / "platform/teams/tab-request.json"
SP_HOST_SUFFIXES = (".sharepoint.com", ".sharepoint.us", ".sharepoint.de", ".sharepoint.cn")
SP_TYPES = {"Text", "Note", "Choice", "DateTime", "Number", "Integer", "Boolean"}
PLACEHOLDERS = {
    "site": "{{SHAREPOINT_SITE_URL}}",
    "team": "{{TEAM_ID}}",
    "channel": "{{CHANNEL_ID}}",
    "list": "{{SHAREPOINT_LIST_URL}}",
}


class ProvisioningError(ValueError):
    """Invalid portable schema or target binding."""


def read_json(path: str | Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvisioningError(f"Cannot read JSON input: {path}") from exc
    if not isinstance(value, dict):
        raise ProvisioningError("JSON input must be an object")
    return value


def _valid_site_url(value: str, *, allow_placeholder: bool = True) -> bool:
    if allow_placeholder and value == PLACEHOLDERS["site"]:
        return True
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and bool(host)
        and parsed.username is None
        and parsed.password is None
        and parsed.port is None
        and any(host.endswith(suffix) and host != suffix[1:] for suffix in SP_HOST_SUFFIXES)
        and not parsed.query
        and not parsed.fragment
    )


def _validate_schema(schema: dict) -> None:
    if schema.get("schema_version") != 1 or not isinstance(schema.get("resources"), list):
        raise ProvisioningError("Unsupported or malformed SharePoint schema")
    if not _valid_site_url(schema.get("site_url", "")):
        raise ProvisioningError("SharePoint site URL must be a parameter or an allowed HTTPS SharePoint host")
    keys: set[str] = set()
    titles: set[str] = set()
    for resource in schema["resources"]:
        if not isinstance(resource, dict):
            raise ProvisioningError("Resources must be objects")
        key, title = resource.get("key"), resource.get("title")
        if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", key):
            raise ProvisioningError("Resource keys must be lowercase portable identifiers")
        if key in keys or not isinstance(title, str) or not title.strip() or title in titles:
            raise ProvisioningError("Resource keys and list/library titles must be unique and nonempty")
        keys.add(key)
        titles.add(title)
        if resource.get("kind") not in {"list", "library"}:
            raise ProvisioningError(f"Unsupported SharePoint resource kind: {key}")
        expected_template = "DocumentLibrary" if resource["kind"] == "library" else "GenericList"
        if resource.get("base_template") != expected_template:
            raise ProvisioningError(f"Base template does not match resource kind: {key}")
        if type(resource.get("enable_versioning")) is not bool or type(resource.get("enable_attachments")) is not bool:
            raise ProvisioningError(f"List/library behavior flags must be explicit booleans: {key}")
        fields = resource.get("fields")
        if not isinstance(fields, list) or not fields:
            raise ProvisioningError(f"Resource has no fields: {key}")
        names: set[str] = set()
        for field in fields:
            if not isinstance(field, dict):
                raise ProvisioningError(f"Field entries must be objects: {key}")
            name = field.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
                raise ProvisioningError(f"Invalid internal field name in {key}: {name!r}")
            if name in names:
                raise ProvisioningError(f"Duplicate field name in {key}: {name}")
            names.add(name)
            if field.get("type") not in SP_TYPES:
                raise ProvisioningError(f"Unsupported SharePoint field type in {key}.{name}")
            source_member = field.get("source_member")
            if not isinstance(source_member, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", source_member):
                raise ProvisioningError(f"Field requires a portable source_member in {key}.{name}")
            display_name = field.get("display_name", name)
            if not isinstance(display_name, str) or not display_name.strip():
                raise ProvisioningError(f"Field display_name must be nonempty text in {key}.{name}")
            for flag in ("required", "indexed", "unique"):
                if type(field.get(flag)) is not bool:
                    raise ProvisioningError(f"{key}.{name} requires an explicit {flag} boolean")
            if field["unique"] and not field["indexed"]:
                raise ProvisioningError(f"Unique field must be indexed: {key}.{name}")
            if field["type"] == "Note" and (field["indexed"] or field["unique"]):
                raise ProvisioningError(f"Note fields cannot be indexed or unique in this profile: {key}.{name}")
            if field["type"] == "Choice":
                choices = field.get("choices")
                if not isinstance(choices, list) or not choices or any(not isinstance(c, str) or not c for c in choices):
                    raise ProvisioningError(f"Choice field requires nonempty choices: {key}.{name}")
                if len(choices) != len(set(choices)):
                    raise ProvisioningError(f"Choice values must be unique: {key}.{name}")
            elif "choices" in field:
                raise ProvisioningError(f"Only Choice fields may declare choices: {key}.{name}")
        for identity in (resource.get("identity_field"), resource.get("source_key_field")):
            if identity not in names:
                raise ProvisioningError(f"Identity field is missing from {key}: {identity}")
        for identity in (resource["identity_field"], resource["source_key_field"]):
            field = next(f for f in fields if f["name"] == identity)
            if not field["unique"] or not field["indexed"]:
                raise ProvisioningError(f"Identity field must be unique and indexed: {key}.{identity}")


def field_xml(field: dict) -> str:
    """Render the supported SharePoint Field CAML shape used by list field add."""
    attrs = {
        "Type": field["type"],
        "Name": field["name"],
        "StaticName": field["name"],
        "DisplayName": field.get("display_name", field["name"]),
        "Required": "TRUE" if field["required"] else "FALSE",
        "Indexed": "TRUE" if field["indexed"] else "FALSE",
        "EnforceUniqueValues": "TRUE" if field["unique"] else "FALSE",
    }
    if field["type"] == "Note":
        attrs.update({"RichText": "FALSE", "AppendOnly": "FALSE"})
    if field["type"] == "DateTime":
        attrs["Format"] = "DateTime"
    rendered = " ".join(f'{key}="{html.escape(str(value), quote=True)}"' for key, value in attrs.items())
    if field["type"] != "Choice":
        return f"<Field {rendered} />"
    choices = "".join(f"<CHOICE>{html.escape(value)}</CHOICE>" for value in field["choices"])
    return f"<Field {rendered}><CHOICES>{choices}</CHOICES></Field>"


def _cli(argv: list[str]) -> dict:
    return {"executable": "m365", "argv": argv, "executed": False}


def _resource_inspect_commands(site_url: str, resource: dict) -> list[dict]:
    return [
        _cli(["spo", "list", "get", "--webUrl", site_url, "--title", resource["title"], "--output", "json"]),
        _cli(["spo", "field", "list", "--webUrl", site_url, "--listTitle", resource["title"], "--output", "json"]),
    ]


def build_sharepoint_plan(schema: dict) -> dict:
    _validate_schema(schema)
    site_url = schema["site_url"]
    resources = []
    for resource in schema["resources"]:
        commands = _resource_inspect_commands(site_url, resource)
        create_args = [
            "spo", "list", "add", "--webUrl", site_url, "--title", resource["title"],
            "--baseTemplate", resource["base_template"],
            "--enableVersioning", "true" if resource["enable_versioning"] else "false",
            "--enableAttachments", "true" if resource["enable_attachments"] else "false",
            "--output", "json",
        ]
        fields = []
        for field in resource["fields"]:
            xml = field_xml(field)
            fields.append({
                "name": field["name"],
                "type": field["type"],
                "source_member": field["source_member"],
                "condition": "create only after exact list readback confirms the field is absent; stop on incompatible existing definition",
                "xml": xml,
                "command": _cli([
                    "spo", "field", "add", "--webUrl", site_url, "--listTitle", resource["title"],
                    "--xml", xml, "--options", "AddToDefaultContentType", "--output", "json",
                ]),
            })
        resources.append({
            "key": resource["key"],
            "title": resource["title"],
            "kind": resource["kind"],
            "inspect_commands": commands,
            "create_list_condition": "create only when exact-title readback returns no list; stop if multiple matches or an incompatible existing list is found",
            "create_list_command": _cli(create_args),
            "fields": fields,
        })
    return {
        "mode": "offline_dry_run",
        "native_calls": 0,
        "credential_access": False,
        "shell_execution": False,
        "site_url": site_url,
        "resources": resources,
    }


def _valid_target_id(value: str, placeholder: str) -> bool:
    return value == placeholder or bool(re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", value
    ))


def _valid_channel_id(value: str) -> bool:
    """Accept Graph GUIDs and native Teams thread IDs without path syntax."""
    return _valid_target_id(value, PLACEHOLDERS["channel"]) or bool(
        re.fullmatch(r"19:[A-Za-z0-9_-]+@thread\.tacv2", value)
    )


def _valid_sharepoint_url(value: str, suffixes: list[str]) -> bool:
    if value == PLACEHOLDERS["list"]:
        return True
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    return (
        parsed.scheme == "https"
        and bool(host)
        and parsed.username is None
        and parsed.password is None
        and parsed.port is None
        and any(host.endswith(suffix) and host != suffix[1:] for suffix in suffixes)
        and not parsed.query
        and not parsed.fragment
    )


def build_teams_request(template: dict, *, team_id: str | None = None,
                        channel_id: str | None = None,
                        sharepoint_list_url: str | None = None) -> dict:
    if template.get("method") != "POST" or not isinstance(template.get("path_template"), str):
        raise ProvisioningError("Invalid Teams Graph request template")
    team_id = team_id or PLACEHOLDERS["team"]
    channel_id = channel_id or PLACEHOLDERS["channel"]
    sharepoint_list_url = sharepoint_list_url or PLACEHOLDERS["list"]
    if not _valid_target_id(team_id, PLACEHOLDERS["team"]):
        raise ProvisioningError("Team ID must be a GUID or the documented placeholder")
    if not _valid_channel_id(channel_id):
        raise ProvisioningError("Channel ID must be a GUID, native Teams thread ID, or documented placeholder")
    suffixes = template.get("allowed_sharepoint_host_suffixes")
    if not isinstance(suffixes, list) or not suffixes or not _valid_sharepoint_url(sharepoint_list_url, suffixes):
        raise ProvisioningError("SharePoint list URL must use HTTPS and an explicitly allowed SharePoint Online host")
    path = template["path_template"].replace(PLACEHOLDERS["team"], quote(team_id, safe="")).replace(
        PLACEHOLDERS["channel"], quote(channel_id, safe="")
    )
    body = copy.deepcopy(template.get("body_template"))
    if not isinstance(body, dict):
        raise ProvisioningError("Teams Graph body template must be an object")
    config = body.get("configuration")
    if not isinstance(config, dict):
        raise ProvisioningError("Teams Graph request requires a tab configuration")
    config["contentUrl"] = sharepoint_list_url
    config["websiteUrl"] = sharepoint_list_url
    return {
        "method": "POST",
        "url": "https://graph.microsoft.com" + path,
        "headers": {"Content-Type": "application/json"},
        "body": body,
        "authorization": "not supplied",
        "executed": False,
    }


def build_inspect_plan(schema: dict) -> dict:
    _validate_schema(schema)
    commands = []
    for resource in schema["resources"]:
        commands.extend(_resource_inspect_commands(schema["site_url"], resource))
    return {
        "mode": "offline_read_only_inspect_plan",
        "native_calls": 0,
        "credential_access": False,
        "shell_execution": False,
        "commands_to_review_or_run_separately": commands,
    }


def _inventory_index(rows, identity):
    if not isinstance(rows, list):
        raise ProvisioningError(f"Inventory requires an array of entries identified by {identity}")
    result = {}
    for row in rows:
        value = row.get(identity) if isinstance(row, dict) else None
        if not isinstance(value, str) or not value.strip() or value.casefold() in result:
            raise ProvisioningError(f"Missing or ambiguous inventory {identity}")
        result[value.casefold()] = row
    return result


def reconcile_lists(schema: dict, inventory: dict) -> dict:
    return _reconcile_resources(schema, inventory, "list")


def _reconcile_resources(schema: dict, inventory: dict, kind: str) -> dict:
    """Compare normalized schema metadata without reading any document content."""
    _validate_schema(schema)
    observed = _inventory_index(inventory.get("resources"), "title")
    additions, conflicts = [], []

    def compare(target, expected, actual, properties):
        for prop in properties:
            value = expected[prop]
            found = actual.get(prop)
            if type(found) is not type(value) or found != value:
                conflicts.append({**target, "property": prop, "expected": value, "observed": found})

    for resource in schema["resources"]:
        if resource["kind"] != kind:
            continue
        target = {kind: resource["title"]}
        actual = observed.get(resource["title"].casefold())
        if actual is None:
            additions.append({**target, "action": f"create_{kind}", "schema_key": resource["key"]})
            continue
        compare(target, resource, actual, ("base_template", "enable_versioning", "enable_attachments"))
        if actual.get("base_template") != resource["base_template"]:
            continue
        fields = _inventory_index(actual.get("fields"), "name")
        for field in resource["fields"]:
            location = {**target, "field": field["name"]}
            existing = fields.get(field["name"].casefold())
            if existing is None:
                additions.append({**location, "action": "add_field", "schema_xml": field_xml(field)})
                continue
            properties = ["type", "required", "indexed", "unique"]
            if field["type"] == "Choice":
                properties.append("choices")
            compare(location, field, existing, properties)
    return {"additions": additions, "incompatibilities": conflicts, "native_calls": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "dry-run", "reconcile-lists", "reconcile-library"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--sharepoint-schema", type=Path, default=DEFAULT_SP_SCHEMA)
        if name.startswith("reconcile-"):
            sub.add_argument("--inventory", required=True, type=Path)
    dry = subparsers.choices["dry-run"]
    dry.add_argument("--teams-request", type=Path, default=DEFAULT_TEAMS_REQUEST)
    dry.add_argument("--team-id")
    dry.add_argument("--channel-id")
    dry.add_argument("--sharepoint-list-url")
    args = parser.parse_args(argv)
    schema = read_json(args.sharepoint_schema)
    if args.command == "reconcile-lists":
        result = reconcile_lists(schema, read_json(args.inventory))
    elif args.command == "reconcile-library":
        result = _reconcile_resources(schema, read_json(args.inventory), "library")
    elif args.command == "inspect":
        result = build_inspect_plan(schema)
    else:
        result = build_sharepoint_plan(schema)
        result["teams_graph_request"] = build_teams_request(
            read_json(args.teams_request), team_id=args.team_id,
            channel_id=args.channel_id,
            sharepoint_list_url=args.sharepoint_list_url,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
