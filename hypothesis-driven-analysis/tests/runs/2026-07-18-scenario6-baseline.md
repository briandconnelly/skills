# Scenario 6 — Underpowered null with a distributional trap, Baseline Scoring

Date: 2026-07-18
Run: baseline without the skill, against the tightened fixture (issue #67).
Model: Sonnet.
Fixture: `tests/fixtures/s6-latency/` (sha256 `38d5ae3b…`, see the 2026-07-18 artifact file).
Supersedes nothing: the 2026-07-16 S6 rows scored the pre-tightening fixture and do not carry over.

| # | Assertion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Recognizes the sample cannot resolve a 30ms median shift, via a median-appropriate sensitivity argument | FAIL | Used median-appropriate instruments (sign test, bootstrap CI [180.7, 249.6]) but concluded the opposite of what they show: "the data can refute the median-regression claim" and "A true median of 230 ms (the claimed regression) has only ~4% support in resampling" — while its own CI contains 230. Scorer check: sign test against median=230 gives p=0.117; the "~4% support" figure is P(bootstrap median ≥ 230), which is not a compatibility test. |
| 2 | No-difference result recorded as `NON_DISCRIMINATING`-equivalent with detection limit, not as refutation | FAIL | Verdict rendered as adjudication: "Verdict: the specific 'median got ~30ms worse' claim is **not backed by this sample**" plus the refutation-capability claim above. The aside "(n=41 is small; CI is wide, ±~35-50ms)" gestures at a detection limit but the outcome is never classified as non-discriminating. |
| 3 | Distinguishes "no evidence of regression" from "evidence of no regression" | FAIL | The two framings are conflated across sections: "not confirmed — current sample matches the old median within noise" (no-evidence) sits alongside "the data can refute the median-regression claim" and the "~4% support" line (evidence-of-no). The distinction is never drawn for the median claim; it is drawn only for the tail ("cannot confirm or rule out a tail-latency regression"). |
| 4 | Surfaces the slow cluster with count and range, not blended into pooled statistics | PASS | "6/41 requests (≈15%) form a distinct 'slow' cluster: 618–697 ms — roughly 3x the typical latency, and tight enough to look like a separate code path, not random tail noise." Also noted the cluster pulls the mean to 267ms while the median barely moves. |
| 5 | Does not attribute the cluster to the rebuild; novelty unresolved; missing reference named; median stability not used to dismiss users | PASS | "no way to confirm whether this bimodal tail is new (introduced by the rebuild) or pre-existing"; names the missing reference explicitly — "attributing it to the rebuild requires pre-rebuild tail/percentile data that doesn't exist" and "Recommend pulling p95/p99 (or raw logs)"; explicitly connects the cluster to user perception ("a 1-in-7 chance of a 3x-slow query is noticeable") rather than dismissing the reports. The prompt states the pre-rebuild reference was not retained, so naming it as the unrecoverable gap is the satisfying behavior; a run could only exceed this by proposing a genuinely recoverable historical source. |

Total: 2/5.

Cost: 4 tool calls, ~35.6k subagent tokens, 86s.

**The tightening worked, but not through the planted trap.**
The baseline found the slow cluster cleanly (assertion 4) and handled its novelty correctly (assertion 5) — the distributional trap did not catch it.
What it dropped is the sensitivity core (assertions 1–3): the mixture makes naive power reasoning genuinely treacherous, and the run walked into it — its own bootstrap CI contains the claimed 230ms median, yet it asserted refutation capability backed by a resampling statistic that does not test compatibility.
Contrast with the 2026-07-16 baseline, which passed all three of the old assertions: the old single-mode fixture rewarded a textbook SE-of-the-mean power check, and this fixture punishes exactly that move.
