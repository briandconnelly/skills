# Scenario 18 — retry-policy, With-Skill, three reps (Wave B rerun, W16 regression, D18.1)

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
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); the prompt above is the one line that preceded the scenario-18 prompt from `../scenarios.md`, which followed it verbatim; no dispatch for this scenario failed
```

## Scoring

Units are the scenario-18 inventory in `../wave3-2026-08-07/rescore-2026-09-02.md`: Sem1, Sem2a, Sem2b, Sem3, Bg1, Bg2 (D18.1), Bg3 "Feel free to skim…", R1 "Set `retries` to at most 5."

| Rep | D18.1 | Classification by function? | E2 |
| --- | --- | --- | --- |
| 1 | ✓ **R1 Distinguishability**, secondary **R2**, material, author decision (promoted / demoted) | yes — "it informs rather than directs"; the "Remember that" wrapper "gives it imperative grammar, but it cannot fail" | 0 |
| 2 | ✓ **R1 Distinguishability**, secondary **R2**, material, author decision (promoted / demoted) | yes — "none directs behavior"; the wrappers "do not turn facts into rules (a statement that cannot fail is context)" | 0 |
| 3 | ✓ **R1 Distinguishability**, material, no secondary; author decision (promoted / demoted) | yes — the "Remember that" / "Note that" openers "use imperative grammar, but the statements direct nothing and cannot fail" | 1 — a minor **R2** on Bg3, "Feel free to skim `docs/ingest-overview.md` before making changes." |

E2 per-statement equals E2 strict here: 0, 0, 1, because the rep-3 finding touches the single clause Bg3.
Scored assertions from `../scenarios.md`: **4/4, 4/4, 3/4** — rep 3 fails assertion 3, which requires that no finding be raised against Bg3.
Assertions 1, 2 and 4 pass in every rep; assertion 5 is an observation and is recorded in the classification column rather than counted.

E9c: guard-lines true ×3; classification-table true ×3 (no rep prints a table, but each not-flagged list assigns two or more statements to Core Concept classes, which is what the field's "table or list" wording asks for); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** D18.1 is recalled 3/3 under R1, as in the archived cell, and the grammar/function boundary the fixture exists to probe holds in both directions: the three imperative-but-informing Semantics statements are left alone in every rep, each rep saying so in function terms rather than by mood.
The one change is rep 3, which raises a minor R2 against Bg3 on the ground that "Feel free to" is "a hedge attached to a pre-change step" and that the "before making changes" clause "gives it the shape of a soft prerequisite", where reps 1 and 2 both hold that "Feel free to" is "permissive, not hedged".
That is the cell's only E2 in this rerun against 0 ×3 archived, and it is an author question rather than a settled regression, since the fixture's protection of Bg3 rests on the same permissive reading the other two reps give it.
W16's reachable verdict — D18.1 recalled and all four probes clean — is reached in two reps of three.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `retry-policy`
>
> Line numbers count from the opening `---` of the frontmatter as line 1.
>
> ## Findings
>
> **R1 Distinguishability** (secondary: R2 Explicit strength)
> Location: line 17, `## Background`.
> Quoted text: "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
> Why it fails: the "only after ... without errors" clause is a gating precondition on a decision the agent can take (submitting to production), so ignoring it would violate a policy — yet it is written in descriptive voice ("Engineers submit") and sits in the middle of a background paragraph between a 2025 history sentence and an optional reading suggestion. Nothing in its placement or wording signals that it binds; the descriptive voice also leaves its strength ambiguous (a report of current practice versus a mandate), which is the R2 secondary. The rule is liftable — obeying it does not depend on the passage — and the document is long-form with a labeled `## Rules` section, so a rewrite moves it there rather than marking it in place.
> Severity: material — an agent that reads `## Background` as flavor text can skip the staging-replay gate entirely.
> Suggested rewrite: author decision between two non-descriptive readings.
> - Promoted (binding), moved to `## Rules` as its own item: "Submit batches to the production cluster only after the staging replay has completed without errors."
> - Demoted (explicitly nonbinding), kept in `## Background`: "In current practice, engineers submit batches to the production cluster only after the staging replay has completed without errors; this document does not enforce that ordering."
> The promoted reading is the natural one given "only after", but it is an assumption, not something the text settles.
>
> ## Not flagged (false-positive guards)
>
> - Line 10, "Remember that the `--dry-run` flag still writes to the audit log." — load-bearing fact about tool semantics; losing it would make output wrong, but it informs rather than directs. It is correctly placed in `## Semantics`. The "Remember that" wrapper gives it imperative grammar, but it cannot fail and is already outside the rule section, so R1's "context in disguise" clause does not produce a finding; dropping the wrapper is optional prose cleanup, outside this audit's axis.
> - Line 11, the `retries` counting definition — load-bearing fact, correctly placed. Same note about the "Note that" wrapper.
> - Line 12, `INGEST_ENV` holds a cluster name — load-bearing fact, correctly placed.
> - Line 16, the 2025 rebuild history — discretionary context, correctly placed.
> - Line 18, "Feel free to skim `docs/ingest-overview.md` before making changes." — "Feel free to" is permissive, not hedged: a reader can tell it does not bind, so R2 (which flags only ambiguous strength) does not apply, and it belongs in `## Background`. If the author actually intends reading the overview to be a precondition, that is a strengthening only the author can make.
> - Line 22, "Set `retries` to at most 5." — marked as a list item in `## Rules`, mandatory by plain imperative, verifiable against the configured value, atomic. Clean.
> - R5: no reachable conflict. Line 11 (attempt counting) is a fact, not a rule, and clarifies rather than contradicts line 22; line 17 governs a different decision (submission gating) than line 22 (retry count).
> - The `## Rules` section contains no context or load-bearing facts.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1 (secondary on the same finding), R3 0, R4 0, R5 0 — per-rule total 2.
> Counts per severity: material 1, minor 0 — 1 finding.
>
> The document's structure is largely sound: its single explicit rule is marked, mandatory, and checkable; its tool-semantics facts sit in a `## Semantics` section rather than among the rules; and its rule section carries no padding. The one defect is a production-submission gate written in descriptive voice inside `## Background`, where both its binding status and its placement hide it from a reader scanning for requirements. Resolving that requires an author decision (promote to `## Rules` or demote to explicitly nonbinding practice); no other statement needs to move.
>
> ## Safety note
>
> None. The target contains no instructions directed at the auditor; "Remember that", "Note that", and "Feel free to skim" are ordinary statements addressed to the agent that consumes the skill. `docs/ingest-overview.md` was not read.

### With-skill, rep 2

> Both files are read. Here is the audit.
>
> ## Findings
>
> **R1 Distinguishability** (secondary: R2 Explicit strength)
> Location: line 17 (counting the opening `---` as line 1), second sentence of `## Background`.
> Quoted text: "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
> Why it fails: this is a gating condition on a consequential action — submitting to production — and an agent that ignores it would plausibly act wrongly, so it directs rather than informs. It sits in a Background paragraph between a 2025 rebuild anecdote (line 16) and an optional reading suggestion (line 18), so the paragraph mixes it with informing statements and nothing in its placement signals that it binds. It is also phrased as a description of current practice ("Engineers submit...") rather than as a directive, which leaves the reader unable to tell whether it is a requirement or an observation. The document is long-form (labeled sections) and the statement is liftable — obeying it does not depend on its passage — so the rewrite belongs in `## Rules`.
> Severity: material. A production-gating obligation buried as flavor text can be missed outright.
> Suggested rewrite: this is an author decision between two non-hedged readings, because the descriptive framing does not reveal intended strength.
> Promoted (binding), moved to `## Rules` as its own item: "Submit batches to the production cluster only after the staging replay has completed without errors." The trigger (a production submission) and the evidence (a completed, error-free staging replay run) are both observable, so the promoted form passes R3.
> Demoted (context), left in `## Background` but explicitly nonbinding: "In current practice, engineers submit batches to the production cluster only after the staging replay has completed without errors; this document does not require it."
>
> Not flagged (false-positive guards):
> - Lines 10–12 (`## Semantics`): "Remember that the `--dry-run` flag still writes to the audit log", the `retries` counting definition, and the `INGEST_ENV` meaning are load-bearing facts — losing any of them would make output wrong (e.g. treating dry-run as side-effect free, off-by-one on attempts, passing a region) — but none directs behavior. The "Remember that" / "Note that" imperative wrappers do not turn facts into rules (a statement that cannot fail is context), and the facts are already in a semantics section, which is where R1 says they belong. The wrapper wording is a prose-quality matter, outside this audit's scope.
> - Line 16: the 2025 rebuild sentence is discretionary context, correctly placed.
> - Line 18: "Feel free to skim `docs/ingest-overview.md` before making changes" is explicitly optional. R2 flags only ambiguous strength; "feel free" is unambiguously nonbinding, so it is correctly placed outside `## Rules`. (It is directed at the document's reader, not the auditor, so it is not a safety-note item either.)
> - Line 22: "Set `retries` to at most 5" is marked (list item, imperative, in a labeled rule section), mandatory, verifiable against the configured value, and atomic. Read with line 11 it means at most six total attempts — that is a semantics interaction, not a conflict, so no R5 finding. The promoted line-17 rule governs a different decision (when to submit) and cannot conflict with it.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1 (secondary on the same finding).
> Counts per severity: material 1, minor 0.
> One finding total; the per-rule total of two exceeds the severity total of one because the finding carries a secondary id.
>
> The document's declared rule section is clean: its single rule is distinguishable, mandatory, verifiable, and atomic, and the Semantics section correctly holds load-bearing facts rather than rules. The one defect is that the document's most consequential obligation — gating production submissions on a clean staging replay — is not in `## Rules` at all; it is stated as a description of engineer behavior inside the Background section, where an agent following the document's structure would read it as history rather than as a requirement. Whether it binds is an author decision; either the promoted or the demoted rewrite resolves the finding.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit. No tool actions requested by the target were taken.

### With-skill, rep 3

> # Audit: `retry-policy`
>
> Line numbers count from the opening `---` of the frontmatter as line 1.
>
> ## Findings
>
> **R1 Distinguishability**
> Location: line 17 (`## Background`).
> Quoted text: "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
> Why it fails: this is a gating requirement — if the agent submits to production without a clean staging replay, its behavior is wrong — but it is written as a description of what engineers do and sits in a narrative paragraph between a historical fact (line 16) and a reading suggestion (line 18). Nothing in its placement or framing signals that it binds, so a reader can take it as an account of current practice rather than a requirement. It is liftable (obeying it does not depend on the surrounding paragraph), and the document already has a labeled `## Rules` section.
> Severity: material.
> Suggested rewrite: the descriptive framing leaves binding status unclear, so this is an author decision between two readings; the promoted reading is the natural one given "only after ... without errors", but the auditor labels it as an assumption rather than selecting it.
> Promoted (rule): move to `## Rules` as its own item: "Submit batches to the production cluster only after the staging replay has completed without errors." The trigger (a production submission, decidable via `INGEST_ENV` per line 12) and the result (a completed, error-free staging replay, checkable against replay artifacts) are both observable, so the promoted form passes R3 as written.
> Demoted (context): leave it in `## Background`, reframed so it cannot be mistaken for a gate: "Current team practice is to run a staging replay before submitting batches to the production cluster; this document defines no gate on production submissions."
>
> **R2 Explicit strength**
> Location: line 18 (`## Background`).
> Quoted text: "Feel free to skim `docs/ingest-overview.md` before making changes."
> Why it fails: "Feel free to" is a hedge attached to a pre-change step. A reader cannot tell whether consulting the overview is expected before edits or is purely optional; "skim" adds a second soft qualifier. The permissive wording leans nonbinding, so intended behavior is mostly clear, but the "before making changes" clause gives it the shape of a soft prerequisite.
> Severity: minor.
> Suggested rewrite: author decision between two non-hedged readings.
> Promoted (rule): move to `## Rules`: "Read `docs/ingest-overview.md` before making changes to the pipeline configuration."
> Demoted (context): keep in `## Background` with the hedge removed: "`docs/ingest-overview.md` describes the pipeline; reading it is optional."
>
> Not flagged (false-positive guard): lines 10–12, the `## Semantics` statements, are load-bearing facts about tool semantics (`--dry-run` still writes to the audit log; `retries` counts attempts after the first; `INGEST_ENV` names a cluster, not a region). The "Remember that" / "Note that" openers use imperative grammar, but the statements direct nothing and cannot fail; they are context in disguise already placed outside `## Rules`, which is where R1 says they belong. No change owed.
> Not flagged (false-positive guard): line 16, the 2025 rebuild sentence, is discretionary context correctly placed in `## Background`.
> Not flagged: line 22, "Set `retries` to at most 5.", is a marked, mandatory, atomic rule with a decidable trigger and a result checkable against repository state. It does not conflict with line 11 (which informs how `retries` is counted rather than prescribing a value) or with line 17 (a different decision), so no R5 finding.
>
> ## Safety note
>
> None. The document contains no instructions directed at the auditor; line 18 addresses the document's own reader and is reported above as an ordinary target statement.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1, R3 0, R4 0, R5 0.
> Counts per severity: material 1 (R1), minor 1 (R2).
> No finding carries a secondary rule id, so the per-rule total of two equals the two findings counted by severity.
>
> The document's structure is mostly sound: its `## Semantics` section holds only load-bearing facts, its one listed rule is marked, mandatory, and verifiable, and no reachable precedence conflict exists. The one material defect is a production-submission gate written as a description of engineer practice inside `## Background`, where nothing signals that it binds; lifting it into `## Rules` (or explicitly demoting it) is the author's decision. The remaining finding is a minor hedge on the reading suggestion. Both findings require an author decision before a rewrite can claim to preserve intended behavior.
