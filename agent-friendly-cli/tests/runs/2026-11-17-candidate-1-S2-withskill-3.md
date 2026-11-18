# Scenario 2 (audit) — with-skill arm 3 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 4/4 conformance
- **Tokens:** 71,446 (final-turn context plus output, read from the transcript)
- **Output words:** 1,266
- **Transcript sha256:** `b3e19892ca14c82de82bd04a3ef4fa233f91eb9300f7ec52c93f28e84d52658a` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S2-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | evidence: `inferred` from `--help` ("Sync the lockfile (asks for confirmation first)"); not observed hanging. Parts: sync prompt flagged as automation-blocking risk = pass; says what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | `inferred` from `--help` ... not observed hanging |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: `observed` (user-supplied capture, `2>/dev/null`) ... `depman ls --json \| jq` fails Parts: flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Errors carry no symbolic code, go to stdout, and use a generic exit code |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Read command performs an update check (undeclared network call) |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` mutates a shared global cache with no dry run |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | "Show stuff" doesn't say what is listed ...; `add` suggests a distinct operation Parts: alias duplication = pass; vague ls description = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Tests \| not-checked — no source or tests supplied |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | severity: `P0` ... type: `schema-gap` ... evidence ... location ... impact ... fix direction Parts: P0-P3 words = pass; template fields = pass |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | `inferred` / `observed` / `absence-of-evidence` used literally |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 severity: `P0`; F2 severity: `P1` Parts: hang P0 = pass; pollution P1+ = pass |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **PASS** | \| Stdin Contract \| not-checked — no info on stdin use ... |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author, so findings lead with contract gaps and concrete redesign guidance.
Task: audit of an existing CLI from captured material only; no probes were run.
All captures discard stderr, so every quoted line is stdout; stderr behavior is unknown.

## Findings (by severity)

### F1 — `sync` prompts for confirmation; no declared non-interactive guarantee
- severity: `P0` (blocking in non-TTY mode is a fixed P0 placement)
- type: `schema-gap`
- evidence: `inferred` from `--help` ("Sync the lockfile (asks for confirmation first)"); not observed hanging.
- location: `depman --help`, `sync` line; `--yes` option.
- impact: an agent calling `depman sync` without `--yes` likely waits on terminal input forever in CI or a non-TTY harness. `--yes` exists but nothing says the prompt is suppressed when stdin is not a TTY, nor what happens if `--yes` is absent there.
- fix direction: when stdin is not a TTY (or in machine mode), never prompt; fail fast with a structured error (e.g. `CONFIRMATION_REQUIRED`, exit `2`, `hint` naming `--yes`). Declare this in a schema and in help.

### F2 — Success stdout mixes banner, progress, and summary with the JSON payload
- severity: `P1` (fixed placement)
- type: `impl-bug` (`--json` was requested, yet non-JSON lines surround the payload)
- evidence: `observed` (user-supplied capture, `2>/dev/null`)
- location: `depman ls --json 2>/dev/null` output: `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- impact: `depman ls --json | jq` fails; agents must strip lines heuristically, which breaks the moment the banner text changes.
- fix direction: in JSON/machine mode, stdout is exactly the payload. Move banner, progress, and timing to stderr, and suppress them entirely in machine mode and when stderr is not a TTY.

### F3 — Read command performs an update check (undeclared network call)
- severity: `P1` (hidden side effect on a read path; no evidence it is local-only)
- type: `design-issue`
- evidence: `observed` (`Checking for updates...` on stdout of `ls`)
- location: `depman ls --json` output
- impact: adds latency and network dependence to a read, can fail or hang offline/sandboxed, and pollutes stdout (compounds F2).
- fix direction: make update checks opt-in, never on by default; never in machine mode; never on stdout.

### F4 — Errors carry no symbolic code, go to stdout, and use a generic exit code
- severity: `P1` (no symbolic code to branch on is a fixed P1 placement)
- type: `design-issue`
- evidence: `observed` (capture shows the error on stdout with stderr discarded; `echo $?` → `1`)
- location: `depman install nonexistent-pkg 2>/dev/null` → `Error: something went wrong (see log)`, exit `1`
- impact: an agent cannot tell "package not found" from network failure, auth failure, or a bug; cannot decide whether to retry; the referenced log has no path. Writing the error to stdout means a caller that parses stdout reads an error as payload.
- fix direction: emit a structured error on stderr (`{"code":"PACKAGE_NOT_FOUND","message":...,"temporary":false,"resource_id":"nonexistent-pkg"}`), empty stdout on failure, exit `3` for not-found; declare an exit-code map and a fallback code (`INTERNAL`, exit `1`). If a log is written, return its `path` in the error.

### F5 — No machine-readable contract or machine profile
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence` (help lists no `schema`, `version`, `--json`, or `--machine`; `--json` works on `ls` but is undocumented)
- location: `depman --help`
- impact: agents must discover flags by trial (as with `--json`), cannot learn output shapes, exit codes, per-command errors, mutating vs read-only classification, or which commands support JSON.
- fix direction: add `depman schema` (plus `--fingerprint` and per-command `depman schema <command>`) declaring command tree, aliases, flags, output class and shape, error catalog, side effects, latency class; add a single `--machine` flag implying JSON, no prompts, no banners, no color, no update check.

### F6 — `clean` mutates a shared global cache with no dry run, and `install`/`sync` declare no mutation contract
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help`)
- location: `depman --help`, `clean`, `install`, `sync`
- impact: agents cannot preview what `clean` will delete, cannot tell which commands mutate, and get no retry/reconcile guidance after a timeout or interrupt during `install`/`sync`.
- fix direction: add `--dry-run` (output includes `dry_run: true` and the planned removals) to `clean`, `install`, and `sync`; classify each command read-only or mutating in the schema; declare signal semantics, lockfile atomicity/locking under concurrent runs, and which mutations are safe to retry.

### F7 — Ambient state undocumented and not disable-able
- severity: `P2`
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `depman --help` (global cache, lockfile, unnamed log; no config/env/registry/credential info)
- impact: agents cannot predict which project/lockfile is selected (cwd?), which registry and credentials are used, or where the log lives.
- fix direction: document config files, env vars, credentials, cache paths, cwd selection with an override flag, and precedence; add `depman config show --resolved`; add `--isolated`/`--no-config`.

### F8 — Prose surfaces are not task-selective; aliases and vague flags
- severity: `P2`
- type: `design-issue`
- evidence: `observed` (`--help`)
- location: `ls  Show stuff`; `install (aliases: i, add)`; `--quiet  Less output`; banner line "the friendly dependency manager!"
- impact: "Show stuff" doesn't say what is listed (installed? direct deps? global cache?); `add` suggests a distinct operation (add to manifest) that may or may not differ from `install`; `--quiet` doesn't say what is suppressed or on which stream.
- fix direction: rules-first summaries (e.g. `list  List installed packages in the current project as name+version; read-only`); prefer full word `list` with `ls` as a declared alias; keep aliases only for migration and declare them in schema; define `--quiet` precisely. Drop marketing text from help.

### F9 — No caller-settable network timeout; no version command
- severity: `P3`
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `depman --help`
- impact: `install`/`sync` (and the update check) can stall with no caller control; version is only discoverable via banner text.
- fix direction: add `--timeout-ms` to networked commands with declared retry defaults; add `depman version` emitting JSON.

## Checklist coverage

| Section | Status |
| --- | --- |
| Command Model | F8 |
| Machine Schema | F5 |
| Stdin Contract | not-checked — no info on stdin use; folded into F5 (undeclared) |
| Shell Safety | not-checked — no evidence on `--` support or argument handling; should be declared in schema (F5) |
| Agent-Safe Invocation | F1, F5, F9 |
| Output | F2 |
| Errors And Exit Codes | F4 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F8 |
| Tests | not-checked — no source or tests supplied |

## Open questions / assumptions

- stderr was discarded in every capture: what does depman write to stderr? Is anything already structured there?
- Does `sync` without `--yes` actually block when stdin is not a TTY, or auto-decline? (F1 is inferred.)
- Is `--json` supported on commands other than `ls`, and is there any non-TTY detection today?
- Does the update check hit the network on every command, and does `--quiet` suppress it?
- Where is "the log" written?

## Suggested remediation order

1. Release blockers (P0/P1): no prompts in non-TTY/machine mode (F1); payload-only stdout (F2); remove default update check (F3); structured stderr errors with symbolic codes and an exit-code map (F4).
2. Then: `--machine` + `schema` (F5), dry runs and mutation contract (F6), ambient-state docs and isolation (F7), help text (F8), timeouts/version (F9).
3. Add automated tests pinning stdout purity, non-TTY prompt suppression, and error codes/exit mappings.
~~~~~~
