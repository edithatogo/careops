"""Delivery-profile and inventory boundary regressions (no network or tenant)."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parents[1] / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


delivery = load("validate_delivery")
dependencies = load("inventory_dependencies")


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".careops").mkdir()
        (self.root / "guide.md").write_text("fictional guide\n")
        self.profile = {
            "schemaVersion": 1,
            "module": "fictional-module",
            "sourceKind": "reusable-source",
            "releasePolicy": "development-first-verified-promotion",
            "standards": "https://github.com/edithatogo/careops/blob/main/docs/development-and-delivery.md",
            "localGuide": "guide.md",
            "nextTasks": [
                {
                    "id": "first",
                    "operation": "Check fixture",
                    "success": "Fixture readback",
                    "lane": "existing",
                    "tools": ["local"],
                    "status": "queued",
                }
            ],
        }

    def write(self):
        (self.root / ".careops/module.json").write_text(json.dumps(self.profile))

    def test_valid_and_duplicate_tasks(self):
        self.write()
        self.assertEqual(delivery.validate(self.root), [])
        self.profile["nextTasks"] *= 2
        self.write()
        self.assertIn(
            "task IDs must be nonempty and unique", delivery.validate(self.root)
        )

    def test_guide_cannot_escape_and_empty_queue_fails(self):
        self.profile.update(localGuide="../outside.md", nextTasks=[])
        self.write()
        errors = delivery.validate(self.root)
        self.assertIn("localGuide must be a repository-relative path", errors)
        self.assertIn("nextTasks must contain an executable queue", errors)

    def test_malformed_profile_fails_without_traceback(self):
        (self.root / ".careops/module.json").write_text("{")
        self.assertTrue(delivery.validate(self.root))
        (self.root / ".careops/module.json").write_text("[]")
        self.assertEqual(
            delivery.validate(self.root), ["module profile must be a JSON object"]
        )

    def test_inventory_uses_tracked_manifests_only_and_marks_action_mutability(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        workflow = self.root / ".github/workflows/test.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "uses: actions/checkout@v7\nuses: actions/setup-python@" + "a" * 40 + "\n"
        )
        (self.root / "requirements-dev.txt").write_text("pytest==9.1.1\n")
        (self.root / "requirements-private.txt").write_text("untracked\n")
        (self.root / "operational.txt").write_text("must never be read\n")
        subprocess.run(
            [
                "git",
                "-C",
                str(self.root),
                "add",
                ".github/workflows/test.yml",
                "requirements-dev.txt",
                "operational.txt",
            ],
            check=True,
        )
        result = dependencies.inventory(self.root)
        self.assertEqual(
            {f["path"] for f in result["declarations"]},
            {".github/workflows/test.yml", "requirements-dev.txt"},
        )
        self.assertEqual([a["immutable"] for a in result["actions"]], [False, True])
        self.assertEqual(
            result["dependencies"],
            [
                {
                    "path": "requirements-dev.txt",
                    "package": "pytest",
                    "version": "==9.1.1",
                    "ecosystem": "pypi",
                }
            ],
        )

    def test_inventory_redacts_nonversion_references(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        (self.root / "package.json").write_text(
            json.dumps(
                {
                    "dependencies": {"fictional": "file:../private"},
                    "engines": {"node": ">=24"},
                }
            )
        )
        subprocess.run(["git", "-C", str(self.root), "add", "package.json"], check=True)
        result = dependencies.inventory(self.root)
        self.assertEqual(
            result["dependencies"][0]["version"],
            "non-version-reference; inspect privately",
        )
        self.assertNotIn("file:../private", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
