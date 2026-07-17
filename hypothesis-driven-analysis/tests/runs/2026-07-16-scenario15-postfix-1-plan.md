# Investigation: Did enabling Assist cause faster incident resolution in the pilot groups, and how many responder-hours can be credibly attributed to it?

## Problem

- Decision informed: whether to recommend expanding Assist company-wide at Monday's ops review, and what (if any) responder-hours figure to hand Finance for the rollout plan.
- Falsifiable question: did switching `identity` and `storage` from the manual workflow to Assist at 2026-06-08T00:00Z cause a reduction in incident time-to-close and/or responder-minutes, net of any severity-mix, staffing, and censoring differences between the manual week (Jun 1-7) and the assist week (Jun 8-14)?
- Success criteria: answered means, for both time-to-close and responder-minutes, we can state whether the change is attributable to Assist, better explained by a confound/artifact, or not identifiable from this data — plus either a defensible responder-hours figure or an explicit statement that none is defensible — and whether the responders' "extra work on difficult incidents" complaint is corroborated or not.
- Stop condition: conclude once severity-mix, staffing, and censoring confounds have been checked against both primary outcomes and no further check available in these three files could change the recommendation.
- Effort budget: 25 analysis queries over the local exports (no re-collection; the extract is frozen, not metered).

## Assignment mechanism (routing note)

Both pilot groups were switched to Assist in a single cutover at 2026-06-08T00:00Z; there was no holdout, no randomization, and no stated independence between assignment and the outcome — every incident's workflow is fully determined by when it opened. This is the "launched it, shipped to everyone, happened in a week when other things also happened" case the skill routes to **full**: nothing identifies the causal effect, and every co-occurring change (composition, staffing, censoring) is a live rival explanation, not noise to average away.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself reduces time-to-close and responder-minutes | within-severity-stratum comparison still favors assist after removing composition/staffing/censoring differences | within-stratum gap vanishes or reverses once matched on severity | assist must show shorter time-to-close / lower responder-minutes than manual **within the same severity stratum** | T1 | incidents.csv, activity.csv |
| H2 | descriptive (estimand: contribution of the severity-mix shift to the marginal time-to-close/responder-minutes gap) | The marginal "assist is faster" reading is a composition artifact: the assist week had a much lower share of sev1/sev2 and much higher share of sev3 | a severity-standardized comparison (assist's within-stratum medians reweighted to manual's severity mix) closes most or all of the raw marginal gap | standardized comparison leaves the gap materially intact | the standardized gap must shrink substantially versus the raw marginal gap | T1 | incidents.csv, activity.csv |
| H3 | causal | The apparent gain (if any) is driven by the staffing increase (active responders, scheduled hours) that started at the same cutover, not by Assist's mechanism | daily staffing level correlates with daily outcome measures, and the staffing increase alone is of comparable magnitude to the observed gap | no relationship between staffing and outcomes | staffing must show measurable independent variation from workflow to be tested at all | T2 | staffing.csv |
| H4 | data-artifact | The "faster in assist week" median is a right-censoring artifact: incidents still open at extract time are disproportionately assist-week and disproportionately severe, and are excluded from the closed-incident time-to-close calculation | censored assist incidents' elapsed time-to-date exceeds the closed-incident time-to-close distribution, and skews toward higher severity than the base rate | censored incidents are few, evenly distributed by workflow/severity, or short-elapsed | censored assist incidents' elapsed time must exceed typical closed time-to-close and/or skew toward higher severity for the artifact to be material | T3 | incidents.csv, activity.csv |
| H5 | descriptive (estimand: responder-minutes and handoffs for sev1/sev2 incidents by workflow) | Assist creates extra responder work specifically on genuinely difficult (high-severity) incidents, as some responders report | assist shows higher responder-minutes and/or handoffs than manual within sev1/sev2 | no difference or lower under assist | assist must show higher responder-minutes than manual in at least the sev1/sev2 strata | T4 | activity.csv |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `incidents.csv` — local frozen export | pre-existing, extract snapshot 2026-06-22T23:59Z | 420 incidents, 2026-06-01 through 2026-06-14, both pilot groups, no nulls observed in key fields |
| S2 | `activity.csv` — local frozen export | same extract | 409 rows (one per closed incident); 11 incidents in S1 have no row — still open at extract |
| S3 | `staffing.csv` — local frozen export | same extract | 28 rows = 14 days x 2 service groups, daily snapshot |

## Data Validity

- Collection method: three flat CSV exports pulled at a single point in time (2026-06-22T23:59Z); no streaming/live feed, so all fields reflect state as of that instant.
- Coverage matrix (workflow x service_group x severity, incident counts and closed-row completeness from S1/S2):
  - manual: identity/sev1 14 (100% closed), identity/sev2 42 (100%), identity/sev3 49 (98.0%); storage/sev1 14 (100%), storage/sev2 42 (100%), storage/sev3 49 (100%)
  - assist: identity/sev1 7 (57.1% closed), identity/sev2 21 (90.5%), identity/sev3 77 (97.4%); storage/sev1 7 (71.4%), storage/sev2 21 (100%), storage/sev3 77 (98.7%)
  - The manual week is essentially fully matured (>=98% closed in every cell); the assist week has a severe, severity-concentrated shortfall — under 60% closed for identity/sev1, the smallest and hardest cell.
- Field population: `closed_at`, `responder_minutes`, `handoffs`, `reopened_within_72h` are 100% populated for every row present in activity.csv — there is no null problem, only a row-absence (censoring) problem, which the coverage matrix above (not a null count) is what surfaces it.
- Coverage baseline: no independent "incidents still open" counter exists in these exports; the baseline used is the internal one available — set difference between incidents.csv ids and activity.csv ids, cross-checked against each open incident's opened_at vs the extract timestamp (elapsed days so far). Recorded as the best available check, not an independent-system baseline.
- Known instrument failures: none documented; the shortfall above is a real censoring pattern (asymmetric maturation window: assist incidents opened Jun 8-14 had 8-14 days to close by the Jun 22 extract, vs 15-21 days for manual incidents), not a logging gap.
- Sensitivity checks performed: the same workflow x field crosstab method applied to `intake_channel` (a field not expected to shift with the cutover) shows a roughly stable mix (customer ~29-31%, monitor ~34-38%, partner ~33-36% in both weeks) — confirming the method is not spuriously finding imbalance everywhere, which makes the severity-mix imbalance found for H2 (sev1 13.3%->6.7%, sev3 46.7%->73.3%) a credible signal rather than a detection artifact.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1, H2 | assist beats manual within every severity stratum (H1) vs. a severity-standardized comparison closes/reverses the raw marginal gap (H2) | compute median time-to-close and responder-minutes by workflow, marginal and stratified by severity (S1 join S2); reweight assist's within-stratum medians to manual's severity mix | NOT_TESTED | S1, S2 |
| T2 | H3 | daily staffing correlates with outcomes independent of workflow | check within-week variation in active_responders/scheduled_responder_hours against the workflow step, and magnitude-compare the staffing change to the observed marginal gap | NOT_TESTED | S3 |
| T3 | H4 | censored assist incidents' elapsed time exceeds closed-incident time-to-close, and skews high-severity | compute elapsed days (opened_at to extract) for the 11 open incidents; compare against closed time-to-close distributions and against baseline severity shares | NOT_TESTED | S1, S2 |
| T4 | H5 | assist shows higher responder-minutes (and handoffs, as a secondary check) than manual within sev1/sev2 | compute median responder-minutes and handoffs by workflow within each severity stratum (S1 join S2) | NOT_TESTED | S2 |

## Amendments

(none yet)

## Conclusion

(pending — populated after Tests run)
