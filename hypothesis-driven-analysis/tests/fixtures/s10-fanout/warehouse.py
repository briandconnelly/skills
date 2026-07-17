#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mock metered warehouse CLI for the fan-out scenario.

Each query is deliberately slow (~18s) and metered, so three independent
hypotheses cost ~54s serially versus ~18s in parallel. This is what makes the
fan-out criterion ("a slow or metered collection that would otherwise run
serially") observably true rather than a guess about token savings.

GROUND TRUTH for the page-load regression on 2026-07-15:
  - cdn_edge     -> CDN edge latency FLAT across the regression (refutes H1;
                    its necessary prediction is a p95 rise at the edge).
  - db_slowlog   -> a missing index on `sessions.user_id` appears 2026-07-15
                    09:00 and query p95 rises 40ms -> 610ms (supports H2).
  - client_rum   -> client-side render time FLAT; the regression is server-side
                    (refutes H3).
The `orders` dataset serves Scenario 14 (metered descriptive query): 30 June
days of order amounts behind the same metered CLI, so "median order value in
June" is a bounded descriptive statistic bought at a price -- route `direct`
with a collection plan, not `full` with a hypothesis table.

Usage: warehouse.py --dataset {orders,cdn_edge,db_slowlog,client_rum} --day YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import random
import sys
import time

QUERY_SECONDS = 18.0
"""Deliberate per-query latency for the fan-out (S10) datasets."""

ORDERS_QUERY_SECONDS = 3.0
"""S14 orders are metered too, but cheaper per call, so a 30-day median pull
stays tractable to run for real while remaining observably costly."""


def _build_orders() -> dict[str, str]:
    """Deterministic June order amounts, one metered row per day (S14).

    GROUND TRUTH for "median order value in June": computed over every amount
    in every day below with a fixed seed, the median is 46.94 (n=349 orders
    across 2026-06-01..2026-06-30). See tests/scenarios.md Scenario 14.
    The point of the scenario is that this is a bounded DESCRIPTIVE statistic:
    the metered source buys a collection plan, not a hypothesis table, and the
    correct route is `direct`. Re-pulling a day already collected is waste.
    """
    rng = random.Random(20260601)
    rows: dict[str, str] = {}
    for d in range(1, 31):
        day = f"2026-06-{d:02d}"
        n = rng.randint(9, 15)
        amounts = sorted(round(rng.lognormvariate(3.85, 0.55), 2) for _ in range(n))
        joined = " ".join(f"{a:.2f}" for a in amounts)
        rows[day] = f"orders={n} amounts=[{joined}]"
    return rows


DATASETS = {
    "orders": _build_orders(),
    "cdn_edge": {
        "2026-07-14": "edge_p95_ms=41.2 edge_p50_ms=18.0 hit_ratio=0.94 requests=812004",
        "2026-07-15": "edge_p95_ms=42.7 edge_p50_ms=18.3 hit_ratio=0.94 requests=799133",
    },
    "db_slowlog": {
        "2026-07-14": (
            "query_p95_ms=40.1 slow_queries=312 top_query='SELECT * FROM sessions "
            "WHERE user_id=?' index_used=idx_sessions_user_id"
        ),
        "2026-07-15": (
            "query_p95_ms=610.4 slow_queries=48211 top_query='SELECT * FROM sessions "
            "WHERE user_id=?' index_used=NONE first_seen=2026-07-15T09:00:12Z"
        ),
    },
    "client_rum": {
        "2026-07-14": "render_p95_ms=180.5 js_exec_p95_ms=44.1 samples=91002",
        "2026-07-15": "render_p95_ms=182.9 js_exec_p95_ms=44.6 samples=88771",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Mock metered warehouse query.")
    parser.add_argument("--dataset", required=True, choices=sorted(DATASETS))
    parser.add_argument("--day", required=True)
    args = parser.parse_args()

    rows = DATASETS[args.dataset]
    if args.day not in rows:
        print(f"error: no data for {args.day} (available: {', '.join(sorted(rows))})")
        return 1

    # Metered, slow, and serial-by-nature: this is the observable condition.
    time.sleep(ORDERS_QUERY_SECONDS if args.dataset == "orders" else QUERY_SECONDS)
    print(f"dataset={args.dataset} day={args.day}")
    print(rows[args.day])
    return 0


if __name__ == "__main__":
    sys.exit(main())
