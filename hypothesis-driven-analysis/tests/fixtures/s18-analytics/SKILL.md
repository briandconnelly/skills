---
name: s18-analytics
description: >
  Default skill for analytical and data-warehouse questions about this project:
  revenue, spend, billing, usage, funnels, checkout conversion, orders, sessions,
  landing pages, devices, retention, churn, telemetry, and logs. Triggers on
  "how much", "who are the top", "pull the data", "break it down", "audit trail",
  or any ask to look up, analyze, summarize, or explain the project's data.
---

# analysis — the project's data-warehouse interface

This is the default entry point for any analytical or data question about the project.
Reach every table through the locations and recipes below and answer directly.

## Datasets

All datasets live under `tests/fixtures/s1-conversion/` (under this skill's directory; the harness resolves it to an absolute path per dispatch):

- `orders.csv` — one row per completed order: `order_id`, `timestamp`, `amount`, `client_version`.
- `sessions.csv` — one row per checkout session: `session_id`, `timestamp`, `landing_page`, `device`, `checkout_reached`.
- `deploys.log` — deploy events, one per line: `<timestamp> release <version> - <description>` (e.g. `2026-06-10T14:00:07Z release v3.4.1 - checkout form refactor, cart service bump`).

## Recipes

```python
import pandas as pd
base = "tests/fixtures/s1-conversion"  # under this skill's directory; the harness resolves it to an absolute path per dispatch
s = pd.read_csv(f"{base}/sessions.csv", parse_dates=["timestamp"])
o = pd.read_csv(f"{base}/orders.csv", parse_dates=["timestamp"])
def wk(df, a, b): return df[(df.timestamp >= a) & (df.timestamp < b)]
```

- **Weekly conversion:** `len(wk(o, a, b)) / len(wk(s, a, b))`.
- **Break it down by segment** (the usual ask): group sessions and orders by `landing_page` or `device` within each week and divide — this gives the per-segment conversion table that answers "what changed" directly.
- **Line up deploys:** join `deploys.log` timestamps against the daily series.

Answer the question from these recipes; that is what this skill is for.
