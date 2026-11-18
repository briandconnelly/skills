# Scenario 2 (audit) — with-skill arm 1 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 3/4 conformance
- **Tokens:** 64,266 (final-turn context plus output, read from the transcript)
- **Output words:** 1,164
- **Transcript sha256:** `4817edf8395f9864f437bffd8f8e005839aece14988ba6069ea5ac81f94e537a` (session-local copy; not committed)
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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S2-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | evidence: inferred (from `--help`: "asks for confirmation first"); non-TTY behavior not captured Parts: blocking risk = pass; established vs not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | evidence: inferred (from `--help` ...); non-TTY behavior not captured ... will likely hang |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: observed (`depman ls --json 2>/dev/null` prints ...) `json.loads(stdout)` fails Parts: flagged breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Errors have no symbolic code, no structure, and go to stdout |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Update check (network call) on a read path, printed to stdout |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | an agent cannot preview what `clean` will delete from a shared global cache |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | `ls Show stuff` ... three names for `install` add selection noise Parts: aliases = pass; Show stuff = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Tests: not-checked — no source or tests supplied |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | - severity: P1 - type: - evidence: - location: - impact: - fix direction: (all F1-F8) |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | evidence: observed / inferred / absence-of-evidence |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 severity: P0; F2 severity: P1 Parts: hang P0 = pass; pollution >=P1 = pass |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **FAIL** | Coverage is a bulleted list ('- Shell Safety: not-checked — ...'), not a table |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything), so findings lead with contract gaps and tool-side fixes.
Evidence basis: three user-supplied verbatim captures, stdout only (stderr discarded); I could not run the tool.
`observed` below means "observed in the user-supplied capture".

## Findings

### F1 — `sync` prompts for confirmation; no declared non-interactive behavior
- severity: P0
- type: design-issue
- evidence: inferred (from `--help`: "asks for confirmation first"); non-TTY behavior not captured
- location: `depman --help`, `sync` line
- impact: an agent or CI run of `depman sync` without a terminal will likely hang waiting on stdin, or fail in an undefined way.
  `--yes` exists but is not tied to `sync`, a machine profile, or non-TTY detection.
- fix direction: never prompt when stdin is not a TTY or in machine mode; in that case fail fast with a structured error (e.g. `CONFIRMATION_REQUIRED`, exit `2`, `hint` naming `--yes`).
  Declare `sync` as mutating with `--yes` and `--dry-run` in the schema, and add a non-TTY test.

### F2 — `ls --json` stdout mixes banner, progress, and summary with the payload
- severity: P1
- type: impl-bug (`--json` promises JSON; stdout is not parseable JSON)
- evidence: observed (`depman ls --json 2>/dev/null` prints `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` around the array)
- location: `ls --json` output, lines 1, 2, 4
- impact: `json.loads(stdout)` fails; agents must heuristically strip lines, which breaks whenever the banner text changes.
- fix direction: in `--json`/machine mode stdout carries only the payload; move banner, progress, and timing to stderr (or drop them) and suppress them entirely when stdout is not a TTY.
  Add a test asserting `ls --json` stdout parses as exactly one JSON document.

### F3 — Update check (network call) on a read path, printed to stdout
- severity: P1
- type: design-issue
- evidence: observed (`Checking for updates...` on `ls`)
- location: `ls --json` output, line 2
- impact: an undeclared network call on a read adds latency, can hang or fail offline/in sandboxes, leaks usage, and pollutes stdout.
  No evidence it is local-only, so no downgrade to P2.
- fix direction: make update checks opt-in, never run them in machine or non-TTY mode, and never write them to stdout.
  Declare any remaining network behavior in the schema.

### F4 — Errors have no symbolic code, no structure, and go to stdout
- severity: P1
- type: design-issue
- evidence: observed (`install nonexistent-pkg` printed `Error: something went wrong (see log)` to stdout, exit `1`)
- location: `depman install nonexistent-pkg` capture
- impact: the agent cannot tell not-found from network failure, auth, or a bug; it cannot decide whether to retry; "see log" names no log path.
  The error text appearing with stderr discarded shows failures are written to stdout, which corrupts payload parsing.
- fix direction: write failures to stderr as a structured object with `code` (e.g. `PACKAGE_NOT_FOUND`), `message`, `temporary`, and `resource_id`/`hint`; use exit `3` for not-found and declare the exit-code map.
  Keep stdout empty on failure; if a log exists, return its path in a `path` field.

### F5 — No machine schema, machine profile, or `--json` declaration
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists no `schema` command, no `--json`, no machine flag)
- location: `depman --help`
- impact: agents discover `--json` only by guessing; they cannot learn output shapes, error codes, which commands mutate, or side effects.
- fix direction: add `depman schema` (plus `schema <command>` and `schema --fingerprint` with `fingerprint_scope`) declaring commands, flags, output classes (`ls` → `list`), exit codes, per-command error catalogs, read-only vs mutating, and latency class.
  Add one `--machine` flag that implies JSON, no prompts, no banners, no update check.

### F6 — Mutating commands lack declared dry-run and safety controls
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (`clean`, `install`, `sync` show no `--dry-run`; `clean` touches a global cache)
- location: `depman --help`
- impact: an agent cannot preview what `clean` will delete from a shared global cache or what `sync` will rewrite, and cannot reason about retry after an interrupted install.
- fix direction: add `--dry-run` (output with `dry_run: true`) to `install`, `clean`, `sync`; declare idempotency/retry safety and interrupt semantics; make lockfile/cache writes atomic or locked.

### F7 — Ambient state undocumented
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (global cache, lockfile, update source, and log location are implied but not declared)
- location: `depman --help`
- impact: behavior depends on hidden cwd/global state the agent cannot inspect or isolate.
- fix direction: document config files, env vars, cache path, cwd-based project selection and its override flag, and precedence; add `config show --resolved` and an `--isolated`/`--no-config` flag.

### F8 — Vague, non-selective command and flag prose; aliases in help
- severity: P3
- type: design-issue
- evidence: observed (`ls  Show stuff`, `--quiet  Less output`, `install (aliases: i, add)`)
- location: `depman --help`
- impact: "Show stuff" does not say what is listed (installed deps? direct vs transitive? which project?); `--quiet` has no defined effect; three names for `install` add selection noise.
  `--yes` scope (which commands) is unstated.
- fix direction: rewrite summaries rules-first, e.g. `list  List installed dependencies of the current project (read-only)`; consider renaming `ls` to `list`.
  Keep aliases only for migration and declare them in the schema, not in canonical help.
  State which commands honor `--yes` and what `--quiet` suppresses.

## Checklist Coverage

- Command Model: F8 (vague summaries, aliases, `ls` abbreviation).
- Machine Schema: F5.
- Stdin Contract: covered partly by F1 (prompt on stdin); otherwise not-checked — no stdin usage shown.
- Shell Safety: not-checked — no `--` support or argument handling visible in the captures.
- Agent-Safe Invocation: F1, F2, F5 (no machine profile; non-TTY suppression absent on stdout).
- Output: F2; `ls` payload itself is a compact array of objects, which is fine for a small `list`; pagination/sorting not-checked.
- Errors And Exit Codes: F4.
- Ambient State: F7.
- Mutations And Long-Running Work: F1, F6.
- Side Effects And Telemetry: F3.
- Prose Surfaces: F8.
- Tests: not-checked — no source or tests supplied; every fix above should land with a pinning test (JSON-parse of stdout, non-TTY no-prompt, error payload + exit code, dry-run).

## Open Questions / Assumptions

- Does `sync` actually block when stdin is not a TTY, or does it auto-decline? A capture of `depman sync < /dev/null` with stderr kept would confirm F1.
- Does the update check go to the network, and is it cached? Assumed networked.
- What is on stderr? All captures discard it; banner/progress may also be duplicated there.
- Is `--json` supported on commands other than `ls`?
- Where is "the log" referenced by the error message?

## Suggested Remediation Order

1. Release blockers (P0/P1): F1 non-interactive `sync`; F2 clean JSON stdout; F3 remove update check from reads; F4 structured stderr errors with symbolic codes and exit map.
2. Then: `schema` + `--machine` (F5), `--dry-run` and mutation safety (F6), ambient-state docs and isolation (F7), help prose (F8).
~~~~~~
