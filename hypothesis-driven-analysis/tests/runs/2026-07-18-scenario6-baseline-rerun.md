# Scenario 6 — Underpowered null with a distributional trap, Baseline Re-run Scoring (Eighth wave)

Date: 2026-07-18 (Eighth wave, issue #71).
Run: baseline without the skill, re-run against the same tightened fixture as the Seventh wave.
Model: Sonnet.
Fixture: `tests/fixtures/s6-latency/` (sha256 `38d5ae3b…`, verified unchanged before and after the batch; see the sensitivity-evidence artifact).
Skill text at `c64ae86` was present in the repository but this arm was not offered it; the run touched exactly one repository file, the fixture CSV (machine-checked manifest).
This run complements, not supersedes, the Seventh-wave baseline file: same fixture, fresh single run, dispatched alongside the post-fix with-skill arms as this wave's control.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms median shift, via a median-appropriate sensitivity argument | PASS | Interval-first and median-appropriate: "a rank-based 95% CI for the median is roughly **[178ms, 250ms]** — wide enough to contain *both* 'no change' and '30ms regression.' This sample can't distinguish those hypotheses; it's simply underpowered". Caveat recorded honestly: no tool call computes any CI (manifest: 1 Read + 2 scratch stats scripts), so the figure was asserted from the printed sorted values, not machine-computed; scorer check: the true order-statistic CI is [177.6, 252.9], the stated "roughly [178, 250]" is approximately right, and both versions contain 200 and 230, so the argument's conclusion matches ground truth. |
| 2 | No-difference result recorded as `NON_DISCRIMINATING`-equivalent with detection limit, not as refutation | PASS | The outcome is classified as non-discriminating in substance: "can't distinguish those hypotheses", and the bottom line renders no refutation — "the confidence interval is too wide to detect a shift that size", i.e. the 30ms claim sits below the stated detection capability. Contrast the Seventh-wave baseline, which asserted "the data can refute the median-regression claim". |
| 3 | Distinguishes "no evidence of regression" from "evidence of no regression" | PASS | "The data does not support the specific claim" is kept as a no-evidence statement, and the interval-contains-both framing does the distinguishing work; no sentence anywhere claims the regression is refuted or that no-change is established. |
| 4 | Surfaces the slow cluster with count and range, not blended into pooled statistics | PASS | "6/41 (15%) values sit in 618–697ms (median ≈651ms) — a distinct slow cluster" with the empty gap named: "a clean gap (356ms → 618ms) with zero observations between — two populations, not one shifted distribution". |
| 5 | Does not attribute the cluster to the rebuild; novelty unresolved; missing reference named; median stability not used to dismiss users | PASS | "We don't know if a similar slow-tail existed before the rebuild; it may not be new at all"; the missing reference is named — "No pre-rebuild raw sample exists — only a single summary number (median)"; and the cluster is connected to user perception ("plausibly explains user complaints of 'slower search' even without the median moving") rather than dismissed. |

Total: 5/5.

Conclusion correctness: correct — the median claim is treated as unresolvable at this sample size (ground truth `NON_DISCRIMINATING`: exact CI [177.6, 252.9] contains 230, sign-test p = 0.117, scorer re-derived), the cluster is surfaced with count and range, and its novelty is left unresolved.
Premature-conclusion: no — the transcript contains exactly one assistant text block and it follows the final tool call (machine-checked).
Cost: 3 tool calls (machine-counted), ~37.0k subagent tokens (harness-reported).

**This baseline passed the assertions the Seventh-wave baseline dropped, so S6's baseline outcome is now measured as unstable across single runs.**
The Seventh-wave baseline (2/5) used the same instruments and concluded the opposite of what they show; this run drew the right conclusion from an interval it stated but never executed — its two scratch scripts compute summary statistics, cluster splits, and correlations, and no CI or sign test appears in any command.
The one soft spot worth naming: "Checked for a warm-up/transient explanation (ruled out)" leans on a 3/3 first-half/second-half split of six points, which is thin evidence for "ruled out" — but no assertion covers the drift, and the run's handling of the assertion-bearing content is correct.
Two single runs on the same fixture landing at 2/5 and 5/5 mean this wave's with-skill 5/5s cannot be read as a skill-vs-baseline margin on S6; see the Eighth-wave section of `scenarios.md`.
