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

SYNTACTIC CHECKS ONLY

  This scorer verifies syntactic presence, not semantic quality. For example,
  a cell like `descriptive (estimand: N/A)` satisfies the C2 syntactic check
  by design; judging whether a named estimand is meaningful is the rubric
  grader's job, not this script's.

Checks exactly two things, both syntactic:

  C1  No row whose claim is `causal` carries status REFUTED.
      Valid only under the scope above. This is the regression the
      status-adequacy revision exists to prevent. A `data-artifact` row is
      exempt from C1: the skill permits refuting one once coverage and
      missingness have been probed -- but see C2, which still applies to it.
  C2  Every REFUTED `descriptive` or `data-artifact` row existed in the
      Plan-time ledger under the same id AND the same claim class. A
      `descriptive` row must also have named a non-empty estimand there; a
      `data-artifact` row need not, since a data-artifact claim (records
      missing or miscounted) has no estimand to name. Catches status
      laundering in both its shapes: inventing a claim at conclusion time (a
      new id), and relabelling an existing row's class (e.g. a Plan-time
      `causal` row re-dressed as `data-artifact`, which cannot be C1-REFUTED
      under scope) to house a REFUTED. Runs on `descriptive`/`data-artifact`
      conclusion rows; a `causal` conclusion row is C1's, not C2's.

WHY IT IS BUILT THE WAY IT IS

A run's own summary of how it did cannot be trusted, so this scorer must never
report a check it did not actually perform. Two rules follow.

Fail closed. Anything it cannot confidently resolve is a parse failure and the
run exits 1 naming what could not be verified: a file with no table carrying the
required columns, more than one such table, a repeated column name, a data row
whose cell count does not match the header, a repeated or empty id, a claim cell
that is none of `causal`, `descriptive`, or `data-artifact`, or a status cell
carrying neither REFUTED nor UNRESOLVED. It never drops or waves through
input it failed to understand, and it never reports C2 against a --plan it
could not parse.

Fail closed row-locally, not audit-wide. A structural failure -- no identifiable
table, a missing or ambiguous id -- means no row can be trusted, so the run bails
before any policy check. But an unrecognized claim or status *cell* is a
row-local fault: the run reports it and still applies C1/C2 to every sibling row
that parses. This exists because ledgers drift their claim/status vocabulary
(issue #73), and the fail-closed-audit-wide version let one drifted token in an
UNRESOLVED row suppress C1 on a genuine causal-REFUTED row beside it -- exit 1,
but the violation the scorer exists to catch went unreported. A near-miss cell
carries a non-authoritative repair hint; the scorer never coerces it to a class.

Report only what was earned. Success output states, per check, whether it was
checked and passed, had nothing to check, or was not checked at all — a run with
no REFUTED descriptive or data-artifact row has not verified C2, and says so
rather than claiming a pass it did not earn.

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
import unicodedata
from pathlib import Path
from typing import NamedTuple

ROW = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
EMPHASIS = re.compile(r"[*_`]")
SPACES = re.compile(r"\s+")
STATUS_TOKEN = re.compile(r"\b(REFUTED|UNRESOLVED)\b")
# The documented syntax (references/ledger-template.md): a descriptive claim
# cell is written `descriptive (estimand: <the quantity>)`. Anchored to that
# labeled, parenthesised form only -- the word "estimand" appearing anywhere
# else in the cell (including prose that disclaims having one) is not a match.
ESTIMAND = re.compile(r"^descriptive\s*\(\s*estimand\s*:\s*(?P<rest>[^)]*)\)", re.IGNORECASE)
# Punctuation that can sit around the captured content once split out of its
# enclosing parenthesis: ASCII punctuation plus U+2013 en dash, U+2014 em
# dash, U+2026 ellipsis.
ESTIMAND_TRIM = " \t:=()[]{}<>*_.,;!?\"'-\u2013\u2014\u2026"
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.*?)\s*#*\s*$")
COMPLETENESS_LABEL = re.compile(
    r"^\s*[-*]\s*source\s+completeness\s+semantics\s*:?\s*", re.IGNORECASE
)
BULLET_OR_HEADING = re.compile(r"^\s*(?:[-*]\s|#{1,6}\s)")
# A documented per-source completeness declaration: a source id (letters+digits)
# immediately followed by a `:` or em/en-dash key-separator, then the value up to
# the first reason delimiter. Anchored so a prose mention of the id (`S2,` /
# `S2 (activity.csv)`) is not read as a declaration.
C3B_DECL = re.compile(
    r"(?P<sid>\b[A-Za-z]{1,4}\s*\d+\b)\s*[:\u2013\u2014]\s*(?P<val>[^\u2013\u2014;,\n]+)"
)

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


def section_body(md: str, name: str) -> str | None:
    """The body under the `## <name>` heading, up to the next heading of the
    same or higher level, or None if no such heading exists.

    Heading titles are matched through the same emphasis/whitespace/case folding
    as ids, so `## Conclusion`, `## conclusion`, and `## **Conclusion**` are one.
    A deeper subheading (### …) stays inside the section; a sibling or higher one
    ends it.
    """
    target = normalize_key(name)
    out: list[str] = []
    capturing = False
    start_level = 0
    for line in md.split("\n"):
        m = HEADING.match(line)
        if m:
            level = len(m.group("hashes"))
            if capturing and level <= start_level:
                break
            if not capturing and normalize_key(m.group("title")) == target:
                capturing = True
                start_level = level
                continue
        if capturing:
            out.append(line)
    return "\n".join(out) if capturing else None


def completeness_bullet(md: str) -> str | None:
    """The content of the `- Source completeness semantics: …` bullet with its
    label removed, or None if the bullet is absent.

    Captures the label line plus any continuation lines until the next bullet,
    heading, or blank line, so a bullet wrapped across lines is read whole. The
    label match tolerates markdown emphasis and an optional trailing colon.
    """
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if COMPLETENESS_LABEL.match(EMPHASIS.sub("", line)):
            first = COMPLETENESS_LABEL.sub("", EMPHASIS.sub("", line)).strip()
            parts = [first] if first else []
            for cont in lines[i + 1 :]:
                if not cont.strip() or BULLET_OR_HEADING.match(cont):
                    break
                parts.append(cont.strip())
            return " ".join(parts).strip() or None
    return None


def _c3b_value(final: str, source_id: str) -> tuple[str | None, list[str]]:
    """The declared completeness value for `source_id`, read from the documented
    `<sid>: <value>` atoms in the completeness bullet, or a fail-closed message.

    Returns (value, []) on exactly one declaration for the source, (None, [fail])
    when the bullet is missing, the source is undeclared, or two declarations for
    the source conflict. The value is read through emphasis/backtick stripping but
    its case is preserved so the caller can require uppercase UNKNOWN.
    """
    bullet = completeness_bullet(final)
    if bullet is None:
        return None, [
            "parse: final ledger: C3b: no `Source completeness semantics` bullet found; "
            "cannot verify the completeness declaration"
        ]
    key = normalize_key(source_id)
    values = [
        EMPHASIS.sub("", m.group("val")).strip()
        for m in C3B_DECL.finditer(bullet)
        if normalize_key(m.group("sid")) == key
    ]
    if not values:
        return None, [
            f"parse: final ledger: C3b: {source_id} has no `{source_id}: <reading>` "
            f"declaration in the completeness bullet; the documented form is "
            f"`{source_id}: UNKNOWN — <why no evidence discriminates>`"
        ]
    if len({v for v in values}) > 1:
        return None, [
            f"parse: final ledger: C3b: {source_id} carries conflicting completeness "
            f"declarations {values!r}; cannot tell which reading is asserted"
        ]
    return values[0], []


def check_c3b(final: str, source_id: str) -> list[str]:
    """C3b: the implicated source's completeness entry must declare canonical
    `UNKNOWN`. Fail closed on anything else.

    Uppercase-exact on the value token: a lowercase `unknown`, a negated
    `not UNKNOWN`, or a definite reading (`still-open`) each fails, because under
    the flag's scope the only licensed reading is a declared UNKNOWN.
    """
    value, fails = _c3b_value(final, source_id)
    if fails:
        return fails
    assert value is not None
    if value == "UNKNOWN":
        return []
    return [
        f"C3b: {source_id}'s completeness reading is {value!r}, not the canonical "
        f"`UNKNOWN`. Under --c3-unknown-source scope no evidence can discriminate "
        f"{source_id}'s missingness, so its only licensed declaration is `UNKNOWN`."
    ]


def _select_table(
    md: str, label: str, required: tuple[str, ...], excluded: tuple[str, ...] = ()
) -> tuple[list[list[str]] | None, list[str]]:
    """The one table whose header carries every required column and none of the
    excluded ones, or a parse failure.

    `excluded` narrows a required-column match to the table it's actually meant
    to find when more than one table in the file happens to carry the same
    required columns — e.g. a Plan-time ledger's Hypotheses table and its
    Conclusion summary both carry `id` + `claim`, and only `status` tells them
    apart. Zero matches and more than one match are both failures: neither
    leaves the scorer able to say which rows it was supposed to check.
    """
    cols = ", ".join(required)
    desc = cols if not excluded else f"{cols}, excluding {', '.join(excluded)}"
    matches = [
        t
        for t in parse_tables(md)
        if t and _header_has(t[0], required) and _header_lacks(t[0], excluded)
    ]
    if not matches:
        return None, [
            f"parse: {label}: no table found whose header carries every required "
            f"column ({desc}); nothing in this file could be checked"
        ]
    if len(matches) > 1:
        return None, [
            f"parse: {label}: {len(matches)} tables carry the required columns "
            f"({desc}); cannot tell which one to score"
        ]
    return matches[0], []


def _header_has(header: list[str], required: tuple[str, ...]) -> bool:
    names = [normalize_key(h) for h in header]
    return all(r in names for r in required)


def _header_lacks(header: list[str], excluded: tuple[str, ...]) -> bool:
    names = [normalize_key(h) for h in header]
    return not any(e in names for e in excluded)


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


def read_table(
    md: str, label: str, *required: str, excluded: tuple[str, ...] = ()
) -> tuple[list[dict[str, str]], list[str]]:
    """Rows of the file's one table carrying every required column (and none of
    the excluded ones), plus parse failures.

    Returns ([], fails) whenever the table cannot be identified or trusted; a
    caller that sees any failure must not treat the rows as a verified reading.
    """
    table, fails = _select_table(md, label, required, excluded)
    if table is None:
        return [], fails
    return _rows_from(table, label)


def claim_of(cell: str) -> str | None:
    """Classify a claim cell as 'causal', 'descriptive', or 'data-artifact', or
    None if unrecognized.

    Strict on purpose: this scorer must not guess. A misspelling, an empty
    cell, or anything else that doesn't start with one of the three known
    forms (after stripping markdown emphasis) is a parse failure, not a
    default classification.
    """
    stripped = EMPHASIS.sub("", cell).strip().lower()
    if stripped.startswith("causal"):
        return "causal"
    if stripped.startswith("descriptive"):
        return "descriptive"
    if stripped.startswith("data-artifact"):
        return "data-artifact"
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
    """The estimand named in a claim cell, or None if it does not match the
    documented `descriptive (estimand: <quantity>)` syntax.

    `descriptive (estimand: marginal median)` names one, tolerant of case and
    markdown emphasis. `descriptive`, `descriptive (estimand: )`, and prose
    that merely mentions or disclaims "estimand" outside that labeled,
    parenthesised form -- e.g. `descriptive - no estimand named` -- do not:
    C2 requires the documented syntax with non-empty content, not the word.

    This check is syntactic presence, not semantic quality: a cell like
    `descriptive (estimand: N/A)` satisfies it by design, and judging whether
    a named estimand is meaningful is the rubric grader's job, not this
    script's.
    """
    stripped = EMPHASIS.sub("", claim).strip()
    m = ESTIMAND.match(stripped)
    if m is None:
        return None
    # Strip Unicode Cf (Format category) characters like U+200B (zero-width space),
    # U+FEFF (zero-width no-break space), U+200C, U+200D, U+2060, U+00AD, etc.
    content = "".join(c for c in m.group("rest") if unicodedata.category(c) != "Cf")
    return content.strip(ESTIMAND_TRIM) or None


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
    """Every claim cell must classify as causal, descriptive, or data-artifact."""
    fails: list[str] = []
    for n, row in enumerate(rows, start=1):
        if claim_of(row["claim"]) is None:
            where = row["id"] or f"data row {n}"
            fails.append(
                f"parse: {label}: {where} has an unrecognized claim cell: {row['claim']!r}"
            )
    return fails


# Non-authoritative repair hints for the exact drift tokens the suite has
# measured landing in a claim cell (issue #73): they arrive because SKILL.md uses
# "associative" for conclusion wording and statistical language for methods. The
# scorer never *coerces* a drift token to a class -- that could exempt a real
# causal row from C1 -- it only points the producer at where the word belongs,
# and still fails the row closed.
_CLAIM_DRIFT_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("associative", "associational", "correlational", "observational"),
        "`associative` is conclusion wording (SKILL.md Conclusion), not a claim "
        "class; a non-causal explanation is `descriptive` or `data-artifact`",
    ),
    (
        ("statistical", "inferential", "quantitative"),
        "`statistical` is not a claim class; if it names a quantity write "
        "`descriptive (estimand: ...)`, otherwise it belongs in Limitations",
    ),
)


def _claim_hint(cell: str) -> str:
    """A non-authoritative repair hint for a known claim-cell drift token, or ''.

    Read through the same emphasis/case normalization as `claim_of`, so a hint
    fires on exactly the forms that fail classification. It never changes the
    verdict -- the row still fails closed.
    """
    words = EMPHASIS.sub("", cell).strip().lower().split()
    if not words:
        return ""
    head = words[0].strip(",;:.()")
    for tokens, hint in _CLAIM_DRIFT_HINTS:
        if head in tokens:
            return f" -- {hint}"
    return ""


def _status_hint(cell: str) -> str:
    """A non-authoritative hint for the measured status-cell drift, or ''."""
    text = EMPHASIS.sub("", cell).strip().lower()
    if "best" in text and "support" in text:
        return (
            ' -- "best supported" is conclusion language for the `basis` column, '
            "not a status; the status set is `REFUTED` or `UNRESOLVED`"
        )
    return ""


def _check_laundering(
    row: dict[str, str], claim: str, planned: dict[str, dict[str, str]]
) -> list[str]:
    """C2: a REFUTED descriptive or data-artifact row must trace back to the
    Plan-time ledger under the same id and the same claim class.

    A descriptive row must also have named a non-empty estimand there. A
    data-artifact row need not: a data-artifact claim ("these records are
    missing or miscounted") has no estimand to name, and demanding one would
    be cry-wolf. Either way, the row must have existed at Plan time under this
    class -- inventing an id and relabelling an existing row's class are the
    two shapes of the laundering this catches. A causal row re-dressed as
    data-artifact to house a REFUTED (a causal row cannot be C1-REFUTED under
    scope) is the relabel case, and it traces to the same id, so the id check
    alone would wave it through.
    """
    p = planned.get(normalize_key(row["id"]))
    if p is None:
        return [
            f"C2: {row['id']} carries a {claim} REFUTED but does not appear in the "
            f"Plan-time ledger. A {claim} row created at conclusion time is laundering."
        ]
    plan_claim = claim_of(p["claim"])
    if plan_claim != claim:
        # planned is only non-None when every Plan-time claim classified, so
        # plan_claim is a real class here, not None.
        return [
            f"C2: {row['id']} carries a {claim} REFUTED but was {plan_claim} at Plan time. "
            f"Relabelling a hypothesis's claim class at conclusion time to house a REFUTED "
            f"is laundering."
        ]
    if claim == "descriptive" and estimand_of(p["claim"]) is None:
        return [
            f"C2: {row['id']} carries a descriptive REFUTED but named no estimand at Plan time."
        ]
    return []


def _check_row(row: dict[str, str], planned: dict[str, dict[str, str]] | None) -> list[str]:
    """Score a single summary row against C1/C2, returning any failures.

    A row's own claim and status cells are validated here, per row. An
    unrecognized cell fails *this* row (still exit 1), but must not suppress
    C1/C2 on sibling rows that parse cleanly: one drifted vocabulary token in
    a status or basis-adjacent cell would otherwise blind the audit to a real
    causal-REFUTED violation elsewhere in the same table (issue #73). Both
    cells are checked before the REFUTED short-circuit so a drift token in an
    UNRESOLVED row is still reported.
    """
    fails: list[str] = []
    status = status_of(row["status"])
    if status is None:
        fails.append(
            f"parse: {FINAL}: {row['id']} has an unrecognized status cell: "
            f"{row['status']!r}{_status_hint(row['status'])}"
        )
    claim = claim_of(row["claim"])
    if claim is None:
        fails.append(
            f"parse: {FINAL}: {row['id']} has an unrecognized claim cell: "
            f"{row['claim']!r}{_claim_hint(row['claim'])}"
        )
    if status is None or claim is None:
        # A row we could not parse cannot be policy-checked; the rows that did
        # parse still are -- see score().
        return fails
    if status != "REFUTED":
        return []

    if claim == "causal":
        return [
            f"C1: {row['id']} is a causal claim marked REFUTED. "
            f"An unidentified exposure-outcome contrast cannot refute a causal hypothesis."
        ]
    # claim is descriptive or data-artifact: both are subject to C2 (status
    # laundering), which requires a --plan to check against.
    if planned is None:
        return []
    return _check_laundering(row, claim, planned)


def _read_plan(plan: str) -> tuple[dict[str, dict[str, str]] | None, list[str]]:
    """The Plan-time rows keyed by normalized id, or None if the plan is untrustworthy.

    Targets the Hypotheses table specifically: it carries `id` + `claim` but no
    `status` column, which distinguishes it from the ledger template's other
    `id` + `claim` table, the Conclusion per-hypothesis summary (which also
    carries `status`). Without excluding `status`, a real Plan-time ledger
    written from the template would carry two matching tables and fail to
    parse even though which one to read is unambiguous.
    """
    rows, fails = read_table(plan, PLAN, "id", "claim", excluded=("status",))
    fails += check_ids(rows, PLAN)
    fails += check_claims(rows, PLAN)
    if fails:
        return None, fails
    return {normalize_key(r["id"]): r for r in rows}, []


def _describe(summary: list[dict[str, str]], plan_supplied: bool) -> list[str]:
    """Say what was actually checked. Called only when nothing failed."""
    refuted = [r for r in summary if status_of(r["status"]) == "REFUTED"]
    laundering_candidates = [
        r for r in refuted if claim_of(r["claim"]) in ("descriptive", "data-artifact")
    ]
    lines = [
        f"C1 checked and passed: {len(summary)} summary row(s) read, {len(refuted)} REFUTED, "
        f"none of them causal"
    ]
    if not plan_supplied:
        lines.append("C2 NOT CHECKED: no --plan supplied; status laundering was not verified")
    elif not laundering_candidates:
        lines.append(
            "C2 nothing to check: the final ledger carries no REFUTED descriptive or "
            "data-artifact row, so no laundering was possible to detect or rule out"
        )
    else:
        ids = ", ".join(r["id"] for r in laundering_candidates)
        lines.append(
            f"C2 checked and passed: {len(laundering_candidates)} REFUTED descriptive/"
            f"data-artifact row(s) ({ids}) each traced to a Plan-time id, the descriptive "
            f"ones naming a non-empty estimand there"
        )
    return lines


def score(final: str, plan: str | None) -> Outcome:
    """Score a final ledger, optionally against its Plan-time ledger."""
    summary, fails = read_table(final, FINAL, "id", "claim", "status")
    fails += check_ids(summary, FINAL)
    # Everything read_table and check_ids catch is audit-wide: a malformed table
    # grid (no table with the required columns, more than one, a repeated column
    # name, a row whose cell count does not match the header) or a missing or
    # ambiguous id leaves no trustworthy row grid to police, so bail before any
    # per-row check. Only an unrecognized claim or status *value* in an
    # otherwise well-formed row is row-local: _check_row reports it and still
    # applies C1/C2 to the sibling rows that parse, so one drifted vocabulary
    # token cannot blind the audit to a real causal-REFUTED violation (issue
    # #73). Making a cell-count mismatch row-local too would need read_table to
    # yield its good rows alongside the bad one; left audit-wide for now, since
    # no measured run has drifted cell counts.
    if fails:
        return Outcome(fails, [])

    planned: dict[str, dict[str, str]] | None = None
    if plan is not None:
        planned, plan_fails = _read_plan(plan)
        fails += plan_fails

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
