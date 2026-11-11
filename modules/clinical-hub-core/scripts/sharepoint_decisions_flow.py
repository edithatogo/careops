# SPDX-License-Identifier: Apache-2.0
"""Build a stopped, read-only native Power Automate SharePoint Standard flow.

The Microsoft SharePoint *Get items* operation (GetItems) owns native pagination.
No custom HTTP, premium connector, Dataverse, Python runtime or AI is required.
The selected target, view, connector identity, permission and runtime response
must be independently qualified before commissioning.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit
from uuid import UUID

from scripts.correspondence_capture import SHAREPOINT

_NAMES = (
    "ForumRef", "RecordRef", "OccurrenceRef", "Kind", "Status",
    "SourceRef", "SourceRevision", "OwnerRef", "DueDate",
    "CompletionEvidenceRef", "OData__UIVersionString",
)
_NON_NULL = ("ForumRef", "RecordRef", "OccurrenceRef", "Kind", "Status",
             "SourceRef", "SourceRevision", "OData__UIVersionString")
_SYSTEM = ("ID", "@odata.etag")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}\Z")
_CONNECTION = re.compile(r"[A-Za-z0-9_.:/-]{1,256}\Z")
_GUID = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\Z")
_MAX = 10000


def _valid_site(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parts = urlsplit(value)
        return (parts.scheme == "https" and bool(parts.hostname)
                and parts.hostname.endswith(".sharepoint.com")
                and parts.username is None and parts.password is None
                and not parts.query and not parts.fragment and not value.endswith("/"))
    except ValueError:
        return False


def _guid(value: object) -> bool:
    if not isinstance(value, str) or not _GUID.fullmatch(value):
        return False
    try:
        return UUID(value).int != 0
    except ValueError:
        return False


def _fail() -> dict:
    return {
        "type": "Terminate",
        "inputs": {
            "runStatus": "Failed",
            "runError": {
                "code": "DECISIONS_SNAPSHOT_UNQUALIFIED",
                "message": "No valid complete snapshot; inspect native run and exact List/view before retry.",
            },
        },
    }


def _sp_required(field: str) -> str:
    return "not(empty(item()?['" + field + "']))"


def build(config: dict) -> dict:
    """Return source candidate; never import, activate or grant access."""
    if not isinstance(config, dict) or set(config) != {
        "site_url", "list_id", "view_id", "connection_name", "fields", "max_items"
    }:
        raise ValueError("Exact selected SharePoint binding required")
    site, list_id, view_id, conn = (
        config["site_url"], config["list_id"], config["view_id"], config["connection_name"]
    )
    if (not _valid_site(site) or not _guid(list_id) or not _guid(view_id)
            or not isinstance(conn, str) or _CONNECTION.fullmatch(conn) is None
            or type(config["max_items"]) is not int
            or not 2 <= config["max_items"] <= _MAX):
        raise ValueError("Unqualified native site/list/view/connection/limit")
    mapping = config["fields"]
    if (not isinstance(mapping, dict) or set(mapping) != set(_NAMES)
            or any(not isinstance(v, str) or _IDENTIFIER.fullmatch(v) is None
                   for v in mapping.values())
            or len(set(mapping.values())) != len(mapping)
            or any(v.casefold() in {"id", "odata__uiversionstring"} for k, v in mapping.items()
                   if k != "OData__UIVersionString")
            or mapping["OData__UIVersionString"] != "OData__UIVersionString"):
        raise ValueError("Expected complete distinct native internal column mappings")

    # Native Get items auto-pagination must be enabled and tested in the target.
    # Fail at the bound (including exactly bound items); a successful run is not
    # proof of freshness, source authority or an independently complete List.
    limit = config["max_items"]
    get_items = {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "apiId": SHAREPOINT,
                "connectionName": "shared_sharepointonline",
                "operationId": "GetItems",
            },
            "parameters": {
                "dataset": site, "table": list_id,
                "$orderby": "ID asc",
                "view": view_id,
            },
            "retryPolicy": {"type": "none"},
        },
        "runAfter": {"Enabled": ["Succeeded"]},
        "runtimeConfiguration": {
            "paginationPolicy": {"minimumItemCount": limit},
            "secureData": {"properties": ["inputs", "outputs"]},
        },
    }

    # The native projection is independent from the offline Python source
    # admission harness. A dynamic List schema can expose escaped/internal
    # names; all names below must be checked against actual native metadata.
    projected = {name: "@item()?['" + mapping[name] + "']" for name in _NAMES}
    projected["ID"] = "@item()?['ID']"
    projected["@odata.etag"] = "@item()?['@odata.etag']"
    checks = [_sp_required(mapping[name]) for name in _NON_NULL]
    checks += [
        "greater(int(coalesce(item()?['ID'],0)),0)",
        "not(empty(item()?['@odata.etag']))",
    ]
    fail_on_bad_row = {
        "type": "Query",
        "inputs": {
            "from": "@body('Get_items')?['value']",
            "where": "@not(and(" + ",".join(checks) + "))",
        },
        "runAfter": {"Read_complete": ["Succeeded"]},
        "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}},
    }
    complete = {
        "type": "If",
        "expression": (
            "@and(equals(parameters('ReadEnabled'),true),"
            "not(empty(body('Get_items')?['value'])),"
            "less(length(body('Get_items')?['value'])," + str(limit) + "),"
            "empty(body('Get_items')?['@odata.nextLink']),"
            "empty(body('Get_items')?['odata.nextLink']))"
        ),
        "runAfter": {"Get_items": ["Succeeded"]},
        "actions": {},
        "else": {"actions": {"Unqualified": _fail()}},
    }
    # A zero-record List can be a valid empty result. The shape validator uses
    # an explicit null/type check instead of nonempty().
    complete["expression"] = complete["expression"].replace(
        "not(empty(body('Get_items')?['value']))",
        "equals(type(body('Get_items')?['value']),'Array')"
    )

    actions = {
        "Enabled": {
            "type": "If",
            "expression": "@equals(parameters('ReadEnabled'),true)",
            "actions": {},
            "else": {"actions": {"Disabled": _fail()}},
        },
        "Get_items": get_items,
        "Read_complete": complete,
        "Reject_invalid_rows": fail_on_bad_row,
        "Require_valid_rows": {
            "type": "If",
            "expression": "@equals(length(body('Reject_invalid_rows')),0)",
            "runAfter": {"Reject_invalid_rows": ["Succeeded"]},
            "actions": {
                "Project_governance_columns": {
                    "type": "Select",
                    "inputs": {"from": "@body('Get_items')?['value']", "select": projected},
                    "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}},
                },
                "Review_only": {
                    "type": "Compose",
                    "inputs": {
                        "state": "read_candidate",
                        "native_write_authorised": False,
                        "source_authenticated": False,
                        "snapshot_freshness_verified": False,
                        "governance_authority_verified": False,
                        "list_id": list_id,
                        "rows": "@body('Project_governance_columns')",
                    },
                    "runAfter": {"Project_governance_columns": ["Succeeded"]},
                    "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}},
                },
            },
            "else": {"actions": {"Rejected_rows": _fail()}},
        },
    }
    definition = {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "$authentication": {"type": "SecureObject", "defaultValue": {}},
            "$connections": {"type": "Object", "defaultValue": {}},
            "ReadEnabled": {"type": "Bool", "defaultValue": False},
        },
        "triggers": {
            "manual": {
                "type": "Request", "kind": "Button",
                "inputs": {"schema": {"type": "object", "properties": {}}},
                "runtimeConfiguration": {
                    "concurrency": {"runs": 1},
                    "secureData": {"properties": ["inputs", "outputs"]},
                },
            }
        },
        "actions": actions,
        "outputs": {},
    }
    return {
        "properties": {
            "displayName": "CareOps Decisions | Read-only selected register",
            "state": "Stopped",
            "definition": definition,
            "connectionReferences": {
                "shared_sharepointonline": {
                    "connectionName": conn,
                    "source": "Embedded",
                    "id": SHAREPOINT,
                }
            },
        },
        "preparation": {
            "nativeSaved": False,
            "activationHeld": True,
            "requires": [
                "Exact list/view/column schema and accepted connector action metadata",
                "Qualified delegated connector and site/list read rights",
                "Proof native GetItems auto-pagination and response shape",
                "Complete parent solution pack and exact-head security checks",
                "Bounded fictional two-forum native runs and recovery",
            ],
        },
    }
