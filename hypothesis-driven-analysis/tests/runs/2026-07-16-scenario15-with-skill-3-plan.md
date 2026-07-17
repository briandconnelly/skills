# Investigation: Did enabling Assist cause faster incident recovery, and how many responder-hours can be credited to it?

## Problem

- Decision informed: whether to recommend company-wide expansion of the Assist workflow at Monday's operations review, and whether to book a responder-hours savings figure into the rollout plan.
- Falsifiable question: for incidents opened 2026-06-01 through 2026-06-14 in the identity and storage pilot service groups, did the Assist workflow (active from 2026-06-08T00:00Z) cause a reduction in time-to-close and responder-minutes relative to what would have happened under the manual workflow, and if so, how large is the credible responder-hours effect?
- Success criteria: answered means (a) each candidate explanation for the observed week-over-week change has a discriminating test outcome, (b) the causal claim is either best-supported net of identified confounds or the evidence establishes it is not identifiable/not supported from this design, and (c) a responder-hours figure is either produced with its estimand and uncertainty stated, or explicitly withheld with the reason.
- Stop condition: conclude when no named unresolved alternative could reverse the expansion recommendation, or the effort budget is exhausted.
- Effort budget: 30 tool calls (bash/analysis commands).

## Orientation findings (schema, coverage, provenance — no cause/outcome relationship inspected)

- incidents.csv: 420 rows, 2026-06-01..2026-06-14, two service groups (identity, storage) at 210 each, exactly 15 incidents/group/day, 30/day total, no gaps.
- `workflow` field is a clean calendar cutover: every incident opened 06-01..06-07 is `manual` (210), every incident opened 06-08..06-14 is `assist` (210). No mixing within a day. This confirms the "every pilot incident followed the workflow active when it opened" claim structurally.
- Severity mix is NOT stable across the two weeks: manual week = 28 sev1 / 84 sev2 / 98 sev3 (210); assist week = 14 sev1 / 42 sev2 / 154 sev3 (210). Sev3 share rises from 46.7% to 73.3%; sev1 and sev2 counts both halve. This is a candidate confound (severity plausibly drives time-to-close independent of workflow) and is registered as H2 below.
- staffing.csv: 28 rows (14 days x 2 groups), `incidents_opened` reconciles exactly against incidents.csv's independently-derived daily/group counts (used as the coverage baseline — an independent denominator, not just an internal total). active_responders and scheduled_responder_hours step up at the same 06-08 cutover (identity 12->14 responders, 93-99->112-115 sched. hours/day; storage 11->13 responders, 84-90->100-107 sched. hours/day). interruption_minutes also rises sharply in the assist week for both groups. Both are candidate confounds co-occurring with the workflow switch, registered as H3.
- activity.csv: 409 rows. Exactly 11 incident_ids in incidents.csv have no matching activity.csv row (verified by id set-difference) — these are still open at the 2026-06-22T23:59Z extract despite the newest incident having 7+ full days to mature. 10 of the 11 open incidents are in the assist week (1 in manual week), and open incidents skew toward sev1 (5 of 11, vs sev1 being ~10% of all incidents). This is a right-censoring pattern strongly asymmetric by week and correlated with severity — registered as H4.
- No empty/missing fields anywhere in incidents.csv or activity.csv (full per-field scan). staffing.csv fully populated. No instrument gaps beyond the open-incident right-censoring above, which is a real feature of the extract, not a data defect.
- Coverage matrix (grain: day x service_group x workflow, crossed with severity where used): every day/group cell has exactly 15 incidents; workflow is fully determined by date; severity counts per week x group are as above (7/21/77 assist per group, 14/42/49 manual per group) — even split across the two service groups within each week, so service_group is not itself confounded with the mix shift.
- Coverage baseline: incidents.csv daily counts cross-checked against staffing.csv's independently recorded `incidents_opened` column — exact match on all 28 day/group cells, so incident-record coverage is verified, not assumed.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself reduces time-to-close and responder-minutes | severity-stratified median TTC/responder-minutes lower under assist in most strata, net of the mix shift | stratified comparison shows no consistent assist advantage once severity is held fixed | assist-week median TTC must be <= manual-week median TTC in a majority (>=2 of 3) of severity strata, weighted by incident volume | T1 | S1, S2 |
| H2 | descriptive (estimand: share of the raw median-TTC drop attributable to the severity-mix shift) | the observed raw drop is substantially a composition effect: sev3 (faster-closing) grew from 47% to 73% of volume | counterfactual reweighting of assist-week per-severity times onto the manual-week severity mix reproduces most of the raw drop | reweighting reproduces little of the raw drop | reweighted gap must reproduce >=50% of the raw gap for the mix shift to count as a substantial driver | T2 | S1, S2 |
| H3 | causal | added staffing capacity (more responders/scheduled hours), not the workflow, drove faster closure | effective capacity (scheduled hours net of interruptions, per incident opened) rises in the assist week | effective capacity is flat or falls once interruption time is netted out | net effective capacity per incident must be higher in the assist week than the manual week | T3 | S3 |
| H4 | descriptive (estimand: bias in the assist-week raw closed-incident median from right-censoring) | the assist week's much higher still-open rate, skewed toward sev1, biases its "closed-only" median downward vs. a censoring-aware estimate | censored/open incidents are disproportionately assist-week AND skew toward slower-resolving severities | censoring rate and severity skew are similar across weeks | open-incident rate must be higher in the assist week than the manual week AND skew toward severities with longer typical closed-sample TTC | T4 | S1, S2 |
| H5 | causal | Assist increases responder burden (minutes/handoffs) specifically on the hardest incidents, even if overall medians fall | within the sev1 (hardest) stratum, median responder-minutes or handoffs is higher under assist than manual | sev1-stratum responder-minutes/handoffs is not higher under assist | sev1-stratum median responder-minutes (or handoffs) must be higher, not lower, under assist for this to hold as an explanation of the responder complaints | T5 | S2 |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `tests/fixtures/s15-assist-rollout/incidents.csv` | frozen local export, extract 2026-06-22T23:59Z | 420 rows, full daily/group coverage, no nulls |
| S2 | `tests/fixtures/s15-assist-rollout/activity.csv` | frozen local export, extract 2026-06-22T23:59Z | 409 rows = 420 incidents minus 11 still-open (right-censored); no nulls among present rows |
| S3 | `tests/fixtures/s15-assist-rollout/staffing.csv` | frozen local export, extract 2026-06-22T23:59Z | 28 rows (14 days x 2 groups), incidents_opened reconciles exactly to S1 |

## Data Validity

- Collection method: three frozen local CSV exports taken at a single point in time (2026-06-22T23:59Z). incidents.csv covers every incident opened in the window; activity.csv covers resolution activity recorded as of the extract (absence = still open at extract time); staffing.csv is a daily per-service-group operating snapshot.
- Coverage matrix: day x service_group is fully populated (15 incidents/group/day, no gaps) across all 14 days for both incidents.csv and staffing.csv. workflow is a deterministic function of date (no within-day mixing). activity.csv coverage is 409/420; the 11-row gap is fully accounted for by explicit incident_id match (not a random or unexplained hole), and is asymmetric: 1/210 manual-week incidents still open vs 10/210 assist-week incidents still open.
- Field population: 100% populated on every field in all three files (verified by per-field empty-string scan); no null/missingness problem distinct from the censoring gap above.
- Coverage baseline: incidents.csv's daily/group incident counts reconcile exactly against staffing.csv's independently recorded `incidents_opened` column (28/28 cells match) — an independent denominator, not a self-referential total, so incident-record coverage is verified clean rather than assumed.
- Known instrument failures: none found. The only material gap is the 11 still-open incidents; per the extract note (>=7 days maturity even for the newest incident), these are not "too new to have closed" — they are incidents that have genuinely not closed within a week or more, concentrated in the assist week and in sev1.
- Sensitivity checks performed: the censoring-rate asymmetry (0.5% manual vs 4.8% assist, 1 vs 10 events out of 210 each) is large relative to plausible single-incident noise and will be tested formally in T4 rather than assumed; the severity-mix shift (28/84/98 -> 14/42/154) is likewise large enough to test as a substantial compositional driver in T2 rather than dismissed.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | assist-week median TTC/responder-minutes <= manual-week in >=2 of 3 severity strata | compute median TTC and responder-minutes per severity x workflow from S1 join S2 (closed incidents only, noting censoring) | NOT_TESTED | |
| T2 | H2 | reweighting assist-week per-severity medians onto manual-week severity mix reproduces >=50% of the raw median-TTC drop | counterfactual reweighting calculation on S1/S2 | NOT_TESTED | |
| T3 | H3 | net effective capacity (scheduled hours net of interruption minutes, per incident opened) is higher in assist week | compute from S3: (scheduled_responder_hours*60 - interruption_minutes) / incidents_opened, by week x group | NOT_TESTED | |
| T4 | H4 | open-incident rate higher in assist week, skewed toward slower-resolving severities | compare open/closed counts and severity mix of the 11 open incidents (S1) against closed-sample per-severity TTC (S2) | NOT_TESTED | |
| T5 | H5 | sev1-stratum median responder-minutes/handoffs higher under assist | compute median responder-minutes and handoffs for sev1 subset, manual vs assist, from S1 join S2 | NOT_TESTED | |

## Amendments

(none at plan time)

## Conclusion

(to be completed after Analysis)
