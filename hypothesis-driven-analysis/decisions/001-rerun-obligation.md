# 001 — What a changed agent-read file owes in rerun arms

Decided 2026-07-25.

## Question

The Iron Law says a measured result belongs to the exact wording it was measured against, so a change to agent-read prose invalidates the measurement.
Taken literally, every edit in every review round owes a full rerun.
Taken loosely, "it was only a small change" excuses everything, and the law means nothing.
Which edits actually owe arms?

Left undecided, this was re-argued every round of PR #112: rounds 3, 4, and 5 each renegotiated it, one of them measuring a byte-identical sentence after an indentation fix, and one skipping two cells on a scoping judgement recorded only in passing.

## Positions

*Rerun everything that changed.* Defensible, and what the law says on its face. Cost: 15 arms across rounds 3–5, most of them reconfirming unanimous results, plus a serial push/wait cycle each time.

*Rerun what a reader's behavior could plausibly depend on.* Cheaper, but "plausibly" is exactly the judgement that got re-argued, so it decides nothing on its own.

*Scope the obligation by reachability.* The one adopted, because it is checkable rather than persuasive: whether a cell's decision point traverses an edited sentence is a question about the fixture and the prose, answerable before any arm runs. `tests/PROTOCOL.md` carries the operative form.

## What settled it

The disagreements were never about the principle; they were about who had to justify what.
A rule that asks "which cells reach this text" puts the burden on a question with an answer, and makes the scoping judgement a thing recorded in the artifact rather than a thing argued in a review thread.

The corollary matters as much as the rule: exempting edits that provably cannot reach a decision point is what stops the law from being quietly ignored in the cases where it does bite.
An obligation nobody can afford gets waived silently; one with an honest floor gets kept.

Paraphrase removal is the case that stayed unsettled.
PR #112 measured that transformation once for one rule (c1 came back 6/6 including arms that never opened the reference file), which is evidence about that rule, not a general licence — hence a confirmation cell rather than either extreme, until someone measures it properly.

## Reopening condition

A rerun performed under this rule comes back materially different from the run it replaced, or a cell that this rule exempted turns out to have moved.
Either means "reaches the changed text" is not tracking what actually changes behavior.

## Where the rule lives

`tests/PROTOCOL.md`, step ordering; the Iron Law itself is stated once at `tests/PROTOCOL.md:6`.

*(Corrected 2026-08-08: this line previously pointed at `tests/scenarios.md`, which has never carried a statement of the law — a calibrated grep finds none, and none appears in its history. `tests/PROTOCOL.md:6` was and is the only operative statement, so the pointer named a home that did not exist. PROTOCOL.md is the right home under decisions/004: it is the file that owns how a wording change gets measured. The law is stated there and nowhere else; `scenarios.md:4` points at PROTOCOL.md rather than restating it.)*
