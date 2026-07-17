# Scenario 5 — Post-peek hypothesis, Baseline Scoring (corrected prompt)

Date: 2026-07-16
Run: baseline without the skill, at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s5-conversion-payment/`.
Prompt: the corrected S5 prompt — data directory named, schema and errors file not mentioned.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The new explanation is appended as a `retrospective` amendment with a reason | FAIL | No ledger; the swiftpay spike and the tracking gap are presented as "two secondary findings". |
| 2 | It is declared best supported only after a fresh discriminating test | PASS (vacuous) | Neither secondary finding was claimed as the driver of the drop. |

Total: 1/2.

Conclusion correctness: **correct on the headline** — `/lp/summer-sale` dilution, ~81% of the drop.
Cost: 12 tool calls, ~49.0k subagent tokens, 184s.

## Two untested causal claims

The baseline found both planted signals — including the `orders > checkout_reached` gap on 6/13–14, which it caught unprompted, as the S1 baseline also did. It then explained both by asserting mechanisms it never tested:

1. "This looks like the form refactor broke the `checkout_reached` analytics event for a subset of sessions" — attributing the gap to the 6/10 `v3.4.1` deploy. The gap appears on 6/13–14 only, three days later; the ground-truth cause is a mobile-session dropout in `sessions.csv`, unrelated to any deploy.
2. "a real reliability regression introduced by the 'cart service bump'" — attributing the swiftpay error spike to the same deploy, and recommending the payments team investigate. The with-skill run tested this and refuted it: swiftpay order volume was flat (48 → 49) straight through the error surge.

Both claims are plausible, fluent, and wrong about mechanism. Both would have dispatched engineers at a deploy that did not cause either symptom. This is the failure mode the skill exists to prevent, and it is the clearest baseline-vs-treatment contrast the suite has produced: same data, same two findings, and the difference is whether the mechanism was tested or narrated.
