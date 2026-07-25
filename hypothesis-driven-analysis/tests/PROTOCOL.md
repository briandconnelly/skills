# Measurement Protocol

How a wording change to this skill gets measured, and in what order.
`scenarios.md` says what the scenarios are; this says how to run a change through them without paying for the same measurement twice.

The Iron Law is unchanged: **measure before wording**, and a measured result belongs to the exact wording it was measured against.
Everything here is about ordering the work so that law costs less to obey.

## Why the order matters

Two documented losses motivate this file, both from issue #103 / PR #112.

The first cost 30 arms.
All four S20 fixture packets rested on a flat p95 — a null result — which the Data section independently gates behind a sensitivity check.
The packets were therefore scored against a rule the change never touched, two of three control arms downgraded on that ground rather than on the planted fault, and every cell had to be rerun after the fixture was fixed.
Nothing about the wording was wrong; the fixture was.

The second cost three review rounds.
Rounds 3, 4, and 5 each changed agent-read prose, each therefore owed arms, and each owed them serially — 15 arms and three push/wait cycles spent largely reconfirming results that had already come back unanimous.

Both are ordering failures, not effort failures.

## The order

1. **Preregister the fixture and the expected outcomes.**
   Write what each packet contains, which rule it exercises, and what a correct answer looks like — before running anything.

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

## What owes a rerun

Decided once, in [decisions/001-rerun-obligation.md](../decisions/001-rerun-obligation.md), rather than re-argued each round.

## Scope caveat

Steps 4 and 5 are procedure, adopted on the reasoning above; neither has itself been measured against a counterfactual where it was skipped.
The two losses they respond to are real and documented, but "this ordering is cheaper" remains an expectation, not a measured result.
Record what it actually costs the next time a semantic change runs through it.
