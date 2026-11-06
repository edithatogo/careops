# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Synthetic Git-range, destination, offline and redaction acceptance tests."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


scan, gate = module("presidio_scan"), module("pre_push")
POLICY = json.loads((HERE / "presidio-policy.json").read_text())


class DestinationTests(unittest.TestCase):
    def test_only_explicit_private_repository(self):
        calls = []

        def command(args):
            calls.append(args)
            return (
                json.dumps(
                    {
                        "private": True,
                        "visibility": "private",
                        "full_name": POLICY["repository"],
                    }
                ).encode()
                if args[0] == "gh"
                else b""
            )

        self.assertEqual(
            [],
            gate.destination(
                "https://github.com/" + POLICY["repository"] + ".git", POLICY, command
            ),
        )
        self.assertEqual(2, len(calls))
        calls.clear()
        self.assertEqual(
            [],
            gate.destination(
                "https://github.com/" + POLICY["repository"],
                POLICY,
                command,
                advertise=False,
            ),
        )
        self.assertEqual(1, len(calls))
        for url in [
            "https://example.invalid/repo",
            "https://github.com/other/repo.git",
            "https://github.com/" + POLICY["repository"] + ".git?extra=value",
        ]:
            with self.subTest(url_hash=len(url)), self.assertRaises(gate.Refusal):
                gate.destination(url, POLICY, command)

    def test_public_unknown_or_wrong_identity_refused(self):
        for state in [
            {"private": False, "full_name": POLICY["repository"]},
            {},
            {"private": True, "full_name": "other/repo"},
        ]:
            with self.assertRaises(gate.Refusal):
                gate.destination(
                    "https://github.com/" + POLICY["repository"],
                    POLICY,
                    lambda _, state=state: json.dumps(state).encode(),
                )

    def test_invalid_push_and_nonbranch_refused(self):
        for payload in [
            b"bad line",
            ("refs/heads/a " + "a" * 40 + " refs/tags/v1 " + "0" * 40).encode(),
        ]:
            with self.assertRaises(gate.Refusal):
                gate.push_rows(payload)

    def test_missing_scanner_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as d, self.assertRaises(gate.Refusal):
            gate.scanner(Path(d), [], POLICY)

    def test_failed_commands_never_echo_output(self):
        result = subprocess.CompletedProcess([], 1, b"private-output", b"private-error")
        with (
            patch.object(gate.subprocess, "run", return_value=result),
            contextlib.redirect_stderr(io.StringIO()) as err,
            self.assertRaises(gate.Refusal),
        ):
            gate.run(["fictional-command"])
        self.assertEqual("", err.getvalue())

    def test_notification_failure_does_not_authorise_push(self):
        with (
            patch.object(gate.sys, "platform", "darwin"),
            patch.object(gate.subprocess, "run", side_effect=OSError),
        ):
            gate.notify()  # Only the optional notification is swallowed; main returns failure.


class GitScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic")
        self.git("config", "user.email", "synthetic@example.invalid")
        (self.root / "sample.txt").write_text("ordinary source")
        self.base = self.commit()

    def git(self, *args):
        return scan.git(self.root, *args)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Synthetic source update")
        return self.git("rev-parse", "HEAD").decode().strip()

    def test_intermediate_deleted_text_and_message_preserved(self):
        text = "".join(map(chr, [74, 97, 110, 101, 32, 68, 111, 101]))
        (self.root / "temporary.txt").write_text(text)
        self.commit()
        (self.root / "temporary.txt").unlink()
        tip = self.commit()
        items = scan.selected_text(self.root, tip, [self.base], POLICY)
        self.assertTrue(any(x["text"] == text for x in items))
        self.assertTrue(any("Synthetic source update" in x["text"] for x in items))
        self.assertTrue(all(len(x["identity"]) == 64 for x in items))

    def test_index_cannot_hide_outgoing_blob(self):
        (self.root / "sample.txt").write_text("outgoing text")
        tip = self.commit()
        (self.root / "sample.txt").write_text("different staged text")
        self.git("add", "sample.txt")
        items = scan.selected_text(self.root, tip, [self.base], POLICY)
        self.assertTrue(any(x["text"] == "outgoing text" for x in items))
        self.assertFalse(any(x["text"] == "different staged text" for x in items))

    def test_scope_limit_fails_instead_of_truncating(self):
        (self.root / "sample.txt").write_text("changed source")
        tip = self.commit()
        with self.assertRaises(scan.Refusal):
            scan.selected_text(
                self.root, tip, [self.base], {**POLICY, "maxTotalBytes": 1}
            )


class EngineUnitTests(unittest.TestCase):
    def test_exact_review_cannot_approve_changed_text(self):
        class Result:
            entity_type, start, end = "PERSON", 0, 4

        class Analyzer:
            def analyze(self, **_kwargs):
                return [Result()]

        item = {"identity": "a" * 64, "text": "code-only"}
        first = scan.analyze([item], POLICY, Analyzer())
        approval = {
            **first["findings"][0]["details"][0],
            "reason": "synthetic technical token",
            "reviewer": "source-review",
        }
        accepted = scan.analyze([item], POLICY, Analyzer(), {"findings": [approval]})
        self.assertFalse(accepted["findings"])
        changed = scan.analyze(
            [{**item, "text": "other text"}],
            POLICY,
            Analyzer(),
            {"findings": [approval]},
        )
        self.assertTrue(changed["findings"])

    def test_scan_output_contains_no_match_or_filename(self):
        class Result:
            entity_type = "PERSON"
            start = 0
            end = 9

        class Analyzer:
            def analyze(self, **_kwargs):
                return [Result()]

        secret = "synthetic personal content"
        result = scan.analyze(
            [{"identity": "a" * 64, "text": secret}], POLICY, Analyzer()
        )
        output = json.dumps(result)
        self.assertNotIn(secret, output)
        self.assertEqual(["PERSON"], result["findings"][0]["entities"])

    def test_overlap_covers_boundaries(self):
        chunks = []

        class Analyzer:
            def analyze(self, **kwargs):
                chunks.append(kwargs["text"])
                return []

        scan.analyze(
            [{"identity": "a" * 64, "text": "abcdefghijklmno"}],
            {**POLICY, "chunkCharacters": 8, "overlapCharacters": 3},
            Analyzer(),
        )
        self.assertEqual("fgh", chunks[0][-3:])
        self.assertTrue(chunks[1].startswith("fgh"))


class ManagedInstallationTests(unittest.TestCase):
    def test_actual_managed_entrypoint_and_changed_owner_refusal(self):
        """Install into a synthetic Git common dir, not the user's active hooks."""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            subprocess.run(
                ["git", "init", "-q", str(root)], check=True, capture_output=True
            )
            source = root / ".careops-security"
            source.mkdir()
            for name in [
                "install_managed.py",
                "pre_push.py",
                "presidio_scan.py",
                "presidio-policy.json",
                "presidio-reviewed-findings.json",
                "presidio-reviewed-costing.json",
                "redact_legacy.py",
            ]:
                shutil.copyfile(HERE / name, source / name)
            env = root / ".venv-careops-privacy-hooks"
            subprocess.run(
                [sys._base_executable, "-m", "venv", "--without-pip", str(env)],
                check=True,
                capture_output=True,
            )
            bundle = root / ".git/careops-privacy-hooks-v1"
            hooks = bundle / "hooks"
            hooks.mkdir(parents=True)
            dispatch = bundle / "dispatch.py"
            sentinel = "synthetic-diagnostic-must-not-escape"
            dispatch.write_text("print(" + repr(sentinel) + ")\n")
            (bundle / "registry.json").write_text(
                json.dumps({"checkouts": {str(root): {}}})
            )
            before = "#!/bin/sh\n# legacy dispatcher " + str(dispatch) + "\nexit 0\n"
            for event in ["pre-commit", "pre-push"]:
                (hooks / event).write_text(before)
                (hooks / event).chmod(0o700)
            subprocess.run(
                ["git", "-C", str(root), "config", "core.hooksPath", str(hooks)],
                check=True,
                capture_output=True,
            )
            command = [
                str(env / "bin/python"),
                "-I",
                str(source / "install_managed.py"),
            ]
            installed = subprocess.run(
                command, cwd=root, capture_output=True, check=False
            )
            self.assertEqual(0, installed.returncode)
            self.assertTrue((bundle / "presidio-hook-installation.json").is_file())
            self.assertEqual(before, (bundle / "pre-push.before-presidio").read_text())
            # A refused URL stops before gh/network/model use. Shell withholds even startup errors.
            outcome = subprocess.run(
                [str(hooks / "pre-push"), "origin", "https://example.invalid/repo"],
                cwd=root,
                env={**os.environ, "CI": "1"},
                input=b"",
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, outcome.returncode)
            self.assertNotIn(str(root).encode(), outcome.stdout + outcome.stderr)
            self.assertNotIn(sentinel.encode(), outcome.stdout + outcome.stderr)
            committed = subprocess.run(
                [str(hooks / "pre-commit")], cwd=root, capture_output=True, check=False
            )
            self.assertEqual(0, committed.returncode)
            self.assertNotIn(sentinel.encode(), committed.stdout + committed.stderr)
            (hooks / "pre-push").write_text("other-owner-hook\n")
            refused = subprocess.run(
                command, cwd=root, capture_output=True, check=False
            )
            self.assertNotEqual(0, refused.returncode)
            self.assertEqual("other-owner-hook\n", (hooks / "pre-push").read_text())


class ReviewMetadataTests(unittest.TestCase):
    def item(self, text, filename="presidio-reviewed-findings.json"):
        raw = text.encode()
        oid = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        return {
            "identity": hashlib.sha256(
                (".careops-security/" + filename + ":" + oid).encode()
            ).hexdigest(),
            "text": text,
        }

    def test_only_exact_typed_control_numbers_not_free_text_or_other_paths(self):
        row = {
            "identity": "a" * 64,
            "blob_sha256": "b" * 64,
            "start": 1689,
            "end": 1692,
            "entity_index": 0,
            "value_sha256": "c" * 64,
            "reason": "contact 131000",
            "reviewer": "synthetic source review",
        }
        manifest = {
            "schemaVersion": 1,
            "policy_sha256": hashlib.sha256(
                (HERE / "presidio-policy.json").read_bytes()
            ).hexdigest(),
            "findings": [row],
        }
        text = json.dumps(manifest, separators=(",", ":"))
        item = self.item(text)
        offset = text.index("1689")
        candidate = {
            "entity_index": POLICY["entities"].index("PHONE_NUMBER"),
            "start": offset,
            "end": offset + 4,
        }
        self.assertTrue(gate.review_control_number(item, candidate, POLICY))
        hash_offset = text.index('"' + 'b' * 64 + '"') + 1
        hash_finding = {**candidate, "entity_index": POLICY["entities"].index("PERSON"), "start": hash_offset, "end": hash_offset + 64}
        self.assertTrue(gate.review_control_number(item, hash_finding, POLICY))
        label_offset = text.index('blob_sha256')
        self.assertTrue(gate.review_control_number(item, {
            "entity_index": POLICY["entities"].index("PERSON"),
            "start": label_offset + 2, "end": label_offset + len("blob_sha256"),
        }, POLICY))
        self.assertFalse(gate.review_control_number(
            item, {**hash_finding, "end": hash_offset + 16}, POLICY
        ))
        self.assertTrue(gate.review_control_number(
            item, {**hash_finding, "end": hash_offset + 52}, POLICY
        ))
        self.assertFalse(gate.review_control_number(
            {**item, "identity": "d" * 64}, hash_finding, POLICY
        ))
        self.assertFalse(
            gate.review_control_number(
                {**item, "identity": "d" * 64}, candidate, POLICY
            )
        )
        offset = text.index("131000")
        self.assertFalse(
            gate.review_control_number(
                item, {**candidate, "start": offset, "end": offset + 6}, POLICY
            )
        )

    def test_invalid_control_schema_cannot_clear_a_numeric_finding(self):
        text = '{"schemaVersion":1,"start":1689}'
        offset = text.index("1689")
        candidate = {
            "entity_index": POLICY["entities"].index("PHONE_NUMBER"),
            "start": offset,
            "end": offset + 4,
        }
        self.assertFalse(gate.review_control_number(self.item(text), candidate, POLICY))



class NetworkRefusalTests(unittest.TestCase):
    def test_existing_udp_socket_and_dns_cannot_bypass_offline_guard(self):
        methods = (
            "connect", "connect_ex", "bind", "listen", "accept", "send", "sendall",
            "sendto", "sendmsg", "sendmsg_afalg", "recv", "recv_into", "recvfrom",
            "recvfrom_into", "recvmsg", "recvmsg_into",
        )
        functions = ("create_connection", "getaddrinfo", "gethostbyname",
                     "gethostbyname_ex", "gethostbyaddr", "getnameinfo")
        # Every original I/O path has a sentinel: a failed guard cannot send even
        # a synthetic packet. The socket predates the class-method replacement.
        with scan.socket.socket(scan.socket.AF_INET, scan.socket.SOCK_DGRAM) as existing:
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.dict(os.environ))
                for name in methods:
                    if hasattr(scan.socket.socket, name):
                        stack.enter_context(patch.object(scan.socket.socket, name,
                            side_effect=AssertionError("unexpected native socket call")))
                for name in functions:
                    stack.enter_context(patch.object(scan.socket, name,
                        side_effect=AssertionError("unexpected native resolver call")))
                scan.prohibit_network()
                for name in methods:
                    if hasattr(existing, name):
                        with self.subTest(method=name), self.assertRaises(scan.Refusal):
                            getattr(existing, name)()
                for name in functions:
                    with self.subTest(resolver=name), self.assertRaises(scan.Refusal):
                        getattr(scan.socket, name)()


if __name__ == "__main__":
    unittest.main()


class ExactReviewSplitTests(unittest.TestCase):
    def test_both_controls_are_required_and_policy_bound(self):
        document = {"schemaVersion": 1, "policy_sha256": hashlib.sha256((HERE / "presidio-policy.json").read_bytes()).hexdigest(), "findings": []}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            shutil.copyfile(HERE / "presidio-policy.json", root / "presidio-policy.json")
            for name in gate.REVIEW_FILES:
                (root / name).write_text(json.dumps(document))
            with patch.object(gate, "HERE", root):
                self.assertEqual([], gate.load_reviews(POLICY)["findings"])
                second = root / gate.REVIEW_FILES[1]
                second.unlink()
                with self.assertRaises(FileNotFoundError): gate.load_reviews(POLICY)
                for bad in [{**document, "policy_sha256": "0" * 64}, {**document, "findings": [{}]}]:
                    second.write_text(json.dumps(bad))
                    with self.assertRaises(gate.Refusal): gate.load_reviews(POLICY)
                second.write_text('{"schemaVersion":1,"schemaVersion":1}')
                with self.assertRaises(gate.Refusal): gate.load_reviews(POLICY)

    def test_only_fixed_second_path_gets_typed_metadata_handling(self):
        document = {"schemaVersion": 1, "policy_sha256": hashlib.sha256((HERE / "presidio-policy.json").read_bytes()).hexdigest(), "findings": [{"identity": "a" * 64, "blob_sha256": "b" * 64, "entity_index": 0, "start": 1689, "end": 1692, "value_sha256": "c" * 64, "reason": "contact 131000", "reviewer": "fictional review"}]}
        text = json.dumps(document)
        fixture = ReviewMetadataTests()
        item = fixture.item(text, "presidio-reviewed-costing.json")
        offset = text.index("1689")
        finding = {"entity_index": POLICY["entities"].index("PHONE_NUMBER"), "start": offset, "end": offset + 4}
        self.assertTrue(gate.review_control_number(item, finding, POLICY))
        self.assertFalse(gate.review_control_number(fixture.item(text, "arbitrary.json"), finding, POLICY))
        offset = text.index("131000")
        self.assertFalse(gate.review_control_number(item, {**finding, "start": offset, "end": offset + 6}, POLICY))


class ExactReviewIndexTests(unittest.TestCase):
    def test_every_binding_and_review_authority_remains_required(self):
        class Result:
            entity_type, start, end = "PERSON", 0, 4
        class Analyzer:
            def analyze(self, **kwargs): return [Result()]
        item = {"identity": "a" * 64, "blob_sha256": "b" * 64, "text": "code-only"}
        initial = scan.analyze([item], POLICY, Analyzer())
        approval = {**initial["findings"][0]["details"][0], "reason": "fictional code token", "reviewer": "source review"}
        decoys = [{**approval, "identity": str(n).zfill(64)} for n in range(10000)]
        accepted = scan.analyze([item], POLICY, Analyzer(), {"findings": [*decoys, approval]})
        self.assertEqual(1, accepted["reviewed"])
        self.assertFalse(accepted["findings"])
        for field in approval:
            bad = {**approval, field: "" if field in {"reason", "reviewer"} else (-1 if isinstance(approval[field], int) else "c" * 64)}
            with self.subTest(field=field):
                refused = scan.analyze([item], POLICY, Analyzer(), {"findings": [*decoys, bad]})
                self.assertEqual(0, refused["reviewed"])
                self.assertTrue(refused["findings"])
