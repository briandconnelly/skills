# Scenario 2 (audit) — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 4/4 conformance
- **Tokens:** 64,459 (final-turn context plus output, read from the transcript)
- **Output words:** 1,558
- **Transcript sha256:** `4934b2a1c2cab33d1b14cfc9a65f8cb5a519244000c748e0e3d252adf1cab811` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Audit this CLI for agent-friendliness and report your findings.
> You cannot run the tool; you have only this captured material.
> Each capture discards stderr (`2>/dev/null`), so every line shown is stdout.
> The audience is the tool's author, who can change anything.
>
> ```text
> $ depman --help 2>/dev/null
> DepMan 3.2 — the friendly dependency manager!
> Usage: depman [command] [options]
> Commands:
>   install     Install dependencies (aliases: i, add)
>   ls          Show stuff
>   clean       Remove unused packages from the global cache
>   sync        Sync the lockfile (asks for confirmation first)
> Options:
>   --quiet     Less output
>   --yes       Assume yes
>
> $ depman ls --json 2>/dev/null
> ✨ DepMan 3.2
> Checking for updates...
> [{"name":"left-pad","version":"1.3.0"},{"name":"is-odd","version":"3.0.1"}]
> Done in 0.42s ✓
>
> $ depman install nonexistent-pkg 2>/dev/null
> Error: something went wrong (see log)
> $ echo $?
> 1
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S2-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | evidence: inferred ...; non-TTY behavior not captured Parts: sync prompt flagged as blocking risk = pass; states what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | inferred (from `--help`: ...); non-TTY behavior not captured Parts: shows documented prompt = pass; distinguishes deduced non-TTY hang = pass |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: observed (user capture, stdout only) Parts: pollution flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Errors with no symbolic code to branch on are a fixed P1 |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | F3 — Update check on a read path |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` mutates the global cache with no declared dry run |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | `ls Show stuff` ... Two aliases for `install` Parts: alias duplication flagged = pass; vague ls description flagged = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | \| Tests \| not-checked — no source or tests supplied |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | severity: P0 / type / evidence / location / impact / fix direction Parts: P0-P3 words = pass; template fields severity/type/evidence/location/impact/fix = pass |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | evidence: observed / inferred / absence-of-evidence |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 severity: P0; F2 severity: P1 |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **PASS** | \| Stdin Contract \| not-checked — no stdin-reading commands shown |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author (can change anything), so this report leads with contract gaps and release-blocking findings.
Task type: audit of an existing CLI from captured material only; no probes were run.
All captures discard stderr, so every line shown is stdout; "observed" below means observed in the user-supplied verbatim capture.

## Findings (ordered by severity)

### F1 — `sync` prompts for confirmation; no declared non-interactive behavior
- severity: P0
- type: design-issue
- evidence: inferred (from `--help`: "Sync the lockfile (asks for confirmation first)"); non-TTY behavior not captured
- location: `depman --help`, `sync` entry
- impact: an agent or CI job calling `depman sync` without `--yes` can block waiting on terminal input. Blocking behavior in non-TTY mode is a fixed P0.
- fix direction: never prompt when stdin is not a TTY or in machine mode; instead fail fast with a structured error (e.g. `code: "CONFIRMATION_REQUIRED"`, exit `2`, `hint` naming `--yes`). Add `--dry-run` to `sync` showing the planned lockfile diff with `dry_run: true`. Declare `--yes` in the schema as the explicit mutation trigger.

### F2 — `ls --json` stdout mixes banner, progress, and summary with the payload
- severity: P1
- type: impl-bug
- evidence: observed (user capture, stdout only)
- location: `depman ls --json` output lines 1, 2, 4 (`✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`)
- impact: `depman ls --json | jq` fails; agents must strip lines heuristically, which breaks on any wording change. Successful stdout mixing banners/progress/summaries with the payload is a fixed P1.
- fix direction: in `--json` (and any non-TTY stdout), stdout contains only the JSON document. Move banner/timing to stderr, and suppress them entirely in machine mode. Add a snapshot test asserting `depman ls --json` stdout parses as JSON exactly.

### F3 — Update check on a read path
- severity: P1
- type: design-issue
- evidence: observed ("Checking for updates..." emitted by `ls`); the network call itself is inferred
- location: `depman ls --json` output line 2
- impact: a read command performs an undeclared network call: adds latency, can fail or hang offline/in sandboxes, and leaks usage. A hidden side effect on a read path is a fixed P1; nothing shows it is confined to the local machine.
- fix direction: make update checks opt-in (or at minimum suppressed in machine mode and non-TTY), never write about them to stdout, and declare the behavior and its disable switch (flag/env var) in the schema.

### F4 — Install failure has no symbolic code, goes to stdout, and defers to an unnamed log
- severity: P1
- type: impl-bug
- evidence: observed (user capture: `Error: something went wrong (see log)` on stdout with stderr discarded; exit `1`)
- location: `depman install nonexistent-pkg`
- impact: agents cannot distinguish not-found from network, auth, or usage errors; exit `1` is generic; the message is on stdout (contaminating the success channel) and gives no path for the log. Errors with no symbolic code to branch on are a fixed P1.
- fix direction: write a structured error to stderr with `code` (e.g. `PACKAGE_NOT_FOUND`), `message`, `temporary: false`, plus `resource_id: "nonexistent-pkg"` and `path` to the log if one exists. Leave stdout empty on failure. Map not-found to exit `3` (and declare the full exit-code map in the schema, per contract-checklist § Errors And Exit Codes).

### F5 — No machine schema or machine profile
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (only prose `--help` supplied; no `schema`, `--help --json`, or fingerprint)
- location: `depman --help`
- impact: agents cannot learn arguments, flag types, output class, error codes, exit codes, read-only vs mutating classification, or side effects without trial and error. `--json` appears only in the `ls` capture and is not listed in `--help`, so agents cannot know which commands support it.
- fix direction: add `depman schema` (and `schema --fingerprint` with `fingerprint_scope`) covering every item in contract-checklist § Machine Schema. Define one machine profile (e.g. `--machine`, implying JSON output, no prompts, no color/banner, no update check) and declare it as a global flag. Declare output class per command (`ls` → `list`; `install`/`clean` → `bulk-result`).

### F6 — `clean` mutates the global cache with no declared dry run or confirmation contract
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`, `clean` entry
- impact: an agent cannot preview what will be removed, and cannot tell from help whether `clean` prompts (if it does, this escalates to P0 like F1). Global-cache writes from concurrent agent runs may race.
- fix direction: add `--dry-run` listing packages to remove with `dry_run: true`; declare mutating classification, concurrency safety (locking), and interrupt semantics.

### F7 — Vague prose surfaces and undeclared aliases
- severity: P2
- type: design-issue
- evidence: observed (user capture of `--help`)
- location: `depman --help`: `ls  Show stuff`, `--quiet  Less output`, `install (aliases: i, add)`
- impact: "Show stuff" does not tell an agent what `ls` lists (project deps? installed? global cache?) so it cannot choose between commands; "Less output" does not say what is removed or whether it is safe for parsing. Two aliases for `install` (one, `add`, implying a different semantic — adding to the manifest) invite inconsistent invocations.
- fix direction: write rules-then-context summaries (e.g. `list  List installed project dependencies as name/version; read-only`). Rename `ls` to `list` with `ls` as a declared deprecated alias. Declare aliases in the schema and use only canonical names in examples; drop `add` or give it distinct, documented semantics.

### F8 — No caller-settable timeout on networked commands
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help` options
- impact: `install`, `sync`, and the update check (F3) hit the network with no `--timeout-ms` and no declared retry behavior; agents cannot bound their runtime.
- fix direction: add global `--timeout-ms`, declare retry defaults and latency class per command (`install`/`sync`: `network` or `slow`).

### F9 — Ambient state undocumented, no isolation or inspection
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`
- impact: a package manager typically reads registry config, credentials, and a global cache; agents cannot see or disable them, so results vary across machines.
- fix direction: document config files, env vars, credential sources, cache location, and precedence; add `--no-config`/`--isolated` and a `config show --resolved` (secrets redacted).

### F10 — No reconciliation contract for interrupted mutations
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `install`, `sync`, `clean`
- impact: after a timeout or kill during `install`/`sync`, agents cannot tell whether the lockfile or cache was written; they may retry blindly. (Would be P1 if shown unreconcilable; here it is simply undeclared.)
- fix direction: declare atomic lockfile writes, interrupt semantics, which commands are safe to retry, and how to verify state (e.g. `list` or a `status` command).

### F11 — `--` end-of-options support undeclared
- severity: P3
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`
- impact: package names beginning with `-` could be parsed as flags.
- fix direction: support and declare `--`; quote operands in canonical examples.

### F12 — Marketing banner in `--help`
- severity: P3
- type: design-issue
- evidence: observed
- location: `depman --help` line 1 (`DepMan 3.2 — the friendly dependency manager!`)
- impact: wasted tokens; version belongs in `depman version`.
- fix direction: lead `--help` with usage; expose version via `version`/schema.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F7, F11 (aliases, vague naming, `ls` abbreviation) |
| Machine Schema | F5 |
| Stdin Contract | not-checked — no stdin-reading commands shown; absence of declaration is part of F5 |
| Shell Safety | F11 |
| Agent-Safe Invocation | F1, F5 (no machine profile), F8 |
| Output | F2, F4 (error on stdout) |
| Errors And Exit Codes | F4 |
| Ambient State | F9 |
| Mutations And Long-Running Work | F1, F6, F10 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F7, F12 |
| Tests | not-checked — no source or tests supplied; at minimum add tests pinning F1 (non-TTY `sync` never blocks), F2 (`ls --json` stdout is pure JSON), F4 (error payload and exit codes) |

## Open questions / assumptions

- F1 assumes `sync` prompts even when stdin is not a TTY; one probe (`depman sync </dev/null`, with a timeout, in a scratch project) would confirm. If it already fails fast, F1 drops to a P2 contract gap.
- Stderr content is unknown because it was discarded; the structured error may already exist there, but the stdout pollution in F2/F4 stands regardless.
- Whether `--quiet` removes the banner/progress from `ls --json` is unknown; even if so, JSON output must be clean without it.
- Whether the update check actually hits the network (F3) is inferred from its message.

## Release decision and remediation plan

Release-blocking: F1 (P0), F2, F3, F4 (P1).

1. Fix stdout hygiene and update check: JSON-only stdout under `--json`/non-TTY; banners, timing, and update checks off in machine mode (F2, F3, F12).
2. Structured stderr errors with symbolic codes and a declared exit-code map (F4).
3. Non-interactive `sync`/`clean`: fail fast without `--yes`, add `--dry-run` (F1, F6).
4. Ship `depman schema` + fingerprint and a `--machine` profile; rewrite help summaries (F5, F7).
5. Then timeouts, ambient-state docs/isolation, reconciliation, `--` (F8–F11), with tests for each.
~~~~~~
