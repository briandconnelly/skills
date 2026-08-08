"""Executable tests for compare_prereg.py — run with:

    uv run --with pytest pytest hypothesis-driven-analysis/tests/test_compare_prereg.py -v

Until 2026-08-08 this instrument had no tests at all, and nothing in prek or CI
ran the suites that did exist. The two gaps these tests pin were both found by
probing the shipped script, not by reading it:

  - The Problem section's precommitments were outside every instrument.
    Weakening the stop condition and quadrupling the effort budget between plan
    and final printed "OK: no preregistered cell changed". The stop rule is the
    loop's central anti-fishing device, and it could be rewritten once the
    results were in.
  - Deleting the necessary-prediction column from both ledgers passed, because
    the diff only ever compared columns the two ledgers share. Immutability and
    presence are different properties; only the first was checked.

compare_prereg imports score_ledger from its own directory, so it is loaded by
path with sys.path prepared, mirroring test_score_ledger.py's importlib
approach. Both modules import only the standard library.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).parent
FIX = HERE / "fixtures"

if str(HERE) not in sys.path:  # compare_prereg does `from score_ledger import ...`
    sys.path.insert(0, str(HERE))

_spec = importlib.util.spec_from_file_location("compare_prereg", HERE / "compare_prereg.py")
assert _spec is not None
assert _spec.loader is not None
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)


# --------------------------------------------------------------------------- #
# helpers — a minimal well-formed plan/final pair
# --------------------------------------------------------------------------- #
PROBLEM = """## Problem

- Decision informed: whether to expand the assist rollout
- Falsifiable question: did assist reduce time-to-close in July 2026
- Success criteria: answered means a signed contrast with an interval
- Stop condition: conclude when every named rival has a recorded outcome
- Effort budget: 25 queries
"""

HYPS = """## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | \
Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | assist sped closes | faster | not faster | assist arm closes faster | T1 | tickets |
"""

TESTS = """## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | assist arm closes faster | median contrast | {outcome} | S1 |
"""


def ledger(problem: str = PROBLEM, hyps: str = HYPS, outcome: str = "NOT_TESTED") -> str:
    return f"{problem}\n{hyps}\n{TESTS.format(outcome=outcome)}"


def run(plan: str, final: str) -> cp.Outcome:
    return cp.compare(plan, final)


# --------------------------------------------------------------------------- #
# baseline — the instrument must pass work that is actually clean, or every
# failure below is indistinguishable from a broken instrument
# --------------------------------------------------------------------------- #
def test_clean_pair_passes_and_reports_what_it_compared() -> None:
    out = run(ledger(), ledger(outcome="CONSISTENT"))
    assert out.fails == []
    assert out.diffs == []
    assert any("Problem section compared" in c for c in out.checked)


def test_archived_calibration_pair_still_passes() -> None:
    """The real s15 arm-e plan/final-clean pair, unchanged by the new checks."""
    plan = (FIX / "s15-prereg-drift" / "arm-e-plan.md").read_text(encoding="utf-8")
    final = (FIX / "s15-prereg-drift" / "arm-e-final-clean.md").read_text(encoding="utf-8")
    out = run(plan, final)
    assert out.fails == []
    assert out.diffs == []


def test_archived_drift_pair_still_reports_its_tests_drift() -> None:
    """The known-positive: the drift this instrument was built for is still caught."""
    plan = (FIX / "s15-prereg-drift" / "arm-e-plan.md").read_text(encoding="utf-8")
    final = (FIX / "s15-prereg-drift" / "arm-e-final.md").read_text(encoding="utf-8")
    out = run(plan, final)
    assert out.fails == []
    assert any("Tests row T1" in d for d in out.diffs)
    # and the new Problem check does not fire on it — no false positive
    assert not any("Problem field" in d for d in out.diffs)


# --------------------------------------------------------------------------- #
# Problem-section precommitments
# --------------------------------------------------------------------------- #
def test_weakened_stop_condition_is_reported() -> None:
    weak = PROBLEM.replace(
        "conclude when every named rival has a recorded outcome",
        "conclude when the leading explanation looks well supported",
    )
    out = run(ledger(), ledger(problem=weak))
    assert out.fails == []
    assert any("'stop condition'" in d and "UNEXPLAINED" in d for d in out.diffs)


def test_inflated_effort_budget_is_reported() -> None:
    out = run(ledger(), ledger(problem=PROBLEM.replace("25 queries", "100 queries")))
    assert any("'effort budget'" in d for d in out.diffs)


def test_amendment_downgrades_the_label_but_never_passes() -> None:
    """Same contract as the row diff: an amendment makes it reviewable, not clean."""
    final = ledger(problem=PROBLEM.replace("25 queries", "100 queries"))
    final += "\n## Amendments\n\n- 2026-08-08: budget raised to 100 after the first pull\n"
    out = run(ledger(), final)
    assert any("CANDIDATE AMENDMENT" in d for d in out.diffs)
    assert out.diffs  # still a difference: exit 1, not waved through


def test_missing_problem_field_is_unverifiable() -> None:
    stripped = "\n".join(
        line for line in PROBLEM.splitlines() if not line.startswith("- Stop condition:")
    )
    out = run(ledger(problem=stripped), ledger())
    assert any("states no 'stop condition'" in f for f in out.fails)


def test_unfilled_placeholder_is_not_a_precommitment() -> None:
    placeheld = PROBLEM.replace("25 queries", "<tool calls | queries | wall-clock>")
    out = run(ledger(problem=placeheld), ledger(problem=placeheld))
    assert any("placeholder" in f for f in out.fails)


def test_absent_problem_section_is_unverifiable() -> None:
    out = run(ledger(problem=""), ledger())
    assert any("'## Problem' section(s)" in f for f in out.fails)


def test_duplicate_problem_field_is_ambiguous() -> None:
    doubled = PROBLEM + "- Stop condition: whenever it feels done\n"
    out = run(ledger(problem=doubled), ledger(problem=doubled))
    assert any("2 times" in f for f in out.fails)


# --------------------------------------------------------------------------- #
# necessary-prediction column — presence, not immutability
# --------------------------------------------------------------------------- #
BOTH_LEDGERS = 2  # plan and final are each named separately in a schema failure


def _drop_necessary_column(hyps: str) -> str:
    out = []
    for line in hyps.splitlines():
        if line.strip().startswith("|"):
            cells = line.split("|")
            del cells[6]
            out.append("|".join(cells))
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def test_column_deleted_from_both_ledgers_is_unverifiable() -> None:
    """The gap: absent from both sides, it read as 'unchanged' and passed."""
    stripped = _drop_necessary_column(HYPS)
    out = run(ledger(hyps=stripped), ledger(hyps=stripped))
    assert any("carries no 'necessary prediction" in f for f in out.fails)
    assert len([f for f in out.fails if "necessary prediction" in f]) == BOTH_LEDGERS


def test_empty_necessary_prediction_cell_is_unverifiable() -> None:
    blanked = HYPS.replace("| assist arm closes faster | T1 |", "|  | T1 |")
    out = run(ledger(), ledger(hyps=blanked))
    assert any("declares no necessary prediction" in f for f in out.fails)


def test_placeholder_necessary_prediction_is_unverifiable() -> None:
    held = HYPS.replace("| assist arm closes faster | T1 |", "| n/a | T1 |")
    out = run(ledger(hyps=held), ledger(hyps=held))
    assert any("declares no necessary prediction" in f for f in out.fails)


def test_descriptive_row_without_an_estimand_is_unverifiable() -> None:
    """The template requires an estimand on every descriptive row; score_ledger's
    C2 only ever checked the ones that ended up REFUTED."""
    desc = HYPS.replace("| H1 | causal |", "| H1 | descriptive |")
    out = run(ledger(hyps=desc), ledger(hyps=desc))
    assert any("names no estimand" in f for f in out.fails)


def test_descriptive_row_with_an_estimand_passes() -> None:
    desc = HYPS.replace("| H1 | causal |", "| H1 | descriptive (estimand: median time-to-close) |")
    out = run(ledger(hyps=desc), ledger(hyps=desc))
    assert out.fails == []
