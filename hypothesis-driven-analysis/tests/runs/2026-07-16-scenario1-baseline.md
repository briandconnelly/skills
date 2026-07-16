# Scenario 1 — Baseline Scoring

Date: 2026-07-16
Run: baseline without the skill. Model: Sonnet. Fixture: `tests/fixtures/s1-conversion/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Ledger with ≥2 candidate explanations plus a data-validity check before analysis queries | FAIL | No ledger; began querying immediately. |
| 2 | Each hypothesis has a preregistered prediction (if true AND if false) | FAIL | No hypotheses stated before the data was examined. |
| 3 | Deploy hypothesis dismissed only by a discriminating test outcome | PASS | "Device-level conversion doesn't show a step change tied to that specific date, and the summer-sale effect alone explains the gap." |
| 4 | Mobile undercount caught by a validity check or stated as a limitation | PASS | Caught the 06-13/06-14 anomaly ("orders counts exceed checkout_reached counts — impossible if every order requires a checkout session") — but misattributed the mechanism to the v3.4.1 deploy's tracking rather than analytics undercounting mobile sessions. |
| 5 | Conclusion names best-supported explanation, associative language, lists remaining alternatives | FAIL | Correct explanation named, but stated flatly ("It is not a product regression, deploy-caused bug, or degradation in existing traffic quality") with no remaining alternatives and no associative hedge. |
| 6 | No queries outside the plan without a ledger amendment | FAIL | No plan exists, so the constraint is vacuous. |

Total: 2/6.

Conclusion correctness: **correct** — identified `/lp/summer-sale` composition dilution as the driver.
Cost: 8 tool calls, ~36.3k subagent tokens, 86s.

Note: the baseline reaches the right substantive answer and catches the planted validity trap. Its failures are all process-shaped (no ledger, no preregistration, unhedged conclusion), which is what the skill is meant to add.
