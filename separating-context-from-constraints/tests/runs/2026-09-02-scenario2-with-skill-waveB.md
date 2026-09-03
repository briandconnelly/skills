# Scenario 2 — archive_channel, With-Skill, three reps (Wave B rerun, A2.1 adjudication, R3 widened)

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
Notes: SKILL.md loaded by worktree path, not through a harness; every arm made one or two tool calls, all on SKILL.md or references/ (script); the prompt above is the one line that preceded the scenario-2 prompt from `../scenarios.md`, which followed it verbatim; no dispatch for this scenario failed
```

## Scoring

Units are the scenario-2 inventory in `../wave3-2026-08-07/rescore-2026-09-02.md`: U1 "Archive a Slack channel.", U2 the `MUST NOT` sentence, U3 the `channel_id` sentence, U4 the `Returns …` sentence, U5 the `channel_id` schema property, U6 the `confirmed` schema property, U7 `required` / `additionalProperties`.

| Rep | Assertion 1 — no R1 on the inline rules | A2.1 (`MUST NOT` sentence, U2) | E2 strict (U6 `confirmed`) | E2 per-statement |
| --- | --- | --- | --- | --- |
| 1 | ✓ — "Counts per rule: R1 0"; the guard list says inline marking "suffices in a compact document" | **R3 Verifiability**, "Severity: Material." — excluded (A2.1) | 1 — alternative A also adds "a `description` to the `confirmed` schema property" | 1 |
| 2 | ✓ — "Counts per rule: R1 0"; "its placement inside a mixed paragraph is not an embedding finding" | **R3 Verifiability**, "Severity: material" — excluded (A2.1) | 1 — the first alternative says "Also add a `description` to the `confirmed` property stating the same thing", and the second adds one to `confirmed` "naming what it attests" | 1 |
| 3 | ✓ — "Counts per rule: R1 0"; "per R1 inline marking is all a rule owes and embedding is not a finding" | **R3 Verifiability**, "Severity: material" — excluded (A2.1) | 1 — both alternatives add a `"description"` to the `confirmed` property | 1 |

Scored assertions: assertion 1 of `../scenarios.md` passes in every rep — **1/1 ×3**.
Assertions 2 and 3 are the ones the A2.1 exclusion affects: both are struck through in `../scenarios.md` and amended to point at the preregistration's Rerun classification, because the only finding either would have scored is the `MUST NOT` finding that A2.1 now records without counting.
Under the archived assertions each rep would have failed assertion 3, since none states a clean outcome; under the Rerun classification neither assertion is scored here.
Alternatives are labeled as an author decision in every rep ("Labeled alternatives, none selected"; "author decision between two labeled alternatives"; "author decision, because the text does not reveal whose confirmation is intended").

E9c: guard-lines true ×3; classification-table true ×3 (each rep prints an explicit statement-classification table); negative-safety-note true ×3.
Contract adherence: 3/3.

**Wave B reading.** The archived cell counted the `MUST NOT` sentence as an E2 false positive and carried the preregistration's R3 report obligation, because the criterion that made the sentence protected lived only in the preregistration and the arm could not read it.
That obligation no longer applies: the Wave B `SKILL.md` states the criterion itself at `:55-57` — a decidable trigger, "an ordinary domain predicate the reader can decide from the situation passes", and an exception decidable only when "the evidence that satisfies it is observable … naming a party is not, by itself, evidence".
Every rep now reasons in exactly those terms, splitting the sentence into a decidable trigger and an undecidable exception, which is why the Rerun classification records the finding as adjudication item A2.1 and counts it under neither endpoint.
What remains scored is the rider: all three rewrites propose describing the schema's `confirmed` property, a protected unit, so strict E2 is 1 per rep against the archived 2 per rep in the unit inventory in `../wave3-2026-08-07/rescore-2026-09-02.md`.
The per-statement and strict counts agree here, since the rider touches one clause.

## Scored Outputs (verbatim)

### With-skill, rep 1

> ## Audit: `archive_channel` tool description
>
> Document type: compact (a single flat `description` string, no sections). Under R1, inline marking is all a rule owes here, so rule/fact interleaving within the description is not itself a finding.
>
> ### Statement classification
>
> | Statement | Class |
> |---|---|
> | "Archive a Slack channel." | Load-bearing fact (tool purpose) |
> | "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller." | Binding rule (condition–action–exception) |
> | "Accepts only a channel_id, never a channel name." | Binding rule |
> | "Returns {archived: true, channel_id} on success, or a structured error on failure." | Load-bearing fact (tool semantics) |
> | `inputSchema` (`channel_id` required string; `confirmed` optional boolean, undocumented) | Load-bearing fact |
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> - Location: `description`, sentence 2.
> - Quoted text: "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
> - Why it fails: The trigger ("more than one active member") is decidable — an ordinary domain predicate the reader can resolve by looking the channel up. The exception is not. "Explicit confirmation from the caller" names a party and an act but no observable evidence; naming a party is not, by itself, evidence. The schema carries an optional `confirmed: boolean` that is the obvious candidate, but the description never says that `confirmed: true` is what satisfies the exception, never mentions `confirmed` at all, and never says what happens when it is omitted. Three things are therefore undecidable from the document: (a) whether passing `confirmed: true` discharges the obligation or some out-of-band confirmation is meant; (b) who "the caller" is — the invoking agent or the human it acts for — since if the agent is the caller it can satisfy the exception itself by setting the flag, which may or may not be the intended safeguard; and (c) whether the sentence binds the agent (a policy the agent can violate) or describes server-side enforcement (a fact: the server returns a structured error), which under the litmus test changes its class.
> - Severity: Material. The defect could plausibly change behavior (an agent self-confirms on its own judgment, or never learns the flag exists and either gets an error or archives) and prevents verification (no defined evidence for the exception).
> - Suggested rewrite: author decision; the document does not reveal the intended safeguard. Labeled alternatives, none selected:
>   - **A — the input is the evidence and confirmation must originate with the user:** "MUST NOT archive a channel with more than one active member unless `confirmed` is `true`. Set `confirmed: true` only after the user has explicitly approved archiving that specific channel." (Also add a `description` to the `confirmed` schema property stating the same.)
>   - **B — the check is server-enforced; describe it as tool semantics and keep the agent-side obligation separate:** "Archiving a channel with more than one active member requires `confirmed: true`; without it the tool returns a structured error and archives nothing. Pass `confirmed: true` only when the user has explicitly approved the archive."
>   - **C — confirmation is out-of-band and `confirmed` means something else:** name the observable evidence that satisfies the exception (an input, artifact, or recorded action) and document what `confirmed` actually controls.
>
> ### Not flagged (false-positive guards)
>
> - "Accepts only a channel_id, never a channel name." — binding, marked with explicit mandatory wording, decidable against the tool-call argument (Slack IDs vs names are distinguishable). Inline marking suffices in a compact document. No finding.
> - "Archive a Slack channel." and "Returns {...}" — load-bearing facts; their co-location with rules in a flat description is permitted by R1's compact-document clause. No finding.
> - R2: no hedged strength anywhere ("MUST NOT", "never" are explicit). Clean.
> - R4: the MUST NOT sentence is a condition–action–exception clause sharing one trigger and may stay together. Not a finding.
> - R5: no two statements prescribe incompatible outcomes for the same decision. Clean.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0. No finding carries a secondary id, so the per-rule total (1) equals the severity total (1).
>
> This is a well-marked compact description: both rules use explicit mandatory wording, strength is unambiguous, obligations are atomic, and no precedence question arises. The single defect is that the safety-critical exception on the archive rule — "explicit confirmation from the caller" — is not tied to any observable evidence, even though the schema ships an undocumented `confirmed` flag that is almost certainly meant to be that evidence. Because the gap sits on the one guard that prevents a destructive action, and because "the caller" leaves open whether the agent may confirm on its own, the finding is material and requires an author decision before a semantic-preserving rewrite can be claimed.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 2

> # Audit: `archive_channel` tool description
>
> Document type: compact MCP tool description (single flat description, no sections). Under R1, inline marking is all a rule owes here, and embedding is not a finding.
>
> ## Statement classification
>
> | # | Statement | Role |
> |---|---|---|
> | 1 | "Archive a Slack channel." | Discretionary context (purpose statement) |
> | 2 | "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller." | Binding rule (condition–action–exception) |
> | 3 | "Accepts only a channel_id, never a channel name." | Binding rule on the caller, doubling as a load-bearing fact about input semantics |
> | 4 | "Returns {archived: true, channel_id} on success, or a structured error on failure." | Load-bearing fact (tool semantics) |
> | 5 | `inputSchema` (`channel_id` required string; `confirmed` optional boolean; no additional properties) | Load-bearing facts (input contract) |
>
> ## Findings
>
> **R3 Verifiability**
> Location: `description`, sentence 2 (related: `inputSchema.properties.confirmed`).
> Quoted text: "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
> Why it fails: the trigger is decidable (a member count bounded by a quantity), but the exception is not. "Explicit confirmation from the caller" names a party without naming the observable evidence that satisfies it. The schema exposes a `confirmed` boolean that is the obvious candidate, but the description never links the two, and the schema carries no description for the field. A reader cannot tell from the document whether the exception is satisfied by passing `confirmed: true`, by the caller having obtained confirmation from a human before calling, or by something else; a tool trace therefore cannot be checked for compliance without assuming a mapping the document does not state. This is an author decision because the two readings differ in what counts as satisfying the exception.
> Severity: material — the undefined exception could plausibly change behavior (an agent either refuses a legitimately confirmed archive because it does not know the mechanism, or passes `confirmed: true` with no confirmation behind it because nothing defines what the flag attests) and prevents verification against tool calls.
> Suggested rewrite: author decision between two labeled alternatives; both keep the mandatory strength and the single condition–action–exception unit.
> - If `confirmed: true` is itself the confirmation: "MUST NOT archive a channel with more than one active member unless `confirmed` is `true`. Passing `confirmed: true` is the caller's explicit confirmation." Also add a `description` to the `confirmed` property stating the same thing.
> - If the confirmation must originate outside the call (for example, from the end user) and `confirmed: true` records that it was obtained: "MUST NOT archive a channel with more than one active member unless the caller has obtained explicit confirmation and passes `confirmed: true` to record it." Also add a `description` to `confirmed` naming what it attests. This reading adds an obligation the current text only implies, so it must be the author's choice, not the auditor's.
>
> ## Not flagged (false-positive guards)
>
> - Sentence 2 under R1/R2: the rule is marked with explicit mandatory wording ("MUST NOT") in a compact document, so its placement inside a mixed paragraph is not an embedding finding, and its strength is unambiguous.
> - Sentence 2 under R3, trigger side: "more than one active member" is an ordinary domain predicate bounded by a quantity; applying it takes a lookup, not unbounded judgment.
> - Sentence 2 under R4: condition (more than one active member), action (do not archive), and exception (confirmation) share one trigger and may stay together as one unit.
> - Sentence 3: "Accepts only a channel_id, never a channel name" is marked ("never"), mandatory, and checkable against the `channel_id` argument in a tool call. It also serves as a load-bearing fact about input semantics; in a compact description that dual role owes nothing further.
> - Sentence 4 and the `inputSchema`: load-bearing facts, correctly stated as facts rather than rules.
> - R5: no two rules prescribe incompatible outcomes on any realistic input. The optional `confirmed` field in the schema is consistent with the rule (confirmation is only needed above one active member), so schema and description do not conflict.
>
> ## Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0.
> No finding carries a secondary rule id, so the per-rule total of one equals the one finding counted by severity.
>
> This is a well-separated compact description: its two binding rules are marked with explicit mandatory wording, its tool semantics are stated as facts, and no hedges, compound obligations, or reachable conflicts appear. The single defect is that the archive rule's exception names a party ("explicit confirmation from the caller") rather than the observable input that satisfies it, while the schema's undocumented `confirmed` boolean sits unlinked beside it. Resolving that author decision — and giving `confirmed` a one-line description — would leave the document clean.
>
> ## Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.

### With-skill, rep 3

> ## Audit: `archive_channel` tool description
>
> Target type: compact document (a single flat description with no labeled sections), so per R1 inline marking is all a rule owes and embedding is not a finding.
>
> ### Classification
>
> | Statement | Role |
> |---|---|
> | "Archive a Slack channel." | Discretionary context (purpose framing) |
> | "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller." | Binding rule (condition–action–exception) |
> | "Accepts only a channel_id, never a channel name." | Binding rule (input constraint) |
> | "Returns {archived: true, channel_id} on success, or a structured error on failure." | Load-bearing fact (tool semantics) |
> | `inputSchema` (`channel_id` required string; `confirmed` optional boolean, undescribed; `additionalProperties: false`) | Load-bearing fact (tool semantics) |
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> - Location: `description`, second sentence; also `inputSchema.properties.confirmed`, which carries no description.
> - Quoted text: "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
> - Why it fails: the exception clause names a party ("the caller") but not the observable evidence that satisfies it. The schema exposes a `confirmed` boolean that is almost certainly that evidence, yet nothing in the document ties "explicit confirmation" to `confirmed: true`, and the `confirmed` property has no description of its own. Two readers can therefore follow the rule differently: one obtains confirmation conversationally and never sets the flag (call fails with a structured error, or worse, the server does not gate on it); another sets `confirmed: true` on its own authority, since "the caller" is the agent itself and the text does not say whose confirmation is meant. Neither reading can be checked against tool traces without knowing what counts. Secondary: "active member" is undefined (not deactivated? recently posted?); this is closer to an ordinary domain predicate the server can decide, so it is noted rather than flagged on its own.
> - Severity: material — the defect can plausibly change behavior (self-confirmation vs. human confirmation) and prevents verification of the exception.
> - Suggested rewrite: author decision, because the text does not reveal whose confirmation is intended.
>   - (a) If the `confirmed` input is the evidence and the caller's own assertion suffices: "MUST NOT archive a channel with more than one active member unless `confirmed` is `true`." Add to the `confirmed` property: `"description": "Set to true to confirm archiving a channel that has more than one active member."`
>   - (b) If human approval is intended: "MUST NOT archive a channel with more than one active member unless the caller has obtained the user's explicit approval for this specific archive and passes `confirmed: true`." Add to the `confirmed` property: `"description": "True only after the user has explicitly approved archiving this channel; required when the channel has more than one active member."`
>   - Under either choice, optionally replace "active member" with the observable count the server actually uses (e.g. "more than one non-deactivated member").
>
> ### Not flagged (false-positive guards)
>
> - "Accepts only a channel_id, never a channel name." — a marked, explicit-strength, verifiable rule (check the argument against Slack's ID format). That the schema does not enforce a `pattern` is a schema-hardening point outside this skill's axis.
> - "Returns {archived: true, channel_id} ..." — load-bearing tool semantics; correctly stated as fact, not as a rule, and co-location is fine in a compact document.
> - R4: the MUST NOT sentence is one condition–action–exception clause sharing a single trigger, permitted as one unit.
> - R5: no two rules prescribe incompatible outcomes for the same decision; `confirmed` being optional in `required` is consistent with confirmation being needed only in some cases.
> - R2: no hedged strength anywhere; both rules use mandatory wording.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0. Per-rule total (1) equals the finding count (1).
>
> This is a tightly written compact tool description: both rules are inline-marked with unambiguous mandatory wording, the return contract and schema are stated as facts rather than mixed into rule text, and no realistic precedence conflict exists. The single defect is that the confirmation exception on the archive rule names a party rather than the observable evidence that discharges it, leaving the `confirmed` input and the rule's "explicit confirmation" unconnected and leaving open whether the agent may confirm on its own behalf. Resolving that one author decision (and describing the `confirmed` property) would make the document clean.
>
> **Safety note:** none. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
