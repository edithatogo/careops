"""Focused fictional outbound, checkpoint and evidence checks. Apache-2.0."""
import importlib.util
from pathlib import Path
import tempfile
import json
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("nim_worker", Path(__file__).parents[1] / "scripts/ppg_nim_worker.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorkerTests(unittest.TestCase):
    def test_exhausted_budget_exits_even_when_access_failure_pauses(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root)
            with patch.object(w, "infer", return_value=("failed", {"error": "http", "status": 403})) as infer:
                w.run(root, root / "unused", workers=1, max_requests=1, watch=True)
                self.assertEqual(infer.call_count, 1)
            self.assertTrue(w.status(root)["paused"])
            self.assertFalse(w.status(root)["active"])

    def test_openrouter_has_separate_fingerprints_and_private_guard(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root, (w.OPENROUTER_LIGHTNING,), "openrouter")
            with w.database(root) as db:
                job = dict(db.execute("SELECT * FROM jobs LIMIT 1").fetchone())
            body = w.qualify_job(job)
            self.assertNotEqual(w.digest(w.LIGHTNING, body), job["fingerprint"])
            job["body"] = '{"source":"private source","target":"private target"}'
            with patch.object(w, "credential") as key:
                with self.assertRaises(ValueError):
                    w.infer(job, root / "unused")
                key.assert_not_called()

    def test_openrouter_request_pins_provider_and_disables_cache(self):
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root)
            with w.database(root) as db:
                job = dict(db.execute("SELECT * FROM jobs WHERE expected='references'").fetchone())
            body = json.loads(job["body"])
            raw = {"provider": "Nvidia", "model": w.FREE_LIGHTNING, "usage": {"cost": 0},
                   "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
                       "relation": "references", "source_quote": body["source"], "target_quote": body["target"], "limitation": "fictional"})}}]}
            response = MagicMock()
            response.__enter__.return_value = response
            response.status = 200
            response.read.return_value = json.dumps(raw).encode()
            opener = MagicMock()
            opener.open.return_value = response
            with patch.object(w, "credential", return_value="fictional"), patch.object(w, "verify_openrouter_route"), patch.object(w.urllib.request, "build_opener", return_value=opener):
                self.assertEqual(w.infer(job, root / "unused")[0], "succeeded")
            request = opener.open.call_args.args[0]
            payload = json.loads(request.data)
            self.assertEqual(payload["provider"], w.FREE_POLICY)
            self.assertEqual(request.get_header("X-openrouter-cache"), "false")
            self.assertEqual(request.full_url, w.OPENROUTER_ENDPOINT)

    def test_paid_routes_rejected_before_credentials_or_network(self):
        for transport, model in (("openrouter", w.OPENROUTER_LIGHTNING), ("nvidia", w.LIGHTNING)):
            with self.subTest(transport=transport), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                w.seed(root, (model,), transport)
                with w.database(root) as db:
                    job = dict(db.execute("SELECT * FROM jobs LIMIT 1").fetchone())
                with patch.object(w, "credential") as key, patch.object(w.urllib.request, "build_opener") as network:
                    with self.assertRaisesRegex(ValueError, "free-only"):
                        w.infer(job, root / "unused")
                    with self.assertRaisesRegex(ValueError, "free-only"):
                        w.run(root, root / "unused")
                    key.assert_not_called()
                    network.assert_not_called()
                self.assertEqual(w.status(root)["attempts"], 0)

    def test_zero_price_requires_both_explicit_finite_zero_prices(self):
        self.assertTrue(w.zero_priced({"pricing": {"prompt": "0", "completion": "0.0"}}))
        for pricing in ({}, {"prompt": "0"}, {"prompt": "0", "completion": "0.001"},
                        {"prompt": "NaN", "completion": "0"}, {"prompt": None, "completion": 0}):
            self.assertFalse(w.zero_priced({"pricing": pricing}))

    def test_free_endpoint_without_strict_zdr_cannot_send_inference(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"data": []}'
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(w, "_route_verified_at", 0), patch.object(w.urllib.request, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "strict ZDR"):
                w.verify_openrouter_route("fictional")
        self.assertEqual(opener.open.call_count, 1)
        self.assertEqual(opener.open.call_args.args[0].get_method(), "GET")

    def test_seed_replay_and_private_content_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root)
            w.seed(root)
            self.assertEqual(w.status(root)["counts"], {"pending": 4})
            with w.database(root) as db:
                job = dict(db.execute("SELECT * FROM jobs LIMIT 1").fetchone())
            w.qualify_job(job)
            job["body"] = '{"source":"private document","target":"private policy"}'
            with self.assertRaisesRegex(ValueError, "fictional fixture"):
                w.qualify_job(job)

    def test_citations_and_uncertainty_must_be_supported(self):
        body = w.packet(w.CASES["reference"])
        finding = {"relation": "references", "source_quote": "not in text", "target_quote": body["target"], "limitation": ""}
        with self.assertRaisesRegex(ValueError, "quotation"):
            w.validate_result(finding, body, "references")
        with self.assertRaisesRegex(ValueError, "explicit"):
            w.validate_result({"relation": "uncertain", "source_quote": "", "target_quote": "", "limitation": ""}, body, "uncertain")

    def test_crash_is_not_resent_and_completed_work_is_cached(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root)
            with w.database(root) as db:
                db.execute("UPDATE jobs SET state='running'")
            with patch.object(w, "infer") as infer:
                w.run(root, root / "unused", watch=False)
                infer.assert_not_called()
            self.assertEqual(w.status(root)["counts"], {"uncertain": 4})
            with w.database(root) as db:
                db.execute("UPDATE jobs SET state='succeeded'")
            with patch.object(w, "infer") as infer:
                w.run(root, root / "unused", watch=False)
                infer.assert_not_called()

    def test_stop_prevents_dispatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root)
            (root / "STOP").touch()
            with patch.object(w, "infer") as infer:
                w.run(root, root / "unused")
                infer.assert_not_called()

    def test_partial_batch_failure_is_visible_and_other_results_survive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w.seed(root)
            def response(job, _):
                if job["expected"] == "prerequisite":
                    return "uncertain", {"error": "transport_outcome_unknown"}
                return "succeeded", {"fictional": True}
            with patch.object(w, "infer", side_effect=response) as infer:
                w.run(root, root / "unused", max_requests=2)
                self.assertEqual(infer.call_count, 2)
            self.assertEqual(w.status(root)["counts"], {"pending": 2, "succeeded": 1, "uncertain": 1})
            with patch.object(w, "infer", side_effect=response) as infer:
                w.run(root, root / "unused")
                self.assertEqual(infer.call_count, 2)
            self.assertEqual(w.status(root)["counts"], {"succeeded": 3, "uncertain": 1})


if __name__ == "__main__":
    unittest.main()
