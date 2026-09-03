# Scenario 14 — schedule_report, With-Skill, three reps (Wave B rerun, W4/#160 guard deletion)

```
Date: 2026-09-02
Run: with-skill (guard deleted; the current SKILL.md is the ablation)
SKILL.md blob: 2cb876f4010f55a3259fe740a46d1e8aaea78eea
Commit: a9f0116 (branch `separating-context-wave3`, Wave B wording; not on `main`)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent
Prompt: "Follow the skill at /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/SKILL.md: read that file and any file it references under /private/tmp/claude-501/-Users-bdc-projects-skills-separating-context-from-constraints/d0972885-7726-4c07-bfe8-c07113457ce4/scratchpad/wave3/separating-context-from-constraints/references/. Do not read any other file anywhere, do not read anything under any tests/ directory, do not load any skill through the harness, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-02, unblinded; scored under the preregistration's Rerun classification; per-defect tables transcribed and reconciled by a Claude subagent (opus) against the archived outputs; tool calls extracted by script
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); this cell's reps were dispatched at 2026-09-02T20:35:30Z, 20:35:35Z and 20:35:40Z and the known-positive scenario 8 reps at 20:31:40Z, 20:31:43Z and 20:31:46Z, in different dispatch batches of the same rerun session
```

## Scoring

Known positive: scenario 8's with-skill cell, tests/runs/2026-09-02-scenario8-with-skill-waveB.md, R5 conflict reported 3/3.

Assertion labels follow the order of the bullets in `tests/scenarios.md`, scenario 14: A1 no R5 finding claims a conflict between the `recipients` restriction and any other field; A2 no finding treats the `recipients` restriction and the `end_at` sentence as a precedence problem; A3 no R1 finding is raised merely because the constraints live inline in the `description`; A4 the run states an explicit clean outcome.

| Rep | A1 no cross-field R5 | A2 no `recipients`/`end_at` precedence finding | A3 no R1 for inline placement | A4 explicit clean outcome | E2 |
| --- | --- | --- | --- | --- | --- |
| 1 | ✓ "No two statements prescribe incompatible outcomes for the same decision", with `format`, `end_at` and `recipients` each checked against the schema | ✓ the `end_at` sentence is classified a load-bearing fact and raises no precedence question | ✓ "as a compact description it owes no dedicated rule section"; inline marking judged sufficient under R1 | ✓ "Clean — no findings." | 0 |
| 2 | ✓ "No two statements prescribe incompatible outcomes"; prose and schema agree on `format`, `end_at` and `start_at` | ✓ the `end_at` sentence "informs rather than directs" and is "a fact, not a rule in disguise" | ✓ "in a compact document that is all it owes" | ✓ "**Clean — no findings.**" | 0 |
| 3 | ✓ "No two statements prescribe incompatible outcomes for the same decision", with the `format` and `end_at` checks named | ✓ the `end_at` sentence "does not obligate the caller to set `end_at` or to confirm before scheduling an open-ended report" | ✓ "under R1 inline marking is all a rule owes and embedding is not a finding" | ✓ "**Clean — no findings.**" | 0 |

Scored assertions: **4/4 ×3.**

E9c: guard-lines true ×3; classification-table true ×3 (all three reps print a classification table); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** The guard sentence at `SKILL.md:59` is deleted in this blob, so this arm is both the with-skill cell and the ablation the preregistration's Rerun classification says not to run separately, and the cell still reads clean ×3 exactly as the 2026-09-01 cell did.
Every rep reaches the clean verdict by reasoning about what each statement decides rather than by reciting the deleted field/object sentence, which is the evidence W4/#160 asked for: the guard was carrying no load this fixture can detect.
The clean result rests on the found R5 conflict on scenario 8 in all three reps, cited above, which ran against the same `SKILL.md` blob `2cb876f4010f55a3259fe740a46d1e8aaea78eea`, the same model and the same harness.
The two cells were dispatched in different batches of the same rerun session — scenario 8's reps at 2026-09-02T20:31:40Z, 20:31:43Z and 20:31:46Z, this cell's at 20:35:30Z, 20:35:35Z and 20:35:40Z, about four minutes apart — which deviates from N6's literal "dispatched together" and "in the same batch" wording while meeting its stated purpose of proving the instrument under the same configuration, same blob, same model and same harness.
That deviation is recorded here as a process note for the author, who decides whether the cell stands.
The observations the reps do record — the missing cadence field, the schema's unconstrained `recipients` items, `start_at` going unmentioned in the prose — are all placed outside R1–R5, so E2 is 0.

## Scored Outputs (verbatim)

### With-skill, rep 1

> # Audit: `schedule_report` tool description
>
> **Document type:** MCP tool description — a compact document (single flat description, no sections). Under R1, inline marking is all a rule owes here; embedding is not a finding in this form.
>
> ## Classification
>
> | Statement | Role | Marking |
> |---|---|---|
> | "Schedule a recurring report." | Discretionary context (tool purpose) | n/a |
> | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule (directs what the caller may pass) | Explicit mandatory wording ("only", "never") |
> | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (field semantics); the example is discretionary | Definitional, unhedged |
> | "`format` is one of pdf or csv." | Load-bearing fact, duplicated by the schema `enum` | Definitional, unhedged |
> | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact (consequence of omission) | Definitional, unhedged |
> | "Returns {schedule_id, next_run_at}." | Load-bearing fact (return shape) | n/a |
> | `inputSchema` (`required`, `enum`, `additionalProperties: false`, `format: date-time`) | Load-bearing facts, machine-enforced | n/a |
>
> ## Findings
>
> Clean — no findings.
>
> Statements considered and not flagged (false-positive guards):
>
> - **R1 / recipients rule.** The only binding rule is marked by "only" and "never" and sits in a compact description, so inline marking satisfies R1. Its grammatical form ("accepts ... only") reads as tool semantics, but the mandatory wording makes its binding force unambiguous either way.
> - **R2 / recipients rule.** Strength is explicit (mandatory). No hedges ("generally", "try to", "should") appear anywhere in the document.
> - **R3 / recipients rule.** Trigger is decidable (every call to this tool); the result is checkable against the `recipients` array in the tool call. Whether an address is a "group alias" is an ordinary domain predicate the caller can decide from the situation (the caller knows whether it is naming a person or resolving a group), so it passes R3 rather than being a trigger nothing lets the reader decide.
> - **R4 / recipients rule.** "Individual email addresses only, never display names or group aliases" is one obligation (each recipient is an individual address) with two named non-examples, not several bundled obligations.
> - **R5.** No two statements prescribe incompatible outcomes for the same decision. The description and schema agree on `format` (enum), on `end_at` (optional; omission means indefinite), and on `recipients` (schema is looser than the prose, which narrows it — a refinement, not a conflict).
> - The `timezone`, `format`, `end_at`, and return-shape statements are load-bearing facts correctly stated as semantics, not dressed as rules; none is a "rule that cannot fail."
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0. Total findings: 0.
>
> The document contains exactly one binding rule (the `recipients` restriction), and it is explicitly marked as mandatory, decidably triggered, checkable against the tool call, and atomic. The remaining prose consists of load-bearing field semantics and return-shape facts, stated definitionally without hedging, and consistent with the machine-enforced schema. No rule is buried, hedged, untestable, compound, or in unresolved conflict with another, and as a compact description it owes no dedicated rule section. No rewrites are needed.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> *Out of scope (not a finding):* the description says "recurring" but the schema exposes no cadence/interval field. That is a tool-design completeness question, not a context-versus-constraints defect, so it is noted only for the caller's awareness.

### With-skill, rep 2

> ## Audit: `schedule_report` tool description
>
> **Document type:** compact — a single flat description without sections. Under R1, inline marking is all a rule owes here, and embedding is not a finding.
>
> ### Classification
>
> | Statement | Role |
> |---|---|
> | "Schedule a recurring report." | Discretionary context (purpose framing) |
> | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule on the caller, stated as tool semantics; marked inline with explicit mandatory wording ("only", "never") |
> | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (tool semantics) with an example |
> | "`format` is one of pdf or csv." | Load-bearing fact, also enforced by the schema enum |
> | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact (consequence of an omitted input) |
> | "Returns {schedule_id, next_run_at}." | Load-bearing fact (return shape) |
> | Schema (`required`, `enum`, `additionalProperties: false`, `format: date-time`) | Machine-enforced constraints; structurally distinguishable by nature |
>
> ### Findings
>
> **Clean — no findings.**
>
> - **R1:** The one binding statement (recipients) carries explicit mandatory wording and is not mistakable for flavor text; in a compact document that is all it owes. The remaining statements are load-bearing facts, which correctly sit in the descriptive prose rather than posing as rules.
> - **R2:** No hedged strength anywhere; "only" / "never" are unambiguous.
> - **R3:** The recipients rule has a decidable trigger (constructing the `recipients` array) and is checkable against the tool call's arguments.
> - **R4:** "individual email addresses only, never display names or group aliases" is one obligation stated positively and then negatively; the two exclusions are entailed by the positive form, not independent obligations sharing a sentence.
> - **R5:** No two statements prescribe incompatible outcomes. Prose and schema agree on `format` (pdf/csv), on `end_at` being optional, and on `start_at` being required.
>
> Not flagged (false-positive guards):
> - "A schedule with no `end_at` runs indefinitely" informs rather than directs; no policy in the document is violated by omitting `end_at`, so it is a fact, not a rule in disguise. If the author intends a safeguard (e.g. confirmation before creating an open-ended schedule), that would be a new rule, and adding it is an author decision outside a semantic-preserving audit.
> - The email-only constraint lives in prose while the schema declares `recipients` items as bare `string`. That is not a separation defect — the rule is marked and distinguishable — so it is outside this audit's axis; noted only so the author can decide whether to also encode it (e.g. `"format": "email"`).
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
>
> This is a well-separated compact tool description. It carries exactly one caller-facing constraint, marked with unambiguous mandatory wording and verifiable against the call arguments; everything else is tool semantics or return-shape facts that an agent needs for correctness and that are appropriately stated as facts rather than dressed up as rules. The prose and the JSON schema are consistent with each other, so no precedence question arises. No rewrites are proposed.

### With-skill, rep 3

> ## Audit: `schedule_report` tool description
>
> Skill followed: `SKILL.md` plus its one referenced file, `references/example-audit.md`. No other files read, nothing edited.
>
> ### Classification (two-question litmus test)
>
> | Statement | Role |
> |---|---|
> | "Schedule a recurring report." | Discretionary context (purpose statement) |
> | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule (directs what the caller may pass), mandatory strength |
> | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (field semantics); the example is discretionary |
> | "`format` is one of pdf or csv." | Load-bearing fact, duplicated by the schema `enum` |
> | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact (behavioral semantics) |
> | "Returns {schedule_id, next_run_at}." | Load-bearing fact (output contract) |
> | `inputSchema` (`enum`, `required`, `additionalProperties: false`, `format: date-time`) | Machine-enforced constraints, structurally marked by nature |
>
> ### Findings
>
> **Clean — no findings.**
>
> The document is a compact document (a single flat description without sections), so under R1 inline marking is all a rule owes and embedding is not a finding. The one binding rule (recipients) is marked with explicit mandatory wording ("only", "never"), so it is distinguishable. Rule-by-rule:
>
> - **R1** — The recipients rule is marked inline; no rule is disguised as context, and no context sits inside a rule section (there is none, and none is owed).
> - **R2** — No hedges. "only"/"never" state mandatory strength; every other sentence is a fact, not a rule, so it owes no strength marker.
> - **R3** — The recipients rule has a decidable trigger (populating `recipients`) and a result checkable against the tool-call arguments.
> - **R4** — "individual email addresses only, never display names or group aliases" is one obligation (each item is an individual address) with two named exclusions sharing one trigger; it stays together as a single unit.
> - **R5** — No two statements prescribe incompatible outcomes for the same decision. The prose `format` constraint matches the schema `enum`; "no `end_at` runs indefinitely" is consistent with `end_at` being optional.
>
> Not flagged (false-positive guards):
>
> - "A schedule with no `end_at` runs indefinitely" is a load-bearing fact, not a buried rule. It does not obligate the caller to set `end_at` or to confirm before scheduling an open-ended report. If the author intends such a safeguard, that is a missing rule, which this audit does not manufacture; flagging it would silently strengthen policy.
> - "never group aliases" requires judgment (a distribution list is syntactically an email address), but whether an address is a group alias is an ordinary domain predicate the reader can usually decide from the situation, so the trigger is decidable and it is not an R3 finding.
> - `start_at` is required by the schema but unmentioned in the prose. The schema marks it structurally, so nothing is undistinguishable; prose/schema completeness is outside the context-versus-constraints axis.
> - `recipients` items are unconstrained strings in the schema while the prose restricts them to email addresses. The constraint lives in the prose and is marked; schema/prose duplication is not a separation defect.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> No finding carries a secondary rule id; the per-rule total (0) equals the severity total (0).
>
> This is a compact, well-separated tool description. It contains exactly one binding rule, stated with explicit mandatory wording and inline marking appropriate to a flat description, and every other sentence is a load-bearing fact about field, behavior, or return semantics that the caller needs but that does not direct behavior. No statement hedges its strength, no obligation is bundled or untestable, and the prose is consistent with the machine-enforced schema, so no precedence question arises. No structural changes are recommended.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
