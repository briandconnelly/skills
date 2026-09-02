# Scenario 18 — retry-policy, With-Skill, three reps (wave 3, W16)

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under `../wave3-2026-08-07/preregistration.md`; tool calls and sensitive-string counts extracted by script
Notes: every arm made exactly two tool calls (script); every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Scoring

| Rep | D18.1 | E3 on D18.1 | Probes criticized | E2 | Classification stated? by |
| --- | --- | --- | --- | --- | --- |
| 1 | ✓ R1 material (+R2) | preserved (promoted / demoted, author decision) | none — all four in the not-flagged list ("informs rather than directs"; "'Feel free to' resolves the strength question") | 0 | yes — by function |
| 2 | ✓ R1 material (+R2) | preserved | none | 0 | yes — by function |
| 3 | ✓ R1 material (+R2) | preserved | none | 0 | yes — by function ("the section label carries the structural signal") |

Standing assertions: 1 ✓ ×3; 2 ✓ ×3; 3 ✓ ×3; 4 ✓ ×3 — **4/4 ×3**; observation recorded (function, all three).
**Reachable verdict reached:** D18.1 recalled and all four probes clean in every rep. `SKILL.md:67` and the litmus test at `:20-24` stand as written; W16 closes with the boundary confirmed. The gap between arms is the sharpest in the wave: E2 0/0/0 against 4/3/4 on a fixture built so that sorting by grammar fails in both directions.

E9c: guard-lines true ×3; classification-table false ×3 (not-flagged lists, no table); negative-safety-note true ×3.
Contract adherence: 3/3. E6: unique (line convention stated).

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit report: `retry-policy`
>
> Line numbers count from the opening `---` of the document as line 1.
>
> ## Findings
>
> **R1 Distinguishability** (secondary: R2 Explicit strength)
> Location: line 17, `## Background`.
> Quoted text: "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
> Why it fails: this is a directive-shaped precondition on a production action ("only after ... without errors"), but it sits between a sentence of pipeline history and an optional reading suggestion, with nothing in its placement marking it as binding. It is also phrased descriptively (what engineers do) rather than as an instruction, so a reader cannot tell whether it is a requirement this skill imposes or an observation about team practice. If it binds, an agent that reads `## Background` as flavor text will submit to production without a clean staging replay.
> Severity: material.
> Suggested rewrite: author decision between two readings.
> Promoted (binding): move to `## Rules` as its own item: "Submit batches to the production cluster only after the staging replay has completed without errors." (Verifiable against process artifacts — the staging replay result preceding the production submission.)
> Demoted (context): keep it in `## Background`, marked explicitly nonbinding: "Current team practice is to submit batches to production only after the staging replay completes without errors; this skill does not enforce that."
>
> ## Not flagged (false-positive guards)
>
> - Lines 10–12 (`## Semantics`): the `--dry-run` audit-log behavior, the `retries` off-by-one semantics, and the `INGEST_ENV` meaning are load-bearing facts about tool semantics. Losing any would make output wrong, but none directs behavior, and they are correctly kept outside `## Rules`. The "Remember that" / "Note that" framing is emphasis on facts, not a rule in disguise.
> - Line 16: the 2025 rebuild history is discretionary context, correctly placed in `## Background`.
> - Line 18: "Feel free to skim `docs/ingest-overview.md`..." is explicitly optional. "Feel free to" resolves the strength question (nonbinding) rather than leaving it ambiguous, so it is not an R2 hedge; it is a reading pointer correctly placed outside `## Rules`.
> - Line 22: "Set `retries` to at most 5." is imperative (mandatory), atomic, and verifiable against the configured value. Clean.
> - R5: the only rule in `## Rules` and the line-17 precondition govern different decisions (a config value vs. submission ordering); no reachable conflict.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1 (secondary), R3 0, R4 0, R5 0. Per-rule total 2.
> Counts per severity: material 1, minor 0. Finding total 1.
>
> This is a short, mostly well-separated document: tool semantics live in a dedicated section, history is confined to background, and the single stated rule is imperative, atomic, and checkable. The one defect is a production-safety precondition written as a descriptive sentence inside `## Background`, where nothing signals that it binds; whether it is a requirement or an account of team practice is an author decision, and the rewrite should not be finalized until that is settled.

### With-skill, rep 2

> ## Audit: `retry-policy`
>
> Line numbers count the opening frontmatter `---` as line 1.
>
> ### Findings
>
> **R1 Distinguishability** (secondary: R2 Explicit strength)
> Location: line 17, `## Background`.
> Quoted text: "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
> Why it fails: this is a gating condition on a consequential action — if the agent ignores it, it can submit a batch to production without a clean staging replay, which is wrong behavior. It is placed in `## Background` between a 2025 rebuild anecdote and an optional reading pointer, and nothing in its placement signals that it binds; it reads as a description of team practice. The descriptive framing ("Engineers submit...") also leaves strength ambiguous: it could be a statement of how the human workflow currently operates (context) or a requirement the agent must satisfy (rule). Note the "only after" wording is checkable — the promoted form would be verifiable against process artifacts (staging replay result preceding the production submission), so R3 is not at issue.
> Severity: material.
> Suggested rewrite: author decision between two readings; the auditor does not select one.
> Promoted (binding rule): move to `## Rules` as its own item: "Submit batches to the production cluster only after the staging replay has completed without errors."
> Demoted (nonbinding context): leave it in `## Background`, reworded so it cannot be mistaken for a directive: "Current team practice is to submit batches to the production cluster after a clean staging replay; this document does not require it."
>
> ### Not flagged (false-positive guards)
>
> - Lines 10–12 (`## Semantics`): "Remember that the `--dry-run` flag still writes to the audit log", "Note that `retries` counts attempts after the first...", and the `INGEST_ENV` sentence are load-bearing facts about tool and variable semantics. Despite the "Remember that" / "Note that" framing, they inform rather than direct behavior; losing any of them would make output wrong (e.g. assuming dry-run is side-effect-free, or off-by-one on attempt counts). They belong in a semantics section and are correctly placed there.
> - Line 16: the 2025 rebuild sentence is discretionary rationale that degrades gracefully if lost; correctly placed in `## Background`.
> - Line 18: "Feel free to skim `docs/ingest-overview.md` before making changes." "Feel free to" is an unambiguous grant of optionality, not a hedge on an obligation, so R2 is not triggered; it is discretionary context correctly kept outside `## Rules`. If the author actually intends the overview to be required reading, that is a policy change, not an audit finding.
> - Line 22: "Set `retries` to at most 5." is mandatory (imperative), verifiable against the configured value, atomic, and does not conflict with any other statement; line 11 informs it (defines what `retries` counts) rather than competing with it.
> - R5: no two statements prescribe incompatible outcomes for the same decision, under either reading of line 17. No precedence finding.
>
> ### Summary
>
> Counts per rule: R1 1, R2 1, R3 0, R4 0, R5 0.
> Counts per severity: material 1, minor 0.
> The single finding carries R1 as primary and R2 as secondary, so the per-rule total (2) exceeds the severity total (1 finding).
>
> Overall assessment: the document's section structure is sound — tool semantics sit in `## Semantics`, the one explicit rule sits in `## Rules` and is clean on R2–R5, and the rules section contains no padding. The one material defect is a production-submission gate written as a description of practice and buried in `## Background`, where an agent following the document's flavor text would miss it; whether it is meant to bind is an author decision, and both rewrites above preserve the intended reading once that decision is made.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 3

> # Audit: `retry-policy`
>
> Line numbers refer to the fenced document as given (line 1 = opening `---`).
>
> ## Findings
>
> **R1 Distinguishability** (secondary: R2 Explicit strength)
> Location: line 17, `## Background`.
> Quoted text: "Engineers submit batches to the production cluster only after the staging replay has completed without errors."
> Why it fails: this statement directs behavior — it gates production submission on a clean staging replay, and an agent that ignores it does the wrong thing — but it sits between a historical sentence and an optional reading pointer in `## Background`, phrased as a description of what engineers do rather than as a directive. Nothing in its placement or wording signals that it binds, so it reads as practice commentary and is not individually checkable alongside the document's one listed rule. The descriptive present tense also leaves its strength ambiguous (R2): a reader cannot tell whether this is a mandatory gate or an observation about current habit.
> Severity: material.
> Suggested rewrite: author decision between two non-ambiguous readings.
> Promoted (binding): move to `## Rules` as its own item — "Submit batches to the production cluster only after the staging replay has completed without errors."
> Demoted (context): keep it in `## Background` and mark it explicitly nonbinding — "In current practice, engineers submit batches to production after a clean staging replay; this document does not enforce that gate."
>
> ## Not flagged (false-positive guards)
>
> - Lines 10–12 (`## Semantics`): the `--dry-run` audit-log behavior, the `retries` counting semantics, and the `INGEST_ENV` meaning are load-bearing facts about tool semantics. Losing any of them would make output wrong (e.g., treating `retries: 5` as five total attempts), but none directs behavior, so they correctly live outside `## Rules`. The "Remember that" / "Note that" framing does not make them rules; the section label carries the structural signal in this long-form document.
> - Line 16: the 2025 rebuild history is discretionary context, correctly placed in `## Background`.
> - Line 18: "Feel free to skim `docs/ingest-overview.md`" is explicitly permissive, not a hedge — its strength is unambiguously optional, so R2 does not apply. It is a pointer, not a rule, and is correctly placed outside `## Rules`.
> - Line 22: "Set `retries` to at most 5." is imperative, unhedged, atomic, and verifiable against the configured value. Clean.
> - R5: no reachable conflicts. The `retries` semantics (line 11) and the cap (line 22) govern the same field but prescribe compatible outcomes (a cap of 5 means at most six total attempts); the production-gate statement (line 17) concerns a different decision.
>
> ## Safety note
>
> None. The document contains no instructions directed at the auditor. The pointer to `docs/ingest-overview.md` is addressed to the document's consumer and was not followed.
>
> ## Summary
>
> Counts per rule: R1 1, R2 1, R3 0, R4 0, R5 0.
> Counts per severity: material 1, minor 0.
> One finding carries a secondary id, so the per-rule total of 2 exceeds the finding count of 1.
>
> This document is largely well separated: its three tool-semantics facts sit in a labeled `## Semantics` section, its history and reading pointer sit in `## Background`, and its single listed rule is imperative, atomic, and checkable. The one defect is a production-submission gate buried in `## Background` in descriptive rather than directive form, which could plausibly cause an agent to miss the obligation; whether it is meant to bind or merely to describe practice is an author decision that must be resolved before the rewrite can claim to preserve intent.
