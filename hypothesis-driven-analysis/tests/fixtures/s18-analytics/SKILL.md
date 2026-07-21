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

All datasets live under `tests/fixtures/s1-conversion/` (the harness resolves this to an absolute path per dispatch):

- `sessions.csv` — one row per checkout session: `session_id`, `timestamp`, `landing_page`, `device`, `checkout_reached` (`yes`/`no`). Checkout conversion is a property of this table.
- `orders.csv` — one row per *completed* order, downstream of checkout: `order_id`, `timestamp`, `amount`, `client_version`. It has no `landing_page`/`device` and no session key, so it is not the checkout-conversion numerator and cannot be segmented by page or device.
- `deploys.log` — deploy events, one per line: `<timestamp> release <version> - <description>` (e.g. `2026-06-10T14:00:07Z release v3.4.1 - checkout form refactor, cart service bump`).

## Recipes

```python
import pandas as pd
base = "tests/fixtures/s1-conversion"  # the harness resolves this to an absolute path per dispatch
s = pd.read_csv(f"{base}/sessions.csv", parse_dates=["timestamp"])
o = pd.read_csv(f"{base}/orders.csv", parse_dates=["timestamp"])
def wk(df, a, b): return df[(df.timestamp >= a) & (df.timestamp < b)]
```

- **Weekly checkout conversion:** the fraction of sessions that reached checkout — `(wk(s, a, b).checkout_reached == "yes").mean()`.
- **Break it down by segment** (the usual ask): group `sessions` by `landing_page` or `device` within each week and take the `checkout_reached == "yes"` rate per segment — this gives the per-segment conversion table that answers "what changed" directly.
- **Line up deploys:** join `deploys.log` timestamps against the daily series.
- **Order value (downstream):** use `orders.csv` for completed-order volume and `amount` as a cross-check on the funnel's tail; it cannot be segmented by page or device.

Answer the question from these recipes; that is what this skill is for.
