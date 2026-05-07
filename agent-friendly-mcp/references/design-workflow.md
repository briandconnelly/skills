# MCP Server Design Workflow

Use this workflow when designing a new MCP server or redesigning an existing one. The output is a server whose tools, resources, and prompts pass `contract-checklist.md` end to end — that is, a contract an agent can plan against from the schema and structured responses alone, never undocumented prose outside the schema.

The steps are deliberately re-entrant: a later step often surfaces a flaw in an earlier decision (a granularity choice that breaks the schema, a discovery design that breaks under eval, an error taxonomy that exposes a missing primitive). Re-entering Step N from Step N+3 is normal — treat earlier outputs as drafts until the eval at Step 7 holds. The checkpoint links at each step point at the relevant `contract-checklist.md` sections; consult them as you work, not only at the end.

## Step 1: Enumerate user/agent tasks

List the real tasks an agent should be able to complete with this server.

- Write tasks, not endpoints. "Send a message to a Slack channel" is a task; `POST /chat.postMessage` is not.
- Pull tasks from real workflows — what a user or agent already does end-to-end without this server.
- Group near-duplicates; collapse 60 endpoint variations into the 6–10 tasks they actually serve.
- Note prerequisites per task (auth scope, workspace/project context, prior calls, implicit state that affects behavior) — these surface again in Step 5.

Output: a written task list, each task expressed as a verb phrase with the user/agent goal.
Checkpoint: §1, §3 granularity rule.

## Step 2: Choose the right primitive per task

For each task, pick tool, resource, or prompt scaffold.

- State-changing or operational? Tool. Annotate with `destructiveHint` / `idempotentHint` honestly.
- Read-only and browseable, with stable URIs the agent will quote back? Resource.
- Multi-step orchestration scaffolding the agent invokes by name? Prompt — but never load-bearing for correctness.
- A "write resource" is a tool. A "prompt that defines argument shapes" is a tool schema in disguise; reclassify it.

Output: per-task primitive assignment (tool / resource / prompt) with one-line justification each.
Checkpoint: §3, §4, §5.

## Step 3: Decide tool granularity

For each tool, choose task-completing vs composable primitive, and record the reason.

- Default to task-completing. Hide internal step granularity unless the steps are themselves separately useful tasks.
- Only split into composable primitives when an eval (Step 7) shows the split helps a code-execution client — not on speculation.
- Endpoint-shaped tools are an anti-pattern: collapse endpoint chains into the task they serve.
- If two tools' descriptions need long prose to disambiguate, the granularity is wrong.

Output: per-tool granularity decision with explicit reasoning (task-completing or composable, and why).
Checkpoint: §3 granularity rule.

## Step 4: Write input schemas

Treat the schema as the authoritative contract. Write it before behavior.

- Required vs optional discipline: required parameters are necessary; optional ones have meaningful defaults declared in schema.
- Strict types: enums for fixed value sets; formats (`date-time`, `uri`, `email`); `integer` vs `number` chosen deliberately.
- Disambiguating names: `user_id` not `user`, `started_after` not `since`, `channel_id` not `channel`.
- Descriptions cover when to use, edge cases, and an example invocation.

Output: complete tool input schemas, resource URI patterns, and prompt argument schemas — including descriptions and examples.
Checkpoint: §3, §4. See `examples.md` §1 for a worked tool schema and §5 for a prompt scaffold.

## Step 5: Design the discovery surface

Decide how an agent finds the right primitive without loading every definition.

- Write the server capability summary: what it does, what it does NOT do, and any prerequisites that affect whether or how an agent should use it.
- Pick a progressive-disclosure mechanism: `search_tools` / `describe_tool`, resource catalog, namespaced filters — at least one.
- Make discovery selective: filter by name, namespace, or topic. A flat list of 80 tools is undiscoverable.
- Index resources; do not inline bodies. Catalog entries carry triage metadata only.

Output: server capability summary, discovery primitives implemented, resource catalog shape.
Checkpoint: §1, §2, §4. See `examples.md` §7 for a server capability summary and §8 for a `search_tools` response.

## Step 6: Design failure recovery

Design the error surface as deliberately as the success surface.

- Define stable, symbolic error codes (`not_found`, `rate_limited`, `invalid_field`) and document per-tool which codes can occur.
- Field-level validation feedback: which field, why invalid, allowed values; include the offending value when safe.
- Retryability and rate-limit signals: `retry_after_ms`, `temporary`, `rate_limit_remaining` where applicable.
- Repair hints reference real callable surfaces — tool names, parameter names, valid enum values — not free-form prose.
- Draft a worked JSON payload for each top failure mode — not just a field inventory. Concrete payloads expose contradictions a field list hides.

Output: error taxonomy with example payloads for the top failure modes per tool, including correlation context (`request_id`, offending parameter).
Checkpoint: §6. See `examples.md` §6 for an actionable error payload.

## Step 7: Build evaluations grounded in real tasks

Build an eval suite from the Step 1 task list before iterating further.

- Use real workflows from Step 1 as the eval tasks; synthetic prompts hide discovery and selection failures.
- Measure first-call correctness: did the agent pick and call the right primitive on the first attempt?
- Measure first-repair correctness: given a structured error, did the agent's next call succeed?
- Measure token consumption and tool-call count per completed task — both are first-class quality signals.

Output: at least one eval task suite covering the high-value tasks from Step 1, with metrics for first-call correctness, first-repair correctness, token consumption, and tool-call count.
Checkpoint: §2, §3, §6, §7 — the eval should exercise discovery, tool selection, error repair, and token consumption.

## Step 8: Iterate against the eval, including transcript review

Run the eval with an agent and read the transcripts; do not trust aggregate scores alone.

- Look for contradictions between description prose and schema; the schema wins, so fix the prose or the schema.
- Look for ambiguity in tool selection — two tools the agent confuses, or descriptions that overlap.
- Look for ineffective discovery: agents loading every definition, agents missing a tool that exists, agents picking the wrong namespace.
- Each iteration should produce a measurable improvement in first-call correctness, first-repair correctness, or token consumption — if it doesn't, the change wasn't grounded.

Output: revised schemas, descriptions, and discovery surface, with eval-measured improvement against the prior baseline.
Checkpoint: §1–§8 — walk the full checklist; iteration is the moment to catch contradictions any earlier checkpoint missed.
