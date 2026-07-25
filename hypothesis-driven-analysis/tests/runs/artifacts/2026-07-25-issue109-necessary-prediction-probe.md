# Issue #109 Defect 1 — decision-point probe: does a test row that misses its necessary prediction produce a false `REFUTED`?

**Date:** 2026-07-25.
**Model:** Sonnet, all nine arms.
**Verdict: the defect did not reproduce. 9/9 arms answered correctly.**
The review's claimed consequence — a false `REFUTED` propagating from the worked example's row structure — is **not supported** at this measurement, and issue #109's `priority: high` was not earned.

**Scope:** this probe ran against `references/ledger-template.md` as it stood *before* the #109 fix (PR #111), when T1 conjoined a stronger-than-necessary timing condition with a cache-hit-rate condition.
Quotations of T1 below are of that pre-fix row and no longer match the current template, which now points T1 at H1's necessary prediction alone and carries the discarded conjunct as T1b.
That is the change this measurement informed, so the pre-fix text is the object under test, not a stale copy.

## What was measured

Issue #109 Defect 1 observes that in `references/ledger-template.md`, H1's declared necessary prediction is

> the p95 step must not precede the deploy — a deploy cannot cause a step that happened before it

while T1 — the test the Hypotheses table names as H1's — preregisters something else:

> p95 step within 10 min of deploy; hit rate drops ≥5pp

Neither conjunct is the necessary prediction: the first is strictly stronger, the second is a "would be nice" prediction that `SKILL.md:224` says cannot refute.
The review predicted that an agent copying this structure and deriving status per `SKILL.md:221-222` would mark H1 `REFUTED` on a test whose failure the skill says cannot refute it.

## Design

A neutral focused decision-point probe, per the repo's established technique for wording-governed failures.
Arms were asked to "write the Conclusion's per-hypothesis summary table" — **not** to check adequacy or verify necessary predictions.
A leading probe would prompt the very step whose absence is the alleged bug; that trap produced a false 0/5 on issue #72.

Two fixtures, identical except two timestamp lines (diff verified, digests below):

- **Arm A (defect probe):** step at 15:10, deploy at 14:30 — the step follows by 40 minutes, so H1's necessary prediction **holds**.
  T1's stated prediction fails, so the row legitimately reads `CONTRADICTED`.
  Correct answer: `UNRESOLVED`.
- **Arm B (over-correction control / known positive):** step at 09:12 — precedes the deploy, so the necessary prediction genuinely **fails**.
  Correct answer: `REFUTED`.

Arm B exists to establish the instrument can surface a positive.
A probe that cannot distinguish the two answers is non-discriminating, and arm A's result would mean nothing.

Two isolation conditions for arm A:

- **A1–A3:** `SKILL.md` + the ledger only.
  `references/` excluded so the worked example's own published `H1 | causal | REFUTED` verdict could not act as an answer key.
  This measures the status-derivation rule operating on the trap row.
- **A4–A6:** `SKILL.md` + `references/ledger-template.md` + the ledger.
  This adds the anchoring path — the example's published `REFUTED` conclusion in context — which is the propagation mechanism the issue actually claims.

All arms read-only, forbidden from `tests/` and from git.

## Results

| Arm | Condition | Inputs | H1 status | Correct |
| --- | --- | --- | --- | --- |
| A1 | necessary prediction holds | SKILL.md only | `UNRESOLVED` | yes |
| A2 | necessary prediction holds | SKILL.md only | `UNRESOLVED` | yes |
| A3 | necessary prediction holds | SKILL.md only | `UNRESOLVED` | yes |
| A4 | necessary prediction holds | + ledger-template.md | `UNRESOLVED` | yes |
| A5 | necessary prediction holds | + ledger-template.md | `UNRESOLVED` | yes |
| A6 | necessary prediction holds | + ledger-template.md | `UNRESOLVED` | yes |
| B1 | necessary prediction fails | SKILL.md only | `REFUTED` | yes |
| B2 | necessary prediction fails | SKILL.md only | `REFUTED` | yes |
| B3 | necessary prediction fails | SKILL.md only | `REFUTED` | yes |

**A: 6/6 correct.
B: 3/3 correct.
Instrument validated by B.**

## The arms diagnosed the trap rather than avoiding it by luck

This is the load-bearing part of the negative result.
Verbatim from the arm outputs:

- **A3:** "T1 (CONTRADICTED) tested T1's own stricter preregistered prediction (10-min alignment + ≥5pp hit-rate drop), not H1's declared necessary prediction ('step must not precede the deploy'). The step (15:10) followed the deploy (14:30), so the necessary prediction was not falsified; a CONTRADICTED outcome on a non-necessary prediction never refutes."
- **A2:** "T1's `CONTRADICTED` outcome was scored against H1's *Prediction if true* (10-min alignment + ≥5pp hit-rate drop), not its declared necessary prediction."
- **A6:** "T1's `CONTRADICTED` outcome applied only to the test's own tighter preregistered prediction [...] a non-necessary prediction; per SKILL.md, a `CONTRADICTED` outcome on a non-necessary prediction never refutes."
- **A1:** "T1's CONTRADICTED outcome reflects only the stricter, non-necessary conjunction [...] which per the skill cannot refute the hypothesis however cleanly it fails."

Every A arm independently identified the exact mismatch the issue describes and applied `SKILL.md:224`/`:241` correctly.
The template-inclusive arms (A4–A6) were not anchored by the worked example's published `REFUTED`.

## What survives, and what is retracted

**Retracted:** the claim that the example's row structure yields a false `REFUTED`.
Not observed in 6/6 arms across both isolation conditions.

**Survives:** the example is still factually wrong — T1 does not test the prediction the Hypotheses table designates as H1's refuting one.
A calibration artifact that models a rule incorrectly should be corrected on its own terms, and the fix (split T1's conjuncts, point T1 at the necessary prediction) remains right.
But it is a correctness-of-example fix, not a false-refutation defence.

**Consequence for #109:** Defect 1's severity paragraph must be rewritten to say measured-and-not-reproduced.
`priority: high` is downgraded.
Defects 2 (T3 filed under H2, H3 absent) and 3 (no stop rule on the cheap-route templates) are unaffected — neither was measured here.

## Honest limits

- n=3 per condition, one model (Sonnet), one fixture shape.
- The fixture is a hand-built ledger, not a live full-route run.
  It hands arms a completed Tests table; it does not measure whether an agent *building* a table from the example would write the same mismatched row in the first place.
  That is the untested half of the propagation claim, and it needs a live run to settle.
- A negative result on a capable model is weaker evidence than a positive one: it shows the trap is survivable, not that no configuration falls into it.
- Arms were told all tests were complete, which removes the option of running a further test to resolve H1 — a live run might instead iterate rather than assign a status.

## Digests

Fixtures and arm outputs, `shasum -a 256`, generated programmatically:

```
6b87b64f6a8c87b26535c1f8f25c639567bb82f1ee94d472dd4f1ea348420ded  ledger-arm-A.md
5d39c9fd24ed618d1318d43ef3d2ceba772cba7bfd9d684eb7b720fd5eee26a6  ledger-arm-B.md
0392a0b031a763c24b936fa5358fabdf954583114d4d33929a03d8c2ff6ab537  out-A1.md
3daa8be6b3f9fb7662a8c7cf28ac956dfcdc96c1c8d78afa5cf8db7a1d777af3  out-A2.md
79e7a8b59f51d7b95db8b1848511ecddbe414ad39d43dd4ecbec0eb278dad138  out-A3.md
6525ff651f76d1685234ba0c030fbb3e84e8b6a453729f8dd0c2a29befa59686  out-B1.md
ec333527a1017b5e62a769e0e292cb1fde6907b34d66e5cb731a5ea595a7fbf3  out-B2.md
9559432ebe3fde11377f646d29ac04d6d3d97ebb566034f7ca5a92127b51bc4d  out-B3.md
2cf4f4b96e44c0afe9bf1a266750f920620527d480e4c08f3a56ef11fc28430d  out-A4.md
335db397dadc7a84f9e062d766478afe5e373e58a586ca07f445c8136381b55c  out-A5.md
20b18b4b03f72e423fcc2feacf3d3115e24ae29fa91a7bfc4d5e49e4368786a0  out-A6.md
```

Raw arm outputs and fixtures are retained in the session scratchpad; the digests above pin their content.

🤖 Generated with Claude Code
