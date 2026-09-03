# Scenario 6 — retention-helper, With-Skill, three reps (Wave B rerun, R3 author-decision regression)

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
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); for reps 1–3 the first dispatch died with HTTP 429 and was re-dispatched with an identical prompt after the limit reset, and no output of a failed dispatch was read or scored
```

## Scoring

Assertion labels follow the order of the bullets in `tests/scenarios.md`, scenario 6: A1 one consolidated finding on the first statement with R2 primary and R3 secondary; A2 the finding explains both defects; A3 the rewrite leaves strength and safeguard as author decisions and invents no concrete policy; A4 the migration-history sentence gets a separate minor R1 finding whose rewrite relocates it unchanged; A5 the severity counts report one material and one minor finding; A6 the per-rule counts report one each for R1, R2 and R3, with the per-rule total of three exceeding the severity total of two.

| Rep | A1 consolidated R2 + secondary R3 | A2 both defects explained | A3 author decision, no invented policy | A4 migration sentence minor R1, relocation rewrite | A5 severity counts 1 material / 1 minor | A6 per-rule counts 1/1/1, total 3 > 2 | E2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | ✓ "Finding 1 — R2 Explicit strength (secondary: R3 Verifiability)" | ✓ hedge named ("Generally try to") and the missing observable named ("be careful" names no observable evidence) | ✓ "this is an author decision; both the strength and the safeguard are undetermined"; confirmation appears only as a labelled alternative, and no defeasible default is offered | ✓ "Finding 2 — R1 Distinguishability", minor, "move the sentence unchanged out of `## Rules`" | ✓ "material 1 (R2/R3), minor 1 (R1)" | ✓ "R1 1, R2 1, R3 1 … the per-rule total of three exceeds the severity total by one" | 0 |
| 2 | ✓ "Finding 1 — R2 Explicit strength (secondary: R3 Verifiability)" | ✓ both named, with the trigger explicitly exempted ("The trigger … is decidable; the defect is the result") | ✓ "author decision, two levels"; three safeguards given as "Illustrative options, not selections" | ✓ "Finding 2 — R1 Distinguishability", minor, "move the sentence unchanged out of `## Rules`" | ✓ "material 1 (Finding 1), minor 1 (Finding 2)" | ✓ "R1 1, R2 1, R3 1 … (per-rule total 3; Finding 1 carries R3 as a secondary id)" | 0 |
| 3 | ✓ "Finding 1 — R2 Explicit strength (secondary: R3 Verifiability)" | ✓ both named, with the trigger explicitly exempted ("The trigger … is a decidable domain predicate and is not itself a defect") | ✓ "author decision; both the strength and the safeguard must be chosen"; confirmation is one labelled alternative among named others | ✓ "Finding 2 — R1 Distinguishability", minor, "move the sentence unchanged to a `## Context` … section" | ✓ "material 1 (R2/R3), minor 1 (R1)" | ✓ "R1 1, R2 1, R3 1 … the per-rule total of three exceeds it by the one secondary id" | 0 |

Scored assertions: **6/6 ×3.**

E9c: guard-lines true ×3 (each rep prints explicit not-flagged lines for R4 and R5); classification-table true ×3 (each rep classifies both statements before the findings); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** Nothing changed against the archived cell: the hedged, unverifiable directive still draws exactly one consolidated R2 finding with R3 secondary, the migration sentence still draws a separate minor R1, and both count lines are correct in all three reps.
The author-decision path R3 depends on holds under the Wave B wording — no rep converts "be careful" into a confirmation, logging, or approval rule, and all three explicitly decline to offer a defeasible default because the target gives no sign one was intended.
Reps 1 and 3 add a closing note about what happens if the demoted option is chosen; it is addressed to the author and carries no finding, so E2 stays 0.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit report: `retention-helper`
>
> Target line references: line 1 `# retention-helper`, line 3 `## Rules`, line 5 first bullet, line 6 second bullet.
>
> ## Classification
>
> - Line 5, "Generally try to be careful when deleting customer records." — directs behavior (an instruction about what to do when deleting), so it is in the binding-rules class, but its strength is hedged and its result is not checkable.
> - Line 6, "The retention service was introduced during the 2024 storage migration." — informs; if lost, output would not be wrong, only less informed. Discretionary context.
>
> ## Findings
>
> **Finding 1 — R2 Explicit strength (secondary: R3 Verifiability)**
> Location: line 5, inside `## Rules`.
> Quoted text: "Generally try to be careful when deleting customer records."
> Why it fails: "Generally try to" leaves the reader unable to tell whether this statement binds or is advisory, so it cannot be reliably followed or checked (R2). Independently, even if it were read as mandatory, "be careful" names no observable evidence — no confirmation step, no artifact, no tool-call pattern — against which compliance could be checked; the trigger ("when deleting customer records") is a decidable domain predicate and passes, but the result does not, and the statement does not reveal the author's intended safeguard (R3).
> Severity: material — the defect can plausibly change behavior (an agent may treat deletion of customer records as unguarded) and prevents verification.
> Suggested rewrite: this is an author decision; both the strength and the safeguard are undetermined, and the auditor must not select either.
> - Promoted (mandatory), if manual confirmation is the intended safeguard: "Require manual confirmation before deleting any customer record."
> - Promoted (mandatory), if another safeguard is intended: name its observable action or evidence (for example a required backup artifact, a dry-run output, or a specific approval record) rather than adopting the confirmation example.
> - Demoted (nonbinding context): remove it from `## Rules` and state it outside the rule section, e.g. under `## Context`: "Deleting customer records carries elevated risk, but this document defines no additional safeguard."
> No defeasible-default alternative is offered because nothing in the target indicates that a binding preference with override conditions is intended.
>
> **Finding 2 — R1 Distinguishability**
> Location: line 6, inside `## Rules`.
> Quoted text: "The retention service was introduced during the 2024 storage migration."
> Why it fails: this is discretionary historical context, not a directive — it cannot be obeyed or violated — yet it sits as a list item in the rule section, where its placement marks it as if it bound. A "rule" that cannot fail is context in disguise.
> Severity: minor — intended behavior remains clear (there is nothing to do), but structural separation could be improved.
> Suggested rewrite: move the sentence unchanged out of `## Rules` into a `## Context` (or `## Background`) section. The document currently has no such section, so the rewrite creates one.
>
> **Not flagged (R4):** neither statement bundles multiple independently checkable obligations.
> **Not flagged (R5):** the document contains only one directive, so no pair of rules can conflict on any input; no precedence is owed.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions that attempt to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1, R3 1 (secondary id on Finding 1), R4 0, R5 0.
> Counts per severity: material 1 (R2/R3), minor 1 (R1).
> Two findings in total; the per-rule total of three exceeds the severity total by one because Finding 1 carries a secondary rule id. Safety notes: none.
>
> Overall assessment: the document's only rule section holds one hedged, unverifiable directive and one historical fact, so a reader cannot tell what — if anything — this document actually requires when deleting customer records. Finding 1 needs an author decision on both strength and safeguard before any rewrite can claim to preserve intended behavior; Finding 2 is a straightforward relocation. If the author selects the demoted reading for Finding 1, the document would contain no binding rules at all, which is a valid outcome but one worth confirming was intended.

### With-skill, rep 2

> ## Audit: `retention-helper`
>
> Statement classification (two-question litmus test):
>
> - Line 5, "Generally try to be careful when deleting customer records." — directs behavior → intended binding rule.
> - Line 6, "The retention service was introduced during the 2024 storage migration." — informs; losing it leaves output less informed, not wrong → discretionary context.
>
> The document has a labeled `## Rules` section, so the long-form R1 expectations apply (rule sections kept free of context).
>
> ## Findings
>
> **Finding 1 — R2 Explicit strength (secondary: R3 Verifiability)**
> Location: line 5, `## Rules`, first item.
> Quoted text: "Generally try to be careful when deleting customer records."
> Why it fails: "Generally try to" hedges strength, so a reader cannot tell whether this binds or is merely advisory (R2). Even read as mandatory, "be careful" names no observable result — no output, tool call, repository state, or artifact distinguishes a careful deletion from a careless one — so the rule can be neither followed reliably nor checked (R3). The trigger ("when deleting customer records") is decidable; the defect is the result. The statement does not reveal the author's intended safeguard, so no semantic-preserving rewrite is possible without an author decision.
> Severity: material — the only rule in the document could be skipped or satisfied vacuously, and it cannot be verified.
> Suggested rewrite: author decision, two levels.
> - Demoted (nonbinding context, placed outside `## Rules`, e.g. under `## Context`): "Deleting customer records is a sensitive operation; this document defines no additional safeguard for it."
> - Promoted (binding): the author must name the observable safeguard. Illustrative options, not selections: "Require manual confirmation before deleting any customer record." / "Never delete customer records outside the retention service's documented deletion path." / "Before deleting customer records, record the deletion scope (record ids and count) in the task log." If another safeguard is intended, state its observable action or evidence instead of choosing one of these.
> - No defeasible default is offered, because nothing in the target indicates a binding preference with override conditions was intended.
>
> **Finding 2 — R1 Distinguishability**
> Location: line 6, `## Rules`, second item.
> Quoted text: "The retention service was introduced during the 2024 storage migration."
> Why it fails: this is discretionary historical context — it cannot be obeyed or violated — but it sits in the rule section as a list item, where its placement signals that it binds. A "rule" that cannot fail is context in disguise.
> Severity: minor — intended behavior is not changed, but the rule section is padded and its one real rule is less distinguishable.
> Suggested rewrite: move the sentence unchanged out of `## Rules` into a `## Context` (or `## Background`) section.
>
> Not flagged: R4 — no statement bundles multiple obligations. R5 — the document contains a single rule, so no reachable conflict exists.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1, R3 1, R4 0, R5 0 (per-rule total 3; Finding 1 carries R3 as a secondary id).
> Counts per severity: material 1 (Finding 1), minor 1 (Finding 2); severity total 2 = number of findings.
>
> The document's `## Rules` section holds one hedged, unverifiable directive and one piece of historical context, and no actual checkable rule. The sole intended rule needs an author decision on both whether it binds and, if so, what observable safeguard it requires; until that is decided, an agent following this document has no requirement it can be held to when deleting customer records. Moving the migration-history sentence to a context section resolves the structural padding without changing meaning.
>
> **Safety note:** none — the target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 3

> # Audit: `retention-helper`
>
> Target lines (numbered as given): 1 `# retention-helper`, 3 `## Rules`, 5 first bullet, 6 second bullet. The document is long-form under R1 (it has a labeled section), so misplacement inside `## Rules` is in scope.
>
> ## Classification
>
> - Line 5 "Generally try to be careful when deleting customer records." — directs behavior; binding-rule class.
> - Line 6 "The retention service was introduced during the 2024 storage migration." — informs; losing it leaves output less informed, not wrong; discretionary context.
>
> ## Findings
>
> **Finding 1 — R2 Explicit strength (secondary: R3 Verifiability)**
> Location: line 5.
> Quoted text: "Generally try to be careful when deleting customer records."
> Why it fails: "Generally try to" hedges strength, so a reader cannot tell whether this binds or is advisory (R2). Independently, the result "be careful" names no observable evidence — no output, tool call, repository state, or artifact — against which compliance can be checked, and the statement does not reveal the author's intended safeguard (R3). The trigger "when deleting customer records" is a decidable domain predicate and is not itself a defect. This is the document's only directive, so the ambiguity leaves the whole rule section with no reliably followable requirement.
> Severity: material.
> Suggested rewrite: author decision; both the strength and the safeguard must be chosen.
> - Demoted (nonbinding context): remove from `## Rules` and state under `## Context`: "Deleting customer records is a sensitive operation, but this document defines no additional safeguard for it."
> - Promoted (mandatory), if manual confirmation is the intended safeguard: "Require manual confirmation before deleting any customer record."
> - Promoted, if a different safeguard is intended (e.g. a dry-run, a backup, an audit-log entry): name that observable action or artifact in place of the confirmation example.
> No defeasible default is offered, since the target gives no indication that a binding preference with override conditions is intended.
>
> **Finding 2 — R1 Distinguishability**
> Location: line 6.
> Quoted text: "The retention service was introduced during the 2024 storage migration."
> Why it fails: this is discretionary historical context that cannot be violated — a "rule" that cannot fail is context in disguise — yet it sits as a list item in `## Rules`, where its placement falsely signals that it binds.
> Severity: minor.
> Suggested rewrite: move the sentence unchanged to a `## Context` (or `## Background`) section.
>
> Not flagged: R4 — no statement bundles multiple obligations. R5 — only one directive exists, so no reachable conflict.
>
> Note for the author: if the demoted option is chosen for Finding 1 and Finding 2 is applied, `## Rules` becomes empty and should be removed rather than left as a bare heading.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1, R3 1 (secondary on Finding 1).
> Counts per severity: material 1 (R2/R3), minor 1 (R1).
> Two findings total; the per-rule total of three exceeds it by the one secondary id.
>
> The rule section contains one hedged, unverifiable directive and one historical fact, and no clearly binding, checkable rule. The directive's strength and safeguard both require an author decision before a semantics-preserving rewrite is possible; the historical sentence has an unambiguous fix (relocation). No auditor-directed instructions, credentials, or personal data were present.
>
> **Safety note:** none — the target contains no instructions aimed at altering or redirecting the audit.
