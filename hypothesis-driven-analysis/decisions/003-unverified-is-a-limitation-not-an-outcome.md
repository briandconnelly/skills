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

*A limitation recorded beside the outcome.* Adopted.
The Outcome cell keeps the worker's own value; the fault travels as a limitation, and reaches the conclusion where it bars treating the result as established or action-ready.

## What settled it

The two rejected options both destroy information, in opposite directions: one discards the worker's finding, the other misdescribes the test.
Keeping the outcome and carrying the doubt separately is the only arrangement where both facts — what the test found, and why you cannot rely on the report of it — survive to the conclusion, which is the only place the distinction changes what anyone does.

That an arm invented `UNVERIFIED` on its own is the useful signal here.
The pull toward a fourth value is real, so the rule has to say explicitly that the doubt is not an outcome, not merely decline to offer one.

## Known gap

This settles the *test outcome*. It does not settle what the affected hypothesis's status should be, and arms split on that question against identical packets.
Tracked as issue #113, deliberately unfixed: the c3 packet in `tests/fixtures/s20-deviation-disposition/` is already the right fixture, and it needs the question asked of it before any wording lands.
Adding an unmeasured rule to SKILL.md is the failure mode #103 exists to punish.

## Reopening condition

Issue #113 measures the hypothesis-status decision point, or a scorer needs the unverified state machine-detectable — which the current arrangement does not provide, since the limitation is prose.

## Where the rule lives

SKILL.md, Analysis section.
Not restated here: see [README.md](README.md).
