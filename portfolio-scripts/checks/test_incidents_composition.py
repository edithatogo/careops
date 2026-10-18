"""Fail-closed source and structured-result boundaries; no private checkout needed."""
import importlib.util
import shutil
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('incidents', Path(__file__).resolve().parents[1] / 'qualify_incidents.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SourceBoundary(unittest.TestCase):
    def test_pin_matches_parent_inventory(self):
        self.assertEqual(MODULE.read_pin()['visibility'], 'public')

    def test_absent_checkout_is_refused(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(ValueError):
                MODULE.check_source(Path(path), 'a' * 40)

    def test_wrong_baseline_and_changed_source_are_refused(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path) / 'module'
            shutil.copytree(MODULE.ROOT / 'modules/careops-incidents', root)
            pin = MODULE.read_pin()
            MODULE.check_source(root, pin['commit'])
            with self.assertRaises(ValueError):
                MODULE.check_source(root, 'a' * 40)
            source = root / 'LICENSE'
            source.write_text('unreviewed change')
            with self.assertRaises(ValueError):
                MODULE.check_source(root, pin['commit'])

    def test_standalone_cli_and_output_preservation(self):
        source_root = MODULE.ROOT / 'modules/careops-incidents'
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            module = root / 'standalone'
            shutil.copytree(source_root, module)
            fixture = root / 'fictional.csv'
            with fixture.open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=['incident_date', 'details_clean'])
                writer.writeheader()
                writer.writerows([{'incident_date': '2040-01-31', 'details_clean': 'heparin medication'}, {'incident_date': '2040-02-29', 'details_clean': 'fictional fixture'}])
            for name in ['build_surveillance_outputs_v1_20260429.py', 'build_health_concept_outputs_v1_20260429.py']:
                script = module / 'powerbi/incidents_dashboard/scripts' / name
                output = root / name
                args = [sys.executable, str(script), '--source', str(fixture), '--output-dir', str(output), '--start', '2040-01-01', '--end', '2040-02-29']
                with self.subTest(script=name):
                    run = subprocess.run(args, cwd=root, capture_output=True, text=True)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    before = {p.name: p.read_bytes() for p in output.iterdir()}
                    self.assertTrue(before)
                    retry = subprocess.run(args, cwd=root, capture_output=True, text=True)
                    self.assertNotEqual(retry.returncode, 0)
                    self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})
                    fixture_args = list(args)
                    fixture_args[fixture_args.index('--source') + 1] = str(root / 'absent.csv')
                    self.assertNotEqual(subprocess.run(fixture_args, cwd=root, capture_output=True).returncode, 0)
                    bad_dates = list(args)
                    bad_dates[bad_dates.index('--start') + 1] = '2041-01-01'
                    self.assertNotEqual(subprocess.run(bad_dates, cwd=root, capture_output=True).returncode, 0)
                    self.assertNotEqual(subprocess.run([sys.executable, str(script)], cwd=root, capture_output=True).returncode, 0)

    def test_deployment_bindings_are_unconfigured(self):
        root = MODULE.ROOT / 'modules/careops-incidents/powerbi/incidents_dashboard/pbip/DatixIncidentDashboard.SemanticModel/definition'
        self.assertIn('RootDataPath = ""', (root / 'expressions.tmdl').read_text())
        targets = (root / 'tables/ValidationTargets.tmdl').read_text()
        for key in ['expected_cleaned_row_count', 'validated_heparin_incidents']:
            line = next(line for line in targets.splitlines() if key in line)
            self.assertIn('null, "Not configured"', line)
        measures = (root / 'tables/MeasureTable.tmdl').read_text()
        self.assertIn('ISBLANK ( [Expected Cleaned Row Count] )', measures)
        self.assertIn('ISBLANK ( [Heparin Reconciliation Target] )', measures)

    def test_structural_issue_cannot_hide_behind_pass_status(self):
        good = {'Status': 'Pass', 'PackageExists': True, **{k: [] for k in ['MissingRequiredPaths', 'JsonParseFailures', 'PageTreeIssues', 'SchemaIssues', 'ModelIssues']}}
        MODULE.validate_structure(good)
        for key in ['MissingRequiredPaths', 'JsonParseFailures', 'PageTreeIssues', 'SchemaIssues', 'ModelIssues']:
            with self.subTest(key=key), self.assertRaises(ValueError):
                MODULE.validate_structure({**good, key: ['fictional issue']})
            incomplete = dict(good)
            del incomplete[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                MODULE.validate_structure(incomplete)
        with self.assertRaises(ValueError):
            MODULE.validate_structure({**good, 'Status': 'Review'})


if __name__ == '__main__':
    unittest.main()
