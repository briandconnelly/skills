# Scenario 2b (audit, fail-fast control) — with-skill arm 3 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,498 (final-turn context plus output, read from the transcript)
- **Output words:** 1,100
- **Transcript sha256:** `6d81e93ddb57f6fc56417eb492d070cc63b8d3edbafcb747179988dad51e3c49` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/S2b-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 — P2 — `sync` exits `4` ... this path did not hang with closed stdin Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity (P1) = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything).
Evidence basis: verbatim captures supplied by the user; nothing was run by me.
Stream attribution comes from the user's redirections: every line shown is stdout except the final capture, which is stderr only.

## Findings (by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- type: `impl-bug` (`--json` promises JSON; stdout is not parseable JSON)
- evidence: `observed` (user capture, stderr discarded)
- location: `depman ls --json` output — `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the array on stdout
- impact: `json.loads(stdout)` fails; agents must strip lines heuristically, and any wording change breaks them.
- fix direction: in `--json` (and any machine/non-TTY mode) stdout carries only the array; move banner/progress/timing to stderr, and suppress them entirely in machine mode. Add a single `--machine` profile flag that implies `--json`, no color, no prompts, no banners.

### F2 — P1 — Update check on a read path
- type: `design-issue`
- evidence: `observed` that `ls` announces `Checking for updates...`; the network call itself is `inferred` from that text
- location: `depman ls --json` stdout
- impact: undeclared network call on a read verb adds latency, can fail or hang offline/sandboxed, and leaks usage. No evidence it is confined to the local machine, so no downgrade.
- fix direction: make update checks opt-in (e.g. `depman self check-update`), never run them on `ls`, suppress in machine mode, and never print to stdout.

### F3 — P1 — `install` failure has no symbolic code, goes to stdout, and points at an unnamed log
- type: `schema-gap`
- evidence: `observed` (with stderr discarded, `Error: something went wrong (see log)` still appeared, so it is on stdout; exit `1`)
- location: `depman install nonexistent-pkg`
- impact: agents cannot distinguish not-found from network, auth, or validation failure; exit `1` is generic; the error pollutes stdout; "see log" names no path.
- fix direction: on failure, empty stdout and a structured error on stderr, matching the shape `sync` already uses: e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found","temporary":false,"resource_id":"nonexistent-pkg","path":"<log path>"}` with exit `3` (not found). Declare a fallback `INTERNAL` code (exit `1`) for uncaught failures.

### F4 — P2 — No machine-readable schema, exit-code map, or error catalog
- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help` lists no `schema` command, no `--json`, no exit codes)
- location: `depman --help`
- impact: agents cannot discover that `--json` exists, which commands mutate, what each command outputs, or what exits mean.
- fix direction: add `depman schema` (+ `schema <command>` and `schema --fingerprint` with `fingerprint_scope`) declaring commands, aliases, flags, read-only vs mutating, output class (`ls`: `list`), stdin contract, side effects, latency class, exit codes, and per-command error catalog.

### F5 — P2 — `sync` exits `4` for `CONFIRMATION_REQUIRED`, undeclared
- type: `schema-gap`
- evidence: `observed` (exit `4`, structured error on stderr)
- location: `depman sync --json < /dev/null`
- impact: under the common convention `4` means unauthenticated; a shell-level caller branching on exit codes will misroute. The symbolic code is fine, but nothing declares the mapping.
- fix direction: map `CONFIRMATION_REQUIRED` to `2` (usage/validation) or a declared domain code (`10`+), and publish it in the catalog. Positive: this path did not hang with closed stdin, kept stdout empty, and emitted `code`/`message`/`hint`/`temporary` — use it as the model for every other error. Make `hint` structured too (e.g. `details.required_flag: "--yes"`).

### F6 — P2 — Mutating commands lack `--dry-run`, and `clean` has no declared confirmation/safety contract
- type: `schema-gap`
- evidence: `absence-of-evidence` (`--help` lists no `--dry-run`; `clean` mentions no confirmation)
- location: `depman --help` (`install`, `clean`, `sync`)
- impact: agents cannot preview `sync`/`clean`/`install` effects; `clean` deletes from the global cache with no visible guard; retry safety after interrupt is undeclared.
- fix direction: add `--dry-run` (output includes `dry_run: true`) to all mutating commands; declare whether `clean` requires `--yes`; declare idempotency/retry safety and interrupt behavior per command, plus lockfile/cache write atomicity under concurrent runs.

### F7 — P2 — Ambient state undocumented
- type: `schema-gap`
- evidence: `absence-of-evidence`
- location: `depman --help`
- impact: agents cannot tell which config, registry credentials, cwd project, or global cache drive behavior, nor disable them.
- fix direction: document config/env/credential sources and precedence; add `config show --resolved` (secrets redacted) and `--isolated`/`--no-config`; declare cwd project selection and an override flag.

### F8 — P3 — Prose surfaces are vague and not task-selective
- type: `design-issue`
- evidence: `observed` (`--help` text)
- location: `depman --help`
- impact: "Show stuff" does not say what `ls` lists (installed? declared? scope?); `--quiet` "Less output" is undefined; banner line precedes the contract; aliases `i`/`add` are not migration aliases and fragment canonical usage; `ls` abbreviates where `list` is clearer.
- fix direction: rules-first summaries, e.g. `list  List installed packages in the current project (read-only; JSON: array of {name, version})`; define exactly what `--quiet` suppresses; rename `ls` to `list` (keep `ls` as declared deprecated alias); declare or drop `i`/`add`; drop the banner from help.

## Checklist Coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F4 |
| Stdin Contract | not-checked beyond `sync` with `/dev/null` (did not block); no stdin contract declared — part of F4 |
| Shell Safety | not-checked: no `--` support or hint-construction evidence; `sync` hint `pass --yes` is a flag, not a shell string (OK) |
| Agent-Safe Invocation | F1 (no machine profile), F2; `sync` non-TTY prompt correctly refused (OK); TTY-stdin behavior with `--json` not-checked; no `--timeout-ms` on networked commands — `absence-of-evidence`, folded into F4 |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F5 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F8 |
| Tests | not-checked: no source or tests supplied |

## Open Questions / Assumptions
- Does `sync` prompt when stdin *is* a TTY even with `--json`? Machine mode must never prompt regardless of terminal status.
- Where is "the log" from F3, and is it written on every run (an implicit write)?
- Does the update check run on every command, including `--help`?
- Does `--quiet` remove the banner/progress from F1? Even if so, `--json` alone must be clean.

## Suggested Remediation Order
1. Release blockers (P1): F1, F2, F3 — clean `--json` stdout, remove default update check, structured errors everywhere modeled on `sync`'s.
2. F4 schema + exit-code map (absorbs F5), then F6, F7.
3. F8 prose cleanup; add tests pinning stdout purity, error payloads/exit codes, and non-TTY no-prompt behavior.
~~~~~~
