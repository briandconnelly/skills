# Investigation: Did enabling Assist cause faster incident resolution, and how many responder-hours can we credit to it for the expansion decision?

## Problem

- Decision informed: whether to recommend expanding Assist company-wide at Monday's operations review, and whether Finance's responder-hours-saved figure can be booked in the rollout plan.
- Falsifiable question: for incidents opened 2026-06-01 through 2026-06-14 across the identity and storage service groups, is the change from the manual workflow (week of June 1) to the Assist workflow (week of June 8) associated with — and, so far as this data can identify, caused by — a reduction in time-to-close and responder-minutes, and if so, how large and how attributable is it?
- Success criteria: answered means the raw before/after gap in time-to-close and responder-minutes is quantified, and each plausible non-Assist explanation (severity-mix shift, staffing/interruption shift, differential right-censoring, difficulty-subgroup reversal) is checked against its own necessary prediction, so the memo states clearly what can and cannot be attributed to Assist and what responder-hours figure (if any) is defensible.
- Stop condition: conclude when no named unresolved alternative could reverse the expansion recommendation; the design is a single company-wide cutover with workflow perfectly collinear with calendar date and no holdout, so conclude with limits once the descriptive facts are quantified rather than waiting for an identified causal estimate that this data cannot produce.
- Effort budget: ~12 analysis computations (script/aggregation passes over the three CSVs); same-day wall-clock (leadership needs this today).

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself causes faster time-to-close and lower responder-minutes | closed-incident time-to-close and responder-minutes are lower in the assist week than the manual week | no raw gap, or gap in the wrong direction | assist closed-incident median time-to-close and median responder-minutes must be lower than manual's, at minimum, for a positive causal effect to be plausible | T1 | incidents.csv, activity.csv |
| H2 | descriptive (estimand: share of the raw gap explained by the June-8 severity-mix shift) | The incident mix shifted toward sev3 (lighter) incidents at the same cutover, and severity itself predicts duration, so part or all of the apparent speed-up is compositional, not workflow-driven | severity predicts duration (sev3 faster) in single-workflow data, and reweighting the manual period to the assist week's severity mix closes a material share of the raw gap | severity has no relationship to duration, or reweighting explains a negligible share | severity must predict duration (sev3 median close time below sev1/sev2) within the manual-only period, where workflow is held constant | T2, T3 | incidents.csv, activity.csv |
| H3 | descriptive (estimand: coincidence of a staffing/interruption-level step change with the workflow cutover) | active_responders and interruption_minutes both stepped at the same June 8 boundary as the workflow change, giving an independent resource-based rival explanation | staffing.csv shows a material (>10%) jump in active_responders and/or interruption_minutes exactly at the cutover date | staffing and interruption levels are flat across the cutover | active_responders per service group must not be flat across June 7→June 8 | T4 | staffing.csv |
| H4 | descriptive (estimand: differential right-censoring of open incidents by workflow arm, and its effect on the closed-incident summary statistics and on any responder-hours total) | Incidents with no activity.csv row (still open at the 2026-06-22 extract) are concentrated in the assist arm and are far longer-running than any closed incident, so excluding them from "closed" statistics mechanically favors assist and understates responder-minutes actually consumed by assist incidents | open incidents skew heavily toward the assist workflow, and their elapsed time as of the extract exceeds the longest observed closed duration | open incidents are evenly split by workflow and/or their elapsed time is comparable to typical closed durations | open (uncensored-outcome) incidents must not be evenly split ~50/50 between workflows given service groups switched together | T5, T6 | incidents.csv, activity.csv |
| H5 | descriptive (estimand: sev1-subgroup non-closure rate and, among closed sev1 incidents, responder-minutes/handoffs, assist vs manual) | Among the hardest (sev1) incidents, Assist incidents are less likely to close within the observation window and/or consume more responder-minutes/handoffs when they do close, consistent with responders' complaint that Assist adds work on genuinely difficult incidents | assist sev1 non-closure rate is materially higher than manual sev1 non-closure rate | sev1 non-closure and responder-minutes/handoffs are comparable or better under assist | assist sev1 non-closure rate must not be lower than or equal to manual's | T7, T8 | incidents.csv, activity.csv |

H1 is a causal claim over an unstated-until-now design: the service owners confirm a single, company-wide cutover with no holdout and workflow fully determined by calendar date. Per the skill's design rule, this contrast (raw or standardized) cannot by itself mark H1 REFUTED or promote it past UNRESOLVED — a co-occurring change (H2/H3/H4/H5, or others unmeasured) could mask or manufacture the appearance of an effect. T1's outcome will be recorded as observed, but H1's status derivation in the Conclusion will apply that carve-out explicitly.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `incidents.csv` (frozen local export) | task start, 2026-07-16 | 420 rows, incidents opened 2026-06-01T00:20Z–2026-06-14T23:32Z; no duplicate incident_ids; no empty fields; workflow is perfectly collinear with opened_at date (manual = June 1–7, assist = June 8–14, no overlap) |
| S2 | `activity.csv` (frozen local export) | task start, 2026-07-16 | 409 rows against 420 incidents (97.4% closed); extract taken 2026-06-22T23:59Z; no duplicate incident_ids, no empty fields, no closed_at earlier than opened_at; closed-incident duration range 121–1919 minutes (2h–32h) |
| S3 | `staffing.csv` (frozen daily operating snapshot) | task start, 2026-07-16 | 28 rows = 14 days × 2 service groups; complete, no gaps |

## Data Validity

- Collection method: three frozen local CSV exports; incidents.csv presumably from the incident tracker, activity.csv resolution activity as recorded as of the 2026-06-22T23:59Z extract, staffing.csv a daily operating snapshot per service group. No system-of-record cross-check is possible; these are the only records available.
- Coverage matrix (incident counts, at the workflow × severity × service_group grain the hypotheses use):
  - workflow × severity: manual = {sev1:28, sev2:84, sev3:98} (n=210); assist = {sev1:14, sev2:42, sev3:154} (n=210). Sev3 share rises from 46.7% (manual) to 73.3% (assist); sev1 share falls from 13.3% to 6.7%.
  - workflow × service_group: manual = {identity:105, storage:105}; assist = {identity:105, storage:105} — balanced, both groups cut over together as stated.
  - workflow × intake_channel: roughly stable proportions across the cutover (not a likely confound).
  - date × workflow: 30 incidents/day every day, manual strictly June 1–7 and assist strictly June 8–14 — confirms workflow is a deterministic function of calendar date with no holdout and no overlap, exactly as the service owners described.
- Field population: opened_at, service_group, severity, intake_channel, workflow are 100% populated in incidents.csv (420/420). closed_at/responder_minutes/handoffs/reopened_within_72h in activity.csv are populated for 409/420 incidents (97.4%) — but this aggregate rate hides a severe imbalance: 11 incidents have no activity.csv row at all (i.e., still open at extract time), and 10 of those 11 (91%) are assist-workflow incidents versus the 50/50 split the balanced design would predict. The 11th (manual) is a sev3 incident. Of the 10 open assist incidents, 5 are sev1 (out of only 14 assist sev1 incidents total — a 36% non-closure rate for the highest-severity assist incidents, versus 0/28 for manual sev1).
- Coverage baseline: no independent denominator (e.g., a separate incident-count feed) is available to cross-check total incident volume; incidents_opened in staffing.csv matches incidents.csv's daily counts exactly (15+15=30/day per the two groups), which is at least an internal consistency check, not an independent one. For the censoring question, the internal baseline is the observed closed-duration range (121–1919 minutes, i.e., up to ~32 hours): the 11 open incidents' elapsed time as of the extract ranges 205–412 hours (8.5–17 days) — 6 to 13× longer than the longest closed incident on record. This is not a subtle gap; the open incidents sit far outside the entire observed closed distribution.
- Known instrument failures: none documented; the extract-timing note in the prompt ("even the newest incidents had at least seven full days to mature") suggests the 11 open incidents are not simply too new to have closed yet — they are incidents that, for whatever reason, have not closed despite ample time.
- Sensitivity checks performed: none yet requiring a known-positive check (no metered/aggregated source is being trusted blind here — all three files are read in full and reconciled row-by-row: incident_id counts, join completeness, and date/workflow crosstabs all check out against each other).

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | assist closed-incident median time-to-close and median responder-minutes < manual's | join incidents.csv + activity.csv on incident_id, restrict to closed incidents, compute median/mean time-to-close (closed_at − opened_at) and responder_minutes by workflow | NOT_TESTED | S1, S2 |
| T2 | H2 | within manual-only data, sev3 median time-to-close < sev2 < sev1 | compute median time-to-close by severity, manual workflow only (holds workflow constant) | NOT_TESTED | S1, S2 |
| T3 | H2 | reweighting manual's within-severity medians by assist's severity-share closes a material part of the T1 gap | direct standardization: apply assist severity shares to manual within-severity medians, compare synthetic figure to raw manual and raw assist figures | NOT_TESTED | S1, S2 |
| T4 | H3 | active_responders and/or interruption_minutes step up materially at the June 7→8 boundary, same date as the workflow cutover | compare staffing.csv daily figures pre- vs post-cutover per service group | NOT_TESTED | S3 |
| T5 | H4 | open (uncensored-outcome) incidents concentrate in the assist arm and their elapsed time exceeds the max closed duration | set-difference incidents.csv incident_ids against activity.csv, tabulate by workflow/severity, compare elapsed-to-extract against max closed duration | NOT_TESTED | S1, S2 |
| T6 | H4 | under low/high bounding assumptions for the 10 open assist incidents' eventual responder-minutes, the "hours saved" figure materially narrows or reverses | bound the missing responder-minutes using (a) current assist closed-arm mean, (b) max observed closed duration, (c) incidents' current elapsed time as a floor; recompute total/average responder-minutes under each bound | NOT_TESTED | S1, S2 |
| T7 | H5 | assist sev1 non-closure rate materially exceeds manual sev1 non-closure rate | restrict to severity=sev1, compute share with no activity.csv row, by workflow | NOT_TESTED | S1, S2 |
| T8 | H5 | among closed sev1 incidents, assist responder-minutes/handoffs are not lower than manual's | restrict to severity=sev1 AND closed, compare median responder_minutes and handoffs by workflow | NOT_TESTED | S1, S2 |

## Amendments

(none yet — plan-time snapshot)

## Conclusion

(not yet reached — plan-time snapshot; to be completed after Tests run)
