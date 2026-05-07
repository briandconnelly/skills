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
- Default to compact, deterministic, structured output; markdown is opt-in, not a parallel contract on every tool.
- Provide explicit discovery primitives so agents can load capabilities selectively.

## When To Use

- Designing a new MCP server that agents (Claude Code, Codex, custom agents) will invoke.
- Defining or hardening tool, resource, or prompt schemas for an existing server.
- Auditing an existing MCP server for agent-friendliness.
- Diagnosing concrete agent failures: wrong-tool selection from many candidates, repeated invalid tool calls, token waste from upfront definition loading, endpoint-mirroring tools that force long chains, broken cross-server upgrades.

## When Not To Use

- General code review of MCP server internals that does not face agents — use the standard code-review skill.
- Library or SDK design that is not exposed via MCP — this skill is MCP-specific.
- Trivial schema additions to an already agent-friendly server; just follow the existing contract.
- Out of scope: elicitation, sampling, notifications/logging streams, server-operator dashboards, packaging/deployment, and skills-over-MCP (experimental at https://github.com/modelcontextprotocol/experimental-ext-skills — revisit when stable).

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
