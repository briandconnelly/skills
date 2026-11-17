# Scenario 2b (audit, fail-fast control) — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 62,971 (final-turn context plus output, read from the transcript)
- **Output words:** 1,269
- **Transcript sha256:** `4d13cd15ec87ae6687e821b3903c57f7956c6d0f986caf159b79592e41b8de38` (session-local copy; not committed)
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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S2b-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F5 — P2 — Exit `4` for `CONFIRMATION_REQUIRED`... (top is P1); `sync --json` with non-TTY stdin did not hang Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything).
Task: review of an existing CLI.
Evidence basis: verbatim user-supplied captures only; I did not run the tool.
Each capture discards stderr except the final `sync` capture, which shows stderr only, so stream attribution below is observed, not inferred.

## Findings (ordered by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- Type: impl-bug
- Evidence: observed (user capture, `depman ls --json 2>/dev/null`)
- Location: stdout lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the JSON array.
- Impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks as soon as wording or emoji change.
  Even an explicit `--json` request does not yield a parseable stdout.
- Fix direction: stdout carries only the payload in JSON mode (and in non-TTY mode); move banner/progress/timing to stderr, and suppress them entirely in machine mode.
  Add a snapshot test asserting `depman ls --json` stdout parses as JSON with nothing else.

### F2 — P1 — Update check on a read path (`ls`)
- Type: design-issue
- Evidence: observed (`Checking for updates...` printed during `ls --json`)
- Location: `ls --json` stdout.
- Impact: undeclared network call on a read verb; adds latency, fails or hangs offline/in sandboxes, leaks usage, and makes `ls` non-deterministic in cost.
  No evidence it is confined to the local machine, so it stays P1.
- Fix direction: make update checks opt-in, never on by default, always suppressed in machine mode, and never written to stdout.
  Declare any remaining network use and its latency class in the schema.

### F3 — P1 — `install` failure has no symbolic code; error is prose on stdout
- Type: impl-bug
- Evidence: observed (`depman install nonexistent-pkg 2>/dev/null` printed `Error: something went wrong (see log)` to stdout; exit `1`)
- Location: install error path.
- Impact: agents cannot distinguish not-found from network, auth, or usage failures; exit `1` is generic; the message is uninformative, and "see log" points at an undeclared file.
  The failure text also lands on stdout, where a caller expects success payload.
- Fix direction: emit a structured error on stderr (`{"code":"PACKAGE_NOT_FOUND","message":...,"temporary":false,"resource_id":"nonexistent-pkg"}`), keep stdout empty on failure, and map to a specific exit code (e.g. `3` not found).
  Declare the log location (or include the relevant detail in `details`) instead of "see log".

### F4 — P2 — No machine-readable schema, machine profile, or exit-code map
- Type: schema-gap
- Evidence: absence-of-evidence (`--help` lists no `schema` command, no `--help --json`, no `--machine`-style flag)
- Location: `depman --help`.
- Impact: agents must infer commands, flags, output classes, mutating vs read-only, and exit codes from prose.
  `--json` exists on at least `ls` and `sync` but is not listed in help at all.
- Fix direction: add `depman schema` (+ `--fingerprint`, `fingerprint_scope`, `schema_version`) declaring the command tree, aliases, flags, output class per command, read-only vs mutating, side effects, latency class, stdin contract, stderr framing (`single-error-object` or `ndjson-typed`), and a per-command error catalog with exit codes and `retryable`.
  Define one machine profile (e.g. `--machine` implying `--json`, no color/progress/prompts/update check).

### F5 — P2 — Exit `4` for `CONFIRMATION_REQUIRED` is undeclared and collides with the conventional "unauthenticated" meaning
- Type: schema-gap
- Evidence: observed (`sync --json < /dev/null` → `exit=4`) plus absence-of-evidence (no exit map declared).
- Location: `sync` capture.
- Impact: shell-level callers that branch on exit codes may treat this as an auth failure.
  The symbolic code is correct and authoritative, so this is a contract gap, not a parse failure.
- Fix direction: declare the exit map; either assign confirmation-required a declared domain code (`10`–`125`) or `2` (usage), and list it in `sync`'s error catalog with the suppressing flag `--yes`.

### F6 — P2 — Mutating commands have no declared dry-run, classification, or reconciliation path
- Type: schema-gap
- Evidence: absence-of-evidence (`--help` shows no `--dry-run`; `clean` removes packages from a global cache with no confirmation mentioned; `install` and `sync` mutate).
- Location: `depman --help`.
- Impact: agents cannot preview `clean`/`sync`/`install` effects, and cannot tell whether a timed-out `install` committed.
  `clean` touches shared global state, so concurrent invocations are a concern.
- Fix direction: add `--dry-run` (output with `dry_run: true`) to `install`, `sync`, `clean`; declare read-only vs mutating, idempotency/retry safety, interrupt semantics, and locking for the global cache and lockfile.

### F7 — P2 — Ambiguous command model and aliases
- Type: design-issue
- Evidence: observed (`--help`)
- Location: `ls  Show stuff`; `install (aliases: i, add)`.
- Impact: "Show stuff" does not let an agent pick `ls` vs anything else (installed? outdated? lockfile?); multiple aliases give several spellings for one operation.
- Fix direction: use a full verb (`list`) with a task-selective summary ("List installed packages with name and version"); keep aliases only for migration and declare them in the schema.

### F8 — P2 — Ambient state undocumented
- Type: schema-gap
- Evidence: absence-of-evidence
- Location: `--help`.
- Impact: global cache, lockfile location, config files, registry credentials, and the error log are all implied but undeclared; no `--isolated`/`--no-config`, no resolved-config inspection.
- Fix direction: document sources and precedence; add `config show --resolved` and an isolation flag; redact secrets.

### F9 — P3 — Prose surfaces are not rules-first
- Type: design-issue
- Evidence: observed (`--help`)
- Location: marketing banner `the friendly dependency manager!`; `--quiet  Less output`; `--yes  Assume yes`.
- Impact: help spends tokens on branding; `--quiet` does not say what it removes, so agents cannot rely on it for clean output; `--yes` does not say which commands it applies to.
- Fix direction: lead with constraints and defaults ("`--yes`: skip confirmation for `sync`/`clean`; required in non-TTY mode"); state exactly what `--quiet` suppresses, or replace it with the machine profile.

### Positive observation
- `sync --json` with non-TTY stdin did not hang: it exited nonzero with a single structured error on stderr containing `code`, `message`, `hint`, and `temporary:false`, and stdout was empty.
  That is the right shape; reuse it for every error (F3).
  Caveat: the `hint` is prose ("pass --yes"); also expose the repair as structured data (e.g. `details.suppressed_by: ["--yes"]`).

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F7 |
| Machine Schema | F4, F5 |
| Stdin Contract | Partially OK: `sync` with `< /dev/null` does not block (observed); otherwise not declared (F4) |
| Shell Safety | not-checked: no `--`/hostile-argument captures |
| Agent-Safe Invocation | F4 (no machine profile); non-TTY prompt suppression OK for `sync` (observed); TTY-vs-non-TTY banner behavior not-checked |
| Output | F1 |
| Errors And Exit Codes | F3, F5; `sync` error shape OK |
| Ambient State | F8 |
| Mutations And Long-Running Work | F6 |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7, F9 |
| Tests | not-checked: no source or tests supplied; F1, F3, F5 indicate missing stdout-purity, error-payload, and exit-map tests |

## Open questions / assumptions
- Does `--quiet` remove the banner/update check from `ls --json` stdout? Not captured; even if so, it should not be required.
- Where is "the log" from `install`, and is it written on every run (an implicit write)?
- Does `clean` prompt or act immediately? Help says nothing.
- Is the update check skipped when offline, and what is its timeout?
- Is the `install` error also on stderr in some form? Only stdout was captured.

## Suggested remediation order
1. Release blockers (P1): F1 stdout purity, F2 update check off by default, F3 structured errors on stderr.
2. Then F4/F5 schema + exit map, F6 dry-run and mutation declarations, F8 ambient state, F7/F9 help text.
~~~~~~
