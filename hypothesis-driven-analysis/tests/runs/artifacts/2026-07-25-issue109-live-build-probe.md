# Issue #109 Defect 1, part 2 — live-build probe: do agents *write* the mismatched row?

**Date:** 2026-07-25.
**Model:** Sonnet, three arms.
**Fixture:** Scenario 1 (`s1-conversion`), live full-route investigation.
**Verdict: the registered decision rule ties — 6/12 hypothesis rows `CONJOINED`, 6/12 `MATCH`.
Neither branch fired.
But all 4 refutations across all 3 arms landed on `MATCH` rows.**

**Scope:** the arms read `references/ledger-template.md` as it stood *before* the #109 fix (PR #111) — that pre-fix worked example is the exposure under test.
References below to "the worked example's T1 pattern" mean that pre-fix row, which conjoined two conditions in one prediction cell; the current template no longer has it.

## Why this ran

The companion probe (`2026-07-25-issue109-necessary-prediction-probe.md`) measured status *derivation* from a handed-over ledger containing the mismatched row: 9/9 arms correct, defect did not reproduce.
That left the other half of the propagation claim untested — whether an agent *building* a ledger from the worked example writes a Tests row whose preregistered prediction is not the hypothesis's declared necessary prediction.

Arms ran a real investigation with `SKILL.md` and `references/` in scope (the worked example is the exposure under test) and all of `tests/` except the fixture directory out of scope.

## Scoring criterion

Registered in `SCORING-PLAN.md` **before** the arms ran, digest below.
Each hypothesis row is classified by comparing its `Necessary prediction (failure refutes)` cell against the `Preregistered prediction` cell of every bound Tests row:

- **MATCH** — a bound test states the necessary prediction alone: no additional conjuncts, not strictly stronger.
- **CONJOINED** — the bound test also states additional conditions in the same cell, so a failure cannot be attributed to the necessary conjunct.
  This is the worked example's T1 pattern.
- **SUBSTITUTED** — no bound test states it; the nearest states something different or stronger.
- **ABSENT** — no necessary prediction declared, or no test bound.

Registered decision rule: majority `CONJOINED`/`SUBSTITUTED` → Defect 1 regains weight as structural hygiene and the fix lands with a row-granularity rule sentence.
Majority `MATCH` → the example is inert, Defect 1 is cosmetic, drop to `priority: low` and add no rule sentence.

## Results

| Arm | Row | Class | Extra conjunct beyond the necessary cell |
| --- | --- | --- | --- |
| L1 | H1 | MATCH | — (T1 restates it with method detail only) |
| L1 | H2 | MATCH | — (the necessary cell itself carries both the "must not precede" claim and its 6/8–6/9 specification) |
| L1 | H3 | CONJOINED | "device-mix-adjusted counterfactual comparable to T1's" |
| L1 | H4 | CONJOINED | "matching exactly elsewhere" |
| L2 | H1 | CONJOINED | "rate drops at/after 06-10 14:00" |
| L2 | H2 | CONJOINED | "recomputing via orders/sessions narrows the gap materially" |
| L2 | H3 | CONJOINED | "reweighting closes most of the gap" |
| L2 | H4 | MATCH | — |
| L3 | H1 | MATCH | — |
| L3 | H2 | CONJOINED | "`/lp/summer-sale` rate much lower; reweight recovers the gap" |
| L3 | H3 | MATCH | — |
| L3 | H4 | MATCH | — |

**Totals: 6 CONJOINED, 6 MATCH, 0 SUBSTITUTED, 0 ABSENT.**
Per arm: L1 2/4, L2 3/4, L3 1/4 conjoined.
Every arm produced at least one conjoined row; no arm produced only conjoined rows.

The registered rule required a *majority* for either branch.
6/12 is not a majority.
**Neither branch fired, and this is recorded as an unresolved rule rather than resolved by reinterpreting the threshold after seeing the data.**

## The secondary observation carried the signal

Registered in advance as: "whether any arm marks a hypothesis `REFUTED` on a test whose failure does not fail that hypothesis's necessary prediction."

Four `REFUTED` rows were produced across the three arms:

| Arm | Row | Class of that row |
| --- | --- | --- |
| L1 | H2 (retrospective) — the deploy | MATCH |
| L2 | H4 — device mix | MATCH |
| L3 | H3 — device mix | MATCH |
| L3 | H4 — the deploy | MATCH |

**4/4 refutations rest on cleanly-stated necessary predictions.
0/6 conjoined rows produced a refutation.**
The conjoined rows all ended `CONSISTENT` or `NON_DISCRIMINATING`.

The pattern across both probes is consistent: agents conjoin freely on rows doing confirmatory or exploratory work, and state the necessary prediction cleanly on rows doing refutation work.
That is why probe 109a found no false `REFUTED` — the harm mechanism requires a refutation resting on a conjoined row, and in 12 rows across 3 live investigations that combination did not occur.

## Disposition proposed

- The worked example's T1 row is still factually wrong and should be corrected: point T1 at H1's necessary prediction, move the discarded conjuncts to a separate supporting row.
- **Do not add the row-granularity rule sentence yet.** Its registered trigger was a `CONJOINED` majority, which did not occur; conjunction at 50% with zero measured harm does not justify adding a sentence to a document already flagged as over-long.
  If a future wave finds a refutation resting on a conjoined row, that sentence is the ready fix and this artifact is its baseline.
- `priority: medium` stands — not `low`, because conjunction is common enough that the calibration artifact is modelling a sloppy shape; not `high`, because neither probe found the harm.

## Unplanned observation, recorded for a separate issue

L1 self-reported an orientation breach: it computed per-page and per-device conversion rates before writing the ledger, recognised that as crossing `SKILL.md:134`'s cause-outcome line, labelled H1/H2/H3 `retrospective`, and declined to certify the landing-page explanation as best supported on the evidence that produced it.
The rule is followable and was followed honestly under self-report — and a live investigation slid across the line anyway.
Relevant to the orientation-boundary item in the 2026-07-25 review (no worked contrasting example exists for that line).

## Honest limits

- n=3, one model (Sonnet), one fixture.
- S1's deploy hypothesis is refuted on flagrant timing, so a clean necessary prediction is easy to state there.
  A `MATCH` on that row is weaker evidence than a `CONJOINED` would have been, and the refutation-alignment finding inherits that weakness: it may reflect that S1's refutable hypotheses happen to have simple predictions, not that agents reserve clean statements for refutation work.
- Classification is a scorer reading of the two cells, not a machine check.
  The extra-conjunct column above quotes the deciding text so the reading can be re-checked.
- The arms' correctness on the underlying question is not scored here; this probe measures row structure only.

## Digests

`shasum -a 256`, generated programmatically:

```
c1d3a08ca31ee681725a3d7e79e74a7830ac623737a6dfeb3245b68b1f07e98c  SCORING-PLAN.md
9815b23014808d125256389374f7c6b84e72d2deb3930a3ed27f21358f9fa446  L1/ledger.md
14334897815621e940ac7176f7490eb6dbf03cba49d1fd7276dafdf4eb5c0efa  L2/ledger.md
6d11c2c0f0a0020884fc9eed7ecb5dddf7bc7c9ab1fda6fce9d74bfa9bb3bfbb  L3/ledger.md
```

🤖 Generated with Claude Code
