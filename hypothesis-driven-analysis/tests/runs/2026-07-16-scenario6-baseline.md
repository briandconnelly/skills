# Scenario 6 — Underpowered null, Baseline Scoring

Date: 2026-07-16
Run: baseline without the skill. Model: Sonnet. Fixture: `tests/fixtures/s6-latency/`.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms shift (or demonstrates sensitivity before trusting a null) | PASS | "Power check: the standard error of the median at n=41 is ~21ms. Detecting a true 30ms shift at this noise level has only ~30% power." |
| 2 | A no-difference result is recorded as non-discriminating with the detection limit stated — not as refutation | PASS | "Inconclusive — not confirmable with this data... The sample is underpowered to distinguish a real 30ms regression from sampling noise." (Reaches the semantics without the skill's vocabulary, which is unavailable to a baseline.) |
| 3 | Answer distinguishes "no evidence of regression" from "evidence of no regression" | PASS | "The point estimate is directionally consistent with the claimed ~30ms slowdown... but neither the Wilcoxon nor sign test rejects 'no change'." |

Total: 3/3.

Cost: 3 tool calls, ~32.8k subagent tokens, 49s.

**Scenario is too easy.** Per the methodology at the top of `scenarios.md`, a baseline satisfying every assertion means the scenario needs tightening. This baseline independently ran a power calculation, refused the null, and flagged that the dashboard's 200ms reference has no attached uncertainty. To retain diagnostic value, S6 must be made harder — e.g. supply a pre-rebuild sample so a naive two-sample test looks legitimate, or make the underpowered comparison the *second* step of a longer investigation where attention is already committed elsewhere.
