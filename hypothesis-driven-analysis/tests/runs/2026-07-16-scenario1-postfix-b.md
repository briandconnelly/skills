# Investigation: weekly checkout conversion dropped from 3.1% to 2.5% (week of 2026-06-01 vs week of 2026-06-08) — why?

## Problem

- Decision informed: whether to roll back the 2026-06-10 `v3.4.1` deploy, pause the `/lp/summer-sale` campaign, or investigate a device-specific checkout bug — these are mutually exclusive remediation paths, so the answer changes what ships next.
- Falsifiable question: what explains the drop in checkout conversion rate for sessions between the week of 2026-06-01 (2026-06-01..2026-06-07) and the week of 2026-06-08 (2026-06-08..2026-06-14), UTC days, all traffic?
- Success criteria: answered means one or more explanations account for the observed drop and survive a discriminating test, with no named unresolved alternative that could reverse the answer.
- Stop condition: conclude when the success criterion is met and no named unresolved alternative could reverse the answer; otherwise stop with limits.
- Effort budget: 30 read-only bash/python queries over the fixture files.

Assumption stated (headless run, consultation gate skipped per skill): "checkout conversion" = `checkout_reached == yes` sessions / total sessions, computed per UTC calendar week. This was confirmed against the stated figures during orientation: week1 = 131/4200 = 3.12%, week2 = 125/4971 = 2.51%, matching the given 3.1%/2.5% to one decimal place. `orders.csv` and `sessions.csv` share no join key (no `session_id` in orders, no `order_id` in sessions), so orders cannot be used as the conversion numerator directly — order counts diverge from `checkout_reached` counts on several days (e.g. 06-13: 17 checkouts vs 23 orders), confirming they are independent, not joinable, records.

## Plan / Orientation (pre-registration; no cause-outcome relationship inspected yet)

Inspected: schema (both CSVs have no null/empty fields), row counts (orders=268, sessions=9171), date coverage (2026-06-01..2026-06-14 in both files), distinct values of `device` (desktop/mobile), `landing_page` (`/home`, `/product`, `/lp/summer-sale`), `client_version` (`3.4.0`, `3.4.1`), and `deploys.log` (3 releases: 06-03 copy tweaks, 06-10T14:00:07Z "checkout form refactor, cart service bump", 06-12 logging-only).
Also inspected, as volume/timing facts only (not yet crossed with the outcome): sessions/day, sessions/day×device, sessions/day×landing_page, orders/day×client_version, and calendar day-of-week for the anomalous tail days. These are coverage/composition/timing facts, not a candidate-cause-vs-outcome relationship, so hypotheses framed from them are not retrospective.

Findings that shaped the hypothesis table:
- `/lp/summer-sale` appears for the first time on 2026-06-08 (start of week2) at ~160 sessions/day, and week2's daily session volume is exactly week1's ~600/day plus that ~160 — i.e. fully additive new traffic, not a shift from existing pages.
- `client_version` in `orders.csv` switches cleanly from `3.4.0` to `3.4.1` starting 2026-06-10, aligned with the `v3.4.1` deploy that day.
- Session volume drops on 2026-06-13/06-14 (587/584 vs ~760 on 06-08..06-12) with a device-mix reversal (desktop > mobile, the only two days in the dataset where that happens). The analogous weekend day in week1, 06-07 (also a Sunday), shows no such dip or reversal (600 sessions, mobile 330 > desktop 270, in line with every other week1 day) — so this isn't an ordinary weekly cycle.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | The 06-10 `v3.4.1` deploy ("checkout form refactor, cart service bump") broke/degraded the checkout funnel | conversion in week2 stays near week1 baseline before 06-10T14:00Z and drops after | conversion is already depressed on 06-08/06-09, before the deploy | the drop must not precede 2026-06-10T14:00:07Z — a deploy cannot cause an outcome shift that already happened before it shipped | T1 | sessions.csv timestamps + checkout_reached, deploys.log |
| H2 | descriptive (estimand: within-landing-page-segment conversion rate, week1 vs week2, and whether the blended drop is arithmetically explained by the new segment's volume and rate) | New `/lp/summer-sale` traffic, added wholesale at week2 start, converts far below the existing pages, mechanically pulling the blended weekly rate down (a mix-shift/compositional effect, not a within-page regression) | `/home` and `/product` per-page rates stay ~flat week1→week2; `/lp/summer-sale`'s rate is well below the others; removing it from week2 restores the blended rate to ~week1 baseline | `/home` and/or `/product` rates also drop by a magnitude comparable to the overall drop | `/home` and `/product` per-page rates must not both drop by a magnitude comparable to the overall week-over-week drop | T2 | sessions.csv landing_page × checkout_reached |
| H3 | causal | The `v3.4.1` "cart service bump" hit mobile checkout disproportionately hard | mobile conversion drops more than desktop between week1 and week2 | mobile and desktop move similarly, or mobile drops less than desktop | mobile's per-device conversion rate must decline measurably more than desktop's | T3 | sessions.csv device × checkout_reached |
| H4 | data-artifact | The 06-13/06-14 session volume dip and device-mix reversal is a session-logging gap (undercounting mobile sessions), not a genuine traffic collapse | an independent signal (order volume) stays within its normal range on those days despite the apparent session/mobile collapse, and the pattern does not match week1's equivalent weekend day | order volume also drops on 06-13/06-14, and/or week1's equivalent weekend (06-07) shows the same dip/reversal, indicating an ordinary weekly cycle instead | order volume must not stay within the normal daily range while sessions (esp. mobile) collapse — if it does, "genuine traffic decline" fails as the explanation | T4 | orders.csv day counts, sessions.csv day×device counts, calendar |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `tests/fixtures/s1-conversion/orders.csv` | read 2026-07-16 | 268 rows, 2026-06-01..2026-06-14, no nulls; no session-level join key |
| S2 | `tests/fixtures/s1-conversion/sessions.csv` | read 2026-07-16 | 9171 rows, 2026-06-01..2026-06-14, no nulls; no order-level join key |
| S3 | `tests/fixtures/s1-conversion/deploys.log` | read 2026-07-16 | 3 lines, full log for the window, no gaps apparent |

## Data Validity

- Collection method: flat-file exports; `sessions.csv` is the funnel-instrumentation record (`checkout_reached` flag), `orders.csv` is the completed-order record; the two are independent systems with no shared key.
- Coverage matrix (week × device, week × landing_page, sessions grain): week1 carries a flat 600 sessions/day, split 400/`home`+200/`product` and ~44%/56% desktop/mobile every single day, including the week1 Sunday (06-07). Week2 carries 760 sessions/day 06-08..06-12 (400/`home`+160/`lp/summer-sale`+200/`product`), then drops to 587 (06-13) and 584 (06-14) with desktop > mobile on those two days only — every other day in both weeks has mobile > desktop. No day in either file has zero rows; the anomaly is a volume/composition shift on exactly 2 of 14 days, not a missing day.
- Field population: `checkout_reached`, `device`, `landing_page`, `timestamp` are 100% populated in `sessions.csv`; `client_version`, `amount`, `timestamp` are 100% populated in `orders.csv` — checked at the per-day grain, not just totals.
- Coverage baseline: no independent request-volume counter exists in these fixtures to corroborate true traffic; used `orders.csv` daily counts as an approximate independent signal for T4, and week1's Sunday (06-07) as an in-sample calendar baseline for "is this an ordinary weekend pattern."
- Known instrument failures: none documented; the 06-13/06-14 anomaly is inferred, not logged.
- Sensitivity checks performed: the checkout-conversion computation was cross-checked against the user-stated 3.1%/2.5% figures before use (3.12%/2.51%), confirming the metric definition and the instrument are not blind to a change of this size.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | drop must not precede 2026-06-10T14:00:07Z | split week2 sessions at the deploy timestamp; compare conversion pre/post, and against week1 baseline | CONTRADICTED | week1 baseline 3.12% (4200 sessions, 131 checkouts); week2 pre-deploy 2.66% (2029, 54); week2 post-deploy 2.41% (2942, 71). Pre-deploy conversion is already close to the full week2 rate (2.51%) and well below week1, i.e. most of the drop existed before the deploy shipped (S2) |
| T2 | H2 | `/home`/`/product` rates flat; `/lp/summer-sale` rate well below them; exclusion restores baseline | per-landing_page conversion week1 vs week2; counterfactual exclusion of `/lp/summer-sale` from week2 | CONSISTENT | `/home` 2.71%→2.68%; `/product` 3.93%→3.76% (both ~flat); `/lp/summer-sale` week2 = 0.57% (1053 sessions, 6 checkouts); week2 excl. summer-sale = 3.04% (3918, 119) vs week1 3.12% — nearly full recovery (S2) |
| T3 | H3 | mobile declines more than desktop | per-device conversion week1 vs week2, blended and re-checked excluding `/lp/summer-sale` | CONTRADICTED | Blended: desktop 3.36%→2.22%, mobile 2.93%→2.79% — desktop dropped more. Excl. summer-sale (isolating within-`/home`+`/product`): desktop 3.36%→2.75% (still down), mobile 2.93%→3.31% (up). Opposite of the predicted direction in both cuts (S2) |
| T4 | H4 | order volume normal while sessions/mobile collapse on 06-13/06-14; no such pattern on week1's equivalent Sunday | compare `orders.csv` daily counts and `sessions.csv` device split on 06-13/06-14 against the rest of the dataset and against 06-07 | CONSISTENT | Orders on 06-13/06-14: 23 and 17 — both within/at the top of the normal daily range (17–23 across the whole dataset), i.e. no order-volume decline. Sessions same days: 587/584 total, desktop>mobile (345/242 and 346/238) — the only two such days in the set. Week1's Sunday 06-07: 600 sessions, mobile 330 > desktop 270, matching every other week1 day — no equivalent dip (S1, S2) |

Supplementary probe (not a separate hypothesis; run to check whether T3's desktop-decline finding materially affects the H2 conclusion or is confined to the H4 anomaly window): within `/home`+`/product` only, desktop conversion by week2 sub-period — 06-08..06-12: 2.84% (1374, 39); 06-13..06-14: 2.54% (552, 14) — the desktop softness is present across week2, not concentrated in the H4 anomaly window, and daily desktop rates swing 2.21%–3.69% on n≈250–300/day (consistent with sampling noise around a ~3% rate, SE≈1pp). Restricting to 06-08..06-12 only (excluding the H4 anomaly entirely): overall conversion is 2.55% (3800, 97), and excluding `/lp/summer-sale` from that same window recovers 3.10% (3000, 93) — matching week1's 3.12% almost exactly, with or without the 06-13/06-14 days included. This shows H4's anomaly is not what drives the topline drop, and the residual desktop/mobile split shift nets to noise-level once the two devices are combined (3.04–3.10% vs 3.12% baseline).

## Amendments

None. All four hypotheses were registered from orientation-only facts (schema, volume, timing, calendar) before any cause-outcome (segment-vs-conversion) data was inspected; no hypothesis is retrospective.

## Conclusion

- Answer: the conversion drop from 3.12% to 2.51% is explained by a traffic-composition change, not a functional regression: a new `/lp/summer-sale` landing page launched exactly at the start of week2, adding ~160 sessions/day that convert at 0.57% (vs. ~3% elsewhere), which mechanically pulls the blended weekly rate down. Within-page conversion on the pre-existing pages (`/home`, `/product`) is essentially unchanged. Removing the new page's traffic from week2 recovers a 3.04–3.10% rate, matching week1's 3.12% baseline — with or without the separately-identified 06-13/06-14 anomaly included. The 06-10 `v3.4.1` deploy and a mobile-specific defect are both ruled out as drivers of the drop.
- Best supported: H2, via T2 (discriminating: flat within-page rates, a starkly low new-segment rate, and a counterfactual exclusion that reproduces the missing ~0.5–0.6pp of the drop).
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | REFUTED | necessary timing prediction failed under T1 — most of the drop (week2 pre-deploy 2.66%, vs. week1's 3.12%) was already present before the 06-10T14:00:07Z deploy |
  | H2 | descriptive (estimand: within-page conversion rate + mix decomposition) | UNRESOLVED | best supported — T2 CONSISTENT: flat within-page rates, low new-segment rate, counterfactual exclusion restores baseline |
  | H3 | causal | REFUTED | necessary directional prediction failed under T3 in both the blended and summer-sale-excluded cuts — desktop declined more than mobile, the opposite of the predicted mechanism |
  | H4 | data-artifact | UNRESOLVED | best supported for the coverage anomaly itself (T4 CONSISTENT: normal order volume alongside a mobile session collapse confined to 06-13/06-14, with no equivalent pattern on week1's matching Sunday) — but the supplementary probe shows this anomaly is not material to the topline conversion drop (06-08..06-12 alone already reproduces the same ~2.5% rate and the same ~3.1% recovery when summer-sale is excluded) |

- Limitations: the claim is associative — `/lp/summer-sale` traffic was not randomly assigned, and while the within-page rates and the counterfactual arithmetic are direct, records-settled facts (H2 is a descriptive/compositional claim, not one requiring causal identification), *why* the new page converts so much lower (creative quality, audience targeting, price-sensitive intent, a landing-page bug) is not determined by this data — the fixtures have no page-level content, funnel-step, or campaign-targeting detail to test that further. A residual desktop-conversion softness (~3.36%→~2.8% within `/home`+`/product`, roughly offset by a mobile uptick) was observed but is small, present across all of week2 (not concentrated in the H4 window), and consistent with sampling noise at the daily grain (n≈250–300/day) — it does not change the answer and was not promoted to a formal hypothesis since it emerged only after inspecting the cause-outcome data (it would be retrospective, and no held-out evidence exists to test it against). The 06-13/06-14 session-logging anomaly (H4) is real by the tests run here but is a separate, non-driving finding worth flagging to whoever owns session instrumentation — it was not investigated further since it doesn't bear on the conversion-drop question.
