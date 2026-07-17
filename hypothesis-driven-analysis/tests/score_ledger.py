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

WHY IT IS BUILT THE WAY IT IS

A run's own summary of how it did cannot be trusted, so this scorer must never
report a check it did not actually perform. Two rules follow.

Fail closed. Anything it cannot confidently resolve is a parse failure and the
run exits 1 naming what could not be verified: a file with no table carrying the
required columns, more than one such table, a repeated column name, a data row
whose cell count does not match the header, a repeated or empty id, a claim cell
that is neither `causal` nor `descriptive`, or a status cell carrying neither
REFUTED nor UNRESOLVED. It never drops or waves through input it failed to
understand, and it never reports C2 against a --plan it could not parse.

Report only what was earned. Success output states, per check, whether it was
checked and passed, had nothing to check, or was not checked at all — a run with
no REFUTED descriptive row has not verified C2, and says so rather than claiming
a pass it did not earn.

Deliberately lenient where real ledgers vary: ids and claim/status cells are read
through markdown emphasis and surrounding prose, `\\|` inside a cell is a literal
pipe rather than a column break, and ids are matched between the two files after
normalizing emphasis, whitespace, and case. A scorer that fails correct ledgers
gets ignored.

Every other assertion in scenario 15 is rubric-scored. Do not add them here
without the ledger fields to support them.

    uv run hypothesis-driven-analysis/tests/score_ledger.py \\
        --final run.md --plan plan.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROW = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
EMPHASIS = re.compile(r"[*_`]")
SPACES = re.compile(r"\s+")
STATUS_TOKEN = re.compile(r"\b(REFUTED|UNRESOLVED)\b")
ESTIMAND = re.compile(r"estimand\b(?P<rest>.*)", re.IGNORECASE | re.DOTALL)
# Punctuation that can sit between "estimand" and its content, or close it off:
# ASCII punctuation plus U+2013 en dash, U+2014 em dash, U+2026 ellipsis.
ESTIMAND_TRIM = " \t:=()[]{}<>*_.,;!?\"'-\u2013\u2014\u2026"

FINAL = "final ledger"
PLAN = "plan ledger"


class Outcome(NamedTuple):
    """What score() concluded: failures to report, and what it actually checked."""

    fails: list[str]
    checked: list[str]


def unescape_cell(cell: str) -> str:
    """Strip a table cell and turn its escaped pipes (\\|) back into literal |."""
    return cell.strip().replace("\\|", "|")


def normalize_key(cell: str) -> str:
    """Fold a header name or row id to its comparison form.

    Drops markdown emphasis, collapses internal whitespace, and casefolds, so
    `**H1**`, `H1`, and `h1` are one id across the two files. Any collision this
    creates surfaces as a duplicate id, never as a silent merge.
    """
    return SPACES.sub(" ", EMPHASIS.sub("", cell)).strip().casefold()


def parse_tables(md: str) -> list[list[list[str]]]:
    """Return every markdown table as a list of rows, each row a list of cells.

    Cells are split on unescaped pipes only, so a literal `|` written as `\\|`
    inside a cell's text does not fragment the row.
    """
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in md.splitlines():
        m = ROW.match(line)
        if not m:
            if current:
                tables.append(current)
                current = []
            continue
        cells = [unescape_cell(c) for c in CELL_SPLIT.split(m.group("cells"))]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue  # separator row
        current.append(cells)
    if current:
        tables.append(current)
    return tables


def _select_table(
    md: str, label: str, required: tuple[str, ...]
) -> tuple[list[list[str]] | None, list[str]]:
    """The one table whose header carries every required column, or a parse failure.

    Zero matches and more than one match are both failures: neither leaves the
    scorer able to say which rows it was supposed to check.
    """
    cols = ", ".join(required)
    matches = [t for t in parse_tables(md) if t and _header_has(t[0], required)]
    if not matches:
        return None, [
            f"parse: {label}: no table found whose header carries every required "
            f"column ({cols}); nothing in this file could be checked"
        ]
    if len(matches) > 1:
        return None, [
            f"parse: {label}: {len(matches)} tables carry the required columns "
            f"({cols}); cannot tell which one to score"
        ]
    return matches[0], []


def _header_has(header: list[str], required: tuple[str, ...]) -> bool:
    names = [normalize_key(h) for h in header]
    return all(r in names for r in required)


def _rows_from(table: list[list[str]], label: str) -> tuple[list[dict[str, str]], list[str]]:
    """Data rows of a matched table, keyed by normalized header name."""
    header = [normalize_key(h) for h in table[0]]
    repeats = sorted({h for h in header if header.count(h) > 1})
    if repeats:
        return [], [
            f"parse: {label}: header repeats column name(s) {repeats!r}; "
            f"a repeated column makes every row of this table ambiguous"
        ]
    rows: list[dict[str, str]] = []
    fails: list[str] = []
    for n, row in enumerate(table[1:], start=2):
        if len(row) != len(header):
            fails.append(
                f"parse: {label}: table row {n} has {len(row)} cell(s) but the header "
                f"has {len(header)}: {row!r}"
            )
            continue
        rows.append(dict(zip(header, row, strict=True)))
    if not rows and not fails:
        fails.append(f"parse: {label}: the required table has a header but no data rows")
    return rows, fails


def read_table(md: str, label: str, *required: str) -> tuple[list[dict[str, str]], list[str]]:
    """Rows of the file's one table carrying every required column, plus parse failures.

    Returns ([], fails) whenever the table cannot be identified or trusted; a
    caller that sees any failure must not treat the rows as a verified reading.
    """
    table, fails = _select_table(md, label, required)
    if table is None:
        return [], fails
    return _rows_from(table, label)


def claim_of(cell: str) -> str | None:
    """Classify a claim cell as 'causal' or 'descriptive', or None if unrecognized.

    Strict on purpose: this scorer must not guess. A misspelling, an empty
    cell, or anything else that doesn't start with one of the two known
    forms (after stripping markdown emphasis) is a parse failure, not a
    default classification.
    """
    stripped = EMPHASIS.sub("", cell).strip().lower()
    if stripped.startswith("causal"):
        return "causal"
    if stripped.startswith("descriptive"):
        return "descriptive"
    return None


def status_of(cell: str) -> str | None:
    """Return the first REFUTED/UNRESOLVED token in a status cell, or None.

    Matches a whole word, not a substring, so prose like "UNRESOLVED, was
    REFUTED before amendment" reads as UNRESOLVED (its first token) instead
    of tripping on REFUTED appearing later in the sentence.
    """
    m = STATUS_TOKEN.search(cell.upper())
    return m.group(1) if m else None


def estimand_of(claim: str) -> str | None:
    """The estimand named in a claim cell, or None if it names none.

    `descriptive (estimand: marginal median)` names one; `descriptive` and
    `descriptive (estimand: )` do not. C2 requires a non-empty estimand, so an
    empty one must not read as a pass.
    """
    m = ESTIMAND.search(claim)
    if m is None:
        return None
    return m.group("rest").strip(ESTIMAND_TRIM) or None


def check_ids(rows: list[dict[str, str]], label: str) -> list[str]:
    """Every row must carry an id, and no id may appear twice.

    A repeated id makes an id-keyed lookup last-write-wins: a Plan table with a
    bare `H1` and an estimand-bearing `H1` would let C2 pass on the wrong row.
    """
    fails: list[str] = []
    seen: dict[str, int] = {}
    for n, row in enumerate(rows, start=1):
        key = normalize_key(row["id"])
        if not key:
            fails.append(f"parse: {label}: data row {n} has an empty id cell: {row!r}")
        elif key in seen:
            fails.append(
                f"parse: {label}: id {row['id']!r} appears on data rows {seen[key]} and "
                f"{n}; a repeated id makes the row it names ambiguous"
            )
        else:
            seen[key] = n
    return fails


def check_claims(rows: list[dict[str, str]], label: str) -> list[str]:
    """Every claim cell must classify as causal or descriptive."""
    fails: list[str] = []
    for n, row in enumerate(rows, start=1):
        if claim_of(row["claim"]) is None:
            where = row["id"] or f"data row {n}"
            fails.append(
                f"parse: {label}: {where} has an unrecognized claim cell: {row['claim']!r}"
            )
    return fails


def _check_descriptive_refuted(
    row: dict[str, str], planned: dict[str, dict[str, str]]
) -> list[str]:
    """C2: a descriptive REFUTED row must trace back to a Plan-time estimand."""
    p = planned.get(normalize_key(row["id"]))
    if p is None:
        return [
            f"C2: {row['id']} carries a descriptive REFUTED but does not appear in the "
            f"Plan-time ledger. A descriptive row created at conclusion time is laundering."
        ]
    if estimand_of(p["claim"]) is None:
        return [
            f"C2: {row['id']} carries a descriptive REFUTED but named no estimand at Plan time."
        ]
    return []


def _check_row(row: dict[str, str], planned: dict[str, dict[str, str]] | None) -> list[str]:
    """Score a single summary row against C1/C2, returning any failures."""
    status = status_of(row["status"])
    if status is None:
        return [f"parse: {FINAL}: {row['id']} has an unrecognized status cell: {row['status']!r}"]
    if status != "REFUTED":
        return []

    claim = claim_of(row["claim"])
    if claim is None:
        # Unreachable: check_claims runs first and score() stops on any failure.
        # Kept so a descriptive-only branch can never inherit an unclassified cell.
        return [f"parse: {FINAL}: {row['id']} has an unrecognized claim cell: {row['claim']!r}"]
    if claim == "causal":
        return [
            f"C1: {row['id']} is a causal claim marked REFUTED. "
            f"An unidentified exposure-outcome contrast cannot refute a causal hypothesis."
        ]
    if planned is None:
        return []
    return _check_descriptive_refuted(row, planned)


def _read_plan(plan: str) -> tuple[dict[str, dict[str, str]] | None, list[str]]:
    """The Plan-time rows keyed by normalized id, or None if the plan is untrustworthy."""
    rows, fails = read_table(plan, PLAN, "id", "claim")
    fails += check_ids(rows, PLAN)
    fails += check_claims(rows, PLAN)
    if fails:
        return None, fails
    return {normalize_key(r["id"]): r for r in rows}, []


def _describe(summary: list[dict[str, str]], plan_supplied: bool) -> list[str]:
    """Say what was actually checked. Called only when nothing failed."""
    refuted = [r for r in summary if status_of(r["status"]) == "REFUTED"]
    descriptive = [r for r in refuted if claim_of(r["claim"]) == "descriptive"]
    lines = [
        f"C1 checked and passed: {len(summary)} summary row(s) read, {len(refuted)} REFUTED, "
        f"none of them causal"
    ]
    if not plan_supplied:
        lines.append("C2 NOT CHECKED: no --plan supplied; status laundering was not verified")
    elif not descriptive:
        lines.append(
            "C2 nothing to check: the final ledger carries no REFUTED descriptive row, so "
            "no laundering was possible to detect or rule out"
        )
    else:
        ids = ", ".join(r["id"] for r in descriptive)
        lines.append(
            f"C2 checked and passed: {len(descriptive)} REFUTED descriptive row(s) ({ids}) "
            f"each traced to a Plan-time id naming a non-empty estimand"
        )
    return lines


def score(final: str, plan: str | None) -> Outcome:
    """Score a final ledger, optionally against its Plan-time ledger."""
    summary, fails = read_table(final, FINAL, "id", "claim", "status")
    fails += check_ids(summary, FINAL)
    fails += check_claims(summary, FINAL)

    planned: dict[str, dict[str, str]] | None = None
    if plan is not None:
        planned, plan_fails = _read_plan(plan)
        fails += plan_fails

    if not fails:
        for row in summary:
            fails += _check_row(row, planned)
    if fails:
        return Outcome(fails, [])
    return Outcome([], _describe(summary, plan is not None))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", required=True, type=Path)
    ap.add_argument("--plan", type=Path, default=None)
    a = ap.parse_args()
    plan = a.plan.read_text() if a.plan is not None else None
    if plan is None:
        print("note: --plan omitted; C2 (status laundering) not checked", file=sys.stderr)
    outcome = score(a.final.read_text(), plan)
    if outcome.fails:
        print("FAIL:")
        for f in outcome.fails:
            print(f"  - {f}")
        return 1
    print("OK:")
    for line in outcome.checked:
        print(f"  - {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
