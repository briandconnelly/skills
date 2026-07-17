# Investigation: Did the Assist workflow cause faster incident recovery in the pilot, and how many responder-hours can we credibly attribute to it?

## Problem

- Decision informed: whether Monday's operations review recommends expanding Assist company-wide, and whether Finance books a responder-hours savings figure into the rollout plan.
- Falsifiable question: for incidents opened June 1-14 in the identity and storage service groups, did the June 8 00:00 UTC cutover to the Assist workflow cause a reduction in time-to-close and/or responder-minutes, net of any confounds that moved at the same time?
- Success criteria: answered means we can state, with named evidence, whether the observed before/after change is attributable to Assist versus identified confounds, and either produce a defensible responder-hours estimate with its basis or state explicitly why the data cannot support one.
- Stop condition: conclude once (a) the naive aggregate contrast, (b) a severity-stratified/reweighted contrast, (c) a censoring-adjusted contrast, and (d) a difficulty-interaction check on the hardest incidents have all been run; iterate only if a specific further test could still reverse the answer within budget.
- Effort budget: ~20 analysis steps (python/bash queries over the three local CSVs).

## Plan orientation (pre-registration findings; no cause-outcome relationship inspected)

- 420 incidents, June 1-14, exactly 15/day/group, 210 identity / 210 storage, split exactly 210 manual / 210 assist along the June 8 00:00 UTC cutover.
- 409/420 incidents have a matching activity (closure) row; 11 have none (no `closed_at`) at extract time.
- Of those 11 unresolved incidents, 10 belong to the `assist` period and only 1 to `manual`; 9 of the 10 assist-period ones are identity; 5 of the 11 are sev1.
- Severity mix differs sharply by period: manual = 13.3% sev1 / 40.0% sev2 / 46.7% sev3; assist = 6.7% sev1 / 20.0% sev2 / 73.3% sev3. Intake-channel mix and service-group split are balanced across periods.
- `staffing.csv`: active_responders and scheduled_responder_hours step up for both service groups on exactly June 8 (identity 12→14, storage 11→13) — the same date as the Assist cutover, with no within-period variation in staffing. interruption_minutes also rises sharply after June 8 (roughly 5-44/day before, 13-110/day after).
- No independent denominator (e.g., a separate ticketing total) exists to validate incident-count coverage; the exact 15/day/group regularity is internally consistent but unverifiable against an outside source.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist workflow itself reduces time-to-close / responder-minutes | severity-stratified, censoring-aware contrast shows assist ≤ manual in most adequately-sized strata | stratified/adjusted contrast shows no advantage or a reversal | the severity-stratified, censoring-adjusted contrast must show an assist advantage in the majority of strata with n≥15; because no holdout/randomization exists, failure here can only leave H1 `UNRESOLVED`, not `REFUTED` (per skill precedence for unidentified causal contrasts) | T1 (naive), T2 (stratified/reweighted) | incidents.csv, activity.csv |
| H2 | causal | Concurrent staffing increase (not Assist) explains the change | some staffing variation independent of the workflow cutover exists that lets the two be separated | staffing changes exactly coincide with the workflow cutover for both groups with zero within-period variation | independent (non-collinear) staffing variation must exist to test this claim at all | T5 | staffing.csv |
| H3 | causal (descriptive estimand: share of the aggregate median/mean gap explained by severity-mix composition) | The severity-mix shift toward more sev3 / fewer sev1 in the assist period explains most of the aggregate "faster" result, not any per-incident speedup | reweighting manual incidents to the assist period's severity mix reproduces most (>50%) of the observed aggregate gap | reweighted gap is close in size to the unadjusted aggregate gap | reweighting must reproduce a majority of the observed aggregate gap for H3 to hold; a reweighted gap similar in size to the raw gap refutes composition as the primary driver | T2 | incidents.csv, activity.csv |
| H4 | data-artifact | Right-censoring (still-open incidents excluded from "time to close") makes the assist period look faster than it is | open-incident rate is higher and severity-skewed in the assist period, and a censoring-aware bound (elapsed time to extract for open incidents) materially narrows or reverses the naive assist advantage, especially for sev1 | open rate similar across periods, or the adjustment leaves the gap materially unchanged | open-incident rate must be higher in assist than manual (already true structurally: 10/210 vs 1/210) and the adjusted contrast must show a materially smaller assist advantage than the naive one; only a check that actually probes coverage/missingness can refute a data-artifact claim | T3 | incidents.csv, activity.csv |
| H5 | causal | Assist increases burden specifically on the hardest (sev1) incidents even as the aggregate looks better, matching responder complaints | sev1 assist incidents show higher responder-minutes and/or handoffs and/or a higher unresolved rate than sev1 manual incidents | sev1 assist incidents are comparable to or better than sev1 manual on these measures | sev1 assist median responder-minutes or handoffs must be ≥ sev1 manual, or sev1 unresolved rate must be clearly higher, for this hypothesis to hold | T4 | incidents.csv, activity.csv |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `tests/fixtures/s15-assist-rollout/incidents.csv` | read locally 2026-07-16 | 420 rows, June 1-14, opened_at/service_group/severity/intake_channel/workflow; no nulls observed in key fields |
| S2 | `tests/fixtures/s15-assist-rollout/activity.csv` | read locally 2026-07-16 | 409 rows keyed by incident_id; closed_at/responder_minutes/handoffs/reopened_within_72h; 11 incidents from S1 have no matching row (unresolved at extract) |
| S3 | `tests/fixtures/s15-assist-rollout/staffing.csv` | read locally 2026-07-16 | 28 rows = 14 days × 2 service groups; active_responders, scheduled_responder_hours, interruption_minutes, incidents_opened |

## Data Validity

- Collection method: three frozen local CSV exports pulled 23:59 UTC June 22; incidents.csv logs every incident opened June 1-14 with the workflow active at open time; activity.csv logs resolution activity as of the extract; staffing.csv is a daily operating snapshot per service group.
- Coverage matrix (date × service_group × workflow, incidents opened vs. matched activity rows): uniform 15 incidents/day/group across all 14 days (420 total, 210/210 manual-assist, 210/210 identity-storage — no gaps). Matched-activity shortfall is concentrated entirely in the assist period: 1 missing in manual (2026-06-05, identity), vs. 10 missing in assist, spread across 2026-06-08, 06-10, 06-11, 06-12, 06-13, 06-14, mostly identity (9 of 10).
- Field population: `closed_at`/`responder_minutes`/`handoffs` are 97.4% populated overall (409/420) but the 2.6% gap is not random — it is 10x more likely in the assist period than the manual period and skews toward sev1 (5 of 14 assist sev1 incidents, 35.7%, are unresolved at extract vs. 0 of 28 manual sev1 incidents). `severity`, `service_group`, `intake_channel`, `workflow`, `opened_at` are 100% populated in S1.
- Coverage baseline: no independent denominator (e.g. a separate ticketing system count) exists to confirm the 15/day/group regularity is genuine and not itself an artifact of the extract; recorded as unverifiable rather than clean. The incidents↔activity join itself is used as an internal cross-check (see above) and is sufficient to detect the censoring pattern even without an external baseline.
- Known instrument failures: right-censoring at the June 22 23:59 UTC extract boundary — incidents opened June 8-14 have had 8-14 days to close, but any incident still open at extract time is absent from activity.csv entirely rather than flagged as open, so a naive time-to-close computation silently drops it.
- Sensitivity checks performed: the censoring pattern (10/210 assist vs 1/210 manual unresolved) is large relative to the overall 2.6% missing rate and concentrated in exactly the severity band (sev1) most likely to drive median time-to-close, so this is not a detection-limit-bound null result — it is a directional, severity-skewed asymmetry visible at raw counts.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | naive assist median time-to-close/responder-minutes (closed incidents only) is lower than manual | join S1+S2, compute time-to-close = closed_at - opened_at and responder_minutes, group by workflow, median/mean | NOT_TESTED | |
| T2 | H1, H3 | severity-stratified contrast and severity-reweighted counterfactual should show whether the aggregate gap survives holding severity mix constant | group S1+S2 by severity × workflow; compute per-stratum medians; reweight manual distribution to assist's severity mix and compare to raw assist median | NOT_TESTED | |
| T3 | H4 | open-incident rate and a censoring-aware lower-bound adjustment should show whether the assist advantage survives accounting for still-open incidents | compute open rate by workflow/severity; compute elapsed time-to-extract (2026-06-22T23:59Z - opened_at) for the 11 open incidents as a lower bound; recompute assist-period central tendency including these as censored lower bounds | NOT_TESTED | |
| T4 | H5 | sev1 assist responder-minutes/handoffs/unresolved-rate should be ≥ sev1 manual if Assist burdens hard incidents | filter S1+S2 to sev1, compare workflow groups on responder_minutes, handoffs, reopened_within_72h, and unresolved rate | NOT_TESTED | |
| T5 | H2 | staffing must show independent (non-collinear) variation from the workflow cutover to be testable | inspect S3 for within-period staffing variation by service group | NOT_TESTED | |

## Amendments

(none yet)

## Conclusion

(pending — filled in after Tests run)
