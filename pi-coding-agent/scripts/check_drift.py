#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4"]
# ///
"""Check the skill against the installed Pi before bumping verified-against.

Stages: citations (every docs/<page>.md[#anchor] in SKILL.md, MAINTAINING.md, and
references/*.md resolves), dependencies (every Pi interface in pi_gate.GATE_DEPENDENCIES
exists), gate (pi-gate --self-test and every fixture outside tests/fixtures/gate/negative/
pass), then the CHANGELOG.md entries since verified-against, for review (MAINTAINING.md).
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

SCRIPTS = Path(__file__).resolve().parent
DEFAULT_SKILL_DIR = SCRIPTS.parent
EXIT_PASS, EXIT_FAIL, EXIT_NO_INSTALL = 0, 1, 2
STAGES = ("citations", "dependencies", "gate", "changelog")
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")
FAUX_DTS = Path("dist/providers/faux.d.ts")
# Case-insensitive so a miscased citation is found (and then fails on the exact-name check,
# which matters on case-insensitive filesystems); the fragment runs to the end of the link
# target so a valid prefix cannot hide invalid trailing text.
CITATION = re.compile(r"(?i)\bdocs/([a-z0-9._-]+\.md)(?:#([^\s)\]>`'\"]+))?")
# A hosted link to a specific page bypasses the installed docs; the bare docs root is allowed.
HOSTED_PAGE = re.compile(r"https?://pi\.dev/docs/latest/[^\s)\]>`'\"]+")
SENTENCE_END = ".,;:!?"


def _load_script(name: str) -> ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pi_docs = _load_script("pi_docs")
pi_gate = _load_script("pi_gate")


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
    version = install.version
    pages = {path.name for path in install.docs.glob("*.md")}  # exact names, any filesystem
    targets_by_page: dict[str, set[str]] = {}
    for document in skill_documents(skill_dir):
        label = document.relative_to(skill_dir).as_posix()
        lines = document.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            for hosted in HOSTED_PAGE.finditer(line):
                checked += 1
                link = hosted.group(0).rstrip(SENTENCE_END)
                reason = "hosted Pi docs link; cite the installed docs/<page>.md instead"
                problems.append(Problem(label, number, link, reason))
            for match in CITATION.finditer(line):
                checked += 1
                page = match.group(1)
                cited_page = match.group(0).split("#")[0]  # as written, e.g. DOCS/Cli.md
                fragment = (match.group(2) or "").rstrip(SENTENCE_END)
                citation = cited_page + (f"#{fragment}" if fragment else "")
                if cited_page != f"docs/{page}" or page not in pages:
                    reason = f"{cited_page} does not exist in Pi {version}"
                    problems.append(Problem(label, number, citation, reason))
                    continue
                if page not in targets_by_page:
                    text = (install.docs / page).read_text(encoding="utf-8")
                    targets_by_page[page] = pi_docs.anchors(text)
                if fragment and fragment not in targets_by_page[page]:
                    reason = f"no heading or <a id> '{fragment}' in docs/{page} (Pi {version})"
                    problems.append(Problem(label, number, citation, reason))
    return checked, problems


def pi_ai_root(root: Path) -> Path | None:
    """pi-ai sits under Pi's own node_modules (global install) or beside it (hoisted)."""
    for candidate in (root / "node_modules" / "@earendil-works" / "pi-ai", root.parent / "pi-ai"):
        if (candidate / FAUX_DTS).is_file():
            return candidate
    return None


def _read(path: Path | None) -> str | None:
    return path.read_text(encoding="utf-8") if path and path.is_file() else None


def dependency_sources(root: Path, help_text: str) -> dict[str, tuple[str, str | None]]:
    """For each GATE_DEPENDENCIES kind: (where it is looked up, that text or None if absent)."""
    docs = root / "docs"
    events = [_read(docs / page) for page in ("json.md", "rpc.md", "rpc-extension-ui.md")]
    pi_ai = pi_ai_root(root)
    return {
        "cli_flags": ("pi --help", help_text),
        "cli_docs": ("docs/cli.md", _read(docs / "cli.md")),
        "env": ("docs/environment-variables.md", _read(docs / "environment-variables.md")),
        "rpc_commands": ("docs/rpc-commands.md", _read(docs / "rpc-commands.md")),
        "events": (
            "docs/json.md, docs/rpc.md, docs/rpc-extension-ui.md",
            "\n".join(text for text in events if text) or None,
        ),
        "extension_api": (
            "dist/core/extensions/types.d.ts",
            _read(root / "dist" / "core" / "extensions" / "types.d.ts"),
        ),
        "faux_exports": (
            f"@earendil-works/pi-ai/{FAUX_DTS.as_posix()}",
            _read(pi_ai / FAUX_DTS if pi_ai else None),
        ),
    }


def _present(kind: str, name: str, text: str) -> bool:
    if kind == "rpc_commands":
        return name in pi_docs.anchors(text)
    if kind == "cli_docs":
        return name in text
    return re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", text) is not None


def check_dependencies(root: Path, version: str, help_text: str) -> tuple[int, list[Problem]]:
    """Every Pi interface pi_gate.py depends on must exist in the installed Pi."""
    checked = 0
    problems: list[Problem] = []
    sources = dependency_sources(root, help_text)
    for kind, names in pi_gate.GATE_DEPENDENCIES.items():
        for name in names:
            checked += 1
            if kind == "files":
                if not (root / name).is_file():
                    problems.append(Problem(name, 0, name, f"file missing from Pi {version}"))
                continue
            where, text = sources[kind]
            if text is None:
                problems.append(Problem(where, 0, name, f"{where} missing from Pi {version}"))
            elif not _present(kind, name, text):
                reason = f"gate depends on {kind} {name}, absent from {where} (Pi {version})"
                problems.append(Problem(where, 0, name, reason))
    return checked, problems


def pi_help(path_env: str | None) -> str:
    """`pi --help` from the same PATH used to find the install, isolated like a gate run."""
    with tempfile.TemporaryDirectory(prefix="check-drift-") as agent:
        env = {key: value for key, value in os.environ.items() if not key.startswith("PI_")}
        env.update(PI_CODING_AGENT_DIR=agent, PI_OFFLINE="1", PI_SKIP_VERSION_CHECK="1")
        if path_env is not None:
            env["PATH"] = path_env
        result = subprocess.run(
            [shutil.which("pi", path=path_env) or "pi", "--help"],
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    return result.stdout


def fixture_gates(skill_dir: Path) -> list[Path]:
    """Every gate file that must pass: all of tests/fixtures/gate except negative/."""
    root = skill_dir / "tests" / "fixtures" / "gate"
    return sorted(
        gate for gate in root.rglob("*gate.json") if "negative" not in gate.relative_to(root).parts
    )


def check_gate(skill_dir: Path, install: Any) -> list[str]:
    """Run pi-gate's self-test and every positive fixture; return one line per failure."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="check-drift-real-") as real:
        options = pi_gate.GateOptions(Path(real))
        ok, lines = pi_gate.self_test(install, Path(real))
        if not ok:
            failures += [line for line in lines if line.startswith("FAIL")]
        for gate in fixture_gates(skill_dir):
            artifact = pi_gate.artifact_for_gate(gate)
            checks = pi_gate.gate(artifact, gate, install, options)
            failures += [
                f"{gate.relative_to(skill_dir)}: {check.code}: {check.detail}"
                for check in checks
                if check.status == "FAIL"
            ]
    return failures


def _version_key(text: str) -> tuple[int, ...] | None:
    match = VERSION.search(text)
    return tuple(int(part) for part in match.groups()) if match else None


def changelog_delta(install: Any, recorded: str | None) -> list[str]:
    """CHANGELOG.md lines of every version after verified-against, up to the installed one."""
    low, high = _version_key(recorded or ""), _version_key(install.version)
    if low is None or high is None or not install.changelog.is_file():
        return []
    lines: list[str] = []
    keep = False
    for line in install.changelog.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            key = _version_key(line)
            keep = key is not None and low < key <= high
        if keep:
            lines.append(line)
    return lines


def _stage_citations(skill_dir: Path, install: Any) -> bool:
    checked, problems = check_citations(skill_dir, install)
    if checked == 0:
        print(
            f"FAIL citations: no docs/<page>.md citations found under {skill_dir}; "
            "nothing was checked",
            file=sys.stderr,
        )
        return False
    for problem in problems:
        print(f"FAIL {problem.file}:{problem.line} {problem.citation}: {problem.reason}")
    status = "FAIL" if problems else "PASS"
    print(
        f"{status} citations: {checked} checked against Pi {install.version}, "
        f"{len(problems)} broken"
    )
    return not problems


def _stage_dependencies(install: Any, help_text: str) -> bool:
    checked, problems = check_dependencies(install.root, install.version, help_text)
    if checked == 0:
        print("FAIL dependencies: GATE_DEPENDENCIES lists nothing; nothing was checked")
        return False
    for problem in problems:
        print(f"FAIL dependency {problem.citation}: {problem.reason}")
    status = "FAIL" if problems else "PASS"
    print(
        f"{status} dependencies: {checked} checked against Pi {install.version}, "
        f"{len(problems)} missing"
    )
    return not problems


def _stage_gate(skill_dir: Path, install: Any) -> bool:
    if not fixture_gates(skill_dir):
        print(f"FAIL gate: no positive fixtures under {skill_dir}/tests/fixtures/gate")
        return False
    failures = check_gate(skill_dir, install)
    for failure in failures:
        print(f"FAIL gate {failure}")
    count = len(fixture_gates(skill_dir))
    status = "FAIL" if failures else "PASS"
    print(
        f"{status} gate: self-test and {count} fixtures against Pi {install.version}, "
        f"{len(failures)} failures"
    )
    return not failures


def _stage_changelog(skill_dir: Path, install: Any) -> bool:
    """Print the delta for review; fail when versions differ and there is no delta to review."""
    recorded = pi_docs.verified_against(skill_dir)
    if recorded is None:
        print("REVIEW changelog: verified-against is unrecorded; review CHANGELOG.md in full")
        return True
    if recorded == install.version:
        print(f"REVIEW changelog: installed Pi {install.version} is the verified version")
        return True
    lines = changelog_delta(install, recorded)
    if not lines:
        print(
            f"FAIL changelog: no CHANGELOG.md entries found between {recorded} and "
            f"{install.version} at {install.changelog}; the delta cannot be reviewed"
        )
        return False
    print(
        f"REVIEW changelog: {recorded} -> {install.version}, {len(lines)} lines; "
        "look for new surfaces and changed contracts (MAINTAINING.md)"
    )
    print("\n".join(lines))
    return True


def pi_help_from(path_env: str | None) -> str:
    try:
        return pi_help(path_env)
    except (OSError, subprocess.SubprocessError) as error:
        print(f"could not run pi --help: {error}", file=sys.stderr)
        return ""


def main(
    argv: list[str] | None = None, *, path_env: str | None = None, cwd: Path | None = None
) -> int:
    parser = argparse.ArgumentParser(
        prog="check-drift", description=(__doc__ or "").splitlines()[0]
    )
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    parser.add_argument(
        "--stages", default=",".join(STAGES), help=f"comma-separated subset of {STAGES}"
    )
    args = parser.parse_args(argv)
    stages = [stage for stage in args.stages.split(",") if stage]
    if not stages or set(stages) - set(STAGES):
        parser.error(f"--stages takes a comma-separated subset of {', '.join(STAGES)}")
    path = path_env if path_env is not None else os.environ.get("PATH")
    try:
        install = pi_docs.find_installs(path, cwd or Path.cwd())[0]
    except pi_docs.NoInstallError as error:
        print(error, file=sys.stderr)
        return EXIT_NO_INSTALL
    ok = True
    if "citations" in stages:
        ok = _stage_citations(args.skill_dir, install) and ok
    if "dependencies" in stages:
        ok = _stage_dependencies(install, pi_help_from(path)) and ok
    if "gate" in stages:
        ok = _stage_gate(args.skill_dir, install) and ok
    if "changelog" in stages:
        ok = _stage_changelog(args.skill_dir, install) and ok
    skipped = [stage for stage in STAGES if stage not in stages]
    if skipped:
        print(f"NOT RUN: {', '.join(skipped)} (--stages); do not bump verified-against")
    return EXIT_PASS if ok else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
