# Scenario 12 — Causal question phrased as "how much"

Date: 2026-07-16
Run: with the skill at commit `e55ba78`. Model: Sonnet. Fixture: `tests/fixtures/s1-conversion/`.
Directly tests the F3 fix (causal intent overrides question phrasing in routing).

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Routes **full**, not estimation, and says why | PASS | "The question... asks 'how much' but requests a causal claim ('improve'). Per the skill's routing table, a causal claim always selects `full` regardless of phrasing... overriding what would otherwise look like an `estimation` question." |
| 2 | Does not report a causal effect estimate as though the campaign's impact were identified | PASS | No lift estimate offered; the question is answered by refusing its premise rather than by producing a number. |
| 3 | Uses associative language, or states the causal question cannot be answered without an identifying design | PASS | "Landing page is user-selected, not randomly assigned, so even this robust association is associative, not causal." |
| 4 | Catches that the premise is wrong: the campaign is associated with *lower* blended conversion | PASS | "The data does not support the claim. Checkout conversion fell, not rose: 3.12% pre-launch → 2.51% post-launch." |

**Total: 4/4.**

Cost: 12 tool calls, ~64.6k subagent tokens, 274s.

## The F3 fix works, and it was load-bearing

Before the override existed, this question matched **estimation** — "how much", not "why" — and estimation precedes full, so first-match-wins routed it away from the loop entirely. It would have produced an estimand, a population, and a confident-looking lift number for an intervention whose effect is not identified in this data at all.

With the override, the run reached the opposite and correct conclusion: the campaign is associated with *lower* blended conversion (a composition effect), the causal question cannot be answered from observational data with no identifying design, and the premise of the question is simply false.

This is the clearest demonstration in the suite that a routing bug is not cosmetic. The same fixture, the same underlying facts, and a one-word difference in phrasing ("how much did X improve Y" vs "why did Y change") decided whether the agent would have manufactured a causal number or refused one.

Worth noting the defect's history: Codex caught this exact shadowing on the `mini` row during design review. That row was fixed by adding "non-causal"; the identical hole one row above went unexamined until an independent reviewer found it. The override now covers every row and any future one, rather than patching rows individually.
