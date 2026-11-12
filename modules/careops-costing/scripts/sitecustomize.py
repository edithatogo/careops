"""Make repository-local packages importable for directly executed scripts.

Python loads ``sitecustomize`` after initialising ``sys.path``. This small,
repository-local bootstrap adds the project root when a script is invoked as
``python scripts/<name>.py`` without installing the package.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
