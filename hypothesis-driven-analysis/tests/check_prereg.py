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
--ledger-pattern, and every earlier tool_use that must be classified.

It deliberately does not judge whether a pre-write data touch was orientation
(schema, row counts, coverage -- permitted before preregistration) or analysis
(a cause-outcome relationship -- forbidden). That line is semantic, so the
checker lists the touches verbatim and the scorer classifies each in the
evidence artifact. Data touches count on attempt, not execution: an errored
read still exposed intent to look.

Fail-closed behaviors:

- The manifest read itself is guarded: an unreadable or undecodable file is
  UNVERIFIABLE (exit 2), never a traceback.
- Manifest integrity is checked before any ordering claim: duplicate
  ordinals, ordinals below 1, malformed lines, and statuses outside
  {ok, error, no-result} each fail closed (exit 2) with a parse message.
- A pre-write row whose target is ``-`` (extract_evidence.py could not
  extract one) is ALWAYS listed for classification, regardless of
  --data-pattern: an invisible target cannot be cleared by a pattern that
  never saw it. Read the row's real input from the events stream.
- If no executed Write/Edit matches --ledger-pattern, Bash rows (any status)
  whose command matches the pattern are surfaced as possible Bash-mediated
  ledger writes (``cat > ledger.md`` and the like); the run stays
  UNVERIFIABLE (exit 2) and those candidates must be verified from the
  events stream and scored manually.

Content check: finding the write proves *when* a ledger file was touched, not
*what* it contained. Whenever a ledger write is found the checker prints a
CONTENT-CHECK REQUIRED line: the scorer must confirm from the events stream
that this first write already carries the hypothesis table and predictions --
a placeholder written early and filled in after analysis is a reconstruction,
not a preregistration.

Stated limitation: ordinals are JSONL serialization order, which is this
instrument's ordering authority, but tool calls issued in parallel within one
assistant turn have no true mutual order. Such rows are only heuristically
flagged: post-write rows sharing the ledger write's exact timestamp and
matching --data-pattern (or carrying target ``-``) are printed under a
SAME-BATCH heading and force exit code >= 1, because serialization order
cannot prove the ledger file existed before they ran. Classify them from the
events stream.

Exit codes:
  0  ledger write found, nothing to classify
  1  ledger write found; pre-write touches and/or same-batch rows listed for
     classification
  2  UNVERIFIABLE: unreadable manifest, integrity failure, invalid pattern,
     or no executed ledger write -- the preregistration assertion fails
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

WRITE_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})
VALID_STATUSES = frozenset({"ok", "error", "no-result"})
EXPECTED_COLUMNS = 5
UNEXTRACTED_NOTE = " (target not extracted — read it from the events stream)"


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
    seen_ordinals: set[int] = set()
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
        if ordinal < 1:
            fails.append(f"parse: line {n} ordinal {ordinal} is below 1; ordinals are 1-based")
            continue
        if ordinal in seen_ordinals:
            fails.append(f"parse: line {n} duplicates ordinal {ordinal}; ordering is ambiguous")
            continue
        seen_ordinals.add(ordinal)
        if cells[3] not in VALID_STATUSES:
            fails.append(
                f"parse: line {n} status {cells[3]!r} is not one of "
                f"{', '.join(sorted(VALID_STATUSES))}"
            )
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


def no_ledger_message(rows: list[Row], pattern: re.Pattern[str], raw_pattern: str) -> str:
    """UNVERIFIABLE message, naming any Bash rows that look like ledger writes."""
    message = (
        f"UNVERIFIABLE: no executed Write/Edit matches --ledger-pattern "
        f"{raw_pattern!r}; preregistration ordering cannot be "
        f"established from this transcript"
    )
    bash_candidates = sorted(
        (r for r in rows if r.tool == "Bash" and pattern.search(r.target)),
        key=lambda r: r.ordinal,
    )
    if bash_candidates:
        ordinals = ",".join(str(r.ordinal) for r in bash_candidates)
        message += (
            f"; possible Bash-mediated ledger write(s) at ordinal(s) {ordinals} "
            f"— verify from the events stream and score manually"
        )
    return message


def report_ordering(rows: list[Row], ledger: Row, data: re.Pattern[str]) -> int:
    """Print the ordering facts for a found ledger write; return the exit code."""
    print(f"PREREG_WRITE: ordinal {ledger.ordinal} ({ledger.tool} -> {ledger.target})")
    print(
        f"CONTENT-CHECK REQUIRED: confirm from the events stream "
        f"(extract_evidence.py events <transcript> --ordinal {ledger.ordinal}) "
        f"that this write already carries the hypothesis table and predictions "
        f"— a placeholder written early and filled after analysis is a "
        f"reconstruction, not a preregistration."
    )
    earlier: list[tuple[Row, str]] = []
    for r in sorted(rows, key=lambda x: x.ordinal):
        if r.ordinal >= ledger.ordinal:
            continue
        if r.target == "-":
            earlier.append((r, UNEXTRACTED_NOTE))
        elif data.search(r.target):
            earlier.append((r, ""))
    same_batch = [
        r
        for r in sorted(rows, key=lambda x: x.ordinal)
        if r.ordinal > ledger.ordinal
        and r.timestamp == ledger.timestamp
        and (r.target == "-" or data.search(r.target))
    ]
    if not earlier and not same_batch:
        print("CLEAN: no data-matching tool_use precedes the ledger write")
        return 0
    if earlier:
        print(
            f"CLASSIFY: {len(earlier)} tool_use(s) precede the ledger write; "
            f"classify each as orientation or analysis in the evidence artifact:"
        )
        for r, note in earlier:
            print(f"  - ordinal {r.ordinal}: {r.tool} [{r.status}] {r.target}{note}")
    if same_batch:
        print(
            f"SAME-BATCH: {len(same_batch)} tool_use(s) share the ledger "
            f"write's timestamp; serialization order cannot prove the ledger "
            f"file existed before they ran — classify from the events stream:"
        )
        for r in same_batch:
            print(f"  - ordinal {r.ordinal}: {r.tool} [{r.status}] {r.target}")
    return 1


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
    try:
        text = a.manifest.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"UNVERIFIABLE: cannot read manifest {a.manifest}: {exc}")
        return 2
    rows, fails = parse_manifest(text)
    if fails:
        print("UNVERIFIABLE:")
        for f in fails:
            print(f"  - {f}")
        return 2
    ledger = first_ledger_write(rows, ledger_pattern)
    if ledger is None:
        print(no_ledger_message(rows, ledger_pattern, a.ledger_pattern))
        return 2
    return report_ordering(rows, ledger, data)


if __name__ == "__main__":
    raise SystemExit(main())
