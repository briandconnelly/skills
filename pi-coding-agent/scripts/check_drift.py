#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check the skill against the installed Pi before bumping verified-against.

Current stage: every docs/<page>.md[#anchor] citation in SKILL.md, MAINTAINING.md,
and references/*.md must resolve in the installed docs. Gate-dependency, self-test,
and changelog-delta stages are added with the gate (see MAINTAINING.md).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

SCRIPTS = Path(__file__).resolve().parent
DEFAULT_SKILL_DIR = SCRIPTS.parent
EXIT_PASS, EXIT_FAIL, EXIT_NO_INSTALL = 0, 1, 2
CITATION = re.compile(r"\bdocs/([A-Za-z0-9._-]+\.md)(?:#([A-Za-z0-9_-]+))?")


def _load_pi_docs() -> ModuleType:
    if "pi_docs" in sys.modules:
        return sys.modules["pi_docs"]
    spec = importlib.util.spec_from_file_location("pi_docs", SCRIPTS / "pi_docs.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["pi_docs"] = module
    spec.loader.exec_module(module)
    return module


pi_docs = _load_pi_docs()


@dataclass(frozen=True)
class Problem:
    file: str
    line: int
    citation: str
    reason: str


def skill_documents(skill_dir: Path) -> list[Path]:
    candidates = [skill_dir / "SKILL.md", skill_dir / "MAINTAINING.md"]
    candidates += sorted((skill_dir / "references").glob("*.md"))
    return [path for path in candidates if path.is_file()]


def check_citations(skill_dir: Path, install: Any) -> tuple[int, list[Problem]]:
    """Count every citation and return the ones that do not resolve in the installed docs."""
    checked = 0
    problems: list[Problem] = []
    targets_by_page: dict[str, set[str] | None] = {}
    for document in skill_documents(skill_dir):
        label = document.relative_to(skill_dir).as_posix()
        lines = document.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            for match in CITATION.finditer(line):
                checked += 1
                page, fragment = match.group(1), match.group(2)
                if page not in targets_by_page:
                    path = install.docs / page
                    targets_by_page[page] = (
                        pi_docs.anchors(path.read_text(encoding="utf-8"))
                        if path.is_file()
                        else None
                    )
                targets = targets_by_page[page]
                version = install.version
                if targets is None:
                    reason = f"docs/{page} does not exist in Pi {version}"
                elif fragment and fragment not in targets:
                    reason = f"no heading or <a id> '{fragment}' in docs/{page} (Pi {version})"
                else:
                    continue
                problems.append(Problem(label, number, match.group(0), reason))
    return checked, problems


def main(
    argv: list[str] | None = None, *, path_env: str | None = None, cwd: Path | None = None
) -> int:
    parser = argparse.ArgumentParser(
        prog="check-drift", description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    args = parser.parse_args(argv)
    try:
        install = pi_docs.find_installs(
            path_env if path_env is not None else os.environ.get("PATH"), cwd or Path.cwd()
        )[0]
    except pi_docs.NoInstallError as error:
        print(error, file=sys.stderr)
        return EXIT_NO_INSTALL
    checked, problems = check_citations(args.skill_dir, install)
    if checked == 0:
        print(
            f"FAIL citations: no docs/<page>.md citations found under {args.skill_dir}; "
            "nothing was checked",
            file=sys.stderr,
        )
        return EXIT_FAIL
    for problem in problems:
        print(f"FAIL {problem.file}:{problem.line} {problem.citation}: {problem.reason}")
    status = "FAIL" if problems else "PASS"
    print(
        f"{status} citations: {checked} checked against Pi {install.version}, "
        f"{len(problems)} broken"
    )
    print("NOT RUN: gate dependencies, gate self-test, changelog delta (added with the gate)")
    return EXIT_FAIL if problems else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
