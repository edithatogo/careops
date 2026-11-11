"""Offline fake-API regressions for exact-head GitHub Actions evidence."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from frontier_ci_collect import CollectionError, REPOSITORY, collect, gh_api

SHA = "a" * 40


def check(name="Security gate", ident=101, conclusion="success"):
    return {"id": ident, "name": name, "head_sha": SHA, "status": "completed",
            "conclusion": conclusion, "app": {"slug": "github-actions"}}


class FakeAPI:
    def __init__(self, protection=True, billing=False, fail=False, stale=False):
        self.protection = protection
        self.billing = billing
        self.fail = fail
        self.stale = stale
        self.calls = []

    def __call__(self, path):
        self.calls.append(path)
        if path.endswith("/protection/required_status_checks"):
            if not self.protection:
                raise CollectionError("forbidden")
            return {"contexts": ["Security gate"], "checks": []}
        if "/check-runs?" in path:
            return {"total_count": 1, "check_runs": [
                check(conclusion="failure" if self.fail else "success")]}
        if "/actions/jobs/" in path:
            return {"id": 101, "run_id": 501, "steps": [
                {"status": "completed", "conclusion": "failure" if self.fail else "success"}]}
        if "/actions/runs/" in path:
            return {"head_sha": "b"*40 if self.stale else SHA}
        if "/annotations?" in path:
            return [{"message": "recent account payments have failed; internal confidential detail"}
                    ] if self.billing else []
        raise AssertionError("unexpected API path")


class CollectorTests(unittest.TestCase):
    def test_verified_executed_checks_still_never_authorise_merge(self):
        result = collect(SHA, FakeAPI())
        self.assertEqual(result["state"], "passed-executed")
        self.assertTrue(result["branch_protection_verified"])
        self.assertFalse(result["protected_merge_qualified"])
        self.assertFalse(result["input_provenance_verified"])

    def test_missing_protection_never_proves_qualification(self):
        result = collect(SHA, FakeAPI(protection=False))
        self.assertFalse(result["branch_protection_verified"])
        self.assertNotEqual(result["state"], "passed-executed")

    def test_billing_message_never_appears_in_results(self):
        result = collect(SHA, FakeAPI(billing=True, fail=True))
        self.assertEqual(result["state"], "executed-failure")
        self.assertNotIn("confidential detail", str(result))

    def test_executed_failure_is_not_billing_only(self):
        self.assertEqual(collect(SHA, FakeAPI(fail=True))["state"], "executed-failure")

    def test_stale_run_refused_to_qualify(self):
        self.assertNotEqual(collect(SHA, FakeAPI(stale=True))["state"], "passed-executed")

    def test_duplicate_or_incomplete_pages_rejected(self):
        class Duplicates(FakeAPI):
            def __call__(self, path):
                if "/check-runs?" in path:
                    return {"total_count": 2, "check_runs": [check(), check()]}
                return super().__call__(path)
        with self.assertRaisesRegex(CollectionError, "duplicate"):
            collect(SHA, Duplicates())

    def test_no_steps_unverified(self):
        class EmptySteps(FakeAPI):
            def __call__(self, path):
                if "/actions/jobs/" in path:
                    return {"id": 101, "run_id": 501, "steps": []}
                return super().__call__(path)
        self.assertNotEqual(collect(SHA, EmptySteps())["state"], "passed-executed")

    def test_api_requests_remain_read_only_and_source_qualified(self):
        api = FakeAPI()
        collect(SHA, api)
        self.assertTrue(api.calls)
        self.assertTrue(all(path.startswith(f"/repos/{REPOSITORY}/") for path in api.calls))
        self.assertTrue(any(f"/commits/{SHA}/check-runs" in p for p in api.calls))

    def test_reject_invalid_source_revision(self):
        for value in ["main", "A"*40, "../" + SHA]:
            with self.subTest(value=value), self.assertRaises(CollectionError):
                collect(value, FakeAPI())

    def test_protection_with_empty_required_checks_is_not_verified(self):
        class EmptyProtection(FakeAPI):
            def __call__(self, path):
                if path.endswith("/protection/required_status_checks"):
                    return {"contexts": [], "checks": []}
                return super().__call__(path)
        result = collect(SHA, EmptyProtection())
        self.assertFalse(result["branch_protection_verified"])

    def test_gh_api_refuses_unsafe_paths_before_invocation(self):
        with patch("frontier_ci_collect.subprocess.run") as run:
            with self.assertRaises(CollectionError):
                gh_api("/repos/edithatogo/careops/../secrets")
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
