# Scenario 2 (audit) — with-skill arm 1 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 3/4 conformance
- **Tokens:** 64,947 (final-turn context plus output, read from the transcript)
- **Output words:** 1,441
- **Transcript sha256:** `19ac1cc0e99207509bafbda37eb7db9077743ec466370f52a7cd98776907cde6` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S2-withskill-1.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | evidence: `inferred` — help says `sync` "asks for confirmation first"; ... A capture of `depman sync < /dev/null` would settle F1. Parts: sync prompt flagged as automation-blocking risk = pass; says what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | `inferred` — help says `sync` "asks for confirmation first"; nothing says the prompt is skipped when stdin is not a TTY |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: `observed` — `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` all appear on stdout Parts: flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Errors have no symbolic code ... No declared exit-code map; not-found returns generic `1` |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | a read command makes an undeclared network call ... leaks usage |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `install`, `clean`, and `sync` show no `--dry-run`. `clean` touches a global cache |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | `ls Show stuff` ... `install` lists aliases `i, add` Parts: alias duplication = pass; vague ls description = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Tests: `not-checked` — no source or tests supplied. |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | ### F1 — ... (P0) - type ... - evidence ... - location ... - impact ... - fix direction Parts: P0-P3 words = pass; template fields = pass |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | `inferred`, `observed`, `absence-of-evidence` used literally |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 ... (P0); F2 ... (P1) Parts: hang P0 = pass; pollution P1+ = pass |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **FAIL** | Coverage is a bullet list ("- Stdin Contract: `not-checked` — ..."), not a coverage table |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool author (who can change anything), so this report leads with contract gaps and release-blocking findings.
Evidence base: three captures you supplied, each with stderr discarded (`2>/dev/null`), so every line shown is stdout.
I did not run the tool; `observed` below means "observed in a verbatim capture you supplied".

Release decision: **blocked** — one P0 and four P1 findings.

## Findings

### F1 — `sync` prompts for confirmation; no declared non-interactive behavior (P0)

- type: `schema-gap`
- evidence: `inferred` — help says `sync` "asks for confirmation first"; nothing says the prompt is skipped when stdin is not a TTY or in a machine mode.
- location: `depman --help`, `sync` line.
- impact: an agent or CI job running `depman sync` can block forever waiting for terminal input. A global `--yes` exists, but nothing ties it to `sync` or says what happens without it in non-TTY mode.
- fix direction: never prompt when stdin is not a TTY; instead fail fast with a structured error (e.g., `code: "CONFIRMATION_REQUIRED"`, exit `2`, `hint` naming `--yes`). Declare `sync` as mutating and `--yes` as its explicit trigger in the schema. Add a test that runs `sync` with stdin closed and asserts it exits rather than hangs.

### F2 — `--json` stdout mixes banner, progress, and summary with the payload (P1)

- type: `impl-bug` (the `--json` flag promises JSON; stdout isn't valid JSON)
- evidence: `observed` — `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` all appear on stdout around the array.
- location: `depman ls --json 2>/dev/null` output.
- impact: `depman ls --json | jq` fails. Agents have to strip lines heuristically, which breaks the moment the banner or timing text changes. The emoji and spinner glyphs also waste tokens.
- fix direction: stdout carries only the payload. Send banner, progress, and timing to stderr, and suppress them entirely in machine mode and when stderr is not a TTY. Add a test that pipes `ls --json` stdout through a strict JSON parser.

### F3 — Update check on a read path (P1)

- type: `design-issue`
- evidence: `inferred` — `Checking for updates...` printed during `ls`. That is almost certainly a network call, and nothing shows it stays on the local machine.
- location: `depman ls --json` output, line 2.
- impact: a read command makes an undeclared network call. That adds latency, can fail or hang offline or in sandboxes, and leaks usage.
- fix direction: make update checks opt-in, off by default, and always off in machine mode. Never write them to stdout. If you keep one, declare it as a side effect in the schema.

### F4 — Errors have no symbolic code, go to stdout, and point at an unnamed log (P1)

- type: `design-issue`
- evidence: `observed` — `Error: something went wrong (see log)` appears with stderr discarded, so it was written to stdout. Exit was `1`.
- location: `depman install nonexistent-pkg` capture.
- impact: agents can't tell not-found from network, auth, or bug failures, so they can't decide whether to retry, fix the name, or escalate. A consumer reading stdout as payload ingests the error text. "see log" names no path.
- fix direction: write failures to stderr as one structured object with `code`, `message`, and `temporary` (e.g., `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"field":"package","resource_id":"nonexistent-pkg"}`). Keep stdout empty on failure. Expose the log location as a `path` field. Declare one fallback code (e.g., `INTERNAL`, exit `1`) for uncaught failures.

### F5 — No declared exit-code map; not-found returns generic `1` (P1)

- type: `schema-gap`
- evidence: `observed` (exit `1` for a nonexistent package) plus `absence-of-evidence` (no exit codes documented anywhere).
- location: `echo $?` after `install nonexistent-pkg`; `--help`.
- impact: shell-level callers can't branch on outcome. Not-found looks the same as every other failure.
- fix direction: declare an exit-code map in the schema (e.g., `2` usage, `3` not found, `4` unauthenticated, `6` rate limited, `7` timeout, `9` transient) and map each symbolic code to one. Add a test that asserts declared exits match runtime exits.

### F6 — No machine schema or machine profile (P2)

- type: `schema-gap`
- evidence: `absence-of-evidence` — help lists no `schema` command, no fingerprint, and no `--json`/`--format` flag. `--json` works on `ls` but is undocumented.
- location: `depman --help`.
- impact: agents have to discover flags by trial and error, can't tell which commands support JSON, and can't cache a contract.
- fix direction: add `depman schema` (plus `schema <command>` and `schema --fingerprint`, with `schema_version` and `fingerprint_scope`). The schema should declare each command's flags, output class (`ls` → `list`), read-only vs mutating, side effects, latency class, and per-command error catalog. Define one machine-profile flag (e.g., `--machine`) that implies JSON output, no prompts, no color or progress, and no update check.

### F7 — Ambiguous command summaries and flags (P2)

- type: `design-issue`
- evidence: `observed` — `ls  Show stuff`, `--quiet  Less output`.
- location: `depman --help`.
- impact: "Show stuff" doesn't say what is listed: installed project deps, the global cache, or outdated packages. An agent can't choose `ls` over other commands from the summary, and can't predict what `--quiet` removes.
- fix direction: write task-selective, rules-first summaries, e.g. `ls  List dependencies installed in the current project (read-only). Output: list.` Define exactly what `--quiet` suppresses, or replace it with the machine profile.

### F8 — Mutating commands lack `--dry-run` and declared side effects (P2)

- type: `schema-gap`
- evidence: `absence-of-evidence` — `install`, `clean`, and `sync` show no `--dry-run`. `clean` touches a global cache that is shared across projects.
- location: `depman --help`.
- impact: agents can't preview what `clean` will delete or what `sync` will rewrite before committing to it. The retry safety of `install` after a timeout or interrupt is undeclared.
- fix direction: add `--dry-run` (output includes `dry_run: true` plus the planned effects) to `install`, `clean`, and `sync`. Declare idempotency and retry safety, signal semantics, and locking for lockfile and cache writes under concurrent runs.

### F9 — Ambient state is undocumented (P2)

- type: `schema-gap`
- evidence: `absence-of-evidence` — the tool clearly uses a global cache, a project lockfile (presumably found from the working directory), a log file, and probably registry config and credentials. None of these are documented.
- location: `depman --help`.
- impact: results depend on hidden state that agents can neither see nor control.
- fix direction: document config files, env vars, the cache path, cwd-based project selection (and a `--project <path>` override), and precedence. Add `config show --resolved` and an `--isolated`/`--no-config` flag. Accept registry tokens only through env vars or files, never as argv.

### F10 — Aliases advertised in primary help (P3)

- type: `design-issue`
- evidence: `observed` — `install` lists aliases `i, add`.
- location: `depman --help`.
- impact: agents may use the aliases inconsistently. `add` usually means something different from `install` in other package managers, which invites confusion.
- fix direction: keep aliases for migration only, declare them in the schema, and leave them out of canonical help and examples. Also consider `noun verb` naming (`depman deps list`) if you're redesigning anyway.

## Checklist Coverage

- Command Model: F7, F10.
- Machine Schema: F6, F5.
- Stdin Contract: `not-checked` — no command shows stdin use. Declare "stdin not read" per command in the schema (folds into F6).
- Shell Safety: `not-checked` — `--` support and hint content aren't visible. Declare `--` support in the schema.
- Agent-Safe Invocation: F1, F2, F6 (no machine profile; no non-TTY suppression).
- Output: F2, F4 (error on stdout), F6 (output class undeclared).
- Errors And Exit Codes: F4, F5.
- Ambient State: F9.
- Mutations And Long-Running Work: F1, F8.
- Side Effects And Telemetry: F3.
- Prose Surfaces: F7.
- Tests: `not-checked` — no source or tests supplied. At minimum, add the regression tests named in F1, F2, and F5.

## Open Questions / Assumptions

- I assumed `Checking for updates...` makes a network call (F3). If it only reads a local timestamp, F3 drops to P2, though it still pollutes stdout (F2).
- I didn't see stderr. The error may also go to stderr, but it definitely reaches stdout.
- Does `--yes` already skip the `sync` prompt, and does `sync` detect a non-TTY stdin? A capture of `depman sync < /dev/null` would settle F1.
- Is `--json` supported on commands other than `ls`?

## Suggested Remediation Order

1. F1: no prompts without a TTY; fail fast with a structured error.
2. F2 and F3: stdout payload-only; update check off by default.
3. F4 and F5: structured stderr errors with symbolic codes and a declared exit-code map.
4. F6: a `schema` command and a `--machine` profile, then F7–F10.
~~~~~~
