"""Tests for scripts/check-skill-frontmatter.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check-skill-frontmatter.py"

_spec = importlib.util.spec_from_file_location("check_skill_frontmatter", SCRIPT)
assert _spec is not None
assert _spec.loader is not None
checker = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = checker
_spec.loader.exec_module(checker)


def _write_skill(tmp_path: Path, text: str) -> Path:
    skill = tmp_path / "demo" / "SKILL.md"
    skill.parent.mkdir()
    skill.write_text(text, encoding="utf-8")
    return skill


def _run(skill: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(skill)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_valid_skill_passes(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "---\nname: demo\ndescription: Does a thing.\n---\nbody\n")
    result = _run(skill)
    assert result.returncode == 0, result.stdout


def test_indented_marker_inside_a_block_scalar_does_not_close() -> None:
    text = "---\nname: demo\ndescription: |\n  first line\n  ---\n  still description\n---\nbody\n"
    assert checker._extract_frontmatter(text) == (
        "name: demo\ndescription: |\n  first line\n  ---\n  still description",
        2,
    )


def test_description_after_an_indented_marker_is_validated(tmp_path: Path) -> None:
    # The over-long tail sits after an indented '---'; truncating there would hide it.
    tail = "x" * (checker.DESCRIPTION_MAX_LEN + 1)
    skill = _write_skill(
        tmp_path,
        f"---\nname: demo\ndescription: |\n  first line\n  ---\n  {tail}\n---\nbody\n",
    )
    result = _run(skill)
    assert result.returncode == 1
    assert "'description' must be at most" in result.stdout


def test_indented_opening_marker_is_not_frontmatter(tmp_path: Path) -> None:
    assert checker._extract_frontmatter("  ---\nname: demo\n---\n") == (None, 0)
    skill = _write_skill(tmp_path, "  ---\nname: demo\ndescription: Does a thing.\n---\nbody\n")
    result = _run(skill)
    assert result.returncode == 1
    assert "missing YAML frontmatter" in result.stdout


def test_trailing_whitespace_on_a_marker_is_allowed() -> None:
    yaml_text, _ = checker._extract_frontmatter("--- \nname: demo\n---\t\nbody\n")
    assert yaml_text == "name: demo"
