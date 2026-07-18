# S5 (post-peek hypothesis) — transcript evidence

Grounds the S5 rows in `tests/scenarios.md` (First and Second waves).
Run keys, hashes, and instrument validation: `2026-07-17-transcript-evidence-corpus.md`; full per-run manifests: `2026-07-17-transcript-evidence-manifests.md`.

**Standing caveat this file preserves:** the scenario is recorded invalid as written, and the skill's `retrospective` rule remains unverified.
Nothing below upgrades that: label occurrences and event orderings are machine facts, but whether any labelled hypothesis was *genuinely* post-peek, and whether any promoting evidence was independent, are human-scored questions these runs cannot settle.

## Scope

| Run key | Wave | Recorded score | Validity |
| --- | --- | --- | --- |
| s5-baseline | First | 1/2 | prompt listed the full `orders.csv` schema (contaminated) |
| s5-with-skill | First | 1/2 scoreable | same contamination; assertion 1 untested |
| s5-baseline-corrected | Second | 1/2 | corrected prompt, but scenario later found invalid as written |
| s5-with-skill-corrected | Second | 1/2 (re-scored from 2/2) | same |

## Machine-checked counts and orderings

| Run | Tool calls | Bash | Read | Write | Edit | Result statuses |
| --- | --- | --- | --- | --- | --- | --- |
| s5-baseline | 14 | 14 | 0 | 0 | 0 | 14 ok |
| s5-with-skill | **13** (Results cell corrected from 12) | 8 | 3 | 1 | 1 | 13 ok |
| s5-baseline-corrected | 12 | 12 | 0 | 0 | 0 | 11 ok, 1 error |
| s5-with-skill-corrected | 14 | 12 | 2 | 0 | 0 | 13 ok, 1 error |

The two `error` results are ordinary command failures, not gate events: s5-baseline-corrected ordinal 8 and s5-with-skill-corrected ordinal 9 are pandas invocations that failed (`Invalid frequency: H`, a pandas 2.x deprecation) and were rerun successfully at the next ordinal.

**s5-with-skill externalized its hypothesis table mid-run — but the ordering does not establish clean preregistration.**
The machine-checked emission order is: Reads 1–3 (skill, template, fixture), Bash 4–5, **ledger Write at ordinal 6 containing a four-row hypothesis table**, test Bash 7–12, amendment Edit at ordinal 13 — so the table preceded every test query, unlike the S1 runs, where all output postdates all queries.
But the pre-Write probes were not schema-only.
Ordinal 5 ran `head -5 checkout_errors.csv`, `tail -5 orders.csv`, and `tail -5 sessions.csv`, and its result exposed four `2026-06-08 northbank timeout` rows and five `/lp/summer-sale` sessions all with `checkout_reached=no` — provider-error data and outcome-labeled campaign rows, seen before H1 (payment provider) and H3 (mix shift) were written.
Under the skill's own line between orientation and cause–outcome inspection, that exposure means the transcript cannot classify these hypotheses as cleanly preregistered; what it establishes is the externalization ordering plus exactly what the agent had seen at Write time.
The Write's H1 row is the payment-provider hypothesis:

```
| H1 | Payment provider (northbank) reliability issue in week 2 caused checkout failures at payment step | checkout_errors concentrated in week 2 / northbank; orders/checkout_reached drops specifically for northbank while checkout_reached rate (top funnel) stays flat | errors flat or absent in week 2; northbank order share unchanged | T2 | checkout_errors.csv, orders.csv (payment_provider), sessions.csv (checkout_reached) |
```

This is the machine evidence for the recorded invalidation: the payment hypothesis was written into the table at ordinal 6 (the contaminated prompt named the schema, and the ordinal-5 probe had already shown the error file's first rows), so the post-peek path assertion 1 exists to test was never exercised.

**s5-with-skill's amendment mechanism fired, with reasons, as a mid-run Edit** (ordinal 13, after the tests it documents).
The Edit's Amendments section, verbatim:

```
- 2026-07-16: discovered `checkout_errors.csv` in the fixture directory (not mentioned in the task's file list). Treated as in-scope, read-only evidence per the data-validity step; added as source S4 and folded into H1/T2 rather than opening a new hypothesis, since it bears directly on the pre-registered payment-provider hypothesis.
- 2026-07-16: added T0 (metric check) before running T1-T5, because the task's stated 3.1%/2.5% only reproduces under `checkout_reached/sessions`, not `orders/sessions` (2.75%, doesn't round to 2.5%). This redefines "checkout conversion" as the session→checkout_reached rate for the remainder of the analysis, not order completion. Consequently T1 (funnel-localization, H4) could not run as planned — recorded NON_DISCRIMINATING rather than silently reinterpreted.
- 2026-07-16: added T5 (retrospective) to check whether the device mix/rate shift is independent of the landing-page effect (H3 originally bundled both under one test); split out because /lp/summer-sale traffic skews the device breakdown.
```

The literal token `retrospective` appears in the T5 amendment; whether T5 was the *kind* of addition the rule governs is judgment, recorded as such.

**s5-with-skill-corrected blanket-labelled every hypothesis `retrospective` and disclosed why** (final text; this run made no Write/Edit, so its ledger exists only in the reply):

> Orientation (schemas, row counts, distinct values, deploy log) was done cleanly first. However, in a non-interactive single pass I then continued directly into cross-period/cross-segment comparisons […] before formally writing the hypothesis table. Per the skill, that crosses the line from orientation into cause-effect inspection, so **every hypothesis below is labeled `retrospective`** and cannot be "best supported" on the strength of that initial exploration alone.

**The re-scored assertion-2 FAIL has a machine-checkable substrate.**
All 12 of s5-with-skill-corrected's Bash commands operate on the s5 fixture directory (11 begin `cd <REPO_ROOT>/hypothesis-driven-analysis/tests/fixtures/s5-conversion-payment`; the twelfth is an `ls` of the same directory), and its 2 Reads are `SKILL.md` and `references/ledger-template.md`.
No other data source exists anywhere in the run's tool surface, so every "fresh discriminating test" necessarily ran over the records that generated the hypotheses.
That the skill's independence bar therefore wasn't met is the recorded scorer judgment; the single-source fact is the transcript's.

## Verbatim testimony behind the recorded judgments

**s5-baseline asserted an untested causal mechanism** (final text):

> This begins ~18 hours after the `v3.4.1` deploy on 2026-06-10 14:00 UTC ("checkout form refactor, cart service bump" — `deploys.log`), suggesting the refactor broke something in the swiftpay payment payload/integration.

**s5-baseline-corrected asserted two, each naming a deploy** (final text):

> This looks like the form refactor broke the `checkout_reached` analytics event for a subset of sessions […]

> Despite this ~12x error spike, swiftpay order counts stayed flat (48 orders wk1 vs 49 wk2), so this doesn't explain the conversion drop — but it's a real reliability regression introduced by the "cart service bump" worth investigating with the payments team.

Ground truth attributes the tracking gap to the v3.4.2 logging-only deploy, not v3.4.1 — "both wrong about which deploy" is the recorded judgment; the claims are now quoted.

**s5-with-skill-corrected refuted the swiftpay claim on its necessary prediction and quantified the artifact** (ledger in final text):

```
| T2 | H2 | swiftpay order volume falls when errors spike 4→47/day | daily swiftpay orders vs error counts | **CONTRADICTED** | swiftpay orders/week: 48 (wk1) vs 49 (wk2); daily counts flat through 6/11–14 despite errors at 47/day (S2, S3) |
```

> Correcting for this using `orders` as ground truth reduces the "real" drop from 0.651pp to 0.370pp — meaning **roughly 43% of the reported drop is a measurement artifact, not a real conversion decline**.

## Reconciliation with the Results tables

- First-wave S5 with-skill tool-call cell corrected 12 → 13 in `tests/scenarios.md`; the other three rows' counts match as recorded.
- The scenario-invalid finding and the `retrospective` rule's unverified status are confirmed, not weakened, by this evidence: the one run that could have exercised post-peek labeling wrote the planted hypothesis into its table at ordinal 6, after a probe that had already shown the planted signal's first rows.
