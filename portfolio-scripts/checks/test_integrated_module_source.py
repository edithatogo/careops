"""Guard the cutover against missing source, drift and old gitlinks."""
import configparser
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('integrated_source', ROOT / 'scripts/integrated_module_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IntegratedSource(unittest.TestCase):
    def test_missing_corrupt_and_residual_gitlink_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'portfolio').mkdir()
            components = []
            entries = {}
            for name, prefix in module.MODULES.items():
                directory = root / prefix
                directory.mkdir(parents=True)
                (directory / 'README.md').write_text('fictional source\n')
                digest = hashlib.sha256((directory / 'README.md').read_bytes()).hexdigest()
                provenance = {'sourceCommit': '1' * 40, 'sourceFiles': {'README.md': digest}, 'maintainedFiles': {'README.md': digest}}
                (directory / 'SOURCE_PROVENANCE.json').write_text(json.dumps(provenance))
                components.append({'name': name, 'path': prefix, 'sourceBaseline': '1' * 40, 'materialization': 'integrated-source'})
                entries[prefix] = b''.join(f'100644 {"2" * 40} 0\t{prefix}/{p}\0'.encode() for p in ('README.md', 'SOURCE_PROVENANCE.json'))
            qualification = {'modules': dict.fromkeys(module.MODULES, '1' * 40), 'modulePaths': module.MODULES}
            (root / 'portfolio/public-runtime-compatibility.json').write_text(json.dumps(qualification))
            (root / 'portfolio/repos.json').write_text(json.dumps({'components': components}))
            (root / 'PUBLIC_SOURCE_FILES.json').write_text(json.dumps({'gitlinks': {}}))
            with patch.object(module.subprocess, 'check_output', side_effect=lambda command: entries[command[-1]]):
                self.assertEqual(module.validate_integrated_modules(root), [])
                for prefix in module.MODULES.values():
                    with self.subTest(module=prefix):
                        path = root / prefix / 'README.md'
                        original_entries = entries[prefix]
                        path.write_text('changed source\n')
                        self.assertTrue(module.validate_integrated_modules(root))
                        path.unlink()
                        self.assertTrue(module.validate_integrated_modules(root))
                        path.write_text('fictional source\n')
                        entries[prefix] = f'160000 {"2" * 40} 0\t{prefix}\0'.encode()
                        self.assertTrue(module.validate_integrated_modules(root))
                        entries[prefix] = original_entries
                        self.assertEqual(module.validate_integrated_modules(root), [])

    def test_current_delivery_never_fetches_absorbed_legacy_repositories(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            text = path.read_text()
            for name in module.MODULES:
                for suffix in ('', '-public'):
                    self.assertNotIn(f'repository: edithatogo/{name}{suffix}\n', text, path.name)


class SourceTopologyDocumentation(unittest.TestCase):
    """Check current entry points; dated historical receipts are not rewritten."""

    def setUp(self):
        self.components = json.loads((ROOT / 'portfolio/repos.json').read_text(encoding='utf-8'))['components']
        self.gitmodules = configparser.ConfigParser(interpolation=None)
        self.gitmodules.read_string((ROOT / '.gitmodules').read_text(encoding='utf-8'))
        self.paths = {self.gitmodules.get(section, 'path') for section in self.gitmodules.sections()}

    def assert_current_table(self, text, state_column):
        rows = {}
        for line in text.splitlines():
            if not line.startswith('| `'):
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            name = cells[0].strip('`')
            self.assertNotIn(name, rows, f'duplicate current module row: {name}')
            rows[name] = cells
        for component in self.components:
            name = component['name']
            with self.subTest(module=name):
                self.assertIn(name, rows, f'missing current module row: {name}')
                row = rows[name]
                self.assertGreater(len(row), state_column)
                self.assertEqual(row[1].strip('`').rstrip('/'), component['path'])
                expected = {'integrated-source': 'Integrated source', 'submodule': 'Optional pinned submodule'}[component['materialization']]
                self.assertTrue(row[state_column].startswith(expected), f'{name}: expected {expected}, got {row[state_column]}')

    def test_readme_topology_matches_registry(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('## Repository topology\n', text)
        current = text.split('## Repository topology\n', 1)[1].split('\n## ', 1)[0]
        self.assert_current_table(current, 2)

    def test_module_catalogue_current_table_matches_registry(self):
        text = (ROOT / 'portfolio/module-catalog.md').read_text(encoding='utf-8')
        self.assert_current_table(text, 3)

    def test_readme_checkout_examples_use_only_actual_optional_paths(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        commands = [line.strip() for line in text.splitlines() if line.strip().startswith('git submodule update ')]
        self.assertTrue(commands, 'expected explicit optional-checkout examples')
        for command in commands:
            with self.subTest(command=command):
                tokens = shlex.split(command)
                self.assertIn('--', tokens, 'use explicit path separator in checkout examples')
                self.assertIn('--checkout', tokens)
                self.assertNotIn('--remote', tokens)
                paths = tokens[tokens.index('--') + 1:]
                self.assertTrue(paths, 'do not implicitly initialise the whole family')
                self.assertTrue(set(paths) <= self.paths, f'obsolete or unregistered submodule path: {paths}')

    def test_module_gitlinks_match_registry_without_initialising_children(self):
        registered_paths = {item['path'] for item in self.components}
        expected = {item['path'] for item in self.components if item['materialization'] == 'submodule'}
        self.assertEqual(self.paths & registered_paths, expected)

    def test_integrated_delivery_locations_match_registry(self):
        delivery = json.loads((ROOT / 'portfolio/delivery-catalog.json').read_text(encoding='utf-8'))['modules']
        by_name = {}
        for item in delivery:
            self.assertNotIn(item['module'], by_name, 'duplicate delivery module')
            by_name[item['module']] = item
        for component in self.components:
            if component['materialization'] != 'integrated-source':
                continue
            with self.subTest(module=component['name']):
                self.assertIn(component['name'], by_name)
                item = by_name[component['name']]
                self.assertEqual(item['sourceKind'], 'integrated-source')
                self.assertEqual(item['repository'].removesuffix('.git'), component['github'].removesuffix('.git'))
                locations = [item[key] for key in ('path', 'sourcePath') if key in item]
                self.assertTrue(locations, 'integrated delivery entry needs a source location')
                self.assertTrue(all(path.rstrip('/') == component['path'] for path in locations))
                self.assertEqual(item['nativeQualification'], 'not-established-by-catalog')
