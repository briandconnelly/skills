# Scenario 2b (audit, fail-fast control) — with-skill arm 1 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,330 (final-turn context plus output, read from the transcript)
- **Output words:** 1,169
- **Transcript sha256:** `a3b8572f326dea39d591d790868be5628ee6e5a506d7e8912fb3d21eac9deefc` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/S2b-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 — P2 ... does not hang on closed stdin, so the P0 hang risk is not present in this capture Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity (P1) = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | `json.loads(stdout)` fails; agents must regex out the array line |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — agent-friendliness audit

Audience: tool author (can change anything).
Task: audit of an existing CLI from user-supplied captures; I ran nothing.
Every `observed` label below means "user-supplied verbatim capture"; stdout and stderr were captured separately, so stream attribution is observed, not inferred.

## Findings (by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- type: `impl-bug` (`--json` promises JSON; stdout is not parseable JSON)
- evidence: `observed` — `depman ls --json 2>/dev/null` prints `✨ DepMan 3.2`, `Checking for updates...`, the array, then `Done in 0.42s ✓`, all on stdout.
- impact: `json.loads(stdout)` fails; agents must regex out the array line, which breaks as soon as wording or line layout changes.
- fix direction: in `--json` (and in any non-TTY stdout) write only the array to stdout; send the banner and timing summary to stderr only when stderr is a TTY, or drop them; never in machine mode (checklist § Output, § Agent-Safe Invocation).

### F2 — P1 — Update check on a read path, by default
- type: `design-issue`
- evidence: `observed` — `Checking for updates...` on `ls --json`; network effect `inferred` from the message (no evidence it is confined to the local machine, so no downgrade to P2).
- impact: undeclared network call on every read: adds latency, can fail or hang offline, leaks usage, and makes `ls` non-deterministic in timing and output.
- fix direction: make update checks opt-in (`--check-updates` or config), never in machine mode, never on stdout; declare any remaining network behavior in the schema (checklist § Side Effects And Telemetry).

### F3 — P1 — `install` failure has no symbolic code, goes to stdout, and points to an unnamed log
- type: `design-issue`
- evidence: `observed` — `depman install nonexistent-pkg 2>/dev/null` prints `Error: something went wrong (see log)` on stdout; exit `1`.
- impact: an agent cannot tell not-found from network failure from a bug; it cannot branch, retry correctly, or locate "the log"; the error pollutes stdout, which must be payload-only.
- fix direction: emit a structured error on stderr with `code` (e.g. `PACKAGE_NOT_FOUND`), `message`, `temporary: false`, plus `resource_id: "nonexistent-pkg"` and `path` to the log file; leave stdout empty; exit `3` (not found) and declare it (checklist § Errors And Exit Codes, § Output).
  Note that `sync` already emits this shape — reuse that error path for every command.

### F4 — P2 — No machine schema, machine profile, or fingerprint
- type: `schema-gap`
- evidence: `absence-of-evidence` — `--help` lists no `schema` command, no `--help --json`, no machine profile flag; `--json` is shown only in captures, not in help.
- impact: agents must infer commands, flags, output shapes, exit codes, and mutating vs read-only status from prose.
- fix direction: add `depman schema [command]` and `depman schema --fingerprint` declaring the command tree, aliases, flags, output class per command (`ls`: `list`), read-only vs mutating, per-command error catalog, exit-code map, stdin contract, and a canonical machine profile (e.g. `--machine` implying `--json`, no banner, no prompts, no update check) (checklist § Machine Schema).

### F5 — P2 — `sync` exit code `4` for `CONFIRMATION_REQUIRED` is undeclared and collides with the conventional "unauthenticated" meaning
- type: `schema-gap`
- evidence: `observed` — `sync --json < /dev/null` exits `4`; stderr carries `{"code":"CONFIRMATION_REQUIRED",...,"temporary":false}`.
- impact: shell-level callers branching on exit code will read this as an auth failure.
  The behavior itself is good: it fails fast with a structured error on stderr and does not hang on closed stdin, so the P0 hang risk is not present in this capture.
- fix direction: map `CONFIRMATION_REQUIRED` to `2` (usage/validation) or a declared domain code in `10`–`123`, and declare it in `sync`'s error catalog with `retryable: false`, suppressed by `--yes`; move `hint` repair data into a structured field (e.g. `details: {"required_flag": "--yes"}`) (checklist § Errors And Exit Codes).

### F6 — P2 — Mutating commands lack `--dry-run` and clear mutation classification
- type: `schema-gap`
- evidence: `absence-of-evidence` — `--help` shows no `--dry-run`; `clean` (deletes from the global cache) and `install` show no confirmation or preview mechanism; only `sync` mentions confirmation.
- impact: agents cannot preview what `clean` will delete or what `sync` will change before committing; `clean` may delete with no explicit trigger.
- fix direction: add `--dry-run` to `install`, `clean`, and `sync` with `dry_run: true` output listing planned effects; require `--yes` consistently for `clean`; declare retry/reconciliation and interrupt semantics for each, plus lockfile/cache concurrency safety (checklist § Mutations And Long-Running Work).

### F7 — P3 — Help prose is not task-selective
- type: `design-issue`
- evidence: `observed` — `ls  Show stuff`; `--quiet  Less output`; `--help` opens with a marketing banner.
- impact: an agent cannot tell what `ls` lists (installed deps? global cache? lockfile?) or what `--quiet` suppresses.
- fix direction: lead with constraints and specifics, e.g. `list  List installed dependencies of the current project (read-only)`; `--quiet  Suppress progress and summary lines on stderr`; drop the banner (checklist § Prose Surfaces).

### F8 — P3 — Command naming: abbreviated `ls`, migration-less aliases `i`/`add`
- type: `design-issue`
- evidence: `observed` in `--help`.
- impact: `ls` vs `list` and three names for `install` widen the space agents guess from; `add` often means "add to manifest", which may differ from install semantics.
- fix direction: canonical full words (`list`, `install`); keep aliases only for migration and declare them in the schema; use canonical names in examples (checklist § Command Model).

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8, F7 |
| Machine Schema | F4 |
| Stdin Contract | not-checked beyond `sync < /dev/null` (fails fast, OK); no declaration exists (F4) |
| Shell Safety | not-checked — no `--` support or hostile-argument captures |
| Agent-Safe Invocation | F1, F4 (no machine profile); `sync` non-TTY prompt suppression OK (observed) |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | not-checked — no captures of config, env, cache, or credential sources (a global cache exists per `clean`; no `--isolated` or resolved-config command visible in help) |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7 |
| Tests | not-checked — no source or tests supplied |

## Open questions / assumptions
- Is `--json` a global flag or per-command? It is absent from `--help`.
- Where does "the log" live, and does `install` write it on every run?
- Does the update check hit the network, and does it write a cache/timestamp file (a second hidden side effect)?
- Does `clean` prompt or delete immediately? Does `--quiet` affect stdout or stderr?
- Does `sync` behave the same when stdin is a TTY but stdout is piped?

## Suggested remediation order
1. Release blockers (P1): F1, F2, F3 — make stdout payload-only, kill default update checks, unify all errors on the structured stderr shape `sync` already uses.
2. Then F4 (schema + `--machine`), F5 (exit-code map), F6 (dry runs).
3. Polish: F7, F8.
~~~~~~
