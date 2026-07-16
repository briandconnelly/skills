# Scenario 5 — Post-peek hypothesis, Baseline Scoring

Date: 2026-07-16
Run: baseline without the skill. Model: Sonnet. Fixture: `tests/fixtures/s5-conversion-payment/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The new explanation is appended as a `retrospective` amendment with a reason | FAIL | No ledger; the swiftpay spike is presented as a "secondary, unrelated finding worth flagging". |
| 2 | It is declared best supported only after a fresh discriminating test | PASS (vacuous) | Did not claim swiftpay explained the conversion drop; kept it separate from the conclusion. |

Total: 1/2.

Conclusion correctness: **correct on the headline** — traffic-mix dilution from `/lp/summer-sale`.
Cost: 14 tool calls, ~45.6k subagent tokens, 178s.

**Unsupported causal claim (the substantive baseline failure).** On the swiftpay error spike the baseline asserted: "This begins ~18 hours after the v3.4.1 deploy... suggesting the refactor broke something in the swiftpay payment payload/integration", and escalated it to "merits urgent investigation". That mechanism was never tested. The with-skill run tested the same hypothesis and refuted it: order counts per provider *rose* across the boundary (northbank 83→88, swiftpay 48→49), and the error log has no join key to orders or sessions, so no lost conversion can be attributed to it. The baseline's recommendation would have sent someone chasing a refutable claim.
