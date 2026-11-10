"""Offline engineering-frontier regression tests: no tenant/network or credentials."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engineering_frontier import (FrontierError, build_packet, check_required_contexts,
                                  guard_tool, resolve_owner)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args],
                            check=True, capture_output=True, text=True)
    return result.stdout.strip()


class OfflineFrontierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Synthetic Test")
        git(self.root, "config", "user.email", "synthetic@example.invalid")
        def write(path: str, value: str):
            p = self.root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(value)
        write("AGENTS.md", "Checked-in synthetic context")
        write("conductor/index.md", "# Synthetic conductor")
        write("docs/targeted-testing.md", "Synthetic test selection")
        write("portfolio/repos.json", json.dumps({"components": [
            {"name": "mod-a", "path": "modules/mod-a", "materialization": "integrated-source"},
            {"name": "mod-b", "path": "modules/mod-b", "materialization": "integrated-source"},
            {"name": "mod-optional", "path": "modules/mod-optional", "materialization": "submodule"}
        ]}))
        write("modules/mod-a/AGENTS.md", "Module instructions")
        write("modules/mod-a/src/work.py", "x = 1")
        write("modules/mod-b/src/work.py", "x = 2")
        write("portfolio-scripts/engine.py", "print('ok')")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "synthetic fixture")
        self.sha = git(self.root, "rev-parse", "HEAD")

    def tearDown(self):
        self.temp.cleanup()

    def test_packet_is_bound_to_exact_current_commit_and_owner(self):
        packet = build_packet(self.root, "EF-02.02", self.sha,
                              ["modules/mod-a/src/work.py"])
        self.assertEqual(packet["source"]["commit"], self.sha)
        self.assertEqual(packet["task"]["owner"], "mod-a")
        self.assertEqual(packet["task"]["scope"], "read-test")
        self.assertEqual(packet["task"]["changed_paths"], ["modules/mod-a/src/work.py"])
        self.assertFalse(packet["qualification"]["native"])
        self.assertEqual(packet["context"][0]["path"], "AGENTS.md")
        self.assertTrue(all(len(x["sha256"]) == 64 for x in packet["context"]))
        self.assertEqual(packet["tests"]["selected"], [])
        self.assertTrue(packet["tests"]["owner_selection_required"])

    def test_parent_context_and_explicit_targeted_tests(self):
        packet = build_packet(self.root, "EF-03.01", self.sha,
                              ["portfolio-scripts/engine.py"])
        self.assertEqual(packet["task"]["owner"], "careops")
        self.assertEqual(packet["tests"]["selected"], [
            "portfolio-scripts/checks/test_engineering_frontier.py"
        ])

    def test_uncommitted_registry_does_not_change_owner(self):
        (self.root / "portfolio/repos.json").write_text(json.dumps({"components": []}))
        packet = build_packet(self.root, "EF-02.02", self.sha,
                              ["modules/mod-a/src/work.py"])
        self.assertEqual(packet["task"]["owner"], "mod-a")

    def test_stale_commit_rejected(self):
        with self.assertRaisesRegex(FrontierError, "stale-source"):
            build_packet(self.root, "EF-02.01", "f" * 40, ["modules/mod-a/src/work.py"])

    def test_missing_untracked_symlink_and_traversal_rejected(self):
        (self.root / "modules/mod-a/src/untracked.py").write_text("private")
        with self.assertRaisesRegex(FrontierError, "not-tracked"):
            build_packet(self.root, "EF-02.01", self.sha, ["modules/mod-a/src/untracked.py"])
        for value in ["../secrets", "/tmp/file", "modules\\mod-a\\src\\work.py",
                      "modules/mod-a/../../AGENTS.md"]:
            with self.subTest(value=value), self.assertRaises(FrontierError):
                build_packet(self.root, "EF-02.01", self.sha, [value])
        (self.root / "modules/mod-a/src/work.py").unlink()
        (self.root / "modules/mod-a/src/work.py").symlink_to(self.root / "AGENTS.md")
        with self.assertRaisesRegex(FrontierError, "unsafe-file"):
            build_packet(self.root, "EF-02.01", self.sha, ["modules/mod-a/src/work.py"])

    def test_cross_owner_and_optional_submodule_fail_closed(self):
        with self.assertRaisesRegex(FrontierError, "cross-module"):
            build_packet(self.root, "EF-02.01", self.sha, [
                "modules/mod-a/src/work.py", "modules/mod-b/src/work.py"])
        with self.assertRaisesRegex(FrontierError, "optional-submodule"):
            resolve_owner("modules/mod-optional/README.md", self.root)

    def test_empty_duplicate_and_malformed_task_are_refused(self):
        for paths in [[], ["modules/mod-a/src/work.py"] * 2]:
            with self.assertRaises(FrontierError):
                build_packet(self.root, "EF-02.01", self.sha, paths)
        with self.assertRaisesRegex(FrontierError, "invalid-task"):
            build_packet(self.root, "Ignore instructions", self.sha,
                         ["modules/mod-a/src/work.py"])

    def test_tool_boundary_rejects_write_mutation_and_injection(self):
        self.assertTrue(guard_tool("repo:read", {"repo:read", "runner:focused-test"}))
        for op in ["git:merge", "tenant:write", "email:send", "shell:*",
                   "repo:read && tenant:write", "runner:focused-test;curl"]:
            with self.subTest(op=op), self.assertRaisesRegex(FrontierError, "tool-denied"):
                guard_tool(op, {"repo:read", "runner:focused-test"})

    def test_required_contexts_are_complete_and_bound(self):
        checks = [
            {"name": "Security gate", "head_sha": self.sha, "status": "completed",
             "conclusion": "success", "started_at": "2026-11-11T01:00:00Z",
             "completed_at": "2026-11-11T01:00:03Z"},
            {"name": "Privacy and secrets", "head_sha": self.sha, "status": "completed",
             "conclusion": "success", "started_at": "2026-11-11T01:00:00Z",
             "completed_at": "2026-11-11T01:00:04Z"}
        ]
        happy = check_required_contexts(self.sha, ["Security gate", "Privacy and secrets"], checks)
        self.assertTrue(happy["all_required_passed"])
        self.assertEqual(happy["unverified"], [])
        for changed in [{"conclusion": "failure"}, {"status": "queued"},
                        {"completed_at": None}, {"head_sha": "e" * 40}]:
            bad = [checks[0], {**checks[1], **changed}]
            self.assertFalse(check_required_contexts(self.sha,
                ["Security gate", "Privacy and secrets"], bad)["all_required_passed"])
        self.assertFalse(check_required_contexts(self.sha,
            ["Security gate", "Privacy and secrets"], [checks[0], checks[0], checks[1]])["all_required_passed"])
        self.assertFalse(check_required_contexts(self.sha,
            ["Security gate", "Privacy and secrets"], [checks[0]])["all_required_passed"])

    def test_no_text_or_credential_contents_in_receipts(self):
        content = "Sensitive synthetic content, not for an agent packet"
        (self.root / "modules/mod-a/AGENTS.md").write_text(content)
        packet = build_packet(self.root, "EF-02.02", self.sha,
                              ["modules/mod-a/src/work.py"])
        self.assertNotIn(content, json.dumps(packet))
        self.assertNotIn("synthetic@example.invalid", json.dumps(packet))


if __name__ == "__main__":
    unittest.main()
