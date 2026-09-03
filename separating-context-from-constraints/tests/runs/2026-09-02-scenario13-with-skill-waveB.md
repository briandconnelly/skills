# Scenario 13 — design-review, With-Skill, three reps (Wave B rerun, W10, D13.2 planted)

```
Date: 2026-09-02
Run: with-skill
SKILL.md blob: 2cb876f4010f55a3259fe740a46d1e8aaea78eea
Commit: a9f0116 (branch `separating-context-wave3`, Wave B wording; not on `main`)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/SKILL.md: read that file and any file it references under /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/references/. Do not read any other file anywhere, do not read anything under any tests/ directory, do not load any skill through the harness, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under the preregistration's Rerun classification; per-defect tables transcribed and reconciled by a Claude subagent (opus) against the archived outputs; tool calls extracted by script
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); the prompt above is the one line that preceded the scenario-13 prompt from `../scenarios.md`, which followed it verbatim; no dispatch for this scenario failed
```

## Scoring

| Rep | D13.1 | D13.2 | B13.1 not flagged | E2 | E3 on D13.1 |
| --- | --- | --- | --- | --- | --- |
| 1 | ✓ **R3**, material | `missed` — left on the guard list as "an ordinary domain predicate" | ✓ — "binding, mandatory, and checkable against tool traces" | 0 | preserved (four labeled alternatives, "none is selected") |
| 2 | ✓ **R3**, material (Finding 2) | ✓ **R3**, material (Finding 1), ground: the trigger "major changes" is "not decidable" | ✓ — "checkable against tool traces. Clean." | 0 | preserved (promoted / demoted, "no defeasible default is substituted") |
| 3 | ✓ **R3**, material (first finding) | ✓ **R3**, material (second finding), ground: "a magnitude qualifier the document does not bound" | ✓ — "trigger decidable (before proposing), result checkable against tool traces" | 0 | preserved (promoted / demoted / bound by a named artifact) |

E1 over D13.1 and D13.2: **1/2, 2/2, 2/2**.
Scored assertions from `../scenarios.md`: assertion 1 (D13.1 under R3), assertion 3 (B13.1 left alone or escalated), and assertion 4 (no finding on the last two rules or the Context paragraph) — **3/3 ×3**.
Assertion 2 is not scored as written: it is amended to point at the Rerun classification, which reclassifies D13.2 from an observation to a planted defect, so D13.2 is scored under E1 in the table above instead.

E9c: guard-lines true ×3; classification-table true ×3 (rep 1 prints a classification table; reps 2 and 3 assign classes to two or more statements in the not-flagged list); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** D13.2 was an observation in the archived cell and is planted under R3 in the rerun, because the Wave B `SKILL.md` requires a decidable trigger (`:55-56`).
Two of three reps flag it, against 3/3 in the archived cell where it counted for nothing, so the wording that made it scorable also made it harder to catch.
Rep 1 missed it by applying the same wording's escape clause to the same phrase, calling "major changes" "an ordinary domain predicate the reviewer can decide from the design document", with the result "checkable against repository state (`docs/decisions/`)", and adding: "Under R3 as written, a trigger is a finding only when nothing lets the reader decide it; that is not the case here."
Rep 3 reaches the opposite reading of the identical clause, holding that "major changes" is "not an ordinary domain predicate in the way" that "hotfix" or "new external dependency" is, so the clause, not the fixture, is what the reps disagree about.
D13.1 stays 3/3 with the author-decision contract intact, B13.1 is left alone 3/3, and E2 stays 0 ×3, so W10's first half is answered partially rather than closed.

## Scored Outputs (verbatim)

### With-skill, rep 1

> **Audit: `design-review`** (audited against the skill's R1–R5; line numbers count the target's opening `---` as line 1)
>
> ## Classification
>
> | Line | Statement | Class |
> |---|---|---|
> | 3 | `description: Use when reviewing a design document before implementation.` | Routing/trigger statement in compact frontmatter; inline marking is all it owes |
> | 10 | Read the linked design document in full before proposing an approach. | Binding rule |
> | 11 | For major changes, add an entry to `docs/decisions/`. | Binding rule |
> | 12 | Keep the review tone professional. | Binding rule |
> | 13 | Post the review as a single pull request comment rather than as inline comments. | Binding rule |
> | 14 | Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner. | Binding rule (condition–action–exception, one trigger) |
> | 18 | Design reviews were introduced after two rewrites shipped without any written rationale. | Discretionary context |
>
> ## Findings
>
> **R3 Verifiability**
> Location: line 12.
> Quoted text: "Keep the review tone professional."
> Why it fails: the trigger is fine (every review), but the result has no observable evidence against which "professional" can be checked. The document bounds the judgment with no quantity, named artifact, or named exclusion, so neither the reviewer nor anyone checking the review can tell whether the rule was followed or violated. It is the same shape as the skill's "Be concise" example. The statement does not reveal the intended safeguard, so the rewrite is an author decision.
> Severity: material (prevents verification).
> Suggested rewrite: author decision between labeled alternatives; none is selected.
> - If a content prohibition is intended: "Address only the design's content; do not comment on the author's competence or make personal remarks." (checkable against the review text)
> - If a form prohibition is intended: name the excluded forms, e.g. "Do not use profanity or sarcasm in the review." (checkable against the review text)
> - If it is only an expectation, not a rule: remove it from `## Rules` and state under `## Context`: "Reviews are expected to read professionally; this document defines no specific tone check."
> - If another safeguard is intended, name its observable evidence rather than choosing one of the above.
>
> ## Not flagged (false-positive guards)
>
> - Line 10: binding, mandatory, and checkable against tool traces (reads covering the linked document before any proposal). It is a policy, not a procedural step — skipping it violates the rule.
> - Line 11: "major changes" is an ordinary domain predicate the reviewer can decide from the design document, and the result is checkable against repository state (`docs/decisions/`). Under R3 as written, a trigger is a finding only when nothing lets the reader decide it; that is not the case here.
> - Line 13: single obligation with a checkable result (one PR comment, no inline comments). "Rather than as inline comments" is the same decision, not a second obligation, so no R4 issue.
> - Line 14: R4 — condition, action, and exception share one trigger and may stay together. R3 — the trigger (design introduces a new external dependency) is decidable from the input, and the exception's evidence is an artifact: the design's naming of a maintenance owner, which is observable in the design document. This is not the "naming a party as authority" pattern R3 excludes; the exception does not defer to a party's say-so, it requires that an owner be written down.
> - Line 18: discretionary context, correctly placed in `## Context` and outside `## Rules`.
> - R1: every rule is a list item in a labeled rule section; the rule section holds no context or load-bearing facts; nothing binding sits in `## Context`. No R1 findings.
> - R2: every rule uses unhedged imperative or "Never" wording; no ambiguous strength.
> - R5: no two rules prescribe incompatible outcomes on a realistic input (the decisions-entry rule at line 11 and the single-comment rule at line 13 concern different artifacts). No precedence is owed.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1 (R3), minor 0. No finding carries a secondary rule id, so the per-rule total equals the one finding counted by severity.
>
> This document is structurally well separated: all five rules are marked list items in a dedicated `## Rules` section, each states its strength plainly, the section contains no context, and the one background sentence sits in `## Context`. The single defect is that "Keep the review tone professional" names no observable evidence, so it cannot be verified as followed or violated; resolving it requires the author to decide whether it is a specific prohibition (and which one) or an expectation to be demoted to context. No rewritten whole document is produced, since the request did not ask for one.

### With-skill, rep 2

> # Audit report: `design-review`
>
> Source of the procedure: `/private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/SKILL.md` and its one referenced file, `references/example-audit.md`. No other files were read.
>
> Line numbers below refer to the target as pasted (line 1 is the opening `---`; rules occupy lines 10–14; the Context sentence is line 18).
>
> ## Findings
>
> **Finding 1 — R3 Verifiability**
> Location: line 11.
> Quoted text: "For major changes, add an entry to `docs/decisions/`."
> Why it fails: the result is checkable against repository state (an entry exists under `docs/decisions/`), but the trigger "major changes" is not decidable. The document does not bound the judgment with a quantity or a named artifact, so two readers can disagree about whether the rule applied, and after the fact no one can tell whether a missing entry is a violation or a non-major change. The obligation can be omitted without any observable breach.
> Severity: material.
> Suggested rewrite: author decision — the safeguard (a decision record) is clear, but the threshold is not. Labeled alternatives, none selected:
> - A — bound the trigger by a named artifact or category: "When the design document is marked major (author names the marker: a frontmatter field, a template checkbox, or a category such as adding/removing a service, public API, or external dependency), add an entry to `docs/decisions/`."
> - B — remove the condition: "For every reviewed design, add an entry to `docs/decisions/`."
> - C — keep the judgment but make its exercise observable: "State in the review comment whether the change is major; for changes stated as major, add an entry to `docs/decisions/`."
>
> **Finding 2 — R3 Verifiability**
> Location: line 12.
> Quoted text: "Keep the review tone professional."
> Why it fails: the trigger (every review) is decidable, but "professional" names no observable evidence — no output property, tool call, or artifact — against which compliance can be checked. As written it cannot be violated in a way anyone could demonstrate, and it does not reveal what safeguard the author intends. (This is on the verifiability axis; the skill's non-goal on tone review excludes auditing the target's own prose tone, not a target rule whose subject is tone.)
> Severity: material.
> Suggested rewrite: author decision between a promoted and a demoted reading; no defeasible default is substituted.
> - Promoted (binding, author supplies the observable criteria): e.g. "Address the design, not its author; the review contains no personal remarks, sarcasm, or profanity."
> - Demoted (nonbinding context, moved out of `## Rules` into `## Context`): "Reviews are expected to keep a professional tone; this document defines no checkable criterion for it."
> - If a different safeguard is intended, name its observable evidence rather than adopting either example.
>
> ## Not flagged (false-positive guards)
>
> - Line 10, "Read the linked design document in full before proposing an approach." — binding (ignoring it is a policy breach, not a mere how-to step), explicitly mandatory, decidable trigger, checkable against tool traces. Clean.
> - Line 13, "Post the review as a single pull request comment rather than as inline comments." — one obligation stated with a contrast, not a compound (R4 passes); checkable against PR state. Clean.
> - Line 14, "Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner." — explicit mandatory strength (R2); "introduces a new external dependency" is an ordinary domain predicate decidable from the design document; the exception is satisfied by an observable artifact (the owner's name written down), so the "naming a party is not evidence" guard does not bite — the exception is the act of naming, not a deferral to a party. Condition–action–exception on one trigger stays together (R4). Clean.
> - Line 18, the Context sentence — rationale that degrades gracefully if lost; correctly placed outside `## Rules`. The `## Rules` section holds only directives, so R1 has no misplaced statements in either direction.
> - R5: no pair of rules prescribes incompatible outcomes for the same decision on a realistic input (delivery form, repository artifact, approval gate, and reading order are all jointly satisfiable). No speculative precedence owed.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: material 2, minor 0. Total findings: 2. No finding carries a secondary rule id, so the per-rule total equals the severity total.
>
> This is a structurally sound document: rules are marked as list items, grouped under a labeled `## Rules` section, uniformly imperative, and the single context sentence sits in its own section. Both defects are on the verifiability axis rather than separation — one rule hangs a repository obligation on the unbounded predicate "major", and one rule prescribes a tone with no observable criterion. Both require an author decision before a semantic-preserving rewrite can be committed to; the alternatives above are labeled and none is selected.

### With-skill, rep 3

> ## Audit: `design-review`
>
> Line references use the fenced document as given (line 1 = opening `---`; Rules items are lines 10–14; the Context sentence is line 18).
>
> ### Findings
>
> **R3 Verifiability**
> Location: line 12.
> Quoted text: "Keep the review tone professional."
> Why it fails: the rule has a decidable trigger (every review) but no result checkable against observable evidence. "Professional" is a judgment the document does not bound with a quantity, a named artifact, or an enumerated criterion, so a reader cannot tell whether a given review satisfies or violates it; it is the same shape as "Be careful with production." The statement does not reveal the author's intended safeguard, so the rewrite is an author decision.
> Severity: material.
> Suggested rewrite: author decision between the following.
> - Promoted (bounded criteria): replace with observable requirements, e.g. "Address every comment to the design, not the author; do not include profanity or personal characterizations." (The author supplies the actual criteria; these are examples of the shape, not the meaning.)
> - Demoted (context): remove it from `## Rules` and state under `## Context`: "Reviews are read by the design's author; this document defines no tone requirement."
> - If a specific standard is intended (a style guide, a code of conduct), name that artifact: "Follow `<artifact>` for review tone."
>
> **R3 Verifiability**
> Location: line 11.
> Quoted text: "For major changes, add an entry to `docs/decisions/`."
> Why it fails: the result is checkable (an entry exists under `docs/decisions/`), but the trigger "major changes" is a magnitude qualifier the document does not bound with a quantity or a named artifact, and it is not an ordinary domain predicate in the way "hotfix" or "new external dependency" is. Two readers of the same design can disagree on whether it is major, so whether the obligation applied cannot be verified and the entry can be silently omitted. This is the closer call of the two findings: if a parent layer or team convention defines "major," that inherited definition would resolve it (cross-layer analysis is out of scope here).
> Severity: material.
> Suggested rewrite: author decision on the threshold.
> - Bound by named artifact or enumerated predicate: "For changes that add or remove a service, change a public API, or alter a persisted schema, add an entry to `docs/decisions/`." (Author supplies the actual list.)
> - Bound by an existing definition: "For changes classified as major under `<named document or label>`, add an entry to `docs/decisions/`."
> - Unconditional: "Add an entry to `docs/decisions/` for every reviewed design." (Only if the author intends the broader obligation; this changes policy and is offered as an alternative, not a selection.)
>
> ### Not flagged (false-positive guards)
>
> - Line 10, "Read the linked design document in full before proposing an approach." Binding, mandatory, trigger decidable (before proposing), result checkable against tool traces. Correctly placed.
> - Line 13, "Post the review as a single pull request comment rather than as inline comments." Binding, mandatory, checkable against the PR. The "rather than" clause contrasts the same obligation and does not bundle a second one (R4 passes).
> - Line 14, "Never approve a design that introduces a new external dependency without naming that dependency's maintenance owner." Condition–action–exception sharing one trigger, so R4 permits the single unit. The exception is decidable: the evidence is a named owner recorded in the design or review, an observable artifact, not merely a party's say-so. Strength is explicit (R2 passes).
> - Line 18, "Design reviews were introduced after two rewrites shipped without any written rationale." Discretionary rationale, correctly placed under `## Context` and absent from `## Rules`.
> - R1: every rule is a marked list item in a labeled rule section; the rule section contains no context or load-bearing facts; the context section contains no embedded rules. No R1 findings.
> - R2: no hedged statements; every rule is an imperative or "Never." No R2 findings.
> - R5: no two rules prescribe incompatible outcomes for the same decision on a realistic input. No R5 findings.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 2, R4 0, R5 0.
> Counts per severity: material 2, minor 0. No finding carries a secondary rule id, so the per-rule total equals the two findings counted by severity.
>
> Structurally this document is already well separated: rules are marked list items under a labeled `## Rules` section, strength is explicit throughout, the one condition–action–exception rule is a legitimate single unit, and the sole context sentence sits outside the rule section. Both findings are on the verifiability axis rather than separation: one rule ("professional tone") has no observable result, and one rule's trigger ("major changes") is unbounded, so neither can be checked as followed or violated. Both require author decisions before a semantic-preserving rewrite can be claimed; no rewrite of the whole document was requested, so none is supplied.
