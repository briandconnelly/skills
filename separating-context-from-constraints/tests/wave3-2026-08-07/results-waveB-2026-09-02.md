# Wave B rerun results — eleven with-skill cells run 2026-09-02

This file records the eleven cells rerun against the Wave B `SKILL.md` wording.
It supersedes [`results.md`](results.md) and [`rescore-2026-09-02.md`](rescore-2026-09-02.md) for any arm reading that wording; those files stand as the pre-Wave-B record, and "archived" below always means the 2026-09-01/02 cell as corrected in `rescore-2026-09-02.md`.

Every cell is with-skill ×3 against `SKILL.md` blob `2cb876f4010f55a3259fe740a46d1e8aaea78eea` at commit `a9f0116` (branch `separating-context-wave3`, Wave B wording; not on `main`), with `references/example-audit.md` blob `f825b78fff6df83c0218ac30f7c020a1c142942b`.
Model `claude-fable-5-1`, the session model, inherited by every subagent with no per-agent override; Claude Code 2.1.257, Agent tool, general-purpose subagents; harness-default sampling.
`SKILL.md` was loaded by worktree path, not through a harness.
Scorer: Claude, the session model, 2026-09-02, unblinded; scored under [`preregistration.md`](preregistration.md), section "Rerun classification (added 2026-09-02, Wave B)", which supersedes the per-scenario sections for any arm reading a post-Wave-B `SKILL.md`.
Per-cell artifacts are in [`../runs/`](../runs/), each named `2026-09-02-scenario<N>-with-skill-waveB.md` and each carrying its own provenance block and verbatim outputs.

Batch 1 lost four arms to HTTP 429, an API session limit — scenario 5 rep 3 and scenario 6 reps 1, 2 and 3 — and all four were re-dispatched with identical prompts after the limit reset; no output of a failed dispatch was read or scored.
Batches 2 through 4, 31 arms, at most 12 concurrent, had no failures.
Every arm made one or two tool calls, all on the worktree `SKILL.md` or `references/`, extracted by a session script that lives in the scratchpad outside this repository and is not committed, calibrated against a known positive carrying three disallowed calls, so the negative result is from an instrument shown to fire.
The third Wave B revision, `a9f0116`, was not Codex-reviewed before the reruns; the declared two-call cap on that review budget was already spent.

## Cell summary

| Scenario | Reps | E1 | E2 (strict) | E3 | Other | Preregistered no-change verdict? | Change vs archived |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 (rules buried in prose) | 3 | — | 0, 0, 0 | — | scored assertions 5/5 ×3; secondary R3 on the Test-plan commit scope in reps 1 and 3, on a planted statement, so an observation | **yes** — the R1 embedding regression holds | none; the secondary R3 is the only movement |
| 2 (legitimate inline rules) | 3 | — | 1, 1, 1 | — (no E3 column is scored in this cell; the artifact records alternatives labeled as an author decision in every rep) | assertion 1 passes ×3; the `MUST NOT` R3 finding recurs 3/3 and is recorded as adjudication item A2.1, counted under neither endpoint; assertions 2 and 3 are the ones that exclusion affects | no — the A2.1 finding recurs; the cell is an adjudication, not a pass | E2 6 → 3 over the three reps; the `MUST NOT` unit leaves the count, the `confirmed` rider stays |
| 5 (clean document) | 3 | — | 0, 0, 0 | — | 4/4 ×3; rule 7's "multiple independent user-visible changes" unflagged ×3 | **yes** — the R3 "ordinary domain predicate" clause manufactures nothing here | none |
| 6 (unverifiable hedge and misplaced context) | 3 | — | 0, 0, 0 | — | 6/6 ×3; one consolidated R2 with R3 secondary, migration sentence separately minor R1; all three reps were 429 re-dispatches | **yes** — the R3 author-decision path holds | none |
| 8 (reachable conflict) | 3 | — | 0, 0, 0 | — | 4/4 ×3; R5 conflict reported 3/3, which is scenario 14's known positive | **yes** — R5's reach survives the `:59` deletion | none |
| 10 (long sectioned document) | 3 | 10/10 ×3 over D10.1–D10.10 | 0, 0, 0 | preserved ×3 | standing assertions 11/11 ×3; E7 direction passes ×3; E6 `unique` ×3; E9a `absent` ×3; D10.11 unflagged ×3; rep 1 adds a secondary R4 on D10.3 | **yes** for W6 and W14; E9a `absent` 6/6; W17's row still not reached | finding for finding identical; the denominator moved, since D10.11 is protected rather than planted, so archived 10/11 reads 10/10 |
| 12a (`release-notes-helper`) | 3 | — | 0, 0, 0 | — | 2/2 ×3; no section demand in any rep | **yes** — W9's 12a half closes | the archived `W9-verdict` section demand, 2/3, is now an E2 false positive under the Rerun classification and did not occur |
| 12b (`provision_workspace`) | 3 | — | 2, 1, 3 | — | no R1 finding ×3; 12b-1 passes 3/3, 12b-2 vacuous | partial — the R1 half holds, the R3/R5 findings are an author question | E2 5 → 6; the archived R1 on the rationale clause and the archived R3 on the seat-cap evidence source are gone, replaced by R3 on the duplicate-call sentence and R3/R5 on the seat-count and default sentences |
| 12c (`backfill-runbook`) | 3 | — | 2, 3, 2 | — | R1 minor on step 3 ×3; S3b moved into `## Rules` 3/3; S4a/S4b and B1 unflagged ×3; 1/2 scored assertions ×3 | no — the open author question | E2 9 → 7, but the direction reversed: no archived arm moved S3b and every Wave B arm does, citing the new liftability clause; the archived R4 split of step 4 is gone |
| 13 (R3's scope) | 3 | D13.1 3/3; D13.2 0/1, 1/1, 1/1; E1 over both 1/2, 2/2, 2/2 | 0, 0, 0 | preserved ×3 | B13.1 unflagged ×3; scored assertions 3/3 ×3 | partial — the R3 wording reaches D13.2 in two reps of three | D13.2 moves from observation to planted defect; flagged 3/3 archived when it counted for nothing, 2/3 now that it counts |
| 14 (R5 semantic scope, held out) | 3 | — | 0, 0, 0 | — | 4/4 ×3 clean; known positive is scenario 8's with-skill cell, R5 3/3, cited by artifact path; the ablated arm is not rerun, because the current `SKILL.md` is the ablation | no — the clean/clean row; W4 closes on the deletion, subject to the N6 dispatch deviation below | clean ×3 as archived, now with the guard actually deleted rather than present |
| 15 (ambiguity volume) | 3 | 10/10, 9/10, 10/10 | 1, 1, 1 | preserved 27/27 | nine R2 defects 9/9 ×3 with promoted and demoted rewrites and an author decision, no silent selection; D15.8 an adjudication item excluded from both endpoints; D15.10 flagged R2 with an R1 secondary ×3; E9a `absent` ×3 | partial — the R2 volume half holds; D15.6 and D15.10 are open | E2 unchanged at 3 over the three reps, all on D15.10; D15.6, planted on rerun, is caught in reps 1 and 3 |
| 18 (litmus question 1) | 3 | D18.1 3/3 | 0, 0, 1 | — | classification by function ×3; scored assertions 4/4, 4/4, 3/4; R2 secondary and an author decision in reps 1 and 2 | partial — D18.1 is recalled ×3 but rep 3 breaks the clean sweep | E2 0 → 1: rep 3 raises a minor R2 on Bg3, "Feel free to skim…", where the archived cell was clean ×3 |

## E2 comparison

The eight fixtures with an archived with-skill cell scored under the same registry are 2, 10, 12a, 12b, 12c, 13, 15 and 18; scenarios 16 and 17 were 0 in the archive and were not rerun, so the eight-fixture archived total is also the archived ten-fixture total.
Scenarios 1, 5, 6, 8 and 14 are new Wave B cells with no archived-comparable with-skill E2 cell, and each is 0 ×3; they are excluded from the totals below rather than added as zeros.
Archived strict values are the corrected table in [`rescore-2026-09-02.md`](rescore-2026-09-02.md), "Corrected E2 cell values (strict reading)"; archived per-statement values are the first-scoring cells that file sums to 17 in its section 1.

| Fixture | Wave B strict (rep 1, 2, 3) | Wave B strict total | Archived strict total | Δ strict | Wave B per-statement | Wave B per-statement total | Archived per-statement total | Δ per-statement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 1, 1, 1 | 3 | 6 | −3 | 1, 1, 1 | 3 | 3 | 0 |
| 10 | 0, 0, 0 | 0 | 0 | 0 | 0, 0, 0 | 0 | 0 | 0 |
| 12a | 0, 0, 0 | 0 | 0 | 0 | 0, 0, 0 | 0 | 0 | 0 |
| 12b | 2, 1, 3 | 6 | 5 | +1 | 2, 1, 3 | 6 | 5 | +1 |
| 12c | 2, 3, 2 | 7 | 9 | −2 | 1, 2, 1 | 4 | 6 | −2 |
| 13 | 0, 0, 0 | 0 | 0 | 0 | 0, 0, 0 | 0 | 0 | 0 |
| 15 | 1, 1, 1 | 3 | 3 | 0 | 1, 1, 1 | 3 | 3 | 0 |
| 18 | 0, 0, 1 | 1 | 0 | +1 | 0, 0, 1 | 1 | 0 | +1 |
| **total, 24 reps** | — | **20** | **23** | **−3** | — | **17** | **17** | **0** |

Strict: 3 + 0 + 0 + 6 + 7 + 0 + 3 + 1 = 20 against 6 + 0 + 0 + 5 + 9 + 0 + 3 + 0 = 23, and the per-fixture deltas −3, 0, 0, +1, −2, 0, 0, +1 sum to −3.
Per-statement: 3 + 0 + 0 + 6 + 4 + 0 + 3 + 1 = 17 against 3 + 0 + 0 + 5 + 6 + 0 + 3 + 0 = 17, and the deltas 0, 0, 0, +1, −2, 0, 0, +1 sum to 0.
The two readings disagree on 12c's absolute values — strict 7 against 9, per-statement 4 against 6 — but agree on its delta, because S3b and S3c are the two clauses of one semicolon-joined sentence and every rep alters both.
The strict total falls by three while the per-statement total is flat, and the whole of that difference is scenario 2, whose archived strict 6 counted two units per rep (the `MUST NOT` sentence and the `confirmed` rider) against a per-statement 3.
Scenario 2's fall is a reclassification, not a behaviour change: the `MUST NOT` finding recurs 3/3 and left the count as adjudication item A2.1.

12b's counts are flagged fixture sentences, not clauses.
`rescore-2026-09-02.md` carries no clause inventory for 12b and the archived 12b cell counted the same way, so the rerun follows it; under a full clause inventory rep 3 would count 4, because its alternative (a) rewords the duplicate-call rationale clause, making 12b 7 and the eight-fixture strict total 21 rather than the recorded 20.

## W-item verdicts

- **W9 (R1's compact/long criterion):** half reached, half reversed.
  12a reaches its preregistered no-change verdict — the section demand is 0/3 where the archived cell had it in two reps of three, and every rep cites the new "marked and grouped" clause — so W9's 12a half closes.
  12c does not: every Wave B arm lifts S3b into a `## Rules` section where no archived arm moved it, which the registry's 2026-08-24 amendment still classes as a false positive, so the wording changed the outcome in the direction the registry calls wrong.
  That is author question 1 and is not decided here.
- **W10 (R3's scope):** partial, not reached.
  The Wave B R3 wording makes two previously unscored statements scorable and catches them in two reps of three each — D13.2 in scenario 13 reps 2 and 3, D15.6 in scenario 15 reps 1 and 3.
  In both misses the same arm applied the same wording's "ordinary domain predicate" escape clause to the same kind of phrase, so the reps disagree about the clause rather than about the fixture.
  Scenario 5's regression cell confirms the clause does not manufacture a finding on a genuine domain predicate, 0/3 on rule 7.
- **W4 / issue #160 (the `:59` guard):** not reached as preregistered; W4 closes on the clean/clean row of the arm-reading table.
  Scenario 14 reads clean ×3 with the guard deleted, and the instrument is proved by scenario 8's with-skill cell, which found the R5 conflict 3/3 against the same blob, model and harness.
  The preregistered no-change verdict needs arm 3 to produce the false positive with the guard untouched, and the guard is deleted in this blob, so that row cannot be reached; the observed path is the arm-reading table's clean/clean row, whose verdict is to demote the guard, and the deletion is that demotion carried through.
  The known positive was dispatched in a different batch of the same rerun session; see the process notes, where that deviation is recorded for the author.
- **W17 (report shape):** E9a `absent` 6/6; W17's row still not reached.
  E9a is `absent` in all six with-skill audit arms of scenarios 10 and 15, so the deliverable sentence is operative and the with-skill convention is stable.
  E9c is recorded per arm in every cell artifact.
  The archived partials that kept W17's row from being reached were baseline arms, and the row also requires the controls to score `full-document`; neither a baseline nor an E9 control was rerun in Wave B, so this rerun narrows the item rather than closing it.
- **Regression cells (1, 5, 6, 8):** green.
  All four reach their scenario assertions with E2 0 ×3, so the Wave B wording disturbed neither the R1 embedding test, nor the R3 domain-predicate reading on a clean document, nor the R3 author-decision path, nor R5's reach on a genuine two-rule collision.

## Author questions

These are recorded for the author and are not decided here.

1. **12c, S3b** — is `Never pass --force…` liftable under the new R1, as all three Wave B arms hold, or protected as a step of a `## Procedure`, as the registry's 2026-08-24 amendment holds?
2. **12b** — the new R3 and R5 findings on the seat-count and duplicate-call sentences, both protected by the scenario text and so counted as false positives.
3. **Scenario 15, D15.10** (`Feel free to reassign…`) — flagged in every with-skill rep, archived and rerun, nine of nine, always as a permission inside a rules list.
4. **Scenario 18, Bg3** — rep 3's minor R2 on "Feel free to skim…", against reps 1 and 2 reading the same phrase as permissive rather than hedged.
5. **Scenario 10, D10.11** — the protection held 3/3, but it was the ruling most open to reversal when the Rerun classification was written.

## Process notes

- Dispatch: four batches, at most 12 concurrent arms.
  Batch 1 lost scenario 5 rep 3 and scenario 6 reps 1, 2 and 3 to HTTP 429 and re-dispatched all four with identical prompts after the limit reset; batches 2 through 4, 31 arms, had no failures.
  No output of a failed dispatch was read or scored.
- Scenario 14's known positive is scenario 8's with-skill cell, dispatched at 2026-09-02T20:31:40Z, 20:31:43Z and 20:31:46Z; scenario 14's own reps were dispatched at 20:35:30Z, 20:35:35Z and 20:35:40Z.
  The two are different dispatch batches of the same rerun session, about four minutes apart, against the same `SKILL.md` blob, the same model and the same harness.
  The preregistration's N6 amendment asks literally for the arms to be "dispatched together" and for the known positive to run "in the same batch"; that literal wording was not met, while N6's stated purpose — proving the instrument under the same configuration — was.
  Whether the cell stands on that basis is an author decision.
- Tool calls: every arm made one or two calls, all on the worktree `SKILL.md` or `references/`, extracted by a script that was calibrated against a known positive carrying three disallowed calls, so the clean result comes from an instrument shown to fire.
- Review: the third Wave B revision, `a9f0116`, was not Codex-reviewed before the reruns, because the declared two-call cap on that budget was spent.
  Every number here is single-scorer.
- Scoring units: E2's unit is the clause ("strict"), with a per-statement count reported alongside where the two differ.
  12b is the exception, counted by flagged fixture sentence because no clause inventory exists for it and the archived cell counted the same way; the clause-unit alternative is given in the E2 comparison so either reading can be reproduced.
- Not rerun: no baseline arm, no E9 control arm, and no ablated arm.
  Scenario 14's ablation is not a separate arm, because the current `SKILL.md` is the ablation.
  The archived controls in [`../runs/2026-09-01-scenario10-with-skill.md`](../runs/2026-09-01-scenario10-with-skill.md) and [`../runs/2026-09-01-scenario15-with-skill.md`](../runs/2026-09-01-scenario15-with-skill.md) remain the calibration for E9a's `full-document` branch.
