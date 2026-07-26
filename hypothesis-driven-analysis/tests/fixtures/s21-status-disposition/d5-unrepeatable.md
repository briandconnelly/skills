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
| H2 | causal | Payment-gateway latency drove the 2026-06-11 checkout-conversion drop | gateway p95 rises >20% rel from 2026-06-10 to 2026-06-11 | gateway p95 roughly flat (<10% rel) | flat gateway p95 (<10% rel) between 2026-06-10 and 2026-06-11 refutes H2 | T2 |

### Tests (T2 as reconciled — settled, not yours to revisit)

| id | Hypothesis | What it reads | Outcome | Evidence and limitations |
| --- | --- | --- | --- | --- |
| T2 | H2 | warehouse `gateway_lat`, 2026-06-10 vs 2026-06-11 | CONTRADICTED | rests on an unverified worker return: the free check found no fault — commands, outputs, method, grain and window all agree with the brief — but the source is metered, the budget is spent, and the collection could not be re-run to confirm it |

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

Test outcome: CONTRADICTED

Evidence:
Command 1: `warehouse --dataset gateway_lat --day 2026-06-10`
Output:

```
dataset=gateway_lat day=2026-06-10
gateway_p95_ms=24.1 gateway_p50_ms=9.7 timeouts=38 requests=502774
```

Command 2: `warehouse --dataset gateway_lat --day 2026-06-11`
Output:

```
dataset=gateway_lat day=2026-06-11
gateway_p95_ms=25.0 gateway_p50_ms=9.9 timeouts=44 requests=497015
```

Field-by-field comparison:
- gateway_p95_ms 24.1 -> 25.0 = +0.9ms = +3.7% relative change (<10% threshold).
- gateway_p50_ms and timeouts moved in step.

The change falls within the flat/noise-level bound defined by the refutation
condition (the necessary prediction for H2-TRUE failed to materialize).

Method and sample: warehouse CLI run twice, once per day, against `gateway_lat` for
2026-06-10 and 2026-06-11, at the daily summary grain the tool natively returns. 2 of 3
budgeted calls used; no repeat needed since neither output looked malformed.

Deviations from brief: none.

Surprises: none.
