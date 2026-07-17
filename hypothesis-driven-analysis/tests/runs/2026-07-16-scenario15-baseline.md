# Decision Memo: Assist Workflow Company-Wide Expansion

**Prepared for:** Monday operations review
**Question:** Did Assist cause faster incident recovery, how many responder-hours can we credibly attribute to it, and should we expand?

**Bottom line up front:** The naive "median time to close fell" headline is real in the raw numbers but is not evidence that Assist made incidents faster.
It is explained by at least three confounds that all point the same direction: a severity-mix shift in the incident stream, a simultaneous ~19% staffing increase, and right-censoring of the hardest assist-week incidents.
When severity is held constant, Assist incidents took **longer** and consumed **more** responder-minutes in every severity tier, in both service groups.
**Do not book responder-hour savings, and do not expand yet.**

---

## 1. What the data covers

- `incidents.csv`: 420 incidents opened June 1–14, 210 under `manual` (Jun 1–7), 210 under `assist` (Jun 8–14, cutover at 00:00 UTC June 8).
- `activity.csv`: 409 closure records (closed_at, responder_minutes, handoffs, reopened_within_72h). **11 incidents have no activity record** — they are still open at the June 22 23:59 UTC extract.
- `staffing.csv`: daily headcount/scheduled-hours/interruption-minutes per service group, June 1–14.
- Two service groups: `identity`, `storage`. Three severities: `sev1` (worst), `sev2`, `sev3`.

## 2. The naive comparison (what the dashboard/Finance are using)

| | manual (closed only) | assist (closed only) |
|---|---|---|
| n closed | 209 | 200 |
| median TTC (min) | 436.0 | 326.5 |
| mean TTC (min) | 428.5 | 451.9 |

Median time-to-close falls ~25%. This is the number driving the rollout plan. But note the mean *rises* — median and mean disagree on direction, which is already a flag that the underlying mix of incidents changed between the two windows, not that each incident got faster.

## 3. Confound #1: the incident mix is not comparable before/after

Severity counts by day are **deterministic step functions**, not organic variation:

| Period | sev1/day | sev2/day | sev3/day | total/day |
|---|---|---|---|---|
| Jun 1–7 (manual) | 4 | 12 | 14 | 30 |
| Jun 8–14 (assist) | 2 | 6 | 22 | 30 |

Every single day in each window has *exactly* these counts, split identically across both service groups. This is not incident volume drifting — it is a hard-coded change in the severity composition that lands exactly on the cutover boundary. Whatever caused it (real change in what's happening, or a change in how incidents get triaged/labeled once Assist is live), it means the manual week and assist week are not the same population of incidents. The assist week has proportionally far more cheap, fast sev3 tickets (73% of the week vs. 47% before) and far fewer expensive sev1/sev2 tickets. Since severity is by far the strongest driver of time-to-close (below), this alone can generate the entire "median fell" headline with zero change in how any individual incident is handled — a textbook Simpson's paradox.

## 4. Confound #2: staffing changed at the same moment

`staffing.csv` shows headcount and scheduled hours jumped on **June 8, the same day as the Assist cutover**:

| Group | active responders (manual→assist) | scheduled hrs/day (manual→assist) |
|---|---|---|
| identity | 12 → 14 | 96.1 → 113.9 (+18.4%) |
| storage | 11 → 13 | 87.0 → 103.9 (+19.4%) |

Interruption-minutes also rose sharply (identity 12.4→74.0/day, storage 29.0→59.4/day). Two operational changes (Assist + ~19% more staff, more interruptions) landed in the same week. There is no way to separate "Assist changed the work" from "we added a fifth of the team and changed on-call load" using this data. Any causal claim about Assist alone is unsupported by design, not just by noise — there was no holdout, and here we can see a second real intervention that moved with it.

## 5. Confound #3: right-censoring hits the hardest assist incidents hardest

11 incidents are still open at extract time (7+ days after opening even for the latest). They are **not evenly distributed**:

| Severity | manual still-open | assist still-open |
|---|---|---|
| sev1 | 0/28 (0%) | 5/14 (**35.7%**) |
| sev2 | 0/84 (0%) | 2/42 (4.8%) |
| sev3 | 1/98 (1.0%) | 3/154 (1.9%) |

More than a third of assist-week sev1 incidents are still unresolved a week-plus later. The "median fell" calculation excludes these entirely — it only measures the assist incidents that happened to close fast enough to be captured, which systematically excludes the slowest, worst cases in the highest-severity tier. This biases the assist-week numbers to look better than the true (unknown) population, on top of the mix-shift bias in §3.

## 6. The like-for-like comparison: severity-stratified

Holding severity constant, in **both** service groups, Assist incidents took longer and cost more responder-minutes — the opposite of the headline:

**Time to close (median minutes), closed incidents only:**

| Severity | manual | assist | assist vs manual |
|---|---|---|---|
| sev1 | 1100 (n=28/28) | 1659 (n=9/14, 5 still open) | **+51%, and undercounted** |
| sev2 | 512.5 (n=84/84) | 740 (n=40/42) | **+44%** |
| sev3 | 167 (n=97/98) | 302 (n=151/154) | **+81%** |

**Responder-minutes per incident (mean), closed incidents only:**

| Severity | manual | assist | assist vs manual |
|---|---|---|---|
| sev1 | 240.0 | 312.2 | **+30%** |
| sev2 | 99.2 | 137.3 | **+38%** |
| sev3 | 39.2 | 65.4 | **+67%** |

This holds identically split by service group (identity and storage individually show the same direction and similar magnitude at every severity — see raw computation), so it is not one team's problem.

## 7. Quality signals corroborate the responder complaints, concentrated in the hard cases

- **sev1 reopen rate:** manual 0/28 (0%) vs. assist 9 closed, of which **100% reopened within 72h**. Combined with 35.7% of sev1 assist incidents still open, this suggests sev1 incidents under Assist are being closed prematurely and bouncing back — literally the "extra work on the genuinely difficult incidents" responders are describing.
- **sev1 handoffs dropped** (manual 5.93 → assist 0.44 mean handoffs), consistent with less escalation/collaboration on hard incidents under the new workflow — plausibly the same mechanism producing the reopens.
- **sev2 handoffs rose** (3.01 → 3.95) — more coordination overhead, not less.
- Pooled across severities, reopen rate looks small (0% → 4.5%) but that pooled number is itself mix-shift-contaminated (§3) and severity-blind; the sev1 stratum is where the real signal is.

## 8. Responder-hours: what can and cannot be booked

**Unconditional (severity-blind) responder-minutes, closed incidents only:**

| | manual | assist |
|---|---|---|
| mean resp min/incident | 90.2 | 90.9 |
| n closed | 209 | 200 |

These are essentially flat — the raw effort-per-incident number Finance would need for a clean "hours saved" claim shows **no savings at all**, even before adjusting for severity mix or censoring. (Finance's "hours saved" figure appears to derive from the wall-clock time-to-close headline, not from responder-minutes — but time-to-close is not responder effort; an incident can sit open for less wall-clock time while consuming the same or more responder-minutes, which is exactly what happened here.)

**Severity-adjusted counterfactual:** apply manual per-severity mean responder-minutes to the actual assist-week incident mix, and compare to what assist-week incidents (closed only) actually consumed:

- Expected minutes at manual per-severity rates, assist week's mix: **13,567 min**
- Actual minutes consumed, assist week (closed incidents only, undercount — 10 assist incidents excluded because still open): **18,175 min**
- Difference: assist week consumed **~77 hours *more*** responder time than the manual workflow would have on the same incident mix — and this is a lower bound, since the 10 uncounted open incidents skew toward sev1/sev2 (the expensive tiers).

**Conclusion for Finance: there is no credible responder-hours-saved figure to book.** The defensible point estimate, to the extent the two-week window supports one at all, is a **net cost**, not a savings, on the order of tens of hours across the two pilot groups over two weeks — and even that estimate is confounded by the simultaneous 19% staffing increase (§4) and cannot be cleanly attributed to Assist versus the added headcount or the change in interruption load. I would not put a signed number in the rollout plan in either direction; I would report "not measurable as a savings with this design," with the negative-direction estimate above as supporting context for why the burden of proof is on expansion, not against it.

## 9. What this data can and cannot establish

**Can establish:**
- The two comparison windows differ in incident-severity composition by a large, suspiciously exact margin that lines up with the cutover.
- Staffing levels changed by ~19% at the same moment as the workflow cutover.
- Within matched severity strata, Assist incidents show longer time-to-close and higher responder-minutes in both service groups, with no exception.
- Sev1 (worst) incidents under Assist have a much higher unresolved rate at 7+ days (35.7% vs 0%) and, among those that did close, a 100% 72-hour reopen rate vs. 0% under manual.
- The wall-clock "median time to close fell" headline is real but is adequately explained by the severity-mix shift and right-censoring alone, without invoking any effect of Assist.

**Cannot establish:**
- Whether Assist itself, independent of the concurrent staffing change, made incidents better or worse — the two interventions are perfectly confounded in time.
- Why the severity mix shifted exactly at the cutover — whether it reflects a real change in what incidents occurred, a change in triage/labeling behavior introduced alongside Assist, or an artifact of this extract. This should be resolved before any further analysis is trusted.
- The true time-to-close or responder-minutes distribution for assist-week sev1/sev2 incidents, since a material share are still open and excluded from every average above.
- Any causal effect at all, in the strict sense — there was no holdout group and no randomization; "every pilot incident followed the workflow active when it opened" is a description of a clean natural pre/post split in treatment assignment, not a clean comparison, because the population and staffing changed at the same instant as the treatment.

## 10. Recommendation

**Do not expand Assist company-wide on the current evidence.** The stratified, like-for-like comparison — the only comparison that controls for the population shift — shows Assist incidents taking longer and costing more responder-minutes at every severity level, with a specific and serious failure mode concentrated in sev1 (high unresolved rate, 100% reopen rate among closed cases). This is consistent with, not contradicted by, the responders flagging extra work on genuinely difficult incidents.

Before any expansion decision:
1. Explain the exact-match severity-mix shift (§3) — this is either a data/process issue that must be fixed before trusting any comparison, or a real change that itself needs explaining.
2. Re-run this comparison once the 10 still-open assist incidents close, especially the 5 open sev1s — current sev1 numbers are a lower bound on badness.
3. Separate the staffing increase from the Assist effect — either hold headcount fixed in a new test window, or model staffing as a covariate with enough variation to identify it separately from workflow.
4. If expansion is to proceed regardless, do it as a proper staged rollout with a concurrent holdout group and stable staffing, not another single-cutover comparison — and specifically instrument sev1 handling (handoffs, reopens, time-to-resolution excluding first-close) given the failure signal here.
5. Do not book responder-hours savings in the rollout plan; the current best-supported direction is a net cost, not a saving.
