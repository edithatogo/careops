"""Keep parent dependency updates inside the parent publication boundary."""
import fnmatch
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class UpdaterScope(unittest.TestCase):
    def test_all_gitlinks_are_excluded_from_parent_python_updates(self):
        config = yaml.safe_load((ROOT / '.github/dependabot.yml').read_text())
        pip = next(x for x in config['updates'] if x['package-ecosystem'] == 'pip')
        patterns = pip['exclude-paths']
        links = json.loads((ROOT / 'PUBLIC_SOURCE_FILES.json').read_text())['gitlinks']
        for path in links:
            with self.subTest(module=path):
                self.assertTrue(any(fnmatch.fnmatchcase(path + '/requirements.txt', p) for p in patterns))
        for name in ['requirements-ci.txt', 'requirements-ci.lock']:
            with self.subTest(parent=name):
                self.assertFalse(any(fnmatch.fnmatchcase(name, p) for p in patterns))


if __name__ == '__main__':
    unittest.main()
