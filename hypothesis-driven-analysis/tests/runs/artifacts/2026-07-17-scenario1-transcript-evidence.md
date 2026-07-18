# S1 (multi-explanation diagnostic) — transcript evidence

Grounds the S1 rows in `tests/scenarios.md` (First, Second, and Fourth waves).
Run keys, hashes, and instrument validation: `2026-07-17-transcript-evidence-corpus.md`; full per-run manifests: `2026-07-17-transcript-evidence-manifests.md`.

## Scope

| Run key | Wave | Recorded score | Skill text exercised |
| --- | --- | --- | --- |
| s1-baseline | First | 2/6 | none (baseline) |
| s1-with-skill | First | 5/6 | pre-fix skill |
| s1-with-skill-rerun | Second | 6/6 | fixed skill (`e55ba78`) |
| s1-postfix-a | Fourth | 6/6 (causal-status probe only) | restored status vocabulary |
| s1-postfix-b | Fourth | 6/6 (causal-status probe only) | restored status vocabulary |

The Fourth-wave runs were scored only for causal-status behavior and `data-artifact` adoption, not S1's full assertion table; this file preserves that scoping.

## Machine-checked counts and orderings

Tool totals (predicate: count of `tool_use` blocks; per-tool split from `identity`):

| Run | Tool calls | Bash | Read | Write | Result statuses |
| --- | --- | --- | --- | --- | --- |
| s1-baseline | 8 | 7 | 1 | 0 | 8 ok |
| s1-with-skill | **13** (Results cell corrected from 12) | 9 | 3 | 1 | 13 ok |
| s1-with-skill-rerun | 13 | 9 | 4 | 0 | 13 ok |
| s1-postfix-a | 14 | 11 | 2 | 1 | 14 ok |
| s1-postfix-b | 15 | 12 | 2 | 1 | 15 ok |

**The baseline produced no ledger, machine-checked over the complete output surface.**
It made zero Write/Edit calls, and its assistant text contains zero matches for the ledger-structure predicate `^\| H[0-9]|^#+ +Hypotheses|^#+ +(Sources|Tests|Amendments)\b`.
The same predicate fires 8 times on the s12-rerun transcript's text, so its zero here is a working instrument's zero.

**Ledger emission order — what it can and cannot establish.**
In s1-with-skill the ledger Write is ordinal 13 of 13, after all 9 Bash queries, and the run's only assistant text block also follows tool_use 13.
s1-with-skill-rerun emitted everything in a single text block after tool_use 13; s1-postfix-a's ledger Write is ordinal 14 of 14; s1-postfix-b's is 15 of 15.
So for all four with-skill runs, the transcript's emission order cannot establish S1 assertion 1 ("a ledger … before running analysis queries"): every externalized ledger postdates every query.
The recorded passes on that assertion rest on the ledgers' internal structure — which is the agent's own narrative — and the Second-wave rerun discloses this itself (see below).
This is recorded as a limit, not a re-score: preregistration may well have happened in-context, but the transcript cannot show it.

**`data-artifact` adoption is literal, not paraphrase.**
The Fourth-wave record says both postfix runs labelled the records-quality hypothesis `data-artifact`; the literal token `data-artifact` appears in both ledger Writes (2 occurrences each, the claim-column cell and the summary row for H4).

**The six causal-status rows the Fourth-wave findings count are in the ledger Writes, verbatim:**

s1-postfix-a (Write ordinal 14), per-hypothesis summary rows:

```
| H1 (retrospective) | causal | UNRESOLVED | necessary prediction held under T1 (residual gap ~0 on the cleanest subset), but retrospective with no qualifying held-out evidence in this dataset, so not promoted to "best supported" under the skill's bar — reported as the leading exploratory explanation |
| H2 | causal | REFUTED | necessary prediction (completion-ratio drop at/after the deploy) failed under T2, an adequate test |
| H3 (retrospective) | causal | REFUTED | necessary prediction (reweighting closes the gap) failed under T3, an adequate test — refutation stands regardless of retrospective status |
| H4 | data-artifact | UNRESOLVED | best supported for its narrow claim; T4 CONSISTENT, non-retrospective |
```

s1-postfix-b (Write ordinal 15), per-hypothesis summary rows:

```
| H1 | causal | REFUTED | necessary timing prediction failed under T1 — most of the drop (week2 pre-deploy 2.66%, vs. week1's 3.12%) was already present before the 06-10T14:00:07Z deploy |
| H2 | descriptive (estimand: within-page conversion rate + mix decomposition) | UNRESOLVED | best supported — T2 CONSISTENT: flat within-page rates, low new-segment rate, counterfactual exclusion restores baseline |
| H3 | causal | REFUTED | necessary directional prediction failed under T3 in both the blended and summer-sale-excluded cuts — desktop declined more than mobile, the opposite of the predicted mechanism |
| H4 | data-artifact | UNRESOLVED | best supported for the coverage anomaly itself (T4 CONSISTENT: normal order volume alongside a mobile session collapse confined to 06-13/06-14, with no equivalent pattern on week1's matching Sunday) — but the supplementary probe shows this anomaly is not material to the topline conversion drop (06-08..06-12 alone already reproduces the same ~2.5% rate and the same ~3.1% recovery when summer-sale is excluded) |
```

Run a's causal `REFUTED` rows are H2 and H3; run b's are H1 and H3 — the four rows the over-caution finding counts, now quoted rather than tallied from memory.

## Verbatim testimony behind the recorded judgments

**s1-baseline caught the mobile undercount and concluded categorically** (final text, the run's only text block):

> There's a smaller, separate data-quality anomaly: on 06-13 and 06-14 (after the v3.4.1 deploy), `orders` counts exceed `checkout_reached` counts (23 vs 17, and 17 vs 11) — impossible if every order requires a checkout session.

> **Bottom line:** The conversion drop is a mix-shift artifact from launching a new `/lp/summer-sale` landing page/campaign on 2026-06-08 […] It is not a product regression, deploy-caused bug, or degradation in existing traffic quality.

Whether that second sentence is an "unhedged conclusion" (the recorded 2/6's basis) is scorer judgment; the sentence itself is now on the record.

**s1-with-skill wrongly marked H4 REFUTED on a schema-only check** (ledger Write, ordinal 13):

```
| T6 | H4 | schema/logging discontinuity at the boundary (nulls, dupes, new categories, format shift) | null/dupe/unique-value audit on both files | CONTRADICTED | 0 nulls, 0 duplicate ids in either file; checkout_reached strictly {yes,no}; device strictly {desktop,mobile}; landing_page gained exactly one new legitimate value (/lp/summer-sale), not a corruption pattern |
```

with the summary line "H4 (data artifact) REFUTED — T6 found a clean schema with no corruption signature."
The recorded failure ("missed the undercount and wrongly marked H4 REFUTED") is visible here: the check audited schema shape, never daily `orders` vs `checkout_reached` counts.

**s1-with-skill-rerun caught the undercount, refuted it on direction, and disclosed its own retrospective status** (final text):

> Anomaly found: on 06-13 and 06-14, orders exceed `checkout_reached` counts by +6 each day (23 vs 17, 17 vs 11). This works in the direction of *overstating* wk2 conversion, not understating it — it cannot be the cause of the drop […]

> (H1–H4 are retrospective: segment/day-level rates were inspected during orientation before this table was formalized, in a single continuous investigation rather than strict two-phase separation. Flagged per skill rules rather than hidden.)

## Reconciliation with the Results tables

- First-wave S1 with-skill tool-call cell corrected 12 → 13 in `tests/scenarios.md`; the other four rows' counts match as recorded.
- The recorded per-run judgments (2/6, 5/6, 6/6) are scorer conclusions; this file grounds their factual substrate (counts, ledger rows, quoted conclusions) but does not re-derive the scores.
- Assertion 1's "before running analysis queries" is not establishable from any of these transcripts' emission order; future runs wanting that assertion machine-checked need mid-run ledger externalization with orientation-only pre-Write probes (s12-rerun is the one qualifying example; s5-with-skill externalized mid-run but its pre-Write probe had already exposed outcome-bearing rows — see the corpus file).
