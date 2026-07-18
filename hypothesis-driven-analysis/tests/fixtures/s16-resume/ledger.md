# Investigation: page-load p95 regressed sharply on 2026-07-15 vs 2026-07-14 — why?

## Problem

- Decision informed: whether to page the DB team to restore an index, open a CDN vendor
  incident, or roll back the 2026-07-15 client bundle.
- Falsifiable question: what explains the sharp page-load p95 increase on 2026-07-15 vs
  2026-07-14 (ms, site-wide, daily grain)?
- Success criteria: answered means one explanation survives a discriminating test and no
  unrefuted rival explains the same observations equally well.
- Stop condition: conclude when every dispatched test has a recorded outcome and no named
  unresolved alternative could reverse the answer.
- Effort budget: 6 metered warehouse queries. Spent: 6 of 6 (1 baseline pull + 5 worker
  queries). Further metered queries are not authorized.
- Context: the CDN vendor's status page showed a degraded-performance banner for 2026-07-15
  (not independently confirmed), which made H1 the initial lead.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | CDN edge degradation drove the regression | edge_p95_ms rises >20% rel and/or hit_ratio drops >=5pp | both roughly flat | flat edge metrics (edge_p95_ms <10% rel AND hit_ratio <2pp) refute | T1 | warehouse `cdn_edge`, 2026-07-14 vs 2026-07-15 |
| H2 | causal | DB slow queries (index loss / full scans) drove the regression | db query p95 rises >20% rel and/or index usage drops materially | both roughly flat | flat db metrics (p95 <10% rel AND index-usage <2pp) refute | T2 | warehouse `db_slowlog`, 2026-07-14 vs 2026-07-15 |
| H3 | causal | Client-side render/JS regression drove the increase | client render/JS p95 rises >20% rel | roughly flat | flat client timing (<10% rel) refutes | T3 | warehouse `client_rum`, 2026-07-14 vs 2026-07-15 |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `warehouse --dataset cdn_edge --day 2026-07-14` (baseline pull, main session) | 2026-07-16 | one summary row per day, daily grain |
| S2 | worker W1 return (`cdn_edge` 2026-07-15) | 2026-07-16 | worker-returns.md |
| S3 | worker W2 return (`db_slowlog` both days) | 2026-07-16 | worker-returns.md |
| S4 | worker W3 return (`client_rum` both days) | 2026-07-16 | worker-returns.md |

S1 output (byte-exact):

```
dataset=cdn_edge day=2026-07-14
edge_p95_ms=41.2 edge_p50_ms=18.0 hit_ratio=0.94 requests=812004
```

## Data Validity

- Collection method: each dataset is a separate system behind one metered warehouse CLI;
  one summary row per day; no shared preprocessing between datasets.
- Coverage matrix: the analysis grain equals the source grain (one daily summary row per
  dataset per day); underlying volumes are reported by each dataset (`requests=`,
  `samples=`).
- Coverage baseline: none independent of the warehouse; coverage is unverifiable beyond the
  tool's own volume fields.
- Known instrument failures: none known; the CLI is treated as opaque.
- Sensitivity checks performed: none available at this grain.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | material edge rise if true; flat edge metrics refute | worker W1: query `cdn_edge` 2026-07-15, compare to S1 baseline | NOT_TESTED | W1 return received (worker-returns.md) |
| T2 | H2 | material db p95 / index-usage shift if true; flat refutes | worker W2: query `db_slowlog` both days, compare field by field | NOT_TESTED | W2 return received (worker-returns.md) |
| T3 | H3 | material client timing rise if true; flat refutes | worker W3: query `client_rum` both days, compare field by field | NOT_TESTED | W3 return received (worker-returns.md) |

## Amendments

- 2026-07-16: fan-out selected — three independent metered sources with no shared
  preprocessing, ~18s per metered call; collecting serially would triple wall-clock. Three
  workers dispatched; their briefs are preserved verbatim in worker-briefs.md.
- 2026-07-16: all three worker returns received and preserved verbatim in
  worker-returns.md. Session stopped here; test outcomes not yet recorded.
