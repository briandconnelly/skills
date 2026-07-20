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


def test_cell_count_mismatch_bails():
    # An unescaped stray `|` gives the H2 row an extra cell. Today this bails
    # audit-wide (score_ledger.py notes the cell-count case is left audit-wide
    # "for now"; issue #81 tracks narrowing it to row-local). We pin only the
    # stable contract — the parse failure is surfaced and nothing is earned —
    # and deliberately leave C1 visibility on the sibling UNSPECIFIED so #81's
    # improvement does not redden this characterization test.
    out = sl.score(
        summary(
            "| H1 | causal | REFUTED | violation |\n"
            "| H2 | descriptive | UNRESOLVED | a | b stray pipe |"
        ),
        None,
    )
    assert has("cell(s) but the header", out.fails)
    assert out.checked == []  # nothing earned behind the parse failure


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
    body = (
        "| id | claim | status | basis |\n| --- | --- | --- | --- |\n"
        "| H3 | data-artifact | UNRESOLVED | the still-open cases mean the median "
        "is understated |\n"
    )
    assert any("C3a" in m for m in sl.check_c3a(concl(body)))


def test_c3a_fails_closed_without_conclusion():
    f = sl.check_c3a("## Sources\n\n| id | x |\n| --- | --- |\n| S1 | y |\n")
    assert any("Conclusion" in m for m in f)


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
