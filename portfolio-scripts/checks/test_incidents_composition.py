"""Fail-closed source and structured-result boundaries; no private checkout needed."""
import importlib.util
import shutil
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('incidents', Path(__file__).resolve().parents[1] / 'qualify_incidents.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
INTEROP_PATH = MODULE.ROOT / 'modules/careops-incidents/powerbi/incidents_dashboard/scripts/incident_interop_v1.py'
INTEROP_SPEC = importlib.util.spec_from_file_location('incidents_interop', INTEROP_PATH)
INTEROP = importlib.util.module_from_spec(INTEROP_SPEC)
INTEROP_SPEC.loader.exec_module(INTEROP)


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


class FictionalCountInterop(unittest.TestCase):
    def setUp(self):
        self.records = [
            {'event_id': f'evt-{index}', 'event_date': '2040-01-15', 'cohort': 'cohort-a'}
            for index in range(3)
        ] + [
            {'event_id': 'evt-small', 'event_date': '2040-02-15', 'cohort': 'cohort-b'},
            *[
                {'event_id': f'evt-large-{index}', 'event_date': '2040-02-15', 'cohort': 'cohort-c'}
                for index in range(3)
            ],
        ]
        self.digest = hashlib.sha256(json.dumps(self.records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def packet(self, **changes):
        args = {
            'records': self.records,
            'source_id': 'fictional-source',
            'source_revision': 'fixture-r1',
            'source_sha256': self.digest,
            'source_as_of': MODULE.date(2040, 2, 28),
            'period_start': MODULE.date(2040, 1, 1),
            'period_end': MODULE.date(2040, 2, 29),
            'as_of': MODULE.date(2040, 3, 1),
            'maximum_age_days': 7,
            'minimum_cell_size': 3,
        }
        args.update(changes)
        return INTEROP.prepare_count_packet(**args)

    def test_suppresses_all_counts_and_denominators_in_small_cell_month(self):
        packet = self.packet()
        INTEROP.validate_count_packet(packet)
        january = [row for row in packet['rows'] if row['month'] == '2040-01']
        february = [row for row in packet['rows'] if row['month'] == '2040-02']
        self.assertEqual(january[0]['count'], 3)
        self.assertEqual(january[0]['denominator'], 3)
        self.assertEqual(february[0]['status'], 'suppressed')
        self.assertIsNone(february[0]['count'])
        self.assertIsNone(february[0]['denominator'])
        self.assertEqual({row['status'] for row in february}, {'suppressed'})
        self.assertEqual(packet['source']['sha256'], self.digest)
        self.assertFalse(packet['generatedFindings'])
        self.assertFalse(packet['operationalData'])

    def test_absent_stale_incompatible_duplicate_and_wrong_digest_refuse(self):
        cases = [
            {'records': None},
            {'source_as_of': MODULE.date(2040, 1, 1)},
            {'source_sha256': '0' * 64},
            {'minimum_cell_size': 0},
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(INTEROP.ContractError):
                self.packet(**changes)
        with self.assertRaises(INTEROP.ContractError):
            self.packet(records=self.records + [self.records[0]])
        with self.assertRaises(INTEROP.ContractError):
            INTEROP.validate_count_packet({**self.packet(), 'schemaVersion': 'careops.incidents.count-packet.v999'})
        packet = self.packet()
        packet['rows'][0]['count'] = 99
        with self.assertRaises(INTEROP.ContractError):
            INTEROP.validate_count_packet(packet)
        packet = self.packet()
        packet['rows'][0]['count'] = 1
        packet['rows'][0]['denominator'] = 3
        canonical = json.dumps({k: v for k, v in packet.items() if k != 'packetSha256'}, sort_keys=True, separators=(',', ':'))
        packet['packetSha256'] = hashlib.sha256(canonical.encode()).hexdigest()
        with self.assertRaises(INTEROP.ContractError):
            INTEROP.validate_count_packet(packet)

    def test_retry_is_deterministic(self):
        self.assertEqual(self.packet(), self.packet())


if __name__ == '__main__':
    unittest.main()
