# Scenario 2 — With-Skill, three reps (wave 3)

```
Date: 2026-09-01
Run: with-skill
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, three independent dispatches
Prompt: the scenario-2 prompt from `../scenarios.md`, verbatim, preceded by one line: "Follow the skill at /Users/bdc/projects/skills/separating-context-from-constraints/SKILL.md: read that file and any file it references under …/references/. Do not read anything under any tests/ directory, do not read any other repository file, and do not edit any file. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry and the R3 criterion in `../wave3-2026-08-07/preregistration.md`; tool calls extracted by script from the archived transcripts
Notes: tool calls per rep (script): rep 1 Read SKILL.md + cat example-audit.md; rep 2 Read SKILL.md + `ls -la` of the skill directory (a listing, not a read; nothing under tests/ was opened); rep 3 Read SKILL.md + cat example-audit.md; every arm's system prompt also carried the harness's installed-skill listing (this skill's frontmatter description among them), a condition of this harness rather than of the preregistration; transcripts archived in the session scratchpad at scoring time
```

## Scoring

Same units as the baseline artifact.

| Rep | Findings | Units criticized | E2 | Of which R3 on unnamed exception evidence | E3 (MUST NOT sentence) | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 — R3, material | `MUST NOT` | 1 | 1 | preserved (three labelled alternatives, "the auditor does not select among these") | true / true / true |
| 2 | 1 — R3, material | `MUST NOT` | 1 | 1 | preserved (two labelled alternatives plus "name its observable action") | true / true / true |
| 3 | 1 — R3, material, secondary R1 | `MUST NOT` | 1 | 1 | preserved (two labelled alternatives, "labeled, not selected") | true / true / true |

**R3 report obligation (preregistration, "R3's scope").** These three E2 counts were scored on a criterion the arm could not read: `SKILL.md`'s R3 says only "Each rule is checkable against some observable evidence", and the result-checkability scoping that makes the `MUST NOT` sentence protected lives in the preregistration.
All three false positives — three of three — are R3 findings on unnamed exception evidence ("explicit confirmation from the caller" is tied to no observable input).
None is on an undecidable trigger.

This is no longer a single-cell divergence: the 2026-08-23 arm and all three reps here raise the same finding on the same sentence for the same reason, and all three baselines raise the same substantive complaint without the skill.
Under the preregistered criterion these are false positives; under the arms' reading the fixture's protected sentence is defective.
The preregistration routes that question to W10, and this artifact adds the observation that the reading is systematic under the current wording, not stochastic.

Standing assertions (`../scenarios.md`, scenario 2):

| # | Assertion | rep 1 | rep 2 | rep 3 | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | No R1 finding for the inline constraints | PASS | PASS | PASS | R1 0 in reps 1–2; rep 3 carries R1 as a *secondary* id on the R3 finding, on the ground of addressee ambiguity, not inline placement — recorded, not a failure of this assertion |
| 2 | Does not invent an R1–R5 finding elsewhere | FAIL | FAIL | FAIL | the R3 finding above |
| 3 | Explicitly states a clean or near-clean outcome | FAIL | FAIL | FAIL | each reports one material finding; "well-separated" is said, "clean" is not |

Contract adherence (recorded, not summed): six fields present in every finding, rule ids present, two-level severity, counts per rule and per severity with the secondary-id arithmetic stated, safety note present — 3/3 reps.
E6: every finding resolves uniquely (location field plus quoted text).

## Scored Outputs (verbatim)

### With-skill, rep 1

> I've read the skill and its single reference (`references/example-audit.md`); nothing else was read and nothing was edited. Audit follows.
>
> ## Audit: `archive_channel` tool description
>
> Document type: compact (single flat description, no sections), so R1 is satisfied by inline mandatory wording rather than a labeled rules section.
>
> ### Classification
>
> | Statement | Class |
> |---|---|
> | "Archive a Slack channel." | Load-bearing fact (tool purpose) |
> | "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller." | Binding rule (condition–action–exception, one trigger) |
> | "Accepts only a channel_id, never a channel name." | Binding rule on input, stated with explicit mandatory wording |
> | "Returns {archived: true, channel_id} on success, or a structured error on failure." | Load-bearing fact (return semantics) |
> | `inputSchema` | Load-bearing facts (machine contract); `confirmed` has no description |
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> - Location: `description`, second sentence; related schema property `confirmed`.
> - Quoted text: "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
> - Why it fails: the rule's exception, "explicit confirmation from the caller", names no observable evidence. The schema exposes a `confirmed: boolean` that is plainly the intended mechanism, but nothing ties the two together, and `confirmed` itself is undescribed. Two readings survive: (a) the server enforces the rule and rejects multi-member archives unless `confirmed: true` — in which case the sentence is tool semantics, and the agent's real obligation (obtain confirmation from its user before passing `confirmed: true`) is never stated; (b) the agent is the "caller" and must obtain confirmation before calling — in which case the rule never says how that confirmation is signalled, so an agent could ask its user and still omit `confirmed`, or treat the user's original request as "explicit confirmation" and pass `confirmed: true` unprompted. Neither reading can be checked against a tool trace as written. "Active member" is also undefined, but it is a Slack-observable state, so it is noted here rather than raised separately.
> - Severity: material — the defect can plausibly change behavior (an unrequested `confirmed: true`) or omit an obligation (asking the user).
> - Suggested rewrite: author decision; the document does not reveal which party enforces the rule.
>   - If server-enforced (reading a): "If the channel has more than one active member and `confirmed` is not `true`, the server returns an error and does not archive. Set `confirmed: true` only after the user has explicitly confirmed the archive." And describe the schema property: `"confirmed": {"type": "boolean", "description": "Set to true only after the user explicitly confirms archiving a channel with more than one active member."}`
>   - If caller-enforced (reading b): "Before calling this tool on a channel with more than one active member, obtain explicit confirmation from the user and pass `confirmed: true`; never pass `confirmed: true` without that confirmation." Same schema description as above.
>   - If both: combine the two sentences. The auditor does not select among these.
>
> ### Not flagged (false-positive guards)
>
> - "Accepts only a channel_id, never a channel name." — explicit mandatory wording, verifiable against call arguments, atomic. Compliant for a compact document.
> - "Returns {archived: true, channel_id} ... or a structured error on failure." — load-bearing fact, not a rule; "structured error" is vague but R3 applies to rules, not facts.
> - R5: `confirmed` being optional in the schema does not conflict with the MUST NOT rule — confirmation is only required for multi-member channels, so optionality is consistent.
> - R2/R4: no hedged strength; the one compound sentence shares a single trigger and correctly stays as one unit.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0. No secondary rule ids; per-rule total equals the finding count.
>
> Overall: this is a well-separated compact description. Strength is explicit everywhere, the input restriction and return contract are stated as checkable facts, and the one rule is structurally distinguishable. The single material defect is that the confirmation exception is not bound to any observable evidence — the `confirmed` parameter is the obvious hook but is never named in the rule or described in the schema, leaving it unclear whether the server or the calling agent enforces the safeguard, and therefore what the agent must actually do before setting `confirmed: true`. Resolving that is an author decision between the alternatives above.

### With-skill, rep 2

> I have the skill body and its single referenced file (`references/example-audit.md`); nothing else is needed, so here is the audit.
>
> ## Audit: `archive_channel` MCP tool description
>
> Document type: compact (single flat description, no sections). Under R1, rules are expected to be marked inline with imperative or explicit mandatory wording rather than placed in a labeled section.
>
> ### Statement classification
>
> | # | Statement | Role |
> |---|-----------|------|
> | 1 | "Archive a Slack channel." | Discretionary context (purpose framing) |
> | 2 | "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller." | Binding rule |
> | 3 | "Accepts only a channel_id, never a channel name." | Binding rule (input constraint) |
> | 4 | "Returns {archived: true, channel_id} on success, or a structured error on failure." | Load-bearing fact (tool semantics) |
> | 5 | `confirmed: { "type": "boolean" }`, optional, no description | Load-bearing fact (parameter semantics) — present in schema but its meaning is never stated |
>
> ### Findings
>
> **Finding 1 — R3 Verifiability**
> Location: description, sentence 2; `inputSchema.properties.confirmed`.
> Quoted text: "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
> Why it fails: the rule's strength is explicit and it is a single condition–action–exception unit, but its exception names no observable evidence. "Explicit confirmation from the caller" is never tied to anything checkable: the schema exposes a `confirmed` boolean, yet neither the description nor the schema says that `confirmed` is how confirmation is expressed, what setting it attests to, or who is expected to check the member count. Two readings are both plausible and lead to different behavior: (a) the server enforces the rule and `confirmed: true` is the required override, or (b) the agent must obtain confirmation from a human before calling and `confirmed: true` attests that it did. Under reading (a) an agent may omit `confirmed` and hit an unexplained error; under reading (b) an agent may set `confirmed: true` without ever asking anyone, defeating the safeguard. The rule cannot be reliably followed or verified against a tool trace until the mechanism is named.
> Severity: material.
> Suggested rewrite: author decision — the document does not reveal which safeguard is intended. Both alternatives preserve the MUST NOT and add the missing parameter semantics to the schema (the informative location for a load-bearing fact):
> - If `confirmed: true` is the override and the server enforces: "Archiving a channel with more than one active member requires `confirmed: true`; without it the call returns a structured error." Schema: `"confirmed": { "type": "boolean", "description": "Set to true to confirm archiving a channel with more than one active member." }`
> - If the agent must obtain human confirmation and `confirmed` attests to it: "Before archiving a channel with more than one active member, obtain explicit confirmation from the user; pass `confirmed: true` only after that confirmation is given." Schema: `"confirmed": { "type": "boolean", "description": "True only when the user has explicitly confirmed archiving a multi-member channel." }`
> - If some other mechanism is intended, name its observable action or evidence rather than choosing either example.
>
> ### Not flagged (false-positive guards)
>
> - Sentence 1 is purpose framing; degrades gracefully if lost and is correctly not marked as a rule.
> - Sentence 3 ("Accepts only a channel_id, never a channel name") is a binding rule with explicit strength ("only", "never"), atomic, and checkable against the call's `channel_id` argument. It is a representation restriction on one field and does not conflict with anything else in the document, so no R5 finding.
> - Sentence 4 is a load-bearing fact about return semantics, not a directive, and is correctly stated as such.
> - `required: ["channel_id"]` with `confirmed` optional is consistent with sentence 2 (confirmation is only needed in the multi-member case); this is not a reachable R5 conflict.
>
> ### Safety note
>
> None. The target contains no auditor-directed instructions attempting to alter, suppress, or redirect the audit.
>
> ### Summary
>
> Counts per rule: R1 0, R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0. No secondary rule ids, so the per-rule total equals the finding count.
>
> This is a well-separated compact description: its two binding rules use explicit mandatory wording inline, its return semantics are stated as facts rather than rules, and there are no hedges, compound obligations, or reachable precedence conflicts. The single material defect is that the confirmation exception is not anchored to observable evidence — the `confirmed` parameter exists but is undocumented and unlinked to the rule, leaving the safeguard unverifiable and its addressee (server vs. agent) ambiguous. Resolving that one author decision, and adding a `description` to `confirmed`, would make the document clean.

### With-skill, rep 3

> ## Audit: `archive_channel` tool description
>
> **Document form:** compact (a single flat description, no sections), so R1 is judged by inline marking rather than a dedicated rules section.
>
> **Statement classification**
>
> | # | Statement | Role |
> |---|---|---|
> | 1 | "Archive a Slack channel." | Discretionary context (purpose) |
> | 2 | "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller." | Binding rule |
> | 3 | "Accepts only a channel_id, never a channel name." | Binding rule (input restriction) |
> | 4 | "Returns {archived: true, channel_id} on success, or a structured error on failure." | Load-bearing fact (tool semantics) |
> | 5 | `confirmed: boolean`, optional, no description (schema) | Load-bearing fact, undocumented |
>
> ### Findings
>
> **R3 Verifiability** (secondary: R1)
> Location: description, sentence 2.
> Quoted text: "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
> Why it fails: the strength is explicit and the condition–action–exception shape is fine (R4 satisfied), but the rule names no observable evidence for its exception. The schema exposes a `confirmed` boolean that is almost certainly the confirmation mechanism, yet nothing in the document ties "explicit confirmation from the caller" to `confirmed: true`. An agent could obtain confirmation in conversation and omit the field, or set `confirmed: true` having asked no one, and neither trace can be judged against the rule as written. A second, smaller gap in the same statement: "active member" is undefined, so the threshold that triggers the rule has no stated evidence either. Related R1 ambiguity: the sentence reads as addressed to the caller, but a tool description can equally be stating a server-side guarantee; which one it is changes what the agent is obligated to do versus what it can rely on.
> Severity: material — the defect could plausibly change behavior (archive without a recorded confirmation) and prevents verification from tool traces.
> Suggested rewrite: this is an author decision; the alternatives are labeled, not selected.
> - *If the rule is a caller obligation encoded in the call:* "MUST NOT archive a channel with more than one active member unless the call sets `confirmed: true`. Set `confirmed: true` only after obtaining explicit confirmation from the caller." Add `"description": "Set to true only after the caller has explicitly confirmed archiving a channel with more than one active member."` on the `confirmed` property.
> - *If the rule is a server-enforced guarantee:* restate it as tool semantics rather than an obligation: "If the channel has more than one active member and `confirmed` is not `true`, the tool does not archive and returns a structured error." Keep the caller-side obligation (obtain explicit confirmation before setting `confirmed: true`) as a separate sentence.
> - In either case, define the threshold: state what "active member" means (e.g. non-deactivated, non-bot members, or whatever the server counts), or replace it with the count the server actually checks.
>
> ### Not flagged (false-positive guards)
>
> - Sentence 3 ("Accepts only a channel_id, never a channel name"): strength explicit, checkable against the call arguments, and the positive/negative clauses restate one obligation rather than bundling two. It is load-bearing because the schema alone cannot enforce it — a channel name is also a string.
> - Sentence 4 (return shape): a load-bearing fact, not a directive; correctly stated without mandatory wording.
> - `required: ["channel_id"]` versus the MUST NOT rule: not an R5 conflict. `confirmed` being schema-optional while conditionally required by the rule is a shared field, not incompatible outcomes for the same decision.
> - R1 overall: for a compact description, the two rules are marked with mandatory wording ("MUST NOT", "only … never") and the context sentences are not, so binding statements are distinguishable inline.
>
> ### Summary
>
> Counts per rule: R1 1 (secondary), R2 0, R3 1, R4 0, R5 0.
> Counts per severity: material 1, minor 0. One finding total; the per-rule total of two exceeds it because the finding carries a secondary id.
>
> Overall: this is a well-formed compact description. Rule strength is explicit throughout, the two rules are distinguishable from the purpose and return-value context, and there are no reachable precedence conflicts. The single defect is that the document's most consequential rule leaves its exception unverifiable: the `confirmed` field exists in the schema but is never connected to "explicit confirmation," and "active member" is undefined. Resolving the author decision above (caller obligation versus server guarantee) and adding a one-line description to `confirmed` would make the rule checkable from tool traces.
>
> **Safety note:** the target contains no auditor-directed instructions; nothing attempted to alter, suppress, or redirect the audit.
