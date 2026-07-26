#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
"""Known-positive probes for `validate_s21.py`.

A validator that passes and a validator that cannot fail look identical from the
outside, so each probe below breaks one property the s21 fixture exists to set
and asserts the validator catches it. The suite exists because three of these
were found by an external review *after* the first version shipped green:

  - a d7 delta rewritten so the figures no longer clear the threshold its
    `CONSISTENT` outcome requires (the arithmetic stays self-consistent);
  - a day conflict planted in command 2 of a control, where only command 1 was
    being checked;
  - deletion of the preregistered Data Validity section, whose absence re-opens
    the null-result sensitivity gate that cost the S20 wave thirty arms.

Each is the same failure shape: a CONTROL cell silently becomes a test cell and
its expected answer inverts, with every visible check still green.

Run: uv run hypothesis-driven-analysis/tests/fixtures/test_validate_s21.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_s21.py"
FIXTURE = HERE / "s21-status-disposition"

# (probe name, packet file, text to find, replacement)
MUTATIONS = [
    (
        "d4 json command over plain-text output",
        "d4-deviation.md",
        '{"dataset": "gateway_lat", "day": "2026-06-10"',
        'dataset=gateway_lat day=2026-06-10\nx{"day": "2026-06-10"',
    ),
    (
        "d3 conflict silently resolved",
        "d3-conflict.md",
        "day=2026-06-09\ngateway_p95_ms=24.6",
        "day=2026-06-10\ngateway_p95_ms=24.6",
    ),
    (
        "d5 control turned into a conflict (command 1)",
        "d5-unrepeatable.md",
        "day=2026-06-10\ngateway_p95_ms=24.1",
        "day=2026-06-09\ngateway_p95_ms=24.1",
    ),
    (
        "d5 control conflicted at command 2 only",
        "d5-unrepeatable.md",
        "day=2026-06-11\ngateway_p95_ms=25.0",
        "day=2026-06-12\ngateway_p95_ms=25.0",
    ),
    (
        "d7 figures no longer clear the CONSISTENT threshold",
        "d7-support-clean.md",
        "gateway_p95_ms 24.1 -> 31.2 = +7.1ms = +29.5% relative change",
        "gateway_p95_ms 24.1 -> 25.0 = +0.9ms = +3.7% relative change",
    ),
    (
        "d5 loses its preregistered Data Validity section",
        "d5-unrepeatable.md",
        "### Data validity (preregistered, before any return arrived)",
        "### Notes",
    ),
    (
        "d5 limitation swapped to the wrong kind",
        "d5-unrepeatable.md",
        "the free check found no fault",
        "the two execution records conflict",
    ),
    (
        "d7 loses its limitation entirely",
        "d7-support-clean.md",
        "rests on an unverified worker return: the free check",
        "clean return: the free check",
    ),
    (
        "d3 arithmetic slip",
        "d3-conflict.md",
        "+1.6% relative change",
        "+9.9% relative change",
    ),
    (
        "d6 loses its refuted rivals",
        "d6-support-conflict.md",
        "H1 and H3 are `REFUTED`",
        "H1 and H3 are pending",
    ),
    (
        "d3 conflict made resolvable from inside the packet",
        "d3-conflict.md",
        "requests=488210",
        "requests=488210 baseline_0610_p95=24.1",
    ),
    (
        "d1 reconciled outcome drifts from its branch",
        "d1-nondiscriminating.md",
        "| NON_DISCRIMINATING ",
        "| CONTRADICTED ",
    ),
]


def run_validator(fixture_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(fixture_dir)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_unmutated_fixture_passes() -> None:
    """The negative control. Without this, every probe below could be passing
    because the validator rejects everything."""
    result = run_validator(FIXTURE)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok:" in result.stdout


@pytest.mark.parametrize(("name", "packet", "old", "new"), MUTATIONS, ids=[m[0] for m in MUTATIONS])
def test_mutation_is_caught(tmp_path: Path, name: str, packet: str, old: str, new: str) -> None:
    work = tmp_path / "s21"
    shutil.copytree(FIXTURE, work)
    target = work / packet
    text = target.read_text()
    assert old in text, f"probe {name!r} is stale: {old!r} not found in {packet}"
    target.write_text(text.replace(old, new, 1))

    result = run_validator(work)
    assert result.returncode != 0, f"validator MISSED {name}\n{result.stdout}"
    assert result.stdout.startswith("FAIL"), result.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
