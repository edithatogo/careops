"""Private staging: visually qualified, reproducibly rendered PDF image evidence.

Verification binds the attestation to bytes; it cannot verify human perception.
"""
import hashlib
import re
import shutil
import subprocess
import struct
import tempfile
from datetime import datetime
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_image_witness(witness, original_bytes, *, executable=None):
    if not isinstance(witness, dict) or witness.get('kind') != 'pdf-visual-transcription-v1':
        raise ValueError('Unsupported image witness')
    if not isinstance(original_bytes, bytes) or not original_bytes.startswith(b'%PDF-'):
        raise ValueError('PDF bytes required')
    if sha(original_bytes) != witness.get('pdfSHA256'):
        raise ValueError('PDF hash mismatch')
    page, dpi, crop = witness.get('page'), witness.get('dpi'), witness.get('crop')
    if type(page) is not int or not 1 <= page <= 10000 or type(dpi) is not int or not 36 <= dpi <= 300:
        raise ValueError('Invalid page or rendering resolution')
    if not isinstance(crop, dict) or set(crop) != {'x', 'y', 'width', 'height'} or any(type(crop[k]) is not int for k in crop):
        raise ValueError('Integer crop rectangle required')
    if not (0 <= crop['x'] <= 20000 and 0 <= crop['y'] <= 20000 and 1 <= crop['width'] <= 20000 and 1 <= crop['height'] <= 20000):
        raise ValueError('Invalid crop bounds')
    transcription = witness.get('transcription')
    if not isinstance(transcription, str) or not transcription.strip() or len(transcription) > 4000:
        raise ValueError('Exact visual transcription required')
    reviewer = witness.get('reviewer')
    if not isinstance(reviewer, dict) or reviewer.get('method') != 'direct-visual-review' or reviewer.get('affirmedExactTranscription') is not True or not isinstance(reviewer.get('identity'), str) or not reviewer['identity'].strip():
        raise ValueError('Named visual reviewer affirmation required; OCR alone is insufficient')
    try:
        instant = datetime.fromisoformat(reviewer['reviewedAtUtc'].replace('Z', '+00:00'))
        if instant.utcoffset() is None or instant.utcoffset().total_seconds() != 0:
            raise ValueError()
    except (KeyError, AttributeError, TypeError, ValueError):
        raise ValueError('UTC reviewer timestamp required') from None
    executable = executable or shutil.which('pdftoppm')
    if not executable:
        raise ValueError('pdftoppm renderer unavailable on PATH')
    try:
        version = subprocess.run([executable, '-v'], capture_output=True, timeout=10, check=True)
        version_line = (version.stderr or version.stdout).decode('utf-8').splitlines()[0]
        if version_line != witness.get('rendererVersion') or not re.match(r'^pdftoppm version ', version_line):
            raise ValueError('Renderer version mismatch')
        with tempfile.TemporaryDirectory(prefix='ppg-image-witness-') as d:
            source = Path(d)/'source.pdf'; source.write_bytes(original_bytes)
            prefix = Path(d)/'page'
            common = [executable, '-f', str(page), '-l', str(page), '-singlefile', '-r', str(dpi), '-png']
            subprocess.run([*common, str(source), str(prefix)], capture_output=True, timeout=60, check=True)
            rendered = prefix.with_suffix('.png').read_bytes()
            if rendered[:8] != b'\x89PNG\r\n\x1a\n' or len(rendered) < 24:
                raise ValueError('Invalid rendered PNG')
            width, height = struct.unpack('>II', rendered[16:24])
            if crop['x'] + crop['width'] > width or crop['y'] + crop['height'] > height:
                raise ValueError('Crop exceeds page bounds')
            prefix = Path(d)/'crop'
            subprocess.run([*common, '-x', str(crop['x']), '-y', str(crop['y']), '-W', str(crop['width']), '-H', str(crop['height']), str(source), str(prefix)], capture_output=True, timeout=60, check=True)
            cropped = prefix.with_suffix('.png').read_bytes()
    except (OSError, subprocess.SubprocessError, IndexError) as error:
        raise ValueError('PDF page rendering failed') from error
    if sha(rendered) != witness.get('pageRenderSHA256') or sha(cropped) != witness.get('cropSHA256'):
        raise ValueError('Rendered image or crop hash mismatch')
    return True
