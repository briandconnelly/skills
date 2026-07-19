#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check preregistration ordering from an extract_evidence.py manifest.

The skill's central promise is that predictions are written before
cause-outcome relationships are inspected. A ledger emitted only in the final
report cannot demonstrate that, so this checker reads the transcript manifest
(TSV from ``extract_evidence.py manifest``) and establishes the ordering
facts: the ordinal of the first *executed* Write/Edit whose target matches
--ledger-pattern, and every earlier tool_use whose target matches
--data-pattern.

It deliberately does not judge whether a pre-write data touch was orientation
(schema, row counts, coverage -- permitted before preregistration) or analysis
(a cause-outcome relationship -- forbidden). That line is semantic, so the
checker lists the touches verbatim and the scorer classifies each in the
evidence artifact. Data touches count on attempt, not execution: an errored
read still exposed intent to look.

Exit codes:
  0  ledger write found, no data-matching tool_use precedes it
  1  ledger write found, N earlier data touches listed for classification
  2  UNVERIFIABLE: no executed ledger write, or the manifest failed to parse
     -- the preregistration assertion fails
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

WRITE_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})
EXPECTED_COLUMNS = 5


class Row(NamedTuple):
    """One manifest line: a tool_use in serialization order."""

    ordinal: int
    timestamp: str
    tool: str
    status: str
    target: str


def parse_manifest(text: str) -> tuple[list[Row], list[str]]:
    """Manifest rows plus parse failures; any failure means fail closed."""
    rows: list[Row] = []
    fails: list[str] = []
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != EXPECTED_COLUMNS:
            fails.append(f"parse: line {n} has {len(cells)} column(s), expected {EXPECTED_COLUMNS}")
            continue
        try:
            ordinal = int(cells[0])
        except ValueError:
            fails.append(f"parse: line {n} ordinal {cells[0]!r} is not an integer")
            continue
        rows.append(Row(ordinal, cells[1], cells[2], cells[3], cells[4]))
    if not rows and not fails:
        fails.append("parse: manifest has no data rows")
    return rows, fails


def first_ledger_write(rows: list[Row], pattern: re.Pattern[str]) -> Row | None:
    """The first executed Write/Edit whose target matches the ledger pattern.

    Only a paired ok result proves execution (extract_evidence.py's contract),
    so an errored or unpaired write attempt is not a preregistration.
    """
    for row in sorted(rows, key=lambda r: r.ordinal):
        if row.tool in WRITE_TOOLS and row.status == "ok" and pattern.search(row.target):
            return row
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--ledger-pattern", required=True)
    ap.add_argument("--data-pattern", required=True)
    a = ap.parse_args()
    try:
        ledger_pattern = re.compile(a.ledger_pattern)
        data = re.compile(a.data_pattern)
    except re.error as exc:
        print(f"UNVERIFIABLE: invalid pattern {exc.pattern!r}: {exc}")
        return 2
    rows, fails = parse_manifest(a.manifest.read_text(encoding="utf-8"))
    if fails:
        print("UNVERIFIABLE:")
        for f in fails:
            print(f"  - {f}")
        return 2
    ledger = first_ledger_write(rows, ledger_pattern)
    if ledger is None:
        print(
            f"UNVERIFIABLE: no executed Write/Edit matches --ledger-pattern "
            f"{a.ledger_pattern!r}; preregistration ordering cannot be "
            f"established from this transcript"
        )
        return 2
    print(f"PREREG_WRITE: ordinal {ledger.ordinal} ({ledger.tool} -> {ledger.target})")
    earlier = [r for r in rows if r.ordinal < ledger.ordinal and data.search(r.target)]
    if not earlier:
        print("CLEAN: no data-matching tool_use precedes the ledger write")
        return 0
    print(
        f"CLASSIFY: {len(earlier)} data-matching tool_use(s) precede the "
        f"ledger write; classify each as orientation or analysis in the "
        f"evidence artifact:"
    )
    for r in sorted(earlier, key=lambda x: x.ordinal):
        print(f"  - ordinal {r.ordinal}: {r.tool} [{r.status}] {r.target}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
