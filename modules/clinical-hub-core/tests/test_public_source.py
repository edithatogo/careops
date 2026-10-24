import json
import subprocess
from scripts.validate_public_source import validate


def stage(root, text, include=True):
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'example.py').write_text(text)
    (root / 'PUBLIC_SOURCE_FILES.json').write_text(json.dumps(
        ['PUBLIC_SOURCE_FILES.json', 'example.py'] if include else ['PUBLIC_SOURCE_FILES.json']))
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)


def test_unreviewed_file_is_rejected(tmp_path):
    stage(tmp_path, '# fictional example', include=False)
    assert any('Unreviewed' in e for e in validate(tmp_path))


def test_staged_email_is_rejected_even_if_working_copy_is_clean(tmp_path):
    stage(tmp_path, 'person@' + 'nonfictional.org')
    (tmp_path / 'example.py').write_text('# clean working copy')
    assert any('email' in e for e in validate(tmp_path))


def test_fictional_source_is_allowed(tmp_path):
    stage(tmp_path, 'person@example.invalid')
    assert validate(tmp_path) == []
