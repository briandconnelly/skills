# Scenario 5 — Post-peek hypothesis, With-Skill Scoring (corrected prompt)

Date: 2026-07-16
Run: with the skill at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s5-conversion-payment/`.
Prompt: the corrected S5 prompt — the data directory named, but **neither `payment_provider` nor `checkout_errors.csv` mentioned**. Supersedes `2026-07-16-scenario5-with-skill.md`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | The new explanation is appended as a `retrospective` amendment with a reason, not silently inserted as if preregistered | PASS (weakly) | "in a non-interactive single pass I then continued directly into cross-period/cross-segment comparisons... Per the skill, that crosses the line from orientation into cause-effect inspection, so **every hypothesis below is labeled `retrospective`**"; recorded as an amendment. But see below — a blanket label is disclosure, not discrimination. |
| 2 | It is declared best supported only after a fresh discriminating test | **FAIL on re-scoring** | "I therefore ran additional fresh discriminating tests (reweighting counterfactual, hourly gap analysis, two-proportion z-tests) after declaring the hypotheses" — every one of those ran over the same fixture records that generated the hypotheses. That is a fresh *query*, not fresh *evidence*. |

**Total: 1/2** (originally scored 2/2; corrected after a Codex adversarial review).

Conclusion correctness: **correct, and more complete than the baseline's**. Cost: 14 tool calls, ~72.9k subagent tokens, 356s (vs corrected baseline 12 calls / ~49.0k).

## Re-scored: the rule this run "passed" was too weak to pass

I originally scored this 2/2 and wrote that the `retrospective` rule was "tested at last and passes". A Codex adversarial review showed that conclusion was wrong, and the rule — as worded when this run executed — was doing nothing.

The old wording said a retrospective hypothesis "cannot be best supported without evidence gathered after they were added". *Gathered after* is a statement about **query order**. This run inspected cross-period relationships, wrote hypotheses that matched what it had just seen, then ran reweighting, hourly-gap, and z-tests over **the same fixture records** and presented those as the fresh evidence that earned its conclusion. Nothing independent was ever consulted; the records that suggested the hypotheses are the records that confirmed them. Re-running a statistic over data you have already stared at cannot protect against post-selection bias, because the selection already happened.

So the label was disclosure theater: honest about sequence, empty as protection. The run deserves credit for the honesty and none for the safeguard.

The rule now requires evidence that **did not inform** the hypothesis — a held-out slice, a later window, an independent source, or a new measurement — and says explicitly that a fresh statistic over the same records does not qualify. That wording has **not** been tested; this run predates it. S5 also needs a fixture redesign before it can test it (see below).

## S5 still cannot test what it claims

Codex also showed the scenario is incoherent with the skill's own orientation rule. The prompt withholds the filename `checkout_errors.csv`, but SKILL.md explicitly permits inspecting the source inventory before preregistering — so a *compliant* agent lists the directory, sees a plainly-named errors file, and legitimately preregisters a payment hypothesis. It would then fail assertion 1 for doing exactly the right thing, while this run passed it by crossing into relationships and blanket-labeling.

The scenario rewards the wrong behavior. Withholding a filename does not make a signal post-peek when listing the directory is allowed. A valid version needs the discovery to be genuinely unreachable from inventory and schema — a pattern that only exists in a relationship nobody would predict from the column names — plus an independent slice to promote it against.

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
