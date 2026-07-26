# 005 — Hypothesis status under an unverified return: measured, and left unwritten

Decided 2026-07-25, closing issue #113.

## Question

`decisions/003` settled where an unverifiable return's doubt is recorded: a limitation beside the outcome, not a fourth outcome value.
It left a gap it named at the time — what status the affected hypothesis takes.

The Conclusion section's status set is closed: `REFUTED` when the necessary prediction "failed under an adequate test", `UNRESOLVED` otherwise.
It does not say whether *verification* is part of adequacy.
So for one faulted return two literal readings both follow: the recorded `CONTRADICTED` outcome means the necessary prediction failed, so H is `REFUTED` while carrying a limitation saying it is not established; or an unverified return cannot be an adequate test, so H stays `UNRESOLVED`.
`REFUTED`-but-not-established is a state the closed vocabulary has no room for.

## What was decided

**The substantive answer is the second reading**, and **no wording was added to say so**, because measurement showed the text already produces it.

## Positions

*Ship a Conclusion rule.* The obvious move, and three separate rationales for it were drafted and killed.

- *"Adequacy has to be shown, not assumed."* This is the modal test `decisions/002` already rejected. A worker's report can always be wrong, so under a modal reading nothing is ever established and no metered return could refute anything.
- *Key the rule on the unverified-return limitation.* The Analysis section describes two different states in near-identical words — a return the free check **cleared** that merely could not be re-run "rests on an unverified worker return", and a return whose execution records conflict is left "resting on an unverified return". Keying a status rule on that wording would have blocked refutation for every unrepeatable metered return, which is the common case in any metered investigation and a far worse regression than the ambiguity being fixed. Found independently by a cross-model review and by inspection, and the reason cells d5 and d7 exist.
- *"A status cell must not encode a verdict whose essential qualifier cannot ride in the cell."* Proves too much. The Outcome cell is also closed-vocabulary and machine-read, and `decisions/003` deliberately keeps `CONTRADICTED` there with the qualifier in prose beside it. Applied consistently this reopens 003.

*Measure first, and let the result decide.* Adopted, per the repo's Iron Law and the S19 precedent.

## What settled it

Scenario 21 — a decision-point probe that hands an arm the reconciled ledger the skill itself prescribes and asks only what status follows.
Eighteen scored Sonnet arms against the **unedited** skill, n=3 on every cell, plus six canary arms that are fixture validation rather than evidence (`tests/PROTOCOL.md` step 4).

All eighteen scored arms answered correctly, and so did all six canaries.

- The two test cells — an execution-record conflict under `CONTRADICTED` (d3) and under `CONSISTENT` (d6) — came back `UNRESOLVED`, and d6 additionally declined "best supported", 3/3 each.
- The two regression controls — a cleared-but-unrepeatable return under each outcome (d5, d7) — held `REFUTED` and held "best supported", 3/3 each.
- The remaining controls held too: a disclosed immaterial deviation (d4) stayed `REFUTED` and a `NON_DISCRIMINATING` outcome (d1) stayed `UNRESOLVED`, 3/3 each.

The rationales are what settled it rather than the labels.
Arms did not stumble onto the right answers; they reconstructed the rule that was about to be written, from the text as it stands, and drew the two-limitation distinction unprompted.
Quoting the archived answers: scored `d3-conflict-1` held that a test whose record cannot be trusted "cannot be the adequate test that clears that bar, so the CONTRADICTED outcome cannot carry H2 to REFUTED" — the disputed inference, drawn correctly.
Scored `d7-support-clean-3` supplied the scope guard the draft rule needed, calling the unrepeatable return the "milder case the skill names" rather than "the harsher conflicting-execution-records case".

`tests/PROTOCOL.md`'s ordering, and the S19 precedent — "If all three arms pass 1–5, the current text already induces correct handling and item 4 needs no wording change" — both point the same way.
S19's item 4 was declined on weaker evidence than this.

## Why the ambiguity is nonetheless real

The two readings are both available to a careful reader, and one archived arm took the wrong one: `round1-preC3-2` in the Fifteenth wave derived `REFUTED` and wrote the unverified-return limitation beside it — the unrepresentable state itself, reached by "mechanically deriving H2's status from that CONTRADICTED outcome".
That is one occurrence in fifteen archived c3 arms and zero of six in that wave's authoritative round.

So the honest description is: a textual ambiguity that is real on the page and was not observed in behaviour at this n, on one model against one fixture family.
Not the same as absent — at a one-in-fifteen rate, eighteen arms miss the mode entirely about 29% of the time, and the preregistration renounced the absence claim in advance.
What the result does establish is that the inference is not fragile enough to show up readily, and adding prose that changes no measured behaviour has a cost — one more sentence to keep consistent, and `decisions/004` exists because duplicated normative statements diverge silently.

## What this decision is not

It is not a preregistered outcome. Scenario 21's table expected to ship the wording on exactly this result, and the decline was decided after the arms returned, on the S19 analogy and the cost argument above.
The abort gate the table carried was keyed on post-edit controls, so with no edit it never ran.
Recording that plainly is the point: this record would be worth little if it presented a judgement call as a rule firing.

## Where the rule lives

SKILL.md, in the sentences the arms themselves quoted: the Analysis section's disposition of a return whose execution records conflict, and the Conclusion section's closed status set.
Nothing was added, because the reading follows from those two and agents draw it.

An earlier draft of this record claimed there was "no owning file to point at". That was wrong, and it inverted the finding: the whole result is that the existing text *does* produce the reading, so the existing text owns it and this file points at it like any other.

## Known gaps

- **A return whose execution records are absent or unquotable** — the Evidence field summarized, the commands omitted — is neither "records that conflict" nor "cleared by the free check", because the free check could not run. Neither the text nor this measurement covers it. Adjacent to S19's no-return case, and distinct from it.
- **Machine-detectability is unchanged.** The limitation is still prose, so no scorer can tell a `REFUTED` row resting on a conflicted return from one resting on a clean one. `decisions/003`'s reopening condition on this point stands, and `references/ledger-template.md`'s `adequacy:` atom is the precedent if it is ever built.
- n=18, one model (Sonnet), one fixture family; the probe hands the arm a correct reconciliation, so it measures the status inference alone and never whether an agent reconciles correctly first — S20 measures that.

## Reopening condition

An arm reaches the disposition Scenario 21's d3 or d6 cell scores as a miss, under any wording of the Analysis or Conclusion sections — which is the signal that the inference stopped being reliable and has to be written down after all.
Scenario 21's eighteen scored cells are the intended standing check, but nothing currently reruns them: the prek hook validates only the fixture text, so an edit to either section will not trigger them by itself. Treat it as a check someone has to remember, not one the repo enforces.
