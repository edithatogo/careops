"""Run explicit focused checks without treating cached selection as full proof."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


def commands(runner: str, mode: str, selectors: list[str], tests_root: str,
             cache_dir: str, no_cov: bool = False) -> list[list[str]]:
    if mode == 'focused' and not selectors:
        raise ValueError('Focused mode requires explicit test files, nodes or discovery patterns')
    if mode != 'focused' and selectors:
        raise ValueError('Use focused mode for explicit selectors')
    if any(s.startswith('-') or Path(s.split('::')[0]).is_absolute()
           or '..' in Path(s.split('::')[0]).parts for s in selectors):
        raise ValueError('Selectors must be test identities, not options or parent traversal')
    if runner == 'unittest':
        if mode not in {'focused', 'full'}:
            raise ValueError('Unittest uses explicit discovery patterns; pytest cache modes do not apply')
        return [[sys.executable, '-m', 'unittest', 'discover', '-s', tests_root,
                 '-p', pattern, '-v'] for pattern in (selectors or ['test_*.py'])]
    flags = {
        'focused': [],
        'last-failed': ['--last-failed', '--last-failed-no-failures=none'],
        'failed-first': ['--failed-first'],
        'stepwise': ['--stepwise'],
        'full': [],
    }
    if mode not in flags:
        raise ValueError('Unsupported mode')
    args = [sys.executable, '-m', 'pytest', '-o', f'cache_dir={cache_dir}']
    if no_cov and mode not in {'full', 'failed-first'}:
        args.append('--no-cov')
    return [args + flags[mode] + (selectors if mode == 'focused' else [tests_root])]


def cache_location(root: Path) -> str:
    digest = hashlib.sha256(sys.version.encode())
    digest.update(str(Path(sys.prefix).resolve()).encode())
    for name in ('.python-version', 'pyproject.toml', 'pytest.ini', 'conftest.py',
                 'uv.lock', 'requirements-ci.lock', 'requirements-ci.txt'):
        path = root / name
        digest.update(name.encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return str(root / '.pytest_cache' / digest.hexdigest()[:20])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runner', choices=['pytest', 'unittest'], required=True)
    parser.add_argument('--mode', choices=['focused', 'last-failed', 'failed-first',
                                         'stepwise', 'full'], default='focused')
    parser.add_argument('--tests-root', default='tests')
    parser.add_argument('selectors', nargs='*')
    args = parser.parse_args()
    root = Path.cwd().resolve()
    if sys.version_info[:2] != (3, 15):
        parser.error('Use the selected repository-local Python 3.15 interpreter')
    if sys.prefix == sys.base_prefix or not Path(sys.prefix).resolve().is_relative_to(root):
        parser.error('Use a virtual environment within the repository working directory')
    test_root = (root / args.tests_root).resolve()
    if not test_root.is_relative_to(root) or not test_root.is_dir():
        parser.error('Tests root must be an existing directory within this repository')
    try:
        selected = commands(args.runner, args.mode, args.selectors, args.tests_root,
                            cache_location(root), importlib.util.find_spec('pytest_cov') is not None)
    except ValueError as error:
        parser.error(str(error))
    if args.mode in {'focused', 'last-failed', 'stepwise'}:
        print('SELECTED_SCOPE_ONLY: zero cached failures is not full-suite verification.', flush=True)
    else:
        print('FULL_SCOPE_REQUESTED: retain failure, skip and xfail reporting.', flush=True)
    environment = os.environ.copy()
    # Do not inherit automatic rerun policy that could hide the first failure.
    if args.runner == 'pytest' and importlib.util.find_spec('pytest_rerunfailures') is not None:
        for command in selected:
            command[3:3] = ['--reruns=0', '--force-reruns=0']
    for command in selected:
        result = subprocess.run(command, env=environment, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
