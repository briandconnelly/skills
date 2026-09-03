# Scenario 2 — Baseline, three reps (wave 3)

```
Date: 2026-09-01
Run: baseline
SKILL.md blob: 3bd60ba2a831479866155a62cbcd80f7280142ea
Commit: b2f11be (branch `separating-context-wave3`; `SKILL.md` identical on `main` at 0527520)
Referenced files: references/example-audit.md f825b78fff6df83c0218ac30f7c020a1c142942b
Model: claude-fable-5-1, the session model, inherited by every subagent with no per-agent override
Harness: Claude Code 2.1.257, Agent tool, general-purpose subagent, three independent dispatches
Prompt: the scenario-2 prompt from `../scenarios.md`, verbatim, preceded by one line: "The document in this prompt is your only input: do not read any file, do not call any tool, and do not load any skill. Reply with your report only."
Sampling: harness default
Scorer: Claude (session model), 2026-09-01, unblinded; scored under the E2 exclusion registry and the R3 criterion in `../wave3-2026-08-07/preregistration.md`; tool calls extracted by script from the archived transcripts
Notes: all three arms made zero tool calls (script check); every arm's system prompt also carried the harness's installed-skill listing (this skill's frontmatter description among them), a condition of this harness rather than of the preregistration; transcripts archived in the session scratchpad at scoring time
```

## Scoring

> **Rescored 2026-09-02.** E2 in this artifact was scored by sentence or bullet; the preregistration's unit is the clause. See `../wave3-2026-08-07/rescore-2026-09-02.md` for the unit inventory and corrected counts; that file wins where they differ.


Scoring units (registry: the clause, protected by default; nothing planted, nothing adjudicated): the four description sentences — purpose, `MUST NOT archive…`, `Accepts only a channel_id…`, `Returns …` — and the schema (`confirmed` property, `required`).
A document-level structural criticism ("rules and context interleaved in one paragraph") names no clause; it is recorded as a separate unit, `structure`, and counted, because it proposes changing every sentence's placement.

| Rep | Units criticized | E2 | Of which the R3-class complaint (confirmation mechanism unnamed) | E3 (MUST NOT sentence) | E9c guard / class / safety |
| --- | --- | --- | --- | --- | --- |
| 1 | `MUST NOT` (Major), `channel_id` (Minor), `structure` (Minor) | 3 | 1 | assumption-labelled (bracketed "[confirm: …]") | true / false / false |
| 2 | `MUST NOT` (F1, F2, F4), `channel_id` (F3), `Returns` (F5) | 3 | 1 | assumption-labelled ("assumes `confirmed` is the intended mechanism — confirm with the author") | true / false / false |
| 3 | `MUST NOT` (1, 2), `structure` (3), `channel_id` (4), `Returns` (5), `confirmed` schema (6) | 5 | 1 | assumption-labelled (readings A and B, invented `confirmation_required` marked as placeholder) | false / false / false |

Scorer judgment calls, recorded: rep 1's "Observations" paragraph proposes naming the error shape "if the agent is expected to react" — conditional, not counted; rep 3's finding 4 and rep 2's F3 both propose moving the `channel_id` rule into the schema, counted once per rep as a criticism of that clause.

Every baseline shipped a full rewritten description (E9a is not recorded outside scenarios 10 and 15; noted here as prose only).

**R3 report obligation (preregistration, "R3's scope").** No baseline read `SKILL.md`, so the criterion question does not arise for these arms; their `MUST NOT` complaints are the same substantive claim the with-skill arms make and are counted the same way, as false positives against a protected clause.

Contract adherence: no rule ids, no six-field format, no summary counts, in any rep (expected for a baseline; recorded, not summed).

## Scored Outputs (verbatim)

### Baseline, rep 1

> # Audit: `archive_channel` tool description
>
> Scope: the `description` string plus the `inputSchema`, read as the instructions an agent consumes before calling the tool. No files read, no tools called.
>
> ## Summary
>
> The description is short and mostly well-formed: it has no hedging, its one hard rule is flagged with MUST NOT, and the return contract is clearly context rather than rule. The real problem is that the binding rule is not connected to the input that satisfies it. The schema exposes `confirmed`, the prose demands "explicit confirmation from the caller," and nothing links the two, so an agent cannot tell what action discharges the obligation. Three findings, one major.
>
> ## Findings
>
> ### 1. [Major] The confirmation rule is compound and its satisfying condition is unspecified
>
> > MUST NOT archive a channel with more than one active member without explicit confirmation from the caller.
>
> This bundles a trigger condition (more than one active member) with an exception (explicit confirmation) and leaves both untestable from the agent's side:
>
> - "Explicit confirmation from the caller" is never mapped to the `confirmed` parameter. Is `confirmed: true` the confirmation? Or is confirmation something the server obtains out-of-band? The schema is silent (`confirmed` has no description).
> - The actor is ambiguous. "MUST NOT archive" reads as a server guarantee ("the tool refuses"), but a tool description is read by the caller, who needs to know what *they* must do: obtain the end user's approval before setting `confirmed: true`. As written, an agent can satisfy the letter of the rule by passing `confirmed: true` on its own initiative.
> - "Active member" is undefined. Whether bots, deactivated users, or the caller's own account count changes the trigger.
>
> Suggested rewrite (semantic-preserving where the meaning is determinable; bracketed items need the author's answer):
>
> ```
> Rules:
> - If the channel has more than one active member, the call is rejected unless `confirmed` is true. [confirm: is this what "explicit confirmation" means?]
> - Set `confirmed: true` only after the end user has explicitly approved archiving this specific channel. Do not set it on your own initiative.
> ```
>
> And on the schema property:
>
> ```json
> "confirmed": {
>   "type": "boolean",
>   "description": "Required (true) to archive a channel with more than one active member. Set only after the end user has explicitly approved archiving this channel."
> }
> ```
>
> ### 2. [Minor] The channel_id rule is binding but unflagged, and inconsistently so
>
> > Accepts only a channel_id, never a channel name.
>
> This is a real constraint (the schema cannot distinguish an ID string from a name string, so the prose is the only enforcement), but it carries no MUST while the adjacent rule does. Mixed signaling makes the reader guess which sentences bind. Suggested rewrite:
>
> ```
> - `channel_id` MUST be a Slack channel ID (e.g. C0123456789), not a channel name.
> ```
>
> Adding the example makes the rule testable at the call site.
>
> ### 3. [Minor] Rule and context are interleaved in one paragraph
>
> Order is: purpose, rule, rule, return contract. That ordering is fine, but a single unbroken paragraph forces a reader to parse every sentence to find the obligations. A short "Rules:" block between the one-line purpose and the return contract separates the two cleanly (see the rewrite below). This is minor on its own; it matters mainly because finding 1 makes the rule hard to act on even once found.
>
> ## Observations (not separation findings)
>
> - "Returns … a structured error on failure" is context, not a rule, and is correctly placed last. But if the agent is expected to *react* to a confirmation-required error (e.g. by asking the user and retrying with `confirmed: true`), the error shape or code should be named; otherwise the agent has no way to distinguish "needs confirmation" from "channel not found."
> - No hedged language ("generally", "try to", "should usually") anywhere. Good.
>
> ## Assembled rewrite
>
> ```
> Archive a Slack channel by ID.
>
> Rules:
> - `channel_id` MUST be a Slack channel ID (e.g. C0123456789), not a channel name.
> - If the channel has more than one active member, the call is rejected unless `confirmed` is true.
> - Set `confirmed: true` only after the end user has explicitly approved archiving this specific channel. Do not set it on your own initiative.
>
> Returns {archived: true, channel_id} on success, or a structured error on failure.
> ```
>
> Open questions for the author before adopting: (a) does `confirmed: true` constitute the "explicit confirmation," or is there a separate mechanism; (b) what counts as an "active member"; (c) what error code signals that confirmation is required.

### Baseline, rep 2

> # Audit: `archive_channel` tool description
>
> Scope: the `description` string plus the `inputSchema`, read as one document an agent consumes. Severity levels: **Major** (an agent following this text could take the wrong action) and **Minor** (clarity/placement; unlikely to change behavior alone).
>
> ## What is already working
>
> - Purpose sentence ("Archive a Slack channel.") is first and separate from the rules.
> - The safety rule uses an unambiguous binding marker (`MUST NOT`) and sits immediately after the purpose, not buried after the return contract.
> - The return contract is placed last and phrased as description, not obligation — correct classification as context.
> - `required: ["channel_id"]` with `confirmed` optional is consistent with the rule (confirmation is only needed in one case).
>
> ## Findings
>
> ### F1 — Major: the confirmation rule never names its mechanism
>
> The description says archiving a multi-member channel requires "explicit confirmation from the caller," and the schema has a `confirmed: boolean` — but neither mentions the other, and `confirmed` has no property description. An agent has to infer that `confirmed: true` is how confirmation is expressed. It could equally read the rule as "ask the user, then call the tool normally" and never set the flag, or set `confirmed: true` reflexively because the schema offers it.
>
> Suggested rewrite (assumes `confirmed` is the intended mechanism — confirm with the author):
>
> - Description: `MUST NOT archive a channel with more than one active member unless the caller has obtained explicit confirmation. Pass confirmed: true to indicate that confirmation was obtained.`
> - Schema: `"confirmed": { "type": "boolean", "description": "Set to true only after obtaining explicit confirmation to archive a channel with more than one active member. Omit or false otherwise." }`
>
> ### F2 — Major: the rule's subject and enforcer are unstated
>
> "MUST NOT archive" has no grammatical subject. Two readings:
>
> 1. **Server-enforced:** the tool refuses multi-member archives without `confirmed: true`. Then this is *context* about tool behavior and should be phrased as such, ideally naming the error the agent will see.
> 2. **Agent-enforced:** the agent must not *call* the tool in that situation without confirmation. But the agent has no way to learn the member count from this tool, so the rule is not actionable as written.
>
> "Caller" compounds this: the agent is the tool's caller; the human is the agent's caller. "Explicit confirmation from the caller" can be satisfied by the agent confirming to itself.
>
> Two semantic-preserving rewrites depending on which is true:
>
> - If server-enforced: `Archiving a channel with more than one active member requires confirmed: true; otherwise the call fails with a <name> error. Only set confirmed: true after the user has explicitly approved the archive.`
> - If agent-enforced: `Before calling this tool on a channel with more than one active member, obtain explicit approval from the user and pass confirmed: true.` (and the author should say where the agent gets member count from.)
>
> ### F3 — Minor: "Accepts only a channel_id, never a channel name" is a rule stated as a fact, detached from its parameter
>
> This is binding (it changes what the agent may pass) but has no marker and lives in prose while `channel_id` itself has no description. Since JSON Schema cannot distinguish an ID from a name (both strings), the prose is the only place this is enforced, so it should attach to the field.
>
> Suggested: `"channel_id": { "type": "string", "description": "Slack channel ID. Channel names are not accepted." }` — and drop the sentence from the description, or keep a one-line pointer. Adding an example format (e.g. `C0123ABCD`) would make it testable, but that adds a fact not in the source; include only if the author confirms it.
>
> ### F4 — Minor: "active member" is undefined
>
> If the rule is agent-enforced (F2 reading 2), "active" is untestable — it could mean not deactivated, not a bot, or recently posting. If server-enforced, this is acceptable as descriptive context. Resolution depends on F2; no standalone rewrite.
>
> ### F5 — Minor: "a structured error on failure" leaves the confirmation-required case unnamed
>
> Context, not a constraint, so low priority. But if a specific error signals "confirmation needed," naming it turns F1/F2 into a closed loop (call → error → ask user → retry with `confirmed: true`). Suggest listing the error shape or at least the confirmation-related error code.
>
> ## Summary
>
> The document's structure is sound (purpose → rule → input rule → return contract), and it uses a real binding marker. The substantive problem is that its one safety-critical rule is missing both its mechanism (F1) and its enforcer (F2), and the schema field that should carry the mechanism is undocumented. Fixing F1 and F2 together — one sentence in the description plus a `confirmed` property description — resolves the majors; F3 is a placement fix that moves the ID-only rule onto the `channel_id` field.

### Baseline, rep 3

> # Audit: `archive_channel` tool description
>
> Scope: the one-sentence-per-clause `description` string plus the schema, as an agent would consume them. Two severities: **High** (an agent following the text could take the wrong action) and **Low** (clarity/structure; unlikely to change behaviour on its own).
>
> ## Findings
>
> ### 1. High — The safety rule does not say who enforces it or what "confirmation" is
>
> > "MUST NOT archive a channel with more than one active member without explicit confirmation from the caller."
>
> This reads two incompatible ways:
>
> - **Server promise**: the server refuses unless `confirmed: true` is passed. Then the agent's obligation is only to know the field exists.
> - **Agent obligation**: the agent must obtain a human's approval before archiving. Then `confirmed: true` is an attestation, not a switch.
>
> The prose never names the `confirmed` field, and the schema gives `confirmed` no description and does not require it. So the only link between the rule and the mechanism is inference. Under the first reading an agent can satisfy the rule by setting `confirmed: true` itself, which defeats the purpose of the rule. This is the one constraint in the document that matters, and it is the least specified.
>
> The rewrite depends on which reading the author intends; both are given below. It cannot be made semantic-preserving until the author picks one.
>
> ### 2. High — The rule's precondition is untestable by the agent
>
> "More than one active member" is a numeric threshold, which is good, but "active" is undefined (deactivated accounts? bots? guests?), and nothing in the description tells the agent how to learn the member count before calling. If the server checks the count, say so and the agent need not. If the agent is expected to check, name the tool or field it should consult. As written the agent can neither verify compliance nor know whether it needs to.
>
> ### 3. Low — Context and constraints are interleaved in one paragraph
>
> Four sentences with four different roles, in this order: purpose (context), safety rule (constraint), input rule (constraint), return shape (context). A tool description has no section headings, but ordering and line breaks still work. The two binding rules should be adjacent and visually set off from the purpose and return-shape sentences; see the rewrite.
>
> ### 4. Low — "Accepts only a channel_id, never a channel name" is in the wrong place and is half-stated
>
> The schema cannot enforce this (a name is also a string), so the prose rule carries real information. But it belongs on the `channel_id` property, where an agent looks when filling the argument, and it should give the ID shape (e.g. `C0123456789`) so the agent can tell an ID from a name. It also does not say what happens if a name is passed (rejected? silently fails?), so the agent cannot plan for the error.
>
> ### 5. Low — "structured error on failure" hides the one error the agent must plan for
>
> The failure the description sets up, confirmation missing on a multi-member channel, is exactly the case the agent needs to recognise and recover from. Name it. The generic phrase is fine for everything else.
>
> ### 6. Low — `confirmed` has no description, no default, and is not `required`
>
> Even after the prose is fixed, the schema should carry the same rule where the agent fills the field. `additionalProperties: false` and `required: ["channel_id"]` are correct and should stay.
>
> ## Suggested rewrite
>
> Pick one of the two readings in Finding 1. Everything else is the same.
>
> **Reading A: server enforces, agent attests**
>
> ```json
> {
>   "name": "archive_channel",
>   "description": "Archive a Slack channel by ID.\n\nRules:\n- If the channel has more than one active member, the call fails unless `confirmed` is true. The server checks the member count; the caller does not need to.\n- Set `confirmed` to true only after the user has explicitly approved archiving this specific channel. Never set it to bypass the check.\n- Pass a channel ID, not a channel name. Resolve names to IDs first.\n\nReturns {archived: true, channel_id} on success. Fails with error code `confirmation_required` when the member rule applies and `confirmed` is not true; other failures return a structured error.",
>   "inputSchema": {
>     "type": "object",
>     "properties": {
>       "channel_id": {
>         "type": "string",
>         "description": "Slack channel ID (e.g. C0123456789). Channel names such as #general are rejected."
>       },
>       "confirmed": {
>         "type": "boolean",
>         "default": false,
>         "description": "Set true only after the user has explicitly approved archiving this channel. Required when the channel has more than one active member."
>       }
>     },
>     "additionalProperties": false,
>     "required": ["channel_id"]
>   }
> }
> ```
>
> **Reading B: agent is responsible for the check** — replace the first two rule bullets with:
>
> ```
> - Before calling, check the channel's active member count (via <name the tool>). If it is greater than one, obtain the user's explicit approval for this specific channel and pass `confirmed: true`. Do not call without approval in that case.
> ```
>
> and drop "The server checks the member count" from the description. In this reading the server may not enforce anything, and the agent needs to know that too.
>
> Placeholder in both: `confirmation_required` and the definition of "active member" (e.g. "non-deactivated, non-bot") are the author's to fill in; I have not invented the server's actual behaviour.
>
> ## What I did not do
>
> Per your instructions I read only the document in the prompt: no files, tools, or skills were consulted. This is a static reading of the text, not a behavioural test of how an agent acts on it.
