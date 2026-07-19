#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare a Plan-time ledger against the final ledger for silent rewording of
preregistered cells.

WHAT THIS EXISTS TO CATCH

  The ledger contract makes preregistered predictions immutable: a test entry's
  ``outcome`` and ``evidence`` fields are the only sanctioned in-place updates,
  and any other change to a Plan-time cell requires a dated Amendment, not an
  edit. Nothing checked that. An outcome-fill Edit was observed silently
  rewording preregistered Tests cells at conclusion time -- a censoring bound
  dropped from a method, a prediction's ``/`` widened to ``and/or`` to fit the
  result it was about to record -- while the Amendments section said "none".
  ``check_prereg.py`` only certifies that the *first* ledger write already
  carried predictions; ``score_ledger.py`` C2 compares *statuses*, never the
  prediction or method text. This script is the missing plan-vs-final cell diff.

WHAT COUNTS AS IMMUTABLE

  Per references/ledger-template.md, ``outcome`` and ``evidence`` are the only
  sanctioned in-place updates. So for every row present in BOTH ledgers under
  the same id, this compares:

    - every column of the Hypotheses table (id, claim, candidate explanation,
      the two prediction columns, necessary prediction, cheapest adequate test,
      data needed), and
    - every column of the Tests table EXCEPT ``outcome`` and ``evidence``
      (id, hypothesis, preregistered prediction, method).

  The issue that motivated this names prediction-if-true/false, necessary
  prediction, and method specifically; this enforces the whole immutability rule
  the template states, of which those columns are a subset, so a Tests row
  silently reassigned to a different hypothesis is caught too.

  Comparison is exact on the cells as the table parser returns them -- stripped,
  with ``\\|`` unescaped to ``|`` once (score_ledger.parse_tables already does
  this; it is not repeated here, since a second unescape is not idempotent and
  could collapse a real difference). Internal whitespace, case, punctuation, and
  markdown emphasis are all significant (leading and trailing whitespace is
  stripped by the parser): the contract is immutability, and a run that
  wants to reword a preregistered cell must file a dated Amendment, not edit it.
  A change that is only emphasis/whitespace is still reported, labelled
  ``formatting-only`` so a reader can see it is cosmetic -- it does not change
  the exit code, because the instrument's job is to surface every edit for a
  human, not to wave cosmetic ones through.

ROWS THAT APPEAR OR DISAPPEAR

  A Plan-time row absent from the final ledger is a deletion of a preregistered
  prediction and is reported. A row present only in the final ledger was added
  after Plan time; the template requires such additions to be dated Amendments
  (and post-data hypotheses to carry the ``retrospective`` label), so it is
  reported for review, noting for a hypothesis whether the label is present.

THE AMENDMENT ESCAPE VALVE -- ADVISORY ONLY

  A difference is legitimate if a dated Amendment names the cell. Matching an
  Amendment line to the exact cell it is meant to cover is a semantic judgement
  this script does not make. It only checks, for each changed row, whether the
  final ledger's Amendments section carries a dated entry that names the row id;
  if so the change is labelled a CANDIDATE AMENDMENT for a human to verify. It
  is NEVER auto-passed: any preregistered difference exits 1 either way. Absence
  or ambiguity of an Amendments section is treated as "no covering amendment"
  (the fail-closed reading), never as a reason the run could not be checked.

WHY IT IS BUILT THE WAY IT IS

  A run's own account of what it changed cannot be trusted, so this must fail
  closed and report only what it actually compared.

  Fail closed. If either ledger's Hypotheses or Tests table cannot be uniquely
  identified, has a repeated or empty id, has a row whose cell count does not
  match its header, or -- for a given table -- the two files do not carry the
  same set of columns (exempt columns included; a well-formed Tests table always
  carries Outcome and Evidence at Plan time), the run is UNVERIFIABLE (exit 2)
  and names what could not be compared. It never diffs a table it failed to
  understand.

  Report only what was earned. Success output states, per table, how many shared
  rows and columns were compared, so an UNVERIFIABLE run never reads as though a
  table it could not parse was checked.

Exit codes (mirroring check_prereg.py):
  0  every immutable cell identical; no row added or removed since Plan time
  1  a preregistered cell differs, a Plan-time row was deleted, or a row was
     added after Plan time -- each listed, and each difference labelled
     unexplained or candidate-amendment
  2  UNVERIFIABLE: a file could not be read, a required table could not be
     uniquely parsed, an id was empty or repeated, or the two ledgers' immutable
     column sets for a table differ

    uv run hypothesis-driven-analysis/tests/compare_prereg.py \\
        --plan plan.md --final final.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

# Reuse the scorer's table machinery so parsing and fail-closed behaviour stay
# identical across the two instruments. score_ledger.py sits beside this file;
# the script's own directory is on sys.path[0] when run directly or via uv.
from score_ledger import check_ids, normalize_key, read_table

# The Hypotheses and Tests tables are identified by a column signature unique to
# each: only Hypotheses carries "prediction if true"; only Tests carries
# "preregistered prediction". Both also carry "id", which anchors row matching.
HYPOTHESES_SIG = ("id", "claim", "prediction if true")
TESTS_SIG = ("id", "preregistered prediction", "method")

# Tests columns whose in-place update is sanctioned by the template; every other
# column of either table is immutable once the Plan-time ledger is written.
TESTS_EXEMPT = frozenset({"outcome", "evidence"})

EMPHASIS = re.compile(r"[*_`]")
SPACES = re.compile(r"\s+")
# A dated Amendment entry starts (after list punctuation) with an ISO date.
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RETROSPECTIVE = re.compile(r"retrospective", re.IGNORECASE)

PLAN = "plan ledger"
FINAL = "final ledger"


class Outcome(NamedTuple):
    """What compare() concluded: differences to report, and what it compared."""

    fails: list[str]  # UNVERIFIABLE parse failures (exit 2 when present)
    diffs: list[str]  # reportable differences (exit 1 when present, no fails)
    checked: list[str]  # per-table statement of what was actually compared


def _table_columns(table_rows: list[dict[str, str]]) -> set[str]:
    """The normalized column names carried by a parsed table's rows."""
    return set(table_rows[0].keys()) if table_rows else set()


def _cosmetic_equal(a: str, b: str) -> bool:
    """True when two cells differ only in markdown emphasis and whitespace.

    Used solely to label a reported difference as ``formatting-only``; it never
    suppresses the difference or changes the exit code.
    """

    def fold(s: str) -> str:
        return SPACES.sub(" ", EMPHASIS.sub("", s)).strip()

    return fold(a) == fold(b)


def _amendment_ids(final_md: str) -> set[str]:
    """Normalized row ids named by a dated entry in the final ledger's one
    ``## Amendments`` section.

    Advisory only. If the section is missing or appears more than once, returns
    the empty set -- the fail-closed reading in which no change is treated as
    amendment-covered. A returned id means "a dated amendment mentions this id
    somewhere", not "the amendment covers the changed cell": that judgement is
    left to a human, which is why a candidate amendment still exits 1.
    """
    headings = [m.start() for m in re.finditer(r"^##\s+Amendments\b", final_md, re.MULTILINE)]
    if len(headings) != 1:
        return set()
    body = final_md[headings[0] :]
    nxt = re.search(r"^##\s+", body[3:], re.MULTILINE)  # skip the heading's own "##"
    if nxt:
        body = body[: nxt.start() + 3]
    named: set[str] = set()
    for line in body.splitlines():
        if not DATE.search(line):
            continue
        # Tokens that could be a row id: a letter run followed by digits, like
        # H1, T6, H4. Bare numbers are excluded so the dated entry's own date
        # fragments (2026, 07, 19) never enter the set -- template ids are always
        # letter-prefixed, and this only affects a diff's label, never the exit.
        for tok in re.findall(r"[A-Za-z]+\d+", line):
            named.add(normalize_key(tok))
    return named


def _compare_table(
    plan_md: str,
    final_md: str,
    label: str,
    signature: tuple[str, ...],
    amended: set[str],
) -> tuple[list[str], list[str], str | None]:
    """Diff one table's immutable cells between the two ledgers.

    Returns (parse_fails, diffs, checked_line). A non-empty parse_fails means the
    table could not be trusted and no diff was produced for it.
    """
    plan_rows, pf = read_table(plan_md, f"{PLAN} {label} table", *signature)
    final_rows, ff = read_table(final_md, f"{FINAL} {label} table", *signature)
    fails = pf + ff
    fails += check_ids(plan_rows, f"{PLAN} {label} table")
    fails += check_ids(final_rows, f"{FINAL} {label} table")
    if fails:
        return fails, [], None

    plan_cols = _table_columns(plan_rows)
    final_cols = _table_columns(final_rows)
    if plan_cols != final_cols:
        only_plan = ", ".join(sorted(plan_cols - final_cols)) or "(none)"
        only_final = ", ".join(sorted(final_cols - plan_cols)) or "(none)"
        return (
            [
                f"parse: {label} table: the two ledgers carry different columns "
                f"(only in plan: {only_plan}; only in final: {only_final}); "
                f"cannot compare immutable cells like-for-like"
            ],
            [],
            None,
        )

    # outcome/evidence are sanctioned in-place updates in the Tests table only;
    # the Hypotheses table has no such column and every one of its cells is
    # immutable, so nothing is exempted there.
    exempt = TESTS_EXEMPT if label == "Tests" else frozenset()
    immutable = sorted(c for c in plan_cols if c not in exempt)
    plan_by = {normalize_key(r["id"]): r for r in plan_rows}
    final_by = {normalize_key(r["id"]): r for r in final_rows}
    diffs: list[str] = []

    for pid, prow in plan_by.items():
        rid = prow["id"]
        if pid not in final_by:
            diffs.append(
                f"DELETED: {label} row {rid} was preregistered at Plan time but is "
                f"absent from the final ledger -- a preregistered row cannot be dropped "
                f"without a dated amendment."
            )
            continue
        frow = final_by[pid]
        for col in immutable:
            # read_table's cells are already stripped and pipe-unescaped by
            # score_ledger.parse_tables; compare them as-is. Unescaping a second
            # time is not idempotent (\\| -> \| -> |) and could collapse a real
            # difference to equal, so it must not be repeated here.
            pv, fv = prow[col], frow[col]
            if pv == fv:
                continue
            kind = "formatting-only" if _cosmetic_equal(pv, fv) else "reworded"
            if pid in amended:
                verdict = (
                    "CANDIDATE AMENDMENT -- REVIEW REQUIRED (a dated amendment names "
                    "this row; confirm it actually covers this cell)"
                )
            else:
                verdict = "UNEXPLAINED -- no dated amendment names this row (fail closed)"
            diffs.append(
                f"CHANGED [{kind}]: {label} row {rid}, column '{col}' -- {verdict}\n"
                f"    plan : {pv!r}\n"
                f"    final: {fv!r}"
            )

    for fid, frow in final_by.items():
        if fid in plan_by:
            continue
        rid = frow["id"]
        extra = ""
        if label == "Hypotheses" and not RETROSPECTIVE.search(rid):
            extra = " and its id carries no 'retrospective' label"
        note = ""
        if fid in amended:
            note = " (a dated amendment names it; confirm it authorizes the addition)"
        diffs.append(
            f"ADDED: {label} row {rid} appears only in the final ledger -- a row added "
            f"after Plan time needs a dated amendment{extra}{note}."
        )

    shared = set(plan_by) & set(final_by)
    plan_only = set(plan_by) - set(final_by)
    final_only = set(final_by) - set(plan_by)
    checked = (
        f"{label} table compared: {len(shared)} shared row(s) across "
        f"{len(immutable)} immutable column(s) ({', '.join(immutable)}); "
        f"{len(plan_only)} plan-only, {len(final_only)} final-only"
    )
    return [], diffs, checked


def compare(plan_md: str, final_md: str) -> Outcome:
    """Compare the Plan-time and final ledgers for preregistered-cell drift."""
    amended = _amendment_ids(final_md)
    fails: list[str] = []
    diffs: list[str] = []
    checked: list[str] = []
    for label, sig in (("Hypotheses", HYPOTHESES_SIG), ("Tests", TESTS_SIG)):
        tf, td, tc = _compare_table(plan_md, final_md, label, sig, amended)
        fails += tf
        diffs += td
        if tc is not None:
            checked.append(tc)
    if fails:
        return Outcome(fails, [], [])
    return Outcome([], diffs, checked)


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan-vs-final preregistered-cell comparator")
    ap.add_argument("--plan", required=True, type=Path)
    ap.add_argument("--final", required=True, type=Path)
    a = ap.parse_args()
    try:
        plan_md = a.plan.read_text(encoding="utf-8")
        final_md = a.final.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"UNVERIFIABLE: cannot read a ledger: {exc}")
        return 2

    outcome = compare(plan_md, final_md)
    if outcome.fails:
        print("UNVERIFIABLE:")
        for f in outcome.fails:
            print(f"  - {f}")
        return 2
    if outcome.diffs:
        print("DIFFERENCES:")
        for d in outcome.diffs:
            print(f"  - {d}")
        print("checked:")
        for c in outcome.checked:
            print(f"  - {c}")
        return 1
    print("OK: no preregistered cell changed between plan and final")
    for c in outcome.checked:
        print(f"  - {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
