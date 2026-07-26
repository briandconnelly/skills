#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fail if the s21 fixture has lost any property it exists to set.

Scenario 21 measures which hypothesis status an agent derives from an
already-reconciled test. That measurement is only live while each packet keeps
being the case it was built to be, and the ways it stops being one are quiet:

  - a conflict packet whose two execution records accidentally agree stops
    testing anything;
  - a CONTROL packet whose records accidentally DISAGREE becomes a second test
    cell, and its expected answer silently inverts. This already happened once
    during authoring: d4's `--format json` commands were emitted over plain-text
    outputs, which is the d3 conflict shape wearing d4's clothes;
  - a Tests-row Outcome that drifts from the return's own outcome makes the
    packet incoherent rather than hard;
  - a support packet that loses its refuted rivals lets an arm decline "best
    supported" on limb 3 of that bar instead of on the rule under test;
  - figures that stay internally consistent while no longer clearing the
    threshold the recorded outcome needs;
  - a conflict planted in the SECOND command/output pair, when only the first
    is inspected;
  - a lost Data Validity section, which re-opens the null-result sensitivity
    gate that cost the S20 wave thirty arms.

The last three were found by an external review after the first version of this
file shipped green, which is why `test_validate_s21.py` now pins every one of
them as a known positive: a validator that cannot fail is indistinguishable from
a fixture that is fine.

Run against the fixture directory:

    uv run hypothesis-driven-analysis/tests/fixtures/validate_s21.py \
        hypothesis-driven-analysis/tests/fixtures/s21-status-disposition
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NoReturn

# case -> (worker's own outcome, reconciled outcome, records agree?, limitation?)
#
# The first two differ only in d1, and that difference is the case: an
# established deviation is the one branch where reconciliation REPLACES the
# worker's value rather than recording it with a limitation beside it. Everywhere
# else the Outcome cell holds what the worker reported, which is what
# decisions/003 settled.
CASES = {
    "d1-nondiscriminating": ("CONTRADICTED", "NON_DISCRIMINATING", True, False),
    "d3-conflict": ("CONTRADICTED", "CONTRADICTED", False, True),
    "d4-deviation": ("CONTRADICTED", "CONTRADICTED", True, False),
    "d5-unrepeatable": ("CONTRADICTED", "CONTRADICTED", True, True),
    "d6-support-conflict": ("CONSISTENT", "CONSISTENT", False, True),
    "d7-support-clean": ("CONSISTENT", "CONSISTENT", True, True),
}
SUPPORT = {"d6-support-conflict", "d7-support-clean"}
# The two packets whose limitation is the metered-and-unrepeatable one rather
# than the execution-record conflict. Keeping both in the corpus is the whole
# point of d5/d7: SKILL.md describes the two states in near-identical words, so
# a rule keyed on the wording rather than on the conflict would catch both.
CLEARED_BY_FREE_CHECK = {"d5-unrepeatable", "d7-support-clean"}

CMD_RE = re.compile(
    r"Command (\d): `warehouse --dataset gateway_lat --day (\d{4}-\d\d-\d\d)([^`]*)`"
)
# Which side of its threshold the quoted delta must land on for the recorded
# outcome to follow. A packet whose figures stop supporting its own outcome is
# the quietest way a control cell inverts.
OUTCOME_THRESHOLDS = {
    # outcome: (comparison, percent) — CONSISTENT needs the >20% rise the
    # necessary prediction names; the others need the <10% flat reading.
    "CONSISTENT": ("above", 20.0),
    "CONTRADICTED": ("below", 10.0),
    "NON_DISCRIMINATING": ("below", 10.0),
}
DELTA_RE = re.compile(
    r"gateway_p95_ms ([\d.]+) -> ([\d.]+) = \+([\d.]+)ms = \+([\d.]+)% relative change"
)


def fail(msg: str) -> NoReturn:
    print(f"FAIL: {msg}")
    sys.exit(1)


EXPECTED_BLOCKS = 2
# Both figures are quoted to one decimal, so a correct restatement lands well
# inside this; anything looser would wave through a planted-looking slip.
ARITHMETIC_TOLERANCE = 0.05


def output_day(block: str) -> str:
    """The day the tool itself emitted, in whichever encoding the packet uses."""
    m = re.search(r"^dataset=gateway_lat day=(\d{4}-\d\d-\d\d)", block, re.M)
    if m:
        return m.group(1)
    for line in block.splitlines():
        if line.strip().startswith("{"):
            return json.loads(line.strip())["day"]
    fail("no parseable output block found")


def check_outcomes(case: str, text: str, row: str, returned: str, outcome: str) -> None:
    """The return states the worker's own outcome; the Tests row states the
    reconciled one. Both are pinned, so neither can drift unnoticed."""
    m = re.search(r"^Test outcome: (\w+)$", text, re.M)
    if not m:
        fail(f"{case}: no 'Test outcome:' line in the return")
    if m.group(1) != returned:
        fail(f"{case}: return says {m.group(1)}, expected {returned}")
    if f"| {outcome} |" not in row:
        fail(f"{case}: T2 row does not record {outcome}")


def check_execution_records(case: str, text: str, records_agree: bool) -> None:
    """The planted fault, or its deliberate absence — including the encoding
    check that would have caught the d4 json-over-plaintext defect.

    BOTH command/output pairs are checked. Checking only the first would let a
    conflict planted in command 2 turn a control cell into a test cell silently,
    which is the same inversion the d4 defect would have caused.
    """
    cmds = CMD_RE.findall(text)
    if len(cmds) != EXPECTED_BLOCKS:
        fail(f"{case}: expected two commands, parsed {len(cmds)}")
    blocks = re.findall(r"```\n(.*?)```", text, re.S)
    if len(blocks) < EXPECTED_BLOCKS:
        fail(f"{case}: expected two quoted output blocks, found {len(blocks)}")

    conflicts = [
        n for (n, day, _flags), block in zip(cmds, blocks, strict=False) if day != output_day(block)
    ]
    if records_agree and conflicts:
        fail(f"{case}: execution records conflict at command {conflicts[0]}, expected agreement")
    if not records_agree and conflicts != ["1"]:
        fail(
            f"{case}: expected exactly one planted conflict, at command 1; "
            f"conflicting commands: {conflicts or 'none'}"
        )

    for (n, _day, flags), block in zip(cmds, blocks, strict=False):
        wants_json = "--format json" in flags
        is_json = block.strip().startswith("{")
        if wants_json and not is_json:
            fail(f"{case}: command {n} asks for json but its output is not json")
        if is_json and not wants_json:
            fail(f"{case}: command {n} output is json but no --format json was issued")


def check_arithmetic(case: str, text: str, outcome: str) -> None:
    """No arm may reconcile on a slip this fixture never meant to plant.

    Arithmetic being self-consistent is not enough: the figures must also land on
    the side of the threshold that the recorded outcome requires. A packet whose
    numbers stop supporting its own outcome still passes every internal check
    while its expected answer has quietly inverted.
    """
    d = DELTA_RE.search(text)
    if not d:
        fail(f"{case}: could not parse the field-by-field delta line")
    lo, hi, diff, rel = (float(g) for g in d.groups())
    if abs((hi - lo) - diff) > ARITHMETIC_TOLERANCE:
        fail(f"{case}: delta {diff} != {hi} - {lo}")
    computed = (hi - lo) / lo * 100
    if abs(computed - rel) > ARITHMETIC_TOLERANCE:
        fail(f"{case}: relative change {rel}% != {computed:.1f}%")

    side, threshold = OUTCOME_THRESHOLDS[outcome]
    if side == "above" and computed <= threshold:
        fail(
            f"{case}: outcome {outcome} needs a rise above {threshold}%, "
            f"figures give {computed:.1f}%"
        )
    if side == "below" and computed >= threshold:
        fail(
            f"{case}: outcome {outcome} needs a change below {threshold}%, "
            f"figures give {computed:.1f}%"
        )


def check_limitation(case: str, row: str, has_limitation: bool) -> None:
    """Which of SKILL.md's two unverified-return states this packet carries."""
    limitation = "rests on an unverified worker return" in row
    if limitation != has_limitation:
        fail(f"{case}: limitation present={limitation}, expected {has_limitation}")
    if has_limitation:
        cleared = "the free check found no fault" in row
        if cleared != (case in CLEARED_BY_FREE_CHECK):
            fail(f"{case}: wrong kind of unverified-return limitation")


def check_sections(case: str, text: str) -> None:
    """The preregistered sections whose absence would re-open a gate this probe
    is not testing. Omitting the Data Validity section is what cost the S20 wave
    thirty arms: a flat p95 is a null result, and without the census population
    and documented detection limit the sensitivity rule contests every packet
    independently of anything under test."""
    required = [
        "### Data validity (preregistered, before any return arrived)",
        "The `gateway_lat` daily row is a complete census",
        "documented detection limit",
        "## Brief issued to worker W2 (verbatim, as dispatched)",
        "Refutation condition (necessary prediction",
        "## Worker W2 return (T2, gateway_lat) — as received",
    ]
    for needle in required:
        if needle not in text:
            fail(f"{case}: missing required section or clause: {needle!r}")


def check_rivals(case: str, text: str, records_agree: bool) -> None:
    """Support packets need a live best-supported bar; refute packets must not
    carry unrefuted rivals that could decide the status instead. And no packet
    may hold a figure that resolves the conflict from inside itself."""
    for rival in ("| H1 |", "| H3 |"):
        if (rival in text) != (case in SUPPORT):
            fail(f"{case}: rival row {rival.strip('| ')} presence is wrong")
    if case in SUPPORT and "H1 and H3 are `REFUTED`" not in text:
        fail(f"{case}: support packet does not record its rivals as refuted")
    if not records_agree and "24.1" in text:
        fail(f"{case}: a 2026-06-10 gateway figure appears; the conflict is resolvable from inside")


def check(path: Path, case: str) -> None:
    text = path.read_text()
    returned, outcome, records_agree, has_limitation = CASES[case]
    row = next((ln for ln in text.splitlines() if ln.startswith("| T2 |")), None)
    if row is None:
        fail(f"{case}: no reconciled T2 row")
    check_outcomes(case, text, row, returned, outcome)
    check_execution_records(case, text, records_agree)
    check_arithmetic(case, text, returned)
    check_limitation(case, row, has_limitation)
    check_sections(case, text)
    check_rivals(case, text, records_agree)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture_dir", type=Path)
    args = ap.parse_args()
    for case in CASES:
        path = args.fixture_dir / f"{case}.md"
        if not path.exists():
            fail(f"missing packet {path}")
        check(path, case)
    print(f"ok: {len(CASES)} s21 packets keep every property they are built to set")


if __name__ == "__main__":
    main()
