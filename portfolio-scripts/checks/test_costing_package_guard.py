"""Exercise the actual migrated package guard using only fictional archives."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[2]


class CostingPackageGuard(unittest.TestCase):
    def test_actual_guard_rejects_wrong_identity_mode_version_publisher_and_parts(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/fcd-source.yml').read_text())
        step = next(s for s in workflow['jobs']['costing-package']['steps']
                    if s.get('name', '').startswith('Verify packaged solution identity'))
        script = step['run'].split('\n', 1)[1].rsplit('PYCODE', 1)[0]

        def document(identity='fictional_canonical', managed='1', version='1.2.3.4', publisher='fictional', component='fictional_table'):
            return ('<ImportExportXml><SolutionManifest><UniqueName>' + identity + '</UniqueName>'
                    '<Managed>' + managed + '</Managed><Version>' + version + '</Version>'
                    '<Publisher><UniqueName>' + publisher + '</UniqueName><CustomizationPrefix>demo</CustomizationPrefix></Publisher>'
                    '<RootComponents><RootComponent type="1" schemaName="' + component + '" /></RootComponents>'
                    '</SolutionManifest></ImportExportXml>')

        cases = [({}, True, True), ({'identity': 'wrong'}, True, False),
                 ({'managed': '0'}, True, False), ({'version': '9.9.9.9'}, True, False),
                 ({'publisher': 'wrong'}, True, False), ({'component': 'wrong'}, True, False),
                 ({}, False, False)]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'powerplatform/solution_bootstrap/src/Other/Solution.xml'
            source.parent.mkdir(parents=True)
            source.write_text(document(managed='0'))
            output = root / 'powerplatform/dist/source-ci/WorkforceCosting-managed.zip'
            output.parent.mkdir(parents=True)
            for changes, complete, success in cases:
                with self.subTest(changes=changes, complete=complete):
                    with zipfile.ZipFile(output, 'w') as archive:
                        archive.writestr('solution.xml', document(**changes))
                        if complete:
                            archive.writestr('customizations.xml', '<xml/>')
                            archive.writestr('[Content_Types].xml', '<xml/>')
                    result = subprocess.run([sys.executable, '-c', script], cwd=root,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, success, result.stderr)


class CostingPackageXml(unittest.TestCase):
    def test_package_xml_rejects_dtd_and_custom_entities(self):
        path = ROOT / 'modules/careops-costing/powerplatform/scripts/compare_solution_packages.py'
        spec = importlib.util.spec_from_file_location('costing_package_compare', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.xml_shape(b'<xml>A &amp; B</xml>')[2], 'A & B')
        for document in [
            '<!DOCTYPE xml [<!ENTITY example "expanded">]><xml>&example;</xml>',
            '<!DOCTYPE xml SYSTEM "file:///fictional/never-read"><xml/>',
        ]:
            for encoding in ['utf-8', 'utf-16']:
                with self.subTest(encoding=encoding, document=document):
                    with self.assertRaisesRegex(ValueError, 'must not contain a DTD'):
                        module.xml_shape(document.encode(encoding))
