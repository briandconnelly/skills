# Scenario 1 — Multi-explanation diagnostic, RERUN against the fixed skill

Date: 2026-07-16
Run: with the skill at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s1-conversion/`.
Supersedes `2026-07-16-scenario1-with-skill.md`, which exercised the old wording.
Prompt: as recorded in `scenarios.md` S1, plus the standard execution constraints.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Ledger with ≥2 candidate explanations plus a data-validity check before analysis queries | PASS | H1–H4 with a Sources table and a Data Validity section; orientation performed first (see caveat below). |
| 2 | Each hypothesis has a preregistered prediction (if true AND if false) | PASS | Table carries both columns plus the new "Necessary prediction (failure refutes)" column. |
| 3 | Deploy hypothesis dismissed only by a discriminating test outcome | PASS | T1: "06-08→06-12 rates (2.83, 3.17, 3.50, 2.83, 3.17%) reproduce 06-01→06-05 rates exactly — no shift at the deploy" → CONTRADICTED. |
| 4 | Mobile undercount caught by the data-validity check or stated as a limitation | **PASS — first with-skill run to catch it** | "Anomaly found: on 06-13 and 06-14, orders exceed `checkout_reached` counts by +6 each day (23 vs 17, 17 vs 11)... it is an unresolved data-quality wrinkle"; carried into Limitations. |
| 5 | Conclusion names best-supported explanation, associative language, lists remaining alternatives | PASS | "associated with a traffic-mix shift"; "this is associative, not causal — no intervention was run"; H3 anomaly left unresolved and named. |
| 6 | No queries outside the plan without a ledger amendment | PASS | T5 recorded as an amendment. |

**Total: 6/6** (old wording scored 5/6, failing assertion 4).

Conclusion correctness: **correct**. Cost: 13 tool calls, ~56.3k subagent tokens, 254s.

## The coverage fix: helped, but 1-for-2, and not by the prescribed route

This run caught the planted defect and handled it well. It did *not* stop at "no nulls": it found the 06-13/06-14 anomaly, promoted it to H3 (data artifact), gave it a necessary prediction, and refuted it on **direction** — an undercount that inflates week 2's rate cannot explain a *drop*. That reasoning is correct and is the exact discipline the rule was rewritten to produce. It also ran a genuine known-positive check: "for 9 of 14 days, `checkout_reached='yes'` count equals same-day order count exactly (known positive — the two independent series agree when nothing else is going on)."

Two honest qualifications:

1. **The companion rerun (`scenario7-serial-rerun`) still missed it**, reporting "Data is complete (no nulls), covers both full weeks". So the rewritten rule is 1-for-2, not fixed. Tally across the suite: old wording 0/3 caught; new wording 1/2.
2. **The catch did not come from the mechanism the rule prescribes.** The rule asks for row counts per period *and per segment*. This run found the anomaly by cross-checking two independent sources (orders vs `checkout_reached`) — the same route both baselines used. Per-segment mobile counts were never compared. The rule may be getting credit here for a check the run would have done anyway.

## Retrospective labeling, tested at last

S5 could never exercise this. This run did, unprompted:

> "(H1–H4 are retrospective: segment/day-level rates were inspected during orientation before this table was formalized, in a single continuous investigation rather than strict two-phase separation. Flagged per skill rules rather than hidden.)"

The agent inspected cause-outcome relationships (landing page × conversion rate) during orientation, recognized that this crossed the line the new orientation rule draws, and labeled its hypotheses `retrospective` rather than passing them off as preregistered. The boundary is now concrete enough to be self-detected — which is what F5 asked for — and the honesty is the rule working, not failing.

It is also evidence the boundary is drawn in a demanding place: a single-pass investigation naturally inspects rates while orienting. Worth watching whether agents start labeling everything retrospective, which would drain the label of meaning.
