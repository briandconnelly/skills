---
name: agent-friendly-cli
description: Use when designing, building, auditing, or reviewing a command-line interface that AI agents will invoke directly. Symptoms include agents picking the wrong subcommand from prose help, parsing English to branch on errors, hanging on prompts in CI, mixing banners with JSON on stdout, getting burned by hidden state or surprise side effects, or wasting tokens on unstable output. Also use when defining a machine-readable contract or schema for a CLI.
---

# Agent-Friendly CLI

Use this skill to make CLIs easy for agents to discover, invoke correctly, and use at low token cost without sacrificing correctness.

## Standard

[contract-checklist.md](references/contract-checklist.md) is the single home for every rule in this skill.
The workflows order the work and point at its sections; [examples.md](references/examples.md) instantiates it; this file routes.
Where another file in this skill appears to disagree with the checklist, the checklist governs.

## When To Use

- Designing a new CLI that agents (Claude Code, Codex, custom agents) will invoke.
- Defining or hardening a machine-readable schema, JSON contract, or exit-code map for an existing CLI.
- Auditing an existing CLI for agent-friendliness.
- Diagnosing concrete agent failures: wrong-command selection, prose parsing, hangs, stdout pollution, hidden state, non-deterministic output, lost errors.

## When Not To Use

- General code review of CLI internals that does not face agents — use your normal code-review workflow.
- Library or SDK design that is not exposed as a command — this skill is CLI-specific.
- Deciding whether a capability should be a CLI or an MCP server at all — use the agent-friendly-mcp skill's `references/mcp-vs-cli.md` decision aid first, then return here if a CLI is the right surface.
- Trivial flag additions to an already-agent-friendly CLI; just follow the existing schema.

## Vocabulary

Definitions only; the rules that govern each term live in [contract-checklist.md](references/contract-checklist.md).

- **Machine profile**: the canonical flag bundle, declared in the schema, that puts the CLI in machine mode (e.g., a single `--machine` flag that implies the rest).
- **Machine mode**: the runtime state the machine profile produces — no prompts, no color, no progress, no pager, no browser, structured output only.
- **Isolation profile**: an optional flag bundle that disables ambient config, credentials, caches, and other implicit state (e.g., `--isolated` or `--no-config`).
  Distinct from the machine profile.
- **Non-TTY mode**: runtime behavior derived from each stream's terminal status rather than from an explicit flag.
- **Output class**: the declared shape family of a command's success output.
  The built-in set:
  - `scalar`: one value or status
  - `record`: one resource
  - `list`: finite collection
  - `stream`: NDJSON records
  - `bulk-result`: per-item results plus aggregate exit-code semantics
  - `artifact`: large result written to disk with a structured pointer
- **Ambient state**: config files, environment variables, credentials, and caches the CLI reads implicitly.

## Workflow

1. Identify the audience before choosing the output shape: tool author, internal operator, or third-party consumer.
   - Tool author: optimize for contract gaps, release-blocking findings, and concrete redesign guidance.
   - Internal operator: lead with the smallest safe caller-side mitigation, then separate owner-side fixes from operator-side workarounds.
   - Third-party consumer: do not assume they can change the tool; prioritize containment, explicit assumptions, and what to escalate to the owner.
   - If the audience is unclear, say so and default to the most actionable split: caller-side mitigation first, tool-side fixes second.
2. Classify the task: new CLI or redesign vs contract hardening vs review of an existing CLI vs diagnosis of a concrete failure.
   Audience and task are orthogonal: audience decides output shape (what to lead with); task decides workflow path (which file to follow).
3. For new design or redesign, follow [design-workflow.md](references/design-workflow.md).
4. For contract hardening when the user owns the CLI, follow [design-workflow.md](references/design-workflow.md); if a contract already exists, first walk [review-workflow.md](references/review-workflow.md) to find the gaps, then design the fixes.
   For a contract the user does not own, follow [review-workflow.md](references/review-workflow.md) only.
5. For an audit or diagnosis, follow [review-workflow.md](references/review-workflow.md); audit-vs-diagnosis routing, evidence labels, severity scale, and report format live there.
6. Use [contract-checklist.md](references/contract-checklist.md) as the detailed standard for both workflows.
7. When writing or auditing prose surfaces — `--help` text, command summaries, schema `description` fields — apply [contract-checklist.md](references/contract-checklist.md) § Prose Surfaces.
8. Use [examples.md](references/examples.md) for concrete schema, payload, error, and review-finding shapes.

## Done Criteria

Before declaring done, read the relevant workflow and walk [contract-checklist.md](references/contract-checklist.md) against your output.

- **Design tasks**: every checklist section must have an answer in the schema or be explicitly marked not-applicable with a one-line justification.
- **Review tasks**: the report follows [review-workflow.md](references/review-workflow.md) § Report Format, including its checklist-coverage table and the evidence label on every finding.
- **Diagnosis tasks**: the response satisfies the diagnosis-mode items in [review-workflow.md](references/review-workflow.md) §0 and stops there.
