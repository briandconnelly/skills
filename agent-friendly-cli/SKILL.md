---
name: agent-friendly-cli
description: Use when designing, building, auditing, or reviewing a command-line interface that AI agents will invoke directly. Symptoms include agents picking the wrong subcommand from prose help, parsing English to branch on errors, hanging on prompts in CI, mixing banners with JSON on stdout, getting burned by hidden state or surprise side effects, or wasting tokens on unstable output. Also use when defining a machine-readable contract or schema for a CLI.
---

# Agent-Friendly CLI

Use this skill to make CLIs easy for agents to discover, invoke correctly, and use at low token cost without sacrificing correctness.

## Core Standard

- Treat the machine-readable schema as the primary contract.
- Optimize for the first successful non-interactive invocation.
- Keep stdout as success payload only; put diagnostics and structured failures on stderr.
- Make ambient state, side effects, auth, latency, truncation, retryability, and secret-handling visible.
- Prefer compact, deterministic output shapes over prose explanations.

## When To Use

- Designing a new CLI that agents (Claude Code, Codex, custom agents) will invoke.
- Defining or hardening a machine-readable schema, JSON contract, or exit-code map for an existing CLI.
- Auditing an existing CLI for agent-friendliness.
- Diagnosing concrete agent failures: wrong-command selection, prose parsing, hangs, stdout pollution, hidden state, non-deterministic output, lost errors.

## When Not To Use

- General code review of CLI internals that does not face agents — use your normal code-review workflow.
- Library or SDK design that is not exposed as a command — this skill is CLI-specific.
- Trivial flag additions to an already-agent-friendly CLI; just follow the existing schema.

## Vocabulary

- **Machine profile**: the canonical flag bundle that puts the CLI in non-interactive, machine-readable mode (e.g., `--json --machine --no-progress`). Declared in the schema.
- **Machine mode**: the runtime state the machine profile produces — no prompts, no color, no progress, no pager, no browser, structured output only.
- **Isolation profile**: an optional flag bundle that disables ambient config, credentials, caches, and other implicit state when the CLI can support that safely (e.g., `--isolated` or `--no-config`).
  Distinct from the machine profile.
- **Non-TTY mode**: runtime behavior based on each stream's terminal status: stdout controls human rendering and pagers, stderr controls diagnostic color and progress, and stdin controls prompts.
  Conservatively suppress terminal-only behavior even without the explicit machine profile.
- **Output class**: one of `scalar`, `record`, `list`, `stream`, `bulk-result`, `artifact`, or another explicitly declared class with a stable contract. Each command declares one.
- **Ambient state**: config files, environment variables, credentials, and caches the CLI reads implicitly.

## Workflow

1. Identify the audience before choosing the output shape: tool author, internal operator, or third-party consumer.
   - Tool author: optimize for contract gaps, release-blocking findings, and concrete redesign guidance.
   - Internal operator: lead with the smallest safe caller-side mitigation, then separate owner-side fixes from operator-side workarounds.
   - Third-party consumer: do not assume they can change the tool; prioritize containment, explicit assumptions, and what to escalate to the owner.
   - If the audience is unclear, say so and default to the most actionable split: caller-side mitigation first, tool-side fixes second.
2. Classify the task: new CLI or redesign vs contract hardening vs review of an existing CLI vs diagnosis of a concrete failure. Audience and task are orthogonal: audience decides output shape (what to lead with); task decides workflow path (which file to follow).
3. For new design or redesign, follow [design-workflow.md](references/design-workflow.md).
4. For contract hardening, follow [design-workflow.md](references/design-workflow.md) when the user owns the CLI and wants a contract designed; follow [review-workflow.md](references/review-workflow.md) when evaluating an existing third-party contract.
5. For an audit or diagnosis, follow [review-workflow.md](references/review-workflow.md); audit-vs-diagnosis routing, severity scale, and report format live there.
6. Use [contract-checklist.md](references/contract-checklist.md) as the detailed standard for both workflows.
7. Use [examples.md](references/examples.md) for concrete schema, payload, error, and review-finding shapes.

## Done Criteria

Before declaring done, read the relevant workflow and walk [contract-checklist.md](references/contract-checklist.md) against your output.

- **Design tasks**: every checklist section must have an answer in the schema or be explicitly marked not-applicable with a one-line justification.
- **Review tasks**: every checklist section is either covered by a finding, marked `OK` with brief evidence, or noted `not-checked` with reason. Use the severity scale and report format defined in [review-workflow.md](references/review-workflow.md).
- **Diagnosis tasks**: response names the most likely failure path with an evidence label, separates caller-side mitigations the user can take today from owner-side fixes, and either offers safe confirmation probes or states why probing isn't useful. Full checklist coverage isn't required unless the answer broadens into an audit.
