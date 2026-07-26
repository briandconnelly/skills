# 003 — An unverifiable return is a limitation, not a fourth outcome

Decided 2026-07-25, during issue #103 / PR #112.

## Question

When a return's own execution records conflict with each other — a quoted output with no source among the commands shown, a command and the output beneath it naming different days — nothing about it can be established and nothing verified.
Where does that fact get recorded?

## Positions

*A new outcome value.* Natural, and one arm invented exactly this, writing `UNVERIFIED` into the Outcome cell unprompted.
It breaks the closed outcome set, which is the property the ledger's machine checks depend on, and it overwrites information: the worker's own outcome is still the best available account of what its test found, and replacing it discards that.

*Reuse `NON_DISCRIMINATING`.* Wrong for a different reason.
That value says a test could not discriminate.
A return that is unverifiable may have discriminated perfectly well — the doubt is about the report, not the test — and collapsing the two makes the ledger say something false about the evidence.

*A limitation recorded beside the outcome.* Adopted; SKILL.md's Analysis section carries what that means in practice.
The property it buys is the one the other two options destroy — what the test found and why the report of it cannot be relied on stay separable, all the way to the conclusion.

## What settled it

The two rejected options both destroy information, in opposite directions: one discards the worker's finding, the other misdescribes the test.
Keeping the outcome and carrying the doubt separately is the only arrangement where both facts — what the test found, and why you cannot rely on the report of it — survive to the conclusion, which is the only place the distinction changes what anyone does.

That an arm invented `UNVERIFIED` on its own is the useful signal here.
The pull toward a fourth value is real, so the rule has to say explicitly that the doubt is not an outcome, not merely decline to offer one.

## Known gap

This settles the *test outcome*. It did not settle what the affected hypothesis's status should be.

Closed by [005](005-status-under-an-unverified-return.md): Scenario 21 asked that question of a purpose-built decision-point fixture, and the existing text turned out to produce the intended status without a new rule.
The claim recorded here in the first draft — that arms split on the question against identical packets — overstated the archive, and issue #113 inherited the error. One arm of fifteen derived the other status, in the Fifteenth wave's superseded round.

## Reopening condition

A scorer needs the unverified state machine-detectable, which the current arrangement does not provide, since the limitation is prose.

## Where the rule lives

SKILL.md, Analysis section.
Not restated here: see [README.md](README.md).
