# Confirmation cells: removing status-rule paraphrases from `ledger-template.md`

Date: 2026-07-25.
Scope: the reconciliation described in [decisions/004](../../../decisions/004-single-authority-for-normative-rules.md), which deleted three restatements of SKILL.md status rules from `references/ledger-template.md`.

## What this is, and what it is not

This is the confirmation cell [decisions/001](../../../decisions/001-rerun-obligation.md) requires for an edit that removes a paraphrase while leaving the authoritative statement untouched — one cell per removed rule, not a batch.

**It is not a before/after measurement.** Only the post-edit state was run.
The question it answers is narrow: with the template's paraphrase gone, does the rule still reach an agent through SKILL.md alone?
It cannot tell you whether the paraphrase was doing anything useful before, and no arm was run against the old wording.

n = 1 per rule. Two rules, two arms.

## Digests

| Artifact | SHA-256 |
| --- | --- |
| `SKILL.md` (unchanged by this work) | `da9cefbcff3d7783f86c8480e3ce476974d5a1649ebd5edf8b9039801550fdef` |
| `references/ledger-template.md` before | `e630b7b5f9760a0dc17e96b0ee5c26cada168bce45a19ae37fa72321ae8960d3` |
| `references/ledger-template.md` after | `97f84c6f27b3c872bbf1a6d1108c6b62676032b3b415c6c06846d4f1ae16c1a8` |
| arm output, causal cell | `60343576b78e77a46c4686b29392a7564bd954e72275667c35b58ae051416dfa` |
| arm output, data-artifact cell | `777d62a1ce682bb1c422d84289fb52fd434d9f209bcc90fa9cd6cd5642699736` |

## Method

Each arm was a fresh subagent (Sonnet) given only: a two-row ledger excerpt with a preregistered necessary prediction and a worker-returned `CONTRADICTED` outcome, and the instruction to state the hypothesis status the skill dictates and quote the sentences it relied on.
Arms were pointed at `SKILL.md` and `references/`, and forbidden from reading anything under `tests/` — the assertions and prior runs would contaminate the result.
Each arm wrote to a unique output path.
Neither prompt named the removed template lines, the expected status, or that anything had been edited.

The two cells correspond to the two removed rules that SKILL.md still owns.
The third removed clause — that a `descriptive` row cannot be added after Plan time — was not measured, because it was deleted as *wrong* rather than as duplicated: it contradicted SKILL.md and the same template two lines below.

## Results

**Causal cell** — non-identifying contrast (self-selected beta opt-in) returning `CONTRADICTED` on the necessary prediction.
Answer: `UNRESOLVED`.
The arm reached it by quoting SKILL.md's Conclusion section directly: "An exposure–outcome contrast from a design that does not identify the causal contrast cannot by itself mark that causal hypothesis `REFUTED`: that test leaves it `UNRESOLVED`, because a co-exposure pushing the other way could mask a real effect."
It also checked the escape hatch — independent evidence not relying on the unidentified contrast — and correctly found it unavailable, since T1 was the only test on record.

**Data-artifact cell** — a field-validity sweep, probing no coverage or missingness, returning `CONTRADICTED`.
Answer: `UNRESOLVED`.
The arm quoted SKILL.md's Conclusion section: "A data-artifact hypothesis is never `REFUTED` on a validity check that did not probe coverage and missingness."
It reached the same place by a second, independent route — the Analysis section's established-deviation rule, since the Method column is itself a coherent execution record of a procedure the brief did not authorize — and reconciled T3 to `NON_DISCRIMINATING` before deriving status.

Both arms cited SKILL.md, not the template, for the governing rule.
Neither arm's reasoning depended on a template sentence that this change removed.

## Reading these results

They support the narrow claim that the two removed paraphrases were not load-bearing: the rules reached both arms through the file agents always read.
They do not establish that no paraphrase removal is ever load-bearing, and decision 001 does not license treating them that way.

One arm cited the template's *worked example* (the H5 data-artifact row and its T6 independent-counter comparator) as a model for what the correct test would have been.
That is the template doing what it is for — showing how a ledger records a rule — and is untouched by this change.
