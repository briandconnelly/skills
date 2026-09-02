# Wave 3 results — arms run 2026-09-01 and 2026-09-02

Every cell below was scored under [`preregistration.md`](preregistration.md) as amended through `b2f11be`, against `SKILL.md` blob `3bd60ba2a831479866155a62cbcd80f7280142ea` (identical on `main` at 0527520) and `references/example-audit.md` blob `f825b78fff6df83c0218ac30f7c020a1c142942b`.
Model `claude-fable-5-1`, Claude Code 2.1.257, general-purpose subagents, harness-default sampling.
Scorer: Claude, the session model, unblinded; selection, rule-id, tool-call, digest, and sensitive-string checks were extracted by script from the archived transcripts before hand scoring.
Per-cell artifacts are in [`../runs/`](../runs/), each with its provenance block and verbatim outputs.
No `SKILL.md`, `references/`, or `agents/` wording changed during the wave.

Nine arms died with HTTP 429 (an API session limit) on 2026-09-01 and three more on 2026-09-02; all were re-dispatched with identical prompts after the limit reset, and no output from a failed dispatch was read or scored.

## Cell summary

| Scenario | Arm | Reps | E1 | E2 | E3 | Other | Preregistered no-change verdict? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9R | trigger | 3 (+3 controls, +6 negatives) | selection 3/3; body loading 3/3 with known positive 2/2 | over-selection 0/6, correct-alternative 6/6 | — | — | **yes** — W12 closes |
| 2 | baseline / with-skill | 3 / 3 | — | 3, 3, 5 / 1, 1, 1 | assumption-labelled ×3 / preserved ×3 | with-skill's single FP is R3 on unnamed exception evidence, 3/3 | no (standing assertions 2–3 fail 3/3) |
| 10 | baseline / with-skill (+E9 control) | 3 / 3 (+1) | 10/11 ×3 / 10/11 ×3 (+10/11) | 6, 3, 5 / 0, 0, 0 | mixed / preserved ×3 | E6 unique; E7 in direction but tracks framing; E9a absent ×3, control full-document | **yes** for W6, W14's direction test, W17's absent branch |
| 11 | control / with-skill / baseline (sequential) | 1 each | — / 4/4 / 4/4 | — / 0 / 1 | — | digest changed / unchanged / unchanged; classifier 1 / 0 / 0 | **yes** — W8 closes |
| 12a | baseline / with-skill | 3 / 3 | — | 2, 2, 2 / 0, 0, 0 | — | `W9-verdict` 3/3 / 2/3 | no — W9 reworded (see below) |
| 12b | baseline / with-skill | 3 / 3 | — | 6, 6, 5 / 1, 2, 2 | — | retrieval-pressure R1 ground 3/3 baseline (observation) | partial |
| 12c | baseline / with-skill | 3 / 3 | — | 3, 1, 1 / 2, 2, 2 | — | prohibition moved by 2/3 baselines, 0/3 with-skill | no (registry question, below) |
| 13 | baseline / with-skill | 3 / 3 | D13.1 3/3 / 3/3 | 2, 2, 3 / 0, 0, 0 | assumption-labelled ×2, preserved ×1 / preserved ×3 | D13.2 flagged under R3 on the trigger 3/3 with-skill | **yes** — R3 needs no rewording *on this cell* (see W10) |
| 14 | guard / known positive / ablated | 3 / 3 / 3 | — / R5 3/3 / — | 0 ×3 / — / 0 ×3 | — | — | no — "clean / clean": demote `:59` under W4 |
| 15 | baseline / with-skill (+control, +3 author arms) | 3 / 3 | 9/9 ×3 / 9/9 ×3 | 1 ×3 / 1 ×3 (D15.10 in every arm) | 5 labelled + 4 silent, 9, 9 / preserved 27/27 | author arms 9, 8, 6 of 9 resolved, 0 silent drops of 27; reports 8.1–8.5× | partial — the silent-drop premise does not hold; "all nine resolved" met 1/3 |
| 16 | baseline / with-skill | 3 / 3 | both observation items reported 3/3 / 3/3 | 1, 2, 2 / 0, 0, 0 | — | with-skill ids: D16.1 R5 3/3; D16.2 R5 2/3, R1+R5 1/3 | **yes** — W13 closes as an R5 clarification |
| 17 | baseline / with-skill | 3 / 3 | 2/2 ×3 / 2/2 ×3 | 0 ×3 / 0 ×3 | — | E5 quoted-in-full ×3 / redacted ×3 (script: 0 occurrences) | **yes** — W15 closes |
| 18 | baseline / with-skill | 3 / 3 | 1/1 ×3 / 1/1 ×3 | 4, 3, 4 / 0, 0, 0 | — | classification by grammar ×3 / by function ×3 | **yes** — W16 closes |

Totals across the twelve fixtures with both arms (2, 10, 12a–c, 13, 15, 16, 17, 18): recall is identical or within one planted item between arms everywhere; E2 is 63 for the 30 baseline reps and 13 for the 30 with-skill reps, and 12 of those 13 are the same three sentences (scenario 2's `MUST NOT`, 12c's two, 15's `Feel free`) plus 12b's two W10-class findings; E3 has 4 silent selections in baselines and 0 in with-skill arms; E5 is 0/3 against 3/3 redacted.
This is the 2026-08-06 re-score's picture at held-out scale: detection is not where the skill helps, false-positive discipline and rewrite safety are.

## R3 report obligation (preregistration, "R3's scope")

The E2 counts for **scenario 2** (1, 1, 1) and **scenario 13** (0, 0, 0) were scored on a criterion the arm could not read: R3's shipped sentence says only that a rule is "checkable against some observable evidence", and the result-checkability scoping that protects scenario 2's `MUST NOT` sentence lives in the preregistration.
Of scenario 2's three with-skill false positives, three are R3 findings on unnamed exception evidence and none on an undecidable trigger.
Scenario 13 had no with-skill false positives, but D13.2 was flagged under R3 on the undecidable trigger in all three reps.
Scenario 12b's two with-skill R3 findings (retry condition, seat-cap source) are the same class.

## W-item verdicts from the arms

- **W6 (location):** closes. Every with-skill finding across every fixture resolved uniquely; every arm stated its line convention ("the opening `---` is line 1") rather than assuming one.
- **W8 (audit-only boundary):** closes with no prohibition added; the boundary is observed behavior under a calibrated instrument.
- **W9 (R1's compact/long criterion):** the opposite of the no-change verdict. 12a produced `W9-verdict` in 2/3 with-skill reps and the contrary reading in the third — the shipped sentence yields both outcomes on one input. 12c produced R1 findings on the rationale clause inside step 3 in 3/3 reps (never moving the prohibition). W9 is a wording item; the B1 dependency criterion is the candidate.
- **W10 (R3's scope):** the arms' R3 is already operational determinacy — undecidable triggers (13, 3/3), unnamed exception evidence (2, 3/3), unnamed evidence sources (12b, 2/3) are all flagged under R3, always with the author-decision contract intact. The preregistered criterion, not the wording, is what disagrees with them. The decision is whether to write that reading into R3 and unprotect the fixture sentences, or to add the not-a-finding clause R3 alone lacks (review finding F2) and keep them protected. Either way it is a `SKILL.md` edit that forces arms.
- **W11 (author-decision volume):** the premise does not hold as stated — zero silent drops in 27 author decisions, one of three author arms resolving all nine. What remains is length (8×) and the "name the exception" escalations; no wording change is indicated by this cell.
- **W12 (trigger test):** closes; catalog rebuilt, selection and body loading confirmed, no over-selection.
- **W13 (duplicated rules):** closes as an R5 clarification; no sixth rule.
- **W14 (severity):** the direction test passes, but severity as operated is a distinguishability label — mandatory prohibitions outside the rule section are "minor" in 3/3 reps and the control because their wording is explicit, regardless of consequence. The decision (sharpen, add a level, or drop) is now on real data.
- **W15 (redaction):** closes; `SKILL.md:78` is operative and the gap between arms is 3/3.
- **W16 (litmus question 1):** closes; the litmus test stands.
- **W17 (report shape):** E9a `absent` on every audit arm of 10 and 15, controls `full-document`; E9c consistent across reps within every scenario (guard lines and negative safety notes always present with the skill; classification tables present on most). The observed convention is stable; whether Finding Format should state it is the author's call.
- **W4 / issue #160 (the `:59` guard):** "clean / clean" — demote to a worked example. A `SKILL.md` edit; forces arms.

## Adjudication questions for the author (unanimous arm readings against preregistered protections)

1. **Scenario 2, `MUST NOT archive … without explicit confirmation from the caller`** — flagged under R3 by 4/4 with-skill arms across two dates and criticized by 3/3 baselines. Protected by the R3 criterion. Either the criterion changes (W10) or the sentence stays protected and the cell keeps scoring these as reasoned false positives.
2. **Scenario 10, D10.11 (`update … together`)** — classified as procedure by 7/7 arms. The B1 table plants it on the ground that "together" forecloses updating one file alone.
3. **Scenario 15, D15.10 (`Feel free to reassign…`)** — flagged by 6/6 arms as a permission inside a rules list. Protected as an explicit permission.
4. **Scenario 12c, the rationale clause inside step 3** — R1 finding in 3/3 with-skill reps. Protected on 12c, but the identical shape is planted as D10.6/D10.7 on scenario 10 and recalled there. The registry is inconsistent across fixtures on this shape.

## Author decisions this wave does not make

Whether R3 is widened or bounded (W10); whether `:59` is demoted (W4); whether R1's compact/long sentence adopts the dependency criterion (W9); whether severity is redefined (W14); whether Finding Format names the report components (W17); whether the four protections above stand.
Each is a `SKILL.md` edit that forces arms under the standing rule, and the wave's cells are the pre-edit baseline for those reruns.
