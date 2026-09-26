# Mixed Sentence — Confirmation Cell (prior wording)

Date: 2026-09-26
Run: with-skill
SKILL.md blob: 713c6967362667a405048a7e75d04f18c329804c
Commit: `d709291` (main at dispatch); `SKILL.md` was written to the session scratchpad with `git show main:separating-context-from-constraints/SKILL.md`, and `references/example-audit.md` was copied beside it unchanged
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model at dispatch, inherited by each subagent with no per-agent override
Harness: Claude Code 2.1.283, Agent tool, general-purpose subagent, three independent dispatches in one parallel batch
Prompt: the fixture below, verbatim, preceded by the preface quoted under "Dispatch" below
Sampling: harness default
Scorer: Claude Fable 5.1 (claude-fable-5-1), the session model, 2026-09-26, unblinded
Notes: this is a confirmation cell, not a scenario. The fixture is not in `tests/scenarios.md` and was written for this cell. It is the known-positive probe for a proposed wording change, so it runs on the PRIOR wording first; the preregistration below says when the wording ships and when it is declined.

## Why this cell

The 2026-09-26 review (`review-20260926.md`, finding 2) observes that Core Concept assigns each *statement* one of three roles but never says what to do with a sentence that pairs an obligation with its rationale, and that Finding Format's "one finding per statement" therefore leaves extraction and consolidation undefined for such sentences.
The review calls the result unstable.
The archive does not show instability: the 2026-09-14 scenario 1 cell handled the fixture's mixed sentence ("must never exceed 72 characters, since several terminal-based git tools…") the same way in 3/3 reps — one R1 finding, the whole sentence quoted, the rewrite separating the obligation from the rationale.
That fixture only has the mixed sentence buried in context.
It does not exercise the other shape a clause-level unit would touch: a correctly placed rule inside `## Rules` that carries its own rationale clause, where a clause-level reading could produce a new minor R1 finding (context inside the rule section) that the current wording does not induce.

This cell settles whether the wording is needed before it is written into `SKILL.md`, per the S19/S21 precedent in the adopted protocol: a wording that the current text already induces is declined as a measured no-change-needed outcome.

## Fixture

```markdown
# release-notes-bot

## Context

Release notes are generated from merged pull requests once a week.
Every entry must name the affected component first, because the support team searches the notes by component.
The bot was moved off the legacy pipeline in 2025.

## Rules

- Never include a ticket number in an entry, since customers cannot open the tracker.
- Tag each entry with exactly one of `added`, `changed`, or `fixed`.
```

Planted (D1): line 6, the component-first sentence — a binding rule buried in `## Context` with its rationale attached in the same sentence.
Probe (P1): line 10, the ticket-number rule — correctly placed in `## Rules`, with a rationale clause attached. Neither planted nor protected; the cell records what each arm does with it.
Protected: line 5 (schedule fact), line 7 (history), line 11 (clean rule).

## Preregistered questions

| # | Question | Expected on prior wording |
| --- | --- | --- |
| 1 | D1 receives exactly one R1 finding — not one per clause and not zero — with material severity, quoted text that contains the obligation clause, and a rewrite that moves the obligation into `## Rules` and keeps the rationale as context | PASS, by the 2026-09-14 scenario 1 precedent |
| 2 | P1: does the rationale clause draw a finding? Record id, severity, and rewrite if so | Recorded, not scored; this is the over-correction baseline for any clause-level wording |
| 3 | No finding against the three protected lines | PASS |

## Preregistered outcomes for the finding-2 wording

The candidate wording, held out of `SKILL.md` until this table says it ships:

> Core Concept: "The classification unit is the clause, not the sentence. A sentence can pair an obligation with its rationale — "Never exceed 72 characters, because terminals wrap longer subjects" — and then holds a binding rule and discretionary context; classify each clause by its own role."
> Finding Format: "A sentence whose clauses play different roles is one finding: quote the whole sentence, and let the rewrite separate the clauses."

| Prior-wording result | Action |
| --- | --- |
| Q1 3/3 and Q3 3/3 | **Decline** the wording as measured no-change-needed. Record the decline in `tests/scenarios.md` and in the PR. The self-compliance edits (review findings 4a and 4b) ship alone, with their own confirmation cells. |
| Q1 < 3/3 (any rep splits D1 into two findings, misses it, or quotes only the rationale) | Write the wording, run this fixture on the new wording ×3. Ship only if new Q1 = 3/3, new Q3 = 3/3, and the new Q2 count is not higher than the prior Q2 count. |
| New-wording Q2 count higher than prior | Over-correction: do not ship; open an author decision on whether a rationale clause attached to its own rule inside a rule section is an R1 finding. |
| Any wording that ships | Scenario 1 ×3 and scenario 5 ×3 on the shipped blob; standing assertions must hold (5/5 and 4/4) or the wording is reverted. |

Written before any arm was dispatched.

## Dispatch

Each rep received this preface, with its own skill directory and output path substituted, followed by the prompt "Audit this document for separation of context from constraints, and report your findings:" and the fixture:

> Follow the skill at `<skill dir>/SKILL.md`. Read that file first; you may also read files under `<skill dir>/references/`.
> Do not read any other file anywhere (in particular nothing under any tests/ directory), do not run shell or git commands, do not invoke any other skill, and make no edits except one: write your complete audit report to `<rep output path>` and also return it as your final message.
> Then complete this task:
