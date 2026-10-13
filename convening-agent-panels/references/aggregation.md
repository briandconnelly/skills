# Aggregation menu

Aggregation turns N member outputs into one result. Choose by **output type**: a label, a ranking, a score, or free text. The wrong rule silently discards signal — a bare mean lets one miscalibrated judge swing the result; a majority vote over correlated members manufactures confidence. Pick deliberately in step 3 of the selection procedure.

## Discrete answers (labels, choices, yes/no)

- **Majority / plurality vote.** Each member casts one vote; the most common wins. Sound only when members are independent and individually better than chance. Define the tie rule up front (see *Even counts* below).
- **Weighted vote.** Weight by member reliability, calibration, or domain fit. Weights can be static (trust a heavier model more on a hard task) or learned from past accuracy. Better than flat voting when members vary in quality — but you need a basis for the weights, or you have just encoded a guess.
- **Confidence-weighted vote.** Members emit a confidence; weight by it. Powerful only if members are *calibrated* — and models are routinely overconfident, so this backfires without calibration. Prefer it only when you have evidence the members' confidence tracks correctness.

## Rankings (ordering multiple candidates)

- **Borda count.** Each member ranks all candidates; points by position, summed. Rewards the broadly-strong candidate that pure top-1 voting ignores. Good default for ranking.
- **Condorcet / pairwise.** Compare candidates head-to-head across members; the one that beats all others wins. More robust, but can produce cycles (A>B>C>A) that need a resolution rule (e.g. fewest pairwise losses).

## Numeric scores (the judge-panel case)

- **Mean** — simple but sensitive to one wild outlier judge. Rarely the right default for small panels.
- **Median / trimmed mean** — drop the extremes first. The robust default when one judge misreads the rubric.
- **Per-criterion aggregation** — when judges score multiple dimensions (correctness, clarity, safety), aggregate each dimension separately rather than collapsing to one number. Preserves signal and makes disagreement legible (a candidate that's correct-but-unclear reads differently from one that's clear-but-wrong).

## Structured findings (review and judge panels)

- **Findings merge.** When judges return lists of findings (the `codex_review_changes` shape: each finding with a severity, evidence, risk, recommendation), **union** them across judges and dedupe to the same underlying issue. Keep the **highest severity** any judge assigned to a given issue — a "critical" from one judge is not averaged down by another judge's silence. A finding raised by only one judge is a **lead to verify, not a claim outvoted**; the others may simply not have looked there. This is the most common real shape for two- or three-judge code review and is distinct from scoring: you are merging issue lists, not combining numbers.
- **Verdict reconciliation.** If judges also return an overall verdict (pass/concerns/fail), take the **most cautious** verdict as the panel's, then let the merged findings justify it. Do not majority-vote verdicts — one judge's "fail" backed by real evidence outweighs two "pass" verdicts that missed it.

## Free text (the hard case)

- **Synthesis (merge).** The chair reads all responses and writes one combined answer. Most flexible, captures nuance — but introduces the chair's own bias and is a single point of failure. This is the MoA aggregator role.
- **Select-best.** A judge picks the single strongest response *verbatim* (best-of-N). Avoids the "averaged mush" where merging dilutes a sharp answer. Prefer when one member is likely to be cleanly right rather than all partially right.
- **Extract-and-union.** Pull structured claims/concerns from each member, dedupe, present the union. Best when completeness matters more than a single voice (persona panels, risk reviews).

## Cross-cutting decisions (set these for every panel)

- **Abstention.** Let members say "unsure" and opt out of the tally rather than forcing a noisy vote. An abstaining member that would otherwise guess only adds variance.
- **Disagreement as the output.** High variance among members is itself a result: it usually means the item is genuinely ambiguous and should be **routed to a human** rather than resolved by the rule. Do not aggregate away a real split — surface it.
- **Even counts and ties.** Cross-family panels are often even (one Claude, one Codex; or 2+2). Decide the tiebreak before dispatch: a designated tiebreaker member (a third family/model that fires only on a split), or fall to the chair. Avoid breaking ties by headcount duplication of one family — that reintroduces correlated error.
- **Correlated members.** Voting and averaging both assume independence. Members sharing a base model fail together, so their agreement is near-worthless and their vote over-counts one viewpoint. Weight correlated members down, or better, fix it upstream by staffing for diversity (step 4).

## Quick map

| Output type | Default rule | Robust alternative |
|-------------|--------------|--------------------|
| Label / choice | Majority vote | Weighted vote (if reliability differs) |
| Ranking | Borda | Condorcet (needs cycle rule) |
| Score | Median / trimmed mean | Per-criterion median |
| Findings list | Findings merge (union, max severity) | + most-cautious verdict |
| Free text | Synthesis | Select-best / extract-and-union |

When in doubt, prefer the rule that *exposes* disagreement (per-criterion, extract-and-union, named split) over the rule that *hides* it (single mean, single merged paragraph). The disagreement is usually where the panel earned its cost.
