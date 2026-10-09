#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Turn a scheduled check_drift.py run into one GitHub issue per Pi version.

The issue lifecycle is defined in MAINTAINING.md, "Scheduled drift check".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

LABEL = "pi-drift"
TITLE = "pi-coding-agent: Pi {version} — {status}"
TITLE_VERSION = re.compile(r"^pi-coding-agent: Pi (\S+) — ")
MAX_BODY = 60_000  # GitHub's issue body limit is 65,536 characters
EXIT_PASS, EXIT_DRIFT, EXIT_GH = 0, 1, 3
SKILL_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Op:
    kind: str  # create, edit, reopen (then edit), or close
    number: int | None
    title: str
    body: str  # the issue body, or the closing comment


@dataclass(frozen=True)
class DriftRun:
    """One check_drift.py run against the installed Pi."""

    installed: str
    verified: str  # verified-against
    exit_code: int
    output: str


@dataclass
class Plan:
    ops: list[Op] = field(default_factory=list)
    fail: bool = False


def _body(run: DriftRun, links: str) -> str:
    state = "check_drift.py failed" if run.exit_code else "check_drift.py passed"
    head = (
        f"The scheduled drift check installed Pi {run.installed}; "
        f"`verified-against` is {run.verified}. {state} (exit {run.exit_code}).\n\n"
        "What this issue means and how it closes: "
        "pi-coding-agent/MAINTAINING.md#scheduled-drift-check.\n\n"
        f"{links}\n\n"
    )
    fence = "```"
    room = MAX_BODY - len(head) - 2 * len(fence) - 100
    output = run.output
    if len(output) > room:
        output = output[:room] + f"\n… truncated {len(output) - room} characters; see the run log"
    return f"{head}{fence}\n{output}\n{fence}\n"


def _version(issue: dict) -> str | None:
    match = TITLE_VERSION.match(issue["title"])
    return match.group(1) if match else None


def _order(version: str | None) -> tuple[int, ...] | None:
    """Numeric release order, or None for a version this script does not compare."""
    parts = version.split(".") if version else []
    return tuple(int(part) for part in parts) if parts and all(map(str.isdigit, parts)) else None


def _own_issue(installed: str, issues: list[dict]) -> dict | None:
    """The issue for this version: an open one first, else the most recent closed one."""
    mine = [issue for issue in issues if _version(issue) == installed]
    mine.sort(key=lambda issue: (issue["state"] == "OPEN", issue["number"]), reverse=True)
    return mine[0] if mine else None


def decide(run: DriftRun, issues: list[dict], links: str) -> Plan:
    """What to do with the pi-drift issues, open and closed, after one check_drift.py run."""
    installed = run.installed
    plan = Plan(fail=run.exit_code != 0)
    open_issues = [issue for issue in issues if issue["state"] == "OPEN"]
    if run.exit_code == 0 and installed == run.verified:
        comment = f"Pi {installed} is verified (verified-against) and check_drift.py passes."
        plan.ops = [Op("close", issue["number"], issue["title"], comment) for issue in open_issues]
        return plan
    status = "drift found" if run.exit_code else "update review owed"
    title = TITLE.format(version=installed, status=status)
    body = _body(run, links)
    mine = _own_issue(installed, issues)
    if mine is None:
        plan.ops.append(Op("create", None, title, body))
    else:
        kind = "edit" if mine["state"] == "OPEN" else "reopen"
        plan.ops.append(Op(kind, mine["number"], title, body))
    current = _order(installed)
    superseded = f"Superseded by the issue for Pi {installed}."
    for issue in open_issues:
        older = _order(_version(issue))
        if issue is not mine and current and older and older < current:
            plan.ops.append(Op("close", issue["number"], issue["title"], superseded))
    return plan


class GhError(Exception):
    pass


def _gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise GhError(f"gh {' '.join(args[:2])} failed: {result.stderr.strip()}")
    return result.stdout


def version_issues() -> list[dict]:
    """Every pi-drift issue, open and closed, so a version keeps one issue."""
    listed = _gh(
        "issue", "list", "--label", LABEL, "--state", "all", "--limit", "200",
        "--json", "number,title,state",
    )  # fmt: skip
    return json.loads(listed)


def apply(plan: Plan) -> None:
    if any(op.kind == "create" for op in plan.ops):
        _gh("label", "create", LABEL, "--force", "--description", "pi-coding-agent drift check")
    for op in plan.ops:
        if op.kind == "create":
            _gh("issue", "create", "--title", op.title, "--body", op.body, "--label", LABEL)
        elif op.kind in ("edit", "reopen"):
            if op.kind == "reopen":
                _gh("issue", "reopen", str(op.number))
            _gh("issue", "edit", str(op.number), "--title", op.title, "--body", op.body)
        else:
            _gh("issue", "close", str(op.number), "--comment", op.body)


def _links() -> str:
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo, run = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID")
    return f"Run: {server}/{repo}/actions/runs/{run}" if repo and run else "Run: local"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="drift-report", description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, required=True, help="check_drift.py output")
    parser.add_argument("--exit-code", type=int, required=True, help="check_drift.py exit code")
    parser.add_argument("--installed", required=True, help="installed Pi version")
    parser.add_argument("--verified", help="defaults to the skill's verified-against")
    parser.add_argument("--dry-run", action="store_true", help="print the plan; write nothing")
    args = parser.parse_args(argv)
    verified = args.verified or (SKILL_DIR / "verified-against").read_text().strip()
    output = args.output.read_text(encoding="utf-8", errors="replace")
    try:
        run = DriftRun(args.installed, verified, args.exit_code, output)
        plan = decide(run, version_issues(), _links())
        if args.dry_run:
            print(json.dumps(asdict(plan), indent=2))
        else:
            apply(plan)
    except GhError as error:
        print(error, file=sys.stderr)
        return EXIT_GH
    return EXIT_DRIFT if plan.fail else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
