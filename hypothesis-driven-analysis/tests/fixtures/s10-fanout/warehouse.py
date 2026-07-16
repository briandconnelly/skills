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
Usage: warehouse.py --dataset {cdn_edge,db_slowlog,client_rum} --day YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import sys
import time

QUERY_SECONDS = 18.0
"""Deliberate per-query latency; the whole point of the fixture."""

DATASETS = {
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
    time.sleep(QUERY_SECONDS)
    print(f"dataset={args.dataset} day={args.day}")
    print(rows[args.day])
    return 0


if __name__ == "__main__":
    sys.exit(main())
