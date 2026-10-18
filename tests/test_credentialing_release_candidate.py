from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from typing import cast

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_credentialing_release_candidate import build_candidate  # noqa: E402

REGISTRY = ROOT / "portfolio" / "credentialing-release-sources.json"


class CredentialingReleaseCandidateTests(unittest.TestCase):
    """Validate candidate generation without network or repository writes."""

    def registry(self) -> dict[str, object]:
        value = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return cast("dict[str, object]", value)

    @staticmethod
    def resolver(repository: str, reference: str) -> str:
        seed = sum(ord(character) for character in repository + reference)
        return f"{seed:040x}"[-40:]

    def test_candidate_is_immutable_but_not_promoted(self) -> None:
        candidate = build_candidate(
            self.registry(),
            observed_at="2026-09-10T12:00:00+10:00",
            resolver=self.resolver,
        )

        self.assertEqual(candidate["status"], "candidate-not-validated")
        self.assertEqual(candidate["observed_at"], "2026-09-10T02:00:00Z")
        self.assertFalse(candidate["production_writes"])
        self.assertEqual(len(candidate["modules"]), 7)
        self.assertEqual(len(candidate["source_collections"]), 1)
        self.assertTrue(all(not value for value in candidate["validation_gates"].values()))
        self.assertEqual(
            set(candidate["changed_from_baseline"]),
            set(candidate["modules"]),
        )
        self.assertTrue(
            all(
                len(source["commit"]) == 40
                for source in candidate["modules"].values()
            )
        )

    def test_baseline_change_detection_is_explicit(self) -> None:
        initial = build_candidate(
            self.registry(),
            observed_at="2026-09-10T00:00:00Z",
            resolver=self.resolver,
        )
        baseline = {
            module_id: source["commit"]
            for module_id, source in initial["modules"].items()
        }
        baseline["careops-costing"] = "0" * 40
        candidate = build_candidate(
            self.registry(),
            observed_at="2026-09-10T00:00:00Z",
            resolver=self.resolver,
            baseline=baseline,
        )

        self.assertEqual(candidate["changed_from_baseline"], ["careops-costing"])

    def test_non_github_or_credentialled_repository_is_rejected(self) -> None:
        for repository in (
            "https://example.test/repository.git",
            "https://user:secret@github.com/example/repository.git",
        ):
            with self.subTest(repository=repository):
                registry = copy.deepcopy(self.registry())
                modules = cast("list[dict[str, object]]", registry["modules"])
                modules[0]["repository"] = repository
                with self.assertRaisesRegex(ValueError, "Repository"):
                    build_candidate(
                        registry,
                        observed_at="2026-09-10T00:00:00Z",
                        resolver=self.resolver,
                    )

    def test_missing_core_module_fails_closed(self) -> None:
        registry = copy.deepcopy(self.registry())
        modules = cast("list[dict[str, object]]", registry["modules"])
        registry["modules"] = [
            module for module in modules if module["id"] != "careops-decisions"
        ]

        with self.assertRaisesRegex(ValueError, "Required credentialing MVP modules"):
            build_candidate(
                registry,
                observed_at="2026-09-10T00:00:00Z",
                resolver=self.resolver,
            )

    def test_production_write_registry_fails_closed(self) -> None:
        registry = copy.deepcopy(self.registry())
        registry["productionWrites"] = True

        with self.assertRaisesRegex(ValueError, "prohibit production writes"):
            build_candidate(
                registry,
                observed_at="2026-09-10T00:00:00Z",
                resolver=self.resolver,
            )

    def test_timezone_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            build_candidate(
                self.registry(),
                observed_at="2026-09-10T00:00:00",
                resolver=self.resolver,
            )


if __name__ == "__main__":
    unittest.main()
