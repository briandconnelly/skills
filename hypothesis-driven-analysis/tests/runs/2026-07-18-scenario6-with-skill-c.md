# Scenario 6 — Underpowered null with a distributional trap, With-Skill Run C Scoring (Eighth wave)

Date: 2026-07-18 (Eighth wave, issue #71).
Run: with-skill treatment against the skill text at `c64ae86` — the amended sensitivity rule (interval-first; fresh-draw or independent-data known-positives only).
Model: Sonnet.
Fixture: `tests/fixtures/s6-latency/` (sha256 `38d5ae3b…`, verified unchanged; see the sensitivity-evidence artifact).
Files read (machine-checked from the transcript manifest): `SKILL.md`, `references/ledger-template.md`, the fixture CSV — nothing else.
This run complements, not supersedes, the Seventh-wave with-skill file, which measured the pre-fix rule on the same fixture.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms median shift, via a median-appropriate sensitivity argument (or a demonstrated known-positive check before trusting a null) | PASS, with a checked discrepancy | Interval-first: "computed two independent ways (bootstrap resampling and a distribution-free sign/order-statistic interval)… **[180.7, 249.6] ms**… That interval contains **both** 'no change' (200ms) **and** the claimed post-rebuild value (~230ms)." Discrepancy: the run's order-statistic script has an off-by-one (0-indexed ranks 14/26 = 15th/27th order statistics), so its "order-statistic" interval is really a 94.0%-coverage interval; the true 95% order-statistic CI is [177.6, 252.9] (ranks 14/28, scorer re-derived), and "landed on the *same* interval both times" is an artifact of the bug coinciding with the bootstrap. Outcome unchanged: both the erroneous and the correct interval contain 200 and 230, so `NON_DISCRIMINATING` stands either way; the error is anti-conservative (narrower interval) but not outcome-changing here. No perturb-and-resample control anywhere in the transcript (machine-checked). |
| 2 | No-difference result recorded as `NON_DISCRIMINATING` with detection limit, not as refutation | PASS | Ledger T1 and T2 outcomes `NON_DISCRIMINATING` with the limit stated ("detection limit ≈ ±35ms at this sample size, larger than the claimed 30ms effect itself"); answer: "the data simply cannot distinguish a 30ms regression from zero — the detection limit (~±35ms) is wider than the effect being claimed." |
| 3 | Distinguishes "no evidence of regression" from "evidence of no regression" | PASS | Explicit in the ledger's limitations — "'no detectable shift' is a power limitation, not evidence of 'no shift'" — and in the answer: "every causal/magnitude hypothesis is `UNRESOLVED` — none refuted, none confirmed." |
| 4 | Surfaces the slow cluster with count and range, not blended into pooled statistics | PASS | "~15% (6/41) sit at 618–697ms — separated by a 262ms gap, roughly 8x the largest gap found anywhere else in the sorted data"; T4 preregisters the gap-dominance prediction and the executed script verifies it (largest intra-bulk gap 33.2ms vs 261.8ms). |
| 5 | Does not attribute the cluster to the rebuild; novelty unresolved; missing reference named; median stability not used to dismiss users | PASS | The cluster hypothesis is self-labeled `retrospective` via an explicit ledger amendment and capped at "an open, worth-checking lead… not a conclusion"; the missing reference is named ("no pre-rebuild raw rows exist anywhere"; "the pre-rebuild side is a bare point estimate with no distribution or sample size"); and the tail is offered as the explanation for "'feels slower' user complaints… that a median-based dashboard is largely blind to" rather than the median being used against the users. |

Total: 5/5.

Conclusion correctness: correct on every assertion-bearing point; one stated statistic is wrong in a non-outcome-changing way (the "order-statistic" interval above, and its "same interval both times" agreement claim).
The run's secondary trend check is honest: it computed P(0 of 6 slow samples in the last 10 slots) ≈ 0.16 (scorer re-derived: 0.1637) and correctly declined to treat the pattern as discriminating.
Premature-conclusion: no — exactly one assistant text block, after the final tool call (machine-checked).
Cost: 8 tool calls (machine-counted), ~68.8k subagent tokens (harness-reported), +86% vs this wave's baseline.

**The fix held here too, and the run's one defect is the exact class the amended rule cannot police: implementation error inside a compliant procedure.**
The rule got the run to compute the interval first and record `NON_DISCRIMINATING`, which is the behavior issue #71 required; nothing in any rule text can guarantee the interval arithmetic itself is right.
This wave got lucky in one narrow sense — the off-by-one produced a *narrower* interval that still contained the claimed effect; a fixture where the claimed effect sits between the erroneous and true bounds would convert this same bug into a false `REFUTED`, and no such fixture exists in the suite yet.
Worth remembering as a tighten-later candidate rather than a skill defect: the failure mode is arithmetic, not epistemics.
