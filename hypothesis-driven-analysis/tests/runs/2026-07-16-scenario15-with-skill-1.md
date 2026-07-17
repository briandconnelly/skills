# Investigation: Did the Assist workflow cause faster incident recovery for the two pilot service groups (identity, storage), and how many responder-hours can be credibly attributed to it for the expansion decision?

## Problem

- Decision informed: whether to recommend expanding Assist company-wide at Monday's operations review, and what responder-hours-saved figure (if any) goes into the rollout plan for Finance.
- Falsifiable question: for incidents opened June 1–14 2026 in the `identity` and `storage` service groups, did the Assist workflow reduce time-to-close and responder-minutes relative to the manual workflow, net of confounds visible in the three local exports (`incidents.csv`, `activity.csv`, `staffing.csv`)?
- Success criteria: answered means either (a) a defensible causal effect estimate survives the named rival explanations, with a stated responder-hours figure and its uncertainty, or (b) a definitive statement that this design does not identify a causal effect, with each rival explanation's tested magnitude and a best-available associational estimate clearly labeled as such.
- Stop condition: conclude when no named unresolved alternative could reverse the expansion recommendation, or the effort budget is exhausted.
- Effort budget: 25 analysis queries against the local CSVs (no external/metered collection involved). Used: 10.

## Orientation (Plan-time, pre-outcome)

Performed before looking at any relationship between workflow and the outcomes (time-to-close, responder-minutes) — unchanged from the Plan-time ledger:

- `incidents.csv`: 420 rows, unique ids, `opened_at` June 1 00:20 UTC – June 14 23:32 UTC. `service_group` balanced 105/105 per workflow. Workflow-by-date is a **clean, non-overlapping cutover**: every incident June 1–7 is `manual` (30/day), every incident June 8–14 is `assist` (30/day) — confirms the stated design (no holdout, single simultaneous switch, workflow perfectly collinear with calendar week).
- `activity.csv`: 409 of 420 incidents have closed. The 11 open ones are **10 assist / 1 manual** (open-rate 4.76% vs 0.48%), all open 8.6–17.2 days at extract, skewed toward sev1 and toward `identity`.
- `staffing.csv`: `active_responders`/`scheduled_responder_hours` step up **on the same date as the cutover, June 8** — identity 12→14 responders, storage 11→13; scheduled hours/incident up ~17–19% in both groups. `incidents_opened` flat at 15/group/day throughout (no volume confound).
- Severity mix shifted sharply: manual = 13.3% sev1 / 40.0% sev2 / 46.7% sev3; assist = 6.7% sev1 / 20.0% sev2 / 73.3% sev3. Channel and service-group mix balanced across periods.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | Assist workflow itself reduces incident time-to-close and responder-minutes | severity-stratified, censoring-adjusted TTC/responder-minutes are materially lower in assist than manual within most strata | adjustment removes most/all of the raw gap, or reverses it | the adjusted, within-stratum gap must remain materially in Assist's favor across most severity strata | T1, T3, T5 | incidents.csv, activity.csv |
| H2 | descriptive (estimand: share of the raw median/mean TTC gap attributable to the severity-mix shift, via direct standardization) | The mix shift toward sev3 mechanically lowers the raw headline TTC/responder-minutes even with no workflow effect | mix-standardizing removes most (>50%) of the raw gap | standardizing barely moves the gap | standardization must remove >50% of the raw gap, or H2 is refuted as the primary driver | T1 | incidents.csv, activity.csv |
| H3 | descriptive (estimand: bias in the raw assist-period TTC/responder-hours figures caused by differential right-censoring of still-open incidents) | Assist's disproportionately-censored still-open incidents (skewed sev1/hard) are excluded from the headline, biasing the assist median/mean low | assist censoring rate much higher than manual's, and a lower-bound sensitivity floor narrows or eliminates the raw gap | censoring rates similar, or the floor barely moves the numbers | assist censoring rate must exceed manual's materially AND the floor must move assist statistics upward non-trivially, or H3 is refuted | T2, T3 | incidents.csv, activity.csv |
| H4 | causal | The concurrent staffing increase beginning June 8 — not the workflow — drives some/all of the apparent change | capacity increase is large enough to plausibly matter, coincident with the cutover | capacity change is trivial, or timing doesn't align | capacity increase must be materially >5–10% of pre-cutover staffing, coincident with the cutover, or H4 is refuted | T4 | staffing.csv |

H1 and H4 are causal claims from a design with no concurrent control (workflow collinear with calendar week; a second exposure — staffing — changed at the identical moment). Per the skill's precedence rules, a failing within-design contrast on either can only leave the hypothesis `UNRESOLVED`, not `REFUTED`. H2 and H3 are descriptive and can be settled directly by the records.

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `.../s15-assist-rollout/incidents.csv` | 2026-07-16 (this session) | 420 rows, June 1–14 2026; no missing fields |
| S2 | `.../s15-assist-rollout/activity.csv` | 2026-07-16 (this session) | 409 rows = incidents closed as of extract (2026-06-22T23:59Z); 11 incidents.csv ids absent (still open); no nulls within present rows |
| S3 | `.../s15-assist-rollout/staffing.csv` | 2026-07-16 (this session) | 28 rows, daily × 2 service groups, June 1–14 2026, fully populated |

## Data Validity

- Collection method: frozen local CSV exports; `activity.csv` is an as-of snapshot (2026-06-22T23:59Z) and necessarily omits incidents still open at that moment.
- Coverage matrix (workflow × service_group, incidents.csv): 105/105/105/105 — fully balanced.
- Coverage matrix (workflow × closure status): manual closed 209/210 (99.5%), assist closed 200/210 (95.2%) — gap concentrated in assist.
- Field population: activity.csv fields 100% populated where a row exists; the gap is entirely absent rows, not nulls — a schema/null audit alone would have missed this.
- Coverage baseline: `incidents_opened` in staffing.csv (15/group/day) matches incidents.csv exactly, confirming incidents.csv itself is not missing rows.
- Sensitivity check performed: lower-bound imputation for the 11 open incidents (elapsed time to extract as a floor), stratified by severity — see T3.
- Standardization assumption stated explicitly: severity is treated as a pre-treatment stratifier for the T1 standardization. The data does not indicate when severity is assigned relative to workflow (intake vs. post-triage), so it is possible severity is partly downstream of the workflow itself (e.g., different triage behavior under Assist). This is noted as a limitation below; the within-stratum finding (see T1) is robust to this concern because it holds in the same direction inside every observed severity label, not just in the marginal comparison.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1, H2 | Severity-standardizing assist to manual's mix removes >50% of the raw gap if H2 drives it; gap surviving standardization is consistent with (not proof of) H1 | Direct standardization: within-severity mean/median TTC and responder-minutes (closed incidents), assist reweighted to manual's severity shares | H2: **CONSISTENT** (standardization does not merely shrink the gap, it reverses it). H1: **CONTRADICTED** (within-stratum comparison moves the opposite direction of "if true") | S1, S2. Raw mean TTC manual 428.5 min vs assist 451.9 min; assist standardized to manual's severity mix = 661.7 min (+54% vs manual raw). Raw mean RM manual 90.2 vs assist 90.9; standardized assist RM = 127.4 (+41%). Within every severity stratum, assist mean/median TTC and RM exceed manual's: sev1 1071.6→1692.2 min (RM 240.0→312.2), sev2 509.9→731.1 min (RM 99.2→137.3), sev3 172.4→304.0 min (RM 39.2→65.4). |
| T2 | H3 | Assist non-closure rate materially higher than manual's | Compare closure rate (activity.csv match) by period | **CONSISTENT** | S1, S2. manual open-rate 0.48% (1/210); assist open-rate 4.76% (10/210) — ~10x higher. |
| T3 | H1, H3 | Crediting the 11 open incidents with elapsed-to-extract as a floor narrows or eliminates the gap | Recompute T1's stratified comparison including censored incidents at their lower-bound elapsed duration | H3: **CONSISTENT** (floor moves assist numbers further up, not down — confirms censoring was flattering the raw assist figures). H1: **CONTRADICTED** (gap widens further against Assist) | S1, S2. sev1: assist floor-adjusted mean TTC 7491.8 min (5 of 14 sev1-assist incidents still open, uncapped; median with floor 1768.0 vs manual 1100.0); sev2: 1326.1 vs manual 509.9; sev3: 614.1 vs manual 423.1 (manual sev3 also has 1 open incident, minor). |
| T4 | H4 | Staffing/capacity increase >10%, coincident with June 8 cutover | Per-incident scheduled_responder_hours and active_responders before/after June 8, from staffing.csv | **CONSISTENT** | S3. Responders: identity +16.7% (12→14), storage +18.2% (11→13). Scheduled hours/incident: identity 6.41→7.59 (+18.4%), storage 5.80→6.92 (+19.4%) — both jump exactly at the cutover date. |
| T5 | H1 | Responder-minutes shows the same severity-stratified pattern as TTC | Within-severity mean responder_minutes, closed incidents, both raw and standardized | **CONTRADICTED** (same direction as T1) | S1, S2 — see T1 evidence; also confirmed robust across both service groups individually: identity and storage each show assist worse than manual in every severity stratum (e.g. identity sev3 RM 38.9→65.1, storage sev3 RM 39.6→65.7). |
| T6 | consistency check (secondary fields, not a hypothesis row) | If Assist adds coordination overhead on hard incidents, sev1 closed incidents should show worse handoffs/reopen signal in assist | Compare handoffs and reopened_within_72h for sev1 closed incidents, manual vs assist | **CONSISTENT** with the adverse pattern (though not with the specific "more handoffs" prediction) | S1, S2. sev1 assist closed incidents: mean handoffs 0.44 (vs manual 5.93 — lower, suggestive of thinner coordination before close) but reopened_within_72h = 100% (9/9) vs manual 0% (0/28). Combined with T2's censoring finding, all 14 sev1-assist incidents show either non-closure (5) or reopen-after-close (9) — i.e., 0 of 14 sev1 assist incidents represent a clean, durable resolution, vs 28/28 in manual. sev2/sev3 handoffs are higher in assist (sev2 3.01→3.95, sev3 0.54→1.52), consistent with added coordination overhead outside sev1 too. |

## Amendments

None. All four hypotheses were preregistered before any workflow-vs-outcome contrast was inspected; no retrospective hypotheses were added.

## Conclusion

- **Answer:** The Assist pilot did not make incidents resolve faster. The dashboard's "median time to close fell materially" is real as a raw, aggregate statistic (436 → 326.5 min, −25%), but it is a composition artifact: the assist week's incident mix shifted sharply toward sev3 (73% of assist incidents vs 47% of manual), and sev3 incidents are inherently much faster to close than sev1/sev2. Once compared **within the same severity label**, Assist incidents took longer and consumed more responder-minutes than manual incidents at every severity level, in both pilot groups, before any censoring adjustment — and the gap widens further once the 10 assist incidents still unresolved at the extract (vs. 1 in manual) are given credit for their elapsed time. There is no credible reading of this data in which Assist reduced responder effort.
- **Best supported:** H2 (severity-mix shift explains the entire raw headline — standardizing eliminates and reverses it, T1) and H3 (differential censoring further flatters the raw assist figures, T2/T3) both clear the bar as descriptive findings that the records settle directly. H1 (Assist causally helps) does not clear the bar and is contradicted by the within-stratum, censoring-adjusted comparison in every stratum and both groups (T1, T3, T5), corroborated by an independent field — reopen rate — showing sev1 assist closures are far less durable (T6).
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | necessary prediction failed under T1/T3/T5 in every stratum and both groups, but the design (workflow collinear with calendar week, plus a concurrent staffing increase) does not identify the causal contrast, so this cannot formally REFUTE by the skill's precedence rule — it can only leave H1 unsupported. Note the direction of the one confound we could quantify (H4, more staff) runs counter to the observed slowdown, which argues against a hidden masked benefit rather than for one. |
  | H2 | descriptive | best supported (not formally "REFUTED"/"CONSISTENT" as a binary — cleared the >50%-removed bar decisively) | T1: standardization reverses the raw improvement entirely (+54% TTC, +41% RM at matched severity mix) |
  | H3 | descriptive | best supported | T2 (10x higher censoring rate in assist) and T3 (floor adjustment moves assist numbers further adverse, not toward parity) |
  | H4 | causal | UNRESOLVED | T4 confirms a real, ~18% capacity increase exactly coincident with the cutover — a genuine co-exposure the design cannot separate from the workflow change, but its direction cannot explain the observed slowdown, so it does not rescue H1 |

- **Responder-hours for Finance:** No positive figure can be credibly booked. The only defensible same-severity comparison shows responder-minutes-per-incident *increased* under Assist by roughly +37 min (+41%) at matched severity mix (90.2 → 127.4 min/incident, standardized), and this is likely a floor — an underestimate — because the assist incidents most likely to be expensive (5 of 14 sev1 cases) are still open and their eventual responder-minutes aren't in this extract at all. Recommend Finance withdraw the hours-saved figure from the rollout plan; if anything, the pilot data supports budgeting for a responder-hours *increase* on comparable volume, though even that number should be treated as provisional given the identification limits below.
- **Limitations:**
  - This is a single-cutover, no-holdout design: workflow is perfectly collinear with calendar week, so no adjustment here can fully separate "Assist" from "whatever else changed in week 2" (staffing +18%, and any unmeasured secular trend, ramp-up/Hawthorne effect, or on-call rotation change). The within-stratum, within-group, censoring-adjusted result is the strongest evidence this data can produce, and it is consistently adverse to Assist — but formally it remains associative, not proven causal, in both directions.
  - Severity may be partly downstream of the workflow (assigned differently under Assist) rather than a clean pre-treatment stratifier; the standardization in T1 assumes it is not. The finding is robust to this concern only in the sense that every observed severity label independently got worse, not because the assumption has been verified.
  - The 11 still-open incidents (10 in assist) are a real gap: their true eventual TTC/responder-minutes are unknown; T3's floor is a lower bound, not the true value, so the true assist-vs-manual gap could be even larger than reported.
  - Small sample sizes at sev1 in assist (9 closed + 5 open = 14 total) limit precision at that stratum, though the direction is corroborated by sev2/sev3 (larger n) and by both service groups independently.
  - Reopen and handoff patterns (T6) are secondary, exploratory signals, not separately hypothesis-tested with their own necessary prediction — reported as corroborating context, not as independent proof.

---

# Decision memo — Assist workflow expansion (for Monday's operations review)

**Bottom line:** Do not expand Assist company-wide on the current evidence. The pilot's headline ("median time to close fell") is real but is an artifact of a severity-mix shift during the assist week, not a workflow effect — and once you compare like-for-like (same severity, same censoring treatment), Assist incidents took longer and consumed more responder time than manual incidents, in both pilot groups, at every severity level. Withdraw the responder-hours-saved figure from the rollout plan.

**What happened, mechanically:**
1. The assist week's incident mix shifted sharply toward sev3 (73% vs 47% in the manual week) and away from sev1/sev2. Sev3 incidents close much faster regardless of workflow, so the aggregate median fell even though nothing got faster within any severity band. Standardizing away this mix shift reverses the result: TTC would have been ~54% *higher* and responder-minutes ~41% *higher* under Assist at manual's severity mix.
2. 10 of 210 assist-period incidents (4.8%) are still unresolved at the extract date, 8.6–17 days after opening — versus 1 of 210 (0.5%) in the manual week — and they skew toward sev1/`identity`. Excluding them from the "closed" sample used for the headline removes the assist week's hardest, slowest cases and mechanically flatters its numbers. Crediting them with even their current elapsed time (a conservative floor) widens the gap further.
3. A second change happened on the exact same day as the Assist cutover: both pilot groups' staffing/scheduled hours rose ~17-19%. That confound cuts *against* Assist looking good — more capacity typically helps — yet outcomes still got worse, which argues the true effect of Assist alone is unlikely to be positive, though the design cannot cleanly isolate it.
4. The responders' complaint about "extra work on genuinely difficult incidents" is corroborated in the data: of the 14 sev1 incidents opened during the assist week, none represent a clean, durable resolution — 5 are still open, and the other 9 that did close were all (9/9) reopened within 72 hours, versus 0/28 reopens in the manual week.

**What this data can and cannot establish:**
- It can establish that the raw "median time fell" claim is not evidence of improvement — it is fully explained by composition and censoring, and the like-for-like comparison points the opposite direction, consistently across both service groups and every severity band.
- It cannot formally prove Assist *caused* worse outcomes, or rule out that some other unmeasured change in week two (beyond the staffing bump we could quantify) is responsible. There was no holdout and no randomization; the design cannot fully separate "Assist" from "everything else that changed in week two."
- It cannot produce a trustworthy responder-hours-saved (or -cost) figure with tight uncertainty bounds — sample sizes at sev1 are small and the open-incident tail is still unresolved. The directional finding (no savings, likely a cost) is nonetheless consistent across every cut of the data we could check.

**Recommendation:** Do not approve company-wide expansion based on this pilot. Before any further rollout decision: (1) pull a second data extract after the open sev1 incidents close, to see whether the pattern holds or was transient; (2) if the pilot continues, run it with a true concurrent comparison group (e.g., stagger the cutover across additional service groups, or hold one group back) so the workflow effect is not confounded with calendar week and staffing changes; (3) investigate directly why sev1 incidents under Assist are reopening at 100% and stalling open — that is the most actionable, corroborated finding in this dataset regardless of the overall causal verdict.
