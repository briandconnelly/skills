# MCP Server Contract Checklist

This is the normative standard for the skill, used by both `design-workflow.md` and `review-workflow.md`. The section order serves audit walks: discovery first (what an agent sees first), then the primitives that get invoked, then the cross-cutting concerns that span all primitives, then versioning. Walk it top to bottom when designing or reviewing a server.

---

## 1. Server-Level

- **Name with a service prefix.** Use a descriptive, agent-facing name with no version numbers, not a host-language convention. The name shows up in tool selection across multi-server contexts and is part of the discovery surface.

- **Avoid generic service names.** Names like `api`, `data`, or `tools` collide silently in multiplexed clients. Pick a name a human could disambiguate at a glance.

- **Choose transport explicitly.** Use `stdio` for local single-client; use streamable HTTP for shared or remote. Document the choice in the capability summary.

- **`stdio` servers MUST NOT log to stdout.** Stdout is the JSON-RPC channel; mixing log output corrupts the protocol stream. Send logs to stderr or a file.

- **Declare the auth model when it affects agent behavior.** State required scopes and permission boundaries that change capability availability, result shape, or repair. Keep credential setup mechanics out of the first-read summary unless the agent can act on them.

- **Distinguish credential failure modes.** "Missing credential," "wrong credential," and "insufficient scope" are three different repair paths. Collapsing them forces the agent to guess.

- **Declare agent-actionable implicit state.** List workspace/project context, default resources, caches, session data, or configuration only when it affects tool choice, results, permissions, or repair. Hidden deployment details belong in operator docs, not the first-read surface.

- **Surface observability in responses, not dashboards.** Rate limits, timeouts, retry hints, deprecation notices, and the capability fingerprint belong in the response payload an agent reads. Operator dashboards are out of scope here.

- **Treat server metadata as contract.** Name, version, fingerprint, and summary are part of the discovery surface. Changes to them are discoverable changes (see §8). See `examples.md` §7 for a capability summary that carries server identity, negative scope, and actionable prerequisites.

Audit prompt: Can an agent learn what this server does, what it doesn't, and which prerequisites affect use, in a single read?

---

## 2. Discovery Primitives

*Worked shapes: `examples.md` §7 (server capability summary), §8 (`search_tools` response shape).*

- **Provide a server capability summary.** A concise overview of what the server does, what it does not do, and any prerequisites that affect whether or how an agent should use it. This is the first thing an agent reads.

- **State negative scope explicitly.** What the server does NOT do is as important as what it does. Negative scope prevents wasted exploration and wrong-tool selection.

- **Provide at least one progressive-disclosure mechanism.** `search_tools` / `describe_tool` and resource-catalog endpoints are valid patterns. The requirement is that clients can load definitions on demand rather than receiving everything upfront.

- **Make discovery selective.** Clients can filter by name, namespace, or topic. A server with 80 tools and no filter is functionally undiscoverable.

- **Discovery obeys token-efficiency rules.** Definitions paginate, support filtering, and return concise summaries by default with an opt-in detailed mode (see §7).

- **Index resources; do not inline bodies.** Catalog entries carry metadata sufficient to triage; bodies are fetched on demand (see §4).

- **The discovery surface itself is contract.** Renaming a tool, changing its namespace, or removing it from a catalog is a discoverable change to clients; treat it as a versioned event (see §8).

- **Resource catalogs are part of discovery.** A catalog that omits new resources or returns inconsistent metadata silently breaks agent planning. Treat the catalog as authoritative.

- **Include the capability fingerprint in discovery responses.** Clients can short-circuit a re-walk if nothing has changed (see §8).

Audit prompt: Can an agent find the right tool or resource for a task without loading every definition the server exposes?

---

## 3. Tools

*Worked shapes: `examples.md` §1 (namespaced tool schema), §2 (structured tool response), §10 (worked task: API mirroring vs. task completion).*

- **Name with `snake_case`, prefix, verb, noun.** `slack_send_message`, not `send_message`. Generic verbs collide across servers in multi-server contexts.

- **Reuse verbs consistently.** `list`, `get`, `create`, `update`, `delete`, `send`, `search` should mean the same thing across tools. Inconsistent verbs make the agent second-guess otherwise-obvious calls.

- **Write descriptions that are narrow and unambiguous.** Cover when to use, edge cases, and an example invocation. Descriptions are the primary input to tool selection.

- **Disambiguate parameter names.** Use `user_id`, not `user`; `channel_id`, not `channel`; `started_after`, not `since`. Ambiguous names cause wrong-shape arguments on the first call.

- **Apply required-vs-optional discipline strictly.** Required parameters must be necessary; optional parameters must have meaningful defaults declared in schema.

- **Use strict types.** Enums where the value set is fixed; formats (`date-time`, `uri`, `email`) where the shape is conventional; `integer` vs `number` chosen deliberately.

- **Default to structured output.** Markdown is opt-in via an explicit detail mode, not a parallel contract on every tool. Token-efficiency rules for responses live in §7.

- **Declare side effects, idempotency, and rate limits as first-class contract.** Use tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) and structured response fields.

- **Set annotations honestly.** `readOnlyHint: true` on a tool that mutates is worse than no annotation, because clients will skip safety prompts.

- **Annotations are hints, not security.** Declare them so agents can plan; do not rely on them for access control. Enforcement lives in the implementation.

- **Prefer task-completing tools over endpoint mirrors.** Tool granularity follows user/agent tasks, not the underlying API's resource map.

- **Hide internal step granularity.** When a task requires multiple steps internally, expose the task — not the steps — unless the steps are themselves separately useful tasks.

- **Failure paths are part of the contract.** Repair signals belong in tool result errors (see §6), not in description prose.

- **Declare every parameter the tool reads.** Hidden parameters (env, config, session) belong in the ambient-state declaration (see §1), not implicit in tool behavior.

### Anti-patterns

- **Wrapping every API endpoint as a tool.** More tools dilute discovery, increase token cost on every definition load, and make selection harder. A 60-tool server where every tool maps to a REST endpoint typically expresses 6–10 actual user tasks. Collapse endpoint chains into the task they serve.

- **Burying side effects, idempotency, or rate limits in description prose.** Agents do not reliably read prose for safety-relevant signals. If a tool mutates state, say so via `destructiveHint`; if it can be retried safely, say so via `idempotentHint`; if it has a per-minute call limit, surface that in the response, not the description.

Audit prompt: For each tool, can an agent decide to use it, call it correctly, and recover from a failure — using only the schema and structured response, never the prose?

---

## 4. Resources

*Worked shapes: `examples.md` §3 (resource index entry), §4 (resource body with chunking).*

- **Use stable, hierarchical, predictable URI patterns.** Resource URIs are identifiers agents quote back to the server and may cache; instability breaks repeat calls.

- **URI segments use stable domain nouns.** Not internal identifiers that change between deployments. The URI is part of the contract.

- **Distinguish lightweight indexes from bodies.** Resource lists return summaries with metadata sufficient for the agent to decide whether to fetch the body.

- **Surface a summary before the body for large resources.** Force the agent to opt in to bulk content rather than handing it whole documents by default.

- **Make body content chunkable with stable identifiers.** Agents need to fetch chunk N+1 without re-fetching N, and to cite a chunk back to a tool.

- **Chunk identifiers are stable across reads of the same resource version.** If the resource changes, identifiers may change — but the change is observable via the resource's modification metadata.

- **Include the metadata fields agents use to triage.** `title`, `summary`, `size`, `last_modified`, `content_type`. Missing metadata pushes the agent into fetching bodies blindly.

- **Keep summaries short.** Typically 1–3 sentences, not paragraphs. Resource summaries appear in lists of dozens; long summaries defeat the index.

- **Resources share the failure-recovery contract.** Missing-credential, not-found, gone, and rate-limit signals must be machine-readable (see §6).

- **Pagination, filtering, and truncation rules live in §7.** Reference them; do not duplicate.

- **A write-surface "resource" is a tool.** Resources are read-oriented; if mutation is the point, model it as a tool with the appropriate annotations (see §3).

Audit prompt: Can an agent decide whether to fetch a resource — and which chunk of it — without first reading the full body?

---

## 5. Prompts

- **State when to use the prompt explicitly.** The agent needs to recognize the matching task, not infer it from the title.

- **List prerequisites.** Which tools, which resources, and which permission or context assumptions the prompt relies on. Missing prerequisites surface as confusing failures partway through execution.

- **Reference expected follow-on tools and resources by name.** A prompt that doesn't tell the agent what to invoke next is half a scaffold.

- **Keep prompts as orchestration scaffolding, not contract.** Essential behavior — argument shapes, side effects, error shapes — belongs in tool and resource schemas. See `examples.md` §5 for a prompt scaffold that references tools and resources without redefining them.

- **Prompts may reference; they may not redefine.** A prompt may name a tool by canonical name, but it must not redefine the tool's contract or override its arguments. The schema is authoritative.

- **Prompts are optional.** A server with no prompts is fine; a server whose prompts are load-bearing for correctness is broken.

### Anti-patterns

- **Prompts as contract container.** Encoding required behavior in prompt text rather than schema means the agent must read prose to call correctly, and any client that bypasses prompts (most code-execution clients do) will call incorrectly. Orchestration scaffolding is not a substitute for schema. If behavior is essential, encode it in tool/resource schemas.

Audit prompt: If every prompt on this server were removed, would any tool or resource become incorrect or unsafe to call?

---

## 6. Failure Recovery

*(Cross-cutting; co-equal with first-call success.)*

- **Use stable, machine-readable error codes.** Codes are symbolic strings (e.g., `not_found`, `rate_limited`, `invalid_field`), not numeric exit codes. The symbolic code is the authoritative branch key for agents.

- **Document every error code per tool.** An undocumented code is an undiscoverable code; agents cannot branch on it reliably. List the codes a tool can return in its schema.

- **Code semantic changes are breaking.** Introducing a new additive code is safe; changing or renaming an existing code's meaning is a breaking change. Both are recorded in the fingerprint (see §8).

- **Provide field-level validation feedback.** Which field, why it's invalid, and which values are allowed. "Invalid input" without a field name forces the agent to guess.

- **Include the offending value when safe.** The agent's repair attempt depends on knowing what it sent. Redact when sensitive; never omit silently.

- **Signal retryability and rate limits explicitly.** Use `retry_after_ms`, `temporary: true|false`, and `rate_limit_remaining` where applicable. Agents need to distinguish "wait and retry" from "stop and reconsider."

- **Include "what to do next" repair hints.** The corrective call, parameter, or filter. The first repair attempt is as important as the first call.

- **Repair hints reference real, callable surfaces.** Tool names, parameter names, valid enum values — not free-form prose.

- **Tool semantic errors return as tool result errors.** Set `isError: true` on the tool result. Protocol-level JSON-RPC errors are reserved for transport and protocol failures; conflating them strips the structured-response contract from the failure path. See `examples.md` §6 for an actionable tool-result error payload.

- **Errors include correlation context.** A `request_id`, the offending parameter, and (where applicable) the resource URI. Agents need to correlate failures with the requests that caused them.

Audit prompt: For each failure mode, does the agent receive enough structured signal to either retry, repair, or escalate — without parsing the message field?

---

## 7. Token Efficiency

*(Cross-cutting; rules apply to both tools and resources.)*

- **Default to a concise response.** Offer richer variants via an explicit detail toggle (e.g., `detail: "summary" | "full"`), not a free `response_format` parameter. See `examples.md` §2 for the concise-vs-detailed response pattern.

- **Detail is orthogonal to format.** Changing detail level changes the density of fields included, not the schema's shape. The same parser handles both modes.

- **Use cursor-based pagination by default.** Offset-based pagination is acceptable only when ordering is stable and the result set is small enough that pages don't shift between calls.

- **Pagination responses include `has_more`.** If `has_more` is true, include a navigation token (`next_cursor`) and, where available, `estimated_total`.

- **Provide filters that meaningfully reduce response size.** `since=`, `query=`, `category=`, `field=`. Filters that don't change wire size are noise.

- **Truncate explicitly with a repair hint.** `"truncated": true, "truncation_hint": "hit cap of 200; narrow with since= or query="`. Silent truncation breaks agent planning.

- **Prefer semantic identifiers over opaque UUIDs.** Raw IDs are allowed when needed for follow-up calls; surface a stable, readable label alongside.

- **Support per-capability detail levels.** Progressive disclosure applies to both definitions (in discovery, see §2) and responses. The agent should be able to ask for "summary" before "full" at every level.

- **Strip null and default-valued fields from concise responses.** Where they add no information, they cost tokens and clutter parsing. Detail mode may include them for completeness.

### Anti-patterns

- **Free `response_format` toggles** (markdown vs. json vs. xml as parallel contracts on the same tool). Format proliferation creates ambiguous contracts: which format is authoritative? Which one carries error signals? Which gets versioned when the schema changes? Prefer one structured default with an opt-in detail toggle.

Audit prompt: Could an agent complete a typical task on this server in a single context window, including discovery, calls, and one round of repair?

---

## 8. Versioning and Compatibility

- **Publish a capability fingerprint.** A versioned identity for the server's surface. Clients use it to detect breaking changes cheaply, without re-walking the discovery surface. See `examples.md` §9 for fingerprint evolution across deprecation and removal.

- **The fingerprint covers the full agent-visible surface.** Tool definitions, resource catalogs, prompt scaffolds, error codes, and the server capability summary. Anything an agent can plan against is part of the fingerprint input.

- **Define deprecation semantics.** How a tool, resource, or prompt is marked deprecated, how long it remains available, and what replaces it. Deprecation is a contract, not a sticky note.

- **Deprecated capabilities remain discoverable.** They continue to appear in discovery (see §2) until removal, with a deprecation marker and a pointer to the replacement. Silently dropping them breaks cached clients.

- **Adding optional fields is safe.** Removing or renaming fields, codes, or tools requires a fingerprint bump. Document the migration in the deprecation marker.

- **Treat tool rename as remove-plus-add.** Renaming a tool is a discovery-surface change (see §2) — clients that cached the old surface will break silently otherwise. Keep the old name with a deprecation pointer for the documented window.

- **Declare stability tiers if used.** `stable`, `preview`, `experimental`. Mixing tiers without labels makes every capability look stable, which is worse than labeling some as risky.

- **Stability tier is discovery metadata.** Each capability's tier is part of its discovery record so agents can filter by tier (see §2).

- **Error codes are part of the versioned surface (see §6).** Changing a code's meaning is a breaking change; introducing a new code is additive but still recorded in the fingerprint.

- **The fingerprint format itself is stable.** Changing how the fingerprint is computed (hashing algorithm, included fields) is a breaking change for any client caching by fingerprint.

Audit prompt: If a client cached this server's surface yesterday, can it tell — from the fingerprint alone — whether anything it depends on changed?
