"""Offline correspondence contract/candidate checks; no native access.

SPDX-License-Identifier: Apache-2.0
"""
import unittest
from scripts.correspondence_capture import build, classify, OUTLOOK, SHAREPOINT


def fixture():
    return {"site_url": "https://fictional-example.sharepoint.com/sites/executive",
            "register_list_id": "11111111-1111-4111-8111-111111111111",
            "receipts_list_id": "22222222-2222-4222-8222-222222222222",
            "sender": "sending-office@example.com", "outlook_connection": "fictional-outlook",
            "sharepoint_connection": "fictional-sharepoint"}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.message = {"from": "sending-office@example.com", "id": "fixture-id",
                        "internetMessageId": "<message@example.com>", "subject": "Fictional matter",
                        "receivedDateTime": "2026-10-26T02:00:00Z"}

    def decision(self, message=None, **kwargs):
        return classify(message or self.message, sender=fixture()["sender"], start="2026-10-26T00:00:00Z", **kwargs)

    def test_identity_replay_partial_create_and_ambiguous_messages(self):
        self.assertEqual(self.decision(), "RegisterForReview")
        self.assertEqual(self.decision(exact=1), "AlreadyRegistered")
        self.assertEqual(self.decision(exact=2), "NeedsReview")
        self.assertEqual(self.decision(conversation_matches=1), "NeedsReview")
        self.assertEqual(self.decision(title_matches=1), "NeedsReview")

    def test_sender_boundary_and_incomplete_identity(self):
        for change, expected in [({"from": "other@example.com"}, "Excluded"),
                ({"receivedDateTime": "2026-10-25T23:59:59Z"}, "Excluded"),
                ({"internetMessageId": ""}, "NeedsReview"), ({"internetMessageId": "x" * 256}, "NeedsReview"),
                ({"id": ""}, "NeedsReview"), ({"subject": " "}, "NeedsReview"),
                ({"receivedDateTime": "invalid"}, "NeedsReview")]:
            self.assertEqual(self.decision({**self.message, **change}), expected)

    def test_candidate_is_stopped_and_default_disabled_with_future_boundary(self):
        c = build(fixture()); d = c["properties"]["definition"]
        self.assertEqual(c["properties"]["state"], "Stopped")
        self.assertIs(d["parameters"]["CaptureEnabled"]["defaultValue"], False)
        self.assertEqual(d["parameters"]["CaptureStartUtc"]["defaultValue"], "2100-01-01T00:00:00Z")
        t = next(iter(d["triggers"].values()))
        self.assertIn("CaptureEnabled", str(t["conditions"]))
        self.assertFalse(t["inputs"]["parameters"]["includeAttachments"])

    def test_no_premium_send_mailbox_mutation_or_existing_register_update(self):
        c = build(fixture()); calls = [x for x in walk(c) if x.get("type") == "OpenApiConnection"]
        self.assertTrue(calls)
        self.assertEqual({x["inputs"]["host"]["apiId"] for x in calls}, {OUTLOOK, SHAREPOINT})
        for x in calls:
            i = x["inputs"]; op = i["host"]["operationId"]
            self.assertIn(op, {"HttpRequest", "OnNewEmailV3"})
            self.assertEqual(i["retryPolicy"], {"type": "none"})
            if i["host"]["apiId"] == OUTLOOK and op == "HttpRequest":
                self.assertEqual(i["parameters"]["Method"], "GET")
            if i["host"]["apiId"] == SHAREPOINT:
                self.assertIn(i["parameters"]["parameters/method"], {"GET", "POST"})
        self.assertFalse(any(x.get("type") in {"Http", "HttpWebhook", "Workflow", "Function"} for x in walk(c)))

    def test_escape_mail_literals_and_never_retry_uncertain_create(self):
        c = build(fixture()); text = str(c)
        self.assertIn("decodeUriComponent('%27%27')", text)
        self.assertIn("CREATE_UNCERTAIN_NO_RETRY", text)
        self.assertIn("CREATE_RECONCILED", text)
        self.assertIn("SOURCE_IDENTITY_OR_LINK_UNVERIFIED", text)
        creates = [x for x in walk(c) if x.get("type") == "OpenApiConnection" and
                   x["inputs"]["parameters"].get("parameters/uri") == "_api/web/lists(guid'11111111-1111-4111-8111-111111111111')/items" and
                   x["inputs"]["parameters"].get("parameters/method") == "POST"]
        self.assertEqual(len(creates), 1)

    def test_action_names_unique_and_dependencies_locally_resolvable(self):
        c = build(fixture()); names = []
        for x in walk(c):
            if "actions" in x:
                actions = x["actions"]; names.extend(actions)
                for action in actions.values():
                    self.assertTrue(set(action.get("runAfter", {})).issubset(actions))
        self.assertEqual(len(names), len(set(names)))

    def test_separate_receipt_site_and_case_sensitive_identity(self):
        config = {**fixture(), "receipts_site_url": "https://fictional-example.sharepoint.com/sites/private"}
        c = build(config)
        posts = [x["inputs"]["parameters"] for x in walk(c) if x.get("type") == "OpenApiConnection" and x["inputs"]["parameters"].get("parameters/method") == "POST"]
        for p in posts:
            is_receipt = config["receipts_list_id"] in p["parameters/uri"]
            self.assertEqual(p["dataset"], config["receipts_site_url"] if is_receipt else config["site_url"])
        self.assertIn("SOURCE_KEY_COLLISION_OR_DUPLICATE", str(c))
        self.assertIn("base64(outputs('Message_key'))", str(c))

    def test_invalid_bindings_are_rejected(self):
        for change in [{"receipts_site_url": "http://example.org"}, {"site_url": "http://example.org"}, {"site_url": "https://user:pass' + '@fictional-example.sharepoint.com"},
                       {"register_list_id": "not-id"}, {"sharepoint_connection": ""},
                       {"receipts_list_id": fixture()["register_list_id"]}, {"sender": "not-an-address"}]:
            with self.assertRaises(ValueError):
                build({**fixture(), **change})


if __name__ == "__main__":
    unittest.main()
