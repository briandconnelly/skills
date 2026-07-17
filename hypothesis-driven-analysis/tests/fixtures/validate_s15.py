#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fail if the s15 fixture has lost any trap it exists to set.

The s15 scenario tests whether an analyst assigns a causal status on evidence
that cannot support one. That test is only live while the fixture keeps every
trap below. Run against the fixture directory:

    uv run hypothesis-driven-analysis/tests/fixtures/validate_s15.py \
        hypothesis-driven-analysis/tests/fixtures/s15-assist-rollout
"""

from __future__ import annotations

import argparse
import csv
import statistics as st
from datetime import datetime
from pathlib import Path

SEVS = ("sev1", "sev2", "sev3")

# Trap 2: severity mix must shift by more than this share at the cutover, or
# the shift is too small to plausibly explain the headline as a mix effect.
SEV3_MIX_SHIFT_FLOOR = 0.15

# Trap 4: missing activity rows must concentrate in the assist week by at
# least this share, or the selection trap (assist rows vanish, not manual
# ones) is too diluted to bias the marginal median.
MISSING_ROWS_ASSIST_FLOOR = 0.8

# Trap 4: assist sev1 closure rate must trail manual sev1 closure rate by at
# least this many percentage points, or missingness isn't concentrated enough
# in the stratum (sev1) that drives the reversal.
ASSIST_SEV1_CLOSURE_GAP_FLOOR = 0.25

# Trap 7: assist sev1 reopen rate must exceed manual sev1 reopen rate by at
# least this many percentage points, or the reopen cluster used to explain
# away the "improvement" is too weak to be convincing.
ASSIST_SEV1_REOPEN_GAP_FLOOR = 0.5


def _load(d: Path) -> tuple[list[dict], dict[str, dict]]:
    inc = list(csv.DictReader((d / "incidents.csv").open()))
    act = {a["incident_id"]: a for a in csv.DictReader((d / "activity.csv").open())}
    return inc, act


def _ts(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def _rows(inc: list[dict], act: dict[str, dict]) -> list[dict]:
    out = []
    for r in inc:
        a = act.get(r["incident_id"])
        rec = dict(r)
        rec["closed"] = a is not None
        if a:
            rec["ttc_h"] = (_ts(a["closed_at"]) - _ts(r["opened_at"])).total_seconds() / 3600
            rec["rmin"] = int(a["responder_minutes"])
            rec["handoffs"] = int(a["handoffs"])
            rec["reopen"] = int(a["reopened_within_72h"])
        out.append(rec)
    return out


def _sel(rows, wf, sev=None, closed=True):
    return [
        r
        for r in rows
        if r["workflow"] == wf
        and (sev is None or r["severity"] == sev)
        and (r["closed"] or not closed)
    ]


def _check_volume_matched(rows: list[dict]) -> list[str]:
    """Trap 1: volume identical across weeks, so volume cannot explain the headline."""
    fails: list[str] = []
    n_man = len(_sel(rows, "manual", closed=False))
    n_ass = len(_sel(rows, "assist", closed=False))
    if n_man != n_ass:
        fails.append(f"volume differs across weeks ({n_man} vs {n_ass}); volume becomes a rival")
    return fails


def _check_severity_mix_shift(rows: list[dict]) -> list[str]:
    """Trap 2: severity mix shifts at the cutover."""

    def share(wf, sev):
        g = _sel(rows, wf, closed=False)
        return sum(1 for r in g if r["severity"] == sev) / len(g)

    fails: list[str] = []
    if not (share("assist", "sev3") - share("manual", "sev3")) > SEV3_MIX_SHIFT_FLOOR:
        fails.append("severity mix no longer shifts materially at the cutover")
    return fails


def _check_severity_mix_constant_within_week(rows: list[dict]) -> list[str]:
    """Trap 3: the mix is constant within each week (a systematic change, not drift)."""
    fails: list[str] = []
    for wf in ("manual", "assist"):
        by_day: dict[str, list[str]] = {}
        for r in _sel(rows, wf, closed=False):
            by_day.setdefault(r["opened_at"][:10], []).append(r["severity"])
        sigs = {tuple(sorted(v).count(s) for s in SEVS) for v in by_day.values()}
        if len(sigs) != 1:
            fails.append(f"{wf} week mix is no longer constant day to day: {sorted(sigs)}")
    return fails


def _check_missing_activity_selection(rows: list[dict]) -> list[str]:
    """Trap 4: missing activity concentrates in the assist week and in sev1."""
    fails: list[str] = []
    miss = [r for r in rows if not r["closed"]]
    if not miss:
        fails.append("no missing activity rows; the selection trap is gone")
        return fails

    frac = sum(1 for r in miss if r["workflow"] == "assist") / len(miss)
    if frac < MISSING_ROWS_ASSIST_FLOOR:
        fails.append(f"missing rows no longer concentrate in assist ({frac:.0%} < 80%)")

    man1 = _sel(rows, "manual", "sev1", closed=False)
    ass1 = _sel(rows, "assist", "sev1", closed=False)
    rate_m = sum(r["closed"] for r in man1) / len(man1)
    rate_a = sum(r["closed"] for r in ass1) / len(ass1)
    if rate_m - rate_a < ASSIST_SEV1_CLOSURE_GAP_FLOOR:
        fails.append(
            f"assist sev1 closure rate no longer far below manual "
            f"({rate_a:.0%} vs {rate_m:.0%}; need a 25pp gap)"
        )
    return fails


def _check_marginal_reversal(rows: list[dict]) -> list[str]:
    """Trap 5: THE trap. Marginal median falls while every stratum median rises."""
    fails: list[str] = []
    marg_m = st.median([r["ttc_h"] for r in _sel(rows, "manual")])
    marg_a = st.median([r["ttc_h"] for r in _sel(rows, "assist")])
    if marg_a >= marg_m:
        fails.append(f"marginal median no longer falls ({marg_m:.2f} -> {marg_a:.2f}); no headline")
    for s in SEVS:
        m = st.median([r["ttc_h"] for r in _sel(rows, "manual", s)])
        a = st.median([r["ttc_h"] for r in _sel(rows, "assist", s)])
        if a <= m:
            fails.append(
                f"{s} median no longer rises under assist ({m:.2f} -> {a:.2f}); no reversal"
            )
    return fails


def _check_responder_effort_rises(rows: list[dict]) -> list[str]:
    """Trap 6: responder effort rises within every stratum."""
    fails: list[str] = []
    for s in SEVS:
        m = st.median([r["rmin"] for r in _sel(rows, "manual", s)])
        a = st.median([r["rmin"] for r in _sel(rows, "assist", s)])
        if a <= m:
            fails.append(f"{s} responder effort no longer rises under assist ({m} -> {a})")
    return fails


def _check_assist_sev1_reopen_cluster(rows: list[dict]) -> list[str]:
    """Trap 7: the assist sev1 reopen cluster."""
    fails: list[str] = []
    ass1c = _sel(rows, "assist", "sev1")
    man1c = _sel(rows, "manual", "sev1")
    r_a = sum(r["reopen"] for r in ass1c) / len(ass1c)
    r_m = sum(r["reopen"] for r in man1c) / len(man1c)
    if r_a - r_m < ASSIST_SEV1_REOPEN_GAP_FLOOR:
        fails.append(f"assist sev1 reopen cluster gone ({r_a:.0%} vs manual {r_m:.0%})")
    return fails


def _check_handoffs_reversal(rows: list[dict]) -> list[str]:
    """Trap 8: handoffs carries the same reversal, marginally improving."""
    fails: list[str] = []
    h_m = st.mean([r["handoffs"] for r in _sel(rows, "manual")])
    h_a = st.mean([r["handoffs"] for r in _sel(rows, "assist")])
    if h_a >= h_m:
        fails.append(f"handoffs no longer improves marginally ({h_m:.3f} -> {h_a:.3f})")
    for s in ("sev2", "sev3"):
        m = st.mean([r["handoffs"] for r in _sel(rows, "manual", s)])
        a = st.mean([r["handoffs"] for r in _sel(rows, "assist", s)])
        if a <= m:
            fails.append(f"{s} handoffs no longer worsens under assist ({m:.3f} -> {a:.3f})")
    return fails


_TRAP_CHECKS = (
    _check_volume_matched,
    _check_severity_mix_shift,
    _check_severity_mix_constant_within_week,
    _check_missing_activity_selection,
    _check_marginal_reversal,
    _check_responder_effort_rises,
    _check_assist_sev1_reopen_cluster,
    _check_handoffs_reversal,
)


def check(d: Path) -> list[str]:
    inc, act = _load(d)
    rows = _rows(inc, act)
    fails: list[str] = []
    for trap_check in _TRAP_CHECKS:
        fails.extend(trap_check(rows))
    return fails


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture_dir", type=Path)
    args = parser.parse_args()
    fails = check(args.fixture_dir)
    if fails:
        print("FAIL: s15 has lost traps it exists to set:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK: every s15 trap present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
