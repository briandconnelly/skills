# Review Workflow

Use this workflow when auditing an existing CLI or advising how to make it more agent-friendly.

## 0. Route Audit vs Diagnosis

If the user reports a concrete failure while using an existing CLI, start in diagnosis mode before broadening to a full audit.

In diagnosis mode:
- identify the most likely failure mechanism from the evidence at hand
- give the smallest caller-side changes that reduce the failure today
- separate those from tool-side fixes the owner should make
- if one or two safe probes would confirm the hypothesis, ask for permission before running them

If the user is asking for a general audit or redesign, continue with the full workflow below.

## 1. Establish Evidence

Prefer direct evidence over inferred behavior.

When recording findings, label each as `observed` (you ran it), `inferred` (deduced from related output), or `absence-of-evidence` (a contract piece is missing from `--help`/schema/session).
Absence is itself a finding when a contract piece is required.

Before probing a live CLI, decide whether direct runs would materially reduce uncertainty.

If yes, ask the user for permission before you run commands, even for read paths.
Prefer the cheapest safe probes first: `--help`, `version`, `schema`, one harmless read, and one invalid-input case.
For anything riskier, follow the approval rule below.
If permission is not available, continue with the supplied help text, sessions, schema, or source and label findings as `observed`, `inferred`, or `absence-of-evidence`.

If the CLI is runnable, collect:

- `tool --help`
- `tool schema` or equivalent
- `tool schema --fingerprint` or equivalent
- `tool version`
- a successful read command
- a command with empty results
- invalid input
- not-found input
- auth failure when safe to simulate
- a mutating command in `--dry-run` mode if available
- a large-output command if available

For auth failure simulation, prefer isolated modes or obviously invalid placeholder credentials over real-looking incorrect credentials.

If source is available, inspect:

- command definitions and parser setup
- schema or contract generation
- renderers for human, JSON, CSV, NDJSON, and artifacts
- error handling and exit-code mapping
- config/env/auth resolution
- tests for CLI behavior

Do not run unsafe mutations, credential-changing commands, destructive cleanup, or commands that may phone home unless the user explicitly approves.

## 2. Review The Discovery Path

Ask whether an agent can answer these quickly:

- What commands exist?
- Which command should I call?
- What exact arguments and flags are required?
- What does the command read from stdin?
- What does it write to stdout, stderr, files, network, cache, or external resources?
- What output shape, error shape, and exit codes should I expect?

Findings are likely when:

- help is long prose and no machine schema exists
- existing tools expose no stable machine-readable substitute for `tool schema`, such as `--help --json`, a generated schema file, completion metadata, manpage metadata, or an upstream API contract
- aliases or synonyms obscure the canonical command
- examples are required to learn flags
- help text buries constraints and defaults under marketing or background prose (rules-then-context violations)
- default output changes by TTY without a declared contract
- schema is generated after implementation and drifts from reality

## 3. Review Invocation Safety

Check for automation hazards:

- prompts in machine mode or non-TTY contexts
- pagers, browser launch, spinners, ANSI color, or progress on machine paths
- reads with hidden side effects
- machine mode conflated with isolated mode, causing credentials, endpoints, or workspace defaults to disappear from the first non-interactive call
- mutations without `--dry-run`, confirmation bypass, or idempotency
- dry-run output indistinguishable from real mutation output (no `dry_run: true` marker)
- mutations with no reconciliation path after a timeout or interrupt (no idempotency key and no lookup/status command)
- undeclared signal semantics, or local state writes that are unsafe under concurrent invocations
- secrets accepted as flag or argument values, leaking into process listings, shell history, and transcripts
- missing `--` end-of-options support, so option-like operands are misparsed
- long-running operations without async polling, timeout controls, or a cancel operation
- networked commands without explicit `--timeout` and retry behavior
- commands that depend on ambient config, credentials, or caches without inspection or isolation flags

Treat hidden state and blocking behavior as high severity because agents cannot recover reliably.

## 4. Review Output And Errors

Success output should be compact, structured, and deterministic.

Check:

- stdout success payload only
- diagnostics and structured failures on stderr
- machine-mode stderr framing is declared as a closed enum value and parseable: the failure payload is either the only stderr content or arrives as typed NDJSON records, never interleaved with free-form diagnostics
- shallow stable JSON in machine mode
- explicit pagination, truncation, omitted fields, partial failure, and artifact pointers
- cursor contracts declare lifetime, expiry error, restart action, and page-walk consistency
- no banners, summaries, warnings, debug logs, progress, or prose mixed into stdout
- NDJSON for streaming or large per-record output
- deterministic sort order and stable JSON fields
- locale-independent numbers, stable path style, UTF-8, and UTC or explicitly declared timestamp timezones

Failure output should support branching without parsing English.

Check:

- reserved numeric exit codes are not overloaded
- symbolic error code exists in JSON mode
- required fields include `code` and `message`
- `field` names a published flag or argument, never an internal identifier
- `hint` is the smallest concrete correction, with machine-usable repair data in structured fields such as `details`
- retryability is explicit
- rate limits include `retry_after_ms`
- stack traces and raw dumps are opt-in and redact secrets
- secrets are redacted from stdout, stderr, debug output, schema examples, dumps, and artifact metadata unless the command intentionally returns a secret
- partial failure has deterministic aggregate semantics
- declared exit codes match observed runtime behavior

## 5. Review Tests And Release Criteria

Look for tests that pin the contract:

- schema snapshot
- canonical success payload snapshots
- representative failure payloads and exit codes
- TTY vs non-TTY behavior
- machine mode suppression of prompts, color, progress, and prose
- pagination, truncation, streaming, and artifact behavior
- config/env precedence and isolation flags
- deprecation warnings and replacement metadata
- interrupt behavior for mutations, concurrent local-state writes, and long-running cancellation

Release should block when:

- the correct flag combination is discoverable only from examples
- successful stdout contains banners, summaries, or status chatter
- the tool prompts unless the caller remembers a special flag
- output shape changes significantly due to result size or TTY alone
- errors are mostly unstable English paragraphs
- a mutation's outcome after a timeout or interrupt cannot be reconciled
- important config, auth, or cache behavior is not inspectable
- schema regularly drifts from runtime behavior

## 6. Report Format

Put findings first.
Audience-sensitive output shape — including any caller-side mitigation preface for non-owner users — is decided by the audience step in [SKILL.md](../SKILL.md) Workflow §1, not here.

Use this structure:

1. Findings ordered by severity.
2. Checklist coverage: for each section in [contract-checklist.md](contract-checklist.md), one of: covered by finding(s) `Fn`, `OK` with brief evidence, or `not-checked` with reason.
3. Open questions or assumptions.
4. Optional high-level summary or suggested remediation plan.

Each finding should include:

- severity: `P0`, `P1`, `P2`, or `P3` (defined below)
- type: `impl-bug`, `schema-gap`, or `design-issue`
- location: file/line, command output, or doc section
- impact: how this fails for agents
- fix direction: concrete guidance, not generic preference

## Severity

- `P0`: likely data loss, unsafe mutation, credential leak, or commands that hang in automation.
- `P1`: agents cannot reliably invoke, parse, branch on, or recover from common operations.
- `P2`: important contract gaps, ambiguous command design, missing schema fields, or costly output behavior.
- `P3`: polish, documentation drift, terminology inconsistency, or lower-risk ergonomics.

When no findings are found, state that explicitly and call out residual risks such as untested commands or missing live auth coverage.
