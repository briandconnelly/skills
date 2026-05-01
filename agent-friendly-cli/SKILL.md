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
- Make ambient state, side effects, auth, latency, truncation, and retryability visible.
- Prefer compact, deterministic output shapes over prose explanations.

## When To Use

- Designing a new CLI that agents (Claude Code, Codex, custom agents) will invoke.
- Defining or hardening a machine-readable schema, JSON contract, or exit-code map for an existing CLI.
- Auditing an existing CLI for agent-friendliness.
- Diagnosing concrete agent failures: wrong-command selection, prose parsing, hangs, stdout pollution, hidden state, non-deterministic output, lost errors.

## When Not To Use

- General code review of CLI internals that does not face agents — use the standard code-review skill.
- Library or SDK design that is not exposed as a command — this skill is CLI-specific.
- Trivial flag additions to an already-agent-friendly CLI; just follow the existing schema.

## Vocabulary

- **Machine profile**: the canonical flag bundle that puts the CLI in non-interactive, machine-readable mode (e.g., `--json --machine --no-config --no-progress`). Declared in the schema.
- **Machine mode**: the runtime state the machine profile produces — no prompts, no color, no progress, no pager, no browser, structured output only.
- **Non-TTY mode**: any invocation where stdout or stderr is not a terminal; conservatively suppresses color, spinners, pagers, and prompts even without the explicit machine profile.
- **Output class**: one of `scalar`, `record`, `list`, `stream`, `bulk-result`, `artifact`. Each command declares one.
- **Ambient state**: config files, environment variables, credentials, and caches the CLI reads implicitly.

## Workflow

1. Classify the task: new CLI or redesign vs review of an existing CLI.
2. For new design or redesign, follow [design-workflow.md](references/design-workflow.md).
3. For an audit, follow [review-workflow.md](references/review-workflow.md); severity scale and report format live there.
4. Use [contract-checklist.md](references/contract-checklist.md) as the detailed standard for both workflows.
5. Use [examples.md](references/examples.md) for concrete schema, payload, error, and review-finding shapes.

## Done Criteria

Before declaring done, walk [contract-checklist.md](references/contract-checklist.md) against your output.

- **Design tasks**: every checklist section must have an answer in the schema or be explicitly marked not-applicable with a one-line justification.
- **Review tasks**: every checklist section is either covered by a finding, marked `OK` with brief evidence, or noted `not-checked` with reason. Use the severity scale and report format defined in [review-workflow.md](references/review-workflow.md).
