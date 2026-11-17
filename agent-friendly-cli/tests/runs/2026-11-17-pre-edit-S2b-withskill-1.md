# Scenario 2b (audit, fail-fast control) — with-skill arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 63,856 (final-turn context plus output, read from the transcript)
- **Output words:** 1,433
- **Transcript sha256:** `f757bb186bc65da00f9baa6959b7ede377ce0ff8d96d66dd0888225ed0066560` (session-local copy; not committed)
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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S2b-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 ... severity: P2; `sync` does not hang on `< /dev/null` Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — `ls --json` mixes a banner, progress text and a summary with the JSON on stdout |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — agent-friendliness audit

Audience: the tool's author (who can change anything).
Task: an audit of an existing CLI, done only from the captures you supplied (I could not run it).
All `observed` labels below mean "seen in the verbatim capture the user supplied."
Stream attribution is observed: each capture discards stderr, except the last one, which shows only stderr.

## Findings (ordered by severity)

### F1 — `ls --json` mixes a banner, progress text and a summary with the JSON on stdout
- severity: P1 (fixed placement: success stdout mixes banners, progress or summaries with the payload)
- type: impl-bug
- evidence: observed (`depman ls --json 2>/dev/null`)
- location: the `ls --json` capture, lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- impact: `depman ls --json | jq` fails, because stdout is not valid JSON. Agents have to scrape out the array line by guesswork.
- fix direction: In JSON or machine mode, stdout carries only the payload. Send the banner, progress and timing to stderr, or drop them entirely when stdout is not a TTY or a machine flag is set.

### F2 — A read command (`ls`) checks for updates
- severity: P1 (fixed placement: a hidden side effect on a read path; nothing shows the effect stays on the local machine)
- type: design-issue
- evidence: observed that it prints `Checking for updates...`; inferred that this is a network call
- location: the `ls --json` capture
- impact: Each read adds latency and an outbound call the user did not ask for. It can stall or fail in sandboxed or offline agents, and it makes the output nondeterministic.
- fix direction: Make update checks opt-in and turn them off in machine mode and non-TTY mode. They must never write to stdout. Add a declared opt-in flag or setting for them.

### F3 — The `install` failure gives no symbolic code, prints its message on stdout, and returns the generic exit 1
- severity: P1 (fixed placement: an error offers no symbolic code to branch on)
- type: impl-bug
- evidence: observed (`depman install nonexistent-pkg 2>/dev/null` still shows `Error: something went wrong (see log)`, so the message went to stdout; `$?` = 1)
- location: the `install` capture
- impact: An agent cannot tell "package not found" from network, auth or usage failures. It cannot decide whether to retry, and it has to parse English from the success stream. "see log" names no log path.
- fix direction: Write a structured error to stderr, in the same shape `sync` already uses: `{"code":"PACKAGE_NOT_FOUND","message":...,"temporary":false,"resource_id":"nonexistent-pkg","hint":...}`. Exit 3 (not found). Leave stdout empty on failure. If a log exists, put its location in a `path` or `details` field.

### F4 — No machine-readable schema, no machine profile, and `--json` is not documented
- severity: P1 (agents cannot reliably discover how to invoke or parse the commands)
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists no `schema` command, `--json`, `--format` or machine flag, yet `ls` and `sync` accept `--json`)
- location: the `--help` capture
- impact: Agents have to guess flags and output shapes. There is no output-class declaration, exit-code map or error catalog to check against, and no fingerprint to cache.
- fix direction: Add `depman schema` and `depman schema --fingerprint`. The schema should cover:
  - the command tree, with aliases declared as aliases
  - flags with types and defaults
  - read-only vs mutating status per command
  - output class per command (`ls` → `list`)
  - the shape dialect
  - the stdin contract
  - the exit-code map and a per-command error catalog (`sync` → `CONFIRMATION_REQUIRED`, exit 4, suppressed by `--yes`)
  - side effects and latency class
  - `schema_version`, fingerprint and `fingerprint_scope`

  Define a single machine profile, such as `--machine`, that implies JSON output, no prompts, no banner, no update check and no color.

### F5 — Exit 4 for `CONFIRMATION_REQUIRED` is undeclared and clashes with the conventional meaning (unauthenticated)
- severity: P2
- type: schema-gap
- evidence: observed (`exit=4`) together with absence-of-evidence (no exit-code map)
- location: the `sync` capture
- impact: An agent branching on the shell exit code may treat this as an auth failure and try to log in again.
- fix direction: Declare the exit-code map in the schema. Either map confirmation-required to usage/validation (2) or to a declared domain code (10–125), or document that 4 means this for depman. The symbolic `code` stays the authoritative branch key.
- Positive: `sync` does not hang on `< /dev/null`. It fails fast with a well-formed structured error on stderr, including `temporary:false` and a `hint`. This is the right pattern; apply it to every command.

### F6 — Mutating commands have no `--dry-run`, and `clean` has no visible confirmation or guard
- severity: P2 (raise it if `clean` turns out to delete shared state without confirmation)
- type: design-issue
- evidence: absence-of-evidence (`--help`)
- location: `--help`: the `install`, `clean` and `sync` entries
- impact: Agents cannot preview what `clean` would delete from the global cache or what `sync` would rewrite. There is no idempotency or reconciliation guidance after an interrupt, and no concurrency guarantee for writes to the lockfile or cache.
- fix direction: Add `--dry-run` that returns `dry_run: true` and the planned effect. For each mutating command, declare whether it is safe to retry, what an interrupt leaves behind, and how lockfile and cache writes are kept atomic or locked.

### F7 — Help text gives agents too little to choose commands
- severity: P2
- type: design-issue
- evidence: observed (`--help`)
- location: the `--help` capture
- impact:
  - `ls — Show stuff` does not say what it lists (installed deps? the lockfile? the global cache?).
  - `--quiet — Less output` leaves undefined what it suppresses.
  - The `add` alias of `install` is noun/verb ambiguity.
  - `sync` puts its prerequisite (it needs `--yes` or confirmation) in a parenthetical, after the summary.
- fix direction: Write each summary rules-first and task-selective, e.g. "ls: List installed dependencies from the lockfile (read-only)". Define exactly what `--quiet` suppresses. Declare aliases as migration-only in the schema and use only the canonical name in examples. State `sync`'s confirmation requirement and `--yes` up front.

### F8 — The help banner is marketing text
- severity: P3
- type: design-issue
- evidence: observed
- location: the first line of `--help`
- impact: Minor token cost, and it is noise in front of the usage line.
- fix direction: Lead with the usage line. Report the version through `depman version` or the schema.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F7 (aliases, vague naming); otherwise not-checked, because I don't have the flags for each command |
| Machine Schema | F4 |
| Stdin Contract | F4 (undeclared); `sync` with empty stdin is observed to fail fast, not block |
| Shell Safety | not-checked: no `--` support was shown and there are no examples with hostile operands; it is also missing from the schema (F4) |
| Agent-Safe Invocation | F4 (no machine profile); `sync` does not block in non-TTY mode (OK, observed); metadata-path latency not-checked |
| Output | F1 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | not-checked: no config, env or credential information was supplied; no inspection or `--isolated` affordance is visible (absence-of-evidence, folded into F4) |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7, F8 |
| Tests | not-checked: no source or tests were supplied |

## Open questions and assumptions

- I assumed `Checking for updates...` makes a network call. If it only reads a local cache, F2 may drop to P2.
- Is `--json` a global flag or specific to some commands? Does `install` accept it, and does its error turn structured when it is set?
- What does "see log" refer to, and where is that log?
- Does `clean` prompt, and if it does, does it fail fast like `sync`?
- Does depman read config or environment variables (registry URL, tokens)? If it does, the Ambient State section applies in full.

## Suggested remediation order

1. Release blockers (P1): F1, F2, F3, F4. Clean up stdout, gate the update check, make every error structured the way `sync`'s is, and ship a schema plus a machine profile.
2. Next: F5, F6, F7 (exit-code map, dry-run and mutation semantics, help wording).
3. Polish: F8.
4. Add tests that pin JSON-only stdout, the structured error and exit code for each failure, non-TTY behaviour without prompts, and update checks staying off in machine mode.
~~~~~~
