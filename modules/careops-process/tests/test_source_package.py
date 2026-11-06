# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0

"""Build fictional packages to verify source/archive boundaries offline."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("target", ["sdist", "wheel"])
def test_packages_exclude_hypothesis_cache(tmp_path: Path, target: str) -> None:
    """Generated test state never ships, while code and required notices remain."""
    if importlib.util.find_spec("hatchling") is None:
        pytest.skip("Archive regression requires the repository's optional locked build group")
    for name in ("pyproject.toml", ".gitignore", "LICENSE", "NOTICE"):
        shutil.copyfile(name, tmp_path / name)
    package = tmp_path / "src/careops_process"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""Fictional packaging fixture."""\n')
    cache = tmp_path / ".hypothesis/constants"
    cache.mkdir(parents=True)
    (cache.parent / ".gitignore").write_text("*\n")
    (cache / "fictional-generated-state").write_text("fictional local cache; not source\n")
    subprocess.run(  # noqa: S603 - fixed local build backend and pytest-owned fictional paths
        [sys.executable, "-m", "hatchling", "build", "--target", target],
        cwd=tmp_path,
        env={**os.environ, "SOURCE_DATE_EPOCH": "1793059200"},
        capture_output=True,
        check=True,
    )
    artifact = next((tmp_path / "dist").iterdir())
    if target == "sdist":
        with tarfile.open(artifact) as archive:
            names = [item.name.partition("/")[2] for item in archive if item.isfile()]
        assert "src/careops_process/__init__.py" in names
        assert {"LICENSE", "NOTICE"}.issubset(names)
    else:
        with zipfile.ZipFile(artifact) as archive:
            names = archive.namelist()
        assert "careops_process/__init__.py" in names
        assert all(
            any(name.endswith("/licenses/" + item) for name in names)
            for item in ("LICENSE", "NOTICE")
        )
    assert not any(name.startswith(".hypothesis/") for name in names)
