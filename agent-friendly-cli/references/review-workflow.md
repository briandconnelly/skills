# Review Workflow

Use this workflow when auditing an existing CLI or advising how to make it more agent-friendly.
Every rule a CLI is checked against lives in [contract-checklist.md](contract-checklist.md).
This file orders the review, defines evidence labels, severity, and the report format, and where it names a checklist section it points at that section and does not restate its rules.

## 0. Route Audit vs Diagnosis

If the user reports a concrete failure while using an existing CLI, start in diagnosis mode before broadening to a full audit.

In diagnosis mode:

- identify the most likely failure mechanism from the evidence at hand, with its evidence label from §1
- give the smallest caller-side changes that reduce the failure today
- separate those from tool-side fixes the owner should make
- if one or two safe probes would confirm the hypothesis, offer them under the probe rule in §1, or state why probing is not useful
- stop there; full checklist coverage is not required unless the answer broadens into an audit

If the user is asking for a general audit or redesign, continue with the full workflow below.

## 1. Establish Evidence

Prefer direct evidence over inferred behavior.

Label each finding with one evidence label:

- `observed`: you ran it, or the user supplied a verbatim capture of it; say which.
- `inferred`: deduced from related output, such as a non-TTY hang inferred from documented prompting.
- `absence-of-evidence`: a required contract piece is missing from the `--help`, schema, or session you have.

Absence is itself a finding when a contract piece is required.

Before probing a live CLI, decide whether direct runs would materially reduce uncertainty.

If yes, ask the user for permission before you run commands, even for read paths.
Prefer the cheapest safe probes first: `--help`, `version`, `schema`, one harmless read, and one invalid-input case.
For anything riskier, follow the approval rule below.
If permission is not available, continue with the supplied help text, sessions, schema, or source and label findings accordingly.

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

Capture stdout and stderr separately when you run commands, so stream attribution is observed rather than inferred.

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

Check the answers against [contract-checklist.md](contract-checklist.md) § Command Model, § Machine Schema, and § Prose Surfaces.
Where no `tool schema` exists, look for a stable machine-readable substitute before scoring its absence: `--help --json`, a generated schema file, completion metadata, manpage metadata, or an upstream API contract.

## 3. Review Invocation Safety

Check the CLI against [contract-checklist.md](contract-checklist.md) § Agent-Safe Invocation, § Shell Safety, § Ambient State, § Mutations And Long-Running Work, and § Side Effects And Telemetry.
Severity for blocking behavior and for hidden side effects on read paths is fixed by the Severity section below.

## 4. Review Output And Errors

Check success and failure output against [contract-checklist.md](contract-checklist.md) § Output and § Errors And Exit Codes.
Compare the declared exit-code map with the exits you collected in §1: an observed exit the schema does not declare is a finding, and a declared code your probes did not produce is `not-checked` unless source or tests show it is unreachable or mis-mapped.

## 5. Review Tests And Release Criteria

Look for tests that pin each item in [contract-checklist.md](contract-checklist.md) § Tests.
Rate the gaps on the Severity scale below.

## 6. Report Format

Put findings first.
Audience-sensitive output shape — including any caller-side mitigation preface for non-owner users — is decided by the audience step in [SKILL.md](../SKILL.md) Workflow §1, not here.

Use this structure:

1. Findings ordered by severity.
2. Checklist coverage: for each section in [contract-checklist.md](contract-checklist.md), one of: covered by finding(s) `Fn`, `OK` with brief evidence, or `not-checked` with reason.
3. Open questions or assumptions.
4. Optional high-level summary or suggested remediation plan.

Each finding includes:

- severity: `P0`, `P1`, `P2`, or `P3` (defined below)
- type: `impl-bug`, `schema-gap`, or `design-issue`
- evidence: `observed`, `inferred`, or `absence-of-evidence` (defined in §1)
- location: file/line, command output, or doc section
- impact: how this fails for agents
- fix direction: concrete guidance, not generic preference

## Severity

- `P0`: likely data loss, unsafe mutation, credential leak, or commands that hang in automation.
- `P1`: agents cannot reliably invoke, parse, branch on, or recover from common operations.
- `P2`: important contract gaps, ambiguous command design, missing schema fields, or costly output behavior.
- `P3`: polish, documentation drift, terminology inconsistency, or lower-risk ergonomics.

Fixed placements, because agents cannot recover from them reliably:

- Blocking behavior in machine or non-TTY mode (prompts, pagers, waiting on terminal input) is `P0`.
- A hidden side effect on a read path (implicit write, undeclared network call, update check, telemetry) is `P1`; downgrade to `P2` only with evidence that the effect is confined to the local machine.
- Successful stdout that mixes banners, progress, or summaries with the payload is `P1`.
- Errors that offer no symbolic code to branch on are `P1`.
- A mutation whose outcome after a timeout or interrupt cannot be reconciled is `P1`.

Release gating: a `P0` or `P1` finding blocks a release until fixed; `P2` and `P3` findings do not block on their own and are scheduled.
This is the only place that maps severity to the release decision; the checklist states what a CLI must do, not what blocks shipping.

When no findings are found, state that explicitly and call out residual risks such as untested commands or missing live auth coverage.
