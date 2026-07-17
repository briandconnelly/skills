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

import csv
import statistics as st
import sys
from datetime import datetime
from pathlib import Path

SEVS = ("sev1", "sev2", "sev3")


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


def check(d: Path) -> list[str]:  # noqa: PLR0912, PLR0915
    inc, act = _load(d)
    rows = _rows(inc, act)
    fails: list[str] = []

    # Trap 1: volume identical across weeks, so volume cannot explain the headline.
    n_man = len(_sel(rows, "manual", closed=False))
    n_ass = len(_sel(rows, "assist", closed=False))
    if n_man != n_ass:
        fails.append(f"volume differs across weeks ({n_man} vs {n_ass}); volume becomes a rival")

    # Trap 2: severity mix shifts at the cutover.
    def share(wf, sev):
        g = _sel(rows, wf, closed=False)
        return sum(1 for r in g if r["severity"] == sev) / len(g)

    if not (share("assist", "sev3") - share("manual", "sev3")) > 0.15:  # noqa: PLR2004
        fails.append("severity mix no longer shifts materially at the cutover")

    # Trap 3: the mix is constant within each week (a systematic change, not drift).
    for wf in ("manual", "assist"):
        by_day: dict[str, list[str]] = {}
        for r in _sel(rows, wf, closed=False):
            by_day.setdefault(r["opened_at"][:10], []).append(r["severity"])
        sigs = {tuple(sorted(v).count(s) for s in SEVS) for v in by_day.values()}
        if len(sigs) != 1:
            fails.append(f"{wf} week mix is no longer constant day to day: {sorted(sigs)}")

    # Trap 4: missing activity concentrates in the assist week and in sev1.
    miss = [r for r in rows if not r["closed"]]
    if not miss:
        fails.append("no missing activity rows; the selection trap is gone")
    else:
        frac = sum(1 for r in miss if r["workflow"] == "assist") / len(miss)
        if frac < 0.8:  # noqa: PLR2004
            fails.append(f"missing rows no longer concentrate in assist ({frac:.0%} < 80%)")
        man1 = _sel(rows, "manual", "sev1", closed=False)
        ass1 = _sel(rows, "assist", "sev1", closed=False)
        rate_m = sum(r["closed"] for r in man1) / len(man1)
        rate_a = sum(r["closed"] for r in ass1) / len(ass1)
        if rate_m - rate_a < 0.25:  # noqa: PLR2004
            fails.append(
                f"assist sev1 closure rate no longer far below manual "
                f"({rate_a:.0%} vs {rate_m:.0%}; need a 25pp gap)"
            )

    # Trap 5: THE trap. Marginal median falls while every stratum median rises.
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

    # Trap 6: responder effort rises within every stratum.
    for s in SEVS:
        m = st.median([r["rmin"] for r in _sel(rows, "manual", s)])
        a = st.median([r["rmin"] for r in _sel(rows, "assist", s)])
        if a <= m:
            fails.append(f"{s} responder effort no longer rises under assist ({m} -> {a})")

    # Trap 7: the assist sev1 reopen cluster.
    ass1c = _sel(rows, "assist", "sev1")
    man1c = _sel(rows, "manual", "sev1")
    r_a = sum(r["reopen"] for r in ass1c) / len(ass1c)
    r_m = sum(r["reopen"] for r in man1c) / len(man1c)
    if r_a - r_m < 0.5:  # noqa: PLR2004
        fails.append(f"assist sev1 reopen cluster gone ({r_a:.0%} vs manual {r_m:.0%})")

    # Trap 8: handoffs carries the same reversal, marginally improving.
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


def main() -> int:
    if len(sys.argv) != 2:  # noqa: PLR2004
        print("usage: validate_s15.py <fixture_dir>", file=sys.stderr)
        return 2
    fails = check(Path(sys.argv[1]))
    if fails:
        print("FAIL: s15 has lost traps it exists to set:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("OK: every s15 trap present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
