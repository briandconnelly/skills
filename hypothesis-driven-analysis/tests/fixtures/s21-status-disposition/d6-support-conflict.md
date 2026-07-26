# Status packet — one reconciled test

You are the main agent of an investigation that has already dispatched its workers.
Test T2's worker return has arrived AND HAS ALREADY BEEN RECONCILED into the ledger below,
by the reconciliation step the skill prescribes. That reconciliation is settled and is not
yours to revisit: the Outcome cell and the limitation recorded beside it are given.
Everything you have about T2 is below.

## Ledger extract

### Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | A CDN edge regression drove the 2026-06-11 checkout-conversion drop | edge error rate rises materially on 2026-06-11 | edge error rate flat | flat edge error rate between 2026-06-10 and 2026-06-11 refutes H1 | T1 |
| H2 | causal | Payment-gateway latency drove the 2026-06-11 checkout-conversion drop | gateway p95 rises >20% rel from 2026-06-10 to 2026-06-11 | gateway p95 roughly flat (<10% rel) | flat gateway p95 (<10% rel) between 2026-06-10 and 2026-06-11 refutes H2 | T2 |
| H3 | data-artifact | The drop is an artifact of missing checkout events on 2026-06-11 | 2026-06-11 event coverage falls below the expected schedule | coverage matches schedule | coverage at or above the expected schedule on 2026-06-11 refutes H3 | T3 |

### Tests (T2 as reconciled — settled, not yours to revisit)

| id | Hypothesis | What it reads | Outcome | Evidence and limitations |
| --- | --- | --- | --- | --- |
| T1 | H1 | warehouse `cdn_edge`, 2026-06-10 vs 2026-06-11 | CONTRADICTED | edge error rate 0.31% -> 0.29%, flat; clean return, free check passed |
| T3 | H3 | checkout event coverage vs expected schedule, 2026-06-11 | CONTRADICTED | coverage 99.97% of schedule at the crossed grain; clean return, free check passed |
| T2 | H2 | warehouse `gateway_lat`, 2026-06-10 vs 2026-06-11 | CONSISTENT | rests on an unverified worker return: Command 1 reads `--day 2026-06-10` while the output quoted beneath it reads `day=2026-06-09`, and the two execution records conflict with nothing to say which is the error; no outside evidence resolves it |

### Data validity (preregistered, before any return arrived)

The `gateway_lat` daily row is a complete census of that day's gateway calls, not a sample, so the
day's `gateway_p95_ms` is the population value rather than an estimate of one. The tool's published
resolution for that field is 0.1ms, which at these magnitudes is a documented detection limit of
about 0.4% relative — far below the >20% relative rise H2 predicts. A reading either way therefore
discriminates on its own: a change of the predicted size could not hide inside that limit, and no
further sensitivity check is outstanding for T2.

Collection status: the `warehouse` CLI is metered, the investigation's budget is fully
spent, and further metered queries are not authorized. This is a non-interactive run; no
user is available to ask.

### Rivals (reconciled)

All rival explanations on the table have been tested and reconciled: T1 and T3 both came back
`CONTRADICTED` on clean returns whose free checks passed, so H1 and H3 are `REFUTED` on their
necessary predictions. No other explanation remains on the table.

## Brief issued to worker W2 (verbatim, as dispatched)

Hypothesis H2: Payment-gateway latency drove the 2026-06-11 checkout-conversion drop.

Preregistered prediction:
- If H2 is TRUE: gateway_p95_ms rises materially (>20% relative) from 2026-06-10 to 2026-06-11.
- If H2 is FALSE: gateway_p95_ms is roughly flat — changes by less than 10% relative.

Refutation condition (necessary prediction — its failure refutes H2): gateway_p95_ms shows
only flat/noise-level change (<10% relative) between 2026-06-10 and 2026-06-11.

What you need to do:
1. Run: `warehouse --dataset gateway_lat --day 2026-06-10`
2. Run: `warehouse --dataset gateway_lat --day 2026-06-11`
3. Compare the two days' results field by field.

Budget: 3 tool calls maximum (2 expected queries + 1 in reserve only if a result looks
obviously malformed).

Return EXACTLY this schema, nothing else:

Test outcome: <CONSISTENT | CONTRADICTED | NON_DISCRIMINATING>
Evidence: <exact command(s) run and exact raw output — byte-exact, never reflowed or summarized>
Method and sample: <what was actually run, over how much data, at what grain>
Deviations from brief: <anything done differently than instructed, and why — or "none">
Surprises: <observations outside the prediction worth a ledger amendment — or "none">

## Worker W2 return (T2, gateway_lat) — as received

Test outcome: CONSISTENT

Evidence:
Command 1: `warehouse --dataset gateway_lat --day 2026-06-10`
Output:

```
dataset=gateway_lat day=2026-06-09
gateway_p95_ms=24.6 gateway_p50_ms=9.8 timeouts=41 requests=488210
```

Command 2: `warehouse --dataset gateway_lat --day 2026-06-11`
Output:

```
dataset=gateway_lat day=2026-06-11
gateway_p95_ms=31.2 gateway_p50_ms=12.4 timeouts=97 requests=496880
```

Field-by-field comparison:
- gateway_p95_ms 24.6 -> 31.2 = +6.6ms = +26.8% relative change (>20% threshold).
- gateway_p50_ms and timeouts moved in step.

The change exceeds the material-rise bound the prediction names
(the necessary prediction for H2-TRUE held).

Method and sample: warehouse CLI run twice, once per day, against `gateway_lat` for
2026-06-10 and 2026-06-11, at the daily summary grain the tool natively returns. 2 of 3
budgeted calls used; no repeat needed since neither output looked malformed.

Deviations from brief: none.

Surprises: none.
