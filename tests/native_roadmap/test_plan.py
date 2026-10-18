"""Synthetic regressions for the lifecycle-plan guard, not deployment tests."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_native_roadmap import validate


class RoadmapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folders: list[Path] = []
        (self.root / "portfolio").mkdir()
        (self.root / "portfolio/native-credentialing-target.json").write_text(json.dumps({
            "structuredSystemOfRecord": "full-dataverse", "sqliteUse": "synthetic-test-adapter-only"
        }), encoding="utf-8")
        for n in range(1, 13):
            folder = self.root / f"conductor/tracks/native_{n:02}_test_20260923"
            folder.mkdir(parents=True)
            self.folders.append(folder)
            (folder / "metadata.json").write_text(json.dumps({
                "track_id": folder.name, "task_prefix": f"N{n:02}", "task_count": 10,
                "owner": "Test owner", "status": "planned", "depends_on": []
            }), encoding="utf-8")
            (folder / "spec.md").write_text("Synthetic scope", encoding="utf-8")
            (folder / "plan.md").write_text("\n".join(
                f"- [ ] N{n:02}.{i:02} Produce synthetic output; accept tested result."
                for i in range(1, 11)
            ), encoding="utf-8")
        for filename, suffix in (("native-m365-roadmap.md", "plan.md"), ("tracks.md", "")):
            (self.root / "conductor" / filename).write_text("\n".join(
                f"tracks/{folder.name}/{suffix}" for folder in self.folders
            ), encoding="utf-8")

    def metadata(self, **changes: object) -> None:
        path = self.folders[0] / "metadata.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(changes)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_valid_plan(self) -> None:
        self.assertEqual(validate(self.root), (12, 120))

    def test_missing_track(self) -> None:
        self.folders[0].rename(self.folders[0].with_name("not-a-native-track"))
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_wrong_identity(self) -> None:
        self.metadata(track_id="different")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_count_and_owner(self) -> None:
        for changes in ({"task_count": True}, {"task_count": 9}, {"owner": " "}):
            with self.subTest(changes=changes):
                self.metadata(task_count=10, owner="Owner")
                self.metadata(**changes)
                with self.assertRaises(ValueError):
                    validate(self.root)

    def test_invalid_status(self) -> None:
        self.metadata(status="deployed")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_invalid_dependencies(self) -> None:
        for value in (None, [1], ["missing"], ["missing", "missing"], [self.folders[0].name]):
            with self.subTest(value=value):
                self.metadata(depends_on=value)
                with self.assertRaises(ValueError):
                    validate(self.root)

    def test_missing_task_or_acceptance(self) -> None:
        path = self.folders[0] / "plan.md"
        original = path.read_text(encoding="utf-8")
        for text in (original.replace("N01.01", "N01.02"), original.replace("accept", "omit")):
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(self.root)

    def test_false_completion(self) -> None:
        self.metadata(status="completed")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_completion_evidence_and_status(self) -> None:
        path = self.folders[0] / "plan.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace("[ ]", "[x]"), encoding="utf-8")
        self.metadata(status="completed")
        with self.assertRaises(ValueError):
            validate(self.root)
        path.write_text(path.read_text(encoding="utf-8").replace("result.", "result. Evidence: synthetic-receipt"), encoding="utf-8")
        self.assertEqual(validate(self.root), (12, 120))
        self.metadata(status="planned")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_undiscoverable_track(self) -> None:
        (self.root / "conductor/tracks.md").write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_empty_specification(self) -> None:
        (self.folders[0] / "spec.md").write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_wrong_native_target(self) -> None:
        (self.root / "portfolio/native-credentialing-target.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate(self.root)

    def test_non_object_metadata(self) -> None:
        (self.folders[0] / "metadata.json").write_text("[]", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate(self.root)
