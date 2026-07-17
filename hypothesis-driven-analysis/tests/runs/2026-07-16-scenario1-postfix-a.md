# Investigation: weekly checkout conversion dropped 3.1% -> 2.5%, week of 2026-06-01 vs week of 2026-06-08 — why?

## Process note (read before Conclusion)

Orientation for this run did not stay strictly ahead of hypothesis formation.
Before the Hypotheses table below was written, I had already run two candidate-cause x outcome crossings — `checkout_reached` rate by `landing_page` x week, and by `device` x week — while exploring the data.
Per the skill, that means any hypothesis resting on `landing_page` or `device` as the cause is `retrospective`, and can only be marked "best supported" on evidence that did not inform it.
This dataset is small and closed (14 days, 2 files); no held-out slice of it is available.
H1 and H3 are labelled `(retrospective)` below and the bar is applied honestly: `REFUTED` is not gated by this rule (a necessary-prediction failure is a failure regardless of when the hypothesis was written), but `UNRESOLVED` + "best supported" is, and H1 does not formally clear it even though its evidence is strong. This is disclosed rather than smoothed over.
H2 (deploy-log-driven) and H4 (data-validity coverage check) did not require that crossing to be framed and are not retrospective.

## Problem

- Decision informed: whether to roll back / investigate the checkout-form deploy, pause the new campaign landing page, or file a logging-pipeline bug — three different remediation paths with different owners.
- Falsifiable question: what explains the drop in weekly checkout conversion (`checkout_reached='yes'` / sessions) from 3.12% (2026-06-01..06-07) to 2.51% (2026-06-08..06-14)?
- Success criteria: answered means one or more explanations account for the drop and survive a discriminating test; alternatives that don't survive are named as ruled out.
- Stop condition: conclude when no named unresolved alternative could reverse the remediation decision.
- Effort budget: 20 tool calls (used: ~10).

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 (retrospective) | causal | New `/lp/summer-sale` campaign landing page (first seen 2026-06-08) added session volume with a much lower per-session conversion rate, mechanically diluting the blended week-2 rate | excluding summer-sale sessions, week-2 rate ≈ week-1 rate | excluding summer-sale sessions, week-2 rate stays well below week-1 | the residual gap after excluding summer-sale traffic must be small/negligible | T1 | sessions.csv |
| H2 | causal | Checkout-form-refactor deploy (v3.4.1, 2026-06-10T14:00:07Z) degraded checkout completion | completion ratio (orders / checkout_reached='yes') drops at/after the deploy | completion ratio unchanged across the deploy boundary | completion ratio must drop after the deploy relative to before it | T2 | orders.csv, sessions.csv, deploys.log |
| H3 (retrospective) | causal | Device mix shifted toward a lower-converting device between week 1 and week 2 | reweighting week-2's per-device rates onto week-1's device mix recovers most of the week1-vs-week2 gap | reweighting doesn't close the gap | the reweighted rate must land materially closer to week-1's rate than to week-2's actual rate | T3 | sessions.csv |
| H4 | data-artifact | `sessions.csv` logging undercounted `checkout_reached` (and total sessions) on 2026-06-13/06-14, producing an internally impossible count (orders > checkout_reached='yes') confined to those two days | orders > checkout_reached-yes on 06-13/06-14, and nowhere else in the window | orders ≤ checkout_reached-yes on every day, including 06-13/06-14 | orders must exceed checkout_reached-yes on 06-13/06-14 and not on any other day | T4 | orders.csv, sessions.csv |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `tests/fixtures/s1-conversion/orders.csv` | 2026-07-16, local read | 268 rows, 2026-06-01..2026-06-14, no nulls, no duplicate `order_id` |
| S2 | `tests/fixtures/s1-conversion/sessions.csv` | 2026-07-16, local read | 9171 rows, 2026-06-01..2026-06-14, no nulls, no duplicate `session_id` |
| S3 | `tests/fixtures/s1-conversion/deploys.log` | 2026-07-16, local read | 3 release lines, 2026-06-03..2026-06-12 |

## Data Validity

- Collection method: flat CSV exports; `orders.csv` has one row per completed order (`order_id, timestamp, amount, client_version`); `sessions.csv` has one row per site session (`session_id, timestamp, landing_page, device, checkout_reached`). No session-to-order key exists in either file — they can only be joined at the day/segment aggregate level, not per-user.
- Coverage matrix (sessions, day x landing_page): `/home` and `/product` run every day of both weeks (400/day and 200/day respectively, dropping proportionally on 06-13/06-14 with total volume). `/lp/summer-sale` has **zero** rows 06-01..06-07 and appears at ~160/day from 06-08 onward — a clean new-segment launch, not a preexisting low-volume page that grew.
- Coverage matrix (sessions, day x device): desktop and mobile both present every day; desktop share is roughly stable (~44-49%) except 06-13/06-14 where desktop's share rises to ~59% — coincident with the volume shortfall described below, not an independent signal.
- Field population: `landing_page`, `device`, `checkout_reached`, `timestamp` are 100% populated across all 9171 session rows; `client_version` is 100% populated across all 268 order rows but is **day-granular, not request-granular** — every order on 2026-06-10 (deploy day, deploy at 14:00:07Z) is tagged `3.4.1`, including 12 orders timestamped before 14:00. This means `client_version` cannot be used to isolate pre/post-deploy orders on the deploy day itself; the deploy timestamp must be used directly instead.
- Coverage baseline: no independent traffic counter (e.g. a CDN or load-balancer log) exists in this fixture to validate `sessions.csv` volume against, so total session-count coverage is **unverifiable**, not clean. One internal logical check is available: `checkout_reached='yes'` is defined as a prerequisite funnel stage that must be ≥ same-day order count. That check holds as an equality (`checkout_reached-yes == orders`) on 12 of 14 days and is violated only on 06-13 and 06-14 (see T4) — a concrete, falsifiable failure mechanism, not a ritual entry.
- Known instrument failures: the 06-13/06-14 `checkout_reached` undercount (T4); the day-granular `client_version` labeling on orders (above).
- Sensitivity checks performed: the `checkout_reached-yes == orders` check is a positive control on itself — it correctly reads as equality on 12/14 days (proving the method isn't trivially insensitive) and correctly flags inequality exactly on the two days where session and order counts diverge from the pattern, so a real gap of this size (6 and 6 orders respectively) is within its detection range.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | excluding `/lp/summer-sale`, week-2 rate ≈ week-1 rate (3.12%) | recompute week-2 `checkout_reached` rate over `/home` + `/product` only; also compare Mon-Fri-only subsets to sidestep the H4 artifact days | CONSISTENT | Full week-2 excl. campaign: 119/3918 = 3.04% (S2). Mon-Fri-only, excl. campaign, excl. 06-13/14: week-1 93/3000 = 3.10% vs week-2 93/3000 = 3.10% — exact match on both numerator and denominator (S2) |
| T2 | H2 | completion ratio drops at/after 2026-06-10T14:00:07Z | daily `orders / checkout_reached-yes` ratio, 06-08..06-12 (spanning the deploy) | CONTRADICTED | ratio is exactly 100% (orders == checkout_reached-yes) on every one of 06-08, 06-09, 06-10, 06-11, 06-12 — no shift at or after the deploy (S1, S2) |
| T3 | H3 | reweighting week-2 per-device rates onto week-1's device mix lands materially closer to week-1's 3.12% than to week-2's actual 2.51% | counterfactual reweight: Σ(week1 device share x week2 per-device rate) | CONTRADICTED | reweighted rate = 2.54%, essentially identical to the actual week-2 blended rate (2.51%) and far from week-1's 3.12% — the device-mix shift explains almost none of the gap (S2) |
| T4 | H4 | orders > checkout_reached-yes on 06-13/06-14 only | per-day comparison of `checkout_reached-yes` count vs order count across all 14 days | CONSISTENT | equal on all 12 other days (e.g. 06-10: 23=23); 06-13: cr_yes=17 vs orders=23; 06-14: cr_yes=11 vs orders=17 (S1, S2) |

## Amendments

- 2026-07-16: no new hypotheses added after Plan; see Process note above for the retrospective labels applied to H1 and H3 due to an early orientation crossing.

## Conclusion

- Answer: the drop is best explained by traffic-mix dilution from a new campaign landing page (`/lp/summer-sale`, live from 2026-06-08) that converts far below the rest of the site — excluding it, week-2's conversion among pre-existing traffic is statistically indistinguishable from week-1's (T1). A checkout-form deploy on 06-10 is ruled out (T2), and a device-mix shift is ruled out as a material contributor (T3). Separately, a two-day logging gap (06-13/06-14) makes the reported week-2 rate look slightly worse than the underlying traffic actually was (T4/H4); this is a real but minor contributor to the headline number, not the driver.
- Best supported: H4 for its narrow coverage-gap claim (T4 CONSISTENT, non-retrospective). H1 has the strongest and cleanest evidence of any hypothesis in this table (T1: an exact 93/3000 vs 93/3000 match on the Mon-Fri, non-campaign, non-artifact subset) but is retrospective with no held-out slice available in this closed dataset to formally clear the "best supported" bar — reported as the leading explanation, not asserted as fully confirmed. See Limitations.
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 (retrospective) | causal | UNRESOLVED | necessary prediction held under T1 (residual gap ~0 on the cleanest subset), but retrospective with no qualifying held-out evidence in this dataset, so not promoted to "best supported" under the skill's bar — reported as the leading exploratory explanation |
  | H2 | causal | REFUTED | necessary prediction (completion-ratio drop at/after the deploy) failed under T2, an adequate test |
  | H3 (retrospective) | causal | REFUTED | necessary prediction (reweighting closes the gap) failed under T3, an adequate test — refutation stands regardless of retrospective status |
  | H4 | data-artifact | UNRESOLVED | best supported for its narrow claim; T4 CONSISTENT, non-retrospective |

- Limitations:
  - H1's evidentiary strength (T1) is real, but the process note at the top applies: this specific dataset offers no slice of `sessions.csv` that didn't already inform H1 when it was framed, so it cannot be formally promoted past "leading exploratory explanation" per the skill's retrospective-evidence bar. A genuinely new check — e.g. next week's data with the campaign paused, or an independent ad-spend/impressions feed for `/lp/summer-sale` — would let it clear that bar.
  - Whether `/lp/summer-sale`'s 0.57% rate reflects genuinely low-intent promotional traffic or a checkout-tracking gap specific to that landing page cannot be determined from this data — there's no independent instrumentation check for that page the way T4 provided one for 06-13/06-14. Worth checking before deciding whether to pause the campaign or file an instrumentation bug against it.
  - Total session-volume coverage (the 600/day -> 760/day step and the 06-13/06-14 shortfall) has no independent counter to validate against; T4 validates the `checkout_reached` sub-field logically but not total session volume itself.
  - All claims here are associative: landing-page and device assignment were not randomized or otherwise identified, so "the campaign traffic is associated with the lower rate" is as far as this data supports — it does not rule out that the campaign itself was launched for reasons correlated with the drop.
