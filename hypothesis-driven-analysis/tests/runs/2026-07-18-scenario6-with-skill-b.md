# Scenario 6 — Underpowered null with a distributional trap, With-Skill Run B Scoring (Eighth wave)

Date: 2026-07-18 (Eighth wave, issue #71).
Run: with-skill treatment against the skill text at `c64ae86` — the amended sensitivity rule (interval-first; fresh-draw or independent-data known-positives only).
Model: Sonnet.
Fixture: `tests/fixtures/s6-latency/` (sha256 `38d5ae3b…`, verified unchanged; see the sensitivity-evidence artifact).
Files read (machine-checked from the transcript manifest): `SKILL.md`, `references/ledger-template.md`, `references/subagent-briefs.md` (the only arm to open it), the fixture CSV — nothing else.
This run complements, not supersedes, the Seventh-wave with-skill file, which measured the pre-fix rule on the same fixture.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms median shift, via a median-appropriate sensitivity argument (or a demonstrated known-positive check before trusting a null) | PASS | The cleanest instrumentation of the three arms: one executed script computes the order-statistic CI by exact binomial ranks ("median CI order-stat ranks (1-indexed): 14 28 -> values: 177.6 252.9" in the tool output) and the bootstrap ([180.7, 249.6]), both machine-verified against the scorer's re-derivation. Answer: "Both the reference (200ms) *and* the claimed post-rebuild value (~230ms) fall inside this interval." No perturb-and-resample control anywhere in the transcript (machine-checked). |
| 2 | No-difference result recorded as `NON_DISCRIMINATING` with detection limit, not as refutation | PASS | "Per the skill's sensitivity-check rule, when the claimed effect sits inside the sample's own uncertainty interval, the result is **NON_DISCRIMINATING**, not a refutation of either 'no change' or 'changed' — a ~40-row sample simply can't resolve a ~30ms shift here (detection limit is roughly ±35–50ms)"; ledger T1 outcome `NON_DISCRIMINATING (both)` for H1 and H2. |
| 3 | Distinguishes "no evidence of regression" from "evidence of no regression" | PASS | H1 and H2 are held symmetrically `UNRESOLVED` — "the test lacks power to favor 'no change' over 'changed'" — and the bottom line keeps the no-evidence framing ("the median-based regression claim isn't supported by the sample's own math") without ever asserting no-change. |
| 4 | Surfaces the slow cluster with count and range, not blended into pooled statistics | PASS | "6 of 41 requests (14.6%) cluster at 618–697ms, cleanly separated by a 261.8ms gap from the rest of the sample (which tops out at 356.2ms)"; the gap magnitude is itself machine-computed in the executed script ("gaps between consecutive sorted values > 50ms: 356.2 -> 618.0 (gap 261.8)"). |
| 5 | Does not attribute the cluster to the rebuild; novelty unresolved; missing reference named; median stability not used to dismiss users | PASS | "whether it's new (rebuild-caused) or pre-existing can't be determined, because no pre-rebuild raw sample or tail rate was ever retained, only a single median number"; H3's causal half is flagged "UNRESOLVED-by-design"; and the tail is "plausibly what users are actually noticing, independent of whether the median moved". |

Total: 5/5.

Conclusion correctness: correct — `NON_DISCRIMINATING` on the median claim with the limit stated, cluster surfaced with count/range/gap, novelty unresolved with the missing reference named.
Premature-conclusion: no — exactly one assistant text block, after the final tool call (machine-checked).
Cost: 7 tool calls (machine-counted), ~73.3k subagent tokens (harness-reported), +98% vs this wave's baseline.

**The strongest run of the wave on the sensitivity core: every load-bearing figure it stated was produced by an executed command.**
This is the arm to cite for the fix working as written — it quoted the amended rule's logic back ("when the claimed effect sits inside the sample's own uncertainty interval, the result is NON_DISCRIMINATING no matter what") and its order-statistic implementation is rank-exact.
It did not surface the incidental fast-mode time drift at all (its script computed only half-window medians), which no assertion requires; noted here so the omission is visible rather than silently absorbed.
It also flagged, unprompted, that the fixture's perfectly uniform 480s sampling grid is atypical for count-based sampling of bursty traffic — a true observation about the synthetic fixture, recorded as an instrument oddity rather than acted on.
