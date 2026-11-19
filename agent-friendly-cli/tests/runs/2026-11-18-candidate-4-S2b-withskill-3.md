# Scenario S2b — with-skill arm 3 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1380
- **Scoring:** blinded packet, output id `o73`; the scorer received the assertion block verbatim and no arm labels

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
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S2b-withskill-3.md, then reply with only the word done.

## Scorer's verdicts for this output

## A1: No finding claims `sync` hangs/blocks in automation, and no `sync`-prompt finding carries top severity
- o73: PASS
  - Part 1: PASS — "with stdin closed it did not hang; it failed fast" (the "hang offline" in F2 is about the update check, not `sync`).
  - Part 2: PASS — F4 "P2"; top is P1.
## A2: Stdout pollution on `ls --json` is still flagged
- o73: PASS — F1 "`ls --json` stdout mixes banner, progress, and summary with the payload".

## Verbatim final output

~~~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author, who can change anything.
Evidence: all `observed` findings come from user-supplied verbatim captures; I did not run the tool.
Stream attribution follows the stated capture setup: every line shown is stdout, except the last capture, which is stderr only.

## Findings (by severity)

### F1 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- Type: `impl-bug` (`--json` promises a JSON payload)
- Evidence: `observed` (user capture, stderr discarded)
- Location: `depman ls --json 2>/dev/null` — stdout contains `✨ DepMan 3.2`, `Checking for updates...`, the JSON array, and `Done in 0.42s ✓`.
- Impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks the moment wording changes.
- Fix direction: in JSON/machine mode, stdout is the array only. Move banner, progress, and timing to stderr, and suppress them entirely in machine mode and when stdout/stderr are not TTYs. Add a single machine-profile flag (e.g. `--machine`) that implies `--json`, no color, no prompts, no banners.

### F2 — P1 — Undeclared update check on a read path
- Type: `design-issue`
- Evidence: `observed` (`Checking for updates...` on `ls`)
- Location: `depman ls --json` stdout
- Impact: a read command makes an undeclared network call; adds latency, can fail or hang offline, leaks usage, and its output pollutes stdout (F1). No evidence it is local-only, so it stays P1.
- Fix direction: remove update checks by default; make them opt-in (`depman self check-update`), never run in machine mode, never write to stdout.

### F3 — P1 — `install` failure has no symbolic code, goes to stdout, and points at an unnamed log
- Type: `impl-bug` (failure on stdout) + `design-issue` (no code)
- Evidence: `observed` (`Error: something went wrong (see log)` survives `2>/dev/null`, exit `1`)
- Location: `depman install nonexistent-pkg`
- Impact: agents cannot distinguish not-found from network, auth, or bug; they must parse English that carries no information; stdout is not empty on failure, so a caller reading stdout gets an error as if it were output; "see log" names no path.
- Fix direction: emit a structured error on stderr, stdout empty, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","hint":"check the package name"}` with exit `3`. Include a `path` field if a log file exists. Declare a fallback `INTERNAL` (exit 1) for unanticipated failures.

### F4 — P2 — Exit code 4 for `CONFIRMATION_REQUIRED` collides with the conventional "unauthenticated" meaning and is undeclared
- Type: `schema-gap`
- Evidence: `observed` (exit `4`); `absence-of-evidence` for any exit-code map
- Location: `depman sync --json < /dev/null`
- Impact: shell-level branching on exit codes misreads this as an auth failure; nothing declares what 4 means.
- Fix direction: publish an exit-code map. Map confirmation-required to `2` (usage: a required flag was missing) or a declared domain code in `10`–`123`, and keep `CONFIRMATION_REQUIRED` as the authoritative symbolic key.

Note on what `sync` does right: with stdin closed it did not hang; it failed fast with an empty stdout and a well-formed structured error (`code`, `message`, `hint`, `temporary:false`) as the only stderr content. Keep this — it is the pattern F3 should follow. Not observed: behavior when stdin is a TTY-less pipe that stays open, and whether `--json` alone (without closed stdin) suppresses the prompt; pin both with tests.

### F5 — P2 — No machine schema, exit-code map, or error catalog
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (`--help` lists none; no `schema` command shown)
- Impact: agents cannot learn flags, output shapes, read-only vs mutating classification, stdin contract, or which codes each command returns without trial and error.
- Fix direction: add `depman schema [command]` and `depman schema --fingerprint` with `schema_version`, `fingerprint_scope`, per-command output class (`ls`: `list`), JSON Schema shapes, error catalog (`code` → exit, `retryable`, `reconcile_first`), side effects, latency class, stdin contract, ambient-state sources, and the machine profile.

### F6 — P2 — `--json` is undocumented; help omits most of the contract
- Type: `schema-gap`
- Evidence: `observed` (`--help` lists only `--quiet`, `--yes`; `--json` works on `ls` and `sync`)
- Impact: agents cannot discover the JSON mode; they learn it only by guessing. `--quiet` ("Less output") does not say what it removes or whether it is safe for parsing.
- Fix direction: declare `--json` (or `--format json`) as a global flag in help and schema; define `--quiet` precisely or fold it into the machine profile.

### F7 — P2 — Command summaries are not task-selective; `ls`/`clean`/`sync` semantics unclear
- Type: `design-issue`
- Evidence: `observed` (`--help`)
- Impact: `ls — Show stuff` does not tell an agent whether it lists installed, declared, or cached packages; `sync — Sync the lockfile` does not say direction (manifest → lockfile? lockfile → installed?) or that it mutates; `clean` does not say it is destructive or irreversible, and shows no confirmation or `--dry-run`.
- Fix direction: rewrite summaries rules-first, e.g. `list  List packages installed in the current project (read-only)`; `sync  Rewrite the lockfile from the manifest (mutating; requires --yes in non-interactive use)`; `clean  Delete unreferenced packages from the global cache (destructive; supports --dry-run)`. Prefer full words (`list` over `ls`) with `ls` as a declared alias.

### F8 — P2 — Aliases not declared as migration-only; banner in help
- Type: `design-issue`
- Evidence: `observed` (`install (aliases: i, add)`; `DepMan 3.2 — the friendly dependency manager!`)
- Impact: three spellings for one operation inflate the selection space; `add` reads as a distinct operation (add to manifest vs install). Banner costs tokens on every discovery call.
- Fix direction: keep one canonical verb; declare aliases in schema as aliases, use only the canonical form in examples; drop the tagline from `--help`.

### F9 — P2 — No dry-run, idempotency, or retry declarations for mutating commands
- Type: `schema-gap`
- Evidence: `absence-of-evidence` (`install`, `clean`, `sync` show no `--dry-run`; no retry/interrupt semantics)
- Impact: agents cannot preview `clean`/`sync`, and cannot tell whether a timed-out `install` is safe to retry or whether an interrupted `sync` leaves a partial lockfile.
- Fix direction: add `--dry-run` (output with `dry_run: true`) to `install`, `clean`, `sync`; declare atomic lockfile writes and concurrency locking; declare per-command `retryable`/`reconcile_first`.

### F10 — P3 — No ambient-state documentation or isolation flag
- Type: `schema-gap`
- Evidence: `absence-of-evidence`; `inferred` that ambient state exists (global cache per `clean`, current project directory selects the lockfile, likely registry config/credentials)
- Impact: agents cannot see which directory, registry, or cache a command acts on.
- Fix direction: document config/env/cache sources and precedence; add `depman config show --resolved` (secrets redacted), a `--project <path>` override for cwd selection, and `--isolated`.

## Checklist Coverage

| Section | Status |
|---|---|
| Command Model | F7, F8 |
| Machine Schema | F5, F6 |
| Stdin Contract | Partly OK: `sync` with closed stdin fails fast (observed). Undeclared otherwise → F5 |
| Shell Safety | not-checked: no `--` support shown; cannot probe |
| Agent-Safe Invocation | F1 (no machine profile, banners not suppressed); non-TTY prompt suppression on `sync` OK (observed) |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F4; `sync` error object shape OK (observed) |
| Ambient State | F10 |
| Mutations And Long-Running Work | F9; `sync` requires `--yes` OK |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7, F6 |
| Tests | not-checked: no source or tests available; see recommended tests below |

## Open Questions / Assumptions

- Assumed the capture setup is accurate: the `install` error line is on stdout because stderr was discarded.
- Unknown whether the update check also runs on `--help`, `install`, or `sync`, and whether it respects any opt-out env var.
- Unknown whether `ls` without `--json` or `--quiet` changes the banner behavior.
- Unknown where "the log" lives.

## Remediation Plan

1. Release-blocking (P1): F1 clean JSON stdout + machine profile; F2 remove update check from reads; F3 structured errors on stderr with symbolic codes.
2. Next: F4 exit-code map, F5 schema + fingerprint, F6/F7/F8 help rewrite.
3. Then: F9 dry-run and mutation semantics, F10 ambient-state inspection.
4. Tests: snapshot `ls --json` stdout as pure JSON under non-TTY; assert `install` of a missing package yields empty stdout, `PACKAGE_NOT_FOUND`, exit 3; assert `sync` without `--yes` never blocks with stdin closed or open-but-non-TTY; assert no network access on `ls` (e.g. with networking disabled).
~~~~~~~~
