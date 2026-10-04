#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Turn a scheduled check_drift.py run into one GitHub issue per Pi version.

An issue is open while the installed Pi differs from verified-against or check_drift fails;
a passing run on the verified version closes it (MAINTAINING.md, Scheduled drift check).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

LABEL = "pi-drift"
TITLE = "pi-coding-agent: Pi {version} — {status}"
MAX_BODY = 60_000  # GitHub's issue body limit is 65,536 characters
EXIT_PASS, EXIT_DRIFT, EXIT_GH = 0, 1, 3
SKILL_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Op:
    kind: str  # create, edit, or close
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
        "Follow pi-coding-agent/MAINTAINING.md#update-procedure; "
        "this issue closes on the first run after `verified-against` names this "
        "version and check_drift.py passes.\n\n"
        f"{links}\n\n"
    )
    fence = "```"
    room = MAX_BODY - len(head) - 2 * len(fence) - 100
    output = run.output
    if len(output) > room:
        output = output[:room] + f"\n… truncated {len(output) - room} characters; see the run log"
    return f"{head}{fence}\n{output}\n{fence}\n"


def decide(run: DriftRun, open_issues: list[dict], links: str) -> Plan:
    """What to do with the open pi-drift issues after one check_drift.py run."""
    installed = run.installed
    plan = Plan(fail=run.exit_code != 0)
    if run.exit_code == 0 and installed == run.verified:
        comment = f"Pi {installed} is verified (verified-against) and check_drift.py passes."
        plan.ops = [Op("close", issue["number"], issue["title"], comment) for issue in open_issues]
        return plan
    status = "drift found" if run.exit_code else "update review owed"
    title = TITLE.format(version=installed, status=status)
    body = _body(run, links)
    own_prefix = TITLE.format(version=installed, status="")
    mine = [issue for issue in open_issues if issue["title"].startswith(own_prefix)]
    if mine:
        plan.ops.append(Op("edit", mine[0]["number"], title, body))
    else:
        plan.ops.append(Op("create", None, title, body))
    superseded = f"Superseded by the issue for Pi {installed}."
    plan.ops += [
        Op("close", issue["number"], issue["title"], superseded)
        for issue in open_issues
        if issue not in mine[:1]
    ]
    return plan


class GhError(Exception):
    pass


def _gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise GhError(f"gh {' '.join(args[:2])} failed: {result.stderr.strip()}")
    return result.stdout


def open_issues() -> list[dict]:
    listed = _gh("issue", "list", "--label", LABEL, "--state", "open", "--json", "number,title")
    return json.loads(listed)


def apply(plan: Plan) -> None:
    if any(op.kind == "create" for op in plan.ops):
        _gh("label", "create", LABEL, "--force", "--description", "pi-coding-agent drift check")
    for op in plan.ops:
        if op.kind == "create":
            _gh("issue", "create", "--title", op.title, "--body", op.body, "--label", LABEL)
        elif op.kind == "edit":
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
        plan = decide(run, open_issues(), _links())
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
