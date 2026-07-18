# S12 (causal question phrased as "how much") — transcript evidence

Grounds the S12 rows in `tests/scenarios.md` (Second, Fourth, and Fifth waves).
Run keys, hashes, and instrument validation: `2026-07-17-transcript-evidence-corpus.md`; full per-run manifests: `2026-07-17-transcript-evidence-manifests.md`.

## Scope — three runs, three versions of the skill and of the assertion table

| Run key | Wave | Date (UTC) | Model | Version context | Recorded score |
| --- | --- | --- | --- | --- | --- |
| s12-with-skill | Second | 2026-07-16 | sonnet | pre-revision skill; 4-assertion table (assertion 5 did not yet exist) | 4/4 |
| s12-postfix | Fourth | 2026-07-17T03:44Z (2026-07-16 local) | sonnet | causal-status revision + restored status vocabulary; 5-assertion table | 5/5 |
| s12-rerun | Fifth | 2026-07-17 | unrecorded in transcript; run log says Opus 4.8 | current routing table; 5-assertion table | 5/5 |

These runs must not be aggregated into one scenario verdict: the fifth assertion (H1 stays `UNRESOLVED`) postdates the first run, and — as the evidence below shows — the first run would have failed it.

## Machine-checked counts and facts

| Run | Tool calls | Bash | Read | Write | Edit | Result statuses |
| --- | --- | --- | --- | --- | --- | --- |
| s12-with-skill | 12 | 7 | 3 | 2 | 0 | 11 ok, 1 error |
| s12-postfix | 12 | 9 | 2 | 1 | 0 | 12 ok |
| s12-rerun | 9 | 5 | 2 | 1 | 1 | 9 ok |

All three counts match the recorded cells (12, 12, 9).
s12-with-skill's `error` is its first ledger Write attempt (ordinal 9, rejected by the Write tool's read-before-write precondition: "File has not been read yet"); the Write was repeated successfully at ordinal 12 after a Read of the target at ordinal 11 — an attempt/execution distinction the manifest makes visible.
s12-rerun is the suite's one qualifying machine-checked preregistration ordering: ledger Write at ordinal 6 precedes analysis Bash 7–8 (with the amendment Edit at ordinal 9), and its pre-Write probes stayed on the orientation side — schema heads, marginal distributions, exposure coverage — under the declared rule in the corpus file (s5-with-skill externalized mid-run too, but its pre-Write probe had already exposed outcome-bearing rows).

## The load-bearing status rows, verbatim from the ledger Writes

**s12-with-skill (Second wave, pre-revision skill) marked H1 REFUTED from the unidentified pre/post contrast** (Write ordinal 12):

```
| T1 | H1 | post rate > pre rate | site-wide checkout_reached rate, pre (06-01..06-07) vs post (06-08..06-14) | CONTRADICTED | pre 3.12% (131/4200) vs post 2.51% (125/4971) — post is lower |
```

> Per-hypothesis summary: H1 REFUTED (T1: necessary post>pre prediction failed). […]

This was consistent with the 4-assertion table it was scored against, and the run still refused a causal *estimate* and used associative language (quoted below).
But under the current fifth assertion — added with the causal-status revision — an H1 `REFUTED` from an observational pre/post contrast is exactly the forbidden outcome.
The old skill text permitted the defect the causal-status revision later fixed, and this transcript is direct evidence of it; the recorded 4/4 stands only relative to its own assertion-table version.

**s12-postfix (Fourth wave, revised skill) kept H1 `UNRESOLVED` and refuted the rivals instead** (Write ordinal 12):

```
| H1 | causal | UNRESOLVED | best supported (T1 CONSISTENT, corroborated by device-stratified breakdown under T3) |
| H2 | causal | REFUTED | necessary prediction (a rate step at/after the 06-10 deploy on non-campaign pages) failed under T2 — rate is flat across the deploy |
| H3 | causal | REFUTED | necessary prediction (reweighted device mix accounts for a material share of the change) failed under T3 — reweighting reproduces ~0 of the observed move |
| H4 | data-artifact | UNRESOLVED | best supported for the 06-13/14 coverage gap (T4 CONSISTENT against the independent orders.csv baseline) |
```

These are the rows behind the Fourth-wave findings: the new fifth assertion's pass, the two legitimate causal refutations (H2, H3), and the unprompted `data-artifact` adoption (literal token, claim column).

**s12-rerun (Fifth wave, current table) kept H1 `UNRESOLVED` on the design rule and refuted H4 on an independent necessary prediction** (Edit ordinal 9):

```
| H1 | causal | UNRESOLVED | No identifying design (T1 NON_DISCRIMINATING); causal lift not estimable. The associational contrast shows no lift, but a non-identifying design can neither confirm nor refute the causal effect |
| H4 | causal | REFUTED | Necessary prediction failed (T4 CONTRADICTED): per-device rates near-equal, so the mild mix shift cannot materially confound the contrast |
```

## Verbatim testimony behind the recorded judgments

**Route and refusal, s12-with-skill** (final text):

> The question — "how much did launching /lp/summer-sale improve checkout conversion" — asks "how much" but requests a **causal claim** ("improve"). Per the skill's routing table, a causal claim always selects `full` regardless of phrasing […]

> Landing page is user-selected, not randomly assigned, so even this robust association is associative, not causal.

**False premise caught, s12-with-skill** (final text):

> The data does **not** support the claim. Checkout conversion (`checkout_reached`) fell, not rose, after the launch:

> \- Site-wide: **3.12% pre-launch** (06-01–06-07, 131/4200) → **2.51% post-launch** (06-08–06-14, 125/4971).

**Route and refusal, s12-postfix** (final text):

> Route: **full** — this is the skill's own worked example (a causal question wearing an estimation question's clothes; no random/independent assignment of the exposure, multiple co-occurring live rivals: a concurrent checkout-form deploy, device-mix shift, a logging gap).

> Answer: The campaign did **not** improve checkout conversion — it's associated with a decline. […] This is associative, not causal — landing-page assignment is self-selected, not randomized.

**Route, s12-rerun** (final text):

> **1. ROUTE:** `full`.

> The user asked "how much did launching the campaign improve checkout conversion" — a causal question carrying a number, with no design behind it. […] The skill's routing section names this exact case verbatim: *"How much did launching the campaign improve conversion is ... a causal question carrying a number, with no design behind it,"* […]

## Reconciliation with the Results tables

All three rows' counts match as recorded, and the Fourth/Fifth-wave claims about H1 status, the H2/H3 refutations, `data-artifact` adoption, and the independent H4 refutation are now quoted from ledger Writes rather than tallied from scorer memory.
One finding is new: the Second-wave run's ledger marks H1 `REFUTED` from the unidentified contrast — invisible in the old 4/4 row because no assertion then covered it, and direct transcript evidence that the pre-revision skill permitted the exact defect the causal-status revision closed.
`tests/scenarios.md` now records this alongside the Second-wave row.
