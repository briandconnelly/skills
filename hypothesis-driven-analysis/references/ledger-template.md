# Investigation Ledger Templates

Create the ledger at Plan time, before any planned data is collected.
Keep it in scratch space by default; put it in the project directory when the user wants a durable artifact.
The ledger is append-only where integrity matters: preregistered predictions and amendment entries are immutable once written.
A test entry's outcome and evidence fields are the only sanctioned in-place updates: they transition once from `NOT_TESTED` to a terminal value when the test runs, and any later revision requires a dated amendment instead of an edit.

## Full Route Template

```markdown
# Investigation: <one-line question>

## Problem

- Decision informed: <what will be done differently depending on the answer>
- Falsifiable question: <the question, scoped to population, timeframe, units>
- Success criteria: answered means <observable condition>
- Stop condition: <precommitted criterion for concluding or stopping>
- Effort budget: <tool calls | queries | wall-clock — pick one and a number>

## Hypotheses

| id | Candidate explanation | Prediction if true | Prediction if false | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- |
| H1 | ... | ... | ... | T1 | ... |
| H2 | ... | ... | ... | T2 | ... |

Hypotheses added after seeing data get the label `retrospective` in the id column (e.g. `H4 (retrospective)`) and cannot be best supported without evidence gathered after they were added.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | ... | ... | ... |

Every evidence cell in Tests references a source id, so results stay reproducible against the exact data used.

## Data Validity

- Collection method: <how each source is produced>
- Coverage: <row counts per period and per segment, compared across the periods being contrasted — a segment or period that is simply absent will not appear in a null/duplicate scan>
- Field population: <the populated rate of each field relied on, per period; a field present for only part of the data is a coverage gap, not a null problem>
- Known instrument failures: <dashboards, exporters, sampling quirks>
- Sensitivity checks performed: <known positives surfaced, detection limits>

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | ... | ... | NOT_TESTED | S1 ... |

One row per test-hypothesis pair: a test that bears on several hypotheses gets one row each, because a discriminating observation can be `CONSISTENT` for one hypothesis and `CONTRADICTED` for another.
Outcomes: `NOT_TESTED` → `CONSISTENT` / `CONTRADICTED` / `NON_DISCRIMINATING`.
A `NON_DISCRIMINATING` outcome states why (underpowered, wrong grain, no known-positive check available) and any detection limit.

## Amendments

- <date>: <what changed and why — new data request, new hypothesis, revised budget>
- <date>: T<id> outcome superseded: <old> → <new>, because <reason — e.g. unit error found during spot-verification>

An amendment that supersedes a test outcome names the test id, the replacement outcome, and the reason; hypothesis status derives from each test's latest effective outcome.

## Conclusion

- Answer: <answer first>
- Best supported: <explanation(s), with the discriminating evidence>
- Per-hypothesis summary: <one line per hypothesis, status REFUTED or UNRESOLVED derived from test entries>
- Limitations: <named unresolved alternatives, data gaps, associative-only claims>
```

## Mini Route Template

One paragraph, inline in the conversation or scratch space:

```markdown
Claim: <the single stated claim>.
Prediction: <what I expect to observe if it holds / if it fails>.
Probe(s): <at most two bounded read-only probes>.
Outcome: <CONSISTENT / CONTRADICTED / NON_DISCRIMINATING, with evidence pointer>.
Answer: <conclusion, with any limitation>.
```

## Estimation Route Template

```markdown
Goal: <the knowledge goal or decision the estimate informs>.
Estimand: <the quantity being estimated, precisely defined>.
Population: <who or what the estimate describes, over what period>.
Uncertainty method: <interval, resampling, or stated inability to quantify>.
Practical threshold: <the value at which the decision changes>.
Result: <estimate with uncertainty, compared against the threshold>.
Limitations: <coverage gaps, selection concerns, associative-only caveats>.
```

## Worked Example (full route, abridged)

```markdown
# Investigation: API p95 latency doubled on Tue 2026-07-07 — why?

## Problem

- Decision informed: roll back the Tuesday deploy, or leave it and fix elsewhere.
- Falsifiable question: what explains the p95 latency increase for /checkout between 2026-07-06 and 2026-07-08 (ms, per-request, US region)?
- Success criteria: answered means one or more explanations account for the observed increase and survive a discriminating test.
- Stop condition: conclude when no named unresolved alternative could reverse the rollback decision.
- Effort budget: 25 queries.

## Hypotheses

| id | Candidate explanation | Prediction if true | Prediction if false | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- |
| H1 | Tuesday deploy regressed the cache layer | p95 step aligns with deploy timestamp; cache hit rate drops | p95 shift precedes deploy or hit rate flat | T1 | deploy log, cache metrics |
| H2 | Traffic mix shifted toward uncached endpoints | share of cache-miss routes rises independently of deploy | route mix stable across the step | T2 | request logs by route |
| H4 (retrospective) | Upstream payment API slowdown drives most of the added latency | /checkout spans show payment call dominating added latency | added latency spread across spans | T4 | trace spans |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | deploy log `deploys/2026-07-07.log` | 2026-07-08 09:00Z | full day |
| S2 | cache metrics dashboard export, 5-min grain | 2026-07-08 09:05Z | 10% request sample |
| S3 | raw request logs `logs/checkout-2026-07-0{6,7,8}.jsonl.gz` | 2026-07-08 09:10Z | all rows; user-agent field populated for only ~30% of rows |
| S4 | trace spans, Jaeger query `/checkout` 07-06..07-08 | 2026-07-08 10:40Z | 1% trace sampling |

## Data Validity

- Collection method: dashboard aggregates from the metrics pipeline; raw request logs and traces available.
- Coverage: request-log rows are complete, but the user-agent field is populated for only ~30% of rows; the dashboard samples 10% of requests; traces sample 1%.
- Known instrument failures: dashboard p95 is computed over 5-minute windows and hides sub-window spikes.
- Sensitivity checks performed: dashboard step cross-checked against raw logs (known positive: the step appears in both) — dashboard artifact ruled out, so no artifact hypothesis was promoted.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | p95 step within 10 min of deploy; hit rate drops ≥5pp | align deploy log with metrics | CONTRADICTED | step at 09:12, deploy at 14:30; hit rate flat (S1, S2 §3) |
| T2 | H2 | cache-miss route share rises ≥10pp at the step | group logs by route across the step | CONSISTENT | miss-route share 22%→41% at 09:10 (S3 §4) |
| T3 | H2 | new client version drives the miss-route traffic | group miss-route traffic by user agent | NON_DISCRIMINATING | user-agent populated for only ~30% of rows (Sources S3); cannot detect a shift smaller than ~25pp (S3 §5) |
| T4 | H4 | payment span accounts for majority of added p95 | compare span breakdown across the step | CONTRADICTED | added latency distributed across spans (S4 §2) |
| T5 | H2 | reweighting Monday's per-route latencies by Tuesday's route mix reproduces ≥80% of the observed p95 increase | counterfactual reweighting on request logs | CONSISTENT | reweighted p95 +96ms vs observed +110ms (S3 §6) |

## Amendments

- 2026-07-08: added H4 (retrospective) after T2 evidence showed latency also rose on some cached routes; requires fresh evidence (T4).

## Conclusion

- Answer: the p95 increase is associated with a traffic-mix shift toward uncached routes starting 09:10 Tuesday; the deploy is not implicated, so do not roll back.
- Best supported: H2, via T2 and T5 (discriminating: the step co-occurs with the route-mix shift, precedes the deploy, and the mix shift reproduces most of the observed increase under reweighting).
- Per-hypothesis summary: H1 REFUTED (necessary timing prediction failed under an adequate test, T1); H2 UNRESOLVED and best supported (T2, T5 CONSISTENT); H4 REFUTED (its necessary majority-of-added-latency prediction failed under T4).
- Limitations: what drove the traffic shift is unresolved (T3 NON_DISCRIMINATING — user-agent coverage too sparse); the claim is associative, no intervention was run.
```
