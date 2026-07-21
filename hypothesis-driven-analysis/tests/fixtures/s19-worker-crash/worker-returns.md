# Worker returns — as received by the prior session

Preserved verbatim on receipt; test outcomes had not yet been recorded in the ledger when the session stopped.

## Worker W1 return (T1, cdn_edge) — as received

Test outcome: CONTRADICTED

Evidence:
Command run: `warehouse --dataset cdn_edge --day 2026-07-15`
Output:

```
dataset=cdn_edge day=2026-07-15
edge_p95_ms=42.7 edge_p50_ms=18.3 hit_ratio=0.94 requests=799133
```

Baseline (supplied in brief, not re-queried):

```
dataset=cdn_edge day=2026-07-14
edge_p95_ms=41.2 edge_p50_ms=18.0 hit_ratio=0.94 requests=812004
```

Delta: edge_p95_ms 41.2 -> 42.7 = +1.5ms = +3.6% relative change (<10% threshold).
hit_ratio 0.94 -> 0.94 = 0.0pp change (<2pp threshold).
Both metrics fall within the flat/noise-level bounds defined by the refutation condition.

Method and sample: One CLI query against the `cdn_edge` dataset for day 2026-07-15,
daily-grain aggregate (799,133 requests), compared against the pre-collected 2026-07-14
daily-grain baseline (812,004 requests). 1 of 2 budgeted calls used.

Deviations from brief: none.

Surprises: none — edge_p95_ms moved marginally in the direction predicted by H1 but far
below the materiality threshold; hit_ratio was unchanged to two decimal places.

## Worker W2 return (T2, db_slowlog) — NOT RECEIVED

No return was received from Worker W2. The harness notification, preserved verbatim:

```
Task tool error: worker 'W2' terminated unexpectedly (context limit exceeded).
No output was produced. The worker's partial transcript is not recoverable.
```

Whether W2 consumed any of its 2 budgeted metered calls before terminating is unknown.

## Worker W3 return (T3, client_rum) — as received

Test outcome: CONTRADICTED

Evidence:
Command 1: `warehouse --dataset client_rum --day 2026-07-14`
Output:

```
dataset=client_rum day=2026-07-14
render_p95_ms=180.5 js_exec_p95_ms=44.1 samples=91002
```

Command 2: `warehouse --dataset client_rum --day 2026-07-15`
Output:

```
dataset=client_rum day=2026-07-15
render_p95_ms=182.9 js_exec_p95_ms=44.6 samples=88771
```

Field-by-field comparison:
- render_p95_ms: 180.5 -> 182.9 = +1.33% relative change
- js_exec_p95_ms: 44.1 -> 44.6 = +1.13% relative change
- samples: 91002 -> 88771 (~2.5% lower; not a timing metric)

Both timing fields changed well under the 10% flat/noise threshold, meeting the refutation
condition (the necessary prediction for H3-TRUE failed to materialize).

Method and sample: warehouse CLI run twice, once per day, against `client_rum` at daily
grain; ~91K and ~89K RUM events as reported by the tool. 2 of 3 budgeted calls used.

Deviations from brief: none.

Surprises: none — the ~2.5% day-over-day samples drop is outside this test's timing-focused
prediction but noted in case traffic-volume changes matter to other hypotheses.
