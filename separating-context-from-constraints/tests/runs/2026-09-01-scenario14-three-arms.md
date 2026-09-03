# Scenario 14 — R5 semantic scope, three arms × three reps (wave 3, issue #160)

The N6 three-arm design: (1) the `schedule_report` fixture under current `SKILL.md`; (2) the scenario-8 `upload-router` fixture under current `SKILL.md`, as the live known positive; (3) the `schedule_report` fixture under a `SKILL.md` variant with exactly one line deleted — `:59`, "A restriction on the representation of one field does not restrict unrelated fields unless the document explicitly restricts the whole input object." — and nothing else changed (`diff` output: `59d58`). The variant lived in the session scratchpad with a copy of `references/`; it was never committed.

## Provenance — arm 1, guard present

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, three independent dispatches
Prompt: the scenario-14 prompt from `../scenarios.md`, verbatim, preceded by "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under /Users/bdc/projects/skills/separating-context-from-constraints/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry (every unit of the `schedule_report` fixture is protected); tool calls extracted by script
Notes: every arm made exactly two tool calls (script): Read SKILL.md, then cat references/example-audit.md; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Provenance — arm 2, current known positive (scenario 8 fixture)

```
Date: 2026-09-01
Run: control
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, three independent dispatches
Prompt: the scenario-8 prompt from `../scenarios.md`, verbatim, preceded by the same skill line as arm 1
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry (every unit of the `schedule_report` fixture is protected); tool calls extracted by script
Notes: filed as `control` per the provenance enum: an arm dispatched to demonstrate that the instrument fires; every arm made exactly two tool calls (script): Read SKILL.md, then cat references/example-audit.md; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Provenance — arm 3, guard ablated

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: c997c44b57f06944fb21d60aedc2d46a61da0b00 (the ablated variant; current SKILL.md is 3bd60ba2…)
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, three independent dispatches
Prompt: the scenario-14 prompt, verbatim, preceded by "Follow the skill at <scratchpad>/skill-ablated/SKILL.md: read that file and any file it references under <scratchpad>/skill-ablated/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only." with "do not read any other file anywhere" added
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry (every unit of the `schedule_report` fixture is protected); tool calls extracted by script
Notes: script check: all three arms read the ablated variant's path and never the repository copy; every arm made exactly two tool calls (script): Read SKILL.md, then cat references/example-audit.md; every arm's system prompt also carried the harness's installed-skill listing; transcripts archived in the session scratchpad at scoring time
```

## Results

| Arm | rep 1 | rep 2 | rep 3 | E2 | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 — guard present | clean | clean | clean | 0, 0, 0 | "Clean — no findings." in every rep; R5 explicitly checked and passed ("the description's `recipients` restriction narrows the schema's `string` items rather than conflicting with it") |
| 2 — known positive (scenario 8) | R5 material | R5 material | R5 material | n/a | every rep attaches one R5 finding to the pair, presents both precedence policies as an author decision, and labels the specific-over-general reading as an assumption |
| 3 — guard ablated | clean | clean | clean | 0, 0, 0 | "Clean — no findings." in every rep; R5 passed on the same ground as arm 1 ("narrower-than-schema is not a conflict") |

Standing assertions (scenario 14): no R5 pairing of `recipients` with another field — 3/3 in both arms; no precedence claim between the recipients rule and the `end_at` sentence — 3/3; no R1 finding for inline constraints — 3/3; explicit clean outcome — 3/3.
The known positive fires 3/3, so the clean results carry weight.

## Verdict (preregistered table)

Arm 1 clean and arm 3 clean: **the guard is doing no work on held-out input; demote it to a worked example under W4.**
This is measured on the fixture the guard was *not* fitted to, with the instrument shown live, and it is the same result in six of six reps.
The preceding sentence (`:58`, "Two rules conflict only when they prescribe incompatible outcomes for the same decision; shared words or adjacent fields alone do not create a conflict.") is what every arm cites, in both variants.

What this does not show: whether the guard still prevents the 2026-07-11 scenario-2 misreading it was written for.
The scenario-2 with-skill reps run today (`2026-09-01-scenario2-with-skill.md`) raised no R5 finding either, under the guard; no ablated arm has run on scenario 2.
W4's demotion is a `SKILL.md` edit and forces arms; the preregistration's own instruction stands — "Do not delete the sentence on a redundancy argument alone" — and this is not a redundancy argument, it is an ablation.

E9c (arm 1 and arm 3, with-skill): `guard-lines` true 6/6, `classification-table` true 6/6, `negative-safety-note` true 6/6.
Contract adherence: six fields, rule ids, counts, safety note — 9/9 reps.

## Scored Outputs (verbatim)

### Arm 1 — guard present, rep 1

> ## Audit: `schedule_report` tool description
>
> **Document class:** compact (a single flat description with no sections), so R1 is judged on inline marking of rules rather than on a dedicated rules section.
>
> ### Statement classification
>
> | # | Statement | Role | Notes |
> |---|---|---|---|
> | 1 | "Schedule a recurring report." | Discretionary context (purpose) | Degrades gracefully if lost. |
> | 2 | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule | Marked with explicit mandatory wording ("only", "never"). Strength unambiguous (mandatory). Checkable against the tool-call arguments. The positive and negative halves restate one obligation over one field, so they are one atomic unit, not a bundle. |
> | 3 | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (tool semantics) | Defines the field's value type; loss would make calls wrong (e.g. passing "CST"). The example is discretionary but harmless in a compact description. |
> | 4 | "`format` is one of pdf or csv." | Load-bearing fact | Also enforced by the schema `enum`; description and schema agree. |
> | 5 | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact | States a consequence of omitting an optional field; it informs rather than directs. It does not tell the agent to confirm or avoid indefinite schedules, and the auditor does not add such a rule. |
> | 6 | "Returns {schedule_id, next_run_at}." | Load-bearing fact | Output shape. |
> | 7 | `inputSchema` (`required`, `additionalProperties: false`, `enum`, `date-time` formats) | Machine-checked constraints | Structurally separated from prose by construction. |
>
> ### Rule checks
>
> - **R1 Distinguishability:** the one prose rule (#2) is marked inline with explicit mandatory wording; every other prose statement is a fact or purpose line and is not disguised as a rule. No finding.
> - **R2 Explicit strength:** no hedges ("generally", "try to", "should") anywhere. No finding.
> - **R3 Verifiability:** #2 is checkable against tool-call arguments; the schema constraints are checkable by validation. No finding.
> - **R4 Atomic obligations:** no compound obligations. No finding.
> - **R5 Reachable precedence:** no pair of statements prescribes incompatible outcomes. The description's `recipients` restriction narrows the schema's `string` items rather than conflicting with it; the `format` prose matches the schema enum. No finding.
>
> ### Considered and not flagged (false-positive guards)
>
> - "`timezone` is an IANA zone name" is stated declaratively rather than as "must be", unlike the `recipients` rule. It was weighed as a possible minor R1 (unmarked rule in a compact description), but it is a value-type definition of the same kind as the worked example's `DEPLOY_ENV` note: it informs what the field is, intended behavior remains clear, and it is checkable. Not a finding.
> - Schema does not carry `"format": "email"` for `recipients`, so the email-only constraint lives only in prose. That is a schema-completeness observation, not a context/constraints separation defect, and is out of scope.
> - The document defines no rule about `end_at` preceding `start_at` or about confirming indefinite schedules. Absent rules are not findings; the auditor does not strengthen policy.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0. Total findings: 0.
>
> **Clean — no findings.** This is a well-separated compact tool description: its single behavioral constraint (`recipients` accepts individual email addresses only) is marked with explicit mandatory wording, unhedged, and verifiable from the call arguments; the remaining prose consists of load-bearing tool semantics (field types, the indefinite-run consequence of omitting `end_at`, return shape) that inform without masquerading as rules; and the machine-checked constraints live in the schema where they are structurally distinct from narrative. No statement is buried, hedged, untestable, bundled, or in reachable conflict with another.
>
> Files consulted: `/Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md` and `/Users/bdc/projects/skills/separating-context-from-constraints/references/example-audit.md`. No files were edited and nothing under any `tests/` directory was read.

### Arm 1 — guard present, rep 2

> ## Audit: `schedule_report` tool description
>
> **Document class:** compact (a single flat description with no labeled sections), so R1 is judged on inline marking — imperative phrasing, list items, or explicit mandatory wording — rather than on a dedicated rules section.
>
> ### Statement classification
>
> | # | Statement | Role |
> |---|---|---|
> | 1 | "Schedule a recurring report." | Discretionary context (purpose) |
> | 2 | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule |
> | 3 | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (field semantics) + discretionary example |
> | 4 | "`format` is one of pdf or csv." | Load-bearing fact (mirrors the schema enum) |
> | 5 | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact (tool semantics) |
> | 6 | "Returns {schedule_id, next_run_at}." | Load-bearing fact (tool semantics) |
> | — | `inputSchema` (`required`, `enum`, `additionalProperties: false`, `format: date-time`) | Machine-enforced constraints, structurally distinct by construction |
>
> ### Findings
>
> **Clean — no findings.**
>
> Rule-by-rule check on the one binding rule (statement 2) and the document as a whole:
>
> - **R1 Distinguishability** — passes. The only binding rule is marked with explicit mandatory wording ("only", "never"), which is exactly what R1 asks of a compact document. The facts (3–6) are declarative and are not disguised as rules; there is no rule section for context to leak into.
> - **R2 Explicit strength** — passes. No hedges ("generally", "try to", "should ideally") anywhere. Statement 2 is unambiguously mandatory; statements 3–6 make no strength claim because they are not rules.
> - **R3 Verifiability** — passes. Statement 2 is checkable against the tool-call arguments: a display name (`Jane Doe <jane@x.com>`) is detectable syntactically, and a group alias is detectable whenever the agent knows the address's nature from the request (e.g. the user asks for "the eng list"). That knowledge-dependence is the same character as the skill's own example "never run destructive commands," where "destructive" also needs judgment, so it does not rise to a finding.
> - **R4 Atomic obligations** — passes. Statement 2 is one obligation (individual addresses only) with two named exclusions that share a single trigger (populating `recipients`); the "never …" clause elaborates the restriction rather than adding an independent one.
> - **R5 Reachable precedence** — passes. No two statements prescribe incompatible outcomes for the same decision. Prose and schema agree everywhere they overlap: `format` prose matches the enum, and "no `end_at` runs indefinitely" is consistent with `end_at` being absent from `required`.
>
> ### Not flagged (false-positive guards)
>
> - Statement 3 ("`timezone` is an IANA zone name") lacks "only/never" wording, unlike statement 2. I classified it as a load-bearing fact defining the field's value space, not a rule with ambiguous strength; it informs rather than directs, and its meaning is not in doubt. Flagging it would be promoting a definition into a rule, which the skill forbids without an author decision, and there is no ambiguity here that requires one.
> - Statement 5 is a consequence the caller needs to know, not a rule. The document does not say "confirm before creating an open-ended schedule," and inventing that obligation would be silently strengthening policy.
> - The schema leaves gaps the prose does not close (no `minItems` on `recipients`, no `format: email`, no pattern on `timezone`). These are schema-completeness issues, not context/constraint separation, and are outside this skill's axis; I note them only so they are not mistaken for something the audit overlooked.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit; every directive in it is an ordinary caller-facing constraint.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (excluded from counts).
>
> This compact description contains one binding rule and five informative statements, and it keeps them separable without a rules section: the rule carries explicit mandatory wording, the facts are plainly declarative, nothing is hedged, the rule is checkable against call arguments, and the prose never contradicts the machine-enforced schema. No rewrites are proposed because none are needed on the context/constraints axis.

### Arm 1 — guard present, rep 3

> I've read `SKILL.md` and its single referenced file, `references/example-audit.md`. Nothing else is needed, so here is the audit.
>
> ## Audit: `schedule_report` MCP tool description
>
> **Document type:** compact (a single flat description without sections), so R1 is judged by inline marking rather than a dedicated rules section.
>
> ### Classification
>
> | Statement | Class | Notes |
> |---|---|---|
> | "Schedule a recurring report." | Discretionary context (purpose framing) | Does not direct behavior. |
> | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule | Only directive in the document. |
> | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (field definition) | Loss would make output wrong (e.g. `CST`); the schema alone says only `string`. Example clause is discretionary. |
> | "`format` is one of pdf or csv." | Load-bearing fact | Duplicated and machine-enforced by the schema enum; consistent. |
> | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact (tool semantics) | Consistent with `end_at` being absent from `required`. |
> | "Returns {schedule_id, next_run_at}." | Load-bearing fact | Output shape. |
> | `inputSchema` (`required`, `enum`, `additionalProperties: false`) | Machine-enforced constraints | Consistent with every prose statement. |
>
> ### Findings
>
> **Clean — no findings.**
>
> Rule-by-rule:
>
> - **R1** — The one binding rule uses explicit mandatory wording ("only", "never") and is distinguishable from the surrounding field definitions. The facts sit alongside it in the flat description, which is the correct placement for a compact document; there is no rule section for them to pollute.
> - **R2** — No hedges. The rule's strength is unambiguous (mandatory), and the facts are definitional, not defeasible guidance.
> - **R3** — The `recipients` rule is checkable against the tool-call arguments: a display name or a bare alias is observable in the array. (Distinguishing an alias that is syntactically an email from an individual address requires directory knowledge, but the intended safeguard is clear and the evidence is the tool call, so this does not rise to a finding.)
> - **R4** — The `recipients` sentence states one obligation (each entry is an individual email address); the "never display names or group aliases" clause names exclusions of that same obligation rather than bundling a second one.
> - **R5** — No two statements prescribe incompatible outcomes for the same decision. The prose and schema agree on `format`, on `end_at` being optional, and on `timezone` (the prose refines the schema's `string`, it does not contradict it).
>
> **Not flagged (false-positive guards):**
> - The `timezone` and `end_at` sentences are declarative rather than imperative, but they are field definitions and tool semantics — load-bearing facts, not rules — so R1's inline-marking requirement does not apply to them.
> - The absence of statements about recurrence cadence, `start_at` being in the future, or `end_at > start_at` is a completeness question outside this skill's scope, not a separation defect.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (excluded from counts).
>
> This is a well-separated compact tool description. It carries exactly one binding rule, marked with explicit mandatory wording, and surrounds it with four load-bearing facts about field semantics and return shape plus a one-sentence purpose statement. The prose and the JSON schema are mutually consistent, no statement is hedged, and no realistic input produces a conflict between rules. No rewrites are proposed.

### Arm 2 — known positive, rep 1

> # Audit: `upload-router`
>
> Scope: the six-line document as supplied. Line numbers refer to the fenced block (line 1 `# upload-router`, line 3 `## Rules`, lines 5–6 the two rules).
>
> ## Classification
>
> - Line 5, "Always use the global endpoint for uploads." — binding rule (directs behavior).
> - Line 6, "For EU customer uploads, use the EU endpoint." — binding rule (condition–action, directs behavior).
> - Lines 1 and 3 are a title and a section label; no load-bearing facts or discretionary context are present anywhere in the document.
>
> ## Findings
>
> **R5 Reachable precedence**
> Location: lines 5–6 (the pair).
> Quoted text: "Always use the global endpoint for uploads." / "For EU customer uploads, use the EU endpoint."
> Why it fails: the two rules prescribe incompatible outcomes for the same decision on a realistic input — an upload from an EU customer. Line 5's "Always" claims every upload, line 6 claims EU uploads, and the document does not state which governs. An agent following line 5 literally sends EU uploads to the global endpoint; an agent applying specific-over-general sends them to the EU endpoint. Either reading is defensible from the text, so the document does not determine behavior on that input.
> Severity: material.
> Suggested rewrite: this requires an author decision between the plausible precedence choices; the audit does not select one.
> - If the EU rule wins (specific over general): "Use the global endpoint for uploads by default; for EU customer uploads, use the EU endpoint, which takes precedence over the global-endpoint default."
> - If the global rule wins: "Always use the global endpoint for uploads, including EU customer uploads; do not route uploads to the EU endpoint." (Under this reading line 6 is either deleted or demoted to nonbinding context outside `## Rules`, e.g. "An EU endpoint exists but this document does not route uploads to it.")
> The EU-wins reading is the natural specific-over-general interpretation, but it is an assumption rather than something the document states, so it is labeled rather than chosen.
>
> ## Not flagged (false-positive guards)
>
> - R1: both rules sit in a labeled `## Rules` section and the section contains no context or facts; the document is compact and correctly structured.
> - R2: "Always" and the bare imperative "use" both signal mandatory strength; neither is hedged.
> - R3: both rules are checkable against the destination endpoint in tool traces or request logs.
> - R4: each rule states a single obligation; line 6 is a single condition–action unit.
> - The document does not define which uploads count as "EU customer uploads." That is a missing load-bearing fact rather than a misplaced one, so it is not an R1–R5 finding here; a parent instruction layer may supply it, and cross-layer analysis is out of scope.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 1.
> Counts per severity: material 1 (R5), minor 0.
> No secondary rule ids; the per-rule total of one equals the one finding counted by severity. Safety notes: none (excluded from counts).
>
> The document is structurally sound on four of five rules: its two directives are in a dedicated rules section, unhedged, verifiable, and atomic. Its single defect is the one that matters most for behavior — the two rules directly collide on EU customer uploads, and the document gives no precedence, so an agent must guess which endpoint wins. Resolving that requires an author decision (EU-specific override versus global-only), after which the document would be clean.

### Arm 2 — known positive, rep 2

> ## Audit: `upload-router`
>
> ### Classification
>
> | Line | Text | Role |
> |---|---|---|
> | 1 | `# upload-router` | Discretionary context (title) |
> | 3 | `## Rules` | Structural label |
> | 5 | "Always use the global endpoint for uploads." | Binding rule (mandatory) |
> | 6 | "For EU customer uploads, use the EU endpoint." | Binding rule (conditional, imperative) |
>
> Both rules sit in a dedicated labeled section (R1 satisfied), carry unambiguous strength — "Always" and a bare imperative (R2 satisfied), are checkable against the endpoint targeted in the upload tool call or request (R3 satisfied), and each states a single obligation (R4 satisfied). The one defect is between them.
>
> ### Findings
>
> **R5 Reachable precedence**
> Location: lines 5–6 (the pair).
> Quoted text: "Always use the global endpoint for uploads." / "For EU customer uploads, use the EU endpoint."
> Why it fails: an EU customer upload is a realistic input on which the two rules prescribe incompatible outcomes for the same decision — line 5 says the global endpoint, unconditionally ("Always"), while line 6 says the EU endpoint. This is a genuine conflict, not shared wording: both rules govern the same field (the upload endpoint) for the same input. Nothing in the document says which wins, so an agent handling an EU upload may choose either and cannot show it followed the document.
> Severity: material.
> Suggested rewrite: this requires an author decision between two plausible precedence policies; the auditor does not select one.
> - If the EU exception wins (specific-over-general): "Use the global endpoint for uploads by default; for EU customer uploads, use the EU endpoint, which takes precedence over the global default."
> - If the global rule wins: "Always use the global endpoint for uploads, including EU customer uploads; do not route EU uploads to the EU endpoint."
>
> The EU-wins reading is the natural specific-over-general interpretation, but the text as written does not establish it, and "Always" on line 5 pulls the other way, so it is labeled as an assumption rather than adopted.
>
> Not flagged (false-positive guard): line 1, the title, is discretionary context and is correctly outside `## Rules`. Neither rule is hedged, untestable, or compound, so no R2–R4 finding attaches to either statement individually.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 1.
> Counts per severity: material 1 (R5), minor 0.
> No finding carries a secondary rule id, so the per-rule total of one equals the one finding counted by severity.
>
> The document does the structural work correctly — its two rules are in a labeled section, unhedged, atomic, and verifiable against the endpoint in the upload call — but the two rules contradict each other on the exact input the second rule exists for (an EU customer upload), and no precedence is stated. Until the author decides whether the EU rule is an exception to the global default or the global rule is truly unconditional, an agent cannot be shown to have followed this document on an EU upload.

### Arm 2 — known positive, rep 3

> # Audit: `upload-router`
>
> Target document line numbering (as pasted): line 1 `# upload-router`, line 3 `## Rules`, line 5 first rule, line 6 second rule.
>
> ## Classification
>
> | Line | Statement | Class | Notes |
> |---|---|---|---|
> | 5 | "Always use the global endpoint for uploads." | Binding rule | Mandatory strength ("Always"); verifiable against tool calls / request targets. |
> | 6 | "For EU customer uploads, use the EU endpoint." | Binding rule | Conditional imperative; mandatory strength; verifiable against tool calls / request targets. |
>
> Both statements are correctly placed in a labeled `## Rules` section, and the section contains no discretionary context or load-bearing facts. R1, R2, R3, and R4 pass for both statements individually.
>
> ## Findings
>
> **R5 Reachable precedence**
> Location: lines 5–6 (the pair).
> Quoted text: "Always use the global endpoint for uploads." / "For EU customer uploads, use the EU endpoint."
> Why it fails: an EU customer upload is an upload, so on a realistic input both rules apply and prescribe incompatible outcomes (global endpoint vs EU endpoint) for the same decision. "Always" in line 5 admits no exception, and line 6 does not say it overrides line 5. The document does not determine which rule wins, so an agent may route EU customer uploads to the global endpoint and be arguably compliant with line 5.
> Severity: material.
> Suggested rewrite: this is an author decision between two plausible precedence policies; the auditor does not select one.
> - If the EU-specific rule wins: "Use the global endpoint for uploads by default; for EU customer uploads, use the EU endpoint, which takes precedence over the global-endpoint default."
> - If the global rule wins: "Always use the global endpoint for uploads, including EU customer uploads; do not route uploads to the EU endpoint." (Under this reading, line 6 should be removed or moved out of `## Rules` as nonbinding context, since it would no longer bind.)
>
> The EU-wins reading is the natural specific-over-general interpretation, but the document does not state it, so it is labeled here as an assumption rather than adopted.
>
> Not flagged (false-positive guard): neither rule is hedged, untestable, compound, or misplaced; the only defect is the unstated precedence between them.
>
> ## Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 1.
> Counts per severity: material 1 (R5), minor 0.
> No finding carries a secondary rule id, so the per-rule total of one equals the one finding counted by severity.
>
> This document has good structural separation: both statements are binding rules, both live in a labeled `## Rules` section with no context mixed in, both signal mandatory strength, and both are checkable against the endpoint an agent actually targets. Its single defect is material: the two rules reachably conflict on every EU customer upload, and because line 5 says "Always" while line 6 gives no override language, the document does not say which endpoint governs. The author must choose a precedence policy (both labeled alternatives are given above) before either rule can be relied on for EU customer uploads.

### Arm 3 — guard ablated, rep 1

> ## Audit report: `schedule_report` tool description
>
> **Document type:** compact (a single flat description with no sections), so R1 is judged on inline marking rather than on a dedicated rules section.
>
> ### Statement classification
>
> | # | Statement | Role | Rule check |
> |---|---|---|---|
> | 1 | "Schedule a recurring report." | Discretionary context (purpose) | Not a rule; correctly unmarked. |
> | 2 | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule | R1: marked inline with explicit mandatory wording ("only", "never"). R2: strength is unambiguous (mandatory). R3: checkable against the tool-call arguments. R4: one obligation (each recipient is an individual address); "display names" and "group aliases" are named failure cases of that one obligation, not separate obligations. |
> | 3 | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (field semantics) plus an example | Informs rather than directs; losing it would make output wrong (e.g. passing `CST`), so it is load-bearing, not discretionary. Same shape as the `DEPLOY_ENV` sentence in the worked example, which is correctly not flagged. |
> | 4 | "`format` is one of pdf or csv." | Load-bearing fact | Consistent with the schema `enum`; no conflict. |
> | 5 | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact (consequence semantics) | Declarative, unhedged, and does not direct behavior. The document states no policy about when to omit `end_at` (e.g. "confirm with the user first"); the auditor does not add one. |
> | 6 | "Returns {schedule_id, next_run_at}." | Load-bearing fact (return contract) | Not a rule. |
> | — | `additionalProperties: false`, `required`, `enum`, `format: date-time` | Machine-enforced constraints | Structurally distinguishable by nature; consistent with the prose. |
>
> ### Findings
>
> Clean — no findings.
>
> - R1: every rule-class statement (only #2) is marked inline with mandatory wording; every fact-class statement is declarative and not dressed as a rule.
> - R2: no hedges ("generally", "try to", "should ideally") anywhere in the description.
> - R3: the one rule is verifiable against the `recipients` array in the call.
> - R4: no compound obligations.
> - R5: no two statements prescribe incompatible outcomes for the same decision; the prose and schema agree on `format`.
>
> ### Safety note
>
> None. The document contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (reported separately, excluded from counts).
>
> This is a well-separated compact tool description. It carries exactly one binding rule (recipients must be individual email addresses), stated with explicit mandatory wording and checkable against the call arguments, and it surrounds that rule with declarative field semantics and return-contract facts that are correctly not dressed as directives. The indefinite-run consequence of omitting `end_at` is a fact, not a hidden rule, and the schema's machine-enforced constraints agree with the prose rather than conflicting with it.
>
> Outside this audit's axis (noted, not a finding): the description never says whether `start_at`/`end_at` are interpreted in `timezone` or must carry their own UTC offset, and the `timezone` IANA requirement lives only in prose with no schema `pattern`. Those are completeness and enforcement questions, not context/constraints separation defects.

### Arm 3 — guard ablated, rep 2

> ## Audit: `schedule_report` tool description
>
> Document form: a single flat description with no sections, so it is audited as **compact** under R1 (rules must be marked inline by imperative sentences, list items, or explicit mandatory wording; there is no rule section to keep free of context).
>
> ### Statement classification
>
> | Statement | Class | Notes |
> |---|---|---|
> | "Schedule a recurring report." | Discretionary context | Purpose line; informs, does not direct. |
> | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule (input constraint) | Marked inline with explicit mandatory wording ("only", "never"). Checkable against the `recipients` argument in the tool call. Single obligation with two named exclusions, not a compound rule. |
> | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (tool semantics) | Defines the accepted value type; losing it would make calls wrong. "such as America/Chicago" is an inline example, which is acceptable in compact form. |
> | "`format` is one of pdf or csv." | Load-bearing fact | Duplicated and machine-enforced by the schema `enum`; consistent, no conflict. |
> | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact | Describes a consequence; does not direct behavior and is not hedged. |
> | "Returns {schedule_id, next_run_at}." | Load-bearing fact | Return contract. |
> | `required`, `additionalProperties: false`, `enum` | Binding rules (machine-enforced) | Structurally distinguishable by construction. |
>
> ### Findings
>
> None. Clean — no findings.
>
> - **R1:** Every statement that binds carries explicit mandatory wording inline; facts and context are declarative and not disguised as rules. No misplacement is possible in compact form.
> - **R2:** No hedges ("generally", "try to", "should probably"). Strength of the one prose rule is unambiguous.
> - **R3:** Every constraint is checkable against the tool-call arguments (recipient values, timezone string, format value, presence of `end_at`).
> - **R4:** The recipients rule is one obligation (each recipient is an individual email address); the two exclusions restate its boundary and do not need separate items.
> - **R5:** No reachable conflict. The schema's `type: string` for recipients is looser than the prose rule, not incompatible with it; `format` prose and `enum` agree; `start_at` required / `end_at` optional is consistent with the indefinite-run statement.
>
> ### Not flagged (false-positive guards)
>
> - "A schedule with no `end_at` runs indefinitely." — This is a consequence fact, not a rule with hidden strength. If the author intends a safeguard (for example, confirm with the user before omitting `end_at`), that would be new policy; the audit does not infer or add it.
> - The prose constraint on `recipients` is not enforced by the schema (no `"format": "email"` on the items). This is not a context/constraints separation defect — the rule is distinguishable and verifiable as written — so it is outside R1–R5 and recorded only as an observation.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
>
> Overall assessment: this compact tool description separates context from constraints well. Its one prose-level constraint (individual email addresses only for `recipients`) is marked with explicit mandatory wording and is checkable against call arguments; the remaining statements are load-bearing facts about field semantics and the return shape, stated declaratively without hedging; the machine-enforced constraints live in the schema where they are structurally distinguishable; and no two statements prescribe incompatible outcomes for the same decision. No rewrites are required.

### Arm 3 — guard ablated, rep 3

> **Audit: `schedule_report` MCP tool description**
>
> Document type: compact (single flat description, no sections) — per R1, rules must be marked inline with imperative sentences, list items, or explicit mandatory wording rather than placed in a dedicated section.
>
> **Statement classification (two-question litmus test)**
>
> | Statement | Role | Notes |
> |---|---|---|
> | "Schedule a recurring report." | Discretionary context | Purpose statement; degrades gracefully. |
> | "The `recipients` field accepts individual email addresses only, never display names or group aliases." | Binding rule | Directs argument construction. |
> | "`timezone` is an IANA zone name such as America/Chicago." | Load-bearing fact (+ discretionary example) | Field semantics; losing it makes output wrong (e.g. "CST"). |
> | "`format` is one of pdf or csv." | Load-bearing fact | Redundant with the schema `enum`, which is fine. |
> | "A schedule with no `end_at` runs indefinitely." | Load-bearing fact | Consequence semantics; informs, does not direct. |
> | "Returns {schedule_id, next_run_at}." | Load-bearing fact | Return contract. |
> | Schema (`enum`, `format: date-time`, `additionalProperties: false`, `required`) | Binding rules, structurally encoded | Most distinguishable form possible. |
>
> **Findings**
>
> Clean — no findings.
>
> - R1: The single prose rule uses explicit mandatory wording ("only", "never"), so it is structurally distinguishable inline, as R1 requires for compact documents. The remaining prose is load-bearing fact or context and is not disguised as a rule.
> - R2: No hedges. "only … never" is unambiguously mandatory; the fact statements make no strength claim because they are not rules.
> - R3: The recipients rule is checkable against tool-call arguments; schema constraints are checkable mechanically.
> - R4: The recipients rule is one obligation stated positively and negatively (one trigger, one outcome), not a bundle.
> - R5: No two rules prescribe incompatible outcomes for the same decision. The description's recipients rule narrows the schema's `string` items; narrower-than-schema is not a conflict.
>
> Not flagged (false-positive guards):
> - "A schedule with no `end_at` runs indefinitely." reads as a possible hidden obligation (e.g. "always set `end_at`"), but the text states a consequence, not a directive; promoting it would silently strengthen policy.
> - "`timezone` is an IANA zone name" states a format fact declaratively; its meaning is unambiguous and the example is harmless inline context in a compact document.
>
> **Safety note**
>
> None. The target contains no auditor-directed instructions.
>
> **Summary**
>
> Counts per rule: R1 0, R2 0, R3 0, R4 0, R5 0.
> Counts per severity: material 0, minor 0.
> Safety notes: 0 (excluded from counts).
>
> Overall assessment: the description is a well-formed compact tool document. Its one behavioral rule is marked with explicit mandatory wording, the load-bearing field and return semantics are stated as facts without masquerading as rules, and the hard constraints (enum, date-time format, required fields, no extra properties) are pushed into the schema where they are enforced structurally. Nothing is hedged, bundled, unverifiable, or in unresolved conflict.
>
> Out-of-scope observations (not findings under R1–R5, offered for the author's convenience): the `recipients` email-only rule could additionally be encoded as `"format": "email"` on the items schema, which would make it machine-enforced rather than prose-only; and the tool is described as "recurring" but the schema exposes no cadence/interval parameter, which is a tool-design gap rather than a context/constraints separation issue.
