"""Focused offline contract tests for the stopped SharePoint flow candidates.

These checks do not qualify a saved or running Power Automate flow.

SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_flows import (  # noqa: E402
    EVENT_FIELDS,
    VERIFY_FIELDS,
    _event_capture_actions,
    build_all,
    build_event_capture,
    build_reconciliation,
)


class StoppedFlowTests(unittest.TestCase):
    def test_upload_payloads_are_stopped_and_custom_notes_are_separate(self):
        artifacts = build_all()
        receipt = artifacts["preparation-receipt.json"]
        self.assertFalse(receipt["nativeSaved"])
        self.assertTrue(receipt["activationHeld"])
        self.assertFalse(receipt["environmentBindingsResolved"])
        for filename in ("event-capture.flow.json", "source-reconciliation.flow.json"):
            props = artifacts[filename]["properties"]
            self.assertEqual(props["state"], "Stopped")
            self.assertNotIn("preparation", props)
            self.assertEqual(set(props), {"displayName", "state", "definition", "connectionReferences"})
            self.assertIn("__ENV_", json.dumps(props))
        self.assertIn("Run history only", receipt["flows"]["source-reconciliation.flow.json"]["summaryRetention"])

    def test_event_capture_uses_disabled_periodic_poll_and_separate_append_only_target(self):
        flow = build_event_capture()["properties"]
        definition = flow["definition"]
        trigger = definition["triggers"]["Capture_poll"]
        self.assertEqual(trigger["type"], "Recurrence")
        self.assertEqual(trigger["recurrence"], {"frequency": "Minute", "interval": 1})
        self.assertEqual(trigger["conditions"], [{"expression": "@equals(parameters('CaptureEnabled'),true)"}])
        self.assertFalse(definition["parameters"]["CaptureEnabled"]["defaultValue"])
        self.assertEqual(trigger["runtimeConfiguration"]["concurrency"]["runs"], 1)
        actions = definition["actions"]
        self.assertEqual(actions["Read_initiatives"]["inputs"]["host"]["operationId"], "HttpRequest")
        self.assertEqual(actions["Capture_initiatives"]["foreach"], "@body('Read_initiatives')?['value']")
        text = json.dumps(definition)
        self.assertIn("parameters('EventListId')", text)
        self.assertIn("parameters('InitiativeListId')", text)
        self.assertIn("loopPrevention", json.dumps(build_all()["preparation-receipt.json"]))

    def test_event_identity_is_revision_stable_and_separates_effective_from_observed(self):
        actions = build_event_capture()["properties"]["definition"]["actions"]
        nested = actions["Capture_initiatives"]["actions"]["Continue_if_clean"]["actions"]["Validate_source"]["actions"]
        key = nested["Event_key"]["inputs"]
        self.assertIn("InitiativeListId", key)
        self.assertIn("['ID']", key)
        self.assertIn("['Revision']", key)
        snapshot = nested["Event_snapshot"]["inputs"]
        self.assertEqual(tuple(snapshot), EVENT_FIELDS)
        self.assertEqual(snapshot["EffectiveAt"], "@items('Capture_initiatives')?['Modified']")
        self.assertEqual(snapshot["ObservedAt"], "@utcNow()")
        self.assertNotEqual(snapshot["EffectiveAt"], snapshot["ObservedAt"])
        self.assertEqual(snapshot["SourceKey"], "@outputs('Event_key')")
        self.assertEqual(snapshot["EventId"], "@outputs('Event_key')")
        self.assertIn("Revision", snapshot["SourceRevision"])

    def test_effective_timestamp_comparison_normalizes_instants_only(self):
        actions = build_event_capture()["properties"]["definition"]["actions"]
        nested = actions["Capture_initiatives"]["actions"]["Continue_if_clean"]["actions"]["Validate_source"]["actions"]
        route = nested["Route_event"]
        expressions = [route["else"]["actions"]["Verify_existing"]["expression"]]
        create = route["actions"]["Create_missing_event"]["actions"]
        expressions.extend([
            create["Verify_after_create"]["expression"],
            create["Verify_failed_create"]["expression"],
        ])
        for expression in expressions:
            self.assertIn("ticks(first(", expression)
            self.assertIn("ticks(outputs('Event_snapshot')?['EffectiveAt'])", expression)
            for field in ("SourceKey", "EventId", "InitiativeId", "EventType", "SourceSystem", "SourceRecordId", "SourceRevision"):
                self.assertIn(f"equals(first(", expression)
                self.assertIn(f"?['{field}'],outputs('Event_snapshot')?['{field}'])", expression)
        left = datetime.fromisoformat("2026-11-03T10:00:00Z").astimezone(timezone.utc)
        right = datetime.fromisoformat("2026-11-03T20:00:00+10:00").astimezone(timezone.utc)
        self.assertEqual(left, right)

    def test_invalid_source_path_has_no_event_write_in_both_capture_modes(self):
        def connector_methods(node):
            found = []
            if isinstance(node, dict):
                inputs = node.get("inputs", {})
                if not isinstance(inputs, dict):
                    inputs = {}
                host = inputs.get("host", {})
                if host.get("operationId") == "HttpRequest":
                    found.append(inputs.get("parameters", {}).get("parameters/method"))
                for child in node.values():
                    found.extend(connector_methods(child))
            elif isinstance(node, list):
                for child in node:
                    found.extend(connector_methods(child))
            return found

        for deferred in (False, True):
            with self.subTest(deferred_failure=deferred):
                graph = _event_capture_actions("items('Source_rows')", deferred_failure=deferred)
                self.assertEqual(set(graph), {"Validate_source"})
                validation = graph["Validate_source"]
                # Simulate the malformed-row branch: it contains no POST, so an
                # invalid ID/revision cannot create an event before reconciliation stops.
                invalid_branch = validation["else"]["actions"]
                self.assertNotIn("POST", connector_methods(invalid_branch))
                if deferred:
                    self.assertEqual(invalid_branch["Invalid_source"]["type"], "SetVariable")
                else:
                    self.assertEqual(invalid_branch["Invalid_source"]["type"], "Terminate")
                valid_branch = validation["actions"]
                self.assertIn("Event_key", valid_branch)
                self.assertIn("Route_event", valid_branch)
                self.assertIn("POST", connector_methods(valid_branch))

    def test_capture_is_idempotent_and_conflicts_are_not_overwritten(self):
        actions = build_event_capture()["properties"]["definition"]["actions"]["Capture_initiatives"]["actions"]["Continue_if_clean"]["actions"]["Validate_source"]["actions"]
        route = actions["Route_event"]
        self.assertEqual(route["expression"], "@equals(length(body('Lookup_event')?['value']),0)")
        verify_existing = route["else"]["actions"]["Verify_existing"]
        for field in VERIFY_FIELDS:
            self.assertIn(field, verify_existing["expression"])
        self.assertEqual(
            verify_existing["else"]["actions"]["Existing_conflict"]["inputs"]["value"].split(":")[0],
            "EVENT_KEY_CONFLICT",
        )
        create = route["actions"]["Create_missing_event"]["actions"]
        self.assertEqual(create["Create_event"]["inputs"]["parameters"]["parameters/method"], "POST")
        self.assertEqual(create["Create_event"]["inputs"]["retryPolicy"], {"type": "None"})
        self.assertEqual(create["Read_after_create"]["runAfter"], {"Create_event": ["Succeeded"]})
        self.assertEqual(create["Reconcile_failed_create"]["runAfter"], {"Create_event": ["Failed", "TimedOut"]})
        self.assertIn("SourceKey", json.dumps(create["Verify_failed_create"]["expression"]))
        self.assertEqual(create["Verify_failed_create"]["else"]["actions"]["Create_uncertain"]["inputs"]["value"].split(":")[0], "EVENT_CREATE_UNCERTAIN")

    def test_reconciliation_replays_the_same_capture_logic_and_reports_scan_health(self):
        definition = build_reconciliation()["properties"]["definition"]
        actions = definition["actions"]
        self.assertFalse(definition["parameters"]["ReconciliationEnabled"]["defaultValue"])
        self.assertEqual(actions["Read_initiatives"]["inputs"]["parameters"]["parameters/method"], "GET")
        self.assertIn("$top=5000", actions["Read_initiatives"]["inputs"]["parameters"]["parameters/uri"])
        incomplete = actions["Require_complete_page"]["else"]["actions"]["Page_incomplete"]
        self.assertEqual(incomplete["inputs"]["runError"]["code"], "INITIATIVE_PAGE_INCOMPLETE")
        each = actions["Reconcile_initiatives"]
        self.assertEqual(each["runtimeConfiguration"]["concurrency"]["repetitions"], 1)
        replay = each["actions"]["Continue_if_clean"]["actions"]
        capture = build_event_capture()["properties"]["definition"]["actions"]["Capture_initiatives"]["actions"]["Continue_if_clean"]["actions"]
        self.assertEqual(set(replay), set(capture))
        replay_text = json.dumps(replay)
        capture_text = json.dumps(capture)
        for token in ("Event_key", "Event_snapshot", "Lookup_event", "Route_event", "Create_event",
                      "Read_after_create", "Reconcile_failed_create", "SourceKey", "EVENT_KEY_CONFLICT"):
            self.assertIn(token, replay_text)
            self.assertIn(token, capture_text)
        self.assertIn("items('Reconcile_initiatives')?['Modified']", replay_text)
        self.assertIn("@utcNow()", replay_text)
        summary = actions["Health_summary"]["inputs"]
        self.assertTrue(summary["sourceListComplete"])
        self.assertEqual(summary["eventListWrites"], "Append only; existing stable SourceKeys are read and compared.")
        self.assertEqual(summary["initiativesScanned"], "@length(body('Read_initiatives')?['value'])")
        self.assertIn("runId", summary)


if __name__ == "__main__":
    unittest.main()
