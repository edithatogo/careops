#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=.:sharepoint
python -m compileall -q domain.py workflow_runtime.py sharepoint tests tools
python -m unittest discover -s tests -v
python -m unittest discover -s sharepoint/tests -v
python tools/qualify.py
python tools/demo_runtime.py
