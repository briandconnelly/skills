"""Executable tests for score_ledger.py (issue #83) — run with:

    uv run --with pytest pytest hypothesis-driven-analysis/tests/test_score_ledger.py -v

score_ledger.py is otherwise verified only by manual `uv run ...` commands in
fixture READMEs — a procedure that never executes verifies nothing (the repo's
own principle). These tests drive `score()` (a pure `(str, str | None) -> Outcome`)
and the calibration fixtures added for #73/#72, asserting the behaviors the
scorer's docstring promises: the row-local C1 audit under vocabulary drift, the
C2 relabel/laundering checks, audit-wide structural bail, and the deliberate
leniency boundary (`startswith`/first-token/parenthesised-estimand) so it cannot
drift silently.

score_ledger is import-safe (compare_prereg.py already imports from it). We load
it by path with importlib (as vega-lite/tests also does) so no sys.path mutation
is needed at all. score_ledger imports only the standard library, so executing it
here has no side effects.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
FIX = HERE / "fixtures"

_spec = importlib.util.spec_from_file_location("score_ledger", HERE / "score_ledger.py")
assert _spec is not None
assert _spec.loader is not None
sl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sl)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def fails(final: str, plan: str | None = None) -> list[str]:
    return sl.score(final, plan).fails


def read_fixture(*parts: str) -> str:
    return (FIX.joinpath(*parts)).read_text(encoding="utf-8")


def summary(rows: str) -> str:
    """Wrap summary-table body rows in a minimal final-ledger `id|claim|status` table."""
    return (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        + rows
        + "\n"
    )


def plan_table(rows: str) -> str:
    """A minimal Plan-time Hypotheses table (id + claim, no status column)."""
    return "## Hypotheses\n\n| id | claim | note |\n| --- | --- | --- |\n" + rows + "\n"


def has(substr: str, msgs: list[str]) -> bool:
    """True if ANY message contains substr (fragments may be in different messages)."""
    return any(substr in m for m in msgs)


def in_one(fragments: list[str], msgs: list[str]) -> bool:
    """True if some SINGLE message contains every fragment.

    Stronger than separate `has` calls: it rules out a pass where the intended
    row, class, and hint are actually spread across unrelated diagnostics.
    """
    return any(all(fr in m for fr in fragments) for m in msgs)


# --------------------------------------------------------------------------- #
# C1 — causal REFUTED, and the row-local #73 regression it must survive
# --------------------------------------------------------------------------- #
def test_c1_flags_a_causal_refuted_row():
    f = fails(summary("| H1 | causal | REFUTED | naive contrast |"))
    assert in_one(["C1: H1", "causal claim marked REFUTED"], f)


def test_c1_passes_a_causal_unresolved_row():
    out = sl.score(summary("| H1 | causal | UNRESOLVED | fine |"), None)
    assert out.fails == []
    assert has("C1 checked and passed", out.checked)


def test_c1_rowlocal_under_claim_drift_fixture():
    # final-mixed.md: genuine H1 causal|REFUTED beside a drifted `associative` H2.
    # The #73 regression: the drift token used to blind C1 on H1 table-wide.
    # C1:H1 and the H2 repair hint are legitimately SEPARATE messages (different
    # rows), so they are asserted separately — but the hint fragments must share
    # the H2 message.
    f = fails(read_fixture("c1-rowlocal", "final-mixed.md"))
    assert has("C1: H1", f)  # the violation must still be reported...
    assert in_one(
        ["H2", "associative", "associative` is conclusion wording"], f
    )  # ...and the drift


def test_c1_rowlocal_under_status_drift_fixture():
    # final-status-drift.md: H2's *status* cell drifted (`Best supported`). Pin the
    # full near-miss hint in one message: the row, the drift token, the `basis`
    # redirect, and the allowed status set.
    f = fails(read_fixture("c1-rowlocal", "final-status-drift.md"))
    assert has("C1: H1", f)
    assert in_one(
        ["H2", '"best supported" is conclusion language', "basis", "REFUTED", "UNRESOLVED"], f
    )


def test_claim_drift_in_unresolved_row_never_exempts_a_sibling_c1():
    # Minimal inline analogue of the #73 fix: a drifted UNRESOLVED sibling is
    # reported but does not suppress C1 on the genuine causal-REFUTED row.
    f = fails(
        summary("| H1 | causal | REFUTED | contrast |\n| H2 | statistical | UNRESOLVED | drift |")
    )
    assert has("C1: H1", f)
    assert in_one(["H2", "unrecognized claim cell", "statistical"], f)


# --------------------------------------------------------------------------- #
# C2 — status laundering: invented id and claim-class relabel
# --------------------------------------------------------------------------- #
def test_c2_relabel_fixture_fails():
    # final-relabel.md: Plan-time `causal` H1 re-dressed as `data-artifact | REFUTED`
    # under the same id — traces to the same id, so only the class-match check closes
    # it. All three fragments must land in ONE message, not scattered.
    f = fails(
        read_fixture("c2-relabel", "final-relabel.md"),
        read_fixture("c2-relabel", "plan.md"),
    )
    assert in_one(["C2: H1", "data-artifact REFUTED", "was causal at Plan time"], f)


def test_c2_clean_fixture_passes():
    # final-clean.md: legitimate descriptive REFUTED, same class and a non-empty
    # Plan-time estimand. (C2 checks the Plan estimand is *present*, not that it
    # equals the final one — see test_c2_does_not_compare_estimand_values.)
    out = sl.score(
        read_fixture("c2-relabel", "final-clean.md"),
        read_fixture("c2-relabel", "plan.md"),
    )
    assert out.fails == []
    assert has("C2 checked and passed", out.checked)


def test_c2_invented_id_is_laundering():
    final = summary("| H9 | descriptive (estimand: rate) | REFUTED | invented |")
    plan = plan_table("| H1 | descriptive (estimand: rate) | x |")
    assert in_one(["C2: H9", "does not appear in the Plan-time ledger"], fails(final, plan))


def test_c2_descriptive_refuted_without_plan_estimand_fails():
    final = summary("| H1 | descriptive (estimand: rate) | REFUTED | ok |")
    plan = plan_table("| H1 | descriptive | x |")  # no estimand at plan time
    assert in_one(["C2: H1", "named no estimand at Plan time"], fails(final, plan))


def test_c2_data_artifact_needs_no_estimand():
    final = summary("| H1 | data-artifact | REFUTED | records miscounted |")
    plan = plan_table("| H1 | data-artifact | x |")
    out = sl.score(final, plan)
    assert out.fails == []
    assert has("C2 checked and passed", out.checked)


def test_c2_matches_ids_after_normalization():
    # A final id written `**H1**` must trace to a Plan id written `h1`: C2's lookup
    # normalizes emphasis/case, so a legitimate row is not flagged as invented.
    final = summary("| **H1** | descriptive (estimand: rate) | REFUTED | ok |")
    plan = plan_table("| h1 | descriptive (estimand: rate) | x |")
    out = sl.score(final, plan)
    assert out.fails == []
    assert has("C2 checked and passed", out.checked)


def test_c2_does_not_compare_estimand_values():
    # Deliberate: C2 requires a non-empty Plan-time estimand, but does NOT compare
    # its text to the final's. A different estimand string still passes — pinned so
    # nobody assumes estimand relabeling is detected here.
    final = summary("| H1 | descriptive (estimand: p95 latency) | REFUTED | ok |")
    plan = plan_table("| H1 | descriptive (estimand: median handle time) | x |")
    assert sl.score(final, plan).fails == []


def test_c2_not_checked_when_plan_omitted():
    out = sl.score(summary("| H1 | descriptive (estimand: rate) | REFUTED | ok |"), None)
    assert out.fails == []
    assert has("C2 NOT CHECKED", out.checked)


def test_c2_nothing_to_check_when_no_refuted_descriptive():
    out = sl.score(
        summary("| H1 | causal | UNRESOLVED | fine |"),
        plan_table("| H1 | causal | x |"),
    )
    assert out.fails == []
    assert has("C2 nothing to check", out.checked)


def test_plan_selects_hypotheses_over_conclusion_summary():
    # A template-shaped Plan carries BOTH an id+claim Hypotheses table and an
    # id+claim+status Conclusion summary. _read_plan excludes the status-bearing
    # table, so the Plan is unambiguous and C2 scores against the Hypotheses row.
    # Drop that exclusion and the two tables collide into a parse failure — this
    # test reddens if the disambiguation is removed.
    plan = (
        plan_table("| H1 | descriptive (estimand: rate) | x |")
        + "\n## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | descriptive (estimand: rate) | UNRESOLVED | prior outcome |\n"
    )
    final = summary("| H1 | descriptive (estimand: rate) | REFUTED | ok |")
    out = sl.score(final, plan)
    assert out.fails == []
    assert has("C2 checked and passed", out.checked)


def test_unparseable_plan_fails_and_never_reports_c2():
    # A --plan that carries no readable table must surface a Plan parse failure and
    # suppress C2 — while C1 on the final still runs (planned=None does not gate it).
    final = summary(
        "| H1 | causal | REFUTED | contrast |\n| H2 | descriptive (estimand: rate) | REFUTED | x |"
    )
    out = sl.score(final, "# prose only, no Plan table\n")
    assert in_one(["plan ledger", "no table found"], out.fails)  # Plan failure propagated...
    assert has("C1: H1", out.fails)  # ...C1 still audited on the final
    # ...and NO C2 verdict is rendered against a plan that could not be parsed.
    # (Without this, a scorer that returned rows-plus-fails instead of None would
    # emit a bogus "C2: ... does not appear in the Plan-time ledger" and pass.)
    assert not has("C2:", out.fails)
    assert out.checked == []  # nothing earned while a failure stands


def test_plan_with_unrecognized_claim_fails_closed():
    # A drifted claim token in the Plan itself is a Plan-side parse failure, not a
    # silent pass: check_claims on the Plan must fail closed.
    final = summary("| H1 | descriptive (estimand: rate) | REFUTED | ok |")
    plan = plan_table("| H1 | associative | x |")
    out = sl.score(final, plan)
    assert in_one(["plan ledger", "H1", "unrecognized claim cell"], out.fails)
    assert not has("C2:", out.fails)  # no C2 verdict against an unparseable plan
    assert out.checked == []


# --------------------------------------------------------------------------- #
# Structural faults bail audit-wide (no row can be trusted)
# --------------------------------------------------------------------------- #
def test_missing_required_table_bails():
    out = sl.score("# just prose, no table with id|claim|status\n", None)
    assert has("no table found", out.fails)
    assert out.checked == []


def test_two_matching_tables_bail():
    two = (
        summary("| H1 | causal | UNRESOLVED | a |")
        + "\n"
        + summary("| H2 | causal | UNRESOLVED | b |")
    )
    assert has("cannot tell which one to score", fails(two))


def test_repeated_id_bails_before_any_policy_check():
    # A repeated id makes id-keyed lookup ambiguous, so no row is policed — even a
    # genuine causal-REFUTED beside it is not reported (audit-wide bail).
    f = fails(
        summary(
            "| H1 | causal | REFUTED | violation |\n"
            "| H1 | descriptive (estimand: r) | UNRESOLVED | dup |"
        )
    )
    assert has("appears on data rows", f)
    assert not has("C1: H1", f)  # bailed before C1 ran


def test_normalized_id_collision_bails_as_repeated_id():
    # `**H1**` and `h1` normalize to the same key: the collision must surface as a
    # repeated-id failure (never a silent last-write-wins merge), and bail audit-wide.
    f = fails(
        summary(
            "| **H1** | causal | REFUTED | violation |\n"
            "| h1 | descriptive (estimand: r) | UNRESOLVED | collides |"
        )
    )
    assert has("appears on data rows", f)
    assert not has("C1: H1", f)


def test_empty_id_bails():
    f = fails(summary("|  | causal | REFUTED | x |"))
    assert has("empty id cell", f)
    assert not has("C1:", f)  # bailed before C1 ran


def test_header_without_data_rows_bails():
    # A table with the required header but zero data rows is fail-closed, not an
    # empty pass: without this guard the scorer would score an empty ledger exit 0
    # ("C1 checked and passed: 0 rows") — a green that could never have failed.
    out = sl.score(summary(""), None)  # header + separator, no data rows
    assert has("header but no data rows", out.fails)
    assert out.checked == []


def test_plan_side_duplicate_id_fails_closed():
    # check_ids runs on the Plan too (via _read_plan): a duplicated Plan id makes
    # its id-keyed C2 lookup ambiguous, so the Plan must fail closed rather than
    # silently pick a row.
    final = summary("| H1 | descriptive (estimand: rate) | REFUTED | ok |")
    plan = plan_table("| H1 | descriptive (estimand: rate) | a |\n| H1 | causal | b |")
    out = sl.score(final, plan)
    assert in_one(["plan ledger", "appears on data rows"], out.fails)
    assert out.checked == []


def test_repeated_header_bails_audit_wide():
    # A repeated column name makes every row ambiguous with no row-local recovery,
    # so this is a STABLE audit-wide bail (unlike the cell-count case, which #81 may
    # narrow): a genuine causal-REFUTED sibling is not policed behind it.
    f = fails(
        "## Conclusion\n\n"
        "| id | claim | status | claim |\n"
        "| --- | --- | --- | --- |\n"
        "| H1 | causal | REFUTED | causal |\n"
    )
    assert has("repeats column name", f)
    assert not has("C1: H1", f)


def test_cell_count_mismatch_is_row_local():
    # #81: an unescaped stray `|` gives the H2 row an extra cell. The malformed row
    # cannot be read, but it must no longer blind C1 on its well-formed sibling —
    # the same row-local recovery #73 gave a drifted claim/status *value*, one
    # indirection deeper. Known positive: a genuine causal|REFUTED H1 beside the
    # cell-count-drifted H2.
    out = sl.score(
        summary(
            "| H1 | causal | REFUTED | violation |\n"
            "| H2 | descriptive | UNRESOLVED | a | b stray pipe |"
        ),
        None,
    )
    assert has("cell(s) but the header", out.fails)  # the malformed row is reported...
    assert has("C1: H1", out.fails)  # ...and its sibling is still audited (#81)
    assert out.checked == []  # still fail-closed: nothing earned behind the parse failure


def test_cell_count_mismatch_does_not_blind_c2_on_sibling():
    # #81 narrows the bail for C2 as well as C1: a malformed row must not hide a
    # status-laundering sibling. H1 is a `data-artifact | REFUTED` relabel of a
    # Plan-time causal H1, beside a cell-count-drifted H2.
    final = summary(
        "| H1 | data-artifact | REFUTED | relabel |\n"
        "| H2 | descriptive | UNRESOLVED | a | b stray pipe |"
    )
    plan = plan_table("| H1 | causal | x |")
    f = fails(final, plan)
    assert has("cell(s) but the header", f)
    assert in_one(["C2: H1", "data-artifact REFUTED", "was causal at Plan time"], f)


def test_cell_count_mismatch_beside_clean_sibling_still_fails_closed():
    # Known negative for the #81 recovery: when the only fault is the unreadable row
    # and every sibling is clean, the run must STILL fail closed (exit 1, nothing
    # earned). Row-local recovery must never turn an unreadable row into a pass.
    out = sl.score(
        summary(
            "| H1 | causal | UNRESOLVED | fine |\n"
            "| H2 | descriptive | UNRESOLVED | a | b stray pipe |"
        ),
        None,
    )
    assert has("cell(s) but the header", out.fails)
    assert out.checked == []


def test_all_rows_malformed_bails_audit_wide():
    # The floor of the #81 recovery: if NO data row is well-formed there is no
    # trustworthy grid to police, so score() bails audit-wide. The Plan carries a
    # genuine `causal`->`data-artifact` relabel of H1 that C2 would flag *if* score
    # had wrongly continued past the empty summary — asserting no C2 verdict leaks
    # pins that it returned early rather than policing a non-existent row grid.
    out = sl.score(
        summary("| H1 | data-artifact | REFUTED | a | b stray pipe |"),
        plan_table("| H1 | causal | ok |"),
    )
    assert has("cell(s) but the header", out.fails)
    assert not has("C2", out.fails)  # bailed before any per-row/C2 check
    assert out.checked == []


def test_read_table_invariant_nonempty_rows_only_carry_row_local_faults():
    # The structural invariant score()'s #81/#91 recovery leans on, pinned directly
    # at read_table so a future parser change cannot silently break it: whenever
    # read_table returns any row, every accompanying fail is a row-local row-parse
    # fault — a cell-count mismatch (#81) or a row that lost an outer pipe (#91) —
    # never a table-wide one. Table-selection faults (no/ambiguous table, repeated
    # header, no data rows, all-malformed body) must instead return NO rows.
    md = summary(
        "| H1 | causal | REFUTED | good |\n| H2 | descriptive | UNRESOLVED | a | b stray |"
    )
    rows, f = sl.read_table(md, "final ledger", "id", "claim", "status")
    assert rows, "a well-formed sibling must be returned"
    assert f
    assert all("cell(s) but the header" in m for m in f)
    # #91: a missing-outer-pipe row is the OTHER permitted row-local fault kind. A
    # well-formed sibling is still returned beside it.
    md_pipe = summary(
        "| H1 | causal | REFUTED | good |\nH2 | descriptive | UNRESOLVED | lost pipe |"
    )
    rows, f = sl.read_table(md_pipe, "final ledger", "id", "claim", "status")
    assert rows, "a well-formed sibling must be returned beside a missing-pipe row"
    assert f
    assert all(("cell(s) but the header" in m) or ("is malformed" in m) for m in f)
    # And the empty-rows branches carry only table-wide faults, never rows:
    for empty_md in (
        "# no table here\n",  # no matching table
        "## Conclusion\n\n| id | claim | status |\n| --- | --- | --- |\n",  # header, no rows
        summary("| H1 | causal | REFUTED | a | b stray |"),  # every row malformed (cell count)
        summary("H1 | causal | REFUTED | lost pipe |"),  # every row malformed (missing pipe)
    ):
        rows, f = sl.read_table(empty_md, "final ledger", "id", "claim", "status")
        assert rows == []
        assert f


def test_plan_side_cell_count_mismatch_stays_audit_wide():
    # #81's row-local recovery is deliberately scoped to the final ledger. This is
    # the true analogue of the #81 case on the Plan side: a WELL-FORMED H1 Plan row
    # sits beside a malformed H2 one, so _read_plan gets good rows alongside the bad
    # one — yet still voids the ENTIRE Plan map (a malformed Plan row could carry a
    # colliding id, making partial recovery unsafe). The final ledger relabels H1
    # `causal`->`data-artifact`, a genuine C2 laundering that must go UNREPORTED
    # because there is no trustworthy Plan map to compare against; the run fails
    # closed on the Plan parse error instead. Pinned so the boundary is a visible
    # choice, not an oversight.
    final = summary("| H1 | data-artifact | REFUTED | relabel |")
    plan = plan_table("| H1 | causal | ok |\n| H2 | descriptive | a | b stray pipe |")
    out = sl.score(final, plan)
    assert has("plan ledger", out.fails)
    assert has("cell(s) but the header", out.fails)
    assert not has("C2", out.fails)  # C2 suppressed: no trustworthy Plan map
    assert out.checked == []


# --------------------------------------------------------------------------- #
# #91 — a row missing an outer pipe must fail closed, not vanish (false green)
#
# parse_tables used to treat a line failing the outer-pipe ROW regex as a table
# TERMINATOR, so a data row missing its leading or trailing `|` disappeared from
# the grid entirely and the run reported "C1 checked and passed" (exit 0) — a
# fail-OPEN false green, the opposite of the suite's discipline. These pin that
# such a row now surfaces as a row-local parse failure the way #81's cell-count
# mismatch does: reported, exit 1, siblings still audited, nothing earned.
# --------------------------------------------------------------------------- #
def test_row_missing_leading_pipe_fails_closed_not_dropped():
    # The issue's exact reproduction: a `causal | REFUTED` row missing its LEADING
    # pipe beside a well-formed descriptive row. It must NOT vanish into a green.
    out = sl.score(
        summary("| H1 | descriptive | UNRESOLVED | fine |\nH2 | causal | REFUTED | violation |"),
        None,
    )
    assert out.checked == []  # the false green is gone
    assert not has("C1 checked and passed", out.checked)
    assert has("H2 | causal | REFUTED | violation", out.fails)  # the row is surfaced


def test_row_missing_trailing_pipe_fails_closed_not_dropped():
    # The missing-TRAILING-pipe variant behaves identically.
    out = sl.score(
        summary("| H1 | descriptive | UNRESOLVED | fine |\n| H2 | causal | REFUTED | violation"),
        None,
    )
    assert out.checked == []
    assert has("REFUTED | violation", out.fails)


def test_missing_outer_pipe_row_is_row_local_sibling_still_audited():
    # Row-local like #81: a malformed (missing-pipe) row must not blind C1 on a
    # well-formed causal-REFUTED sibling. Known positive: genuine C1 violation on
    # H1 beside the malformed H2.
    out = sl.score(
        summary(
            "| H1 | causal | REFUTED | violation |\n"
            "H2 | descriptive | UNRESOLVED | missing leading pipe |"
        ),
        None,
    )
    assert has("C1: H1", out.fails)  # the sibling is still audited
    assert has("missing leading pipe", out.fails)  # the malformed row reported
    assert out.checked == []  # still fail-closed


def test_only_malformed_data_row_bails_audit_wide():
    # Floor case: header + separator + a single malformed data row (no well-formed
    # sibling). There is no trustworthy grid, so the run fails closed rather than
    # reporting an empty green.
    out = sl.score(
        summary("H1 | causal | REFUTED | missing leading pipe |"),
        None,
    )
    assert out.fails
    assert out.checked == []
    assert not has("C1 checked and passed", out.checked)


def test_plain_prose_line_still_terminates_a_table():
    # Guard the boundary the fix must preserve: a line with NO unescaped pipe still
    # ends a table (it is genuine prose, not a malformed row). Two id|claim|status
    # tables separated only by a prose line stay TWO tables — surfacing as the
    # ambiguous-selection bail, proving the prose line was treated as a terminator.
    md = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | a |\n"
        "some prose with no pipe characters at all\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H2 | causal | UNRESOLVED | b |\n"
    )
    assert has("cannot tell which one to score", sl.score(md, None).fails)


def test_ragged_separator_fails_closed():
    # #91 secondary: an all-dash/colon line whose cell count disagrees with the
    # header is no longer silently discarded. Known positive: an otherwise-CLEAN
    # ledger (a lone causal|UNRESOLVED row triggers no C1/C2), so the ONLY thing
    # that can turn it red is catching the ragged separator itself — guarding
    # against a test that passes for an unrelated reason. A ragged separator still
    # matches ROW; only its width is wrong, so it is routed through the existing
    # cell-count diagnostic (not the missing-outer-pipe one), which is asserted
    # exactly rather than merely "some failure".
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n"
        "| --- | --- |\n"  # ragged: 2 cells under a 4-col header
        "| H1 | causal | UNRESOLVED | fine |\n",
        None,
    )
    assert has("cell(s) but the header", out.fails)
    assert out.checked == []


def test_sibling_after_a_malformed_row_is_still_audited():
    # Codex/#91: a row missing an outer pipe must not split the table and drop the
    # rows that FOLLOW it (an earlier candidate design did). Here the malformed row
    # sits BEFORE a genuine causal-REFUTED sibling; the violation after it must
    # still be reported, and the malformed row still fails closed.
    out = sl.score(
        summary(
            "| H1 | descriptive | UNRESOLVED | fine |\n"
            "H2 | descriptive | UNRESOLVED | lost a leading pipe |\n"
            "| H3 | causal | REFUTED | violation after the malformed row |"
        ),
        None,
    )
    assert has("C1: H3", out.fails)  # the row AFTER the malformed one is still audited
    assert has("lost a leading pipe", out.fails)  # and the malformed row is reported
    assert out.checked == []


def test_stray_matching_width_separator_after_data_does_not_drop_the_violation():
    # Codex review of the #91 branch (HIGH): a candidate design split a table at any
    # matching-width separator by treating the row before it as a new header. A STRAY
    # separator sitting after real data rows then popped a genuine data row into an
    # unselectable table and dropped it — recreating the exact false green. The
    # separator must instead be kept as an ordinary row (fails closed on its
    # unrecognized claim/status), and the causal-REFUTED row before it must stay
    # auditable. Known positive: the violation must still be reported.
    out = sl.score(
        summary(
            "| H1 | causal | UNRESOLVED | clean |\n"
            "| H2 | causal | REFUTED | violation |\n"
            "| --- | --- | --- | --- |"  # stray matching-width separator AFTER data
        ),
        None,
    )
    assert has("C1: H2", out.fails)  # the violation is NOT dropped
    assert out.checked == []  # fail closed, nothing earned


def test_pipe_bearing_line_between_two_tables_still_fails_closed():
    # Codex/#91: a pipe-bearing line no longer terminates a table, so two back-to-
    # back id|claim|status tables separated ONLY by such a line merge into one. That
    # is safe, NOT a false green: the second header becomes an unrecognized data row
    # and the run fails closed, while the second table's causal-REFUTED row stays
    # under the first (identical) header and is still audited. Splitting to preserve
    # a prettier "ambiguous" diagnostic was rejected because it could orphan and drop
    # rows (see the stray-separator regression above); never dropping a row wins.
    md = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | a |\n"
        "stray | prose | with | pipes\n"  # pipe-bearing, no outer pipes
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H2 | causal | REFUTED | b |\n"
    )
    out = sl.score(md, None)
    assert has("C1: H2", out.fails)  # the violation in the second table is still caught
    assert out.checked == []  # fail closed, never a silent single-table pass


# --------------------------------------------------------------------------- #
# #97 — a summary row orphaned by a blank line must fail closed, not vanish
#
# A blank line used to hard-terminate a table, so a summary table split by a
# blank line — header + rows, blank line, then a bare data row with no header of
# its own — orphaned that trailing row: it began a headerless "new table" that
# _select_table declined and silently dropped, with NO red anywhere (fail-OPEN,
# the twin of #91/#93 one terminator over). The fix keys on the BOUNDARY PIPE: a
# blank-adjacent line that starts or ends with `|` is a stranded row (a table row,
# or one that lost an outer pipe) and fails closed (an Orphaned row surfaced by
# _rows_from, or a C3a parse fail), regardless of cell-count faults, escaped pipes,
# or stray delimiters around it; prose with only an internal pipe is left alone. NO
# blank-adjacent pipe block is exempted as a "distinct table" — that is a laundering
# channel. Three review rounds drove this: Codex broke a delimiter-presence rule
# (delimiter-after laundering); Fable broke the width-equality rule that replaced it
# (any cell-count fault re-opened the fail-OPEN); Fable again broke the
# different-width exemption (a short row + matching delimiter, and orphan-behind-a-
# shield-grid). The rule that survives is the strictest: fail closed on everything.
# --------------------------------------------------------------------------- #
def test_blank_split_orphan_row_reddens_score():
    # The issue's exact reproduction through score(final, None): H1 clean, then a
    # blank line, then an orphaned H3 row. It must NOT vanish into a green.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n",
        None,
    )
    assert out.checked == []  # the fail-OPEN green is gone
    assert not has("C1 checked and passed", out.checked)
    assert has("median is understated", out.fails)  # the orphaned row is surfaced


def test_blank_split_separator_first_orphan_reddens_score():
    # A delimiter BEFORE the orphan must NOT re-open the hole: a separator is the
    # same width as the table, so it too is a stranded row and fails closed.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| --- | --- | --- | --- |\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n",
        None,
    )
    assert out.checked == []
    assert has("median is understated", out.fails)


def test_blank_split_delimiter_after_orphan_reddens_score():
    # Codex HIGH: a delimiter AFTER the orphan row used to launder it as a new
    # table (row + matching delimiter), which _select_table declined and dropped —
    # the fail-OPEN reopened. Width keys off the row itself, so the same-width H3
    # is stranded no matter what follows it.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
        "| --- | --- | --- | --- |\n",
        None,
    )
    assert out.checked == []
    assert has("median is understated", out.fails)


def test_blank_split_then_missing_pipe_row_reddens_score():
    # Codex HIGH: a blank followed by a row that ALSO lost an outer pipe was
    # dropped (the orphan scan only saw bounded rows). A lost-pipe row of the
    # table's width has a comparable pipe-segment count, so it is now stranded and
    # fails closed — the #91 fault one terminator over.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "H3 | causal | REFUTED | missing leading pipe, a violation |\n",
        None,
    )
    assert out.checked == []
    assert has("missing leading pipe", out.fails)


def test_two_same_width_tables_split_by_blank_fail_closed():
    # Two same-width summary tables separated by ONLY a blank line are ambiguous:
    # structurally, the second is indistinguishable from a chunk of the first
    # stranded by the blank (a laundered orphan looks identical). Since real ledgers
    # never separate tables by a bare blank (they use a heading or prose), the safe
    # reading is to treat the second as stranded and fail closed, never silently
    # drop it. Nothing is earned.
    md = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | a |\n"
        "\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H2 | causal | REFUTED | a violation that must not vanish |\n"
    )
    out = sl.score(md, None)
    assert out.checked == []
    assert has("a violation that must not vanish", out.fails)  # the row is surfaced


def test_blank_split_wrong_width_orphan_reddens_score():
    # Fable review, the blocker: keying the orphan test on EXACT width let a
    # blank-split row with any cell-count fault slip the gate — the row became a
    # headerless table, silently dropped, and a `causal | REFUTED` passed (exit 0).
    # A bounded row that lost or gained a cell after a blank must still fail closed,
    # exactly as it would inside the table (#81).
    for tail in (
        "| H3 | causal | REFUTED | a violation | extra cell |\n",  # too wide
        "| H3 | causal | REFUTED |\n",  # too narrow
        "| H3 | causal \\| REFUTED | a violation |\n",  # escaped pipe collapses width
    ):
        out = sl.score(
            "## Conclusion\n\n"
            "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
            "| H1 | causal | UNRESOLVED | best supported |\n"
            "\n" + tail,
            None,
        )
        assert out.checked == [], f"wrong-width orphan slipped the gate: {tail!r}"
        assert has("REFUTED", out.fails)


def test_blank_split_stray_narrow_line_does_not_shield_the_block():
    # Fable review (EE): the gate tested only the FIRST post-blank line, so a stray
    # 1-cell line laundered every well-formed same-width row behind it. All bounded
    # rows in the block must fail closed, not just the first.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| note |\n"
        "| H3 | causal | REFUTED | a violation that must not be shielded |\n",
        None,
    )
    assert out.checked == []
    assert has("must not be shielded", out.fails)


def test_prose_with_internal_pipe_after_blank_stays_green():
    # Fable review (W): the boundary-pipe tell must not redden genuine prose that
    # merely contains an internal pipe. Such a line starts and ends with words, not
    # `|`, so it is left as prose and the clean ledger passes.
    md = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "Options were A | B | C | D at the time of writing.\n"
    )
    out = sl.score(md, None)
    assert out.checked
    assert not out.fails


def test_blank_separated_pipe_block_of_any_width_fails_closed():
    # Fable re-review, Finding 1: any exemption for a "distinct-looking" table is a
    # laundering channel. A blank-adjacent pipe block of a DIFFERENT width — even a
    # self-contained header + delimiter + row — is no longer trusted; it fails closed
    # like every other blank-adjacent block. (No real ledger separates tables by a
    # bare blank, so nothing legitimate trips this; a heading is the way to do it.)
    md = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| source | note |\n| --- | --- |\n"
        "| S1 | ok |\n"
    )
    out = sl.score(md, None)
    assert out.checked == []
    assert has("orphaned", out.fails)


def test_blank_split_width_short_row_plus_delimiter_reddens_score():
    # Fable re-review Finding 1, the exploit: a C1-violating row written one cell
    # short (width 3) plus a matching 3-wide delimiter used to be exempted as a
    # "distinct table" and dropped — laundering the fail-OPEN one width over. With no
    # exemption, the short row is a stranded orphan and fails closed.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| H3 | causal | REFUTED |\n"
        "| --- | --- | --- |\n",
        None,
    )
    assert out.checked == []
    assert has("REFUTED", out.fails)


def test_blank_split_orphan_behind_a_shield_table_reddens_score():
    # Fable re-review Finding 2: an Orphaned row only surfaces via the grid it lands
    # in, so an intervening (unselected) table used to shield a stranded violating
    # row from score()'s grid path. With no exemption the shield's rows and the
    # violating row are all swept into the ledger's orphan block, so it fails closed.
    out = sl.score(
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| note | ref |\n| --- | --- |\n| n1 | r1 |\n"
        "\n"
        "| H3 | causal | REFUTED | hidden behind the shield |\n",
        None,
    )
    assert out.checked == []
    assert has("hidden behind the shield", out.fails)


def test_orphan_block_then_pipe_table_all_fail_closed():
    # With no distinct-table exemption, an orphan block and any pipe block glued to
    # it by only a blank (or nothing) are all swept into the split-from table as
    # Orphaned rows — one grid, fully fail-closed. Merging is safe here: every row is
    # reported, nothing is silently dropped.
    md = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | a |\n"
        "\n"
        "| H3 | data-artifact | UNRESOLVED | stranded |\n"
        "| a | b |\n| --- | --- |\n| x | y |\n"
    )
    out = sl.score(md, None)
    assert out.checked == []
    assert has("orphaned", out.fails)
    assert any(isinstance(r, sl.Orphaned) for t in sl.parse_tables(md) for r in t)


# --------------------------------------------------------------------------- #
# Deliberate leniency boundary — pin startswith / first-token / estimand syntax
# --------------------------------------------------------------------------- #
def test_claim_of_startswith_leniency():
    assert sl.claim_of("causal (via timing)") == "causal"
    assert sl.claim_of("**Descriptive**") == "descriptive"
    assert sl.claim_of("data-artifact: miscount") == "data-artifact"
    # Raw `startswith`, not delimiter-aware: a prefix continuation still matches.
    # Pinned so this leniency is a visible choice, not an accident to "fix".
    assert sl.claim_of("causality") == "causal"


def test_claim_of_rejects_unknown_and_drift_tokens():
    for cell in ("associative", "statistical", "correlational", "", "   "):
        assert sl.claim_of(cell) is None


def test_status_of_returns_first_token_only():
    assert sl.status_of("UNRESOLVED, was REFUTED before amendment") == "UNRESOLVED"
    assert (
        sl.status_of("REFUTED, later moved to UNRESOLVED") == "REFUTED"
    )  # first token, either order
    assert sl.status_of("**REFUTED**") == "REFUTED"
    assert sl.status_of("Best supported") is None
    # Whole-word, not substring: a token embedded in a longer word does not match.
    assert sl.status_of("UNRESOLVEDLY") is None
    assert sl.status_of("REFUTEDNESS") is None


def test_estimand_of_requires_the_parenthesised_syntax():
    assert sl.estimand_of("descriptive (estimand: marginal median)") == "marginal median"
    assert sl.estimand_of("**descriptive (estimand: rate)**") == "rate"  # emphasis tolerated
    assert (
        sl.estimand_of("descriptive (estimand: N/A)") == "N/A"
    )  # presence, not quality (docstring)
    assert sl.estimand_of("descriptive (estimand: rate) as recorded") == "rate"  # trailing prose ok
    assert sl.estimand_of("descriptive") is None
    assert sl.estimand_of("descriptive (estimand: )") is None  # empty content
    assert sl.estimand_of("descriptive - no estimand named") is None  # word, not the syntax
    # Content that is only Unicode Cf format chars (here a zero-width space, written
    # as an explicit escape so it is visible in source) is stripped to empty and
    # reads as no estimand — pins the deliberate Cf handling.
    assert sl.estimand_of("descriptive (estimand: \u200b)") is None


def test_escaped_pipe_is_a_literal_not_a_column_break():
    tables = sl.parse_tables(
        "| id | claim | status | basis |\n"
        "| --- | --- | --- | --- |\n"
        r"| H1 | descriptive | UNRESOLVED | a \| b |" + "\n"
    )
    assert len(tables) == 1
    body = tables[0][1]  # first data row (separator row is dropped)
    # The escaped pipe stays inside its cell — the row keeps its 4 columns
    # instead of fragmenting, and the cell holds a literal `|`.
    assert body == ["H1", "descriptive", "UNRESOLVED", "a | b"]


def test_normalize_key_folds_emphasis_and_case():
    assert sl.normalize_key("**H1**") == sl.normalize_key("h1") == "h1"


# --------------------------------------------------------------------------- #
# CLI contract — main() maps a violation to exit 1, a clean ledger to exit 0,
# and the exit code tracks the POLICY output (not just a generic FAIL/OK banner)
# --------------------------------------------------------------------------- #
def test_main_exit_1_on_c2_relabel(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "score_ledger.py",
            "--final",
            str(FIX / "c2-relabel" / "final-relabel.md"),
            "--plan",
            str(FIX / "c2-relabel" / "plan.md"),
        ],
    )
    assert sl.main() == 1
    out = capsys.readouterr().out
    assert "FAIL:" in out
    assert "C2: H1" in out
    assert "was causal at Plan time" in out


def test_main_exit_0_on_clean_ledger(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "score_ledger.py",
            "--final",
            str(FIX / "c2-relabel" / "final-clean.md"),
            "--plan",
            str(FIX / "c2-relabel" / "plan.md"),
        ],
    )
    assert sl.main() == 0
    out = capsys.readouterr().out
    assert "OK:" in out
    assert "C2 checked and passed" in out


# --------------------------------------------------------------------------- #
# C3 — section and completeness-bullet extraction (Task 1)
# --------------------------------------------------------------------------- #
def test_section_body_extracts_named_section():
    md = "# Title\n\n## Data Validity\n\n- a\n- b\n\n## Conclusion\n\n- answer\n- limits\n"
    assert sl.section_body(md, "Conclusion") == "\n- answer\n- limits\n"
    assert "answer" in sl.section_body(md, "conclusion")  # case/emphasis folded


def test_section_body_stops_at_next_heading_of_same_or_higher_level():
    md = "## Conclusion\n\n- answer\n\n### Sub\n\n- deep\n\n## After\n\n- x\n"
    body = sl.section_body(md, "Conclusion")
    assert "answer" in body  # own content stays inside
    assert "deep" in body  # deeper heading stays inside
    assert "x" not in body  # the sibling `## After` ends it


def test_section_body_absent_is_none():
    assert sl.section_body("# Title\n\n## Sources\n\n- s\n", "Conclusion") is None


def test_completeness_bullet_extracts_content_without_label():
    md = (
        "## Data Validity\n\n- Coverage matrix: rows\n"
        "- Source completeness semantics: S2: UNKNOWN — no contract\n"
        "- Sensitivity checks performed: none\n"
    )
    assert sl.completeness_bullet(md) == "S2: UNKNOWN — no contract"


def test_completeness_bullet_absent_is_none():
    assert sl.completeness_bullet("## Data Validity\n\n- Coverage matrix: rows\n") is None


# --------------------------------------------------------------------------- #
# C3b — canonical UNKNOWN atom (Task 2)
# --------------------------------------------------------------------------- #
def dv(bullet: str) -> str:
    """A minimal ledger carrying one Source completeness semantics bullet."""
    return f"## Data Validity\n\n- Source completeness semantics: {bullet}\n"


def test_c3b_passes_canonical_unknown_atom():
    assert sl.check_c3b(dv("S2: UNKNOWN — no completeness contract in these files"), "S2") == []


def test_c3b_passes_emdash_separator_and_emphasis():
    assert sl.check_c3b(dv("**S2** — `UNKNOWN` — no independent denominator"), "S2") == []


def test_c3b_fails_lowercase_unknown_casesensitive():
    # arm b's near-miss: lowercase "unknown" must not pass.
    f = sl.check_c3b(dv("S2: unknown-direction problem, treat as right-censored"), "S2")
    assert any("C3b" in m and "S2" in m for m in f)


def test_c3b_fails_prose_reading_no_atom():
    # arm-e-class prose: names S2 but never in the documented declaration form.
    f = sl.check_c3b(
        dv('for S2, an absent incident_id is read as "not yet closed" — right-censored'), "S2"
    )
    assert any(("C3b" in m) or ("no" in m and "S2" in m) for m in f)


def test_c3b_fails_definite_reading_value():
    f = sl.check_c3b(dv("S2: still-open — the missing rows are unresolved incidents"), "S2")
    assert any("S2" in m for m in f)


def test_c3b_fails_no_completeness_bullet():
    f = sl.check_c3b("## Data Validity\n\n- Coverage matrix: rows\n", "S2")
    assert any("completeness" in m.lower() for m in f)


def test_c3b_fails_source_not_declared():
    f = sl.check_c3b(dv("S3: UNKNOWN — sampled by design"), "S2")
    assert any("S2" in m for m in f)


def test_c3b_fails_conflicting_declarations():
    f = sl.check_c3b(dv("S2: UNKNOWN — no contract; S2: still-open — but really open"), "S2")
    assert any("conflict" in m.lower() or "S2" in m for m in f)


def test_c3b_completeness_bullet_must_be_in_data_validity():
    # a canonical-looking bullet outside Data Validity must fail closed
    md = "## Notes\n\n- Source completeness semantics: S2: UNKNOWN — reason\n"
    assert sl.check_c3b(md, "S2") != []


def test_c3b_reason_clause_smuggling_a_direction_fails_closed():
    # I1: an UNKNOWN atom whose reason text itself asserts an unconditional
    # missingness direction takes back in prose what the atom concedes.
    f = sl.check_c3b(
        dv(
            "S2: UNKNOWN — formally; in practice every absent row is a "
            "still-open incident and the closed-only median understates true "
            "time-to-close"
        ),
        "S2",
    )
    assert any("C3b" in m and "S2" in m for m in f)


def test_c3b_duplicate_data_validity_sections_fail_closed():
    # I2: two `## Data Validity` sections leave no way to tell which declares
    # the source's completeness reading, even when the second is a definite
    # (non-UNKNOWN) reading that would otherwise fail on its own merits too.
    md = (
        "## Data Validity\n\n- Source completeness semantics: S2: UNKNOWN — one\n\n"
        "## Data Validity\n\n- Source completeness semantics: S2: still-open — two\n"
    )
    f = sl.check_c3b(md, "S2")
    assert f != []
    assert any("Data Validity" in m for m in f)


# --------------------------------------------------------------------------- #
# C3a — missingness-direction assertions in the Conclusion (Task 3)
# --------------------------------------------------------------------------- #
def concl(body: str) -> str:
    return "## Conclusion\n\n" + body + "\n"


# --- known positives: the six measured constructions must each fire ---
@pytest.mark.parametrize(
    "unit",
    [
        "The 11 incidents are still open; this understates how bad assist is.",
        "Excluding the still-open cases can only push assist further behind manual.",
        "The missing sev1 cases give a lower bound on eventual time-to-close; direction is known.",
        "The gap is likely understated because the hardest incidents are censored "
        "out of the sample.",
        "The still-open incidents mean the true picture is at least as bad as shown, likely worse.",
        "Right-censoring inflates the assist improvement; the true value is bounded "
        "below by their current elapsed time.",
    ],
)
def test_c3a_fires_on_each_measured_construction(unit):
    f = sl.check_c3a(concl("- " + unit))
    assert any("C3a" in m for m in f), f"expected C3a to fire on: {unit!r}"


# --- known negatives: correct work must NOT fire ---
@pytest.mark.parametrize(
    "unit",
    [
        # licensed conditional sensitivity — decline suppressor rescues it
        "If S2 absence means still-open, the closed-only estimate understates time; "
        "if closed-but-unrecorded, direction is unidentified; overall direction is UNKNOWN.",
        # legitimate confound-direction claim: direction but no missingness anchor
        "The severity-mix confound biases the naive estimate high.",
        # observed composition fact: anchor but skew has no outcome target
        "The missing rows skew toward sev1.",
        # opposing pair present
        "The missing cases could understate or overstate the true assist median.",
        # anchor but no direction predicate
        "The 11 incidents have no recorded closure at the extract.",
        # 'if anything' idiom must NOT be conditional; here no anchor -> still no fire
        "If anything, the confound points to a larger severity effect.",
    ],
)
def test_c3a_does_not_fire_on_correct_work(unit):
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3a_anaphora_inherits_prior_anchor():
    # direction unit led by an anaphor inherits the previous unit's missingness anchor
    body = (
        "- The 11 sev1 incidents are still open at extract.\n- These understate how bad assist is."
    )
    assert any("C3a" in m for m in sl.check_c3a(concl(body)))


def test_c3a_if_anything_idiom_not_suppressed():
    # 'if anything ... likely understated ... censored out' (arm e's real ledger sentence)
    unit = (
        "If anything the direction points toward more cost, with the true gap "
        "likely understated because the hardest incidents are censored out of the sample."
    )
    assert any("C3a" in m for m in sl.check_c3a(concl("- " + unit)))


def test_c3a_ignores_summary_status_cells():
    # an UNRESOLVED status cell is not a missingness anchor; a clean basis cell does not fire
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported, no direction claimed |\n"
    )
    assert sl.check_c3a(concl(body)) == []


def test_c3a_scans_basis_cell_text():
    # the well-formed control for the two #93 tests below: a violating basis cell
    # fires C3a when no malformed row precedes it.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
    )
    assert any("C3a" in m for m in sl.check_c3a(concl(body)))


def test_c3a_malformed_row_does_not_blind_following_basis_cell():
    # #93: a neutral summary row that lost an outer pipe sits inside the summary
    # table, followed by a well-formed basis cell asserting an unconditional
    # missingness direction. The inline parser must NOT reset the table/basis
    # state on the malformed row (as parse_tables no longer does for C1/C2, #91),
    # or the following basis cell is orphaned into a basis-less "new table" and
    # its violation is silently missed -- the fail-open twin of #91.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "H2 | data-artifact | UNRESOLVED | neutral summary, no direction claimed |\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
    )
    f = sl.check_c3a(concl(body))
    # Require the H3 basis-cell violation as a DISTINCT C3a policy message: a bare
    # `any("C3a" in m ...)` would also be satisfied by the malformed-row parse
    # message (which contains "C3a:"), so it could not tell the fix from the very
    # fail-open it guards -- a broken instrument.
    assert any(m.startswith("C3a:") and "median is understated" in m for m in f)


def test_c3a_malformed_row_breaks_anaphora_inheritance():
    # #93 review: an unreadable malformed row must break the anchor-inheritance
    # chain exactly as the well-formed neutral row it stands in for would. An
    # anchor before it must NOT license a following anaphoric direction claim, or
    # the malformed row manufactures a false C3a positive.
    hdr = "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
    anchor = "| H1 | data-artifact | UNRESOLVED | no recorded closure |\n"
    anaphor = "| H3 | data-artifact | UNRESOLVED | These understate the median |\n"
    neutral_ok = "| H2 | data-artifact | UNRESOLVED | neutral summary, no direction |\n"
    neutral_malformed = "H2 | data-artifact | UNRESOLVED | neutral summary, no direction |\n"
    # positive control: with NO row between them the anaphor inherits H1's anchor
    # and fires -- so the two negative assertions below cannot pass vacuously.
    assert any(m.startswith("C3a:") for m in sl.check_c3a(concl(hdr + anchor + anaphor)))
    # control: the well-formed neutral row breaks inheritance -> H3 does not fire
    control = sl.check_c3a(concl(hdr + anchor + neutral_ok + anaphor))
    assert not any(m.startswith("C3a:") for m in control)
    # the malformed row must behave the same -- no manufactured C3a violation
    malformed = sl.check_c3a(concl(hdr + anchor + neutral_malformed + anaphor))
    assert not any(m.startswith("C3a:") for m in malformed)


def test_c3a_surfaces_malformed_conclusion_row():
    # #93: the malformed Conclusion row itself fails closed as a row-local parse
    # error (reported, run reddens), never silently absorbed as prose.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "H2 | data-artifact | UNRESOLVED | neutral summary, no direction claimed |\n"
    )
    f = sl.check_c3a(concl(body))
    assert any(m.startswith("parse:") and "malformed" in m for m in f)


def test_c3a_blank_split_orphan_basis_fails_closed():
    # #97, the C3a twin of #93: a summary table split by a blank line orphans the
    # trailing row, whose basis cell asserts an unconditional missingness direction.
    # The inline parser used to reset table/basis state across the blank and drop
    # the basis cell silently (check_c3a -> []). It must now fail closed on the
    # orphaned row as a row-local parse error. The control (no blank line) firing
    # C3a on the same basis cell is test_c3a_scans_basis_cell_text above.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
    )
    f = sl.check_c3a(concl(body))
    assert f != []  # not the fail-OPEN silent []
    assert any(m.startswith("parse:") and "orphan" in m for m in f)


def test_c3a_separator_first_orphan_fails_closed():
    # A delimiter BEFORE the orphan row must not re-open the hole -- a same-width
    # separator is itself a stranded row.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| --- | --- | --- | --- |\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
    )
    f = sl.check_c3a(concl(body))
    assert any(m.startswith("parse:") and "orphan" in m for m in f)


def test_c3a_delimiter_after_orphan_fails_closed():
    # Codex HIGH at the C3a site: a delimiter AFTER the orphan row must not launder
    # it. The violating basis cell must not vanish; the run fails closed.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
        "| --- | --- | --- | --- |\n"
    )
    f = sl.check_c3a(concl(body))
    assert any(m.startswith("parse:") and "orphan" in m for m in f)


def test_c3a_blank_then_missing_pipe_orphan_fails_closed():
    # Codex HIGH at the C3a site: a blank followed by a row that also lost an outer
    # pipe used to be dropped; a same-width lost-pipe row now fails closed.
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | UNRESOLVED | best supported |\n"
        "\n"
        "H3 | data-artifact | UNRESOLVED | the still-open cases understate the median |\n"
    )
    f = sl.check_c3a(concl(body))
    assert any(m.startswith("parse:") for m in f)  # reddens, not a silent []


def test_c3a_fails_closed_without_conclusion():
    f = sl.check_c3a("## Sources\n\n| id | x |\n| --- | --- |\n| S1 | y |\n")
    assert any("Conclusion" in m for m in f)


def test_c3a_fails_closed_on_empty_conclusion():
    # I3: a `## Conclusion` heading with no scannable prose or basis cells must
    # be a parse failure, not a vacuous pass -- mirrors the "header but no data
    # rows" philosophy elsewhere in the scorer.
    f = sl.check_c3a("## Conclusion\n\n\n")
    assert any(m.startswith("parse:") and "Conclusion" in m for m in f)


def test_c3a_fails_closed_on_duplicate_conclusion():
    # I3: two `## Conclusion` sections leave no way to tell which to score.
    md = "## Conclusion\n\n- ok\n\n## Conclusion\n\n- ok2\n"
    f = sl.check_c3a(md)
    assert any(m.startswith("parse:") and "Conclusion" in m for m in f)


def test_c3a_reports_suppressed_count():
    body = "- The missing cases could understate or overstate the assist median."
    violations, suppressed = sl.c3a_report(concl(body))
    assert violations == []
    assert suppressed >= 1


def test_c3a_anaphora_does_not_leak_across_unrelated_unit():
    # adjacent-only inheritance: an anchor two units back must NOT be inherited
    body = (
        "- The 11 sev1 incidents are still open at extract.\n"
        "- Assist handled 40% of incidents this quarter.\n"
        "- This overstates how good assist looks."
    )
    assert sl.check_c3a(concl(body)) == []


def test_c3a_no_recorded_closure_is_an_anchor():
    # the exact phrase the tool's remediation message recommends must be an anchor
    unit = (
        "These incidents have no recorded closure, so the median understates assist's true speed."
    )
    assert any("C3a" in m for m in sl.check_c3a(concl("- " + unit)))


def test_c3a_under_the_assumption_is_a_conditional_decline():
    unit = (
        "Under the assumption that missing rows are still open, the closed-only "
        "estimate understates time-to-close."
    )
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3a_skew_of_a_composition_rate_is_not_an_outcome_direction():
    assert sl.check_c3a(concl("- The missing rows skew the observed sev1 rate upward.")) == []


def test_c3a_confound_bias_of_an_estimate_still_needs_no_missingness_anchor():
    # guard the fix-2 narrowing did not break a real bias-of-estimate case pairing
    assert sl.check_c3a(concl("- The confound biases the estimate high.")) == []


def test_c3a_hyphenated_censored_out_is_an_anchor():
    assert any(
        "C3a" in m for m in sl.check_c3a(concl("- The censored-out cases understate the median."))
    )


def test_c3a_soft_wrapped_sentence_is_one_unit():
    body = "- The missing rows systematically\n  understate the median."
    assert any("C3a" in m for m in sl.check_c3a(concl(body)))


def test_c3a_unknown_does_not_suppress_a_contradictory_direction():
    unit = "Completeness is unknown, but the missing rows understate the median."
    assert any("C3a" in m for m in sl.check_c3a(concl("- " + unit)))


# --------------------------------------------------------------------------- #
# C3a hardening (#77 critical review) — negation, composition, treating-as,
# `, and`, and leading-concessive cases (battery 7/10/13/15/16)
# --------------------------------------------------------------------------- #
def test_c3a_negation_does_not_fire_the_cardinal_fp():
    # The cardinal false positive the review found: a sentence that NEGATES the
    # direction claim must not fire just because the direction/anchor vocabulary
    # is present.
    unit = "We cannot conclude that the missing rows understate the median."
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3a_composition_shift_does_not_fire():
    # "shifts" describes an observed composition change, not a claim about which
    # way an estimate is wrong -- no outcome target co-occurs with `shifts`.
    unit = (
        "Dropping the 11 cases with no recorded closure shifts the closed-only "
        "sample toward lower-severity incidents."
    )
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3a_treating_as_sensitivity_does_not_fire():
    # A worst-case sensitivity check that explicitly conditions on "treating X as
    # Y" is a licensed conditional, not an unconditional direction claim.
    unit = (
        "A worst-case sensitivity check: treating the 11 as still-open yields a "
        "lower bound of 41 minutes on the assist median."
    )
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3a_and_joined_pair_splits_into_separate_units():
    # A `, and`-joined pair must not let the direction half of the sentence
    # borrow the missingness half's anchor (or vice versa) as if they were one
    # claim unit.
    unit = (
        "The severity-mix confound biases the naive estimate high, and the "
        "missing rows are concentrated in the assist week."
    )
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3a_leading_concessive_still_fires_the_main_clause():
    # A subordinate "While X is unknown," concessive must not suppress the main
    # clause's own unconditional direction claim (I5).
    unit = "While the direction is formally unknown, the missing rows understate the median."
    assert any("C3a" in m for m in sl.check_c3a(concl("- " + unit)))


# --------------------------------------------------------------------------- #
# C3 — integration into score()/main() and reporting (Task 4)
# --------------------------------------------------------------------------- #
COMPLIANT_C3 = (
    "## Data Validity\n\n"
    "- Source completeness semantics: S2: UNKNOWN — no independent denominator "
    "discriminates the live readings\n\n"
    "## Conclusion\n\n"
    "- Answer: no recorded closure for 11 incidents; the missingness direction is "
    "unknown, so no responder-hours figure is credibly attributable.\n\n"
    "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
    "| H1 | causal | UNRESOLVED | unidentified pre/post contrast |\n"
)
VIOLATING_C3 = (
    "## Data Validity\n\n"
    '- Source completeness semantics: for S2, an absent row is read as "still open" '
    "— right-censored\n\n"
    "## Conclusion\n\n"
    "- Limitations: the true gap is likely understated because the hardest "
    "incidents are censored out of the sample.\n\n"
    "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
    "| H1 | causal | UNRESOLVED | unidentified pre/post contrast |\n"
)


def test_c3_not_run_without_flag():
    out = sl.score(VIOLATING_C3, None, c3_source=None)
    assert out.fails == []
    assert has("C3 NOT CHECKED", out.checked)


def test_c3_compliant_ledger_passes_both_subchecks():
    out = sl.score(COMPLIANT_C3, None, c3_source="S2")
    assert out.fails == []
    assert has("C3a checked and passed", out.checked)
    assert has("C3b checked and passed", out.checked)


def test_c3_violating_ledger_fails_both_subchecks():
    out = sl.score(VIOLATING_C3, None, c3_source="S2")
    assert has("C3a:", out.fails)  # ledger direction claim
    assert has("C3b:", out.fails)  # non-canonical S2 entry


def test_c3_note_prints_on_stderr_even_when_another_check_fails(monkeypatch, capsys, tmp_path):
    # A C1 violation must not suppress the C3-not-checked stderr note (it prints
    # before scoring, so a later FAIL cannot mask that C3 never ran).
    p = tmp_path / "final.md"
    p.write_text(
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H1 | causal | REFUTED | naive contrast |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["score_ledger.py", "--final", str(p)])
    assert sl.main() == 1  # C1 violation -> exit 1
    captured = capsys.readouterr()
    assert "C1: H1" in captured.out  # the failing check reported...
    assert "c3-unknown-source" in captured.err  # ...and the C3-not-checked note still printed


def test_main_c3_flag_exit_1_on_violation(monkeypatch, capsys, tmp_path):
    p = tmp_path / "final.md"
    p.write_text(VIOLATING_C3, encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv", ["score_ledger.py", "--final", str(p), "--c3-unknown-source", "S2"]
    )
    assert sl.main() == 1
    out = capsys.readouterr().out
    assert "C3a:" in out
    assert "C3b:" in out


def test_main_c3_note_on_stderr_when_flag_absent(monkeypatch, capsys, tmp_path):
    p = tmp_path / "final.md"
    p.write_text(COMPLIANT_C3, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["score_ledger.py", "--final", str(p)])
    sl.main()
    err = capsys.readouterr().err
    assert "c3-unknown-source" in err


# --------------------------------------------------------------------------- #
# C3 — the documented template form is what C3b/C3a expect (Task 5)
# --------------------------------------------------------------------------- #
TEMPLATE = (Path(sl.__file__).parent.parent / "references" / "ledger-template.md").read_text(
    encoding="utf-8"
)


def test_template_documents_the_unknown_atom():
    # Guard the doc edit specifically: S1 parses as a canonical UNKNOWN
    # declaration only after the grouped "S1, S5 — UNKNOWN" line was rewritten to
    # the documented "S1: UNKNOWN" atom (the comma form does not parse). This is
    # red on the pre-edit template, unlike a bare C3B_DECL.search(TEMPLATE) which
    # matches unrelated text elsewhere in the file.
    s1_declared = any(
        sl.normalize_key(m.group("sid")) == "s1"
        and sl.EMPHASIS.sub("", m.group("val")).strip() == "UNKNOWN"
        for m in sl.C3B_DECL.finditer(TEMPLATE)
    )
    assert s1_declared, "template must declare `S1: UNKNOWN` in the documented atom form"
    # and check_c3b accepts that documented form
    md = (
        "## Data Validity\n\n"
        "- Source completeness semantics: S1: UNKNOWN — no completeness contract checked\n"
    )
    assert sl.check_c3b(md, "S1") == []


def test_template_documents_the_adequacy_atom():
    # Guard BOTH halves of the doc edit, discriminatingly. Asserting on the
    # whole TEMPLATE is too weak: the Tests-section prose's own `adequacy: <rate>
    # ± ... (variants: <range>)` format string parses as an atom (EMPHASIS
    # strips its backticks), so a whole-file assert would stay green even if
    # the worked-example illustration were dropped. Anchor the illustration
    # check to the T4 row, which is what a regression would silently remove.
    t4 = next(line for line in TEMPLATE.splitlines() if line.lstrip().startswith("| T4 "))
    assert sl._adequacy_atoms(t4), "worked-example T4 row must illustrate the adequacy atom"
    # and the Tests-section prose must document the atom's machine-checkable form. Anchored
    # to the prose LINE, not the whole file: a whole-TEMPLATE containment assert is vacuous
    # because the T4 row above already satisfies it, so deleting the documentation sentence
    # would leave it green -- the same trap this test's first half avoids.
    prose = next(
        (ln for ln in TEMPLATE.splitlines() if ln.lstrip().startswith("A `CONTRADICTED` outcome")),
        None,
    )
    assert prose is not None, "Tests-section prose must document the adequacy atom"
    assert "adequacy:" in prose
    assert "(variants:" in prose


def test_worked_example_conclusion_is_a_c3a_negative():
    # Extract the worked example's own Conclusion (the SECOND `## Conclusion` in the
    # file, inside the "## Worked Example" block), not the Full Route Template's
    # placeholder Conclusion (which sl.section_body would return first, and which
    # is not prose at all -- `- Answer: <answer first>` -- proving nothing).
    split_count = 2
    worked = TEMPLATE.split("## Worked Example", 1)
    assert len(worked) == split_count, "template must contain a Worked Example section"
    body = sl.section_body(worked[1], "Conclusion")
    assert body is not None, "must scan the worked-example Conclusion"
    assert "roll back" in body, "must scan the worked-example Conclusion"
    assert sl.check_c3a("## Conclusion\n" + body + "\n") == []


# --------------------------------------------------------------------------- #
# C3 — end-to-end on the archived arm-e ledger and reconstructed entries (Task 6)
# --------------------------------------------------------------------------- #
def test_c3_fails_archived_arm_e_final():
    # arm-e-final.md is a real s15 ledger: Conclusion Limitations carries
    # "likely understated ... censored out of the sample" (C3a) and its S2
    # completeness entry is prose, not the canonical atom (C3b).
    arm_e = read_fixture("s15-prereg-drift", "arm-e-final.md")
    out = sl.score(arm_e, None, c3_source="S2")
    assert has("C3a:", out.fails) or has("C3b:", out.fails)
    # both, in fact:
    assert has("C3a:", out.fails)
    assert has("C3b:", out.fails)


def test_c3_reconstructed_entries_fail_c3b():
    # the six measured completeness entries, reconstructed verbatim, each fail C3b
    for name in (
        "entry-a.md",
        "entry-b.md",
        "entry-c.md",
        "entry-d.md",
        "entry-e.md",
        "entry-f.md",
    ):
        md = read_fixture("c3-completeness", name)
        f = sl.check_c3b(md, "S2")
        assert f, f"{name} should fail C3b"


# --------------------------------------------------------------------------- #
# C3 — second critical-review pass: over-correction regressions and residual FP
# --------------------------------------------------------------------------- #
def test_c3a_coverage_negation_does_not_suppress_the_assertion():
    # "does not include ..." is a coverage negation, not a decline of the direction;
    # the narrowed negation regex must let the assertion fire.
    unit = (
        "The closed-only median does not include the 11 still-open incidents, "
        "so it understates the true time-to-close."
    )
    assert any("C3a" in m for m in sl.check_c3a(concl("- " + unit)))


def test_c3a_cannot_ignore_is_not_a_decline():
    unit = "We cannot ignore that the missing rows understate the median."
    assert any("C3a" in m for m in sl.check_c3a(concl("- " + unit)))


def test_c3a_still_suppresses_a_genuine_decline():
    # the narrowing must NOT reopen the cardinal false positive: a real refusal stays silent
    assert (
        sl.check_c3a(concl("- We cannot conclude that the missing rows understate the median."))
        == []
    )
    assert (
        sl.check_c3a(
            concl("- The evidence does not show that the missing rows understate the median.")
        )
        == []
    )


def test_c3a_plural_outcome_target_fires():
    assert any(
        "C3a" in m for m in sl.check_c3a(concl("- The missing rows bias the estimates downward."))
    )
    assert any(
        "C3a" in m
        for m in sl.check_c3a(
            concl("- Excluding the still-open cases skews the results in assist's favor.")
        )
    )


def test_c3a_bare_attribution_noun_does_not_suppress_an_assertion():
    # "stakeholders should note that X" / "the timing evidence argues that X" assert X;
    # only clear attribution structure (claims/asserts/the memo) suppresses.
    assert any(
        "C3a" in m
        for m in sl.check_c3a(
            concl("- Stakeholders should note that the still-open cases understate the median.")
        )
    )
    # but an attributed-and-rebutted claim still does not fire
    assert (
        sl.check_c3a(
            concl(
                "- The stakeholder memo claims the missing rows understate the median; "
                "these files cannot license that claim."
            )
        )
        == []
    )


def test_c3a_under_named_scenario_is_a_conditional_decline():
    # "under the <adjective> scenario ... understates" is a licensed two-branch sensitivity
    unit = (
        "Under the still-open scenario the median understates time-to-close; "
        "under the closed-unlogged scenario it does not."
    )
    assert sl.check_c3a(concl("- " + unit)) == []


def test_c3b_reason_smuggling_without_a_sentence_boundary_fails_closed():
    # the smuggle must fail even without a `;`/`.` separating the atom from the claim:
    # the `S2: UNKNOWN` atom is stripped before scanning so its own token can't suppress.
    md = (
        "## Data Validity\n\n- Source completeness semantics: S2: UNKNOWN — the absent "
        "rows are still-open incidents so the closed-only median understates true time-to-close\n"
    )
    assert sl.check_c3b(md, "S2") != []


# --------------------------------------------------------------------------- #
# C4 — the positive-contradiction adequacy atom (Task 1)
# --------------------------------------------------------------------------- #
def test_adequacy_of_parses_documented_atom():
    assert sl.adequacy_of("adequacy: 34% (variants: τ ≥ 2h)") == ("34%", "τ ≥ 2h")


def test_adequacy_of_reads_atom_embedded_in_a_larger_cell():
    # the earlier `(S4 §2)` paren must not confuse the match, and the leading `<`
    # of the bound must survive the trim (ADEQUACY_TRIM, unlike ESTIMAND_TRIM, does
    # not strip `<`/`>` — the `<` is load-bearing and distinguishes conflicting bounds)
    cell = (
        "CONTRADICTED; added latency spread across spans (S4 §2). "
        "adequacy: <1 in 20 ± 1pp (variants: any split with payment > 50%)"
    )
    assert sl.adequacy_of(cell) == ("<1 in 20 ± 1pp", "any split with payment > 50%")


def test_adequacy_of_keeps_angle_brackets_distinct_in_bound():
    # `<34%` and `34%` are different bounds; the trim must not collapse them
    assert sl.adequacy_of("adequacy: <34% (variants: x)") == ("<34%", "x")


def test_adequacy_of_reads_through_emphasis():
    assert sl.adequacy_of("**adequacy: 5% (variants: fast-and-slow leak)**") == (
        "5%",
        "fast-and-slow leak",
    )


def test_adequacy_of_na_passes_syntactically():
    # syntactic presence only, like `estimand: N/A`; quality is the rubric's
    assert sl.adequacy_of("adequacy: N/A (variants: none)") == ("N/A", "none")


def test_adequacy_of_none_when_no_atom():
    assert sl.adequacy_of("CONTRADICTED; step at 09:12, deploy at 14:30") is None


def test_adequacy_of_none_when_variants_empty():
    assert sl.adequacy_of("adequacy: 34% (variants: )") is None


def test_adequacy_of_none_when_bound_empty():
    assert sl.adequacy_of("adequacy: (variants: τ ≥ 2h)") is None


def test_adequacy_atoms_collects_multiple():
    cell = "adequacy: 34% (variants: a). adequacy: 40% (variants: b)"
    assert sl._adequacy_atoms(cell) == [("34%", "a"), ("40%", "b")]


# --- C4 check: fixtures built inline (a full final ledger with Conclusion + Tests) ---
def _c4_ledger(status: str, tests_row: str, basis: str = "best supported") -> str:
    """A minimal final ledger: one H4 Conclusion row + one Tests table."""
    return (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        f"| H4 | causal | {status} | {basis} |\n\n"
        "## Tests\n\n"
        "| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"{tests_row}\n"
    )


def test_c4_known_positive_refuted_without_atom_fails():
    # the exact skipped-estimate route the two old-wording S6 arms took
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | "
        "events 2/3/1, not first-third (S1) |",
    )
    f = sl.check_c4(led, ["H4"])
    assert any("C4" in m and "H4" in m for m in f), f


def test_c4_passes_atom_in_contradicted_tests_evidence():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1); "
        "adequacy: 34% (variants: τ ≥ 2h) |",
    )
    assert sl.check_c4(led, ["H4"]) == []


def test_c4_passes_atom_in_conclusion_basis_alternate_site():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1) |",
        basis="refuted; adequacy: 34% (variants: τ ≥ 2h)",
    )
    assert sl.check_c4(led, ["H4"]) == []


def test_c4_unflagged_deterministic_refutation_is_untouched():
    # a legitimate deterministic refutation, NOT flagged, is never seen by C4
    led = _c4_ledger(
        "REFUTED",
        "| T1 | H4 | step must not precede deploy | align logs | CONTRADICTED | "
        "step precedes deploy (S1) |",
    )
    assert sl.check_c4(led, []) == []


def test_c4_flagged_unresolved_is_nothing_to_check():
    led = _c4_ledger(
        "UNRESOLVED",
        "| T4 | H4 | early clustering | compare timing | NON_DISCRIMINATING | underpowered (S1) |",
    )
    assert sl.check_c4(led, ["H4"]) == []


def test_c4_flagged_id_absent_fails_closed():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1) |",
    )
    f = sl.check_c4(led, ["H9"])
    assert any("C4" in m and "H9" in m for m in f)


def test_c4_conflicting_bounds_fail_closed():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | "
        "adequacy: 34% (variants: τ ≥ 2h) |",
        basis="refuted; adequacy: 90% (variants: τ ≥ 2h)",
    )
    f = sl.check_c4(led, ["H4"])
    assert any("C4" in m and "conflicting" in m.lower() for m in f)


def test_c4_no_tests_table_and_no_basis_atom_fails_closed():
    led = (
        "## Conclusion\n\n"
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H4 | causal | REFUTED | best supported |\n"
    )
    f = sl.check_c4(led, ["H4"])
    assert any("C4" in m and "H4" in m for m in f)


def test_c4_not_checked_when_flag_omitted():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1) |",
    )
    # descriptive so a causal-REFUTED does not trip C1 (which would empty `checked`);
    # no --plan -> C2 NOT CHECKED. The point: un-flagged, this REFUTED-with-no-atom
    # row is still green, and C4 reports NOT CHECKED rather than silently passing.
    led = led.replace("| H4 | causal |", "| H4 | descriptive (estimand: split) |")
    out = sl.score(led, None)  # no c4_ids -> C4 not run
    assert has("C4 NOT CHECKED", out.checked)
    assert not any("C4:" in m for m in out.fails)


def test_c4_end_to_end_positive_fails_the_run():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1) |",
    )
    # H4 is causal+REFUTED, so C1 also fires; assert C4 specifically is present
    out = sl.score(led, None, c4_ids=["H4"])
    assert has("C4:", out.fails)
    assert out.checked == []


def test_c4_end_to_end_describe_passed():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1); "
        "adequacy: 34% (variants: τ ≥ 2h) |",
    )
    # keep the row descriptive so C1 (causal-REFUTED) does not also fire
    led = led.replace("| H4 | causal |", "| H4 | descriptive (estimand: split) |")
    plan = plan_table("| H4 | descriptive (estimand: split) | n |")
    out = sl.score(led, plan, c4_ids=["H4"])
    assert has("C4 checked and passed", out.checked), out
    assert out.fails == []


def test_c4_describe_nothing_to_check_when_flagged_unresolved():
    led = _c4_ledger(
        "UNRESOLVED",
        "| T4 | H4 | early clustering | compare timing | NON_DISCRIMINATING | underpowered (S1) |",
    )
    out = sl.score(led, None, c4_ids=["H4"])
    assert has("C4 nothing to check", out.checked)
    assert out.fails == []


def test_c4_duplicate_flags_report_the_row_once():
    led = _c4_ledger(
        "REFUTED",
        "| T4 | H4 | early clustering | compare timing | CONTRADICTED | events 2/3/1 (S1); "
        "adequacy: 34% (variants: τ ≥ 2h) |",
    )
    led = led.replace("| H4 | causal |", "| H4 | descriptive (estimand: split) |")
    plan = plan_table("| H4 | descriptive (estimand: split) | n |")
    out = sl.score(led, plan, c4_ids=["H4", "h4"])  # same row, two casings
    assert out.fails == []
    line = next(m for m in out.checked if "C4 checked and passed" in m)
    assert "1 flagged" in line  # deduped, not "2 flagged"


def test_c4_fixture_known_positive_fails():
    final = read_fixture("c4-adequacy", "positive-no-bound.md")
    plan = read_fixture("c4-adequacy", "plan.md")
    out = sl.score(final, plan, c4_ids=["H4"])
    assert has("C4:", out.fails)
    assert out.checked == []


def test_c4_fixture_bound_recorded_passes():
    final = read_fixture("c4-adequacy", "negative-bound-recorded.md")
    plan = read_fixture("c4-adequacy", "plan.md")
    out = sl.score(final, plan, c4_ids=["H4"])
    assert out.fails == [], out.fails
    assert has("C4 checked and passed", out.checked)


def test_c4_fixture_deterministic_unflagged_is_clean():
    final = read_fixture("c4-adequacy", "negative-deterministic.md")
    plan = read_fixture("c4-adequacy", "plan.md")
    out = sl.score(final, plan)  # NOT flagged
    assert out.fails == [], out.fails
    assert has("C4 NOT CHECKED", out.checked)


def test_c4_fixture_na_passes_syntactically():
    final = read_fixture("c4-adequacy", "negative-na.md")
    plan = read_fixture("c4-adequacy", "plan.md")
    out = sl.score(final, plan, c4_ids=["H4"])
    assert out.fails == [], out.fails
    assert has("C4 checked and passed", out.checked)


# --- C4 fail-open regressions (cross-model review, issue #85) ---
def test_c4_ignores_atom_in_non_contradicted_sibling_row():
    # F1: an adequacy atom in a NON_DISCRIMINATING row (whose text merely mentions
    # "not CONTRADICTED") must NOT satisfy C4 for a flagged REFUTED id.
    led = (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H4 | descriptive (estimand: s) | REFUTED | best supported |\n\n"
        "## Tests\n\n"
        "| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| T4 | H4 | p | m | NON_DISCRIMINATING; not CONTRADICTED | adequacy: 34% (variants: x) |\n"
    )
    assert sl.check_c4(led, ["H4"]) != []  # must fail closed, not harvest the sibling atom


def test_c4_surfaces_malformed_tests_row():
    # F2: a malformed Tests row (lost outer pipe) hiding a conflicting bound must be
    # surfaced, not swallowed because a sibling row parsed and carried an atom.
    led = (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H4 | descriptive (estimand: s) | REFUTED | best supported |\n\n"
        "## Tests\n\n"
        "| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| T4 | H4 | p | m | CONTRADICTED | adequacy: 34% (variants: a) |\n"
        "T5 | H4 | p | m | CONTRADICTED | adequacy: 90% (variants: b) |\n"  # lost leading pipe
    )
    fails = sl.check_c4(led, ["H4"])
    assert any("malformed" in f for f in fails), fails  # the malformed row is surfaced


def test_c4_zero_width_atom_fields_are_empty():
    # F3b: Cf (format) chars like U+200B must be stripped before the emptiness check,
    # exactly as estimand_of does, so a visibly-empty atom is not counted.
    zw = "\u200b"
    assert sl.adequacy_of(f"adequacy: {zw} (variants: {zw})") is None
    led = _c4_ledger(
        "REFUTED",
        f"| T4 | H4 | p | m | CONTRADICTED | adequacy: {zw} (variants: {zw}) |",
    )
    led = led.replace("| H4 | causal |", "| H4 | descriptive (estimand: s) |")
    assert sl.check_c4(led, ["H4"]) != []  # empty atom → fail closed


def test_c4_surfaces_present_but_unreadable_tests_table():
    # Copilot #1: a Tests table PRESENT but unreadable (a header with no data rows, or every
    # row malformed) must fail closed even when a basis atom exists -- the broken table could
    # hide the flagged id's own refuting row, and score() reads the Tests table nowhere else.
    header = (
        "## Tests\n\n"
        "| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )
    concl = (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H4 | descriptive (estimand: s) | REFUTED | refuted; adequacy: 34% (variants: x) |\n\n"
    )
    malformed_row = "T4 | H4 | p | m | CONTRADICTED | events fell 2/3/1 |\n"  # lost leading pipe
    assert sl.check_c4(concl + header + malformed_row, ["H4"]) != []  # all-rows-malformed
    assert sl.check_c4(concl + header, ["H4"]) != []  # header, no data rows


def test_c4_absent_tests_table_with_basis_atom_still_passes():
    # control for Copilot #1: a genuinely ABSENT Tests table (a basis-only / mini-route
    # ledger) is benign -- the basis atom is a valid alternate recording site.
    led = (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H4 | descriptive (estimand: s) | REFUTED | refuted; adequacy: 34% (variants: x) |\n"
    )
    assert sl.check_c4(led, ["H4"]) == []


def test_c4_conflicting_variant_ranges_fail_closed():
    # Copilot #2: same bound, DIFFERENT variant range is an ambiguous record. The requirement
    # is to record a bound AND a variant range, so conflicting (bound, range) pairs fail
    # closed, not only conflicting bounds.
    led = (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H4 | descriptive (estimand: s) | REFUTED | b |\n\n"
        "## Tests\n\n"
        "| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| T4 | H4 | p | m | CONTRADICTED | adequacy: 34% (variants: a) |\n"
        "| T5 | H4 | p | m | CONTRADICTED | adequacy: 34% (variants: b) |\n"
    )
    assert any("conflicting" in m.lower() for m in sl.check_c4(led, ["H4"]))


def _c4_two_site_ledger(basis: str, evidence: str) -> str:
    """A flagged-REFUTED H4 recording an atom at BOTH accepted sites (Conclusion basis and
    its CONTRADICTED Tests row), so double-recording behavior can be exercised."""
    return (
        "## Conclusion\n\n| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        f"| H4 | descriptive (estimand: s) | REFUTED | {basis} |\n\n"
        "## Tests\n\n"
        "| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"| T4 | H4 | p | m | CONTRADICTED | {evidence} |\n"
    )


@pytest.mark.parametrize(
    ("basis", "evidence"),
    [
        # the design invites double recording (primary Tests site + accepted basis
        # alternate), so the SAME atom differing only in spacing or case is not a conflict
        ("adequacy: 34% (variants: any decay)", "adequacy: 34% (variants: any  decay)"),
        ("adequacy: 34% (variants: any decay)", "adequacy: 34% (variants: Any decay)"),
        ("adequacy: 34%±5pp (variants: x)", "adequacy: 34% ± 5pp (variants: x)"),
    ],
)
def test_c4_same_atom_at_both_sites_with_formatting_variance_passes(basis, evidence):
    # a scorer that fails correct ledgers gets ignored: trivial whitespace/case variance
    # between two recordings of the same atom must not read as a conflicting record
    assert sl.check_c4(_c4_two_site_ledger(basis, evidence), ["H4"]) == []


def test_c4_quoted_format_string_is_not_a_record():
    # a cell that merely QUOTES the documented form documents the obligation; it does not
    # record a bound. `<rate>`/`<range>` placeholders must not count as recorded fields.
    led = _c4_two_site_ledger(
        "must record `adequacy: <rate> ± <uncertainty> (variants: <range>)` next time",
        "events fell 2/3/1, no bound computed",
    )
    assert sl.check_c4(led, ["H4"]) != []


def test_adequacy_of_allows_a_parenthetical_inside_the_bound():
    # a citation inside the rate prose must not make the atom invisible (which would fail
    # closed with a misleading "records no adequacy bound" message)
    atom = sl.adequacy_of("adequacy: ~34% under resampling (S1 §3) (variants: any decay)")
    assert atom == ("~34% under resampling (S1 §3)", "any decay")
