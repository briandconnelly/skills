# Scenario 5 — Post-peek hypothesis, With-Skill Scoring

Date: 2026-07-16
Run: with the skill. Model: Sonnet. Fixture: `tests/fixtures/s5-conversion-payment/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The new explanation is appended as a `retrospective` amendment with a reason | **N/A — scenario invalid** | The payment explanation was preregistered as H1, not formed post-peek. Amendment behavior did appear for two genuine mid-course discoveries: "checkout_errors.csv... discovered in the fixture dir though not named in the task — logged as an amendment", and the metric-definition correction "logged as an amendment since it wasn't obvious until computed". |
| 2 | It is declared best supported only after a fresh discriminating test | PASS (vacuous) | H1 was REFUTED, never elevated. |

Total: 1/2 scoreable; assertion 1 untested.

Conclusion correctness: **correct** — traffic-mix shift; deploy and payment errors both refuted.
Cost: 12 tool calls, ~58.6k subagent tokens, 224s (vs baseline 14 calls / ~45.6k).

## Scenario defect — assertion 1 was not testable as written

The prompt names the schema, including `payment_provider`, so a competent agent forms the payment hypothesis at Plan time. It was duly preregistered as H1, which means the run never exercised post-peek labeling at all. To test what this scenario claims to test, the prompt must not name the column or the errors file, and the planted signal must only become reachable after the plan is written. Until then, the skill's `retrospective` rule is **unverified by evidence** — it was neither confirmed nor refuted here.

## What the run did demonstrate

- Amendments fired for real mid-course discoveries rather than silent scope creep.
- The metric definition was pinned before conclusions: only `checkout_reached / sessions` reproduces the stated 3.1%/2.5%; `orders / sessions` gives 2.75% and does not.
- The payment hypothesis was refuted on evidence (provider order counts rose; error volume 200 exceeds week-2 checkout_reached sessions 123; no join key exists), rather than asserted as the baseline did.
- Device mix was recorded `NON_DISCRIMINATING` as an independent driver because it is entangled with the landing-page effect — an accurate use of the vocabulary.
