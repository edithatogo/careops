"""Verify source-package reproducibility, SBOM content and publication boundaries."""

import hashlib
import importlib.util
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "source_release", Path(__file__).resolve().parents[1] / "build_source_release.py"
)
RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELEASE)


class SourceRelease(unittest.TestCase):
    def fixture(self, root):
        module = root / "modules/careops-incidents"
        module.mkdir(parents=True)
        contents = {
            "LICENSE": "MIT fixture licence\n",
            "README.md": "Fictional standalone source\n",
            "SOURCE_PROVENANCE.json": "{}\n",
            "tool.py": 'print("fictional source")\n',
        }
        for name, text in contents.items():
            (module / name).write_text(text)
        inventory = {
            "files": ["modules/careops-incidents/" + n for n in contents],
            "gitlinks": {},
        }
        (root / "PUBLIC_SOURCE_FILES.json").write_text(json.dumps(inventory))

        def git(*args):
            return subprocess.run(
                ["git", "-C", str(root), *args],
                check=True,
                capture_output=True,
                text=True,
            )

        git("init", "-q")
        git("config", "user.name", "Fictional source fixture")
        git("config", "user.email", "fixture@example.invalid")
        git("add", ".")
        git("commit", "-qm", "Fictional reviewed source")
        return module, contents, git

    def test_archive_and_sbom_are_reproducible_and_match_actual_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repository"
            root.mkdir()
            _module, contents, _ = self.fixture(root)
            first, second = Path(tmp) / "one", Path(tmp) / "two"
            a = RELEASE.build(root, first)
            b = RELEASE.build(root, second)
            self.assertEqual(a, b)
            self.assertEqual(
                (first / a["archive"]).read_bytes(),
                (second / b["archive"]).read_bytes(),
            )
            self.assertEqual(
                (first / a["sbom"]).read_bytes(), (second / b["sbom"]).read_bytes()
            )
            sbom = json.loads((first / a["sbom"]).read_text())
            with tarfile.open(first / a["archive"]) as archive:
                entries = {
                    m.name: archive.extractfile(m).read() for m in archive.getmembers()
                }
            self.assertEqual(len(entries), len(contents))
            for item in sbom["files"]:
                checksum = next(
                    c["checksumValue"]
                    for c in item["checksums"]
                    if c["algorithm"] == "SHA256"
                )
                self.assertEqual(
                    checksum,
                    hashlib.sha256(
                        entries[item["fileName"].removeprefix("./")]
                    ).hexdigest(),
                )
            self.assertEqual(
                sbom["packages"][0]["checksums"][0]["checksumValue"], a["sha256"]
            )
            with self.assertRaises(ValueError):
                RELEASE.build(root, first)

    def test_untracked_data_and_modified_worktree_are_not_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repository"
            root.mkdir()
            module, contents, _ = self.fixture(root)
            (module / "untracked.csv").write_text("fictional excluded input")
            (module / "tool.py").write_text("uncommitted owner change")
            out = Path(tmp) / "release"
            receipt = RELEASE.build(root, out)
            with tarfile.open(out / receipt["archive"]) as archive:
                self.assertNotIn("careops-incidents/untracked.csv", archive.getnames())
                self.assertEqual(
                    archive.extractfile("careops-incidents/tool.py").read().decode(),
                    contents["tool.py"],
                )

    def test_unsafe_or_nonregular_reviewed_entries_are_refused(self):
        for replacement in [
            "modules/careops-incidents/../escape",
            "modules/careops-incidents/tool.py",
        ]:
            with self.subTest(path=replacement), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "repository"
                root.mkdir()
                module, _, git = self.fixture(root)
                if replacement.endswith("tool.py"):
                    (module / "tool.py").unlink()
                    (module / "tool.py").symlink_to("README.md")
                else:
                    p = root / "PUBLIC_SOURCE_FILES.json"
                    data = json.loads(p.read_text())
                    data["files"].append(replacement)
                    p.write_text(json.dumps(data))
                git("add", ".")
                git("commit", "-qm", "Invalid publication fixture")
                with self.assertRaises(ValueError):
                    RELEASE.build(root, Path(tmp) / "release")


if __name__ == "__main__":
    unittest.main()
