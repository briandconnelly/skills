---
name: agent-friendly-mcp
description: Use when designing, building, auditing, or reviewing an MCP server that AI agents will invoke directly. Symptoms include agents picking the wrong tool from many candidates, burning tokens loading hundreds of tool definitions upfront, repeated invalid tool calls due to ambiguous schemas, tools that mirror an underlying API endpoint-by-endpoint instead of completing tasks, missing or unclear resource browsing, prompts that duplicate tool contracts, token-heavy responses that should be paginated or filtered, brittle integrations that break across server versions. Also use when defining or hardening tool, resource, or prompt schemas.
---

# Agent-Friendly MCP

Use this skill to make MCP servers easy for agents to discover, invoke correctly, recover from, and use at low token cost without sacrificing correctness.

## Core Standard

- Tool and resource schemas are the operational contract; prompts are advisory scaffolding for orchestration. Do not hide essential behavior in prompts.
- Optimize for the first successful tool call **and** the first successful repair from a cold start.
- Design around user/agent tasks, not the underlying API's endpoint surface.
- Make side effects, idempotency, rate limits, and agent-actionable prerequisites visible.
- Default to compact, deterministic, structured output; structured data is authoritative and text or markdown is supplemental rendering for human-facing clients.
- Provide explicit discovery primitives so agents can load capabilities selectively.
- Design for the least-capable realistic client: some preload tools, paginate discovery, ignore annotations, or expose resources poorly.

## When To Use

- Designing a new MCP server that agents (Claude Code, Codex, custom agents) will invoke.
- Defining or hardening tool, resource, or prompt schemas for an existing server.
- Auditing an existing MCP server for agent-friendliness.
- Diagnosing concrete agent failures: wrong-tool selection from many candidates, repeated invalid tool calls, token waste from upfront definition loading, endpoint-mirroring tools that force long chains, broken cross-server upgrades.
- Designing long-running work: progress notifications, cancellation, task-augmented requests, and long-running operation patterns (see [contract-checklist.md](references/contract-checklist.md) §7 and [examples.md](references/examples.md) §11).

## When Not To Use

- General code review of MCP server internals that does not face agents — use your normal code-review workflow.
- Library or SDK design that is not exposed via MCP — this skill is MCP-specific.
- Trivial schema additions to an already agent-friendly server; just follow the existing contract.
- Out of scope: elicitation, sampling, server logging streams, server-operator dashboards, packaging/deployment, and skills-over-MCP (experimental at https://github.com/modelcontextprotocol/experimental-ext-skills — revisit when stable).

## Vocabulary

- **Discovery surface**: the union of definitions, summaries, and discovery primitives an agent can see before deciding which capability to invoke.
- **Concise vs detailed result**: a single structured default response, with an opt-in detail mode for richer content. Not a free `response_format` toggle.
- **Resource index**: a lightweight catalog of available resources with metadata sufficient to decide whether to read the body, distinct from the bodies themselves.
- **Prompt scaffold**: a reusable task starter that points at tools and resources, with explicit prerequisites and expected follow-on actions.
- **Composable primitive vs workflow tool**: granularity decision: one tool that completes a user task vs. several tools the agent must chain.
- **Operational prerequisites**: auth scopes, workspace/project context, prior setup, or implicit state that affects capability availability, result shape, permissions, or repair.
- **Capability fingerprint**: a versioned identity for the server's surface, so clients can detect breaking changes.
- **Code-execution client**: an agent that writes code against the MCP server's surface (per "Code Execution with MCP") rather than calling tools directly.
- **Repair signal**: error fields that tell the agent specifically how to retry: stable code, offending field, allowed values, retryability, suggested next call.
- **State handle**: an opaque reference to server-side state, such as a job, cursor, or session, with declared lifetime and expiry behavior.
- **Long-running operation**: work that may need progress, cancellation, status polling, or result retrieval after the original request.
- **Task-capable tool**: a tool that supports the task-augmented request pattern, declared via `execution.taskSupport: "optional" | "required" | "forbidden"`, so clients can recover status and results after the original call returns.

## State Handles

- Domain IDs with natural meaning, such as message timestamps, channel names, or usernames, may stay readable.
- State handles, such as job IDs, cursor tokens, and session refs, are opaque IDs with readable labels or summaries where useful.
- Security-sensitive references, such as auth tokens or internal record IDs, are opaque and never leak structure.
- Declare handle lifetime, expiry behavior, and bounded retention policy in the tool or resource contract.
- Check authorization on every handle use, not only when the handle is created.
- Return structured expiry errors with a repair path when a handle can no longer be used.

## Long-Running Operations

- Use blocking `tools/call` for short operations, progress notifications for bounded multi-step work, and task-augmented requests when clients need later recovery.
- Declare expected duration, timeout behavior, and whether partial progress is observable.
- Support `progressToken` and rate-limited `notifications/progress` when progress exists.
- Use `notifications/cancelled` to cancel request-bound non-task work, and `tasks/cancel` to cancel task-augmented work.
- Enable native tasks at both levels: the server declares `capabilities.tasks.requests.tools.call` and the tool declares `execution.taskSupport` as `optional`, `required`, or `forbidden`.
- Recover via native operations — poll `tasks/get` (respecting `pollInterval`), fetch with `tasks/result`, using the spec's task fields (`taskId`, `status`, `ttl`, `createdAt`, `lastUpdatedAt`) and statuses (`working`, `input_required`, `completed`, `failed`, `cancelled`).
- Tasks are experimental in MCP 2025-11-25, so a domain-specific status/cancel tool is an acceptable labeled fallback for clients without task support, mirroring the native signals rather than replacing `tasks/*`.

## Workflow

1. Classify the task: new MCP server or redesign vs review of an existing one.
2. For new design or redesign, follow [design-workflow.md](references/design-workflow.md).
3. For an audit, follow [review-workflow.md](references/review-workflow.md); severity scale and report format live there.
4. Use [contract-checklist.md](references/contract-checklist.md) as the detailed standard for both workflows.
5. Use [mcp-vs-cli.md](references/mcp-vs-cli.md) if deciding which surface to expose; use [examples.md](references/examples.md) for concrete schema, response, error, and discovery shapes.

## Done Criteria

Before declaring done, walk [contract-checklist.md](references/contract-checklist.md) against your output.

- **Design tasks**: every checklist section must have an answer in the schema set or be explicitly marked not-applicable with a one-line justification.
- **Review tasks**: every checklist section is either covered by a finding, marked `OK` with brief evidence, or noted `not-checked` with reason. Use the severity scale and report format defined in [review-workflow.md](references/review-workflow.md).
