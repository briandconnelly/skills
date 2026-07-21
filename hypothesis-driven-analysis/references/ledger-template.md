# Investigation Ledger Templates

Create the ledger at Plan time, before any planned data is collected.
Create means write: the ledger exists as a file before the first planned collection runs, so the preregistration leaves a record the transcript can verify — a ledger first materialized in the final report is a reconstruction, not a preregistration.
Keep it in scratch space by default, named recognizably (e.g. `ledger.md`); put it in the project directory when the user wants a durable artifact.
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

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | ... | ... | ... | ... | T1 | ... |
| H2 | descriptive (estimand: ...) | ... | ... | ... | ... | T2 | ... |

The necessary-prediction column is what makes status mechanically derivable: declare it at Plan time, and only its failure under an adequate test can mark the hypothesis `REFUTED`.
Every row must carry one, and it must be able to fail — it follows from the hypothesis's own mechanism, and you could observe it failing while the rest of the data stays as it is.
The explanation also names the exact effect it explains: a necessary prediction refutes only at the scope the claim states, so "the deploy caused the observed step" is refutable by timing, while a system-wide "the deploy regressed the cache layer" is broader than any single prediction can refute.
A row whose necessary prediction cannot fail is not a testable hypothesis: move it to Limitations as an open possibility rather than leaving it in the table to sit `UNRESOLVED` forever while competing for "best supported".
Each row declares its claim as `causal`, `descriptive`, or `data-artifact`, and a descriptive row names the estimand its prediction is about.
A `data-artifact` row claims the records themselves are wrong — missing, miscounted, mis-instrumented — and per the skill it can only be `REFUTED` by a check that actually probed coverage and missingness.
The claim column is what the status rules read: a `causal` row cannot be `REFUTED` by a contrast whose design does not identify it, and a `descriptive` row cannot be added after Plan time.

Hypotheses added after seeing data get the label `retrospective` in the id column (e.g. `H4 (retrospective)`).
A retrospective hypothesis can only be best supported on evidence that did not inform it — a held-out slice, a later window, a source you had not looked at, or a new measurement.
It need not come from a different system: a slice of the same source you had not seen when you framed the hypothesis qualifies, because what disqualifies evidence is having already shaped the guess.
Re-running a fresh statistic over the same records that suggested it is a new query, not new evidence; if no qualifying evidence exists, it stays exploratory and is reported as an open possibility.
Inspecting inventory, schemas, provenance, and coverage does not make a hypothesis retrospective; inspecting a cause-outcome relationship does.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | ... | ... | ... |

Every evidence cell in Tests references a source id, so results stay reproducible against the exact data used.

## Data Validity

- Collection method: <how each source is produced>
- Coverage matrix: <row counts at the crossed grain the analysis uses — every time bucket compared × every segment appearing in a denominator, contrast, or hypothesis. Separate per-period and per-segment totals do not substitute: a hole in one segment on a few days hides between them.>
- Field population: <the populated rate of each field relied on, at that same crossed grain; a field present for only part of the data is a coverage gap, not a null problem>
- Coverage baseline: <the expected schedule or independent denominator the matrix was compared against; if neither exists, record coverage as unverifiable rather than clean>
- Known instrument failures: <dashboards, exporters, sampling quirks>
- Source completeness semantics: <per source whose absent records bear on any conclusion: what an absent record means — event absent, event unrecorded, or export incomplete — and the evidence for that reading; `UNKNOWN` when no evidence exists or the evidence does not discriminate between the live readings — the source's own missingness pattern never does — which blocks inferring event status or any directional missingness claim from that source's absent records>
A source declared `UNKNOWN` is written in the machine-checkable per-source form `<source-id>: UNKNOWN — <why no evidence discriminates the live readings>`, one declaration per source, so a scorer can confirm the declaration without judging the prose.
- Sensitivity checks performed: <intervals computed and known positives surfaced — fresh draws per trial or independent data, never intervals recomputed from one fixed shifted copy — plus detection limits>

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | ... | ... | NOT_TESTED | S1 ... |

One row per test-hypothesis pair: a test that bears on several hypotheses gets one row each, because a discriminating observation can be `CONSISTENT` for one hypothesis and `CONTRADICTED` for another.
Outcomes: `NOT_TESTED` → `CONSISTENT` / `CONTRADICTED` / `NON_DISCRIMINATING`.
A `NON_DISCRIMINATING` outcome states why (underpowered, wrong grain, no known-positive check available) and any detection limit.
A `CONTRADICTED` outcome that refutes on a positive or distributional contradiction — an observed pattern, timing, or count offered as failing a distributional prediction — records the adequacy bound the skill requires (SKILL.md, Data) beside the outcome, in the machine-checkable form `adequacy: <rate> ± <uncertainty> (variants: <range>)`.
A deterministic prediction a true instance could never fail is exempt and records no bound.

## Amendments

- <date>: <what changed and why — new data request, new hypothesis, revised budget>
- <date>: T<id> outcome superseded: <old> → <new>, because <reason — e.g. unit error found during spot-verification>

An amendment that supersedes a test outcome names the test id, the replacement outcome, and the reason; hypothesis status derives from each test's latest effective outcome.

## Conclusion

- Answer: <answer first>
- Best supported: <explanation(s), with the discriminating evidence>
- Per-hypothesis summary — `status` is `REFUTED` or `UNRESOLVED` and nothing else:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | <the discriminating evidence, or why nothing settled it> |

  "Best supported" is conclusion language, not a status: it belongs in `basis`, as the worked example shows.
- Limitations: <named unresolved alternatives, data gaps, associative-only claims>
```

## Mini Route Template

One paragraph, inline in the conversation or scratch space:

```markdown
Claim: <the single stated claim>.
Prediction: <what I expect to observe if it holds / if it fails>.
Probe(s): <the bounded read-only probes that settle it — as many as it takes; a probe count is a budget, not a hypothesis>.
Outcome: <CONSISTENT / CONTRADICTED / NON_DISCRIMINATING, with evidence pointer>.
Answer: <conclusion, with any limitation>.
```

## Costly Collection Plan Template

Written before any costly pull, on whatever route selected it — including `direct`.
It adds no hypotheses; on the full route these fields are already carried by Problem and Plan, so do not duplicate them.

```markdown
Serves: <the decision or output this pull is for>.
Source and action: <the exact system, query, or endpoint, and what is run against it>.
Cheapest adequate: <why this pull, and not a cheaper one, is the least that answers it>.
Budget: <maximum spend in the metered unit — queries, rows, dollars, wall-clock>.
Authorization: <the grant covering this action, per the authorization gate — or BLOCKED, and what is needed>.
Stop / re-pull condition: <what would make this enough, and what would justify paying again>.
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

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Tuesday deploy regressed the cache layer, causing the observed p95 step | p95 step aligns with deploy timestamp; cache hit rate drops | p95 shift precedes deploy or hit rate flat | the p95 step must not precede the deploy — a deploy cannot cause a step that happened before it | T1 | deploy log, cache metrics |
| H2 | causal | Traffic mix shifted toward uncached endpoints | share of cache-miss routes rises independently of deploy | route mix stable across the step | the cache-miss route share must rise at the step | T2 | request logs by route |
| H4 (retrospective) | causal | Upstream payment API slowdown drives most of the added latency | /checkout spans show payment call dominating added latency | added latency spread across spans | the payment span must account for the majority of added p95 — "drives most of" is false otherwise | T4 | trace spans |
| H5 | data-artifact | The 07-07 21:00–23:00 `/checkout` log shortfall is a logging-pipeline gap, not a traffic drop | an independent request counter shows normal traffic in that window | the independent counter also shows a dip | the load balancer's counter must not dip when the logs do | T6 | LB request counter |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | deploy log `deploys/2026-07-07.log` | 2026-07-08 09:00Z | full day |
| S2 | cache metrics dashboard export, 5-min grain | 2026-07-08 09:05Z | 10% request sample |
| S3 | raw request logs `logs/checkout-2026-07-0{6,7,8}.jsonl.gz` | 2026-07-08 09:10Z | all rows; user-agent field populated for only ~30% of rows |
| S4 | trace spans, Jaeger query `/checkout` 07-06..07-08 | 2026-07-08 10:40Z | 1% trace sampling |
| S5 | load balancer request counter, 1-hour grain | 2026-07-08 11:15Z | independent of the logging pipeline — used as the coverage baseline |

## Data Validity

- Collection method: dashboard aggregates from the metrics pipeline; raw request logs and traces available.
- Coverage matrix: the analysis compares hours × route, so request-log rows were counted at that grain across 07-06..07-08. Every hour carries 3.9k–4.4k rows on every route, except `/checkout` on 07-07 21:00–23:00, which carries ~1.2k/hour — a shortfall confined to one route and three hours. Per-day totals (11.9M, 11.7M, 11.8M) and per-route totals both look healthy and would have hidden it, which is exactly why they are not the check.
- Field population: at the same hour × route grain, `route` and `latency_ms` are 100% populated throughout; `user_agent` is populated for ~30% of rows overall and drops to ~4% on mobile routes after 07-07 12:00 — a coverage gap, not a null problem, and the reason T3 below cannot discriminate.
- Coverage matrix, trace spans (S4): H4/T4 contrasts payment spans against other spans, so span type is a segment the analysis uses and needs its own matrix at hour × span-type. Every hour carries 40–70 sampled traces per span type across both days, with `span_name` and `duration_ms` 100% populated — no hole, so T4's span breakdown rests on checked coverage rather than on S4's global "1% sampling" note, which describes the sample rate and says nothing about whether the sample is evenly spread.
- Coverage baseline: compared against the load balancer's independent request counter, which shows no dip in the 07-07 21:00–23:00 window — so the shortfall is in the logging pipeline, not in real traffic. Promoted to H5 (see Amendments) rather than analyzed as a traffic change.
- Known instrument failures: dashboard p95 is computed over 5-minute windows and hides sub-window spikes.
- Source completeness semantics: S3 request logs — an absent row means the logging pipeline dropped it, not that no request occurred (established by the independent LB counter, S5/T6); S2 dashboard export and S4 trace spans — designed samples (10% and 1%, stated in Sources), so absence means unsampled by design.
S1: UNKNOWN — no completeness contract checked, so no conclusion infers event status or bias direction from its absence.
S5: UNKNOWN — same.
- Sensitivity checks performed: dashboard step cross-checked against raw logs (known positive: the step appears in both), so the dashboard is not blind to steps of this size.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | p95 step within 10 min of deploy; hit rate drops ≥5pp | align deploy log with metrics | CONTRADICTED | step at 09:12, deploy at 14:30; hit rate flat (S1, S2 §3) |
| T2 | H2 | cache-miss route share rises ≥10pp at the step | group logs by route across the step | CONSISTENT | miss-route share 22%→41% at 09:10 (S3 §4) |
| T3 | H2 | new client version drives the miss-route traffic | group miss-route traffic by user agent | NON_DISCRIMINATING | user-agent populated for only ~30% of rows (Sources S3); cannot detect a shift smaller than ~25pp (S3 §5) |
| T4 | H4 | payment span accounts for majority of added p95 | compare span breakdown across the step | CONTRADICTED | added latency distributed across spans (S4 §2); adequacy: a true payment-dominated split fails this in fewer than 1 run in 20 at the observed span counts (variants: any split with payment > 50%) |
| T5 | H2 | reweighting Monday's per-route latencies by Tuesday's route mix reproduces ≥80% of the observed p95 increase | counterfactual reweighting on request logs | CONSISTENT | reweighted p95 +96ms vs observed +110ms (S3 §6) |
| T6 | H5 | LB counter flat while log volume dips 07-07 21:00–23:00 | compare log rows/hour against the LB's independent counter | CONSISTENT | LB counter steady at ~4.1k/hour through the window (S5 §1) while logs carry ~1.2k/hour (S3 §7) — the gap is in logging, so those hours are excluded from the rate denominators |

## Amendments

- 2026-07-08: added H4 (retrospective) after T2 evidence showed latency also rose on some cached routes. Promoting it would need evidence that did not inform it; T4 uses trace spans (S4), a source untouched when H4 was framed, so it qualifies — a second statistic over the same request logs would not have.
- 2026-07-08: added H5 after the coverage matrix showed a `/checkout` log shortfall on 07-07 21:00–23:00. Not retrospective: it came from inspecting coverage, not a cause-outcome relationship.

## Conclusion

- Answer: the p95 increase is associated with a traffic-mix shift toward uncached routes starting 09:10 Tuesday; the deploy is not implicated, so do not roll back.
- Best supported: H2, via T2 and T5 (discriminating: the step co-occurs with the route-mix shift, precedes the deploy, and the mix shift reproduces most of the observed increase under reweighting).
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | REFUTED | necessary timing prediction failed under an adequate test, T1 |
  | H2 | causal | UNRESOLVED | best supported (T2, T5 CONSISTENT) |
  | H4 (retrospective) | causal | REFUTED | its necessary majority-of-added-latency prediction failed under T4, on trace spans that had not informed it |
  | H5 | data-artifact | UNRESOLVED | best supported for the coverage gap (T6 CONSISTENT) |
- Limitations: what drove the traffic shift is unresolved (T3 NON_DISCRIMINATING — user-agent coverage too sparse); the 07-07 21:00–23:00 hours are excluded from rate denominators per H5/T6, which does not change the conclusion but narrows the window the step is measured over; the claim is associative — the route mix was not assigned by anything independent of latency, and no intervention was run, so "the mix shift is associated with the increase" is as far as this data reaches.
```
