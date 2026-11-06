"""Guard the cutover against missing source, drift and old gitlinks."""
import hashlib
import importlib.util
import json
from pathlib import Path
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
                path = root / 'careops-approve/README.md'
                path.write_text('changed source\n')
                self.assertTrue(module.validate_integrated_modules(root))
                path.unlink()
                self.assertTrue(module.validate_integrated_modules(root))
                path.write_text('fictional source\n')
                entries['careops-approve'] = f'160000 {"2" * 40} 0\tcareops-approve\0'.encode()
                self.assertTrue(module.validate_integrated_modules(root))

    def test_current_delivery_never_fetches_legacy_process_or_approve(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            text = path.read_text()
            self.assertNotIn('repository: edithatogo/careops-process\n', text, path.name)
            self.assertNotIn('repository: edithatogo/careops-approve\n', text, path.name)
