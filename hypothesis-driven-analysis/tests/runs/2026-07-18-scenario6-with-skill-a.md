# Scenario 6 — Underpowered null with a distributional trap, With-Skill Run A Scoring (Eighth wave)

Date: 2026-07-18 (Eighth wave, issue #71).
Run: with-skill treatment against the skill text at `c64ae86` — the amended sensitivity rule (interval-first; fresh-draw or independent-data known-positives only).
Model: Sonnet.
Fixture: `tests/fixtures/s6-latency/` (sha256 `38d5ae3b…`, verified unchanged; see the sensitivity-evidence artifact).
Files read (machine-checked from the transcript manifest): `SKILL.md`, `references/ledger-template.md`, the fixture CSV, plus an `ls` of `references/` — nothing else.
This run complements, not supersedes, the Seventh-wave with-skill file, which measured the pre-fix rule on the same fixture.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms median shift, via a median-appropriate sensitivity argument (or a demonstrated known-positive check before trusting a null) | PASS | Interval-first, exactly as the amended rule prescribes: "order-statistic CI ≈ [177.6, 252.9]ms; a 20,000-draw bootstrap agrees, ≈ [180.7, 249.6]ms… Both the no-change value (200ms) *and* the claimed-regression value (230ms) sit comfortably inside that interval." No perturb-and-resample control appears anywhere in the transcript (machine-checked), and the ledger explicitly declines a power claim: "No known-positive dataset exists to validate detection power directly (would require an independent shifted sample), so the interval check is the only sensitivity evidence available — recorded as a limitation." Instrument note: the bootstrap was machine-executed ([180.7, 249.6] in the tool output); the order-statistic figure was stated from ranks 14–28 against the printed sorted values rather than executed, and it is exactly correct (scorer re-derivation [177.6, 252.9]). |
| 2 | No-difference result recorded as `NON_DISCRIMINATING` with detection limit, not as refutation | PASS | Answer: "the test is **non-discriminating**, not a refutation of the regression claim"; ledger T1 outcome `NON_DISCRIMINATING` with the limit stated ("the sample's own uncertainty interval (~±35-40ms around its center) contains both" and "n=41 can't reliably resolve a 30ms shift"). |
| 3 | Distinguishes "no evidence of regression" from "evidence of no regression" | PASS | "there's no evidence of a median regression large enough to see in this sample, but the sample can't rule out the claimed 30ms either — treat this as 'can't tell from this data' rather than a clean yes or no"; H2 (no real shift) is also left `UNRESOLVED` rather than promoted. |
| 4 | Surfaces the slow cluster with count and range, not blended into pooled statistics | PASS | "~15% of sampled queries (6/41) cluster at 618-697ms, cleanly separated from the rest of the distribution (which tops out at 356ms — a 262ms gap with nothing in between)"; dedicated hypothesis H3 with the gap as its necessary prediction. |
| 5 | Does not attribute the cluster to the rebuild; novelty unresolved; missing reference named; median stability not used to dismiss users | PASS | "There's no pre-rebuild distribution on file to check whether this tail is new, so it can't be pinned on the rebuild either — just flagged as worth digging into"; H3 status `UNRESOLVED` with "no pre-rebuild distribution exists to attribute it to the rebuild vs. pre-existing behavior"; the tail "could plausibly be what users are actually feeling as 'slower'". |

Total: 5/5.

Conclusion correctness: correct — matches ground truth on every load-bearing point (`NON_DISCRIMINATING` median claim, cluster surfaced with count and range, novelty unresolved, warm-up drift self-labeled `retrospective` and kept as an open possibility only).
Premature-conclusion: no — exactly one assistant text block, after the final tool call (machine-checked).
Cost: 8 tool calls (machine-counted), ~68.9k subagent tokens (harness-reported), +86% vs this wave's baseline.

**The amended rule produced the flip issue #71 required, by the prescribed route.**
Where the Seventh-wave with-skill run built a same-sample +30ms perturb-and-resample control, claimed "100% of 2,000 sims", and marked H1 `REFUTED`, this run computed the interval first, found the claimed effect inside it, recorded `NON_DISCRIMINATING`, and refused to manufacture a known positive it did not have — citing the rule's own reasoning back ("would require an independent shifted sample").
One self-report discrepancy is on record: the ledger's Data Validity says both intervals were "computed", but only the bootstrap appears in the transcript's tool calls; the order-statistic figure is nonetheless exactly correct, so no assertion outcome changes.
The run also self-labeled its post-hoc warm-up hypothesis `retrospective` at first writing and kept every hypothesis `UNRESOLVED` rather than forcing a verdict — the same intended behaviors the Seventh wave saw, now with the sensitivity core sound as well.
