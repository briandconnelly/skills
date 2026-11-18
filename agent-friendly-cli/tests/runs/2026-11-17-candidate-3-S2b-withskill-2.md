# Scenario 2b (audit, fail-fast control) — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,702 (final-turn context plus output, read from the transcript)
- **Output words:** 1,150
- **Transcript sha256:** `cd2176812ba62891f93fc968147a81a6e8ecb4ffd83298c9780e787eae77aae3` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S2b-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 — P2: "it exited instead of hanging on closed stdin"; TTY hang only raised as an open question; top severity P1 is F1-F3 Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything), so findings lead with contract gaps and release-blocking issues.
Task: review of an existing CLI from user-supplied captures; no probes were run.
All `observed` findings are from the user's verbatim captures (stdout only, except the final stderr-only capture).

## Findings (by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- Type: `impl-bug` (`--json` promises a JSON payload)
- Evidence: `observed` (user capture, stdout only)
- Location: `depman ls --json 2>/dev/null` — lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the JSON array.
- Impact: stdout is not parseable JSON; agents must strip lines heuristically, and any wording change breaks them.
- Fix direction: in `--json` (and a single machine-profile flag such as `--machine`), stdout carries only the array; banner and timing go nowhere in machine mode, and to stderr at most in human mode. Add a test asserting `depman ls --json | jq .` succeeds with empty stderr.

### F2 — P1 — Read command performs an update check
- Type: `impl-bug` (hidden side effect on a read path)
- Evidence: `observed` ("Checking for updates..." on `ls`); the network call itself is `inferred` from the message.
- Location: `depman ls --json` stdout line 2.
- Impact: undeclared network call on a read verb; adds latency, can fail or hang offline, and leaks usage.
  No evidence confines it to the local machine, so it stays P1.
- Fix direction: make update checks opt-in (config or `--check-updates`), never in machine mode, never on stdout; declare any remaining network use in the schema.

### F3 — P1 — `install` failure has no symbolic code, wrong stream, generic exit
- Type: `impl-bug` / `schema-gap`
- Evidence: `observed` (`Error: something went wrong (see log)` appeared with stderr discarded, so it went to stdout; exit `1`).
- Location: `depman install nonexistent-pkg`.
- Impact: agents cannot tell not-found from network, auth, or internal failure; they cannot retry or repair.
  The error pollutes stdout, and "see log" points at an undeclared log file the agent cannot locate.
- Fix direction: emit the structured error object on stderr (as `sync` already does) with e.g. `{"code":"PACKAGE_NOT_FOUND","message":...,"temporary":false,"resource_id":"nonexistent-pkg"}`, exit `3` (not found), and empty stdout. Give the log path in a `path` field if a log exists, and declare a fallback `INTERNAL` code for unanticipated failures.

### F4 — P2 — No machine-readable schema, exit-code map, or error catalog
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (only prose `--help`; no `schema` command, `--help --json`, or fingerprint visible)
- Location: `depman --help`.
- Impact: agents cannot discover flags per command, output classes, read-only vs mutating status, stdin contract, or which codes/exits each command returns; `sync`'s exit `4` cannot be interpreted without guessing.
- Fix direction: add `depman schema [command]` and `depman schema --fingerprint` with `schema_version`, `fingerprint_scope`, per-command flags, output class (`ls` → `list`, `install`/`sync`/`clean` → `bulk-result` or `record`), mutating classification, latency class, stderr framing (`single-error-object`), and a per-command error catalog.

### F5 — P2 — `sync` exit 4 for `CONFIRMATION_REQUIRED` is undeclared and collides with the common "unauthenticated" meaning
- Type: `schema-gap`
- Evidence: `observed` (exit 4; stderr payload).
- Location: `depman sync --json < /dev/null`.
- Impact: shell-level callers branching on exit 4 as auth failure will misroute. The payload itself is good: symbolic `code`, `message`, `temporary:false`, `hint`, and it exited instead of hanging on closed stdin.
- Fix direction: declare the mapping in the schema; consider exit `2` (usage — missing `--yes`) or a declared domain code ≥10. Express the hint structurally too (e.g. `details.required_flag: "--yes"`).

### F6 — P2 — No machine profile; `--json` not shown in help
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (`--json` works on `ls` and `sync` but is not in `--help`; no `--machine`/non-interactive profile).
- Impact: agents cannot know which commands honor `--json` or how to guarantee no prompts, color, or banners.
- Fix direction: one declared global flag (`--machine`) implying `--json`, no prompts, no banners/progress, no update check; document `--json` per command.

### F7 — P2 — Mutating commands lack declared dry-run, idempotency, and confirmation contracts
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (`install`, `clean`, `sync` show no `--dry-run`; only `sync` mentions confirmation; `clean` deletes from the global cache with no stated confirmation).
- Impact: agents cannot preview `clean` (destructive, shared global state) or know whether retrying an interrupted `install`/`sync` is safe.
- Fix direction: add `--dry-run` (output with `dry_run: true`) to all three; declare retry safety, signal semantics, and lockfile/cache concurrency behavior.

### F8 — P2 — Ambient state undocumented
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (global cache, lockfile, log file, update-check endpoint, registry/credentials not described).
- Fix direction: document config/env/cache sources and precedence, add `config show --resolved`, and an `--isolated`/`--no-config` flag.

### F9 — P3 — Prose surfaces are not task-selective; aliases in canonical help
- Type: `design-issue`
- Evidence: `observed` (`--help`).
- Location: `ls  Show stuff`; `install (aliases: i, add)`; `--quiet  Less output`; tagline banner.
- Impact: "Show stuff" does not let an agent choose `ls` (installed? outdated? lockfile?); `--quiet` effect is undefined; aliases add extra names for one operation.
- Fix direction: rules-first summaries, e.g. `list  List installed packages (read-only; --json for array)`; define exactly what `--quiet` suppresses; declare aliases in schema only, and prefer full-word `list` with `ls` as a declared alias.

## Checklist Coverage

| Section | Status |
| --- | --- |
| Command Model | F9 (abbreviation `ls`, aliases); otherwise flat tree is OK |
| Machine Schema | F4 |
| Stdin Contract | Partially OK: `sync` with `/dev/null` stdin exits 4 rather than hanging (observed); undeclared per command → F4; TTY-stdin behavior not-checked |
| Shell Safety | not-checked: no `--` support or hint-construction evidence in captures |
| Agent-Safe Invocation | F6; non-interactive bootstrap and metadata-path latency not-checked |
| Output | F1, F3 (errors on stdout); stderr framing undeclared → F4 |
| Errors And Exit Codes | F3, F5; `sync` error payload shape is OK |
| Ambient State | F8 |
| Mutations And Long-Running Work | F7 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F9 |
| Tests | not-checked: no source or tests supplied; recommend tests pinning F1, F3, F5 behavior and machine-mode suppression |

## Open Questions / Assumptions
- Does `--help` itself trigger the update check or any network call? Not shown.
- Does `sync` prompt (hang) when stdin is a TTY but `--json` is set? Only closed stdin was captured.
- Is "see log" a real file, and where?
- Does `ls --json` stdout pollution also occur with `--quiet`?

## Remediation Plan
Release-blocking (P1): F1, F2, F3 — clean stdout in JSON mode, remove default update check, structured errors on stderr with proper exits.
Then add `depman schema` + machine profile (F4, F6), fix exit-code mapping (F5), and declare mutation/ambient contracts (F7, F8); polish help (F9).
~~~~~~
