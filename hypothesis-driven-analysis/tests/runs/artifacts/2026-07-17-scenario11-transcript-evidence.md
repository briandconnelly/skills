# S11 (mini route) — transcript evidence

Grounds the S11 rows in `tests/scenarios.md` (Second and Fifth waves).
Run keys, hashes, and instrument validation: `2026-07-17-transcript-evidence-corpus.md`; full per-run manifests: `2026-07-17-transcript-evidence-manifests.md`.

## Scope — the two runs exercised different routing-table versions

| Run key | Wave | Date (UTC) | Model | Routing text exercised | Recorded score |
| --- | --- | --- | --- | --- | --- |
| s11-with-skill | Second | 2026-07-16 | sonnet | pre-rewrite table | 3/3 |
| s11-rerun | Fifth | 2026-07-17 | unrecorded in transcript; run log says Opus 4.8 | current (rewritten) table | 3/3 |

The Fifth-wave heading's carry-over claim ("S11 and S12 carry over from the old table unchanged") is a claim about these two runs jointly; each is evidenced separately below, and the model difference is why the rerun is weaker evidence of text-followability (as the run log already notes).

## Machine-checked counts and facts

| Run | Tool calls | Bash | Read | Write | Result statuses | Ledger-structure predicate matches in output |
| --- | --- | --- | --- | --- | --- | --- |
| s11-with-skill | 5 | 3 | 2 | 0 | 5 ok | 0 |
| s11-rerun | 4 | 2 | 2 | 0 | 4 ok | 0 |

Both counts match the recorded cells (5 and 4).
Neither run wrote a file; each emitted its mini-ledger in the reply.
Neither run's assistant text matches the full-route ledger-structure predicate `^\| H[0-9]|^#+ +Hypotheses|^#+ +(Sources|Tests|Amendments)\b` (the predicate fires 8 times on the s12-rerun transcript, so the zeros are a working instrument's zeros) — "no hypothesis table, no Sources/Tests/Amendments sections" is machine-checked over the complete output surface.
Each run's Reads are `SKILL.md` and `references/ledger-template.md`; each run's Bash calls target only `fixtures/s11-mini/checkout_latency.csv` (one orientation/coverage command, one computation; the 07-16 run used a third Bash for a second computation pass).
Both runs' outputs contain the measured `392.2` and the literal `20 of 24 hours` coverage caveat.

## Verbatim testimony behind the recorded judgments

**s11-with-skill routed mini on the claim/assertion distinction and recorded the mini ledger** (final text):

> Single stated non-causal claim ("p95 exceeded 500ms yesterday"), testable with at most two bounded read-only probes against a local CSV — no causal claim, no costly collection. That's an exact match for the `mini` route (not `direct`, since it requires computing a statistic and checking data coverage rather than a pure lookup; not `full`, since there's one claim and no competing causal explanations needed).

```
Claim: checkout p95 latency exceeded 500ms on 2026-07-15.
Prediction: if true, quantile(latency_ms, 0.95) > 500 over that day's requests; if false, ≤ 500.
Probe(s): (1) orient — load CSV, check schema/coverage/nulls/dupes; (2) compute p95 (and p50/p99/max as context).
Outcome: CONTRADICTED. n=1200 one-minute-interval requests, 2026-07-15T00:00–19:59Z, no nulls, no duplicate request_ids.
```

with the unprompted coverage caveat (exact source lines, wrapped as in the ledger):

```
  Limitation: the file covers only 00:00–19:59Z (20 of 24 hours) for 2026-07-15; the last ~4 hours of the day
  are absent from this fixture, so the claim cannot be fully verified for the entire calendar day, only for the
  covered window.
```

Note the route rationale includes an effort clause ("requires computing a statistic … rather than a pure lookup") alongside the claim clause — the "right route, partly for the effort reason" reading that led `tests/scenarios.md` to add the score-the-reasoning caution for this scenario.

**s11-rerun, on the current table, routed mini on the claim distinction alone** (final text):

> **1. ROUTE:** `mini`. Someone has asserted a specific claim with a truth value that will be acted on (p95 > 500ms yesterday), and it is a single non-causal claim with no rival explanation competing for it — the skill's routing section names this exact case ("Someone says p95 exceeded 500ms yesterday") as earning a prediction, a probe, and a recorded outcome.

```
Claim: checkout p95 latency exceeded 500ms on 2026-07-15.
Prediction: if true, the 95th percentile of latency_ms over that day's requests is > 500ms; if false, p95 <= 500ms.
Probe(s): (1) confirm all rows fall on 2026-07-15 and latency_ms is fully populated (coverage/validity check); (2) compute p95 of latency_ms over all rows.
Outcome: CONTRADICTED — p95 = 392.2ms (nearest-rank and linear-interp agree); only 14 of 1200 rows (~1.2%) exceed 500ms; max = 708.7ms.
```

It reproduced the coverage caveat unprompted and quantified what the missing window would need to contain to flip the answer ("roughly 58+ of the ~240 missing minutes would need to exceed 500ms (versus 14 such minutes across the entire observed 20 hours)").

## Reconciliation with the Results tables

Both rows' counts match as recorded, and both runs' correct answer (p95 392.2 ms, claim false) is quoted from output rather than carried from the scorer summary.
The route-*reasoning* quality distinction between the two runs (effort-tinged vs claim-only rationale) is scorer judgment; the rationales are now on the record for it.
