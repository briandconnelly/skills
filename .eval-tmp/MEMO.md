# Decision memo — Assist expansion

**Recommendation: do not expand Assist on this evidence, and do not book the savings.** The −47.5% headline is real arithmetic over the wrong denominator. It is not a treatment effect, and these exports cannot establish one.

## What the data can establish

**1. The headline reproduces, and dissolves under stratification.** Median time to close over closed incidents fell 4.25 h → 2.23 h (−47.5%). But the two weeks did not handle the same work. Incident volume was identical (30/day, every day), while the severity mix moved at exactly the cutover: sev1 13.3% → 6.7%, sev2 40.0% → 20.0%, sev3 46.7% → 73.3%. The Assist week simply contains far more easy incidents.

Within each severity band, Assist incidents were **slower**, not faster:

| Severity | Manual | Assist | Difference | 95% bootstrap CI |
|---|---|---|---|---|
| sev1 | 13.15 h | 14.92 h | **+1.77 h** (+13.4%) | [+1.28, +2.03] |
| sev2 | 4.88 h | 5.58 h | **+0.70 h** (+14.3%) | [+0.42, +0.87] |
| sev3 | 1.68 h | 2.02 h | **+0.34 h** (+20.4%) | [+0.19, +0.54] |

Standardized to the manual week's case mix, the direction flips to a **slowdown of +12% to +15%**, depending on the estimand: exact mix-weighted median 4.28 → 4.82 h (+12.5%), standardized means 4.48 → 5.14 h (+14.7%), mix-weighted average of stratum medians 4.49 → 5.16 h (+15.0%). These are not the same quantity as the raw −47.5% median, so read them as "the reversal survives every reasonable adjustment," not as a single number replacing the headline. This is a textbook aggregation reversal: every stratum moves one way, the total moves the other.

The same reversal hides in a second field. Mean handoffs *improve* marginally (1.79 → 1.77) while worsening within sev2 (2.14 → 2.50) and sev3 (1.12 → 1.50) — the identical composition effect, in a metric nobody flagged.

**2. The comparison also drops its hardest cases, asymmetrically.** Eleven incidents have **no recorded closure** as of the extract; ten are Assist-week. Recorded-closure rates: manual sev1 96.4% vs **Assist sev1 64.3%** — five of fourteen Assist sev1 incidents show no closure 8–14 days after opening, at an extract taken 8+ days after the last one. They are excluded from every median above. (This assumes the activity export captures closures completely; if instead it is dropping records, that is a reporting defect with the same consequence for the dashboard and a different one for operations. The exports cannot tell the two apart.) Since the omission sits entirely in the upper tail, its direction is unambiguous: the within-stratum gaps above **understate** the Assist week's disadvantage.

**3. Finance's saving runs backwards.** Naive weekly totals give 308.8 h → 226.0 h, an apparent 82.8 responder-hours saved. Holding case mix fixed, the same arithmetic gives 312.8 h → **352.1 h**: a standardized complete-case difference of ≈39 responder-hours per 210 incidents, in the opposite direction. Responder minutes are higher under Assist in every band (sev1 +24 min, sev2 +12, sev3 +8.5). **Credibly attributable savings: none — zero hours are bookable today.** Whether Assist *caused* either a saving or a cost is not identified by this design; what is established is that the 82.8 h figure is an artifact of comparing different work.

**4. The responders' report is consistent with the data.** They described extra work on genuinely difficult incidents. Effort is indeed higher in the Assist week in every band (sev1 +24 min), so nothing here contradicts them — though the same confounding that blocks Finance's claim also blocks confirming theirs as an Assist effect.

**5. A signal that needs its own look before anything expands.** Of the nine Assist sev1 incidents that closed, **nine were reopened within 72 hours** (manual: 1 of 27, 3.7%). Marginal reopen rate went 9.1% → 18.5%. If Assist sev1 closures are not durable, "closed" does not mean the same thing in the two weeks, and time-to-close is not measuring the same event.

## What the data cannot establish

**Whether Assist caused anything.** The workflow was assigned by calendar date, to everyone, with no holdout. Every co-occurring change is an equally live explanation, and at least two exist:

- **Case mix** shifted precisely at the cutover, identically on all seven days of each week — a systematic administrative change, not organic variation.
- **Staffing** rose the same day (12→14 identity, 11→13 storage; +13% scheduled hours per incident).

The owners' claim that the comparison is clean because "every incident followed the workflow active when it opened" establishes only that the *labels* are correct. It says nothing about comparability, which is what a before/after contrast needs and this one lacks.

One caveat cuts against my own adjustment: I have treated severity as a pre-treatment covariate. If Assist changed how incidents are *classified* — plausible, given the mix moved on exactly the cutover date — then severity is post-treatment, and stratifying on it is itself biased. That would not rescue the headline; it would make the raw comparison worse. Either way the effect is unidentified.

The staffing increase deserves one more note. Extra capacity would ordinarily be expected to speed things up, and the recorded times went the other way — but "the confounder I measured points the wrong way" is not identification either, and unmeasured week effects remain wide open.

Every quantity in this memo is an **association within an unidentified design**, not an effect. Where I say the Assist week was slower or costlier, that is a statement about two calendar weeks that differ in more ways than the workflow. The one thing the design *does* support refuting is the dashboard's arithmetic: there is no severity band, service group, or intake channel in which recorded times improved, so the −47.5% cannot be read as an improvement in the work.

The contrast is also stable across every cut of the data: Assist is slower in all three severity bands, in **both** service groups, and in **all three** intake channels — ten of ten cells.

## What would settle it

A holdout — randomize by incident or by service group, or stagger the rollout across groups so an untreated comparison period exists. Failing that, a pre-registered analysis on severity assigned *before* workflow assignment, with unclosed incidents carried as censored rather than dropped. Two weeks and 420 incidents is ample data; the missing ingredient is a comparison group, and no amount of re-analysis of these exports substitutes for one.

**Bottom line for Monday: the pilot as run cannot tell you whether Assist works. What it does show — a slowdown and an effort increase in every severity band, and a sev1 reopen rate of 9 out of 9 — is a reason to fix the pilot design before expanding, not to expand.**
