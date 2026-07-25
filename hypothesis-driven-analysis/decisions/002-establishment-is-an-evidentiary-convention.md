# 002 — Establishment is an evidentiary convention, not a modal test

Decided 2026-07-25, during issue #103 / PR #112.

## Question

When a worker's return is faulted, the main agent has to decide whether a deviation from the brief is *established* — real enough to act on — or merely reported.
What makes it established?

## Positions

*Modal test.* The first draft: a deviation is established when every reading consistent with the return contains one.
It reads rigorous and it is worthless.
A worker's report can always be wrong, so for any return there exists a consistent reading in which the reported deviation never happened, and nothing is ever established.
The test does not discriminate hard cases from easy ones; it fails all of them.

*Evidentiary convention.* Adopted: rank the kinds of evidence a return carries, and let the disposition follow the higher-ranked kind when they disagree.
Which kind outranks which, and what follows from their agreement or conflict, is SKILL.md's Analysis section.
The reason for the ranking is what belongs here: a worker's narrative fields are its *description* of what ran, while the quoted commands and tool-emitted output are the account of it, and a description is the thing that can be wrong without anything else changing.

## What settled it

The modal framing was killed by a cross-model review before any arm ran, which is the cheapest catch in the PR and the reason step 3 of `tests/PROTOCOL.md` exists.

The general lesson is the part worth keeping: a discriminator that quantifies over *possible readings* of evidence will collapse whenever the evidence is fallible, which is always.
A discriminator that ranks *kinds* of evidence stays decidable, because ranking is a convention the reader can apply rather than a fact about the world they would have to establish first.

This also fixes what the rule is honest about.
A convention does not claim the deviation certainly happened; it says which evidence the disposition follows when sources disagree, which is all a main agent reading a return can actually settle.

## Reopening condition

A return shape where command-and-output agreement is systematically forgeable or systematically absent — a tool that does not echo its parameters, a harness that reconstructs output — would make the ranking track something other than what ran.

## Where the rule lives

SKILL.md, Analysis section.
Not restated here: see [README.md](README.md).
