"""Exercise the migrated offline pack contract with fictional package identities."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[2]


class DecisionsPackageGuard(unittest.TestCase):
    def test_pack_precedes_identity_validation_and_wrong_packages_are_refused(self):
        job = yaml.safe_load((ROOT / '.github/workflows/fcd-source.yml').read_text())['jobs']['decisions']
        steps = job['steps']
        pack = next(i for i, step in enumerate(steps) if step.get('name') == 'Pack unmanaged solution')
        guard = next(i for i, step in enumerate(steps) if step.get('name') == 'Verify actual unmanaged package identity')
        self.assertLess(pack, guard)
        self.assertEqual('./scripts/New-ReleaseArtifact.ps1 -Unmanaged', steps[pack]['run'])
        install = next(step for step in steps if step.get('name') == 'Install Power Platform tools')
        self.assertEqual('2.13.1', install['with']['pac-version-override'])
        script = steps[guard]['run'].split('\n', 1)[1].rsplit('PYCODE', 1)[0]

        def manifest(identity='fictional_workspace', managed='0'):
            return '<ImportExportXml><SolutionManifest><UniqueName>' + identity + '</UniqueName><Managed>' + managed + '</Managed></SolutionManifest></ImportExportXml>'

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'powerplatform/solutions/DecisionsWorkspace/Other/Solution.xml'
            source.parent.mkdir(parents=True)
            source.write_text(manifest())
            package = root / 'artifacts/solutions/DecisionsWorkspace/unmanaged/DecisionsWorkspace_unmanaged.zip'
            package.parent.mkdir(parents=True)
            for identity, managed, complete, success in [
                ('fictional_workspace', '0', True, True),
                ('wrong_workspace', '0', True, False),
                ('fictional_workspace', '1', True, False),
                ('fictional_workspace', '0', False, False),
            ]:
                with self.subTest(identity=identity, managed=managed, complete=complete):
                    with zipfile.ZipFile(package, 'w') as archive:
                        archive.writestr('solution.xml', manifest(identity, managed))
                        if complete:
                            archive.writestr('customizations.xml', '<xml/>')
                            archive.writestr('[Content_Types].xml', '<xml/>')
                    result = subprocess.run([sys.executable, '-c', script], cwd=root, capture_output=True)
                    self.assertEqual(result.returncode == 0, success, result.stderr)
