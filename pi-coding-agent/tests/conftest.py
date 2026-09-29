from __future__ import annotations

import shutil
from pathlib import Path

import pytest

FIXTURE_INSTALL = Path(__file__).resolve().parent / "fixtures" / "pi-install"


@pytest.fixture
def pi_install(tmp_path: Path) -> tuple[Path, Path]:
    """The fixture package with a `pi` symlink on a private PATH, laid out like Homebrew's."""
    root = tmp_path / "lib" / "node_modules" / "@earendil-works" / "pi-coding-agent"
    shutil.copytree(FIXTURE_INSTALL, root)
    cli = root / "dist" / "bundle" / "cli.js"
    cli.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "pi").symlink_to(cli)
    return bin_dir, root
