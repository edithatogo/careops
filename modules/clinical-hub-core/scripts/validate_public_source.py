"""Validate the reviewed source allowlist; not a complete confidentiality classifier."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    tracked = {p for p in tracked if p}
    prefix = subprocess.check_output(['git', 'rev-parse', '--show-prefix'], cwd=root).decode().strip()
    allowed = set(json.loads(subprocess.check_output(['git', 'show', ':' + prefix + 'PUBLIC_SOURCE_FILES.json'], cwd=root)))
    errors = [f'Unreviewed tracked path: {p}' for p in sorted(tracked - allowed)]
    errors += [f'Missing reviewed path: {p}' for p in sorted(allowed - tracked)]
    forbidden = {'private', 'data', 'deployment', '.flowagent', '.vscode'}
    extensions = {'.docx', '.pdf', '.zip', '.xlsx', '.xlsb', '.pem', '.pfx', '.token'}
    for name in sorted(tracked):
        p = root / name
        mode = subprocess.check_output(['git', 'ls-files', '-s', '--', name], cwd=root).decode().split()[0]
        if mode != '100644' and mode != '100755' or set(Path(name).parts) & forbidden or p.suffix.lower() in extensions:
            errors.append(f'Private/binary/symlink path: {name}')
            continue
        try:
            text = subprocess.check_output(['git', 'show', ':' + prefix + name], cwd=root).decode('utf-8')
        except (UnicodeError, OSError):
            errors.append(f'Non-text source: {name}')
            continue
        for email in re.findall(r'[\w.+-]{1,80}@[\w.-]{1,80}\.[A-Za-z]{2,20}', text):
            if not email.endswith(('.invalid', '.test', '@example.com')):
                errors.append(f'Non-fictional email in {name}')
        if any(url not in {'https://fictional-example.sharepoint.com', 'http://fictional-example.sharepoint.com'} for url in re.findall(r'https?://[a-zA-Z0-9-]+\.(?:sharepoint\.com|crm\d*\.dynamics\.com)', text)):
            errors.append(f'Tenant URL in {name}')
    return errors


if __name__ == '__main__':
    errors = validate()
    print(json.dumps({'status': 'FAIL' if errors else 'PASS', 'errors': errors}, indent=2))
    raise SystemExit(bool(errors))
