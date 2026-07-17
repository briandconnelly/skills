# Investigation: Did enabling Assist cause faster incident recovery in the two pilot service groups, and how many responder-hours can be credibly attributed to it?

## Problem

- Decision informed: whether to recommend company-wide expansion of the Assist workflow at Monday's operations review, and whether Finance's responder-hours savings figure can be booked into the rollout plan.
- Falsifiable question: for incidents opened June 1-14 2026 in the `identity` and `storage` service groups, did the Assist workflow (active from 2026-06-08T00:00Z) cause a reduction in time-to-close and responder-minutes relative to the preceding manual-workflow week, net of other changes that moved at the same time?
- Success criteria: answered means (a) a determination of whether this design identifies a causal effect of Assist, (b) a stated, defensible responder-hours figure (or an explicit statement that none is credible, with the naive number shown alongside for reference), and (c) a recommendation consistent with all outcome and covariate fields, not just the headline metric.
- Stop condition: conclude when no named unresolved alternative (severity-mix shift, staffing-level shift, right-censoring/selection) could reverse the recommendation, or when the available fields are exhausted.
- Effort budget: ~30 read-only queries over the three local CSVs.

## Orientation findings (schema/coverage only, no cause-outcome relationship inspected)

- `incidents.csv`: 420 rows, June 1-14, 15 incidents/day/service_group (2 groups), no duplicate incident_id, no nulls in any field (severity/workflow/intake_channel/service_group counts all sum to 420).
- `workflow` is a clean calendar split: 210 `manual` (June 1-7) / 210 `assist` (June 8-14) with no mixing on any day — matches the stated single-cutover design.
- `activity.csv`: 409 rows (420 incidents - 11 with no closure recorded as of the extract). All closed_at values fall June 1-15; reopened_within_72h is therefore fully matured (extract is June 22) for every closed incident. No negative/zero responder_minutes; handoffs and reopened_within_72h fields fully populated for closed rows.
- The 11 incidents missing from activity.csv (still open at extract) are **10 assist / 1 manual**, and skew toward higher severity (4 of 14 assist sev1 incidents are among them). This is a right-censoring / coverage gap concentrated in one arm and one severity tier — flagged as a candidate selection hypothesis, not yet linked to outcome values.
- `staffing.csv`: 28 rows = 14 days x 2 groups, complete. `incidents_opened` in staffing.csv is a fixed 15/day/group throughout, independently corroborating the incidents.csv daily counts (external cross-check, not a self-referential total).
- Severity mix shifts sharply at the same cutover: manual week sev1=28/sev2=84/sev3=98; assist week sev1=14/sev2=42/sev3=154. This is a compositional covariate shift co-occurring with the workflow change.
- `active_responders` and `scheduled_responder_hours` step up at exactly the same cutover (identity 12→14 responders, 93-99→112-115 sched. hours; storage 11→13, 84-90→100-107 sched. hours) and stay elevated the whole assist week. `interruption_minutes` also rises substantially in the assist week. These are potential confounds/covariates, not outcome values, so inspecting them at Plan time does not cross the orientation line.

No time-to-close or responder-minutes value has yet been compared across workflow at this point in the investigation.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself genuinely reduces time-to-close / responder-minutes | within the same severity tier and service group, assist incidents close faster / use fewer responder-minutes than manual incidents | within-tier comparison shows no improvement, or reversal | assist must show improvement in most severity tiers after stratifying by severity, not only in the pooled aggregate | T1/T2 | incidents.csv + activity.csv joined, stratified by severity |
| H2 | causal (confound) | The severity-mix shift (fewer sev1/sev2, more sev3 in the assist week) drives most of the pooled improvement, independent of workflow | pooled gap shrinks substantially once severity-standardized; within-tier gaps are much smaller than the pooled gap | within-tier gaps are comparable to the pooled gap (mix standardization changes little) | the severity-standardized responder-hours gap must be materially smaller than the naive pooled gap, or H2 is refuted as the dominant driver | T1/T6 | incidents.csv + activity.csv, severity-weighted recombination |
| H3 | causal (confound) | The concurrent staffing increase (more responders/scheduled hours, exactly at the cutover) drives some or all of the apparent improvement, independent of the Assist workflow | workload/queueing-pressure indicators (interruption_minutes, incidents per responder) ease after the staffing bump | workload pressure does not ease, or worsens, despite added staff | interruption_minutes and incidents-per-responder must not both worsen after the staffing increase, or the "added slack relieved pressure" mechanism is refuted as a driver (workflow vs. staffing remain non-identifiable from this data either way, since they moved together) | T3 | staffing.csv |
| H4 | data-artifact | The extract right-censors unresolved incidents, disproportionately dropping the hardest/longest assist-period cases from the "closed" outcome and inflating the apparent assist improvement | the 11 open incidents are concentrated in assist + higher severity, and their (extract - opened_at) elapsed time exceeds the closed-incident distribution for the same severity/workflow | open incidents are a trivial share, evenly distributed, or short-elapsed, so excluding them would not move the medians | at least the assist-arm open incidents must show elapsed time at or above the closed-sample's own high percentiles for the same severity, or H4 is refuted as a material bias | T4 | incidents.csv (opened_at) vs activity.csv coverage gap, extract timestamp 2026-06-22T23:59Z |
| H5 | causal | Assist adds real burden on genuinely difficult (high-severity) incidents even while the aggregate looks better, matching responders' complaint | within sev1 (and/or sev1+sev2), assist incidents show higher responder_minutes and/or handoffs than manual counterparts | no such increase, or a decrease, within the hard tier | assist sev1 responder_minutes or handoffs must not be lower than manual sev1 on average, or H5 is refuted | T5 (+T7 reopen-rate as supporting, non-necessary) | activity.csv joined to incidents.csv, stratified by severity |

Hypotheses H1-H5 are all framed from the Problem statement and orientation-stage coverage/covariate findings, not from any observed cause-outcome relationship, so none is retrospective.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `incidents.csv` (local export, this task's fixture dir) | 2026-07-16 (session start) | 420 rows, June 1-14 opens, complete, no nulls, verified against staffing.csv's independent `incidents_opened` column |
| S2 | `activity.csv` (local export, same dir) | 2026-07-16 | 409 of 420 incidents have a closure record; 11 open/censored at extract, skewed 10 assist / 1 manual and toward sev1 |
| S3 | `staffing.csv` (local export, same dir) | 2026-07-16 | 28 rows, 14 days x 2 groups, complete; reveals concurrent staffing step-change at the workflow cutover |

## Data Validity

- Collection method: three flat-file exports frozen at 2026-06-22T23:59Z (per task statement); no live system access, no re-pull possible.
- Coverage matrix (workflow x severity x service_group, closed vs. open): incidents.csv is fully populated at this grain (420/420, 105 per workflow x service_group cell). activity.csv has a hole concentrated in one cell family: assist x sev1 (4 of 14 open), plus scattered assist sev2/sev3 opens; manual has essentially no hole (1 of 210). This hole sits exactly on the contrast the analysis needs (workflow x severity), so it is treated as a coverage gap requiring its own hypothesis (H4), not smoothed over by an aggregate closed-incident count.
- Field population: severity, workflow, service_group, intake_channel are 100% populated in incidents.csv. responder_minutes, handoffs, reopened_within_72h are 100% populated for the 409 closed rows; closed_at values all precede June 15, so reopened_within_72h has fully matured (72h clear of the June 22 extract) for every closed row — no censoring on that field specifically.
- Coverage baseline: staffing.csv's `incidents_opened` column is an independent daily count that matches incidents.csv's per-day, per-group totals (15/day/group throughout) — used as the coverage baseline for incidents.csv. No independent baseline exists for activity.csv's closure coverage; the 11-row gap is assessed against incidents.csv's opened_at timestamps and the known extract time instead (a maturation-window check, not an external denominator), so that gap is treated as a real finding, not fully independently verified.
- Known instrument failures: none beyond the closure-coverage gap above; no duplicate IDs, no negative/zero durations, no schema drift detected.
- Sensitivity checks performed: none yet requiring a known-positive check (no NON_DISCRIMINATING null result has been produced at Plan time); will apply per test in Analysis if a negative outcome arises, particularly for T3 where staffing and workflow are perfectly collinear at the daily grain and a clean discriminating result may not be obtainable.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1, H2 | pooled (unadjusted) time-to-close/responder-minutes gap between assist and manual shrinks substantially when computed within severity tiers instead of pooled | join incidents.csv+activity.csv on incident_id; compute median/mean time-to-close and responder-minutes by workflow overall, then by workflow x severity | NOT_TESTED | S1, S2 |
| T2 | H1 | within most/all severity tiers, assist still shows improvement over manual after T1's stratification | read off T1's stratified table | NOT_TESTED | S1, S2 |
| T3 | H3 | interruption_minutes and incidents-per-active-responder ease (fall) after the staffing increase, if added staff relieved pressure | compare staffing.csv's interruption_minutes and incidents_opened/active_responders before/after June 8 | NOT_TESTED | S3 |
| T4 | H4 | the 11 open incidents' elapsed time (extract_ts - opened_at) sits at/above the closed-sample's high percentiles for the same severity/workflow, and are concentrated in assist+high-severity | compute elapsed time for the 11 open incidents; compare to closed-incident duration distribution by severity | NOT_TESTED | S1, S2 |
| T5 | H5 | within sev1 (hardest tier), assist responder_minutes and/or handoffs exceed manual's | join S1+S2, filter severity=sev1 (and sev1+sev2), compare responder_minutes/handoffs by workflow | NOT_TESTED | S1, S2 |
| T6 | H2 | severity-mix-standardized responder-hours gap (assist vs. manual, common severity weights) is materially smaller than the naive pooled gap | reweight per-tier responder-minute rates by a common severity distribution (e.g. manual's mix) for both workflows; compare standardized totals to naive totals | NOT_TESTED | S1, S2 |
| T7 | H5 (supporting, non-necessary) | reopened_within_72h rate is not lower for assist than manual, especially within sev1 | compute reopen rate by workflow, and by workflow x severity | NOT_TESTED | S2 |

## Amendments

(none yet)

## Conclusion

(not yet reached — to be filled in after Analysis)
