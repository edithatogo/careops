"""Resolve isolated dependency candidates and retain exact versions, digests and outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess


def versions(text):
    return dict(re.findall(r'^([A-Za-z0-9_.-]+)==([^\s;\\]+)', text, re.MULTILINE))


def resolve(destination, *, preview=False):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Use a fresh candidate directory; preserve earlier evidence')
    destination.mkdir(parents=True)
    baseline = Path('requirements-dev.lock').read_bytes()
    receipt = {'python': platform.python_version(), 'preview_allowed': preview,
               'baseline_sha256': hashlib.sha256(baseline).hexdigest(), 'status': 'resolving'}
    try:
        receipt['uv'] = subprocess.check_output(['uv', '--version'], text=True).strip()
        cmd = ['uv', 'pip', 'compile', '--upgrade', '--generate-hashes', '--python', platform.python_version(),
               'requirements-dev.txt', '-o', str(destination / 'requirements.lock')]
        if preview:
            cmd += ['--prerelease', 'allow']
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        candidate = (destination / 'requirements.lock').read_bytes()
        receipt.update(status='resolved_not_promoted', versions=versions(candidate.decode()),
                       candidate_sha256=hashlib.sha256(candidate).hexdigest())
        if not receipt['versions']:
            raise ValueError('No exact versions resolved')
    except Exception as error:
        receipt.update(status='resolution_failed', error_type=type(error).__name__)
        raise
    finally:
        receipt['baseline_unchanged'] = Path('requirements-dev.lock').read_bytes() == baseline
        (destination / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if not receipt['baseline_unchanged']:
            raise RuntimeError('Qualified baseline changed')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True)
    p.add_argument('--preview', action='store_true')
    args = p.parse_args()
    resolve(args.output, preview=args.preview)
