# S1 (multi-explanation diagnostic) — with-skill run, 2026-07-16

Model: Sonnet, general-purpose subagent. Fixture: `tests/fixtures/s1-conversion/`.
Ledger written to scratch and reproduced in the run output.

## Assertions

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Ledger with ≥2 candidate explanations plus a data-validity check before analysis queries | PASS | Ledger with H1 deploy, H2 traffic-mix, H3 device-mix, H4 data-artifact; validity audit performed at Plan |
| 2 | Each hypothesis has a preregistered prediction (if true AND if false) | PASS | Ledger hypothesis table carries both prediction columns |
| 3 | Deploy hypothesis dismissed only by a discriminating test outcome | PASS | "Daily rate was already lower on 06-08 and 06-09, *before* the 06-10 14:00Z deploy; 06-10 itself was the best day of week 2 — timing contradicts the deploy hypothesis" |
| 4 | Mobile undercount caught by the data-validity check or stated as a limitation | **FAIL** | Validity audit checked "no nulls, no duplicate IDs, no schema drift" only; undercount never surfaced, and H4 (data artifact) was declared REFUTED on that basis |
| 5 | Conclusion names best-supported explanation, associative language, lists remaining alternatives | PASS | "H2 best supported"; "associative only, no intervention run"; open question on why the campaign page converts poorly |
| 6 | No queries outside the plan without a ledger amendment | PASS | No unplanned queries observed; no amendments recorded |

**Score: 5/6.** Conclusion correct (composition effect from `/lp/summer-sale`). Premature conclusion: no.
Cost: 12 tool calls, ~52.4k subagent tokens, 167s.

## Finding against the skill (assertion 4)

The run satisfied the letter of the mandatory data-validity check and still missed the planted defect, then used the inadequate check to license a terminal status:

- SKILL.md asks for "how was the data collected, what does it cover, what instrument failures are known".
- The agent interpreted this as *schema* validation — nulls, duplicate IDs, schema drift — none of which can detect a coverage gap.
- `sessions.csv` drops ~40% of mobile sessions on 06-13/06-14. That data is not null, not duplicated, and not schema-drifted; it is simply absent. The check was structurally incapable of failing on the planted defect.
- The run then recorded **H4 (data artifact) REFUTED**. Per the skill's own adequacy rule, `REFUTED` requires a necessary prediction to fail *under an adequate test*. A null/duplicate scan is not an adequate test for an undercount, so this status is unearned by the skill's own standard.

The baseline run, with no skill at all, *did* catch the anomaly (orders exceeding `checkout_reached` on 06-13/14) — though it misattributed the mechanism to the deploy's tracking rather than analytics undercounting.

This is a skill defect, not an agent defect: the check is named but its adequacy is unspecified, so a cheap schema audit passes for it.
