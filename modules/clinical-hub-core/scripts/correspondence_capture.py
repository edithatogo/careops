"""Prepare a stopped standard-connector capture candidate; never deploy or run it.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

OUTLOOK = "/providers/Microsoft.PowerApps/apis/shared_office365"
SHAREPOINT = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
GUID = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}")


def classify(message: dict, *, sender: str, start: str, exact: int = 0,
             conversation_matches: int = 0, title_matches: int = 0) -> str:
    """Offline contract oracle. This is not a hosted ingestion runtime."""
    try:
        received = datetime.fromisoformat(message["receivedDateTime"].replace("Z", "+00:00"))
        boundary = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if received.tzinfo is None or boundary.tzinfo is None:
            return "NeedsReview"
    except (KeyError, ValueError, AttributeError):
        return "NeedsReview"
    if str(message.get("from", "")).strip().lower() != sender.lower() or received < boundary:
        return "Excluded"
    key = str(message.get("internetMessageId") or "").strip()
    if not 1 <= len(key) <= 255 or not message.get("id") or not 1 <= len(str(message.get("subject") or "").strip()) <= 255:
        return "NeedsReview"
    if exact > 1:
        return "NeedsReview"
    if exact == 1:
        return "AlreadyRegistered"
    if conversation_matches or title_matches:
        return "NeedsReview"
    return "RegisterForReview"


def _q(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def build(config: dict[str, Any]) -> dict[str, Any]:
    """Compile private bindings or fictional fixtures to a held-off definition."""
    site = config["site_url"]
    receipts_site = config.get("receipts_site_url", site)
    u = urlparse(receipts_site)
    if u.scheme != "https" or not u.hostname or not u.hostname.endswith(".sharepoint.com") or u.query or u.fragment or u.username:
        raise ValueError("Expected an exact HTTPS receipts site")
    u = urlparse(site)
    if u.scheme != "https" or not u.hostname or not u.hostname.endswith(".sharepoint.com") or u.query or u.fragment or u.username:
        raise ValueError("Expected an exact HTTPS SharePoint site")
    for name in ("register_list_id", "receipts_list_id"):
        if not isinstance(config.get(name), str) or not GUID.fullmatch(config[name]):
            raise ValueError("List GUID required")
    if config["register_list_id"] == config["receipts_list_id"]:
        raise ValueError("Technical receipts must not be the business register")
    sender = config["sender"].strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+", sender):
        raise ValueError("Exact sender required")
    if not config.get("outlook_connection") or not config.get("sharepoint_connection"):
        raise ValueError("Existing explicit connection bindings required")

    def compose(value: Any, after: dict | None = None) -> dict:
        return {"type": "Compose", "inputs": value, "runAfter": after or {}}

    def sp(method: str, uri: str, body_action: str | None = None, after: dict | None = None, *, dataset: str = site) -> dict:
        params: dict[str, Any] = {"dataset": dataset, "parameters/method": method,
                                 "parameters/uri": uri,
                                 "parameters/headers": {"Accept": "application/json;odata=nometadata"}}
        if body_action:
            params["parameters/headers"]["Content-Type"] = "application/json;odata=nometadata"
            params["parameters/body"] = f"@string(outputs('{body_action}'))"
        return {"type": "OpenApiConnection", "inputs": {
            "host": {"apiId": SHAREPOINT, "connectionName": "shared_sharepointonline", "operationId": "HttpRequest"},
            "parameters": params, "retryPolicy": {"type": "none"}},
            "runAfter": after or {}, "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}}}

    reg = f"_api/web/lists(guid'{config['register_list_id']}')/items"
    receipts = f"_api/web/lists(guid'{config['receipts_list_id']}')/items"

    def lookup(field: str, expression: str, after: dict | None = None) -> dict:
        # Escape OData literals before URL encoding; never concatenate raw mail.
        escaped = f"uriComponent(replace({expression},decodeUriComponent('%27'),decodeUriComponent('%27%27')))"
        uri = f"@concat({_q(reg + '?$filter=' + field + ' eq ')},decodeUriComponent('%27'),{escaped},decodeUriComponent('%27'),{_q('&$top=2&$select=Id,SourceMessageKey,SourceMessageId')})"
        return sp("GET", uri, after=after)

    receipt_number = 0

    def receipt(state: str, record_id: Any = None, code: str = "") -> dict:
        nonlocal receipt_number
        receipt_number += 1
        body_name, save_name = f"Receipt_body_{receipt_number}", f"Save_receipt_{receipt_number}"
        body = {"Title": "@workflow()?['run']?['name']", "MessageKey": "@outputs('Message_key')",
                "State": state, "SourceMessageId": "@coalesce(triggerBody()?['id'],'')",
                "ConversationID": "@coalesce(triggerBody()?['conversationId'],'')",
                "RegisterItemId": record_id, "ErrorCode": code,
                "ReceivedUtc": "@triggerBody()?['receivedDateTime']"}
        return {body_name: compose(body), save_name: sp("POST", receipts, body_name, {body_name: ["Succeeded"]}, dataset=receipts_site)}

    def review(code: str) -> dict:
        return receipt("NeedsReview", code=code)

    reconcile = lookup("SourceMessageKey", "outputs('Message_key')", {"Create_register": ["Failed", "TimedOut"]})
    create_actions = {
        "Register_body": compose({"Title": "@trim(triggerBody()?['subject'])", "DateRecd": "@triggerBody()?['receivedDateTime']",
                                  "Recdby": "@triggerBody()?['from']", "ConversationID": "@coalesce(triggerBody()?['conversationId'],'')",
                                  "LatestEmailDate": "@triggerBody()?['receivedDateTime']", "SourceMessageKey": "@outputs('Message_key')",
                                  "SourceMessageId": "@triggerBody()?['id']", "SavedEmail": "@body('Read_source')?['webLink']", "CaptureState": "NeedsReview"}),
        "Create_register": sp("POST", reg, "Register_body", {"Register_body": ["Succeeded"]}),
        "Created": {"type": "Scope", "runAfter": {"Create_register": ["Succeeded"]},
                    "actions": receipt("Registered", "@body('Create_register')?['Id']")},
        "Reconcile_create": reconcile,
        "Reconciled": {"type": "If", "expression": "@and(equals(length(body('Reconcile_create')?['value']),1),equals(base64(coalesce(first(body('Reconcile_create')?['value'])?['SourceMessageKey'],'')),base64(outputs('Message_key'))),equals(coalesce(first(body('Reconcile_create')?['value'])?['SourceMessageId'],''),triggerBody()?['id']))",
                       "runAfter": {"Reconcile_create": ["Succeeded"]},
                       "actions": receipt("Registered", "@first(body('Reconcile_create')?['value'])?['Id']", "CREATE_RECONCILED"),
                       "else": {"actions": receipt("Uncertain", code="CREATE_UNCERTAIN_NO_RETRY")}},
    }
    matching = {
        "Find_conversation": lookup("ConversationID", "coalesce(triggerBody()?['conversationId'],'')"),
        "Find_title": lookup("Title", "trim(triggerBody()?['subject'])", {"Find_conversation": ["Succeeded"]}),
        "Possible_existing_matter": {"type": "If", "runAfter": {"Find_title": ["Succeeded"]},
                                    "expression": "@or(and(not(empty(triggerBody()?['conversationId'])),greater(length(body('Find_conversation')?['value']),0)),greater(length(body('Find_title')?['value']),0))",
                                    "actions": review("MATCH_REVIEW_REQUIRED"), "else": {"actions": create_actions}},
    }
    try_actions = {
        "Read_source": {"type": "OpenApiConnection", "inputs": {
            "host": {"apiId": OUTLOOK, "connectionName": "shared_office365", "operationId": "HttpRequest"},
            "parameters": {"Method": "GET", "Uri": "@concat('https://graph.microsoft.com/v1.0/me/messages/',uriComponent(triggerBody()?['id']),'?$select=id,internetMessageId,webLink')"},
            "retryPolicy": {"type": "none"}}, "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}}},
        "Find_message": lookup("SourceMessageKey", "outputs('Message_key')", {"Read_source": ["Succeeded"]}),
        "Exact_message_exists": {"type": "If", "runAfter": {"Find_message": ["Succeeded"]},
                                 "expression": "@greater(length(body('Find_message')?['value']),0)",
                                 "actions": {"Unique_match": {"type": "If", "expression": "@and(equals(length(body('Find_message')?['value']),1),equals(base64(coalesce(first(body('Find_message')?['value'])?['SourceMessageKey'],'')),base64(outputs('Message_key'))))",
                                     "actions": receipt("AlreadyRegistered", "@first(body('Find_message')?['value'])?['Id']"),
                                     "else": {"actions": review("SOURCE_KEY_COLLISION_OR_DUPLICATE")}}},
                                 "else": {"actions": matching}},
    }
    # Fail closed if the connector's runtime output shape or source identity differs.
    source_action = try_actions.pop("Read_source")
    try_actions["Find_message"]["runAfter"] = {}
    try_actions = {
        "Read_source": source_action,
        "Source_verified": {"type": "If", "runAfter": {"Read_source": ["Succeeded"]},
            "expression": "@and(equals(body('Read_source')?['id'],triggerBody()?['id']),equals(trim(coalesce(body('Read_source')?['internetMessageId'],'')),outputs('Message_key')),or(startsWith(coalesce(body('Read_source')?['webLink'],''),'https://outlook.office.com/'),startsWith(coalesce(body('Read_source')?['webLink'],''),'https://outlook.office365.com/')))",
            "actions": try_actions, "else": {"actions": review("SOURCE_IDENTITY_OR_LINK_UNVERIFIED")}},
    }
    processing = {
        "Try_capture": {"type": "Scope", "actions": try_actions},
        "Processing_failure": {"type": "Scope", "runAfter": {"Try_capture": ["Failed", "TimedOut"]},
                               "actions": {"Fail_visible": {"type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {"code": "CAPTURE_UNRESOLVED", "message": "Inspect existing register/receipt by source key before recovery; never replay a create blindly."}}}}},
    }
    actions = {
        "Message_key": compose("@trim(coalesce(triggerBody()?['internetMessageId'],''))"),
        "Eligible_message": {"type": "If", "runAfter": {"Message_key": ["Succeeded"]},
            "expression": f"@and(equals(toLower(trim(coalesce(triggerBody()?['from'],''))),{_q(sender)}),greaterOrEquals(ticks(triggerBody()?['receivedDateTime']),ticks(parameters('CaptureStartUtc'))))",
            "actions": {"Valid_identity": {"type": "If",
                "expression": "@and(not(empty(outputs('Message_key'))),lessOrEquals(length(outputs('Message_key')),255),not(empty(triggerBody()?['id'])),not(empty(trim(coalesce(triggerBody()?['subject'],'')))),lessOrEquals(length(trim(coalesce(triggerBody()?['subject'],''))),255))",
                "actions": processing, "else": {"actions": review("MISSING_OR_LONG_IDENTITY")}}},
            "else": {"actions": {"Excluded": compose("Outside selected sender/start boundary")}}},
    }
    definition = {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0", "parameters": {"$authentication": {"type": "SecureObject", "defaultValue": {}},
        "$connections": {"type": "Object", "defaultValue": {}}, "CaptureEnabled": {"type": "Bool", "defaultValue": False},
        "CaptureStartUtc": {"type": "String", "defaultValue": "2100-01-01T00:00:00Z"}},
        "triggers": {"New_selected_email": {"type": "OpenApiConnection", "recurrence": {"frequency": "Minute", "interval": 3}, "splitOn": "@triggerOutputs()?['body/value']",
            "inputs": {"host": {"apiId": OUTLOOK, "connectionName": "shared_office365", "operationId": "OnNewEmailV3"},
                "parameters": {"folderPath": config.get("folder", "Inbox"), "from": sender, "includeAttachments": False},
                "retryPolicy": {"type": "none"}}, "conditions": [{"expression": "@equals(parameters('CaptureEnabled'),true)"}],
            "runtimeConfiguration": {"concurrency": {"runs": 1}, "secureData": {"properties": ["inputs", "outputs"]}}}},
        "actions": actions, "outputs": {}}
    refs = {"shared_office365": {"connectionName": config["outlook_connection"], "source": "Embedded", "id": OUTLOOK},
            "shared_sharepointonline": {"connectionName": config["sharepoint_connection"], "source": "Embedded", "id": SHAREPOINT}}
    return {"properties": {"displayName": "Executive correspondence | Capture for review", "state": "Stopped",
                           "definition": definition, "connectionReferences": refs},
            "preparation": {"nativeSaved": False, "activationHeld": True,
                "requires": ["Qualified SharePoint embedded connection", "Unique SourceMessageKey and new capture columns",
                             "Technical receipts schema", "Native definition validation and fictional runtime qualification",
                             "Explicit start boundary and activation selection"]}}


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bindings", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    with args.output.open("x") as stream:
        json.dump(build(json.loads(args.bindings.read_text())), stream, indent=2)
        stream.write("\n")
