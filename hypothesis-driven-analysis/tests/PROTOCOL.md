# Measurement Protocol

How a wording change to this skill gets measured, and in what order.
`scenarios.md` says what the scenarios are; this says how to run a change through them without paying for the same measurement twice.

**The Iron Law, stated here and nowhere else:** *measure before wording*, and a measured result belongs to the exact wording it was measured against.
This file is the law's single home — `decisions/001` scopes what a changed file owes in rerun arms, and `scenarios.md` points here rather than restating it.
(Before 2026-08-08 this line read "The Iron Law is unchanged: …", which presented it as a restatement of a canonical text held elsewhere; `decisions/001` pointed at `scenarios.md` for that text, and no such statement was ever there.)
Everything here is about ordering the work so that law costs less to obey.

## Why the order matters

Three documented losses motivate this file, the first two from issue #103 / PR #112 and the third from #113 / PR #115.

The first cost 30 arms.
All four S20 fixture packets rested on a flat p95 — a null result — which the Data section independently gates behind a sensitivity check.
The packets were therefore scored against a rule the change never touched, two of three control arms downgraded on that ground rather than on the planted fault, and every cell had to be rerun after the fixture was fixed.
Nothing about the wording was wrong; the fixture was.

The second cost three review rounds.
Rounds 3, 4, and 5 each changed agent-read prose, each therefore owed arms, and each owed them serially — 15 arms and three push/wait cycles spent largely reconfirming results that had already come back unanimous.

The third cost a whole design phase, and it is the cheapest of the three to avoid.
Issue #113 reported that arms had split on a decision point, and a fix was designed for it — a cross-model consult, an adversarial design review, three drafted rules — before anyone checked whether the split had happened.
It had not: re-extracting the archive showed the cited arm belonged to a superseded round, and the claimed split on a second packet did not exist at all.
The design phase was spent on the wrong question, and the wording it produced was never needed.
Worse, the re-extraction that found this was itself wrong on first run — its pattern matched one heading level and silently missed a third of the arms, which nobody noticed because nobody compared its total against the arm count the wave already stated.

All three are ordering failures, not effort failures.

## The order

0. **Verify the reported failure exists, before designing anything.**
   An issue that says agents diverge is a claim about the archive, and the archive can settle it — usually with one script, and always more cheaply than a design phase.
   Re-derive the counts rather than trusting the issue, the wave notes, or a decision record: #113's premise was wrong in all three at once, each having inherited it from the last.
   **Reconcile the extraction against a total the archive already states.**
   A script that reports 30 arms where the wave says 60 is broken, and that discrepancy is visible in one line; the same rule that forbids trusting a clean result from an unproven instrument applies to your own scripts first.
   If the failure is not there, the finding is that the issue's premise does not hold, and it is worth writing down.
   Everything below is for when it does.

1. **Preregister the fixture and the expected outcomes.**
   Write what each packet contains, which rule it exercises, and what a correct answer looks like — before running anything.
   **Enumerate every verdict the run can reach, including "the change turns out unnecessary."**
   A table written by someone who intends to ship will quietly omit the row where nothing ships, and #113's did: it preregistered shipping on the result it actually got, so the decline that followed was a judgement call with no row behind it.
   At least one row must be reachable *without* the change existing.
   An abort gate keyed on post-edit arms cannot fire when the measurement is what decides whether there is a post-edit batch at all, and a gate that cannot fire is not a check.

2. **Ask which *other* rules the fixture triggers.**
   A probe packet is scored against the whole skill, not the rule under test.
   Go through the standing gates the fixture's incidental properties will reach — null results and the sensitivity check, unidentified causal designs, absent records and completeness semantics, the authorization gate — and neutralize each one in the fixture, usually by preregistering the fact that closes it.
   S20's fix was a preregistered census population and a documented detection limit, which turned the flat p95 from a contested null into settled ground.

3. **Cross-model design review, before any arm runs.**
   Review the fixture, the expected outcomes, and the draft wording together.
   Both external catches on #103 were against the design, and the expensive one was expensive only because it arrived after 30 arms had already run.

4. **Canary: one arm per cell, scored on rationale rather than label.**
   The question is not "did it answer correctly" but "did it answer correctly *for the reason under test*".
   An arm that reaches the right label without ever invoking the rule being measured means the fixture is still entangled — return to step 2.
   Canary arms are fixture validation, not evidence: they are named as such and excluded from the scored artifact, because selecting a fixture on its arms and then scoring that fixture with the same arms is selection, not measurement.

5. **Batch every wording review before the validation arms run.**
   Cross-model review, prose parseability, and the mechanical checks all land against one draft.
   Arms are the last thing to run, not the thing each review round interrupts.

6. **Run the full batch, then archive.**
   Evidence artifact under `runs/artifacts/` with prompt hashes, fixture and skill digests, and tool-call manifests, as `scenarios.md` requires.
   **Quote only from the archived artifact, and grep each quote against it.**
   An arm's final message and the answer file it wrote are different texts; quoting the convenient one produces a citation that does not resolve in the evidence a reader is handed.
   `scripts/check-citations.py` cannot catch this, because it keys on a nearby filename and arm names do not qualify.

7. **Review the commit, not the plan for it.**
   A design review reads what you intended to do; only a review of the diff reads what shipped, and the two diverge most exactly when the measurement changed the conclusion — which is the case the whole protocol exists to produce.
   #113's design review examined a plan to ship wording; the change that shipped contained none, and the defects in it went unread until the diff was reviewed separately.

## What owes a rerun

A change to agent-read prose owes arms for **the cells whose decision point traverses an edited sentence**, and for no others.
Whether a cell reaches the changed text is settled before any arm runs, by reading the fixture and the prose together, and the scoping judgement is recorded in the evidence artifact rather than argued in a review thread.

An edit that cannot reach any decision point owes nothing: whitespace, formatting, a comment, a cross-reference, a heading.
Saying so explicitly is what keeps the obligation credible in the cases where it does bite.

Removing a paraphrase while leaving the authoritative statement untouched is the unsettled case.
It owes one confirmation cell per rule removed — not a batch — and the reasoning goes in the artifact.

Why this rule and not a stricter or looser one: [decisions/001-rerun-obligation.md](../decisions/001-rerun-obligation.md).

## Scope caveat

No step in this ordering has been measured against a counterfactual where it was skipped; every one was adopted on the reasoning above.
Where a step restates an obligation that already binds — preregistration under the Iron Law, archiving under `scenarios.md` — that obligation keeps its own authority; what is unmeasured is the order, not the requirement.
The three losses the ordering responds to are real and documented, but "this ordering is cheaper" remains an expectation, not a measured result.
Step 0 is the one with the clearest arithmetic behind it — #113's design phase was spent before the premise was checked, and checking it cost one script — but a saving computed after the fact from a single case is a plausible story, not a measurement.
Record what it actually costs the next time a semantic change runs through it.
