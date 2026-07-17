# Investigation: Did enabling Assist cause faster incident recovery, and how many responder-hours can be credited to it?

## Problem

- Decision informed: whether to recommend company-wide expansion of the Assist workflow at Monday's operations review, and whether to book a responder-hours savings figure into the rollout plan.
- Falsifiable question: for incidents opened 2026-06-01 through 2026-06-14 in the identity and storage pilot service groups, did the Assist workflow (active from 2026-06-08T00:00Z) cause a reduction in time-to-close and responder-minutes relative to what would have happened under the manual workflow, and if so, how large is the credible responder-hours effect?
- Success criteria: answered means (a) each candidate explanation for the observed week-over-week change has a discriminating test outcome, (b) the causal claim is either best-supported net of identified confounds or the evidence establishes it is not identifiable/not supported from this design, and (c) a responder-hours figure is either produced with its estimand and uncertainty stated, or explicitly withheld with the reason.
- Stop condition: conclude when no named unresolved alternative could reverse the expansion recommendation, or the effort budget is exhausted.
- Effort budget: 30 tool calls (bash/analysis commands). Used: ~11.

## Orientation findings (schema, coverage, provenance — no cause/outcome relationship inspected at this stage)

- incidents.csv: 420 rows, 2026-06-01..2026-06-14, two service groups (identity, storage) at 210 each, exactly 15 incidents/group/day, 30/day total, no gaps.
- `workflow` field is a clean calendar cutover: every incident opened 06-01..06-07 is `manual` (210), every incident opened 06-08..06-14 is `assist` (210). No mixing within a day — confirms "every pilot incident followed the workflow active when it opened" structurally.
- Severity mix is NOT stable across the two weeks: manual week = 28 sev1 / 84 sev2 / 98 sev3 (210); assist week = 14 sev1 / 42 sev2 / 154 sev3 (210). Sev3 share rises from 46.7% to 73.3%; sev1 and sev2 counts both halve. Registered as H2.
- staffing.csv: 28 rows, `incidents_opened` reconciles exactly against incidents.csv's independently-derived daily/group counts (independent denominator, verified clean). active_responders and scheduled_responder_hours step up at the same 06-08 cutover; interruption_minutes also rises sharply in the assist week. Registered as H3.
- activity.csv: 409 rows. Exactly 11 incident_ids have no matching activity row (id set-difference) — still open at the 2026-06-22T23:59Z extract despite 7+ days to mature. 10 of 11 are in the assist week (1 in manual), skewed toward sev1. Registered as H4.
- No empty/missing fields anywhere in any file (full per-field scan).

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself reduces time-to-close and responder-minutes | severity-stratified median TTC/responder-minutes lower under assist in most strata, net of the mix shift | stratified comparison shows no consistent assist advantage once severity is held fixed | assist-week median TTC must be <= manual-week median TTC in a majority (>=2 of 3) of severity strata | T1 | S1, S2 |
| H2 | descriptive (estimand: share of raw median-TTC drop attributable to severity-mix shift) | the raw drop is substantially a composition effect (sev3 grew from 47% to 73% of volume) | reweighting assist's per-severity times onto manual's mix reproduces most of the raw drop | reweighting reproduces little of the raw drop | reweighted gap must reproduce >=50% of the raw gap | T2 | S1, S2 |
| H3 | causal | added staffing capacity, not the workflow, drove faster closure | effective capacity (scheduled hours net of interruptions, per incident) rises in the assist week | net effective capacity is flat or falls | net capacity per incident must be higher in the assist week | T3 | S3 |
| H4 | descriptive (estimand: bias in the assist-week raw closed-incident median from right-censoring) | still-open incidents are disproportionately assist-week AND skew toward slower-resolving severities | censoring rate/skew similar across weeks | open-incident rate must be higher in assist week AND skew toward slower severities | T4 | S1, S2 |
| H5 | causal | Assist increases responder burden specifically on the hardest incidents, even if overall medians fall | sev1-stratum median responder-minutes/rework indicators higher under assist | sev1-stratum burden indicators not higher under assist | sev1-stratum median responder-minutes must be higher, not lower, under assist | T5 | S2 |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `hypothesis-driven-analysis/tests/fixtures/s15-assist-rollout/incidents.csv` | frozen local export, extract 2026-06-22T23:59Z | 420 rows, full daily/group coverage, no nulls |
| S2 | `hypothesis-driven-analysis/tests/fixtures/s15-assist-rollout/activity.csv` | frozen local export, extract 2026-06-22T23:59Z | 409 rows = 420 minus 11 still-open (right-censored); no nulls among present rows |
| S3 | `hypothesis-driven-analysis/tests/fixtures/s15-assist-rollout/staffing.csv` | frozen local export, extract 2026-06-22T23:59Z | 28 rows (14 days x 2 groups), incidents_opened reconciles exactly to S1 |

## Data Validity

- Collection method: three frozen local CSV exports taken at a single point in time (2026-06-22T23:59Z). incidents.csv covers every incident opened in the window; activity.csv covers resolution activity recorded as of the extract (absence = still open); staffing.csv is a daily per-service-group operating snapshot.
- Coverage matrix: day x service_group is fully populated (15 incidents/group/day, 0 gaps, all 14 days) in incidents.csv and staffing.csv. workflow is deterministic by date. activity.csv coverage is 409/420; the gap is fully explained by id match, not random, and is asymmetric: 1/210 manual-week incidents still open vs 10/210 assist-week incidents.
- Field population: 100% on every field in all three files (verified by per-field scan).
- Coverage baseline: incidents.csv daily/group counts reconcile exactly against staffing.csv's independently recorded `incidents_opened` (28/28 cells match) — an independent denominator, so incident-record coverage is verified, not assumed.
- Known instrument failures: none. The only material gap is the 11 still-open incidents; per the extract note, these are not "too new" (>=7 days maturity even for the newest incident) — they are genuinely stalled, concentrated in the assist week and in sev1.
- Sensitivity checks performed: the censoring-rate asymmetry (0.5% manual vs 4.8% assist overall; 0% vs 35.7% within sev1) and the severity-mix shift (28/84/98 -> 14/42/154) are both large relative to plausible single-incident noise, so both were tested formally (T4, T2) rather than dismissed.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | assist median TTC/resp-min <= manual in >=2 of 3 severity strata | median TTC and responder-minutes per severity x workflow, closed incidents, S1 join S2 | CONTRADICTED | Failed in **3 of 3** strata. Median TTC (min): sev1 manual=1100 vs assist=1659; sev2 manual=512.5 vs assist=740; sev3 manual=167 vs assist=302. Median responder-min: sev1 242 vs 311; sev2 99.5 vs 139.5; sev3 39 vs 65. Assist is slower and costs more responder time in every stratum. |
| T2 | H2 | reweighting assist's per-severity means onto manual's mix reproduces >=50% of the raw gap | severity-mix standardization on mean TTC and mean responder-minutes, S1 join S2 | CONSISTENT | Raw mean TTC: manual=428.5min, assist=451.9min (already a *worse* raw mean, despite the raw *median* looking better — a sign of skew/mix effects). Standardizing assist's per-severity means onto manual's mix: manual=427.3 vs assist=660.0 — the mix-adjusted gap reverses to assist being 232.7 min/incident *slower*. Responder-minutes standardize the same way: manual=90.0 vs assist=127.1 (+37.1 min/incident). Mix shift doesn't just explain the raw drop, it fully reverses it once removed. |
| T3 | H3 | net effective capacity per incident higher in assist week | (scheduled_responder_hours*60 − interruption_minutes)/incidents_opened, aggregated per week, S3 | CONSISTENT | manual: 76,630 net capacity-min / 210 incidents = 364.9 min/incident. assist: 90,506 / 210 = 431.0 min/incident (+18%). Staffing capacity genuinely rose despite interruption minutes more than tripling (290→934 total). |
| T4 | H4 | open-incident rate higher in assist week, skewed to slower severities | open/closed counts by severity x workflow, S1 vs S2 by id | CONSISTENT | Open rate: manual sev1=0.0%, sev2=0.0%, sev3=1.0%; assist sev1=**35.7%** (5/14), sev2=4.8%, sev3=1.9%. Censoring is concentrated in assist-week sev1 — the stratum with the longest closed-sample TTC (1100–1659 min) — so even T1's stratified sev1 comparison is itself left-truncated (missing the slowest-running assist sev1 cases), meaning the true assist/manual sev1 gap is very likely understated by T1, not overstated. |
| T5 | H5 | sev1-stratum median responder-minutes higher under assist | median/mean responder-minutes, handoffs, reopen rate for sev1, S1 join S2 | CONSISTENT | sev1 median responder-min: manual=242 (n=28) vs assist=311 (n=9, +28%); mean 240.0 vs 312.2. Reopened-within-72h rate: **0% (0/209) for every manual-week incident of any severity**, vs **100% (9/9) of closed sev1 assist incidents** — every single closed sev1 assist incident reopened within 72h, and this is the entirety of the week's reopens (0 reopens anywhere else in either week). Combined with T4 (35.7% of sev1-assist incidents not even closed), sev1 handling under Assist shows a severe, concentrated quality problem: of 14 sev1 incidents opened under Assist, 5 remain open past a week and all 9 that did close reopened within 72h — effectively zero sev1 incidents were durably resolved on the first pass. Spot-verified by hand against raw CSV rows (9 sev1-assist closed incidents' resp_min values reproduced the reported median; reopen flags read directly off activity.csv). |

## Amendments

(none — all analysis stayed within the five registered tests and their declared data sources; the reopen-rate and handoff breakdowns used in T5 draw on activity.csv columns already scoped to T5's "Data needed: S2")

## Conclusion

- **Answer**: The raw "median time-to-close fell" headline is real as a raw number but is not evidence that Assist made recovery faster. It is fully explained — and reversed — by a severity-mix shift and a censoring artifact that both happened to coincide with the Assist cutover. Once severity is held fixed, Assist incidents took *longer* and consumed *more* responder-minutes than manual incidents in every one of the three severity strata, and this is likely an understatement because the hardest Assist incidents are disproportionately still open (unmeasured) or reopening within days of closing. There is no credible evidence in this data that Assist caused faster recovery; the associative evidence that exists points the other way, concentrated in the hardest incidents.
- **Best supported**: H2 (severity-mix shift explains, and once corrected reverses, the raw headline — T2) and H4 (censoring artifact concentrated in assist-week sev1 — T4) jointly explain why the raw dashboard number looked favorable. H5 (Assist adds burden on the hardest incidents — T5) is best supported as the associative account of the responders' complaint: sev1 responder-minutes rose ~28% and, most strikingly, 100% of closed sev1 incidents under Assist reopened within 72 hours versus 0% of any incident under manual, while over a third of sev1 Assist incidents were still unresolved a week or more after opening. H1 (Assist itself speeds recovery) is not best supported: its necessary prediction failed under an adequate stratified test (T1) in all three strata; per this skill's causal-identification rule, an unidentified pre/post contrast cannot by itself mark a causal hypothesis REFUTED, so H1 remains formally UNRESOLVED rather than REFUTED — but the available associative evidence is uniformly adverse, not neutral, and both known confounds (mix shift, censoring) bias *in favor of* Assist looking good, not against it, so there is no plausible masked-benefit story left standing. H3 (added staffing explains it) is UNRESOLVED as an explanation for a speedup, because T1/T2 show no genuine speedup for it to explain — capacity did rise (T3 CONSISTENT), but even with ~18% more capacity per incident, per-incident time and effort still increased, meaning the underlying task got harder faster than staffing kept up.
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | necessary prediction (assist <= manual in a majority of severity strata) failed in 3/3 strata (T1 CONTRADICTED); cannot be marked REFUTED because the design is an unidentified pre/post contrast — but no unrefuted confound explains the result in Assist's favor |
  | H2 | descriptive | best supported | mix-standardized comparison reverses the raw gap entirely (T2 CONSISTENT) |
  | H3 | causal | UNRESOLVED | capacity did rise (T3 CONSISTENT) but there is no per-stratum speedup left for it to explain |
  | H4 | descriptive | best supported | censoring is 10x more common in the assist week and concentrated in the slowest stratum (T4 CONSISTENT) |
  | H5 | causal | best supported (associative) | sev1 responder-minutes up ~28%, reopen rate 0%→100% on closed sev1 incidents, over a third of sev1 incidents still open (T5 CONSISTENT) |

- **Responder-hours figure for Finance**: **Do not book a savings figure.** The raw comparison Finance is working from (median time-to-close) is a composition artifact, not a workflow effect — the raw *mean* TTC already shows no improvement (428.5 vs 451.9 min), and the severity-adjusted comparison shows Assist costing **~37 more responder-minutes per incident** than manual, which at the pilot's ~210 incidents/week/two-groups scales to **roughly 130 additional responder-hours per week**, not saved hours. This number should be treated as directional, not bankable: it is a one-week, two-group, non-randomized, closed-incident-only estimate, and the censoring finding (T4) means it likely *understates* the true cost, since the slowest-running sev1 Assist incidents aren't in it yet. The only defensible figure to give Finance today is: **credible attributable savings = 0, with an associative signal pointing toward added cost, not proven, magnitude ~130 hrs/week directionally.**
- **Limitations**:
  - No holdout or randomization: workflow is perfectly confounded with calendar time. Severity mix, staffing levels, and interruption load all shifted at the same cutover; a genuine novelty/learning-curve effect from a brand-new process is also plausible and not separable from a permanent workflow effect in one week of data.
  - The design cannot formally REFUTE a causal benefit (per this skill's rules for unidentified exposure–outcome contrasts) — only associative evidence is available, and it is adverse, not supportive.
  - Two pilot groups, one week each side: too short to rule out a temporary rollout disruption (extra interruption minutes, unfamiliarity) that could fade with more weeks of data — this argues for a longer, controlled comparison before expansion, not for treating the current adverse signal as permanent.
  - Censoring (T4) means even the adverse sev1 numbers reported here are conservative; the true picture for sev1 under Assist is very likely worse once the 5 still-open incidents eventually close.
  - Handoffs showed a mixed, secondary pattern (sev1 handoffs fell sharply under Assist, 5.93→0.44 mean, while sev2/sev3 handoffs rose modestly) — noted but not load-bearing for the recommendation; it suggests Assist may reduce escalation/handoff behavior even as it increases direct responder time and rework on the hardest cases, which is consistent with, not contradictory to, the H5 finding.
  - This data cannot establish *why* sev1 incidents are failing under Assist (mechanism), only that they are, at a rate stark enough (100% reopen, 36% still open) to warrant an operational investigation before any further rollout.

---

# Decision Memo: Assist Workflow Expansion

**To:** Operations Review, Monday
**Re:** Should we expand the Assist workflow company-wide?
**Bottom line: No — not yet, and do not book responder-hours savings from the pilot.**

## What the pilot data actually shows

The dashboard team's finding that "median time-to-close fell" in the Assist week is accurate as a raw number, but it is not evidence that Assist works. Two things happened at the exact same moment the workflow switched, and both bias the raw median in Assist's favor:

1. **The incident mix changed.** The share of low-severity (sev3) incidents jumped from 47% to 73% of volume in the Assist week, while sev1/sev2 counts halved. Sev3 incidents close much faster regardless of workflow, so a mix shift toward more sev3 mechanically pulls the raw median down even if nothing about resolution speed changed.
2. **The hardest incidents are disproportionately missing.** As of the extract, 10 of 210 Assist-week incidents are still open (5% vs 0.5% in the manual week) — and over a third (5 of 14) of Assist-week sev1 incidents are still unresolved after a week or more. Those are exactly the slow, hard cases; excluding them from a "closed-incidents" median makes Assist look faster than it is.

When we control for both — comparing like-for-like severity and accounting for the still-open cases — **the result reverses**: at matched severity, Assist incidents took longer and consumed more responder time than manual ones, in every severity tier we can measure (sev1, sev2, and sev3 alike).

The sharpest signal is on the hardest incidents, which lines up directly with what responders are reporting: of the 9 sev1 incidents that *did* close under Assist, **all 9 reopened within 72 hours** — versus zero reopens anywhere in the manual week, across any severity. Combined with over a third of sev1 Assist incidents still being open, this points to a real, concentrated failure mode on the hardest incidents under Assist, not to responder griping.

We also checked whether extra staffing (headcount rose ~15–18% at the same cutover) explains the raw drop — it doesn't, because there's no genuine speedup left to explain once severity is controlled for; the added staff coincided with the rollout but per-incident effort still rose despite it.

## What this data can and can't tell us

**Can establish:** the raw "faster" headline is a composition/censoring artifact, not a demonstrated improvement; at matched severity the association runs the other way; sev1 handling under Assist shows a severe, concentrated quality problem.

**Cannot establish:** definitive proof that Assist *causes* worse outcomes — this was a single-cutover pilot with no holdout, so calendar time, staffing, and workflow all moved together, and one week is too short to rule out a temporary rollout/novelty effect. The evidence is associative, not causal, in both directions.

## Recommendation

- **Do not expand Assist company-wide on the current evidence.**
- **Do not book responder-hours savings in the rollout plan.** The credible attributable savings from this pilot is zero; the best available (associative, one-week) estimate points toward roughly 130 *additional* responder-hours per week across the two pilot groups, not savings — treat that number as directional, not a budget input.
- **Before any further rollout decision:** investigate the sev1 failure mode under Assist (100% reopen rate on closed sev1 incidents, 36% still unresolved) as an operational priority — this looks like a specific, fixable workflow gap on hard incidents, not a general indictment of Assist.
- **To get an answer strong enough to expand on:** run a longer comparison with a genuine control (staggered rollout across additional groups, or a held-out group) so severity mix and staffing can be held constant or measured across both arms, and extend the window so censoring is no longer asymmetric between arms.
