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
from score_ledger import check_ids, claim_of, estimand_of, normalize_key, read_table

# The Hypotheses and Tests tables are identified by a column signature unique to
# each: only Hypotheses carries "prediction if true"; only Tests carries
# "preregistered prediction". Both also carry "id", which anchors row matching.
HYPOTHESES_SIG = ("id", "claim", "prediction if true")
TESTS_SIG = ("id", "preregistered prediction", "method")

# Tests columns whose in-place update is sanctioned by the template; every other
# column of either table is immutable once the Plan-time ledger is written.
TESTS_EXEMPT = frozenset({"outcome", "evidence"})

# The Problem section's precommitted fields. These are the anti-fishing device
# the whole loop rests on -- a stop condition and an effort budget fixed before
# the data is seen -- and until 2026-08-08 no instrument read them at all.
# Measured that day: weakening the stop condition to "conclude when the leading
# explanation looks well supported" and quadrupling the effort budget between
# plan and final still printed "OK: no preregistered cell changed", because this
# script only ever diffed the two tables. A stop rule that can be silently
# rewritten once the results are in is not a precommitment.
#
# Keyed on the template's own bullet labels (references/ledger-template.md,
# Full Route Template). The value is everything after the label's colon.
PROBLEM_FIELDS = (
    "decision informed",
    "falsifiable question",
    "success criteria",
    "stop condition",
    "effort budget",
)
PROBLEM_BULLET = re.compile(
    r"^\s*[-*]\s*(?P<label>[^:\n]{1,40}?)\s*:\s*(?P<value>.*)$",
    re.MULTILINE,
)
PROBLEM_HEADING = re.compile(r"^##\s+Problem\b", re.MULTILINE)
NEXT_HEADING = re.compile(r"^##\s+", re.MULTILINE)
# An unfilled template placeholder: `<what will be done differently ...>`. A
# ledger carrying one has not actually precommitted the field.
PLACEHOLDER = re.compile(r"^<.*>$")

# Every hypothesis row must declare the one prediction whose failure refutes it:
# ledger-template.md calls this column "what makes status mechanically
# derivable", and SKILL.md's Conclusion derives REFUTED from it alone. Measured
# 2026-08-08: deleting the column outright from both ledgers passed this script
# and score_ledger.py, because a column absent from both sides is trivially
# unchanged. Immutability is not the same property as presence, so presence is
# checked separately here.
NECESSARY_COL = "necessary prediction (failure refutes)"

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


def _amendments_body(final_md: str) -> str:
    """The final ledger's one ``## Amendments`` section, or "".

    Missing or repeated headings return "" -- the fail-closed reading in which
    nothing is treated as amendment-covered.
    """
    headings = [m.start() for m in re.finditer(r"^##\s+Amendments\b", final_md, re.MULTILINE)]
    if len(headings) != 1:
        return ""
    body = final_md[headings[0] :]
    nxt = re.search(r"^##\s+", body[3:], re.MULTILINE)  # skip the heading's own "##"
    if nxt:
        body = body[: nxt.start() + 3]
    return body


def _amendment_ids(final_md: str) -> set[str]:
    """Normalized row ids named by a dated entry in the final ledger's one
    ``## Amendments`` section.

    Advisory only. If the section is missing or appears more than once, returns
    the empty set -- the fail-closed reading in which no change is treated as
    amendment-covered. A returned id means "a dated amendment mentions this id
    somewhere", not "the amendment covers the changed cell": that judgement is
    left to a human, which is why a candidate amendment still exits 1.
    """
    body = _amendments_body(final_md)
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


def _problem_fields(md: str, label: str) -> tuple[dict[str, str], list[str]]:
    """The Problem section's precommitted field values, keyed by normalized label.

    Fails closed, mirroring _compare_table: a missing or repeated `## Problem`
    heading, a missing required field, a field stated more than once, or a field
    still holding its template placeholder all make the ledger UNVERIFIABLE
    rather than silently comparing whatever was found. A precommitment this
    script cannot locate is not a precommitment it may wave through.
    """
    heads = [m.start() for m in PROBLEM_HEADING.finditer(md)]
    if len(heads) != 1:
        found = "no" if not heads else f"{len(heads)}"
        return {}, [
            f"parse: {label}: {found} '## Problem' section(s); exactly one is "
            f"required to compare the precommitted stop condition and effort budget"
        ]
    body = md[heads[0] :]
    nxt = NEXT_HEADING.search(body[3:])
    if nxt:
        body = body[: nxt.start() + 3]

    seen: dict[str, list[str]] = {}
    for m in PROBLEM_BULLET.finditer(body):
        key = SPACES.sub(" ", EMPHASIS.sub("", m.group("label"))).strip().lower()
        if key in PROBLEM_FIELDS:
            seen.setdefault(key, []).append(m.group("value").strip())

    fails: list[str] = []
    values: dict[str, str] = {}
    for field in PROBLEM_FIELDS:
        got = seen.get(field, [])
        if not got:
            fails.append(
                f"parse: {label}: the Problem section states no '{field}'; the "
                f"template requires it and it cannot be compared if it is absent"
            )
        elif len(got) > 1:
            fails.append(
                f"parse: {label}: the Problem section states '{field}' {len(got)} "
                f"times; which one is the precommitment is ambiguous"
            )
        elif PLACEHOLDER.match(got[0]) or not got[0]:
            fails.append(
                f"parse: {label}: '{field}' is empty or still holds its template "
                f"placeholder ({got[0]!r}); nothing was precommitted"
            )
        else:
            values[field] = got[0]
    return values, fails


def _compare_problem(plan_md: str, final_md: str) -> tuple[list[str], list[str], str | None]:
    """Diff the Problem section's precommitted fields between the two ledgers.

    Same contract as _compare_table: any change exits 1, a dated amendment only
    downgrades the label to CANDIDATE AMENDMENT. The template's own amendment
    example names a "revised budget", so a budget change with a covering
    amendment is legitimate -- but legitimacy is a human judgement, and this
    surfaces it rather than deciding it.
    """
    plan_vals, pf = _problem_fields(plan_md, PLAN)
    final_vals, ff = _problem_fields(final_md, FINAL)
    fails = pf + ff
    if fails:
        return fails, [], None

    amended = bool(DATE.search(_amendments_body(final_md)))
    diffs: list[str] = []
    for field in PROBLEM_FIELDS:
        pv, fv = plan_vals[field], final_vals[field]
        if pv == fv:
            continue
        kind = "formatting-only" if _cosmetic_equal(pv, fv) else "reworded"
        verdict = (
            "CANDIDATE AMENDMENT -- REVIEW REQUIRED (the final ledger carries a "
            "dated amendment; confirm it actually authorizes this change)"
            if amended
            else "UNEXPLAINED -- no dated amendment (fail closed)"
        )
        diffs.append(
            f"CHANGED [{kind}]: Problem field '{field}' -- {verdict}\n"
            f"    plan : {pv!r}\n"
            f"    final: {fv!r}"
        )
    checked = (
        f"Problem section compared: {len(PROBLEM_FIELDS)} precommitted "
        f"field(s) ({', '.join(PROBLEM_FIELDS)})"
    )
    return [], diffs, checked


def _check_necessary_column(rows: list[dict[str, str]], label: str) -> list[str]:
    """The Hypotheses table must carry a necessary-prediction column, populated.

    A presence check, not an immutability check: the diff above compares columns
    the two ledgers share, so a column deleted from both sides reads as
    unchanged. Without this, a ledger that never declared what could refute each
    hypothesis passes every instrument.

    This establishes that the declaration exists -- not that a REFUTED status
    actually followed from that prediction's failure. The Tests table carries no
    machine link naming which test exercises the necessary prediction, so the
    derivation itself remains unverified by any instrument; adding such a link
    is an agent-facing schema change and owes measured arms.
    """
    if not rows:
        return []
    if NECESSARY_COL not in rows[0]:
        return [
            f"parse: {label} Hypotheses table carries no "
            f"'{NECESSARY_COL}' column. That column is what makes status "
            f"mechanically derivable (references/ledger-template.md); a table "
            f"without it declares nothing that could refute any hypothesis."
        ]
    fails = []
    for r in rows:
        cell = r[NECESSARY_COL].strip()
        if not cell or PLACEHOLDER.match(cell) or cell in {"-", "--", "n/a", "N/A", "..."}:
            fails.append(
                f"parse: {label} Hypotheses row {r['id']} declares no necessary "
                f"prediction ({r[NECESSARY_COL]!r}); every row must carry one, "
                f"declared at Plan time before any outcome is read."
            )
    return fails


def _check_schema(plan_md: str, final_md: str) -> list[str]:
    """Schema requirements neither ledger may omit, checked on both sides.

    Distinct from the diff below, which only compares columns the two ledgers
    share and so reads a column deleted from both as unchanged. A parse failure
    here reports whatever read_table could recover; a table it could not parse
    at all is already reported by _compare_table and is not double-reported.
    """
    fails: list[str] = []
    for md, who in ((plan_md, PLAN), (final_md, FINAL)):
        rows, parse_fails = read_table(md, f"{who} Hypotheses table", *HYPOTHESES_SIG)
        if parse_fails:
            continue
        fails += _check_necessary_column(rows, who)
        fails += _check_descriptive_estimand(rows, who)
    return fails


def _check_descriptive_estimand(rows: list[dict[str, str]], label: str) -> list[str]:
    """Every descriptive hypothesis row must name its estimand.

    references/ledger-template.md states this for the Hypotheses table with no
    qualifier: "a descriptive row names the estimand its prediction is about".
    score_ledger's C2 enforces it only on rows that end up REFUTED, because C2
    is a laundering check on the conclusion -- a different question from whether
    the plan declared what it was estimating. A descriptive claim with no
    estimand is unfalsifiable in the same way an absent necessary prediction is:
    there is no stated quantity for a prediction to be wrong about.

    Calibrated 2026-08-08 against every ledger archived in this tree: 25
    descriptive rows, 0 without an estimand. This requires of new work only what
    all existing work already does.
    """
    return [
        f"parse: {label} Hypotheses row {r['id']} is descriptive but names no "
        f"estimand ({r['claim']!r}); the documented form is "
        f"`descriptive (estimand: <the quantity>)`."
        for r in rows
        if claim_of(r["claim"]) == "descriptive" and estimand_of(r["claim"]) is None
    ]


def _column_mismatch(plan_cols: set[str], final_cols: set[str], label: str) -> str | None:
    """The parse failure for two ledgers whose columns differ, or None if they match."""
    if plan_cols == final_cols:
        return None
    only_plan = ", ".join(sorted(plan_cols - final_cols)) or "(none)"
    only_final = ", ".join(sorted(final_cols - plan_cols)) or "(none)"
    return (
        f"parse: {label} table: the two ledgers carry different columns "
        f"(only in plan: {only_plan}; only in final: {only_final}); "
        f"cannot compare immutable cells like-for-like"
    )


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
    if mismatch := _column_mismatch(plan_cols, final_cols, label):
        return [mismatch], [], None

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
    pf, pd, pc = _compare_problem(plan_md, final_md)
    fails += pf
    diffs += pd
    if pc is not None:
        checked.append(pc)
    fails += _check_schema(plan_md, final_md)
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
