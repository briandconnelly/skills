# Investigation: How much did launching /lp/summer-sale improve checkout conversion?

## Route selection

Question: "How much did launching the /lp/summer-sale campaign improve our checkout conversion?"

This is the skill's own canonical example (SKILL.md line 38: "How much did launching the
campaign improve conversion" is a causal question carrying a number, with no design behind
it). Assignment is not randomized and not stated to be independent of the outcome — a
campaign landing page was shipped and drew whatever traffic clicked into it, with a checkout
form refactor and a logging-only release also happening in the same window. Nothing
identifies the effect, and there are multiple live rival explanations (the page itself,
the concurrent deploy, device-mix shift, a possible data gap). Per the routing table this
is **full**: a causal question no identifying design settles. The loop's job is to
establish whether the number is available, not to manufacture one.

Headless run (auto mode) — no user available to ask about assignment mechanism; proceeding
under the "assume nothing identifies the effect" default named in the skill, and stating
that assumption here.

## Problem

- Decision informed: whether to scale/continue the /lp/summer-sale campaign, and whether
  credit for any conversion change belongs to the campaign, the concurrent checkout-form
  deploy, or something else.
- Falsifiable question: what explains the change in checkout conversion (session-level
  `checkout_reached` rate) between the pre-launch period (2026-06-01..07) and the
  post-launch period (2026-06-08 onward), and how much of it, if any, is attributable to
  the /lp/summer-sale landing page itself?
- Success criteria: answered means either (a) a magnitude is produced with a design that
  identifies it, or (b) the loop establishes the magnitude is not identifiable from this
  data and reports the best available (associative) description plus what would be needed
  to identify it.
- Stop condition: conclude when no named unresolved alternative could reverse the answer.
- Effort budget: 20 read-only shell queries over the fixture CSVs (used: 6).

## Orientation (Plan-time, pre-registration)

- `orders.csv`: 268 rows, columns order_id, timestamp, amount, client_version.
  client_version ∈ {3.4.0, 3.4.1}. Timestamps span 2026-06-01T08:24Z .. 2026-06-14T16:54Z.
  No session_id / order_id linkage to sessions.csv exists in either file.
- `sessions.csv`: 9171 rows, columns session_id, timestamp, landing_page, device,
  checkout_reached. landing_page ∈ {/home, /product, /lp/summer-sale}. device ∈
  {desktop, mobile}. checkout_reached ∈ {yes, no}. No nulls/blanks in either file; no
  duplicate ids.
- `/lp/summer-sale` first appears in sessions.csv on 2026-06-08T08:00Z and continues daily
  through 06-14 — that date is the campaign launch.
- `deploys.log`: v3.3.9 (2026-06-03, /product copy tweaks), **v3.4.1 (2026-06-10T14:00Z,
  checkout form refactor + cart service bump)**, v3.4.2 (2026-06-12, logging only). The
  checkout-form deploy lands 2 days *after* the campaign launch, inside the post-launch
  window — a built-in confound for any pre/post comparison anchored on 06-08.
- Daily session volume: 600/day for 06-01..07 (pre-launch), 760/day for 06-08..12
  (post-launch, /lp/summer-sale adds ~160/day), then drops to 587 (06-13) and 584 (06-14)
  even though each day still spans the same 08:00-16:56 window — a volume drop with no
  time-truncation explanation.
- Cross-check against the independent `orders.csv` counter: daily order counts match
  sessions' `checkout_reached=yes` counts exactly for all of 06-01..06-12, then diverge on
  06-13 (17 vs 23) and 06-14 (11 vs 17) — orders run *higher* than the session-derived
  count. This is a data-validity finding from coverage/schema inspection, not from probing
  the landing-page/outcome relationship, so it is not retrospective; it is registered below
  as H4.

## Hypotheses

| id | claim | Candidate explanation | Prediction if true | Prediction if false | Necessary prediction (failure refutes) | Cheapest adequate test | Data needed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | causal | The /lp/summer-sale page itself converts (reaches checkout) at a different rate than existing pages, so adding it to the traffic mix moves the sitewide average | /lp/summer-sale's concurrent checkout_reached rate differs materially from /home and /product's | rate is statistically indistinguishable from other pages | /lp/summer-sale's rate must differ from the concurrent /home+/product rate | T1 | sessions.csv, landing_page × checkout_reached, 06-08..06-12 |
| H2 | causal | The checkout-form refactor deploy (v3.4.1, 06-10) improved checkout reach sitewide, independent of the campaign | non-campaign pages (/home,/product) show a rate step at/after 06-10 | non-campaign rate is flat across the deploy | non-campaign rate must step upward at 06-10 | T2 | sessions.csv, /home+/product only, by period |
| H3 | causal | A device-mix shift (desktop share rising post-launch) drove the aggregate rate change via composition, not the landing page | reweighting pre-launch device rates by post-launch device mix reproduces most of the observed change | reweighting reproduces near-zero of the change | reweighted change must account for a material share of the observed aggregate change | T3 | sessions.csv, device × checkout_reached, both periods |
| H4 | data-artifact | sessions.csv undercounts rows on 06-13/06-14 (logging gap), not a real traffic/conversion drop | independent counter (orders.csv) does not dip on those days while sessions' derived count does | orders.csv also dips in step with sessions | orders.csv daily count must not fall below sessions' checkout_reached=yes count once coverage is intact, and the gap must be confined to the low-volume days | T4 | orders.csv vs sessions.csv daily counts, all 14 days |

## Sources

| id | Origin (file, query, system) | Acquired | Coverage notes |
| --- | --- | --- | --- |
| S1 | `tests/fixtures/s1-conversion/sessions.csv` | 2026-07-16, local read | 9171 rows, 2026-06-01..14, no nulls, session-level, no order linkage |
| S2 | `tests/fixtures/s1-conversion/orders.csv` | 2026-07-16, local read | 268 rows, 2026-06-01..14, no nulls, no session linkage |
| S3 | `tests/fixtures/s1-conversion/deploys.log` | 2026-07-16, local read | 3 release lines, full window |

## Data Validity

- Collection method: sessions.csv appears to be a page/session event log; orders.csv a
  transaction log; deploys.log a release log. All three are flat files with no stated
  pipeline documentation — provenance beyond the files themselves is unknown.
- Coverage matrix (day × landing_page, sessions.csv): /home=400/day and /product=200/day
  hold exactly for 06-01..06-12; /lp/summer-sale=160/day for 06-08..06-12. On 06-13/06-14
  all three pages drop proportionally (311/127/149 and 304/126/154) — a uniform ~22-24%
  shortfall across every landing page and (checked below) both devices, not concentrated
  in one segment.
- Coverage matrix (day × device, sessions.csv): desktop share is stable at 41-46% for
  06-01..06-12, then jumps to 59% on 06-13/14 — consistent with a proportional row-drop
  that does not affect devices evenly in raw counts, but not evidence of a real device
  shift given the corroborating orders mismatch below.
- Field population: landing_page, device, checkout_reached, timestamp all 100% populated,
  every day, both files — a schema audit alone would have called this data clean, which is
  exactly what H4 checks past.
- Coverage baseline: orders.csv used as an independent denominator (produced by a different
  system than sessions.csv). It matches sessions' checkout_reached=yes count exactly for
  12 of 14 days and runs higher on the remaining two (06-13, 06-14), which is the day range
  where session row counts also drop — the shortfall is on the sessions/logging side, not
  in real order volume.
- Known instrument failures: none documented; the 06-13/14 shortfall is inferred here, not
  stated anywhere in the fixtures.
- Sensitivity checks performed: the orders-vs-sessions match on 06-01..06-12 (12/12 exact)
  is the known-positive baseline that the 06-13/14 mismatch is compared against — the
  method is shown capable of detecting a gap of this size before it's used to certify one.

## Tests

| id | Hypothesis | Preregistered prediction | Method | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| T1 | H1 | /lp/summer-sale rate differs materially from /home, /product, concurrently | group sessions.csv by landing_page × checkout_reached, 06-08..06-12 | CONSISTENT | /product 3.90% (39/1000), /home 2.70% (54/2000), /lp/summer-sale 0.50% (4/800) — S1 |
| T2 | H2 | non-campaign (/home+/product) rate steps up at/after 06-10 deploy | group /home+/product sessions by period: pre-launch 06-01..07, post-launch-pre-deploy 06-08..09, post-deploy 06-10..12 | CONTRADICTED | rates 3.12% (131/4200) → 3.00% (36/1200) → 3.17% (57/1800) — flat, no step at the deploy — S1 |
| T3 | H3 | device-mix reweighting reproduces most of the observed aggregate change | pre-launch device rates (desktop 3.36%=62/1846, mobile 2.93%=69/2354) reweighted by post-launch device mix (desktop 45.7%, mobile 54.3%) | CONTRADICTED | reweighted rate = 3.13%, vs actual pre-launch 3.12% — reweighting explains ~0 of the actual post-launch move to 2.4-2.6%; within-device breakdown also shows /lp/summer-sale far below /home,/product on both desktop (0.0%, 0/364) and mobile (0.92%, 4/436) — S1 |
| T4 | H4 | orders.csv (independent) does not dip on 06-13/14 while sessions-derived count does | compare daily order count against daily sessions checkout_reached=yes count, all 14 days | CONSISTENT | exact match all 12 days 06-01..06-12; 06-13: sessions=17 vs orders=23; 06-14: sessions=11 vs orders=17 — orders run higher, consistent with a sessions-side undercount, not a real conversion/order drop — S1, S2 |

## Amendments

None — no hypothesis was added after seeing the landing-page/outcome relationship; H4 came
from coverage inspection at Plan time, which the skill explicitly does not treat as
retrospective.

## Conclusion

- **Answer**: It didn't improve checkout conversion — the data shows the opposite
  association. The sitewide `checkout_reached` rate fell from 3.12% pre-launch
  (2026-06-01..07) to 2.43-2.63% in the post-launch window with clean coverage
  (2026-06-08..12), a drop of roughly 0.5-0.7 percentage points (~15-22% relative). This
  is driven by the new page itself: /lp/summer-sale sessions reach checkout at 0.50%,
  far below /home (2.70%) and /product (3.90%) in the same window, on both desktop and
  mobile. No rival explanation accounts for the change: the concurrent checkout-form
  deploy (06-10) shows no detectable effect on pages it should have improved sitewide if
  it were the driver; device-mix shift explains essentially none of the move under
  reweighting; and a real 06-13/14 volume drop in sessions.csv is a logging shortfall
  (confirmed against orders.csv), not evidence bearing on the campaign's effect, so those
  two days were excluded from the rate comparisons above rather than treated as part of
  the trend.
  This is associative, not causal: landing_page is not randomly assigned — visitors who
  land on /lp/summer-sale are a self-selected population (probably ad-click traffic) that
  may simply have different intent than organic /home or /product visitors, so the low
  rate cannot be attributed to the page's design or the campaign mechanism itself, only
  to which traffic it drew. Either way, "improvement" is not supported by this data; a
  decline is.
- Best supported: H1, via T1 and the device-stratified check under T3 (discriminating:
  the low rate persists within both device strata and is not reproduced by reweighting,
  so it is not a device-composition artifact).
- Per-hypothesis summary:

  | id | claim | status | basis |
  | --- | --- | --- | --- |
  | H1 | causal | UNRESOLVED | best supported (T1 CONSISTENT, corroborated by device-stratified breakdown under T3) |
  | H2 | causal | REFUTED | necessary prediction (a rate step at/after the 06-10 deploy on non-campaign pages) failed under T2 — rate is flat across the deploy |
  | H3 | causal | REFUTED | necessary prediction (reweighted device mix accounts for a material share of the change) failed under T3 — reweighting reproduces ~0 of the observed move |
  | H4 | data-artifact | UNRESOLVED | best supported for the 06-13/14 coverage gap (T4 CONSISTENT against the independent orders.csv baseline) |

- Limitations: this is associative only — no random or plausibly-independent assignment of
  visitors to landing pages exists in this data, so "the campaign caused lower conversion"
  is not licensed, only "the campaign's traffic converts lower, concurrently." Why
  /lp/summer-sale traffic converts so much lower (traffic-source mismatch, page UX, offer
  targeting) is not determinable from these three files and is an open possibility, not
  tested. sessions.csv and orders.csv cannot be joined (no shared id), so `checkout_reached`
  is used as the conversion proxy; it was validated against orders.csv counts on the 12
  clean-coverage days (exact match), which supports the proxy but does not prove a strict
  1:1 causal link at the row level. 06-13 and 06-14 are excluded from all rate comparisons
  because of the identified sessions-logging shortfall; this narrows the post-launch window
  analyzed but does not change the direction of the finding, since orders.csv (unaffected
  by the sessions-side gap) shows no conversion recovery on those two days either.
