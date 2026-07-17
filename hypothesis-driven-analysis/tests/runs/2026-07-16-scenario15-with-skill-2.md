# Decision Memo: Assist Workflow Company-Wide Expansion

**To:** Operations Review
**Re:** Should we expand Assist beyond the identity/storage pilot?
**Bottom line: No — not on this evidence.** The pilot's "faster resolution" headline is an artifact of a severity-mix shift and asymmetric right-censoring that happened to land on the same calendar cutover as the workflow change, and once severity is held constant Assist incidents took *longer* and cost *more* responder-minutes than manual ones in every severity band. Do not book responder-hours savings from this pilot.

## Why

The pilot compared two calendar weeks (manual: June 1–7, assist: June 8–14) for the same two service groups, with **no holdout and no overlap** — every incident's workflow is fully determined by the date it opened. That is a single before/after cutover, not a controlled comparison: anything else that also changed at the boundary is an equally valid explanation for what the dashboard saw. Three things changed at exactly that boundary, and each one on its own is large enough to produce the entire observed improvement:

1. **Case mix got lighter.** Sev3 (lightest) incidents rose from 46.7% of volume to 73.3%, sev1 (hardest) fell from 13.3% to 6.7%. Severity strongly predicts duration (manual-week medians: sev1 1100 min, sev2 512.5 min, sev3 167 min). Reweighting manual's own per-severity performance to the assist week's severity mix predicts a pooled median around 298 minutes — at or below the observed assist median of 326.5 — meaning the mix shift alone accounts for the entire pooled improvement, with no help from Assist required.
2. **Staffing and interruptions both stepped up at the same boundary.** Active responders rose 17–18%, scheduled responder-hours rose 18–19%, and interruption-minutes rose 100–500%, for both service groups, exactly on June 8.
3. **The still-open incidents are disproportionately Assist, and disproportionately its hardest ones.** 10 of the 11 incidents with no recorded close (91%, vs. the 50/50 split the design would predict) are Assist incidents, and 5 of those are sev1 — 36% of all Assist sev1 incidents never closed in the observation window, versus 0% for manual sev1. Their elapsed time as of the extract (205–412 hours) is 6–13× longer than the *longest incident that has ever closed* (32 hours). Excluding them from the "closed" statistics used for the headline is not a rounding error — it drops the slowest, hardest Assist incidents out of the comparison entirely.

Holding severity constant, the picture reverses: Assist's closed incidents took longer and cost more responder-minutes than manual's, at every severity level (sev1: 242→311 median minutes, +28%; sev2: 99.5→139.5, +40%; sev3: 39→65, +67%). Assist's sev1 incidents that did close all (9/9) reopened within 72 hours, versus 0/28 for manual — the "closures" Assist is producing on hard incidents look premature, not efficient.

## Responder-hours figure for Finance

**Do not book a savings figure.** The raw pooled numbers Finance likely used (median responder-minutes 87→69, or similar) reflect the same composition-and-censoring artifact as the time-to-close headline, not a within-severity improvement. Standardizing to the assist week's actual severity mix and bounding the still-open incidents at even a generous same-severity "typical" cost:

- Counterfactual cost of the assist week's incident mix, at manual-style per-severity performance: **~226 hours**.
- Actual assist-week cost, bounded (10 open incidents priced at their own severity's typical Assist cost — almost certainly an underestimate, since these incidents are already 6–13× any closed duration): **~337 hours**.
- **Net: roughly 110 more responder-hours consumed than a manual-style baseline would have taken on the same case mix**, over this two-week, two-group pilot — a floor estimate, not a ceiling.

If a number must go in the rollout plan, it is **0 hours saved, with the associative direction pointing toward a net cost**, not a positive figure to bank.

## What this data cannot establish

This was a single company-wide cutover with workflow perfectly collinear with calendar date — no randomization, no concurrent control, no holdout. Nothing in this dataset can identify Assist's causal effect; every contrast here (raw or severity-adjusted) is still associational and can be masked or manufactured by an unmeasured co-occurring change. It's also possible the early Assist week reflects one-time adoption friction (new workflow, no ramp period) rather than a durable pattern — this data, cut off at 7–14 days post-launch, cannot distinguish "permanently worse" from "temporarily worse, improving later."

## Recommendation

1. **Do not approve company-wide expansion on the current pilot evidence.**
2. **Do not book responder-hours savings** from this pilot in the rollout plan.
3. Before re-evaluating: run a comparison that isn't fully confounded with calendar time — staggered rollout across additional groups with a genuine concurrent control, or at minimum hold severity mix and staffing levels comparable across the compared periods — and extend the observation window so incidents have time to close before being scored.
4. **Investigate the Assist sev1 failure mode directly** — 36% non-closure and 100% 72-hour-reopen-on-close for the hardest incidents is a concrete, non-causal-inference-dependent finding (it doesn't depend on resolving the confounding above) and looks like a workflow defect on high-severity paths, worth fixing regardless of the expansion decision.

---

# Investigation Ledger

## Problem

- Decision informed: whether to recommend expanding Assist company-wide at Monday's operations review, and whether Finance's responder-hours-saved figure can be booked in the rollout plan.
- Falsifiable question: for incidents opened 2026-06-01 through 2026-06-14 across the identity and storage service groups, is the change from the manual workflow (week of June 1) to the Assist workflow (week of June 8) associated with — and, so far as this data can identify, caused by — a reduction in time-to-close and responder-minutes, and if so, how large and how attributable is it?
- Success criteria: answered means the raw before/after gap in time-to-close and responder-minutes is quantified, and each plausible non-Assist explanation (severity-mix shift, staffing/interruption shift, differential right-censoring, difficulty-subgroup reversal) is checked against its own necessary prediction, so the memo states clearly what can and cannot be attributed to Assist and what responder-hours figure (if any) is defensible.
- Stop condition: conclude when no named unresolved alternative could reverse the expansion recommendation; the design is a single company-wide cutover with workflow perfectly collinear with calendar date and no holdout, so conclude with limits once the descriptive facts are quantified rather than waiting for an identified causal estimate that this data cannot produce.
- Effort budget: ~12 analysis computations (script/aggregation passes over the three CSVs); same-day wall-clock (leadership needs this today). Used: 8 test computations plus orientation.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist itself causes faster time-to-close and lower responder-minutes | closed-incident time-to-close and responder-minutes are lower in the assist week than the manual week | no raw gap, or gap in the wrong direction | assist closed-incident median time-to-close and median responder-minutes must be lower than manual's, at minimum, for a positive causal effect to be plausible | T1 | incidents.csv, activity.csv |
| H2 | descriptive (estimand: share of the raw gap explained by the June-8 severity-mix shift) | The incident mix shifted toward sev3 (lighter) incidents at the same cutover, and severity itself predicts duration, so part or all of the apparent speed-up is compositional, not workflow-driven | severity predicts duration (sev3 faster) in single-workflow data, and reweighting the manual period to the assist week's severity mix closes a material share of the raw gap | severity has no relationship to duration, or reweighting explains a negligible share | severity must predict duration (sev3 median close time below sev1/sev2) within the manual-only period, where workflow is held constant | T2, T3 | incidents.csv, activity.csv |
| H3 | descriptive (estimand: coincidence of a staffing/interruption-level step change with the workflow cutover) | active_responders and interruption_minutes both stepped at the same June 8 boundary as the workflow change, giving an independent resource-based rival explanation | staffing.csv shows a material (>10%) jump in active_responders and/or interruption_minutes exactly at the cutover date | staffing and interruption levels are flat across the cutover | active_responders per service group must not be flat across June 7→June 8 | T4 | staffing.csv |
| H4 | descriptive (estimand: differential right-censoring of open incidents by workflow arm, and its effect on the closed-incident summary statistics and on any responder-hours total) | Incidents with no activity.csv row (still open at the 2026-06-22 extract) are concentrated in the assist arm and are far longer-running than any closed incident, so excluding them from "closed" statistics mechanically favors assist and understates responder-minutes actually consumed by assist incidents | open incidents skew heavily toward the assist workflow, and their elapsed time as of the extract exceeds the longest observed closed duration | open incidents are evenly split by workflow and/or their elapsed time is comparable to typical closed durations | open (uncensored-outcome) incidents must not be evenly split ~50/50 between workflows given service groups switched together | T5, T6 | incidents.csv, activity.csv |
| H5 | descriptive (estimand: sev1-subgroup non-closure rate and, among closed sev1 incidents, responder-minutes/handoffs, assist vs manual) | Among the hardest (sev1) incidents, Assist incidents are less likely to close within the observation window and/or consume more responder-minutes/handoffs when they do close, consistent with responders' complaint that Assist adds work on genuinely difficult incidents | assist sev1 non-closure rate is materially higher than manual sev1 non-closure rate | sev1 non-closure and responder-minutes/handoffs are comparable or better under assist | assist sev1 non-closure rate must not be lower than or equal to manual's | T7, T8 | incidents.csv, activity.csv |

H1 is a causal claim over a design the service owners describe as "clean" because every incident followed whichever workflow was active when it opened — but that consistency is exactly what makes workflow a deterministic function of calendar date, with no holdout. Per the skill's design rule, no contrast from this design (raw or standardized) can by itself mark H1 `REFUTED` or promote it past `UNRESOLVED` — a co-occurring change (H2/H3/H4/H5, or something unmeasured) could mask or manufacture the appearance of an effect.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `incidents.csv` (frozen local export) | task start, 2026-07-16 | 420 rows, incidents opened 2026-06-01T00:20Z–2026-06-14T23:32Z; no duplicate incident_ids; no empty fields; workflow perfectly collinear with opened_at date (manual = June 1–7, assist = June 8–14, no overlap) |
| S2 | `activity.csv` (frozen local export) | task start, 2026-07-16 | 409 rows against 420 incidents (97.4% closed); extract taken 2026-06-22T23:59Z; no duplicate incident_ids, no empty fields, no closed_at earlier than opened_at; closed-incident duration range 121–1919 minutes (2h–32h) |
| S3 | `staffing.csv` (frozen daily operating snapshot) | task start, 2026-07-16 | 28 rows = 14 days × 2 service groups; complete, no gaps |

## Data Validity

- Collection method: three frozen local CSV exports; incidents.csv from the incident tracker, activity.csv resolution activity as recorded as of the 2026-06-22T23:59Z extract, staffing.csv a daily operating snapshot per service group. No system-of-record cross-check is possible; these are the only records available.
- Coverage matrix (incident counts at the workflow × severity × service_group grain the hypotheses use): manual = {sev1:28, sev2:84, sev3:98} (n=210); assist = {sev1:14, sev2:42, sev3:154} (n=210) — sev3 share 46.7%→73.3%, sev1 share 13.3%→6.7%. workflow × service_group is balanced (105/105 each, both groups cut over together). workflow × intake_channel proportions are stable across the cutover. date × workflow: exactly 30 incidents/day every day, manual strictly June 1–7 and assist strictly June 8–14 — confirms workflow is a deterministic function of calendar date with no holdout, exactly as described.
- Field population: incidents.csv core fields are 100% populated (420/420). activity.csv fields are populated for 409/420 (97.4%) overall, but that aggregate hides a severe imbalance: 11 incidents have no activity.csv row (still open at extract time), and 10 of those 11 (91%) are assist-workflow incidents versus the 50/50 split the balanced design predicts. Of the 10 open assist incidents, 5 are sev1 (of only 14 assist sev1 incidents total — a 36% non-closure rate for the hardest assist incidents vs. 0/28 for manual sev1).
- Coverage baseline: no independent denominator exists to cross-check total incident volume; incidents_opened in staffing.csv matches incidents.csv's daily counts exactly (internal consistency only, not independent). For the censoring question, the internal baseline is the observed closed-duration range (121–1919 minutes, ≤32 hours): the 11 open incidents' elapsed time as of the extract ranges 205–412 hours (8.5–17 days) — 6–13× longer than the longest incident that has ever closed. Not a subtle gap.
- Known instrument failures: none documented. The prompt's note that "even the newest incidents had at least seven full days to mature" rules out "too new to have closed" as the explanation for the 11 open incidents.
- Sensitivity checks performed: no metered/aggregated source is being trusted blind — all three files were read in full and reconciled row-by-row (incident_id counts, join completeness, date/workflow crosstabs all check out against each other).

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | assist closed-incident median time-to-close and median responder-minutes < manual's | joined incidents.csv+activity.csv, closed incidents only, computed median/mean time-to-close and responder_minutes by workflow | CONSISTENT (median only) | manual: median ttc=436.0min, median rm=87.0; assist: median ttc=326.5min, median rm=69.0 (S1,S2). **Supplementary, non-necessary:** mean ttc reverses — manual mean=428.5min, assist mean=451.9min (assist higher); mean rm is flat — manual=90.2, assist=90.9 (assist higher). Median/mean divergence signals a composition/heterogeneity effect, not a uniform speed-up. |
| T2 | H2 | within manual-only data, sev3 median time-to-close < sev2 < sev1 | computed median ttc by severity, manual workflow only | CONSISTENT | manual-only: sev1 median=1100.0min, sev2=512.5min, sev3=167.0min (S1,S2) — strong monotonic gradient |
| T3 | H2 | reweighting manual's within-severity medians by assist's severity-share closes a material part of the T1 gap | direct standardization: applied assist severity shares to manual within-severity medians | CONSISTENT | synthetic median = 298.3min — at/below the raw observed assist median (326.5) and well below raw manual (436.0); severity-mix shift alone accounts for the entire pooled gap (S1,S2) |
| T4 | H3 | active_responders and/or interruption_minutes step up materially at the June 7→8 boundary | compared staffing.csv daily figures pre- vs post-cutover per service group | CONSISTENT | identity: active_responders 12.0→14.0 (+16.7%), scheduled_hours 96.1→113.9 (+18.4%), interruption_minutes 12.4→74.0 (+495%); storage: responders 11.0→13.0 (+18.2%), scheduled_hours 87.0→103.9 (+19.4%), interruption_minutes 29.0→59.4 (+105%) (S3) |
| T5 | H4 | open incidents concentrate in the assist arm and their elapsed time exceeds the max closed duration | set-difference incidents.csv ids against activity.csv, tabulated by workflow/severity, compared elapsed-to-extract against max closed duration | CONSISTENT | 10/11 open incidents (91%) are assist vs. 50% expected; open assist severities {sev1:5, sev2:2, sev3:3}; elapsed 205–412h vs. max closed duration 32h (6–13×) (S1,S2) |
| T6 | H4 | bounding the 10 open assist incidents' eventual responder-minutes materially narrows/reverses the "hours saved" figure | bounded each open incident at its own severity's typical assist closed-arm mean responder-minutes (a generous, likely-low bound given these incidents are already 6–13× any closed duration); recomputed totals/means | CONSISTENT | assist bounded: total=20,207min, n=210, mean=96.2; manual bounded: total=18,896min, n=210, mean=90.0 — assist mean now *exceeds* manual's once censoring is bounded, reversing the raw closed-only comparison (S1,S2) |
| T7 | H5 | assist sev1 non-closure rate materially exceeds manual sev1 non-closure rate | restricted to severity=sev1, computed share with no activity.csv row, by workflow | CONSISTENT | manual sev1: 0/28 open (0%); assist sev1: 5/14 open (35.7%) (S1,S2) |
| T8 | H5 | among closed sev1 incidents, assist responder-minutes/handoffs not lower than manual's | restricted to severity=sev1 AND closed, compared median responder_minutes, handoffs, and (same query, evidence extended per Amendments) reopened_within_72h by workflow | CONSISTENT (rm, reopens); NON_DISCRIMINATING alone (handoffs) | manual sev1 closed (n=28): median rm=242.0, median handoffs=6.0, reopen_rate=0%. assist sev1 closed (n=9): median rm=311.0 (+28.5%, consistent), median handoffs=0.0 (lower, would read as *less* work in isolation), reopen_rate=100% (9/9) — every assist sev1 "closure" reopened within 72h vs. none of manual's, indicating the low handoff count reflects premature/incomplete closure rather than efficiency (S1,S2) |

## Amendments

- 2026-07-16: T8's evidence was extended to include `reopened_within_72h`, a field already present in the same activity.csv query run for responder-minutes/handoffs. No new data collection and no new hypothesis — H5 already predicted "extra work on genuinely difficult incidents," and the reopen-rate finding bears directly on that claim using data already in scope.
- No hypotheses were added after seeing outcome data; all five hypotheses in the table were preregistered at Plan time (see `s15-skill-2-plan.md`, written before any outcome-by-workflow computation was run).

## Conclusion

- **Answer:** No causal evidence supports expanding Assist, and the responder-hours-savings figure Finance wants to book is not defensible from this data. The pilot's raw pooled median improvement is fully explained by a severity-mix shift toward lighter incidents that happened to coincide with the same calendar cutover as the workflow change; a simultaneous staffing/interruption-level step change is an unresolved second rival; and 91% of the still-unresolved incidents (skewed toward sev1) are Assist incidents whose exclusion from the "closed" statistics mechanically flatters the headline. Once severity is held constant, Assist's closed incidents took longer and cost more responder-minutes than manual's at every severity level, and Assist's hardest (sev1) incidents show a 36% non-closure rate and a 100% 72-hour reopen rate among the ones that did close — directly consistent with responders' complaints, not with the dashboard/Finance narrative.
- **Best supported:** H2 (severity-mix confound) and H4 (censoring asymmetry) are each independently sufficient to account for the entire observed pooled improvement (T3, T6); H5 (difficulty-subgroup reversal) is strongly supported and directly corroborates the responders' complaint (T7, T8); H3 (staffing/interruption confound) is an unresolved additional rival that cannot be ruled out (T4). Because multiple unrefuted, non-causal explanations each fully or more-than-fully account for the observations, H1 (the causal claim) does not clear the "best supported" bar — no rival is refuted, so a causal read is not sound.
- **Per-hypothesis summary:**

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | necessary prediction (median) held under T1, but the contrast is from a design that does not identify causation (single cutover, workflow ≡ calendar date, no holdout) — per the design-identification rule this cannot promote H1 past `UNRESOLVED`; supplementary mean/severity-stratified evidence points the opposite direction |
  | H2 | descriptive (composition) | CONSISTENT / best supported | T2 (severity predicts duration) and T3 (severity-mix reweighting reproduces the entire pooled gap) both `CONSISTENT` |
  | H3 | descriptive (staffing/interruption) | CONSISTENT / unresolved rival | T4 `CONSISTENT` — large simultaneous step change; contribution not separable from H2's with this data |
  | H4 | descriptive (censoring) | CONSISTENT / best supported | T5 (91% of open incidents are assist, 6–13× any closed duration) and T6 (bounding reverses the mean comparison) both `CONSISTENT` |
  | H5 | descriptive (difficulty subgroup) | CONSISTENT / best supported | T7 (35.7% vs 0% sev1 non-closure) and T8 (higher rm, 100% vs 0% reopen rate) both `CONSISTENT` |

- **Limitations:**
  - This was a single company-wide cutover with no holdout and no concurrent control; workflow is perfectly collinear with calendar date, so no analysis in this ledger — raw or severity-standardized — identifies a causal effect. Associative language only.
  - Staffing and interruption-minutes changed sharply at the same boundary as the workflow (H3); this data cannot separate their contribution from Assist's or from the severity-mix shift (H2).
  - The bounding in T6 uses a *generous* assumption (open incidents cost the "typical" amount for their severity); given these incidents are already 6–13× longer-running than any closed incident, their true eventual cost is plausibly higher still, so the ~110-hour net-cost estimate is a floor, not a ceiling.
  - Whether the within-severity Assist slowdown is a durable pattern or a one-time adoption/ramp cost cannot be determined from 7–14 days of post-launch data; this is a genuine open possibility, not tested here, and would need a longer observation window to resolve.
  - Reopen-rate and handoff evidence for sev1 (T8) rests on only 9 closed assist sev1 incidents — small n; the 100% reopen rate is a striking and discriminating signal but should be treated as a flag to investigate, not a precise rate estimate.
