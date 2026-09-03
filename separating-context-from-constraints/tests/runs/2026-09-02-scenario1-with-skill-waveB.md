# Scenario 1 — commit-message-helper, With-Skill, three reps (Wave B rerun, W4/R1 embedding regression)

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
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script)
```

## Scoring

Assertion labels follow the order of the bullets in `tests/scenarios.md`, scenario 1: A1 the conventional-commit prefix clause gets an R1 finding with quoted text and a rewrite into a dedicated rules section; A2 the same for the 72-character subject clause; A3 the same for the "Test plan" clause; A4 all three findings are material; A5 no finding is raised against the pure-background sentences.

| Rep | A1 prefix clause R1 | A2 72-char clause R1 | A3 Test-plan clause R1 | A4 all three material | A5 background sentences clean | E2 | Secondary observations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ✓ Finding 1, quoted, rewrite adds a `## Rules` section | ✓ Finding 2, quoted, same rewrite | ✓ Finding 3, quoted, same rewrite | ✓ material ×3 | ✓ history, sentiment, rationale, joke and `CHANGELOG.md` all in the not-flagged list | 0 | secondary R3 on the Test-plan rule's commit scope, with the two scopes offered as an author decision |
| 2 | ✓ first R1 finding, quoted, rewrite adds a `## Rules` section | ✓ second R1 finding, quoted, same rewrite | ✓ third R1 finding, quoted, same rewrite | ✓ material ×3 | ✓ lines 8, 10, 14, 15, 17 and 22 all in the not-flagged list | 0 | none; the commit-scope question is named but explicitly left outside the finding |
| 3 | ✓ Finding 1, quoted, rewrite adds a `## Rules` section | ✓ Finding 2, quoted, same rewrite | ✓ Finding 3, quoted, same rewrite | ✓ material ×3 | ✓ lines 8, 10, 14, 15, 17 and 22 all in the not-flagged list | 0 | secondary R3 on the Test-plan rule's commit scope, with two labelled readings and neither selected |

Scored assertions: **5/5 ×3.**

E9c: guard-lines true ×3; classification-table true ×3 (each rep's not-flagged list assigns a class — discretionary context or load-bearing fact — to every unflagged sentence); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** Nothing changed against the archived cell: the three buried rules are still reported under R1 with quoted text, material severity, and a rewrite that creates the rules section the target lacks, and no background sentence is flagged.
The Wave B wording of R1 adds an explicit long-form/compact test, and all three reps invoke it by name before lifting anything, which is the behaviour this regression cell exists to confirm.
The only movement is a secondary R3 in reps 1 and 3 on the Test-plan rule's commit scope; it sits on a planted statement, so it is an observation rather than an E2 false positive, and both reps leave the scope as an author decision rather than resolving it.

## Scored Outputs (verbatim)

### With-skill, rep 1

> ## Audit: `commit-message-helper`
>
> Line numbers count from the first `---` of the document as line 1. The document is long-form (it has labeled `## Background` and `## Notes` sections), so under R1 the rewrite for each embedded, liftable rule moves it into a dedicated labeled rule section; the document currently has no rule section at all.
>
> ### Findings
>
> **Finding 1 — R1 Distinguishability**
> Location: line 9 (opening paragraph, no heading).
> Quoted text: "When we finally settled the convention during the 2023 tooling cleanup, we agreed messages should always start with a lowercase conventional-commit type such as feat or fix."
> Why it fails: this is the document's primary binding rule — an agent that ignores it produces a wrong commit message — but it is phrased as a report of a past agreement ("we agreed …") and sits in a paragraph whose other sentences (lines 8 and 10) are history and team sentiment. Nothing in its placement or grammar signals that it binds; the format requirement is carried by a subordinate clause of a narrative sentence. It is liftable: obeying it does not depend on the surrounding history. Strength is not ambiguous ("always" makes it mandatory), so no R2 finding attaches; the two properties (lowercase, conventional-commit type) describe the form of one prefix under one trigger and stay together under R4.
> Severity: material — a rule stated only as narrative can plausibly be missed.
> Suggested rewrite: leave lines 8 and 10 in place as context, drop the rule clause from line 9, and add a `## Rules` section containing: "Always start the commit message with a lowercase conventional-commit type (for example `feat` or `fix`)." Line 9 can be shortened to the remaining context: "The convention was settled during the 2023 tooling cleanup."
>
> **Finding 2 — R1 Distinguishability**
> Location: line 16 (`## Background`).
> Quoted text: "It's also worth noting that the subject line must never exceed 72 characters, since several terminal-based git tools truncate or wrap longer lines awkwardly during review."
> Why it fails: "must never exceed 72 characters" is a mandatory, fully verifiable rule (count the characters of the subject line), but it is introduced with "It's also worth noting that" — framing that marks it as an aside — and it shares a paragraph with tool semantics (line 14), rationale (line 15), and the joke at line 17 that it is "the one rule everybody breaks eventually." The rule occupies its own sentence, yet the paragraph mixes it with informing statements, which is the R1 definition of embedded. It is liftable.
> Severity: material — the "worth noting" framing plus the surrounding banter make it plausible an agent treats the limit as negotiable color rather than a requirement.
> Suggested rewrite: add to the `## Rules` section: "Never let the subject line exceed 72 characters." Keep the rationale in `## Background` as context, e.g. "Several terminal-based git tools truncate or wrap subject lines longer than 72 characters during review." Line 17 is discretionary context and may stay in `## Background`; it is not itself a finding.
>
> **Finding 3 — R1 Distinguishability (secondary: R3 Verifiability)**
> Location: line 21 (`## Notes`).
> Quoted text: "By the way, before you open a pull request the commit body must include a "Test plan" section describing how the change was verified — reviewers have flagged its absence in the past."
> Why it fails: this is a mandatory rule with a decidable trigger (opening a pull request) and an observable result (a "Test plan" section in the commit body), but it is opened with "By the way," placed under a heading named `## Notes`, fused to its rationale in the same sentence, and paired in its paragraph with a load-bearing fact about the release-notes generator (line 22). It is liftable. Secondary R3 observation: the object "the commit body" does not say which commit(s) it covers when a pull request contains several commits, so the result is checkable for a single-commit PR but the document does not let the reader decide the scope for a multi-commit PR.
> Severity: material — a requirement introduced as an afterthought under "Notes" can plausibly be omitted, and reviewers have already observed that omission.
> Suggested rewrite: add to the `## Rules` section, preserving current wording: "Before opening a pull request, include a "Test plan" section in the commit body describing how the change was verified." Move the rationale to context: "Reviewers have flagged missing Test plan sections in the past." The scope question is an author decision; labeled alternatives, without selecting one: (a) "… in the body of every commit in the pull request …"; (b) "… in the body of the pull request's final (or squash) commit …". The primary rewrite above keeps the existing ambiguity rather than resolving it silently.
>
> ### Not flagged (false-positive guards)
>
> - Line 3 (frontmatter description): trigger description, not a behavioral rule.
> - Lines 8, 10, 15, 17: discretionary context — history, sentiment, rationale, and banter; they degrade gracefully if lost and are correctly outside any rule section.
> - Line 14: load-bearing fact (the generator extracts the type prefix); it informs rather than directs and is correctly placed in `## Background`.
> - Line 22: load-bearing fact about tool semantics (`CHANGELOG.md` location); not a directive, correctly placed in a context section.
> - R2: none of the three rules has ambiguous strength ("always", "must never", "must").
> - R4: no rule bundles independently checkable obligations.
> - R5: no two rules prescribe incompatible outcomes for the same decision (type prefix, subject length, and body section are independent), so no precedence is owed.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 3, R2 0, R3 1 (secondary id on Finding 3), R4 0, R5 0.
> Counts per severity: material 3, minor 0. The severity total (3) is the number of findings; the per-rule total (4) exceeds it because one finding carries a secondary id.
>
> Every one of this document's three binding rules — the lowercase conventional-commit prefix, the 72-character subject limit, and the mandatory "Test plan" body section — is buried in narrative prose: one as a subordinate clause of a history sentence, one as an "also worth noting" aside next to a joke about breaking it, one as a "by the way" under `## Notes`. Each rule is individually clear in strength and (with one scope question on the Test plan rule) verifiable, so the defect is purely structural: no reader can tell from placement which sentences bind. The document owes a dedicated `## Rules` section holding the three lifted rules, with the history, rationale, and generator semantics left where they are as context; the facts at lines 14 and 22 and the discretionary sentences are already correctly placed and need no change. The Test plan rule's commit scope requires an author decision before a rewrite can claim to preserve intended behavior.

### With-skill, rep 2

> # Audit: `commit-message-helper`
>
> Line numbers count the fenced document from its opening `---` as line 1. The document is long-form (it has labeled `## Background` and `## Notes` sections), so embedded rules that are liftable owe a dedicated rule section under R1.
>
> ## Findings
>
> **R1 Distinguishability**
> Location: line 9 (intro paragraph, lines 8–10).
> Quoted text: "When we finally settled the convention during the 2023 tooling cleanup, we agreed messages should always start with a lowercase conventional-commit type such as feat or fix."
> Why it fails: this is a binding rule (ignoring it produces a message the release-notes generator cannot parse), but it is embedded in a narrative paragraph about repo history, framed as something "we agreed" rather than as a directive, and sandwiched between two discretionary sentences (drift history, team satisfaction). Nothing structural signals that it binds. The rule is liftable — obeying it does not depend on the history around it. Strength is not ambiguous: "always" reads as mandatory, so no R2 id attaches.
> Severity: material.
> Suggested rewrite: add a `## Rules` section and place the rule there as its own item: "Always start the commit message with a lowercase conventional-commit type (for example `feat` or `fix`)." Keep the history as context in the intro or `## Background`: "The convention was settled during the 2023 tooling cleanup."
>
> **R1 Distinguishability**
> Location: line 16 (`## Background`, paragraph lines 14–17).
> Quoted text: "It's also worth noting that the subject line must never exceed 72 characters, since several terminal-based git tools truncate or wrap longer lines awkwardly during review."
> Why it fails: the rule is stated with explicit strength ("must never") and a checkable result (72 characters), but it is embedded in a paragraph of tool-semantics facts and rationale, inside a section labeled `Background`, and introduced with the aside marker "It's also worth noting" — a framing that signals color, not obligation. The next sentence (line 17, "the one rule everybody breaks eventually") sits alongside it and further blurs whether it is negotiable. A reader skimming for requirements can miss it. Liftable.
> Severity: material.
> Suggested rewrite: move the obligation to `## Rules` as its own item: "Never exceed 72 characters in the subject line." Retain the rationale in `## Background` as context: "Several terminal-based git tools truncate or wrap subject lines longer than 72 characters awkwardly during review." Line 17 may remain as discretionary context; once the rule is lifted it no longer reads as a qualifier on it.
>
> **R1 Distinguishability**
> Location: line 21 (`## Notes`, paragraph lines 21–22).
> Quoted text: "By the way, before you open a pull request the commit body must include a \"Test plan\" section describing how the change was verified — reviewers have flagged its absence in the past."
> Why it fails: this is the document's most consequential obligation (a missing section is an observable defect reviewers act on), yet it appears under a `Notes` heading, is prefaced with "By the way," and is fused with rationale in the same sentence and with a tool-semantics fact (line 22) in the same paragraph. Strength ("must") and trigger ("before you open a pull request") are explicit and the result is checkable against repository state, so no R2/R3 id attaches; the defect is purely that the rule is indistinguishable from the notes around it. Liftable.
> Severity: material.
> Suggested rewrite: move to `## Rules` as its own item: "Before opening a pull request, include a \"Test plan\" section in the commit body describing how the change was verified." Retain the rationale in `## Notes` as context: "Reviewers have flagged missing Test plan sections in the past." The rewrite keeps the original's scope wording ("the commit body") as written; whether that means every commit in the PR or only the commit being drafted is left as the author stated it, and pinning it down would be an author decision outside this finding.
>
> ## Not flagged (false-positive guards)
>
> - Line 14 ("Commit messages are read by the release-notes generator, which extracts the type prefix...") and line 22 ("The release-notes generator reads the `CHANGELOG.md` file...") are load-bearing facts about tool semantics. They inform rather than direct and are correctly placed outside any rule section. They do not conflict with each other (neither is a rule, so R5 does not apply).
> - Lines 8, 10, 15, and 17 are discretionary context (history, sentiment, rationale, joke). They are correctly outside any rule section; prose quality is a non-goal.
> - Line 9's "should always" is not an R2 finding: "always" makes the strength decidable as mandatory. If the author actually intended a defeasible default, the rewrite above would need an override condition added — that would be a policy change, not a structural one.
> - Line 9's "lowercase" plus "conventional-commit type" is not an R4 finding: both properties describe one prefix token under one trigger and stay together as a single unit.
> - R5: the three rules govern disjoint parts of the message (prefix, subject length, body section) and cannot prescribe incompatible outcomes for the same decision; no precedence is owed.
>
> ## Summary
>
> Counts per rule: R1 3, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 3, minor 0.
> No finding carries a secondary rule id, so the per-rule total of three equals the three findings counted by severity.
>
> The document contains exactly three binding rules and places none of them where a reader would look for a rule: one is a clause inside a history anecdote in the intro, one is an aside inside `## Background`, and one is a "by the way" inside `## Notes`. Each rule is individually well-formed — explicit strength, decidable trigger, checkable result, no compound obligations, no reachable conflicts — so the whole audit reduces to a single structural fix: introduce a `## Rules` section holding the three obligations as separate items, and leave the surrounding facts and rationale where they are. The `Background` and `Notes` sections then correctly contain only load-bearing facts and discretionary context.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit; all directives are ordinary target rules addressed to the agent drafting commit messages.

### With-skill, rep 3

> ## Audit: `commit-message-helper`
>
> Line numbers count the opening `---` of the frontmatter as line 1. The document is long-form (it has labeled `## Background` and `## Notes` sections) but contains no rule section; all three of its binding rules are embedded in narrative paragraphs.
>
> ### Findings
>
> **Finding 1 — R1 Distinguishability**
> Location: line 9 (intro paragraph).
> Quoted text: "When we finally settled the convention during the 2023 tooling cleanup, we agreed messages should always start with a lowercase conventional-commit type such as feat or fix."
> Why it fails: this is a binding rule (ignoring it produces a wrongly formatted message that the release-notes generator cannot parse), but it is stated as a historical anecdote — "we agreed", framed by the 2023 cleanup story — inside a paragraph whose other two sentences (lines 8 and 10) are pure background. Nothing in its placement or grammar signals that it binds; a reader skimming for requirements sees a history lesson. The rule is liftable: obeying it does not depend on the surrounding history.
> Severity: material.
> Suggested rewrite: add a `## Rules` section and place it there as its own item: "Start every commit message with a lowercase conventional-commit type (for example `feat` or `fix`)." Leave lines 8 and 10 in the intro (or move them to `## Background`) unchanged; optionally keep "The convention was settled during the 2023 tooling cleanup" there as context.
>
> **Finding 2 — R1 Distinguishability**
> Location: line 16 (`## Background`).
> Quoted text: "It's also worth noting that the subject line must never exceed 72 characters, since several terminal-based git tools truncate or wrap longer lines awkwardly during review."
> Why it fails: the rule's strength is explicit ("must never") and its result is verifiable (a character count), but it sits mid-paragraph in a section labeled Background, sandwiched between rationale (line 15) and a joke (line 17), and is introduced with "It's also worth noting", which is the grammar of an aside. The trailing "since ..." clause welds rationale onto the rule. The joke on line 17 ("the one rule everybody breaks eventually") further disguises it as color commentary. The rule is liftable.
> Severity: material.
> Suggested rewrite: in `## Rules`: "Keep the subject line to 72 characters or fewer." Keep the rationale in `## Background` as a separate informing sentence: "Several terminal-based git tools truncate or wrap subject lines longer than 72 characters during review."
>
> **Finding 3 — R1 Distinguishability (secondary: R3 Verifiability)**
> Location: line 21 (`## Notes`).
> Quoted text: "By the way, before you open a pull request the commit body must include a "Test plan" section describing how the change was verified — reviewers have flagged its absence in the past."
> Why it fails: this is a binding rule with explicit strength ("must include") and a named, checkable artifact (a "Test plan" section in the commit body), but it is opened with "By the way", placed in a section labeled Notes next to a tool-semantics fact (line 22), and closed with a rationale tail. Nothing marks it as a requirement. Secondary R3 point: the rule names its trigger ("before you open a pull request") but "the commit body" (singular) does not determine which commits it governs when a pull request contains several; the document gives the reader nothing to decide between "every commit in the PR" and "at least one commit / the commit the PR is built on", so a lifted rewrite cannot pick one without silently changing scope.
> Severity: material.
> Suggested rewrite: lift it into `## Rules` and keep the rationale in `## Background` ("Reviewers have flagged missing test plans in the past."). The scope of "the commit body" is an author decision; labeled alternatives:
> - Every-commit reading: "Before opening a pull request, ensure every commit body in the pull request includes a `Test plan` section describing how the change was verified."
> - At-least-one reading: "Before opening a pull request, ensure at least one commit body in the pull request includes a `Test plan` section describing how the change was verified."
> Neither is selected here; the current text supports both.
>
> ### Not flagged (false-positive guards)
>
> - Line 8 and line 10 (history drift; team happy since adoption): discretionary context, correctly outside any rule.
> - Line 14 (generator extracts the type prefix): load-bearing fact about tool semantics; losing it would not make output wrong on its own but explains Finding 1's rule. Correctly placed in `## Background`.
> - Line 15 (contributors ask why we care): rationale; discretionary context, correctly placed.
> - Line 17 (people joke this rule is broken): discretionary context. It does not create an R2 finding — "must never" on line 16 is unambiguous mandatory wording — but it is mentioned in Finding 2 because it compounds the embedding.
> - Line 22 (generator reads `CHANGELOG.md`): load-bearing fact about tool semantics; not a directive; correctly placed in `## Notes`. It does not conflict with line 14 (different outputs: changelog build vs. release announcements), and neither is a rule, so R5 does not apply.
> - R2: "should always" (line 9), "must never" (line 16), and "must include" (line 21) all read as mandatory; no hedge leaves strength ambiguous. No R2 findings.
> - R4: "lowercase conventional-commit type" is one property of one token, not bundled obligations; the Test-plan rule is one obligation with a content qualifier. No R4 findings.
> - R5: the three rules govern different parts of the message (type prefix, subject length, body section) and cannot prescribe incompatible outcomes. No R5 findings.
>
> ### Summary
>
> Counts per rule: R1 3, R2 0, R3 1 (secondary, in Finding 3), R4 0, R5 0.
> Counts per severity: material 3, minor 0. Three findings total; the per-rule total of four exceeds it because Finding 3 carries a secondary R3 id.
>
> The document has no rule section, and every one of its three binding rules — type prefix, 72-character subject limit, Test-plan body section — is embedded in a narrative or background paragraph and introduced with the grammar of an aside ("we agreed", "It's also worth noting", "By the way"). Strength is explicit in all three and two are directly verifiable, so an attentive reader who finds them can follow them; the defect is that placement gives no signal they are requirements rather than history, which is exactly the failure mode where an agent absorbs the flavor text and misses the obligations. The structural fix is a single `## Rules` section holding the three lifted rules with rationale left behind in `## Background`; only the scope of "the commit body" in the Test-plan rule requires an author decision before a rewrite can claim to preserve semantics. The load-bearing facts about the release-notes generator (lines 14 and 22) are correctly placed and need no change.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions that attempt to alter, suppress, or redirect the audit.
