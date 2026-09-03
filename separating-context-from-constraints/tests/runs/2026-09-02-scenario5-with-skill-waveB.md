# Scenario 5 — changelog-entry-writer, With-Skill, three reps (Wave B rerun, R3 regression)

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
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); the first dispatch of rep 3 died with HTTP 429 and was re-dispatched with an identical prompt after the limit reset, and no output of a failed dispatch was read or scored
```

## Scoring

Assertion labels follow the order of the bullets in `tests/scenarios.md`, scenario 5: A1 an explicit clean outcome for R1–R5; A2 no manufactured minor findings against rules 1–5 or the context sentences; A3 no R2 finding on rule 6's "by default"; A4 no R5 finding, since rule 7 states precedence.
The rule-7 column records the statement this cell was added to watch: R3's trigger clause could reach "multiple independent user-visible changes" if read too widely.

| Rep | A1 clean outcome | A2 no manufactured findings | A3 "by default" not an R2 hedge | A4 no R5 finding | Rule 7 "multiple independent user-visible changes" not flagged | E2 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ✓ "Clean — no findings." | ✓ counts per rule all 0; rules 1–5 and both context sentences classified as correctly placed | ✓ quoting rule 6: "by default" signals strength explicitly, and the override condition is supplied by rule 7 | ✓ "precedence over rule 6 is stated explicitly, satisfying R5" | ✓ "a domain predicate the reader can decide from the pull request" | 0 |
| 2 | ✓ "**Clean — no findings.**" | ✓ counts per rule all 0; classification table marks every statement's placement correct | ✓ quoting rule 6: an explicit default ("by default") whose override condition is stated in rule 7 | ✓ "The only reachable conflict (rule 6 vs rule 7 on a multi-change PR) has explicit precedence stated in rule 7." | ✓ "ordinary domain predicates decidable from the PR, and rule 7 bounds its judgment with a quantity" | 0 |
| 3 | ✓ "Clean — no findings." | ✓ counts per rule all 0; the redundancy in rule 7 is recorded as an out-of-scope observation, not a finding | ✓ quoting rule 6: "by default", which explicitly marks it defeasible, and rule 7 supplies the override condition | ✓ "the only reachable conflict, rules 6 vs 7 …, has explicit precedence" | ✓ "ordinary domain predicates decidable from the PR" | 0 |

Scored assertions: **4/4 ×3.**

E9c: guard-lines true ×3; classification-table true ×3 (rep 2 prints a classification table, reps 1 and 3 a classification list); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** The cell is clean ×3, as expected, and the watched statement holds: no rep raises R3 against rule 7's "multiple independent user-visible changes".
All three reps invoke the domain-predicate reading, two of them verbatim on rule 7, so the clean verdict is attributable to the wording under test rather than to the arms not looking.
Rep 3's redundancy remark and rep 2's zero-user-visible-change coverage gap are both stated as observations outside R1–R5 and carry no finding, so E2 stays 0.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `changelog-entry-writer`
>
> Audited against R1–R5 as defined in the wave-3 SKILL.md, using the two-question litmus test on every statement.
>
> ## Classification
>
> **`## Context`**
> - "Changelog entries are read by users deciding whether to upgrade, not by contributors reviewing code." — informs; discretionary context (rationale for rules 2–5). Correctly placed outside `## Rules`.
> - "This skill is invoked once per merged pull request, after CI has passed." — informs; environment fact about when the caller invokes the skill. It is declarative, not a directive the executing agent could violate, so it is not an embedded rule. Correctly placed.
>
> **`## Rules`**
> - Rule 1 — binding, mandatory, verifiable against output (tag present, in the four-item set, exactly one). Atomic.
> - Rule 2 — binding, mandatory, verifiable against a named location (the first sentence). "User-visible effect" is an ordinary domain predicate; the document bounds the judgment with a named artifact, so it is not an R3 finding.
> - Rules 3, 4, 5 — binding, mandatory ("Never"), each verifiable against entry text, each stated separately.
> - Rule 6 — binding default; "by default" signals strength explicitly, and the override condition is supplied by rule 7 with an explicit cross-reference. Not ambiguous under R2.
> - Rule 7 — condition–action–precedence sharing one trigger, which R4 allows as a single unit; precedence over rule 6 is stated explicitly, satisfying R5. "Independent user-visible change" is a domain predicate the reader can decide from the pull request.
>
> ## Findings
>
> Clean — no findings.
>
> ## Not flagged (false-positive guards)
>
> - Rule 3 enumerates three identifier kinds (function, class, variable) under one prohibition. This is one obligation with an enumerated object, like rule 1's tag set, not three bundled obligations; the author already split the distinct prohibitions into rules 3, 4, and 5. Not an R4 finding.
> - Rule 6 does not restate its override condition inline; rule 7 carries it and names rule 6. The document as a whole makes the strength explicit, which is what R2 requires. Not a finding.
> - Rule 7's precedence clause repeats its own trigger ("If a pull request bundles multiple independent user-visible changes … whenever a pull request contains more than one independent user-visible change"). That is redundancy, a prose-quality matter outside this audit's scope (Non-Goals), and the redundancy does not obscure which rule wins.
> - Rules 2 and 3 share the field "entry text" and could seem to pull against each other when the user-visible effect concerns a named public function. They prescribe outcomes for different decisions (what the first sentence conveys vs. which vocabulary is forbidden) and both can be satisfied by describing the capability rather than the identifier, so this is not a reachable R5 conflict.
> - Rules 1 and 7 do not conflict: when rule 7 yields several entries, each entry still carries exactly one tag.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
>
> This document separates context from constraints cleanly. Both context statements are informing statements placed in a labeled context section; all seven rules are numbered list items with imperative grammar, explicit strength (five mandatory "never"/imperative rules, one stated default, one exception with named precedence), decidable triggers, and results checkable against the entry text. No rule section item is context in disguise, no compound obligations need splitting, and the one realistic rule pair that could conflict (6 vs. 7) states its precedence explicitly.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 2

> # Audit: `changelog-entry-writer`
>
> Audited against R1–R5 from the wave-3 SKILL.md, using the finding format there and the worked example in `references/example-audit.md` as the pattern. Files read: those two only.
>
> ## Classification
>
> | Location | Statement | Class | Placement |
> |---|---|---|---|
> | Frontmatter `description` | "Use when writing a changelog entry for a merged pull request." | Binding trigger (compact, inline) | Correct |
> | Context, sentence 1 | "Changelog entries are read by users deciding whether to upgrade, not by contributors reviewing code." | Discretionary context (audience rationale) | Correct — outside `## Rules` |
> | Context, sentence 2 | "This skill is invoked once per merged pull request, after CI has passed." | Load-bearing fact (environment / invocation semantics) | Correct — outside `## Rules` |
> | Rules 1–5 | Tag set; first-sentence effect; no identifiers; no ticket numbers; no file paths | Binding, mandatory | Correct — listed, imperative, unhedged |
> | Rule 6 | "…one changelog entry per pull request by default." | Binding, explicit default | Correct |
> | Rule 7 | "If a pull request bundles multiple independent user-visible changes, write one entry per change instead; this rule takes precedence over rule 6…" | Binding, condition–action with explicit precedence | Correct |
>
> ## Findings
>
> **Clean — no findings.**
>
> Rules checked and passed:
>
> - **R1** — Every rule is a numbered list item in a labeled `## Rules` section; nothing binding is embedded in the `## Context` paragraph, and nothing in `## Rules` is context or a fact. Both context sentences inform rather than direct.
> - **R2** — Rules 1–5 use mandatory wording ("exactly one", "never"). Rule 6 is an explicit default ("by default") whose override condition is stated in rule 7. No hedges.
> - **R3** — Each rule has a decidable trigger (the entry / the entry text / the pull request) and a result checkable against the produced entry. "User-visible effect" and "independent user-visible changes" are ordinary domain predicates decidable from the PR, and rule 7 bounds its judgment with a quantity ("more than one").
> - **R4** — Rule 3 names three identifier kinds under one prohibition with one trigger; that is a single obligation (no code identifiers), not a bundle of independently checkable ones, so it is not flagged. Rules 6 and 7 are already split into default and exception.
> - **R5** — The only reachable conflict (rule 6 vs rule 7 on a multi-change PR) has explicit precedence stated in rule 7.
>
> Not flagged (false-positive guards):
>
> - Context sentence 2 could be misread as a directive ("invoked once per merged pull request"), but it describes when the skill runs, not what the agent must do; it is a load-bearing environment fact and belongs where it is.
> - Rule 7's trailing precedence clause is redundant with "instead", but it is a directive that R5 asks for, not discretionary padding, and redundancy is a prose-quality matter outside this audit's scope.
> - A PR with zero user-visible changes leaves rule 2 unsatisfiable while rule 6 still requires an entry. This is a coverage gap, not an R5 conflict — the two rules do not prescribe incompatible outcomes for the same decision — and the Context section's "invoked once per merged pull request" suggests the author assumes every invocation has a user-visible change. Noted for the author; not a finding under R1–R5.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (reported separately, excluded from counts).
>
> This document already separates context from constraints cleanly: the two informing statements sit in a labeled `## Context` section, all seven binding rules sit as list items in a labeled `## Rules` section with explicit mandatory or default strength, each rule is checkable against the produced entry, obligations are atomic, and the one realistic rule conflict carries stated precedence. No rewrite is owed.

### With-skill, rep 3

> **Audit: `changelog-entry-writer`** (per the skill at the scratchpad path; I read only `SKILL.md` and its one referenced file, `references/example-audit.md`; no edits made).
>
> ## Classification
>
> - Context, sentence 1 ("read by users deciding whether to upgrade…") — informs; discretionary context (rationale for rules 2–5). Correctly placed outside `## Rules`.
> - Context, sentence 2 ("invoked once per merged pull request, after CI has passed") — informs; environment detail (load-bearing fact). It describes when the skill runs, not what the agent must do, so it is not a rule in disguise. Correctly placed.
> - Rules 1–7 — all direct behavior; all are list items with imperative or explicit mandatory/default wording.
>
> ## Findings
>
> Clean — no findings.
>
> Not-flagged guards (each checked, each passes):
>
> - **R1**: every rule is its own numbered item; the rule section contains no facts or rationale; the context section contains no directives.
> - **R2**: rules 1–5 and 7 use unhedged imperatives/"never". Rule 6 says "by default", which explicitly marks it defeasible, and rule 7 supplies the override condition. Defaults with stated overrides are legitimate rules, and no hedge ("generally", "try to") appears anywhere.
> - **R3**: every rule is checkable against the entry text (tag value, first sentence, absence of identifiers/ticket numbers/paths, entry count). "User-visible effect" and "independent user-visible changes" take judgment, but they are ordinary domain predicates decidable from the PR, and rule 2 bounds its judgment with a named artifact (the first sentence).
> - **R4**: rule 3's "function, class, or variable" is one prohibition with a disjunctive object (code identifiers), not three bundled actions. Rule 7's precedence clause shares rule 7's trigger, which R4 permits as a single unit.
> - **R5**: the only reachable conflict, rules 6 vs 7 (a PR with several independent changes), has explicit precedence. Rules 2 vs 3 do not conflict: a compliant entry can state the effect without naming an identifier, so they compose rather than prescribe incompatible outcomes.
>
> One observation outside the audit's scope (prose quality is a non-goal, so not a finding): rule 7's precedence clause restates its own trigger verbatim ("whenever a pull request contains more than one independent user-visible change" is the same condition as "bundles multiple independent user-visible changes"). It is redundant, not ambiguous.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
>
> The document already separates its two informing statements into a context section and its seven directing statements into a numbered rule section; every rule is marked, unhedged, checkable against the entry text, atomic, and the one realistic conflict (one entry per PR vs. one per change) carries explicit precedence. No rewrite is warranted.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
