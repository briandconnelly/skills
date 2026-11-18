# Scenario 2b (audit, fail-fast control) — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 65,217 (final-turn context plus output, read from the transcript)
- **Output words:** 1,585
- **Transcript sha256:** `e3fa5507d3642387a7a6b23caf1b67d09a3bd6b1aa20ad640359c8565e364a1d` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S2b-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | With `< /dev/null` it did not hang. ... F5 — P2 — Exit code `4` for `CONFIRMATION_REQUIRED` (top severity is P1) Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding carries top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — P1 — `ls --json` mixes a banner, an update-check line, and a summary into stdout with the payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 agent-friendliness audit

Audience: the tool's author, who can change anything.
I did not run the tool, so every `observed` label below refers to the verbatim captures you supplied.
Stream attribution comes from your redirections: lines shown under `2>/dev/null` are stdout, and the last capture shows stderr only.

## Findings (ordered by severity)

### F1 — P1 — `ls --json` mixes a banner, an update-check line, and a summary into stdout with the payload
- type: `design-issue`
- evidence: `observed` (your capture of `depman ls --json 2>/dev/null`)
- location: lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` around the JSON array
- impact: `depman ls --json | jq` fails, so agents have to strip lines heuristically, and that breaks whenever the banner text changes.
  Even `--json` does not give a clean payload, so there is no way to get one.
- fix direction: in JSON or machine mode, stdout carries only the JSON array.
  Send the banner, progress, and timing to stderr, and suppress them in machine mode or when stdout is not a TTY.
  Add a single `--machine` profile that implies `--json`, no color, no progress, and non-interactive behavior.

### F2 — P1 — The read path performs an update check (hidden side effect)
- type: `design-issue`
- evidence: `inferred` (the `Checking for updates...` line on `ls`; I cannot see whether a network call actually happened)
- location: `depman ls --json` output
- impact: a read verb makes an undeclared network call.
  That adds latency, can fail or hang offline or in a sandbox, and leaks usage.
  It stays at P1 because nothing shows the effect is confined to the local machine.
- fix direction: no update checks by default.
  Make them opt-in (for example `depman update-check`, or a config key), suppress them in machine mode, and never write them to stdout.

### F3 — P1 — `install` failures have no symbolic code, go to stdout, and say nothing useful
- type: `design-issue`
- evidence: `observed` (`depman install nonexistent-pkg 2>/dev/null` printed `Error: something went wrong (see log)` on stdout, exit `1`)
- location: install error path
- impact: an agent cannot tell "package not found" from network, auth, or internal failures.
  It cannot branch except by parsing English, which here carries no information anyway.
  The message points to an unnamed log, and the error lands on stdout, where a consumer would try to parse it as payload.
- fix direction: emit a structured error on stderr, with empty stdout, in the same shape `sync` already uses.
  For example: `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","hint":"check the package name"}`, with exit `3` (not found).
  Declare a fallback code such as `INTERNAL` (exit `1`) for uncaught failures.
  If a log exists, give its path in a `path` field.

### F4 — P2 — No machine-readable schema or contract
- type: `schema-gap`
- evidence: `absence-of-evidence` (only prose `--help` was supplied, and it lists no `schema`, `--help --json`, or similar command)
- location: `depman --help`
- impact: agents cannot discover flags per command, output shapes, which commands mutate, stdin behavior, exit codes, or error catalogs.
  For example, `--json` is not listed in help at all, yet `ls` and `sync` accept it.
- fix direction: add `depman schema` (full contract), `depman schema <command>`, and `depman schema --fingerprint` with `fingerprint_scope`.
  The schema should cover the command tree, flags with types, read-only vs mutating classification, output class (`ls` → `list`), the stdin contract, the exit-code map, the per-command error catalog (with `retryable` and `reconcile_first`), side effects, latency class, and `schema_version`.

### F5 — P2 — Exit code `4` for `CONFIRMATION_REQUIRED` is undeclared and collides with the conventional meaning
- type: `schema-gap`
- evidence: `observed` (`sync --json < /dev/null` → exit 4)
- location: `sync` error path
- impact: by this skill's convention, `4` means unauthenticated.
  With no declared map, a shell-level caller may treat this as an auth failure and try to re-login.
- fix direction: either use `2` (usage or validation: a required flag is missing) or a declared domain code in `10`–`123`.
  Publish the map in the schema.
  Agents should branch on `code` anyway.

### F6 — P2 — Mutating commands have no declared dry-run or confirmation contract; `clean` has no apparent guard
- type: `schema-gap`
- evidence: `absence-of-evidence` (help lists no `--dry-run`; `clean` "Remove[s] unused packages from the global cache" and, unlike `sync`, does not mention confirmation)
- location: `depman --help`
- impact: agents cannot preview `sync`, `install`, or `clean`.
  If `clean` deletes without `--yes`, an agent exploring the commands can wipe the shared global cache.
  If it prompts, it may block, and that would be P0, but this is unverified (see Open questions).
- fix direction: add `--dry-run` to `install`, `sync`, and `clean`, with `dry_run: true` and the planned effect in the output.
  Give `clean` the same no-TTY behavior as `sync`: refuse with `CONFIRMATION_REQUIRED` unless `--yes` is passed.
  Declare signal semantics, and declare lockfile and cache write safety under concurrent runs (atomic replace or locking).

### F7 — P2 — Prose surfaces are not task-selective, and aliases are undeclared outside help
- type: `design-issue`
- evidence: `observed` (help text)
- location: `depman --help`
- impact:
  - `ls — Show stuff` does not tell an agent what is listed: installed deps, the lockfile, or the cache.
  - `--quiet — Less output` does not say what is removed.
  - `--yes` does not say which commands honor it.
  - The `i` and `add` aliases for `install` widen the surface without a stated canonical form.
- fix direction:
  - Rewrite the summaries rules-first, for example `ls  List installed dependencies of the current project (read-only)`.
  - State which commands mutate and which require `--yes`.
  - Name `install` as canonical, and declare the aliases in the schema as aliases.
  - Rename `ls` to `list` (keeping `ls` as a declared alias) if you adopt consistent verbs.

### F8 — P2 — Ambient state is undocumented
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: help and schema (none)
- impact: `install`, `sync`, and `clean` almost certainly depend on the cwd (project and lockfile), a global cache, registry config, and possibly credentials.
  None of these sources, their precedence, or overrides are declared, so agent runs are not reproducible.
- fix direction:
  - Document the config files, env vars, cache location, cwd selection (with a `--project <path>` override), and precedence.
  - Add `depman config show --resolved` with secrets redacted.
  - Add `--isolated` / `--no-config`.
  - Accept registry tokens only through env, file, or keychain, never through flags.

### F9 — P2 — No caller-settable timeout on network commands
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `install` and `sync` (and the update check)
- impact: agents cannot bound how long a registry fetch takes.
- fix direction: add `--timeout-ms`, declare retry behavior, and add a transport-failure code (for example `NETWORK_ERROR`, `temporary: true`) to the catalogs.

### F10 — P3 — `--help` starts with a marketing banner
- type: `design-issue`
- evidence: `observed`
- location: `DepMan 3.2 — the friendly dependency manager!`
- impact: wastes tokens on a metadata path, and the version is not available in a parseable form.
- fix direction: put usage first, and add a `depman version --json` command.

### Positive note
`sync` without a TTY is a good example to copy everywhere else.
With `< /dev/null` it did not hang.
It wrote nothing to stdout, emitted a single structured error on stderr with `code`, `message`, `hint`, and `temporary:false`, and exited nonzero (`observed`).
Make `install` errors (F3) and `clean` (F6) follow this pattern.
The one fix it needs is the exit code (F5).

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F7 (aliases, vague names); `not-checked`: selector patterns and flag reuse, because per-command flags are unknown |
| Machine Schema | F4 |
| Stdin Contract | F4 (undeclared); `sync` with empty stdin observed non-blocking; other commands `not-checked` |
| Shell Safety | `not-checked`: no `--` support was shown, and there is no source to check subshell use; declare it in the schema |
| Agent-Safe Invocation | F1 (no machine profile), F9 (timeout), F10 (slow-path banner on `--help`); non-TTY prompt suppression on `sync` is OK (observed) |
| Output | F1 |
| Errors And Exit Codes | F3, F5; `sync` error shape OK (has `code`, `message`, `temporary`, `hint`) |
| Ambient State | F8 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7, F10 |
| Tests | `not-checked`: no source or test suite was supplied; at minimum, pin stdout purity in `--json`, the error payloads and exit codes, and non-TTY no-prompt behavior for `sync` and `clean` |

## Open questions / assumptions
- Does `clean` prompt, refuse, or delete immediately when there is no TTY and no `--yes`? If it prompts and blocks, it is P0.
- Does `Checking for updates...` make a network call, and does it run on every command, including `--help`?
- Is there a machine-readable schema or a `--help --json` that was not captured?
- Does `--json` exist for every command, and what does `install --json` emit on failure?
- What do the other exit codes mean (if any besides 0, 1, and 4)?

## Suggested remediation order
1. Release blockers (P1): clean stdout in `--json` (F1), remove or opt-in the update check (F2), structured `install` errors (F3).
2. Contract: `depman schema` and the fingerprint (F4), a declared exit-code map (F5), `--dry-run` and a `clean` guard (F6).
3. Ambient state, timeouts, and prose polish (F7–F10).
~~~~~~
