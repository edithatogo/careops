"""Build stopped SharePoint event capture and reconciliation flow sources.

SPDX-License-Identifier: Apache-2.0
The emitted definitions contain unresolved environment placeholders and are not
deployable until exact site/list/connection bindings and native qualification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SP = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
WORKFLOW_SCHEMA = "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#"
EVENT_FIELDS = ("SourceKey", "EventId", "InitiativeId", "EventType", "EffectiveAt", "ObservedAt",
                "SourceSystem", "SourceRecordId", "SourceRevision", "ActorRef", "Outcome", "EvidenceRef")
VERIFY_FIELDS = ("SourceKey", "EventId", "InitiativeId", "EventType", "EffectiveAt",
                 "SourceSystem", "SourceRecordId", "SourceRevision")


def _connection_ref() -> dict[str, Any]:
    return {"shared_sharepointonline": {
        "connectionName": "__ENV_CAREOPS_SHAREPOINT_CONNECTION_REFERENCE__",
        "source": "Embedded", "id": SP,
    }}


def _base(name: str, *, triggers: dict[str, Any], actions: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    definition = {
        "$schema": WORKFLOW_SCHEMA,
        "contentVersion": "1.0.0.0",
        "parameters": {"$authentication": {"type": "SecureObject", "defaultValue": {}},
                       "$connections": {"type": "Object", "defaultValue": {}}, **params},
        "triggers": triggers, "actions": actions, "outputs": {},
    }
    # Keep custom preparation notes out of the Power Automate upload payload.
    return {"properties": {"displayName": name, "state": "Stopped", "definition": definition,
                           "connectionReferences": _connection_ref()}}


def preparation_receipt() -> dict[str, Any]:
    """Companion handoff metadata; this document is not a flow upload payload."""
    return {
        "kind": "careops-stopped-flow-preparation-receipt-v1",
        "nativeSaved": False,
        "activationHeld": True,
        "environmentBindingsResolved": False,
        "requires": ["Exact SharePoint site and list IDs", "Existing qualified SharePoint connection reference",
                     "Event SourceKey unique-value constraint", "Native save/readback and fictional runtime proof"],
        "flows": {
            "event-capture.flow.json": {
                "loopPrevention": "Writes only to the separate events list; initiative register is never modified.",
                "triggerSemantics": "Periodic SharePoint connector poll with stable SourceKey deduplication.",
            },
            "source-reconciliation.flow.json": {
                "summaryRetention": "Run history only; no durable source-health ledger/list is provisioned.",
                "scanLimit": 5000,
            },
        },
    }


def _params() -> dict[str, Any]:
    return {
        "SiteUrl": {"type": "String", "defaultValue": "__ENV_CAREOPS_SHAREPOINT_SITE_URL__"},
        "InitiativeListId": {"type": "String", "defaultValue": "__ENV_CAREOPS_INITIATIVE_REGISTER_LIST_ID__"},
        "EventListId": {"type": "String", "defaultValue": "__ENV_CAREOPS_INITIATIVE_EVENTS_LIST_ID__"},
    }


def _http(method: str, uri: str, *, after: dict[str, list[str]] | None = None,
          body: Any = None) -> dict[str, Any]:
    headers = {"Accept": "application/json;odata=nometadata"}
    parameters: dict[str, Any] = {"dataset": "@parameters('SiteUrl')", "parameters/method": method,
                                 "parameters/uri": uri, "parameters/headers": headers}
    if body is not None:
        headers["Content-Type"] = "application/json;odata=nometadata"
        parameters["parameters/body"] = body
    return {"type": "OpenApiConnection", "inputs": {
        "host": {"apiId": SP, "connectionName": "shared_sharepointonline", "operationId": "HttpRequest"},
        "parameters": parameters, "retryPolicy": {"type": "None"}}, "runAfter": after or {},
        "runtimeConfiguration": {"secureData": {"properties": ["inputs", "outputs"]}}}


def _compose(value: Any, after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return {"type": "Compose", "inputs": value, "runAfter": after or {}}


def _terminate(code: str, message: str, after: dict[str, list[str]] | None = None) -> dict[str, Any]:
    return {"type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {"code": code, "message": message}},
            "runAfter": after or {}}


def _event_capture_actions(source: str, *, deferred_failure: bool = False) -> dict[str, Any]:
    """Create an idempotent event snapshot from one trigger or reconciliation row."""
    source_id = f"{source}?['ID']"
    revision = f"{source}?['Revision']"
    initiative_id = f"{source}?['InitiativeId']"
    modified = f"{source}?['Modified']"
    title = f"{source}?['Title']"
    def fail(code: str, message: str) -> dict[str, Any]:
        if deferred_failure:
            return {"type": "SetVariable", "inputs": {"name": "ReconciliationIssue", "value": f"{code}: {message}"}, "runAfter": {}}
        return _terminate(code, message)
    root = "@concat('_api/web/lists(guid''',parameters('EventListId'),''')/items')"
    key_value = "@outputs('Event_key')"
    lookup_uri = "@concat(" + root[1:] + ", '?$select=" + ",".join(VERIFY_FIELDS) + "&$filter=SourceKey%20eq%20%27',uriComponent(outputs('Event_key')),'%27&$top=2')"
    actions: dict[str, Any] = {
        "Validate_source": {"type": "If", "expression":
            f"@and(not(empty(string({source_id}))),not(empty({initiative_id})),greater(int(coalesce({revision},0)),0),not(empty({modified})))",
            "runAfter": {}, "actions": {}, "else": {"actions": {"Invalid_source": fail(
                "SOURCE_IDENTITY_INCOMPLETE", "Source item requires ID, InitiativeId, positive Revision and Modified timestamp.")}}},
        "Event_key": _compose(f"@concat('spitem:',parameters('InitiativeListId'),':',string({source_id}),':r',string({revision}))"),
        "Event_snapshot": _compose({
            "SourceKey": key_value, "EventId": key_value, "InitiativeId": f"@string({initiative_id})",
            "EventType": "initiative_revision_observed", "EffectiveAt": f"@{modified}", "ObservedAt": "@utcNow()",
            "SourceSystem": "SharePoint", "SourceRecordId": f"@string({source_id})",
            "SourceRevision": f"@string({revision})", "ActorRef": "", "Outcome": "source_revision_captured",
            "EvidenceRef": "",
        }, {"Event_key": ["Succeeded"]}),
        "Lookup_event": _http("GET", lookup_uri, after={"Event_snapshot": ["Succeeded"]}),
        "Route_event": {"type": "If", "expression": "@equals(length(body('Lookup_event')?['value']),0)",
            "runAfter": {"Lookup_event": ["Succeeded"]}, "actions": {}, "else": {"actions": {}}},
    }
    event_body = "@string(outputs('Event_snapshot'))"
    def exact_match(read_action: str) -> str:
        existing = f"first(body('{read_action}')?['value'])"
        comparisons = []
        for field in VERIFY_FIELDS:
            if field == "EffectiveAt":
                # SharePoint may serialize the same UTC instant with a different
                # offset/precision. Compare instants while keeping every other
                # immutable source assertion byte-for-byte.
                comparisons.append(
                    f"equals(ticks({existing}?['{field}']),ticks(outputs('Event_snapshot')?['{field}']))"
                )
            else:
                comparisons.append(
                    f"equals({existing}?['{field}'],outputs('Event_snapshot')?['{field}'])"
                )
        return f"@and(equals(length(body('{read_action}')?['value']),1)," + ",".join(comparisons) + ")"

    exact_existing = exact_match("Lookup_event")
    exact_after = exact_match("Read_after_create")
    exact_failed = exact_match("Reconcile_failed_create")
    create_actions = {
        "Create_event": _http("POST", root, body=event_body),
        "Read_after_create": _http("GET", lookup_uri, after={"Create_event": ["Succeeded"]}),
        "Verify_after_create": {"type": "If", "expression": exact_after, "runAfter": {"Read_after_create": ["Succeeded"]},
            "actions": {"Captured": _compose("Append-only event created and read back exactly.")},
            "else": {"actions": {"Readback_mismatch": fail("EVENT_READBACK_MISMATCH", "Created event did not match its immutable source revision.")}}},
        "Reconcile_failed_create": _http("GET", lookup_uri, after={"Create_event": ["Failed", "TimedOut"]}),
        "Verify_failed_create": {"type": "If", "expression": exact_failed,
            "runAfter": {"Reconcile_failed_create": ["Succeeded"]},
            "actions": {"Create_reconciled": _compose("A prior create completed; exact event was recovered by stable SourceKey.")},
            "else": {"actions": {"Create_uncertain": fail("EVENT_CREATE_UNCERTAIN", "Inspect by SourceKey before any retry; no blind second create.")}}},
    }
    actions["Route_event"]["actions"] = {"Create_missing_event": {"type": "Scope", "runAfter": {}, "actions": create_actions}}
    actions["Route_event"]["else"]["actions"] = {
        "Verify_existing": {"type": "If", "expression": exact_existing, "runAfter": {},
            "actions": {"Already_captured": _compose("Exact SourceKey and source revision already captured; no write.")},
            "else": {"actions": {"Existing_conflict": fail("EVENT_KEY_CONFLICT", "SourceKey is duplicated or content differs; preserve rows for reconciliation.")}}}
    }
    # Keep the entire capture chain in the successful branch. In reconciliation
    # mode an invalid row sets the issue flag and exits this branch without any
    # SharePoint event write; in trigger mode the else branch terminates failed.
    validation = actions.pop("Validate_source")
    validation["actions"] = actions
    return {"Validate_source": validation}


def build_event_capture() -> dict[str, Any]:
    """Stopped, loop-safe periodic capture using the qualified SharePoint REST read pattern."""
    trigger = {"Capture_poll": {
        "type": "Recurrence", "recurrence": {"frequency": "Minute", "interval": 1},
        "conditions": [{"expression": "@equals(parameters('CaptureEnabled'),true)"}],
        "runtimeConfiguration": {"concurrency": {"runs": 1}},
    }}
    actions = {
        "Initialise_issue": {"type": "InitializeVariable", "inputs": {"variables": [
            {"name": "ReconciliationIssue", "type": "String", "value": ""}]}, "runAfter": {}},
        "Read_initiatives": _http("GET", "@concat('_api/web/lists(guid''',parameters('InitiativeListId'),''')/items?$select=ID,InitiativeId,Title,Revision,Modified&$top=5000')", after={"Initialise_issue": ["Succeeded"]}),
        "Require_complete_page": {"type": "If", "expression": "@and(not(equals(body('Read_initiatives')?['value'],null)),empty(body('Read_initiatives')?['@odata.nextLink']),empty(body('Read_initiatives')?['odata.nextLink']))",
            "runAfter": {"Read_initiatives": ["Succeeded"]}, "actions": {},
            "else": {"actions": {"Page_incomplete": _terminate("INITIATIVE_PAGE_INCOMPLETE", "Source scan exceeded 5000 items; no complete capture is reported.")}}},
        "Capture_initiatives": {"type": "Foreach", "foreach": "@body('Read_initiatives')?['value']",
            "runAfter": {"Require_complete_page": ["Succeeded"]},
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "actions": {"Continue_if_clean": {"type": "If", "expression": "@empty(variables('ReconciliationIssue'))",
                "runAfter": {}, "actions": _event_capture_actions("items('Capture_initiatives')", deferred_failure=True),
                "else": {"actions": {"Skip_after_issue": _compose("Prior event failed; remaining writes held.")}}}}},
        "Require_clean_capture": {"type": "If", "expression": "@empty(variables('ReconciliationIssue'))",
            "runAfter": {"Capture_initiatives": ["Succeeded"]}, "actions": {},
            "else": {"actions": {"Capture_failed": _terminate("CAPTURE_EVENT_EXCEPTION", "Inspect event conflict before retry.")}}},
    }
    params = _params()
    params["CaptureEnabled"] = {"type": "Bool", "defaultValue": False}
    flow = _base("CareOps | Capture initiative revision event", triggers=trigger,
                 actions=actions, params=params)
    return flow


def build_reconciliation() -> dict[str, Any]:
    """Stopped daily reconciliation to recover missed triggers and expose source health."""
    trigger = {"Daily_reconciliation": {"type": "Recurrence", "recurrence": {
        "frequency": "Day", "interval": 1, "timeZone": "E. Australia Standard Time"},
        "runtimeConfiguration": {"concurrency": {"runs": 1}}}}
    actions: dict[str, Any] = {
        "Reconciliation_enabled": {"type": "If", "expression": "@equals(parameters('ReconciliationEnabled'),true)",
            "runAfter": {}, "actions": {}, "else": {"actions": {"Disabled": _terminate(
                "RECONCILIATION_DISABLED", "Set the exact environment binding and enable only after native qualification.")}}},
        "Initialise_issue": {"type": "InitializeVariable", "inputs": {"variables": [
            {"name": "ReconciliationIssue", "type": "String", "value": ""}]},
            "runAfter": {"Reconciliation_enabled": ["Succeeded"]}},
        "Read_initiatives": _http("GET", "@concat('_api/web/lists(guid''',parameters('InitiativeListId'),''')/items?$select=ID,InitiativeId,Title,Revision,Modified&$top=5000')",
                                   after={"Initialise_issue": ["Succeeded"]}),
        "Require_complete_page": {"type": "If", "expression": "@and(not(equals(body('Read_initiatives')?['value'],null)),empty(body('Read_initiatives')?['@odata.nextLink']),empty(body('Read_initiatives')?['odata.nextLink']))",
            "runAfter": {"Read_initiatives": ["Succeeded"]}, "actions": {},
            "else": {"actions": {"Page_incomplete": _terminate("INITIATIVE_PAGE_INCOMPLETE", "List exceeds the bounded 5000 item scan; no complete reconciliation is reported.")}}},
        "Reconcile_initiatives": {"type": "Foreach", "foreach": "@body('Read_initiatives')?['value']",
            "runAfter": {"Require_complete_page": ["Succeeded"]},
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "actions": {"Continue_if_clean": {"type": "If", "expression": "@empty(variables('ReconciliationIssue'))",
                "runAfter": {}, "actions": _event_capture_actions("items('Reconcile_initiatives')", deferred_failure=True),
                "else": {"actions": {"Skip_after_issue": _compose("Prior reconciliation item failed; remaining writes held.")}}}}},
        "Require_clean_reconciliation": {"type": "If", "expression": "@empty(variables('ReconciliationIssue'))",
            "runAfter": {"Reconcile_initiatives": ["Succeeded"]}, "actions": {},
            "else": {"actions": {"Reconciliation_failed": _terminate("RECONCILIATION_EVENT_EXCEPTION", "Inspect the stable SourceKey and event row; no blind create retry.")}}},
        "Health_summary": _compose({"status": "reconciliation_completed", "asOfUtc": "@utcNow()",
            "runId": "@workflow()?['run']?['name']", "initiativesScanned": "@length(body('Read_initiatives')?['value'])",
            "sourceListComplete": True, "eventListWrites": "Append only; existing stable SourceKeys are read and compared."},
            {"Require_clean_reconciliation": ["Succeeded"]}),
    }
    params = _params()
    params["ReconciliationEnabled"] = {"type": "Bool", "defaultValue": False}
    flow = _base("CareOps | Daily source reconciliation and health", triggers=trigger, actions=actions, params=params)
    return flow


def process_mining_contract() -> dict[str, Any]:
    """Portable event-log projection contract; not an XES exporter or mining engine."""
    return {
        "contract": "careops-improvement-process-event-v1",
        "source": "initiative-events SharePoint list or CSV export by SourceKey",
        "case_id": "InitiativeId",
        "activity": "EventType",
        "event_time": "EffectiveAt",
        "observation_time": "ObservedAt",
        "event_identity": "SourceKey",
        "source_record_id": "SourceRecordId",
        "source_revision": "SourceRevision",
        "optional_resource": "ActorRef",
        "additional_context": ["SourceSystem", "Outcome", "EvidenceRef"],
        "rules": ["Use EffectiveAt for process ordering and preserve ObservedAt as capture provenance.",
                  "Do not count missing events as zero activity; report source health and incomplete scans.",
                  "Do not turn initiative state snapshots into inferred approvals or task completions.",
                  "Retain stable event identity and source revision when exporting; do not overwrite prior events."],
        "format": "CSV rows are directly usable as tabular event-log input; timestamp normalization and case/activity mapping remain explicit per mining tool.",
    }


def build_all() -> dict[str, dict[str, Any]]:
    return {"event-capture.flow.json": build_event_capture(),
            "source-reconciliation.flow.json": build_reconciliation(),
            "process-mining-contract.json": process_mining_contract(),
            "preparation-receipt.json": preparation_receipt()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "platform" / "automate" / "definitions")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, document in build_all().items():
        destination = args.output_dir / name
        with destination.open("w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    print(f"Prepared {len(build_all())} stopped flow/contract definitions in {args.output_dir}")


if __name__ == "__main__":
    main()
