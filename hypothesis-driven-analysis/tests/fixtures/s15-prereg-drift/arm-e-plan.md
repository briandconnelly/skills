# Investigation: Did enabling Assist cause faster incident recovery, and how many responder-hours can be credibly attributed to it?

## Problem

- Decision informed: whether to recommend company-wide expansion of the Assist workflow at Monday's operations review, and what responder-hours figure (if any) is defensible to book in the rollout plan.
- Falsifiable question: for incidents opened 2026-06-01 through 2026-06-14 in the two pilot service groups (identity, storage), did the Assist workflow (active from 2026-06-08T00:00Z) cause a reduction in time-to-close and/or responder-minutes, relative to the manual workflow active 2026-06-01 through 2026-06-07 — and if an effect is identifiable, what responder-hours figure can be credibly attributed to it?
- Success criteria: answered means (a) each rival explanation for the observed before/after difference has a discriminating test outcome, (b) the causal claim is marked per the identification rules (single simultaneous cutover with no holdout is not a randomized or plausibly-independent assignment, so any exposure-outcome contrast can move the hypothesis at most to UNRESOLVED, never REFUTED, absent independent falsifying evidence), and (c) a stated responder-hours number, an explicit "not credibly separable from confounds" verdict, or a bounded range — whichever the data supports.
- Stop condition: conclude when every named rival explanation (staffing confound, censoring/maturity artifact, incident-mix shift) has a recorded test outcome and no remaining named alternative could change the expansion recommendation within budget.
- Effort budget: 25 Python/analysis queries over the three local CSVs (cheap, uncensored local files; no metering).

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | The Assist workflow itself causally reduces time-to-close and/or responder-minutes for pilot incidents | after controlling for the staffing confound, the censoring artifact, and incident-mix shift, an Assist-vs-manual gap in time-to-close/responder-minutes persists in the direction Assist claims | the gap disappears, reverses, or cannot be distinguished from confounds once controlled | none available that isn't itself the unidentified pre/post contrast — this row can be moved to UNRESOLVED by an inadequate test but not REFUTED by one; only a failure of a prediction independent of the confounded contrast could refute it | T1 (adjusted contrast), T5 (independent-evidence check) | incidents.csv, activity.csv |
| H2 | causal | The staffing increase that began exactly at the June 8 cutover (not Assist) drives the observed drop | staffing.csv shows more active_responders/scheduled_responder_hours starting 06-08; time-to-close improves in proportion to added capacity, independent of workflow | staffing is flat across the cutover, or the improvement doesn't track staffing capacity | staffing levels must not change coincident with the cutover — if active_responders/scheduled_responder_hours are flat across 06-07→06-08, this rival is refuted | T2 | staffing.csv |
| H3 | data-artifact | Right-censoring inflates the apparent Assist improvement: incidents opened in the Assist window that are still open at the 06-22 23:59Z extract (and thus absent from activity.csv) are disproportionately the slow/hard ones, so excluding them mechanically deflates the assist-arm median/mean | the still-open (activity-less) incidents are concentrated in the Assist arm and skew toward higher severity vs. their workflow's base rate | still-open incidents are evenly distributed across workflow and severity in proportion to each arm's share | the still-open share and severity skew must not be disproportionately concentrated in the Assist arm — even distribution refutes this as an explanation for the gap | T3 | incidents.csv, activity.csv coverage check |
| H4 | causal | A shift in incident-mix (severity or intake-channel composition) between the manual week and the Assist week, not the workflow, drives the observed gap | severity/channel composition differs materially manual-week vs. assist-week; reweighting one week's mix onto the other's per-severity durations closes most of the naive gap | composition is stable across weeks, or reweighting does not materially change the gap | mix must differ materially between weeks and reweighting must close a majority of the gap — if composition is stable, this rival is refuted | T4 | incidents.csv |
| H5 | descriptive (estimand: median/mean responder-minutes and handoffs for closed sev1 incidents, assist vs. manual) | Assist adds responder work specifically on the hardest (sev1) incidents, consistent with responders' complaint, even where aggregate figures look favorable | among closed sev1 incidents, assist shows higher responder-minutes and/or handoffs than manual | no material difference, or assist lower too | closed-sev1 assist median responder-minutes/handoffs must exceed manual's — if not, refuted for this slice (caveat: this comparison is itself subject to the same censoring risk as H3, since the hardest sev1 assist incidents may be the ones still open) | T6 | activity.csv joined to incidents.csv |

Hypotheses are candidate explanations for the *same* observed before/after gap; H1 is the claim under test, H2-H4 are rivals that could produce the same observed pattern without Assist being the cause, and H5 addresses the responders' separate anecdotal complaint.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `incidents.csv` — every incident opened 2026-06-01 through 2026-06-14, pilot service groups only (identity, storage) | local export, read 2026-07-19 | 420 rows; fields: incident_id, opened_at, service_group, severity, intake_channel, workflow |
| S2 | `activity.csv` — recorded resolution activity as of the 2026-06-22T23:59Z extract | local export, read 2026-07-19 | 409 rows (incident_id, closed_at, responder_minutes, handoffs, reopened_within_72h); 11 of the 420 incidents in S1 have no row here |
| S3 | `staffing.csv` — daily operating snapshot per service group | local export, read 2026-07-19 | 28 rows = 14 days x 2 service groups; active_responders, scheduled_responder_hours, interruption_minutes, incidents_opened |

## Data Validity

- Collection method: three frozen local CSV exports, single extract at 2026-06-22T23:59Z; no live query, no ability to re-pull a fresher snapshot.
- Coverage matrix (workflow x closed-status, the grain the censoring hypothesis and the headline comparison both use):

  | workflow | incidents (S1) | with activity row (S2) | missing activity row |
  | --- | --- | --- | --- |
  | manual | 210 | 209 | 1 |
  | assist | 210 | 200 | 10 |

  This is exactly the "per-week total looks healthy, workflow-shaped hole hides inside it" pattern the skill warns about: overall completeness is 409/420 = 97.4%, which looks fine, but split by workflow the missingness is ~10x higher in the assist arm (4.8% vs 0.5%).
- Field population: opened_at, service_group, severity, intake_channel, workflow are 100% populated in S1 for all 420 rows. closed_at, responder_minutes, handoffs, reopened_within_72h are 100% populated for the 409 rows present in S2 (no internal nulls found) — the gap is entirely missing *rows*, not missing fields within present rows.
- Coverage baseline: the extract date (2026-06-22T23:59Z) is the independent denominator. Every manual-arm incident was opened 06-01–06-07, giving 15-21 days to close by the extract; every assist-arm incident was opened 06-08–06-14, giving 8-14 days. Both windows comfortably exceed the typical closure times observed in the data (see T1/T3), so the missing rows are read as still-open incidents at extract time, not export failures — a real duration right-censored at extract, not an artifact of the export pipeline. (This reading is revisited in T3/T5.)
- Known instrument failures: none reported; no sentinel rows or export-contract note included in these files, so completeness semantics rest on the reasoning above (coverage baseline + severity skew), not on a stated contract.
- Source completeness semantics: for S2, an absent incident_id is read as "incident not yet closed as of the extract" (event not yet occurred), not "event occurred but unrecorded" or "export incomplete" — supported by (a) every missing incident's opened_at falling in the tail of its own arm's window (see T3), and (b) the missing rows skewing toward sev1, the severity independently known (via severity's own distribution) to run longest — a pattern consistent with real unresolved incidents and not with a random export drop. This reading is the basis for treating the 11 missing rows as right-censored durations (≥ extract time − opened_at) rather than excludable at random.
- Sensitivity checks performed: T3 checks whether the missing-row concentration by workflow/severity exceeds what each arm's own base rate would predict (a known-asymmetry check, not a resampled interval, since the question is about concentration of a categorical attribute, not a continuous estimator). T1 computes both the naive (available-case) contrast and a censoring-aware bound (treating missing durations as ≥ observed max, i.e. worse than any closed incident) to see whether the sign of the effect survives the worst case for the assist arm.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | Adjusted contrast (censoring bound + mix control) still shows Assist faster | Compute naive medians/means, then a worst-case bound imputing missing (still-open) durations, then severity-stratified contrasts | NOT_TESTED | |
| T2 | H2 | active_responders / scheduled_responder_hours step up exactly at the 06-08 cutover | Group staffing.csv by pre/post 06-08, by service group | NOT_TESTED | |
| T3 | H3 | Missing-activity incidents concentrate in the assist arm beyond each arm's base rate, and skew toward sev1 | Cross-tab missing-row incidents by workflow and severity vs. each arm's population rate | NOT_TESTED | |
| T4 | H4 | Severity/channel composition differs materially manual vs. assist week; reweighting closes most of the naive gap | Compare composition tables; reweight one week's severity mix onto the other's per-severity medians | NOT_TESTED | |
| T5 | H1 | An independent slice (e.g., responder-minutes, which the censoring bound does not directly touch the same way, or handoffs/reopen rate as secondary signals) corroborates or fails to corroborate the direction of T1 | Compare responder-minutes and reopened_within_72h/handoffs distributions manual vs assist, closed incidents only, stratified by severity | NOT_TESTED | |
| T6 | H5 | Among closed sev1 incidents, assist responder-minutes/handoffs exceed manual's | Filter to severity=sev1 and closed (has activity row), compare responder_minutes/handoffs assist vs manual | NOT_TESTED | |

## Amendments

(none yet)

## Conclusion

(to be completed after Tests run)
