# 006 — Why the agent is not told to run the scorer on its own ledger

Decided 2026-08-08.

## Question

An audit found that live agents are never told the instruments exist: no agent-read prose mentions `score_ledger.py` or `check_prereg.py`, so every machine check runs at scoring time, against runs already finished.
Enforcement on a live investigation is therefore prose alone.

The audit's proposed remedy was to have SKILL.md direct the agent to run `score_ledger.py` against its own ledger before concluding.
That would add live enforcement and, the argument went, relieve the pressure to keep strengthening prose that keeps failing — the repo's own lesson from issue #77 → C3 being that a repeatedly-failing prose rule belongs in an instrument.

## Positions

*Point the agent at `score_ledger.py`.* Attractive: the skill ships as a directory, so `tests/` travels with it; the checks already exist; and it converts scoring-time discipline into live discipline for free.

*Point the agent at nothing; keep enforcement at scoring time.* The status quo, which leaves the gap the audit names.

*Build a separate, fixture-neutral validator and point the agent at that.* The one adopted in principle, and deliberately not built in this pass.

## What settled it

The first position is not merely imperfect, it is unsafe, and the scorer says so itself.
`score_ledger.py`'s SCOPE header states that it scores ledgers from scenarios whose ground truth contains *no legitimate causal refutation*, that C1 is not a general ledger invariant, and that running C1 against a should-refute scenario "would fail correct work and teach analysts never to conclude anything — the top regression risk this revision is trying to avoid."
The skill explicitly permits refuting a causal hypothesis on independent evidence, and the worked example in `references/ledger-template.md` does exactly that twice.

So an agent told to run this scorer on its own ledger and satisfy it would be told, on any investigation that legitimately refutes a causal hypothesis, to downgrade a correct `REFUTED` to `UNRESOLVED`.
The instrument would not be enforcing the skill; it would be contradicting it.
C3 and C4 compound this — both are gated on caller attestations about the fixture that no agent can make about a live investigation.

That kills the specific remedy without settling the underlying gap, which is real.
What a fixture-neutral validator could check is structural and worth having: the canonical Problem fields present and filled, the Hypotheses schema complete, necessary predictions non-empty, ids well-formed, the closed vocabularies respected.
What it could not check is whether a stop condition is genuinely anti-fishing, or whether a necessary prediction follows from the hypothesis's mechanism.
It would therefore complement the semantic prose rather than license deleting them — which also means it does not, on its own, answer the accrual problem the audit raised.

Two constraints any such validator inherits, both reasons it is not a five-minute change: it must be a public interface outside `tests/` with no third-party dependencies and a tested runtime floor, because the skill declares no runtime capability and may be loaded without a stable filesystem path or a Python interpreter; and a tool that is unavailable must be recorded as unavailable, never mistaken for a clean pass.
Adding any such instruction to SKILL.md is an agent-facing wording change and owes measured arms under decisions/001, which is why the instruction is not in this pass either.

## Reopening condition

A fixture-neutral structural validator exists as a public, dependency-free CLI with its own tests, and the SKILL.md sentence pointing at it has been preregistered and measured on the cells its placement reaches.
Or: someone demonstrates a structural-only mode of `score_ledger.py` that cannot reach C1–C4 without their caller attestations, which would make the cheap version of the first position safe after all.

## Where the rule lives

Nowhere yet — this decision records why no agent-read file points at an instrument, so that the next reader does not re-propose it.
The scorer's own applicability limits are stated in `tests/score_ledger.py`'s SCOPE header, which is the authority on what it may be pointed at.
