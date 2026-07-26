# Draft plan: improving `hypothesis-driven-analysis` (Claude's draft — critique this)

## Evidence base

Two independent with-skill runs have now misused the `REFUTED` status in *different* ways:

- **Scenario 1** (`tests/scenarios.md` results table, 2026-07-16): "wrongly marked H4 REFUTED on a schema-only validity check." This earned a targeted patch — the current line "A data-artifact hypothesis is never `REFUTED` on a validity check that did not probe coverage and missingness."
- **This eval** (Assist rollout, `.eval-tmp/`): marked a *causal* hypothesis `REFUTED` on a confounded before/after contrast, while simultaneously concluding the causal effect was unidentified. Self-contradicting, and the skill did not stop it.

One patch per instance is a losing game if the *class* is the problem. The class hypothesis: **the skill polices causal restraint in prose but not in statuses.**

## The structural claim I want you to attack

`Conclusion` contains strong causal restraint, but all of it targets *wording*:

> "Use causal wording only when the design supports a counterfactual... Absent such a design, associative language is mandatory."

The status rules in the same section are design-blind. `REFUTED` requires only "the declared necessary prediction failed under an adequate test" — and "adequate" is never tied to identification. So a faithful reader can:

1. conclude "the effect is unidentified" (obeying the wording rule), and
2. mark the causal hypothesis `REFUTED` on the very data that fails to identify it (obeying the status rule),

in the same ledger. I did exactly this. The skill's own machinery permitted it.

## Candidate fixes, ranked

**F1 — Causal statuses must read the design (high confidence).**
A causal hypothesis cannot be `REFUTED` by outcome data from a design that does not identify its effect: a real effect could be masked by any co-exposure, so the necessary prediction does not follow from the mechanism alone. Split the claim — the descriptive claim ("the records show an improvement") is settled by the records and *is* refutable; the causal claim stays `UNRESOLVED`.

**F2 — Plan and Conclusion contradict each other on artifact hypotheses (high confidence).**
`Plan` says: "Promote a data-artifact hypothesis into the table only when you can state a concrete failure mechanism." `Conclusion` says a `retrospective` hypothesis "clears that bar only on evidence that did not inform it," and "Re-running a fresh statistic over the same records you were already staring at is a new query, not new evidence."

But an artifact hypothesis discovered during orientation is **retrospective at birth** — orientation is what surfaced it. So Plan invites you to register it and Conclusion forbids you from ever resolving it, and nothing in the skill says so. I walked into this: my O3 stated H3's necessary prediction *before* H3 was registered, then "tested" H3 by re-running the same query. Proposed: at Plan, an orientation-discovered artifact hypothesis is registered `retrospective` at birth, with the held-out evidence that could promote it named — or it goes to limitations instead of the table.

**F3 — A reversal is a property of the mix, not the metric (medium).**
`Analysis` says "watch for confounds and aggregation reversals" but gives no procedure. I checked the primary outcome and missed the identical reversal in `handoffs` — in numbers my own test had already printed. Proposed: if composition moved, re-check every reported metric at the stratum grain.

**F4 — Precommitment audit before concluding (medium).**
My stop condition promised a within-stratum censoring-aware contrast; I ran sev1 only and concluded anyway. Nothing in `Conclusion` checks that the precommitted plan actually executed at its declared scope.

**F5 — An absent record is not an absent event (medium-low).**
I wrote "still open" where the export supports only "no recorded closure." The skill has strong coverage/missingness material but nothing on this inference.

**F6 — Estimand naming on the full route (low; may be out of scope).**
I compared a weighted-average-of-stratum-medians against a raw median as though the headline "became" +15%. The `estimation` route demands an estimand; `full` doesn't. **I suspect this violates the "not a methods textbook" Non-Goal — argue me out of it.**

## What I want from you

1. **Defect vs. execution error.** For each of F1–F6: is this genuinely a skill defect, or just me analyzing badly and blaming the tool? Be ruthless. Patching the skill for my mistakes makes it longer and worse. I would rather ship two fixes than six.
2. **Is the structural claim right?** Is "prose is policed, statuses are not" the real defect, or am I pattern-matching one run into a grand theory? If F1/F2 are symptoms of something deeper, name it.
3. **Minimal edit that kills the class, not the instance.** The skill is 222 dense lines and explicitly warns it costs 11–47% more tokens than unstructured analysis. Every line must earn itself. What is the smallest change with the largest coverage?
4. **What regresses?** The eval suite (14 scenarios) currently passes. What could these edits break — especially routing, and especially the risk of making analysts *too* timid to ever conclude anything?
5. **What did I miss?** Is there a failure mode in my ledger/memo that neither of us has named, that the skill should have caught?
6. **Validation.** Scenario 5 ("post-peek hypothesis") is already marked invalid as written. Should the Assist fixture become a permanent scenario? What are its assertions?
