# Scenario 6 — Underpowered null, With-Skill Scoring

Date: 2026-07-16
Run: with the skill. Model: Sonnet. Fixture: `tests/fixtures/s6-latency/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms shift (or demonstrates sensitivity before trusting a null) | PASS | Sensitivity check performed at Plan time, before the test: "computed the bootstrap-CI detection limit... The detection limit (~±47ms half-width) exceeds the claimed effect (30ms), so a 'CI contains 200' outcome must be recorded as NON_DISCRIMINATING, not as evidence of no change." |
| 2 | A no-difference result is recorded as `NON_DISCRIMINATING` with the detection limit stated — not as refutation | PASS | T1 outcome `NON_DISCRIMINATING`, detection limit ~47ms vs claimed 30ms effect. |
| 3 | Answer distinguishes "no evidence of regression" from "evidence of no regression" | PASS | "Can't tell from this data... H1 UNRESOLVED — point estimate matches the claim, but not statistically distinguishable from no change at this sample size." |

Total: 3/3.

Cost: 5 tool calls, ~41.2k subagent tokens, 117s (vs baseline 3 calls / ~32.8k).

Both runs land the same substantive answer. What the skill added:

- The sensitivity check ran **before** the test and pre-committed how a null would be classified, rather than rationalizing after seeing the CI.
- Exact vocabulary (`NON_DISCRIMINATING`, `UNRESOLVED`, `REFUTED`) instead of the ambiguous "inconclusive".
- H3 (dashboard/sample comparability) was carried as a standing unresolved confound rather than a closing caveat.
- The stop rule fired explicitly: "no further test is available within the given data... Stopping with limits."

The skill did not change the answer. It changed the auditability of the answer, at ~26% more tokens.
