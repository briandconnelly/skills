# Investigation ledger — Assist rollout review

## Problem

**Decision informed:** whether to expand Assist company-wide, and whether Finance may book responder-hours saved.

**Falsifiable question:** did enabling Assist on 2026-06-08 cause a reduction in time-to-close and responder minutes for pilot incidents, and is an attributable responder-hour saving estimable from these exports?

**Answered means:** either (a) a causal effect estimate with an uncertainty statement and the identifying design named, or (b) a determination that these data do not identify the effect, naming the specific threats and reporting what the data *do* establish.

**Population / timeframe / units:** incidents opened 2026-06-01..2026-06-14 in the `identity` and `storage` service groups. Time-to-close = closed_at − opened_at, hours. Responder effort = responder_minutes, minutes.

**Stop condition:** conclude once the within-stratum, censoring-aware contrast is computed and each named rival is resolved or declared unresolvable. **Budget:** ≤ 8 analysis passes over the local exports. No new collection is authorized or needed.

## Gates

**Authorization:** the user directed analysis of three frozen local exports and said to work from these only. Reads of those files fall inside that grant. No production system, no mutation, no external source is touched. Collection is not costly (local files, ~850 rows) → no collection plan required.

**Consultation:** interactive, but the problem statement required no judgment call the user must arbitrate; assumptions are recorded inline. Proceeding.

## Orientation findings (pre-preregistration; no cause↔outcome relationship inspected)

- O1. Volume is exactly 30 incidents/day, 15 per group, all 14 days. No volume shift at cutover.
- O2. Severity mix shifts sharply at the cutover and is constant within each week: manual sev1/sev2/sev3 = 13.3/40.0/46.7%, assist = 6.7/20.0/73.3%. Exposure-vs-covariate, not exposure-vs-outcome.
- O3. 11 of 420 incidents have no activity row. 10 of 11 are assist-week; they skew sev1. Coverage hole at the day×group×severity grain.
- O4. staffing.csv shows active_responders 12→14 (identity) and 11→13 (storage) effective 2026-06-08 — the same date as the cutover. A co-exposure, discovered during orientation.

**Data-validity check:** coverage matrix built at day × group × severity (the grain the analysis uses). Denominator = incidents.csv, which the user states is every incident opened in the window; the activity file is checked against it rather than against itself. The extract is stated to be 8+ days after the last open, so "not yet closed" cannot be explained by a short maturation window for sev3, but must be assessed per stratum.

## Hypotheses and preregistered predictions

| # | Hypothesis | Necessary prediction (failure ⇒ REFUTED) | Discriminating test | Status |
|---|---|---|---|---|
| H1 | Assist causally reduces time-to-close | Within a severity stratum, assist incidents close faster than manual ones | T3 | |
| H2 | The headline is case-mix composition, not treatment | Standardizing the assist week to the manual week's severity mix removes most of the marginal gain | T3 | |
| H3 | Censoring/survivorship: unclosed incidents are excluded from the median, biasing it down | The missing activity rows concentrate in the assist week and in high-severity strata | T1 | |
| H4 | Concurrent staffing increase, not Assist, drives any improvement | Responder capacity per incident rises at the cutover date | T5 | |
| H5 | Assist adds effort on hard incidents (responders' claim) | Within sev1/sev2, responder_minutes is higher under assist than manual | T4 | |

H1–H3, H5 are prospective. **H4 is `retrospective`** — O4 informed it — so it may only be promoted on evidence that did not shape it, and per the skill it cannot be promoted on the staffing figures themselves.

**Note on H2 vs H4:** these are not exclusive; multiple contributing explanations are allowed.

## Test plan (cheapest-adequate-first, all inline)

No subagent fan-out: one local source, ~850 rows, no metered or slow collection, no parallel request → the skill's fan-out conditions do not hold.

- T1 — completion rate by week × severity (free, no join to outcomes). Discriminates H3.
- T2 — reproduce the dashboard's marginal median TTC claim. Establishes the claim under audit.
- T3 — within-severity median TTC by week + direct standardization to the manual mix. Discriminates H1 from H2.
- T4 — responder_minutes within severity by week. Discriminates H5; audits Finance's savings arithmetic.
- T5 — staffing and interruption_minutes at the cutover. Addresses H4.
- T6 — secondary outcomes (reopen rate, handoffs) for consistency.

## Sensitivity note

A null within-stratum difference counts as evidence only if the same method can surface a real difference of comparable size. T3 reports stratum-level effect sizes and spreads so a null is interpretable against the observed manual-week between-severity gaps.

## Outcomes

| Test | Result | Outcome |
|---|---|---|
| T1 | Closure rate manual sev1 96.4% / sev2 100% / sev3 100%; assist sev1 **64.3%** / sev2 95.2% / sev3 98.1%. 10 of 11 still-open are assist-week; 5 of 14 assist sev1 never closed, open 8–14 days at extract. | `CONSISTENT` with H3 |
| T2 | Marginal median TTC over closed incidents: 4.25 h → 2.23 h = **−47.5%**. The dashboard claim reproduces exactly. | claim confirmed as stated |
| T3 | Within severity, assist is **slower in every stratum**: sev1 13.15→14.92 h (+13.4%), sev2 4.88→5.58 (+14.3%), sev3 1.68→2.02 (+20.4%). Standardized to the manual mix: 4.49 → 5.16 h = **+15.0%**. | H1 `CONTRADICTED` on its necessary prediction; H2 `CONSISTENT` |
| T4 | Responder minutes within severity, all higher under assist: sev1 +24 min, sev2 +12, sev3 +8.5. Naive weekly totals 308.8 h → 226.0 h; standardized to manual mix 312.8 h → **352.1 h**. | H5 `CONSISTENT` |
| T5 | active_responders 12→14 / 11→13 at the cutover; scheduled hours per incident 6.25 → 7.07 (+13%). Incident volume identical (210 vs 210). | H4 `NON_DISCRIMINATING` (see below) |
| T6 | Reopen-within-72h: 9.1% → 18.5% marginal. Within sev1: manual 3.7% (1/27) vs assist **100% (9/9)**. | undermines outcome comparability |

### Verification (spot-verify per Analysis)

All analysis was inline — no worker returns to audit — so the free check was applied to my own numbers, plus a re-run (cheap: local files).

- V1: headline recomputed by an independent hand-join straight from the raw files → 4.25 / 2.23 reproduced.
- V2: instrument sanity — 0 negative TTC, 0 closures after the stated extract time.
- V3: bootstrap (4000 resamples, seed 0) on the within-stratum median difference: sev1 [+1.28, +2.03], sev2 [+0.42, +0.87], sev3 [+0.19, +0.54]. All three exclude 0, all in the direction of assist being **slower**.
- V4: standardization re-run under three estimators — mean-of-stratum-medians +15.0%, standardized means +14.7%, mix-reweighted pooled median +13.3%. The sign is not an artifact of the estimator.
- V5: censoring-aware median (censoring is entirely upper-tail, so KM-equivalent): assist sev1 14.92 → 15.15 h. Dropping unclosed incidents flatters Assist; the within-stratum penalty is a **lower bound**.
- V6: the 100% sev1 reopen figure traced to the 9 underlying ids — all 9 have `reopened_within_72h=1`. Quote appears in the rows it came from.
- V7: Finance's arithmetic reproduced (82.8 h/week naive saving) and re-run under fixed case mix → −39.3 h, i.e. a cost.
- **Shared-assumption check:** every test rides on one join (incidents ⋈ activity on incident_id) and one TTC definition. Both were validated independently in V1/V2, so a shared bad join would have surfaced there.

### Sensitivity (per Data: a null counts only if the method can see a positive)

Not applicable in the usual direction — the within-stratum results are non-null and signed. The method's discriminating power is nonetheless demonstrated: the same estimator resolves the between-severity gaps (1.68 / 4.88 / 13.15 h) cleanly, and the manual-week IQRs are tight (sev3 1.4–2.0), so an improvement of the size Finance claims would have been trivially visible had it existed.

## Hypothesis statuses (derived from the latest effective outcome; never edited directly)

**Amendment 2026-07-16 (post-review).** The statuses below supersede my first pass, which Codex's review showed was self-contradicting: I called the causal effect unidentified and simultaneously marked the causal H1 `REFUTED`. A design that cannot identify a benefit cannot refute one either — a real Assist benefit could be masked by any co-occurring week effect. The fix is to split the causal claim from the descriptive one; only the latter was ever testable here.

| # | Hypothesis | Status | Basis |
|---|---|---|---|
| H1-causal | Assist causally reduces TTC | **UNRESOLVED** | Its necessary prediction follows from the mechanism only under a no-confounding assumption this design does not supply, so no test here is *adequate* to refute it. Superseded status; was `REFUTED`. |
| H1-desc | The recorded data show an improvement in time-to-close | **REFUTED** | This claim is settled by the records themselves and needs no design. It failed in all three severity bands, both service groups and all three intake channels — 10 of 10 cells, all in the wrong direction. This, not the causal claim, is what kills the dashboard's reading. |
| H2 | Headline is an aggregation artifact of recorded case mix | **UNRESOLVED**, best supported *as a descriptive claim* | Standardization mechanically reproduces the reversal under four estimands (+12.5% to +15.0%); `CONSISTENT` on T3, which discriminates it from H1-desc. Prospective: the mix↔workflow shift shaped it, but the TTC outcomes that tested it did not. The "…and not treatment" clause is struck — standardization cannot establish that. |
| H3 | Censoring/survivorship | **UNRESOLVED**, exploratory | Codex is right: O3 stated H3's necessary prediction *before* H3 was registered, so T1 re-ran the evidence that shaped it. Under the skill's retrospective rule this is exploratory and reported as an open contributing possibility, not promoted. |
| H4 | Concurrent staffing increase | **UNRESOLVED** | Retrospective (informed by O4), and cannot be promoted on the staffing figures that suggested it. Framed to explain an improvement that does not exist within strata. Its residual role is directional context only, not a resolved rival. |
| H5 | Assist adds effort on hard incidents | **UNRESOLVED** | Effort is higher in the Assist week in every band (T4), which is consistent with the responders' report and inconsistent with Finance's. But T4 cannot discriminate Assist from any concurrent temporal cause, so "best supported" is withdrawn. |

No hypothesis is promoted to a causal answer. H2 is the only one that clears a "best supported" bar, and only for the descriptive claim that composition mechanically produces the reversal.

## Review findings accepted (Codex, 2026-07-16)

Verified independently before accepting — all of Codex's recomputations reproduced exactly (`check_codex.py`):

1. **H1 `REFUTED` was incoherent** with the unidentified conclusion. Accepted; split above.
2. **H3's preregistration was circular** — O3 already asserted its necessary prediction. Accepted; demoted to exploratory.
3. **The memo asserted causation while claiming not to** ("Assist *costs* 39 h", "lower bound on the harm", "the responders are right") and then declared "all language here is associative by design". That sentence was false as written. Accepted; memo language corrected throughout.
4. **Estimand mismatch** — the weighted-average-of-stratum-medians is not the raw median's estimand. Accepted; exact weighted-ECDF median added (4.28→4.82, +12.45%), all estimands now named.
5. **"Still open" overclaimed** — the export shows absence of a *recorded closure*, not confirmed non-closure; and my ∞-imputed median is a tail-order bound, not Kaplan–Meier. Accepted; both corrected.
6. **Missed a second aggregation reversal in `handoffs`** (marginal 1.789→1.765 improves; sev2 +0.357 and sev3 +0.374 worsen). I printed these numbers in T6 and failed to read them. Accepted; added.
7. **Robustness cuts never run.** Now run: the contrast holds in both service groups and all three intake channels (10/10 cells).
8. **Bootstrap CIs assume IID over what is a census with week-level assignment.** Accepted; they are descriptive resampling sensitivity showing sign stability, not inferential intervals, and are relabelled as such.
9. **Stop condition partially unmet** — it promised a within-stratum censoring-aware contrast; V5 covered sev1 only. Now completed: assist sev2 5.583→5.600, sev3 2.017→2.033 tail-completed. Qualitative result unchanged.

Interruption minutes, dropped from my interpretation, also rise 358→497 total (median 25.5→29.5) — another live week effect I should have reported.

## Stop rule applied

**Stop with limits.** The success criterion is met via branch (b): these data cannot identify the causal effect, and the specific threats are named. No named unresolved alternative could reverse the finding that the −47.5% headline is not a treatment effect, and no further local test could identify the effect — the exposure is perfectly confounded with the calendar.
