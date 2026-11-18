# Scenario 2 (audit) — with-skill arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 3/4 conformance
- **Tokens:** 63,852 (final-turn context plus output, read from the transcript)
- **Output words:** 1,331
- **Transcript sha256:** `39520fd4473744ae7b62dab475dca28b252c092f493157466dcf847d135a66c9` (session-local copy; not committed)
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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-instrument/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S2-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | Evidence: inferred (from `--help`: ...); no non-TTY behavior is documented Parts: sync prompt flagged as blocking risk = pass; states what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | inferred (from `--help`: "Sync the lockfile (asks for confirmation first)") Parts: shows documented prompt = pass; distinguishes deduced non-TTY hang = pass |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | Evidence: observed (stdout-only capture) ... `depman ls --json \| jq` fails Parts: pollution flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | F4 — Errors are prose on stdout with no symbolic code and a generic exit |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | F3 — Read command performs an update check (hidden network side effect) |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | F6 — `clean` mutates the global cache with no dry run |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | multiple names for one operation...; "Show stuff" does not say what `ls` lists Parts: alias duplication flagged = pass; vague ls description flagged = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Stdin Contract: not-checked ... Tests: not-checked |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | Severity: P0 / Type: design-issue / Evidence / Location / Impact / Fix direction Parts: P0-P3 words = pass; template fields severity/type/evidence/location/impact/fix = pass |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | Evidence: observed / inferred / absence-of-evidence |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 Severity: P0; F2 Severity: P1 |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **FAIL** | Coverage is a bulleted list, not a table: '- Stdin Contract: not-checked — ...' |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything).
Task: review of an existing CLI from user-supplied captures only; no probes were run.
All captures discarded stderr, so every line shown is stdout.
`observed` below means "observed in the user-supplied verbatim capture".

Release gating: F1–F4 (P0/P1) block a release until fixed.

## Findings

### F1 — `sync` prompts for confirmation, so it can hang in automation
- Severity: P0
- Type: design-issue
- Evidence: inferred (from `--help`: "Sync the lockfile (asks for confirmation first)"); no non-TTY behavior is documented
- Location: `depman --help`, `sync` entry
- Impact: an agent that runs `depman sync` without `--yes` blocks forever on a prompt in CI or under a non-TTY harness. `--yes` is global ("Assume yes") with no stated scope, so the agent cannot tell whether it suppresses the prompt or only some prompts.
- Fix direction: make non-TTY stdin and machine mode never prompt. Without `--yes` in machine mode, fail fast with a structured error (e.g. `code: "CONFIRMATION_REQUIRED"`, `temporary: false`, exit 2) instead of waiting. Add `sync --dry-run` that reports the planned lockfile diff with `dry_run: true`.

### F2 — `ls --json` stdout mixes banner, progress, and summary with the payload
- Severity: P1 (fixed placement: mixed success stdout)
- Type: impl-bug
- Evidence: observed (stdout-only capture)
- Location: `depman ls --json` output, lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- Impact: `depman ls --json | jq` fails; agents must strip lines heuristically. The non-ASCII decorations make naive line filtering fragile too.
- Fix direction: in `--json` (and in any non-TTY stdout), stdout is exactly the JSON payload. Move banner, progress, and timing to stderr, and suppress them entirely in machine mode. Add a test that `depman ls --json | python -m json.tool` succeeds.

### F3 — Read command performs an update check (hidden network side effect)
- Severity: P1 (fixed placement: hidden side effect on a read path; no evidence it is local-only)
- Type: design-issue
- Evidence: observed (`Checking for updates...` printed during `ls`)
- Location: `depman ls --json` output, line 2
- Impact: a read makes an undeclared network call: adds latency, fails or stalls offline or in sandboxed agents, and leaks usage. It is also printed to stdout (see F2).
- Fix direction: no update checks by default; make them opt-in (e.g. `depman self check-update`) and always suppressed in machine mode. If kept, declare it in the schema and never write it to stdout.

### F4 — Errors are prose on stdout with no symbolic code and a generic exit
- Severity: P1 (fixed placement: no symbolic code to branch on)
- Type: impl-bug
- Evidence: observed (`Error: something went wrong (see log)` appeared with stderr discarded, so it was written to stdout; `echo $?` → `1`)
- Location: `depman install nonexistent-pkg`
- Impact: an agent cannot distinguish not-found from network, auth, or usage failure; it cannot decide whether to retry; the message gives no fix; "see log" points at an undisclosed path. Error text on stdout can also be mistaken for payload.
- Fix direction: write failures to stderr as one structured object, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"field":"package","resource_id":"nonexistent-pkg","hint":"check the package name"}`, with empty stdout. Map to a declared exit code (e.g. 3 for not found, 2 usage, 6/7/9 transient). Declare the stderr framing (`single-error-object` or `ndjson-typed`). Report the log path in a `path` field.

### F5 — No machine-readable contract: no schema, fingerprint, or version command, no machine profile
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence (`--help` lists no `schema`/`version` command and no `--machine`/`--format` flag; `--json` is used but not listed in help)
- Location: `depman --help`
- Impact: agents must scrape prose help to learn commands, flags, output shapes, and exit codes; `--json` is undiscoverable and its per-command availability is unknown.
- Fix direction: add `depman schema` (command tree, flags with types/defaults, aliases, read-only vs mutating, output class per command — e.g. `ls`: `list`, per-command error catalog, exit-code map, side effects, latency class) and `depman schema --fingerprint` with `fingerprint_scope`. Define one machine profile, e.g. `--machine` implying JSON output, no prompts, no color/progress/banner, no update check. Add `depman version`.

### F6 — `clean` mutates the global cache with no dry run or declared scope
- Severity: P2
- Type: design-issue
- Evidence: inferred (from `--help`: "Remove unused packages from the global cache"); no `--dry-run` listed
- Location: `depman --help`, `clean` entry
- Impact: an agent cannot preview what will be deleted; the global cache is shared state outside the project, so a cleanup can affect other projects or concurrent runs. Whether it prompts is undocumented (if it does, it is another P0 like F1).
- Fix direction: add `clean --dry-run` returning the list of packages and bytes to be removed with `dry_run: true`; declare it mutating, its non-interactive behavior, and its concurrency safety (locking) against simultaneous `install`.

### F7 — Help text is vague and not task-selective
- Severity: P2
- Type: design-issue
- Evidence: observed
- Location: `depman --help`
- Impact: "Show stuff" does not say what `ls` lists (installed deps? project or global? direct or transitive?). `--quiet` ("Less output") does not say what is removed or whether it affects stdout payload. `sync` does not say direction (lockfile → install, or manifest → lockfile). The help's own stdout opens with a marketing banner.
- Fix direction: rules-then-context summaries, e.g. `ls  List installed packages for the current project (read-only; --json for machine output)`. Define `--quiet` precisely or replace with the machine profile. Drop the banner from help output.

### F8 — Ambient state is undocumented
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence
- Location: `depman --help`; "see log" in error output; "global cache" in `clean`
- Impact: the global cache location, log location, registry/config sources, credentials, and env vars are unknown, so agents cannot reproduce or isolate runs.
- Fix direction: document config files, env vars, cache and log paths, and precedence; add a resolved-config inspection command (e.g. `depman config show --resolved`) and an `--isolated`/`--no-config` flag.

### F9 — Command naming: aliases and abbreviations
- Severity: P3
- Type: design-issue
- Evidence: observed
- Location: `depman --help` (`install` aliases `i`, `add`; `ls`)
- Impact: multiple names for one operation multiply what agents may emit and what docs must cover; `add` vs `install` may read as different semantics.
- Fix direction: keep `install` canonical; declare aliases in the schema as deprecated or migration-only; consider `list` as the canonical name for `ls` with `ls` as a declared alias.

## Checklist Coverage

- Command Model: F7, F9.
- Machine Schema: F5.
- Stdin Contract: not-checked — no stdin behavior shown or documented; absence of any stdin declaration is part of F5.
- Shell Safety: not-checked — no `--` support or argument-handling evidence in captures.
- Agent-Safe Invocation: F1, F5 (no machine profile); network timeout flag for `install`/`sync` absent — folded into F5.
- Output: F2, F4 (error on stdout).
- Errors And Exit Codes: F4.
- Ambient State: F8.
- Mutations And Long-Running Work: F1, F6; no dry run, idempotency, or interrupt semantics for `install`/`sync` declared.
- Side Effects And Telemetry: F3.
- Prose Surfaces: F7.
- Tests: not-checked — no source or test suite supplied; recommend tests for stdout purity under `--json`, non-TTY no-prompt behavior, error payloads and exit codes.

## Open Questions / Assumptions

- Does `depman` already detect non-TTY and skip the `sync` prompt? F1 assumes not, since nothing documents it.
- Does `--json` apply to every command, including errors? Only `ls --json` was shown.
- Is the update check cached or rate-limited? Treated as a network call per invocation.
- What is written to stderr? It was discarded in every capture; stderr content is unknown.

## Suggested Remediation Order

1. Machine mode: non-TTY never prompts; stdout payload-only; no update check (F1–F3).
2. Structured stderr errors with symbolic codes and a declared exit-code map (F4).
3. `depman schema` + fingerprint + `--machine` profile (F5), then dry runs (F6), help text (F7), ambient-state docs (F8), aliases (F9).
~~~~~~
