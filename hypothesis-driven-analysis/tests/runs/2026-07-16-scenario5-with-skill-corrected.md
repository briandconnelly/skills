# Scenario 5 — Post-peek hypothesis, With-Skill Scoring (corrected prompt)

Date: 2026-07-16
Run: with the skill at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s5-conversion-payment/`.
Prompt: the corrected S5 prompt — the data directory named, but **neither `payment_provider` nor `checkout_errors.csv` mentioned**. Supersedes `2026-07-16-scenario5-with-skill.md`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The new explanation is appended as a `retrospective` amendment with a reason, not silently inserted as if preregistered | **PASS** | "in a non-interactive single pass I then continued directly into cross-period/cross-segment comparisons... Per the skill, that crosses the line from orientation into cause-effect inspection, so **every hypothesis below is labeled `retrospective`**"; recorded as an amendment. |
| 2 | It is declared best supported only after a fresh discriminating test | **PASS** | "I therefore ran additional fresh discriminating tests (reweighting counterfactual, hourly gap analysis, two-proportion z-tests, sensitivity check) after declaring the hypotheses, and the conclusion rests on those." |

**Total: 2/2.** Assertion 1 was untestable in the contaminated run; it is now tested and passes.

Conclusion correctness: **correct, and more complete than the baseline's**. Cost: 14 tool calls, ~72.9k subagent tokens, 356s (vs corrected baseline 12 calls / ~49.0k).

## The retrospective rule is no longer unverified

The old prompt named the schema, so the payment hypothesis got preregistered and the rule never fired. With the naming removed, the run hit the boundary honestly, disclosed crossing it, labeled all four hypotheses `retrospective`, and then earned its conclusion on tests run *after* the labels — which is exactly the sequence the rule prescribes.

## Where the skill beat the baseline outright

Both runs found the same two signals. They handled them differently:

| | Corrected baseline | With-skill |
| --- | --- | --- |
| Swiftpay error spike | "a real reliability regression introduced by the 'cart service bump'" — asserted, untested | **H2 REFUTED** on its necessary prediction (T2: swiftpay orders 48→49, flat despite errors at 47/day), with a sensitivity check confirming the test could have detected a drop |
| `orders > checkout_reached` gap | "the form refactor broke the `checkout_reached` analytics event" — asserted, wrong deploy (6/10) | **H3**, tested, quantified: gap on 6/13–14 only, zero on the other 12 days; "roughly 43% of the reported drop is a measurement artifact, not a real conversion decline" |
| Net conclusion | mix-shift explains ~81%; two loose causal claims left dangling | mix-shift ~81% **plus** artifact correction, then T5: after removing both, z≈0.05 — no real change at all |

The baseline shipped two untested causal claims that would have sent people after the wrong deploy. The skill run refuted one and quantified the other, then closed the loop with a joint test showing nothing was left to explain.

## Second with-skill catch of the planted defect — with the mechanism still wrong

The run found the artifact and got its *direction and magnitude* right. It did not identify its *mechanism*: the gap is caused by `sessions.csv` dropping ~40% of mobile sessions on 06-13/06-14, not by a logging deploy. The run attributed it to the v3.4.2 "logging only" release and noticed the story didn't quite fit — "onset lags the deploy by ~1.5 days rather than being instantaneous" — but preferred the deploy narrative anyway rather than treating the misfit as evidence against it.

So the coverage rule's tally on the new wording is **2 caught / 3 runs** (S1 rerun caught, S5 caught, S7-serial missed), against **0 / 3** on the old wording. Better, still not reliable, and in both catches the route was a cross-source count comparison rather than the per-segment coverage comparison the rule actually prescribes. Nobody has yet identified the defect as mobile-specific.

## Note on skill mutation during the run

`SKILL.md`'s Gates section was edited while this run was in flight. This scenario exercises routing, orientation, and status rules — not Gates — and the run cites post-`e55ba78` machinery throughout, so scoring is unaffected. Recorded because editing a skill under a live run is a methodology error regardless.
