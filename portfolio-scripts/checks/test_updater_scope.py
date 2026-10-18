"""Keep parent dependency updates inside the parent publication boundary."""
import fnmatch
import configparser
import subprocess
import tempfile
import os
import re
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

    def test_recursive_clone_does_not_fetch_optional_children(self):
        config = configparser.RawConfigParser()
        config.read(ROOT / '.gitmodules')
        with tempfile.TemporaryDirectory() as path:
            parent = Path(path) / 'parent'
            parent.mkdir()
            subprocess.run(['git', 'init', '-q', str(parent)], check=True)
            for key, value in [('user.name', 'Fictional fixture'), ('user.email', 'fixture@example.invalid')]:
                subprocess.run(['git', '-C', str(parent), 'config', key, value], check=True)
            for section in config.sections():
                self.assertNotIn(config.get(section, 'ignore', fallback='none'), ['dirty', 'all'])
                config.set(section, 'url', str(Path(path) / 'unavailable-child'))
                target = config.get(section, 'path')
                subprocess.run(['git', '-C', str(parent), 'update-index', '--add', '--cacheinfo', '160000,' + 'a' * 40 + ',' + target], check=True)
            with (parent / '.gitmodules').open('w') as handle:
                config.write(handle)
            subprocess.run(['git', '-C', str(parent), 'add', '.gitmodules'], check=True)
            subprocess.run(['git', '-C', str(parent), 'commit', '-qm', 'Fictional module policy'], check=True)
            clone = Path(path) / 'clone'
            env = os.environ.copy()
            env['GIT_ALLOW_PROTOCOL'] = 'file'
            subprocess.run(['git', 'clone', '--quiet', '--recurse-submodules', '--shallow-submodules', str(parent), str(clone)], check=True, env=env, capture_output=True, timeout=20)
            for section in config.sections():
                self.assertFalse((clone / config.get(section, 'path') / '.git').exists())

    def test_direct_ci_pins_match_the_installed_hash_lock(self):
        direct = {}
        locked = {}
        for name, result in [('requirements-ci.txt', direct), ('requirements-ci.lock', locked)]:
            for line in (ROOT / name).read_text().splitlines():
                match = re.match(r'^([A-Za-z0-9_.-]+)==([^ \\]+)', line)
                if match:
                    result[re.sub(r'[-_.]+', '-', match[1]).lower()] = match[2]
        self.assertTrue(direct)
        for package, version in direct.items():
            self.assertEqual(locked.get(package), version, package + ': regenerate the CI hash lock')


if __name__ == '__main__':
    unittest.main()
