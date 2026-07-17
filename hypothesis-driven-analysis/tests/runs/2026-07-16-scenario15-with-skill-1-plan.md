# Investigation: Did the Assist workflow cause faster incident recovery for the two pilot service groups (identity, storage), and how many responder-hours can be credibly attributed to it for the expansion decision?

## Problem

- Decision informed: whether to recommend expanding Assist company-wide at Monday's operations review, and what responder-hours-saved figure (if any) goes into the rollout plan for Finance.
- Falsifiable question: for incidents opened June 1–14 2026 in the `identity` and `storage` service groups, did the Assist workflow reduce time-to-close and responder-minutes relative to the manual workflow, net of confounds visible in the three local exports (`incidents.csv`, `activity.csv`, `staffing.csv`)?
- Success criteria: answered means either (a) a defensible causal effect estimate survives the named rival explanations, with a stated responder-hours figure and its uncertainty, or (b) a definitive statement that this design does not identify a causal effect, with each rival explanation's tested magnitude and a best-available associational estimate clearly labeled as such.
- Stop condition: conclude when no named unresolved alternative could reverse the expansion recommendation, or the effort budget is exhausted.
- Effort budget: 25 analysis queries against the local CSVs (no external/metered collection involved).

## Orientation (Plan-time, pre-outcome)

Performed before looking at any relationship between workflow and the outcomes (time-to-close, responder-minutes):

- `incidents.csv`: 420 rows, unique ids, `opened_at` June 1 00:20 UTC – June 14 23:32 UTC. `service_group` ∈ {identity, storage} (105/105 per workflow each — balanced). `severity` ∈ {sev1,sev2,sev3}. `intake_channel` ∈ {customer,monitor,partner}. `workflow` ∈ {assist,manual}.
- Workflow-by-date is a **clean, non-overlapping cutover**: every incident June 1–7 is `manual` (30/day), every incident June 8–14 is `assist` (30/day). Confirms the stated design — no holdout, single simultaneous switch, workflow perfectly collinear with calendar week.
- `activity.csv`: 409 rows, all fields populated (no nulls) where a row exists. **11 of 420 incidents have no activity row** — i.e., not yet closed as of the extract. Of those 11, **10 are `assist`-period and only 1 is `manual`-period** (assist non-closure rate 10/210 ≈ 4.8% vs manual 1/210 ≈ 0.5%). All 11 have been open 8.6–17.2 days at extract time (well past typical closure), skewed toward sev1 (5 of 11) and toward `identity` (8 of 11). This is a differential right-censoring pattern tied to the extract cutoff, not a schema/null problem — flagged as a data-artifact hypothesis (H3) with a concrete mechanism.
- `staffing.csv`: 28 rows (14 days × 2 groups), fully populated. `active_responders` and `scheduled_responder_hours` step up **on the same date as the Assist cutover, June 8**: identity 12→14 responders (94→~114 hrs/day), storage 11→13 responders (~87→~105 hrs/day). This is a concurrent capacity change co-occurring exactly with the workflow switch — flagged as a rival causal hypothesis (H4). `incidents_opened` is flat at 15/group/day throughout (no volume confound).
- Severity mix shifted sharply between periods: manual = 13.3% sev1 / 40.0% sev2 / 46.7% sev3; assist = 6.7% sev1 / 20.0% sev2 / 73.3% sev3. Channel and service-group mix are balanced across periods. The severity shift is a compositional confound — flagged as H2.
- No outcome (time-to-close, responder_minutes) has been computed by workflow yet; the above is coverage/composition/schema orientation only.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist workflow itself reduces incident time-to-close and responder-minutes | severity-stratified, censoring-adjusted TTC/responder-minutes are materially lower in assist than manual within most strata | adjustment removes most/all of the raw gap, or reverses it | the adjusted, within-stratum gap must remain materially in Assist's favor across most severity strata | T1, T3, T5 | incidents.csv, activity.csv |
| H2 | descriptive (estimand: share of the raw median/mean TTC gap attributable to the severity-mix shift, via direct standardization) | The mix shift toward sev3 (easier/faster) incidents during the assist week mechanically lowers the raw headline TTC/responder-minutes even with no workflow effect | mix-standardizing (applying manual's severity mix to each period's within-severity times) removes most (>50%) of the raw gap | standardizing barely moves the gap | standardization must remove >50% of the raw gap, or H2 is refuted as the primary driver | T1 | incidents.csv, activity.csv |
| H3 | descriptive (estimand: bias in the raw assist-period TTC/responder-hours figures caused by differential right-censoring of still-open incidents at the extract) | 10/210 assist incidents vs 1/210 manual incidents are still open at extract and excluded from the "closed" sample used for the headline; these excluded incidents skew toward sev1/hard cases, so the observed assist median/mean is biased low (faster-looking than reality) | assist censoring rate is much higher than manual's, and a lower-bound sensitivity adjustment (crediting open incidents with at least their elapsed-to-extract duration) narrows or eliminates the raw gap | censoring rates are similar across periods, or the sensitivity adjustment barely moves the numbers | assist censoring rate must exceed manual's materially AND the sensitivity bound must move the assist statistics upward non-trivially, or H3 is refuted | T2, T3 | incidents.csv, activity.csv |
| H4 | causal | The staffing/capacity increase that began June 8 (same date as the cutover) — not the Assist workflow — drives some or all of the apparent improvement | capacity increase (responders, scheduled hours per incident) is large enough in magnitude to plausibly explain a meaningful share of any observed TTC/responder-minutes change, and its timing exactly matches the cutover | capacity change is trivial in size, or its timing does not align with the outcome shift | the capacity increase must be a non-trivial fraction (materially >5-10%) of pre-cutover staffing, coincident with the cutover date, or H4 is refuted as a plausible confound | T4 | staffing.csv |

Both H1 and H4 are causal claims from a design with no concurrent control (workflow is perfectly collinear with calendar week, and a second exposure — staffing — changed at the identical moment). Per the skill's precedence rules, a failing within-design contrast on either can only leave the hypothesis `UNRESOLVED`, not `REFUTED`; only independent evidence not relying on the unidentified before/after contrast, or a genuinely descriptive test (H2, H3), can produce a `REFUTED` status here.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `.../s15-assist-rollout/incidents.csv` | 2026-07-16 (this session) | 420 rows, June 1–14 2026, all incidents opened in window; no missing fields observed |
| S2 | `.../s15-assist-rollout/activity.csv` | 2026-07-16 (this session) | 409 rows = incidents closed as of extract (2026-06-22T23:59Z); 11 incidents.csv ids absent (not yet closed); no nulls within present rows |
| S3 | `.../s15-assist-rollout/staffing.csv` | 2026-07-16 (this session) | 28 rows, daily × 2 service groups, June 1–14 2026, fully populated |

## Data Validity

- Collection method: frozen local CSV exports; `incidents.csv` and `staffing.csv` appear to be complete registries for their stated window/grain; `activity.csv` is an as-of snapshot of resolution activity taken 2026-06-22T23:59Z, so it necessarily omits incidents still open at that moment — this is a completeness/timing property of the source, not a defect, but it must be accounted for in any TTC/responder-minutes comparison.
- Coverage matrix (workflow × service_group, incidents.csv): manual/identity 105, manual/storage 105, assist/identity 105, assist/storage 105 — fully balanced, no gap.
- Coverage matrix (workflow × closure status, activity.csv join): manual closed 209/210 (99.5%), assist closed 200/210 (95.2%) — a real gap concentrated in assist, not uniform.
- Field population: activity.csv fields (closed_at, responder_minutes, handoffs, reopened_within_72h) are 100% populated for every row present; the gap is entirely rows absent, not nulls within rows — a schema/null audit would have missed this, which is why the join against incidents.csv was necessary.
- Coverage baseline: `incidents_opened` in staffing.csv (15/group/day, every day) is used as an independent denominator for incidents.csv volume — matches incidents.csv exactly (105 rows per workflow×group / 7 days = 15/day), confirming incidents.csv is not itself missing rows.
- Known instrument failures: none identified beyond the extract-timing right-censoring above.
- Sensitivity checks performed (planned, to run in Analysis): a lower-bound imputation for the 11 open incidents using elapsed time to extract, to test whether the raw headline is sensitive to their exclusion (T2/T3).

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1, H2 | Severity-standardizing the assist-period within-severity TTC distribution to manual's severity mix removes >50% of the raw median/mean TTC gap if H2 is the primary driver; if the gap survives standardization within most strata, that is consistent with (not proof of) H1 | Direct standardization: compute within-severity mean/median TTC for closed incidents in each period; reweight assist period by manual's severity shares; compare raw gap vs standardized gap | NOT_TESTED | S1, S2 |
| T2 | H3 | Assist-period non-closure rate is materially higher than manual's | Compare closure rate (activity.csv match) by workflow period | NOT_TESTED | S1, S2 |
| T3 | H1, H3 | Crediting the 11 open incidents with their elapsed-to-extract duration as a lower bound narrows or eliminates the raw/standardized assist-vs-manual gap | Recompute T1's standardized comparison including the censored incidents at their lower-bound elapsed duration; compare to T1's closed-only result | NOT_TESTED | S1, S2 |
| T4 | H4 | Staffing/capacity increase (responders, scheduled hours per incident) is a non-trivial (>10%) jump coincident with the June 8 cutover | Compute per-incident scheduled_responder_hours and active_responders before/after June 8 from staffing.csv | NOT_TESTED | S3 |
| T5 | H1 | Responder-minutes per incident (Finance's basis for hours-saved) shows the same severity-stratified pattern as TTC in T1 | Within-severity mean responder_minutes for closed incidents, manual vs assist, raw and standardized | NOT_TESTED | S1, S2 |
| T6 | consistency check (not a hypothesis row — requested by the task) | If Assist adds coordination overhead on genuinely hard incidents, sev1 closed incidents should show higher handoffs and/or reopen rate in assist vs manual | Compare handoffs and reopened_within_72h for sev1 closed incidents, manual vs assist | NOT_TESTED | S1, S2 |

## Amendments

(none yet)

## Conclusion

(pending — to be completed after Analysis)
