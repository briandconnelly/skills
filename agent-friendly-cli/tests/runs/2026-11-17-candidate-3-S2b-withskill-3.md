# Scenario 2b (audit, fail-fast control) — with-skill arm 3 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 65,495 (final-turn context plus output, read from the transcript)
- **Output words:** 1,639
- **Transcript sha256:** `c36be09a260503d39ed440cc1a1bac661c125ce955bc7e8c5cd4b98c8f2d3fc0` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

## Exact prompt given

> Audit this CLI for agent-friendliness and report your findings.
> You cannot run the tool; you have only this captured material.
> Each capture discards stderr (`2>/dev/null`), so every line shown is stdout, except the last, which shows stderr only (`2>&1 >/dev/null`).
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
>
> $ depman sync --json < /dev/null 2>/dev/null; echo "exit=$?"
> exit=4
> $ depman sync --json < /dev/null 2>&1 >/dev/null
> {"code":"CONFIRMATION_REQUIRED","message":"sync needs confirmation","hint":"pass --yes","temporary":false}
> ```

## Arm instructions

> You are a test arm in an evaluation.
>
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S2b-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 (sync, P2): "with stdin set to `/dev/null`, `sync` did not hang"; top severity used is P1 (F1-F4) Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — `ls --json` stdout mixes a banner, progress, and a summary with the JSON payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author, who can change anything, so findings are ordered for release gating and give redesign guidance.
Task: review of an existing CLI.
I could not run anything. Every `observed` finding comes from the user's verbatim captures. Each capture shows stdout only, except the last, which shows stderr only.
Release gate: F1–F4 are P0/P1 and block a release.

## Findings

### F1 — `ls --json` stdout mixes a banner, progress, and a summary with the JSON payload
- Severity: P1
- Type: impl-bug (`--json` promises a parseable payload)
- Evidence: observed (user capture, stdout only)
- Location: `depman ls --json 2>/dev/null` prints `✨ DepMan 3.2`, `Checking for updates...`, the array, and then `Done in 0.42s ✓`, all on stdout.
- Impact: `json.loads(stdout)` fails. Agents then have to strip lines by guesswork, and that breaks whenever the decoration changes. The non-ASCII glyphs also cost tokens.
- Fix direction: In JSON or machine mode, stdout carries only the payload. Send diagnostics to stderr and frame them as declared (`single-error-object` or `ndjson-typed`). Drop the banner and the timing summary there entirely. Add a `--machine` profile that implies `--json`, no color, no progress, and no prompts. Add a snapshot test that asserts `ls --json` stdout parses as exactly one JSON value.

### F2 — Update check runs on a read path, by default
- Severity: P1 (hidden network side effect on a read; there is no evidence it stays on the local machine)
- Type: design-issue
- Evidence: observed (`Checking for updates...` on `ls` stdout)
- Location: `depman ls --json`
- Impact: The update check adds an undeclared network call and latency to a read. It can fail or stall when offline or in sandboxed CI, and it leaks usage. Its progress text also contaminates stdout (see F1).
- Fix direction: Make update checks opt-in. Never run them in machine mode or non-TTY mode, and never print them on stdout. Declare any remaining network use in the schema's side effects and latency class.

### F3 — `install` failure gives no symbolic code, no structure, and an unspecific message, and it goes to stdout
- Severity: P1 (errors offer no symbolic code to branch on)
- Type: design-issue
- Evidence: observed. The capture discarded stderr, so `Error: something went wrong (see log)` was written to stdout. Exit was `1`.
- Location: `depman install nonexistent-pkg`
- Impact: An agent cannot tell "package not found" apart from network, auth, or registry failures. It cannot decide whether to retry. "see log" names no log path. The error text on stdout can also be read as success payload.
- Fix direction: Write a structured error to stderr and leave stdout empty on failure. For example: `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","hint":"check the package name"}` with exit `3` (not found). Map transport failures to their own codes with `temporary:true`. Declare a fallback `INTERNAL` code on exit `1`. If a log exists, return its path in a `path` or `details` field.

### F4 — No machine-readable schema, machine profile, or fingerprint; `--json` is not even listed
- Severity: P1. Agents cannot find out which flags exist (`--json` appears only in usage, not in `--help`), what output shapes to expect, or what the exit codes mean, so they cannot invoke or branch reliably.
- Type: schema-gap
- Evidence: absence-of-evidence (no `schema` command in help, and no listed `--json`, `--machine`, or `--dry-run`)
- Location: `depman --help`
- Impact: Agents fall back on trial and error and on parsing prose.
- Fix direction: Add `depman schema`, `depman schema <command>`, and `depman schema --fingerprint` with `fingerprint_scope`. The schema should declare:
  - the command tree with aliases (`i` and `add`, marked migration-only)
  - flags with types and defaults
  - the machine profile
  - read-only vs mutating status for each command
  - the output class (`ls` → `list`)
  - stdin contract, ambient state, and side effects
  - the exit-code map and per-command error catalogs
  - latency class
  - `schema_version` with its compatibility promise
  - the shape dialect (JSON Schema)

### F5 — `sync` uses exit 4 for confirmation-required, and nothing declares it
- Severity: P2
- Type: schema-gap
- Evidence: observed (`exit=4`, structured `CONFIRMATION_REQUIRED` on stderr)
- Location: `depman sync --json < /dev/null`
- Impact: In the common convention, exit `4` means unauthenticated, so a shell-level branch can misroute this. Nothing documents what 4 means for depman.
  The good part: with stdin set to `/dev/null`, `sync` did not hang. It emitted a well-formed error with `code`, `message`, `hint`, and `temporary`, only on stderr. Keep this.
- Fix direction: Declare the exit-code map. Either move confirmation-required to exit `2` (usage: a required flag is missing) or to a declared domain code ≥10. Put `CONFIRMATION_REQUIRED` in the `sync` error catalog with `retryable:false` and list `--yes` as the flag that suppresses it. Express the hint as structured data (for example `details.required_flag: "--yes"`) as well as prose.

### F6 — Mutating commands (`clean`, `install`, `sync`) declare no dry run, idempotency, or interrupt semantics
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence (`--help` shows no `--dry-run`)
- Location: `depman --help`
- Impact: `clean` deletes from a global cache with no preview. Agents cannot plan safely. After a timeout they cannot tell whether `install` or `sync` committed, or whether the lockfile or cache is half-written.
- Fix direction: Add `--dry-run` to every mutating command. Its output must include `dry_run: true` and the planned removals or additions, and it must exit `0` when the plan is valid. Declare which commands are safe to retry. Declare signal behavior and atomic lockfile and cache writes, with locking for concurrent runs. Decide whether `clean` needs `--yes` the way `sync` does, and declare it either way.

### F7 — Help prose is not task-selective, and its flags are vague
- Severity: P2 (ambiguous command design)
- Type: design-issue
- Evidence: observed (`--help` capture)
- Location:
  - `ls  Show stuff`
  - `--quiet  Less output`
  - `--yes  Assume yes`
  - `sync  Sync the lockfile` (direction unspecified)
- Impact: An agent cannot tell what `ls` lists (installed, direct, or transitive dependencies; local or global). It cannot tell which way `sync` writes (lockfile → installed, or installed → lockfile). It cannot tell what `--quiet` suppresses, or which commands `--yes` applies to.
- Fix direction: Write summaries rules-first, for example `ls  List installed packages in the current project (read-only; --json → array of {name, version})`. Say which commands are mutating. Name `sync`'s direction. Scope `--yes` to the commands that prompt. Replace `--quiet` with the machine profile, or define exactly what it suppresses. Consider renaming `ls` to `list` with `ls` as a declared alias.

### F8 — Ambient state is undocumented
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence. The tool clearly reads a global cache (`clean`), a lockfile selected by the current directory (`sync`), and presumably registry config and credentials, but none of these are declared.
- Location: `depman --help`
- Impact: Results depend on hidden cwd, config, and cache state that agents cannot inspect or override.
- Fix direction: Document the config, env, and credential sources and their precedence, and say how cwd selects the project. Add a `--project <path>` override, a `config show --resolved` style inspection command, and `--isolated` / `--no-config`. Accept registry tokens through env, a credential file, or stdin, never through argv.

### F9 — `ls` output class, ordering, and size behavior are undeclared
- Severity: P3
- Type: schema-gap
- Evidence: absence-of-evidence (payload observed; no declared shape)
- Location: `depman ls --json`
- Impact: Large dependency trees have no pagination or truncation contract. The sort order is unknown, so diffs between runs may be unstable.
- Fix direction: Declare `list` with a JSON Schema for items and a deterministic sort (by name). Declare limits and truncation, or switch to NDJSON for large trees. Add `--filter` and `--field`.

## Checklist Coverage

| Section | Status |
|---|---|
| Command Model | F7. Aliases are undeclared (F4). |
| Machine Schema | F4 |
| Stdin Contract | Partly OK: `sync` with `/dev/null` stdin did not hang (observed). The stdin contract is undeclared for every command (F4). Whether `sync` prompts on a TTY stdin is not-checked: no capture. |
| Shell Safety | not-checked: no evidence of `--` support or of how arguments are handled. Declare `--` in the schema. |
| Agent-Safe Invocation | F1, F2. No machine profile (F4). Non-blocking non-TTY stdin observed for `sync`. |
| Output | F1, F9 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | F8 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7 |
| Tests | not-checked: no source or tests supplied. At minimum, add pinned tests for F1 (stdout parses as JSON), F3/F5 (error payloads and exit codes), and non-TTY suppression. |

## Open Questions And Assumptions

- I assumed `--json` is a global flag. It is not in `--help`, so it might be specific to `ls` and `sync`.
- Did `install`'s message also appear on stderr? That capture discarded stderr, so this is unknown.
- Does `sync` prompt when stdin is a TTY? `--help` says it "asks for confirmation". That is fine for humans only if non-TTY and machine mode never prompt, which the capture suggests.
- Does the update check write anything locally, such as a cache timestamp? That would also be an implicit write on a read.
- Where is "the log" that the `install` error refers to?

## Suggested Remediation Order

1. Make stdout payload-only in JSON mode and remove the default update check (F1, F2).
2. Add structured errors with symbolic codes on every failure path (F3).
3. Ship `schema`, `--machine`, and the exit-code map, and remap `CONFIRMATION_REQUIRED` (F4, F5).
4. Add dry-run and mutation semantics, help prose, ambient-state inspection, and list contract details (F6–F9).
~~~~~~
