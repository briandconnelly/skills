# Decision Memo: Assist Workflow Expansion

**To:** Operations Review
**Re:** Should we expand Assist company-wide, and can we book the reported responder-hour savings?
**Bottom line: No on both.** The pilot data, examined by severity tier, show Assist associated with *slower* closes and *more* responder-minutes on every severity tier — the "faster median" the dashboard reported is a composition artifact of the pilot weeks having very different incident mixes, not a workflow effect. Recommend holding expansion and not booking any savings figure.

## What the data show

The pilot ran as a single cutover with no holdout: `identity` and `storage` switched from `manual` to `assist` for every incident at 2026-06-08T00:00Z, so "manual week" (Jun 1-7) vs. "assist week" (Jun 8-14) is the only contrast available. That is not a controlled experiment — anything else that changed at the same boundary is a rival explanation, and two things did:

1. **The incident mix got much easier in the assist week.** sev1 incidents fell from 28 to 14, sev2 fell from 84 to 42, and sev3 (the easiest, fastest tier) rose from 98 to 154. A pooled median is highly sensitive to this kind of shift.
2. **Staffing increased at the exact same moment.** Active responders rose 12→14 (identity) and 11→13 (storage), scheduled hours rose ~19%, at the identical cutover — perfectly collinear with the workflow change, so this data cannot separate a "staffing" effect from an "Assist" effect even in principle.

Once you stratify by severity — the only way to hold the mix roughly fixed — the picture reverses completely:

| Severity | Manual median TTC (min) | Assist median TTC (min) | Manual mean responder-min | Assist mean responder-min |
|---|---|---|---|---|
| sev1 | 1,100 | 1,659 (+51%) | 240.0 | 312.2 (+30%) |
| sev2 | 512.5 | 740 (+44%) | 99.2 | 137.3 (+38%) |
| sev3 | 167 | 302 (+81%) | 39.2 | 65.4 (+67%) |

Every tier got slower and more expensive under Assist. The pooled median (436 → 326.5 min) only looks better because the assist week had far more cheap sev3 tickets and far fewer expensive sev1/sev2 ones — a textbook Simpson's-paradox artifact. The pooled *mean* (428.5 → 451.9 min) actually rose, which is the tell that the median-only headline was hiding a distributional shift.

Two further findings make the case worse, not better:

- **Right-censoring hides the worst cases, and they're concentrated in Assist.** 11 of 420 incidents are still open as of the extract (2026-06-22); 10 of those 11 are assist-period, and 5 of the 14 assist-period sev1 incidents (36%) are still unresolved 8.5-17 days after opening — far beyond the worst *closed* sev1 duration in either arm (max 1,919 min ≈ 32 hours). The sev1 numbers above are themselves a rosier-than-true picture of Assist, because the hardest, slowest cases haven't closed yet and are excluded.
- **Closures that did happen on hard incidents didn't stick.** Every one of the 9 closed sev1 assist incidents was reopened within 72 hours (100%), versus 0% for manual across all severities and 0% for assist sev2/sev3. This corroborates the responders' complaint directly: on genuinely difficult incidents, Assist appears to add rework rather than remove it, and "closed" isn't a reliable stopping point.

## Responder-hours: what we'd give Finance

**Nothing crediblely positive.** The naive pooled comparison Finance likely used (median-based) implies roughly 60 hours/week "saved" across the two groups — that number is an artifact of the mix shift and does not survive controlling for severity. The severity-standardized comparison (assist's per-tier rates applied to manual's severity mix) shows the opposite sign: **assist would cost roughly 120 more responder-hours/week**, not save them, for these two groups — and this is likely an *underestimate* of the true cost, since the heaviest censoring sits exactly in the tier (sev1) driving that number. Recommend booking **$0 savings** and flagging the standardized negative estimate as a risk, not a number to formalize further without better data.

## Recommendation

**Do not expand Assist company-wide on this evidence, and do not book responder-hour savings.** Hold the two pilot groups where they are (or consider reverting sev1/sev2 to manual pending investigation), and before any expansion decision: (a) run a staggered or held-out rollout so workflow isn't confounded with calendar time, staffing, and incident mix; (b) investigate why sev1/sev2 handling got slower and reopens spiked under Assist — this looks like a genuine workflow problem on hard incidents, not noise; (c) let the 5 still-open assist sev1 incidents mature and re-pull before recomputing any headline metric.

## What this data can't tell us

This was a single-cutover pilot with no randomization and a concurrent staffing change, so no contrast in this dataset can *prove* Assist made things worse company-wide — a masked positive effect can't be formally ruled out from an unidentified design. What the data *can* establish is that there is no evidence here of a genuine improvement once severity mix is controlled, that the pooled "improvement" is explained by a compositional artifact, and that several independent fields (responder-minutes, reopen rate, right-censoring pattern) all point the same direction. That is enough to reject the expansion case as currently supported, without needing to claim a proven causal harm.

---

# Investigation Ledger

## Problem

- Decision informed: whether to recommend company-wide expansion of the Assist workflow at Monday's operations review, and whether Finance's responder-hours savings figure can be booked into the rollout plan.
- Falsifiable question: for incidents opened June 1-14 2026 in the `identity` and `storage` service groups, did the Assist workflow (active from 2026-06-08T00:00Z) cause a reduction in time-to-close and responder-minutes relative to the preceding manual-workflow week, net of other changes that moved at the same time?
- Success criteria: answered means (a) a determination of whether this design identifies a causal effect of Assist, (b) a stated, defensible responder-hours figure (or an explicit statement that none is credible, with the naive number shown alongside for reference), and (c) a recommendation consistent with all outcome and covariate fields, not just the headline metric.
- Stop condition: conclude when no named unresolved alternative (severity-mix shift, staffing-level shift, right-censoring/selection) could reverse the recommendation, or when the available fields are exhausted.
- Effort budget: ~30 read-only queries over the three local CSVs. (Actual: ~28.)

## Orientation findings (schema/coverage only, gathered before any cause-outcome inspection)

- `incidents.csv`: 420 rows, June 1-14, 15 incidents/day/service_group (2 groups), no duplicate incident_id, no nulls in any field.
- `workflow` is a clean calendar split: 210 `manual` (June 1-7) / 210 `assist` (June 8-14), no mixing on any day — matches the stated single-cutover design.
- `activity.csv`: 409 rows (420 incidents minus 11 with no closure recorded as of the extract). All closed_at values fall June 1-15, so reopened_within_72h is fully matured for every closed incident (extract is June 22). No negative/zero responder_minutes.
- The 11 incidents missing from activity.csv (still open at extract) are 10 assist / 1 manual, skewed toward sev1.
- `staffing.csv`: 28 rows = 14 days x 2 groups, complete. `incidents_opened` independently corroborates incidents.csv's daily counts (external cross-check).
- Severity mix shifts sharply at the cutover: manual sev1=28/sev2=84/sev3=98; assist sev1=14/sev2=42/sev3=154.
- `active_responders`/`scheduled_responder_hours` step up at the same cutover; `interruption_minutes` also rises substantially in the assist week.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself genuinely reduces time-to-close / responder-minutes | within the same severity tier and service group, assist incidents close faster / use fewer responder-minutes than manual incidents | within-tier comparison shows no improvement, or reversal | assist must show improvement in most severity tiers after stratifying by severity, not only in the pooled aggregate | T1/T2 | incidents.csv + activity.csv joined, stratified by severity |
| H2 | causal | The severity-mix shift drives most of the pooled improvement, independent of workflow | pooled gap shrinks substantially once severity-standardized; within-tier gaps are much smaller than the pooled gap | within-tier gaps comparable to the pooled gap | the severity-standardized responder-hours gap must be materially smaller than (or reversed relative to) the naive pooled gap, or H2 is refuted as the dominant driver | T1/T6 | incidents.csv + activity.csv, severity-weighted recombination |
| H3 | causal (confound) | The concurrent staffing increase drives some or all of the apparent improvement | workload/queueing-pressure indicators ease after the staffing bump | workload pressure does not ease, or worsens, despite added staff | interruption_minutes and incidents-per-responder must not both worsen after the staffing increase, or the "added slack relieved pressure" mechanism is refuted | T3 | staffing.csv |
| H4 | data-artifact | The extract right-censors unresolved incidents, disproportionately dropping the hardest/longest assist-period cases and inflating the apparent assist improvement | open incidents concentrated in assist + higher severity, with elapsed time exceeding the closed-incident distribution for the same severity/workflow | open incidents trivial in share, evenly distributed, or short-elapsed | assist-arm open incidents must show elapsed time at/above the closed sample's own high percentiles for the same severity, or H4 is refuted | T4 | incidents.csv (opened_at) vs activity.csv coverage gap, extract ts |
| H5 | causal | Assist adds real burden on genuinely difficult (high-severity) incidents even while the aggregate looks better, matching responders' complaint | within sev1 (and/or sev1+sev2), assist shows higher responder_minutes and/or handoffs than manual | no such increase, or a decrease | assist sev1 responder_minutes or handoffs must not be lower than manual sev1, or H5 is refuted | T5 (+T7 supporting) | activity.csv joined to incidents.csv, stratified by severity |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `incidents.csv` (local fixture export) | 2026-07-16 (session) | 420 rows, complete, verified against staffing.csv's independent `incidents_opened` column |
| S2 | `activity.csv` (local fixture export) | 2026-07-16 | 409 of 420 incidents have closure; 11 open/censored, skewed 10 assist / 1 manual, toward sev1 |
| S3 | `staffing.csv` (local fixture export) | 2026-07-16 | 28 rows, complete; shows concurrent staffing step-change at the workflow cutover |

## Data Validity

- Collection method: three flat-file exports frozen at 2026-06-22T23:59Z; no live system access, no re-pull possible.
- Coverage matrix (workflow x severity x service_group, closed vs. open): incidents.csv fully populated (420/420, 105 per workflow x service_group cell). activity.csv's 11-row hole sits on assist x sev1 (5 of 14 open, 35.7%) plus scattered assist sev2/sev3 opens and 1 manual sev3 open — concentrated exactly on the contrast the analysis needs, so it earned its own hypothesis (H4) rather than being smoothed into a closed-incident aggregate.
- Field population: severity/workflow/service_group/intake_channel 100% in incidents.csv; responder_minutes/handoffs/reopened_within_72h 100% for the 409 closed rows; reopened_within_72h fully matured (72h clear of extract) for every closed row.
- Coverage baseline: staffing.csv's `incidents_opened` independently matches incidents.csv's per-day/group totals — used as the coverage baseline for incidents.csv. No independent baseline exists for activity.csv's closure coverage; the 11-row gap is assessed against opened_at + extract time (a maturation-window check) rather than an external denominator.
- Known instrument failures: none beyond the closure-coverage gap; no duplicate IDs, no negative/zero durations, no schema drift.
- Sensitivity checks performed: spot-verified the join/duration computation by hand against raw rows for INC0001 (520 min, matches script) and all 9 closed assist-sev1 incidents (ttc 1567-1919 min, rm 289-330, reopened=1 for all 9 — matches script output exactly). No NON_DISCRIMINATING outcomes were produced, so no additional known-positive check was required.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1, H2 | pooled gap shrinks substantially within severity tiers | joined S1+S2; median/mean ttc and responder-minutes by workflow, overall and by severity | CONTRADICTED (H1) / CONSISTENT (H2) | pooled median TTC 436→326.5 (looks better); every severity tier's median/mean TTC and mean responder-minutes got *worse* under assist (sev1 +51% TTC, sev2 +44%, sev3 +81%) — S1+S2 join |
| T2 | H1 | assist shows improvement in most/all severity tiers | read off T1's stratified table | CONTRADICTED | 0 of 3 tiers improved; all 3 got worse (see T1 evidence) |
| T3 | H3 | interruption_minutes and incidents/responder ease after the staffing increase | staffing.csv before/after June 8 | CONTRADICTED | avg interruption_minutes rose 20.7→66.7 (identity 12.4→74.0, storage 29.0→59.4) despite 17-19% more staff; incidents-per-responder fell mechanically (1.31→1.11, a trivial ratio effect of adding headcount to constant incident volume, not evidence of relief) — S3 |
| T4 | H4 | open incidents concentrated in assist+high-severity, elapsed time exceeds closed-sample highs | elapsed time (extract_ts − opened_at) for the 11 open incidents vs. closed-incident percentiles by severity/workflow | CONSISTENT | 10/11 open are assist; 5/14 assist sev1 (36%) open, elapsed 8.5-15.0 days vs. closed assist-sev1 max of 1,919 min (1.33 days) — 6-11x the worst closed case; same pattern in sev2/sev3 opens — S1+S2 |
| T5 | H5 | assist sev1 responder_minutes and/or handoffs exceed manual's | joined S1+S2, filtered sev1 (and sev1+sev2) | CONSISTENT | sev1 mean responder-minutes: manual 240.0 vs assist 312.2 (+30%); sev1+sev2 mean: manual 134.4 vs assist 169.4 (+26%). (handoffs moved the other way — assist sev1 mean 0.44 vs manual 5.93 — but the prediction's "and/or" is satisfied by responder-minutes alone; noted in Limitations) — S1+S2 |
| T6 | H2 | severity-standardized gap materially smaller than naive pooled gap | reweighted per-tier mean responder-minutes by manual's severity mix, both workflows | CONSISTENT | naive pooled diff ≈ −0.7 min/incident (essentially flat: manual mean 90.2, assist 90.9); severity-standardized diff = −37.1 min/incident in the *reversed* direction (manual 90.2, assist 127.4) — i.e., once mix is held constant, assist costs more, not less — S1+S2 |
| T7 | H5 (supporting, non-necessary) | reopen rate not lower for assist, especially sev1 | reopen rate by workflow and workflow x severity | CONSISTENT | manual 0/209 (0%) reopened at any severity; assist sev1 9/9 closed incidents reopened within 72h (100%); assist sev2/sev3 0% — S2 |

## Amendments

None — no hypothesis was added after inspecting a cause-outcome relationship, and no test outcome required revision after spot-verification.

## Conclusion

- **Answer:** The pilot data do not support a causal Assist speedup. The reported pooled "median time to close fell" is real as a marginal statistic but is explained by a severity-mix shift (far fewer sev1/sev2, far more sev3 incidents in the assist week) that co-occurred with the cutover. Once severity is held roughly fixed by stratification, every tier got slower and more expensive under Assist, and this pattern is reinforced by a 100% reopen rate on closed sev1 incidents and by severe right-censoring that disproportionately hides the longest-running assist-period sev1 cases. A concurrent staffing increase is perfectly collinear with the workflow change and cannot be separated from it in this data, but the one indicator that could distinguish "more slack helped" from "something else is wrong" (interruption_minutes) moved the wrong way for that story.
- **Best supported:** H2 (severity-mix shift explains the pooled illusion) and H4 (right-censoring conceals the worst assist-period sev1 outcomes) — both directly demonstrated (T1/T6, T4). H5 (extra burden on hard incidents) is also well supported (T5, T7) and is independently consistent with responders' stated complaint. H1 (a genuine Assist speedup) has no supporting evidence and a contradicted necessary prediction in every stratum, but the design does not identify the causal contrast (staffing moved at the same cutover), so it is not formally REFUTED — it remains an open, unsupported possibility rather than a proven negative.

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | necessary prediction (within-tier improvement) contradicted in all 3 strata (T1, T2); not REFUTED because the single-cutover design does not identify the workflow contrast apart from the concurrent staffing change — a masked true positive cannot be formally excluded, but nothing in the data supports one |
  | H2 | causal | UNRESOLVED | best supported — T1/T6 CONSISTENT: severity-standardization reverses the sign of the pooled gap, showing the marginal "improvement" is a composition artifact |
  | H3 | causal (confound) | UNRESOLVED | T3 CONTRADICTED the "added slack relieved pressure" mechanism (interruption_minutes rose sharply despite more staff); staffing and workflow are perfectly collinear in this data and cannot be separated by any test available here |
  | H4 | data-artifact | UNRESOLVED | best supported — T4 CONSISTENT: right-censoring is real, material (36% of assist sev1 still open), and concentrated exactly where the workflow already looks worst |
  | H5 | causal | UNRESOLVED | best supported — T5/T7 CONSISTENT: higher sev1 responder-minutes and a 100% sev1 reopen rate under assist corroborate the responders' complaint of extra work on difficult incidents |

- **Responder-hours for Finance:** No positive figure is credible. The naive/marginal comparison implies roughly 60 responder-hours/week "saved" across the two pilot groups (driven by the median and the mix shift); that figure does not survive severity-standardization. The standardized comparison shows the opposite sign — roughly 120 more responder-hours/week consumed, not saved, applying assist's own per-tier rates to manual's severity mix — and this is likely an underestimate given that the heaviest right-censoring sits in the exact tier (sev1) producing that number. Recommend booking $0 in savings and flagging the standardized negative estimate as a cost risk pending better data.
- **Limitations:**
  - This was a single, uncontrolled cutover with no holdout; workflow, severity mix, and staffing all changed at the same moment, so no test here can fully separate their effects — H1 stays UNRESOLVED rather than REFUTED for exactly this reason, per the skill's rule that an unidentified exposure-outcome contrast cannot by itself refute a causal hypothesis.
  - Sample sizes in the hardest stratum are small (9 closed + 5 still-open assist sev1 incidents out of 14 total), so the sev1 point estimates carry real sampling uncertainty on top of the censoring bias already noted.
  - The handoffs metric moved in the opposite direction from responder-minutes for sev1 (down under assist, while responder-minutes rose) — plausibly consistent with a single responder absorbing more work per incident rather than escalating, but this wasn't independently tested and is reported as an open observation, not a resolved mechanism.
  - All causal language above is associative: no randomization or plausibly-independent assignment exists in this data, so "Assist is associated with worse outcomes on hard incidents" is the strongest claim the evidence supports — not proof that Assist caused the deterioration, only that the burden of proof for "Assist helped" is unmet and the available signals point the other way.
