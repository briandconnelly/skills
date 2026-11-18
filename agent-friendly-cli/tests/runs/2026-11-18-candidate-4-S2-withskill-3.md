# Scenario S2 — with-skill arm 3 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1423
- **Scoring:** blinded packet, output id `o39`; the scorer received the assertion block verbatim and no arm labels

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
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S2-withskill-3.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 — sync prompt blocking risk + what capture establishes/does not
- o39: PASS — part1 "hangs waiting on terminal input" pass; part2 "inferred — `--help` says... nothing says the prompt is suppressed" pass.
### A2 — hang finding separates shown prompt from deduced hang
- o39: PASS — "`--help` says `sync` 'asks for confirmation first'; nothing says the prompt is suppressed when stdin is not a TTY".
### A3 — stdout pollution flagged as breaking parsing, established by capture
- o39: PASS — part1 "`json.loads(stdout)` fails" pass; part2 "Evidence: observed" pass.
### A4 — unstructured error + generic exit 1, no symbolic code
- o39: PASS — "no symbolic code ... use a generic exit code".
### A5 — update check on read path as hidden side effect
- o39: PASS — "hidden side effect on a read path".
### A6 — `clean` without `--dry-run`
- o39: PASS — F6 "`clean` is a destructive mutation with no dry run".
### A7 — aliases `i`, `add` and `ls Show stuff`
- o39: PASS — part1 "aliases `i, add`" pass; part2 "`ls  Show stuff`" pass.
### A8 — states areas captures cannot answer
- o39: PASS — "Shell Safety | not-checked"; "Stderr content was never captured ... not-checked".
### C1 — P0–P3 + template fields (severity, type, evidence, location, impact, fix direction) on every finding
- o39: FAIL — F11 has no Location field.
### C2 — literal evidence labels
- o39: PASS — same three words used.
### C3 — hang P0, pollution ≥P1
- o39: PASS — F1 P0, F2 P1.
### C4 — coverage table with not-checked reasons
- o39: PASS — table, "not-checked — no stdin usage shown".

## Verbatim final output

~~~~~~~~markdown
# depman 3.2 — agent-friendliness audit

Audience: the tool's author (can change anything).
Evidence base: three user-supplied verbatim captures with stderr discarded, so every line shown is stdout.
I did not run the tool; `observed` below means "observed in the supplied capture".

## Findings (ordered by severity)

### F1 — `sync` prompts for confirmation with no declared non-interactive behavior
- Severity: P0 (blocking behavior in non-TTY/machine mode is a fixed P0 placement)
- Type: design-issue
- Evidence: inferred — `--help` says `sync` "asks for confirmation first"; nothing says the prompt is suppressed when stdin is not a TTY, and no machine mode exists to suppress it.
- Location: `depman --help`, `sync` entry
- Impact: an agent or CI job calling `depman sync` without `--yes` hangs waiting on terminal input, or (worse) reads a piped stdin as the answer.
- Fix direction: when stdin is not a TTY, or in machine mode, never prompt; fail fast with a structured error (e.g. `code: "CONFIRMATION_REQUIRED"`, exit `2`, `temporary: false`, `hint` naming `--yes`). Keep `--yes` as the explicit action trigger, and add `--dry-run` showing the planned lockfile diff.

### F2 — `ls --json` stdout mixes banner, progress, and a summary with the payload
- Severity: P1 (fixed placement: successful stdout mixing banners/progress/summaries)
- Type: impl-bug (`--json` promises JSON; stdout is not parseable JSON)
- Evidence: observed — `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` all appear on stdout around the array.
- Location: `depman ls --json` capture
- Impact: `json.loads(stdout)` fails; agents resort to fragile line-scraping and burn tokens on decoration.
- Fix direction: in `--json` (and any non-TTY stdout) write only the JSON array to stdout; send banner/progress/timing to stderr, and suppress them entirely in machine mode.

### F3 — Update check on a read path
- Severity: P1 (hidden side effect on a read path; no evidence it is local-only, so no downgrade to P2)
- Type: design-issue
- Evidence: observed — `Checking for updates...` printed by `ls`; that it makes a network call is inferred from the message.
- Location: `depman ls --json` capture
- Impact: undeclared network access on a read verb adds latency, can fail or hang offline/sandboxed, and leaks usage.
- Fix direction: make update checks opt-in, never run them in machine mode or non-TTY, never print to stdout; declare any remaining network behavior per command.

### F4 — Errors carry no symbolic code, go to stdout, and use a generic exit code
- Severity: P1 (fixed placement: errors with no symbolic code)
- Type: design-issue
- Evidence: observed — with stderr discarded, `Error: something went wrong (see log)` still appears, so the error is on stdout; exit is `1` for what is a not-found package.
- Location: `depman install nonexistent-pkg` capture
- Impact: agents cannot tell not-found from network failure from auth failure, cannot decide whether to retry, and an error on stdout can be mistaken for payload. "see log" points at an unnamed file.
- Fix direction: write errors to stderr as a structured object with required `code`, `message`, `temporary` (e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found","temporary":false,"resource_id":"nonexistent-pkg","hint":"check the package name"}`); map not-found to exit `3`; keep stdout empty on failure; declare a fallback `INTERNAL` code; if a log exists, put its path in a `path` field.

### F5 — No machine schema, machine profile, or discoverable `--json`
- Severity: P1 (agents cannot reliably discover how to invoke or parse)
- Type: schema-gap
- Evidence: absence-of-evidence — `--help` lists no `schema`/`version` command, no fingerprint, no `--json`/`--format`/`--machine` flag; `--json` works on `ls` but is undocumented.
- Location: `depman --help`
- Impact: agents must guess flags per command and infer output shapes, exit codes, and side effects from prose.
- Fix direction: add `depman schema` (plus `schema <command>` and `schema --fingerprint`) declaring commands, aliases, flags, stdin contract, read-only vs mutating, output class per command (`ls` = `list`), error catalog, exit codes, side effects, latency class; add a single `--machine` flag implying JSON output, no prompts, no color/progress/banners; document `--format json`.

### F6 — `clean` is a destructive mutation with no dry run or declared confirmation
- Severity: P2
- Type: schema-gap
- Evidence: inferred from `--help` ("Remove unused packages from the global cache"); no `--dry-run` flag is listed, and unlike `sync` it does not say it confirms.
- Location: `depman --help`, `clean` entry
- Impact: an agent cannot preview what will be removed; shared global cache means the effect reaches other projects.
- Fix direction: add `--dry-run` (output with `dry_run: true` and the list of packages to remove); declare whether `clean` needs `--yes`; declare concurrency safety of global-cache writes (locking or atomic replacement) and interrupt semantics.

### F7 — Vague and non-task-selective help prose; undeclared aliases
- Severity: P2
- Type: design-issue
- Evidence: observed — `ls  Show stuff`, `--quiet  Less output`; `install` has aliases `i, add` with no migration rationale.
- Location: `depman --help`
- Impact: "Show stuff" does not tell an agent whether `ls` lists installed deps, the lockfile, or the cache; `--quiet` does not say what is suppressed or whether it affects stdout payload. Multiple aliases multiply invocation paths.
- Fix direction: rewrite summaries rules-first (e.g. `list  List installed dependencies of the current project as name/version records`); prefer full word `list` with `ls` as a declared alias; define exactly what `--quiet` suppresses; declare aliases in the schema and use only the canonical name in examples.

### F8 — Ambient state undocumented
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence — the tool uses a global cache, a lockfile (presumably cwd-selected), and an unnamed log, none of which are documented; no `--no-config`/`--isolated`, no resolved-config inspection.
- Location: `depman --help`
- Impact: agents cannot predict which project/lockfile is acted on or reproduce runs.
- Fix direction: document config files, env vars, cache and log locations, cwd selection plus an override flag (e.g. `--project <path>`), precedence; add `config show --resolved` and an isolation flag.

### F9 — No caller-settable timeout on networked commands
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence — `install`/`sync` presumably hit a registry; no `--timeout-ms` and no declared retry behavior.
- Location: `depman --help`
- Impact: agents cannot bound runtime; an interrupted `install` has undeclared outcome.
- Fix direction: add `--timeout-ms`, declare retry defaults, a transport-failure error code, and what an interrupt leaves behind (atomic lockfile writes).

### F10 — `--help` itself prints a decorative banner
- Severity: P3
- Type: design-issue
- Evidence: observed — `DepMan 3.2 — the friendly dependency manager!`
- Location: `depman --help`
- Impact: minor token waste; acceptable for human help, but version belongs in `depman version`.
- Fix direction: lead help with usage and binding constraints; expose version via a `version` command.

### F11 — No evidence of contract tests
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence (no source or tests supplied)
- Impact: F2/F4 style regressions ship silently.
- Fix direction: add tests for clean JSON stdout under `--json`, non-TTY no-prompt behavior for `sync`, error payloads and exit codes, dry-run output, and schema snapshots.

Release gating: F1 (P0) and F2–F5 (P1) block a release until fixed.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F7 (aliases, abbreviations, vague verbs) |
| Machine Schema | F5 |
| Stdin Contract | F1 (prompt vs piped stdin); otherwise not-checked — no stdin usage shown |
| Shell Safety | not-checked — no `--` support or hostile-argument evidence in captures |
| Agent-Safe Invocation | F1, F5, F9 |
| Output | F2, F4 (error on stdout) |
| Errors And Exit Codes | F4 |
| Ambient State | F8 |
| Mutations And Long-Running Work | F1, F6, F9 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F7, F10 |
| Tests | F11 |

## Open questions / assumptions

- I assumed "Checking for updates..." performs a network request; if it is a local-only check, F3 drops to P2.
- I assumed `sync` prompts even when stdin is not a TTY; if it already auto-declines or errors non-interactively, F1 drops — but that behavior still needs declaring.
- Stderr content was never captured; stderr framing and whether errors also appear there are not-checked.
- Unknown whether `--json` is supported by commands other than `ls`.

## Suggested remediation order

1. Make `sync` never prompt in non-TTY/machine mode (F1).
2. Clean stdout for `--json`; move decoration to stderr; remove update check from reads (F2, F3).
3. Structured stderr errors with symbolic codes and a declared exit map (F4).
4. Add `--machine` and `depman schema` (F5), then F6–F11.
~~~~~~~~
