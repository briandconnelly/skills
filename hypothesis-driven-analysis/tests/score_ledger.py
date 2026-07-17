#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score the machine-checkable assertions of a hypothesis-driven-analysis ledger.

SCOPE — read before pointing this at a new scenario:

  This scores ledgers from scenarios whose ground truth contains NO legitimate
  causal refutation. That is true of s15 by construction: the fixture supplies no
  timing, mechanism, or negative-control evidence bearing on the Assist
  hypothesis, so any causal REFUTED in an s15 ledger is necessarily wrong.

  C1 is NOT a general ledger invariant. The skill explicitly permits refuting a
  causal hypothesis on independent evidence that does not run through an
  unidentified contrast, and the worked example in references/ledger-template.md
  does exactly that twice (H1 on timing, H4 on trace spans). Running C1 against a
  should-refute scenario would fail correct work and teach analysts never to
  conclude anything — the top regression risk this revision is trying to avoid.
  A should-refute scenario needs its own check, not this one.

Checks exactly two things, both syntactic:

  C1  No row whose claim is `causal` carries status REFUTED.
      Valid only under the scope above. This is the regression the
      status-adequacy revision exists to prevent.
  C2  Every REFUTED `descriptive` row existed in the Plan-time ledger under the
      same id with a non-empty estimand. Catches status laundering: inventing a
      descriptive claim at conclusion time to house a REFUTED.

Every other assertion in scenario 15 is rubric-scored. Do not add them here
without the ledger fields to support them.

    uv run hypothesis-driven-analysis/tests/score_ledger.py \
        --final run.md --plan plan.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$")


def parse_tables(md: str) -> list[list[list[str]]]:
    """Return every markdown table as a list of rows, each row a list of cells."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in md.splitlines():
        m = ROW.match(line)
        if not m:
            if current:
                tables.append(current)
                current = []
            continue
        cells = [c.strip() for c in m.group("cells").split("|")]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue  # separator row
        current.append(cells)
    if current:
        tables.append(current)
    return tables


def find_rows(md: str, *required: str) -> list[dict[str, str]]:
    """Rows of the first table whose header contains every required column."""
    for t in parse_tables(md):
        if not t:
            continue
        header = [h.lower() for h in t[0]]
        if all(any(r == h for h in header) for r in required):
            return [dict(zip(header, row, strict=True)) for row in t[1:] if len(row) == len(header)]
    return []


def claim_of(cell: str) -> str:
    return "causal" if cell.strip().lower().startswith("causal") else "descriptive"


def score(final: str, plan: str | None) -> list[str]:
    fails: list[str] = []
    summary = find_rows(final, "id", "claim", "status")
    if not summary:
        return ["no per-hypothesis summary table with id/claim/status found in the final ledger"]

    for row in summary:
        status = row["status"].upper()
        if "REFUTED" not in status:
            continue
        if claim_of(row["claim"]) == "causal":
            fails.append(
                f"C1: {row['id']} is a causal claim marked REFUTED. "
                f"An unidentified exposure-outcome contrast cannot refute a causal hypothesis."
            )
        elif plan is not None:
            planned = {r["id"]: r for r in find_rows(plan, "id", "claim")}
            p = planned.get(row["id"])
            if p is None:
                fails.append(
                    f"C2: {row['id']} carries a descriptive REFUTED but does not appear in the "
                    f"Plan-time ledger. A descriptive row created at conclusion time is laundering."
                )
            elif "estimand" not in p["claim"].lower():
                fails.append(
                    f"C2: {row['id']} carries a descriptive REFUTED but named no estimand at "
                    f"Plan time."
                )
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", required=True, type=Path)
    ap.add_argument("--plan", type=Path, default=None)
    a = ap.parse_args()
    plan = a.plan.read_text() if a.plan else None
    if plan is None:
        print("note: --plan omitted; C2 (status laundering) not checked", file=sys.stderr)
    fails = score(a.final.read_text(), plan)
    if fails:
        print("FAIL:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK: C1 passed" + ("; C2 passed" if plan else " (C2 skipped)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
