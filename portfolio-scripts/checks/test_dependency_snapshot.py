"""Graph preservation, privacy and fail-closed payload preparation controls."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "dependency_snapshot.py"
SPEC = importlib.util.spec_from_file_location("dependency_snapshot", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class Snapshot(unittest.TestCase):
    def setUp(self):
        self.kw = {
            "sha": "a" * 40,
            "ref": "refs/heads/main",
            "manifest": "uv.lock",
            "job_id": "123",
            "correlator": "python-lock",
            "scanned": "2026-10-24T00:00:00Z",
        }
        self.bom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "metadata": {"component": {"bom-ref": "project"}},
            "components": [
                {
                    "bom-ref": n,
                    "purl": "pkg:pypi/" + n + "@1.0",
                    "externalReferences": [
                        {
                            "type": "distribution",
                            "url": "https://files.pythonhosted.org/packages/fictional.whl",
                        }
                    ],
                }
                for n in ["alpha", "beta"]
            ],
            "dependencies": [
                {"ref": "project", "dependsOn": ["alpha"]},
                {"ref": "alpha", "dependsOn": ["beta"]},
                {"ref": "beta"},
            ],
        }

    def test_preserves_direct_transitive_edges_and_filters_private_fields(self):
        self.bom["metadata"]["private"] = "DO_NOT_EXPORT"
        self.bom["components"][0]["properties"] = [
            {"name": "local-path", "value": "DO_NOT_EXPORT"}
        ]
        value = module.snapshot(self.bom, **self.kw)
        packages = value["manifests"]["uv.lock"]["resolved"]
        self.assertEqual(
            packages["pkg:pypi/alpha@1.0"]["dependencies"], ["pkg:pypi/beta@1.0"]
        )
        self.assertEqual(packages["pkg:pypi/alpha@1.0"]["relationship"], "direct")
        self.assertEqual(packages["pkg:pypi/beta@1.0"]["relationship"], "indirect")
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(value))

    def test_missing_unknown_and_duplicate_nodes_fail(self):
        variants = []
        unknown = copy.deepcopy(self.bom)
        unknown["dependencies"][1]["dependsOn"].append("unknown")
        variants.append(unknown)
        missing = copy.deepcopy(self.bom)
        missing["dependencies"].pop()
        variants.append(missing)
        duplicate = copy.deepcopy(self.bom)
        duplicate["components"].append(duplicate["components"][0])
        variants.append(duplicate)
        for value in variants:
            with (
                self.subTest(value=value["dependencies"]),
                self.assertRaises(ValueError),
            ):
                module.snapshot(value, **self.kw)

    def test_distribution_urls_and_non_pypi_identifiers_are_rejected(self):
        for url in [
            "https://private.example/pkg.whl",
            "https://user:secret@pypi.org/pkg",
            "https://pypi.org/pkg?token=private",
        ]:
            value = copy.deepcopy(self.bom)
            value["components"][0]["externalReferences"][0]["url"] = url
            with self.assertRaisesRegex(ValueError, "Non-public distribution"):
                module.snapshot(value, **self.kw)
        self.bom["components"][0]["purl"] = "pkg:generic/local@1.0"
        with self.assertRaises(ValueError):
            module.snapshot(self.bom, **self.kw)

    def test_source_identity_path_and_timestamp_controls(self):
        for key, value in [
            ("sha", "main"),
            ("ref", "refs/heads/../private"),
            ("manifest", "../uv.lock"),
            ("manifest", "/tmp/uv.lock"),
            ("scanned", "2026-10-24T00:00:00+10:00"),
        ]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.snapshot(self.bom, **{**self.kw, key: value})

    def test_inventory_retains_packages_without_inventing_dependency_edges(self):
        source = {
            "version": "1",
            "environment": {"python_version": "3.15", "python_full_version": "3.15.1"},
            "installed": [
                {
                    "metadata": {"name": "Alpha_Package", "version": "1.0"},
                    "metadata_location": "DO_NOT_EXPORT",
                }
            ],
        }
        value = module.snapshot(
            module.pip_inventory(source),
            **{**self.kw, "manifest": "scripts/bootstrap-tools.lock"},
            inventory_only=True,
        )
        package = value["manifests"]["scripts/bootstrap-tools.lock"]["resolved"][
            "pkg:pypi/alpha-package@1.0"
        ]
        self.assertEqual(package, {"package_url": "pkg:pypi/alpha-package@1.0"})
        self.assertNotEqual(
            value["detector"]["name"],
            module.snapshot(self.bom, **self.kw)["detector"]["name"],
            "Inventory must not replace resolved graph snapshots under the same correlator",
        )
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(value))
        source["installed"][0]["direct_url"] = {"url": "file:private"}
        with self.assertRaises(ValueError):
            module.pip_inventory(source)

    def test_cli_does_not_overwrite_an_existing_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / "source.json", Path(tmp) / "snapshot.json"
            source.write_text(json.dumps(self.bom))
            command = [
                sys.executable,
                str(SCRIPT),
                "--sbom",
                str(source),
                "--output",
                str(output),
            ]
            for key, value in self.kw.items():
                command.extend(["--" + key.replace("_", "-"), value])
            subprocess.run(command, check=True, capture_output=True)
            original = output.read_bytes()
            second = subprocess.run(command, capture_output=True, check=False)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), original)

    def test_empty_exports_and_wrong_inspection_runtime_fail(self):
        self.bom["components"] = []
        with self.assertRaises(ValueError):
            module.snapshot(self.bom, **self.kw)
        with self.assertRaises(ValueError):
            module.pip_inventory(
                {
                    "version": "1",
                    "environment": {
                        "python_version": "3.14",
                        "python_full_version": "3.14.6",
                    },
                    "installed": [],
                }
            )


if __name__ == "__main__":
    unittest.main()
