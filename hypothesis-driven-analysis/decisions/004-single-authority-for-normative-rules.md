# 004 — Normative rules have one home; reference files point, never paraphrase

Decided 2026-07-25.

## Question

Reference files are read by agents doing the work, so it is tempting to restate the rules they need where they will encounter them.
Issue #103 was the bill for that: SKILL.md and `references/subagent-briefs.md` prescribed different recorded outcomes for the same faulted return, and both were followed — measurement showed 2/3 arms taking SKILL.md's disposition and 3/3 taking the reference file's when it was also in context.
Where does a normative rule live?

## Positions

*Restate for the reader.* The convenience is real: a worker reading a brief template should not have to open SKILL.md to know what it owes.
The cost is that two statements of one rule diverge silently, and nothing fails when they do — the prose still reads correctly on both sides.

*Single authority.* Adopted, and stated for the repo in `AGENTS.md`, because divergence is not hypothetical here.
`subagent-briefs.md` had already drifted before anyone looked: its summary narrowed "did not adequately test" to "untested" and dropped the outside-evidence exception, which is the same drift #103 was filed about, reproduced in miniature by the file that was supposed to be summarizing the fix.

## What settled it

Measurement, and then a second instance of the same failure found by inspection.
The pointer version was not a guess: after the fix, arms that never opened the reference file reached the intended disposition 6/6 — the rule reached them through SKILL.md, which is the file they always read.
The convenience the restatement bought was smaller than it looked.

The condition is structural, so it is not enough to fix the instance.
`references/ledger-template.md` carried three more restatements of SKILL.md rules, one of which had *already* diverged: it said a `descriptive` row cannot be added after Plan time, which is stronger than what SKILL.md prescribes and contradicts the same template two lines below, where hypotheses added after seeing data are given a `retrospective` label.
Nobody noticed, because nothing was checking.

Not everything that names a closed-set value is a duplication.
The template legitimately owns the machine-checkable `adequacy: <rate> ± <uncertainty> (variants: <range>)` atom, which exists in the template and in `tests/score_ledger.py` and nowhere else; moving that into SKILL.md would be worse.
The line is between *what the rule is* (SKILL.md) and *how a ledger records it* (the template).

## Not enforced by a linter

The first proposal was a hook flagging closed-set vocabulary beside prescriptive modals in reference files.
Run against the real corpus it flagged worked-example prose and template-owned syntax while missing four of the lines that prompted it, because the duplications that matter are not written with the modals a lexical rule can look for.
An `<!-- authority: -->` escape hatch would have been applied wholesale on day one and become a rubber stamp.

What shipped instead is `scripts/check-citations.py`, which checks something decidable: a quote attributed to a file must appear in that file, and line-number citations into files still being edited are rejected because they rot silently.
It does not detect paraphrase. It detects the citations that were supposed to keep paraphrase honest.

## Reopening condition

A duplication appears that the citation check cannot see and inspection did not catch — which would mean the structural fix needs an instrument after all, and the question becomes which one, not whether.

## Where the rule lives

`AGENTS.md`, repo-wide. SKILL.md owns this skill's normative rules; the reference files point at it from the sites where a summary used to be.
