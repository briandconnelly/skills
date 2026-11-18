# Scenario 2 (audit) — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 3/4 conformance
- **Tokens:** 64,035 (final-turn context plus output, read from the transcript)
- **Output words:** 1,189
- **Transcript sha256:** `99c7cf73caeb84aca9b80151f8e44abaf2e9f22674067cb09d745e08dc0c1570` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S2-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | held at P1 only because the hang itself is not observed Parts: sync prompt flagged as automation-blocking risk = pass; says what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | evidence: inferred (help says "asks for confirmation first"; no statement of non-TTY behavior) |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: observed (`depman ls --json 2>/dev/null` prints `✨ DepMan 3.2` ...) ... `json.loads(stdout)` fails Parts: flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Errors are prose on stdout with no symbolic code |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Undeclared update check (network side effect) on a read path ... phones home |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` is a destructive mutation with no declared confirmation, dry run |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | aliases `i`/`add` multiply invocation paths; `ls` "Show stuff" gives no basis to choose it Parts: alias duplication = pass; vague ls description = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | \| Shell Safety \| not-checked — `--` support and argument handling not visible \| |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | ### F1 — P1 (provisional P0) ... - type ... - evidence ... - location ... - impact ... - fix direction Parts: P0-P3 words = pass; template fields = pass |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | inferred / observed / absence-of-evidence used literally |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **FAIL** | Hang finding is "P1 (provisional P0)", not P0 Parts: hang P0 = fail; pollution P1+ = pass |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **PASS** | \| Stdin Contract \| not-checked — no stdin behavior shown or documented ... |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything). Task: audit of an existing CLI from supplied captures only; no probes run.
All `observed` labels below mean "user-supplied verbatim capture"; every capture discarded stderr, so all shown text is stdout.

## Findings (by severity)

### F1 — P1 (provisional P0) — `sync` prompts for confirmation; no declared non-interactive behavior
- type: schema-gap
- evidence: inferred (help says "asks for confirmation first"; no statement of non-TTY behavior)
- location: `depman --help`, `sync` line
- impact: if `sync` waits on terminal input when stdin is not a TTY, an agent or CI job hangs. That would be P0 (blocking in non-TTY mode); held at P1 only because the hang itself is not observed. `--yes` exists but is not declared per-command and there is no machine profile that implies it.
- fix direction: never prompt when stdin is not a TTY or in machine mode; instead fail fast with a structured `CONFIRMATION_REQUIRED` error (exit 2) whose hint names `--yes`. Make `--machine` imply non-interactive. Add a non-TTY test.

### F2 — P1 — Banners, update check, and summary mixed into `--json` stdout
- type: impl-bug (`--json` promises JSON; stdout is not parseable JSON)
- evidence: observed (`depman ls --json 2>/dev/null` prints `✨ DepMan 3.2`, `Checking for updates...`, payload, `Done in 0.42s ✓`)
- location: `ls --json` output
- impact: `json.loads(stdout)` fails; agents must scrape the middle line. Also costs tokens and contains non-ASCII glyphs.
- fix direction: stdout carries only the payload in JSON mode (and by default for non-TTY stdout). Move banner/progress/timing to stderr, suppressed in non-TTY and machine mode.

### F3 — P1 — Undeclared update check (network side effect) on a read path
- type: design-issue
- evidence: observed ("Checking for updates..." on `ls`)
- location: `ls --json` output
- impact: a read command phones home: adds latency, fails or stalls offline/sandboxed, leaks usage. Fixed P1 placement; no evidence it is local-only.
- fix direction: remove update checks by default; make them opt-in, never in machine mode, never on stdout.

### F4 — P1 — Errors are prose on stdout with no symbolic code
- type: design-issue
- evidence: observed (`install nonexistent-pkg` prints `Error: something went wrong (see log)` on stdout, exit `1`)
- location: `install` failure capture
- impact: agents cannot branch (not-found vs network vs auth), cannot decide retry, and the error lands on stdout where success payloads go. "see log" points to an undisclosed location.
- fix direction: write a structured error to stderr: `{"code":"PACKAGE_NOT_FOUND","message":"...","temporary":false,"resource_id":"nonexistent-pkg","hint":"..."}`; keep stdout empty on failure; declare stderr framing (`single-error-object`). Name the log path in the payload (`path`) if a log exists.

### F5 — P1 — Exit codes undifferentiated
- type: schema-gap
- evidence: observed (not-found → exit 1) + absence-of-evidence (no exit-code map anywhere)
- location: `install` failure; `--help`
- impact: shell-level callers cannot distinguish not-found from transient failure.
- fix direction: declare a map (0 success, 1 generic/`INTERNAL`, 2 usage, 3 not found, 7 timeout, 9 transient, ...) and a per-command error catalog with `retryable`.

### F6 — P2 — No machine schema, fingerprint, or machine profile
- type: schema-gap
- evidence: absence-of-evidence (`--help` lists no `schema` command; `--json` not even listed in help)
- impact: agents discover flags by trial (`--json` is undocumented), cannot cache a contract, and have no single flag that guarantees non-interactive structured output.
- fix direction: add `depman schema [command]` and `depman schema --fingerprint` with `schema_version`, `fingerprint_scope`, output classes (`ls` = `list`), read-only vs mutating flags, error catalog, side effects, latency class. Add `--machine` implying `--format json`, non-interactive, no color/progress/banners.

### F7 — P2 — `clean` is a destructive mutation with no declared confirmation, dry run, or idempotency
- type: schema-gap
- evidence: absence-of-evidence
- location: `--help`, `clean`
- impact: an agent cannot preview what will be removed or know whether it prompts, needs `--yes`, or is safe to re-run. Same gaps apply to `install` and `sync`.
- fix direction: `--dry-run` on `clean`, `install`, `sync` returning `dry_run: true` and planned effects; declare retry safety, signal semantics, and lockfile/cache concurrency (locking or atomic replace).

### F8 — P2 — Ambient state undocumented
- type: schema-gap
- evidence: absence-of-evidence (global cache mentioned; registry, config, credentials, cwd project selection not described)
- impact: hidden state (global cache, registry auth, which lockfile via cwd) makes results non-reproducible.
- fix direction: document config/env/credential sources and precedence; add `config show --resolved`, a `--project <path>` override for cwd, and `--isolated`/`--no-config`.

### F9 — P2 — Networked commands lack timeout and retry contract
- type: schema-gap
- evidence: absence-of-evidence
- location: `install`, `sync`
- fix direction: `--timeout-ms`, declared retry defaults, transport-failure code in the catalog.

### F10 — P2 — Command model: aliases, vague names, odd verbs
- type: design-issue
- evidence: observed (`--help`)
- impact: aliases `i`/`add` multiply invocation paths; `ls` "Show stuff" gives no basis to choose it; `--quiet` "Less output" has no defined effect.
- fix direction: canonical `list` (keep `ls` as declared alias), declare aliases in schema and avoid them in examples, define `--quiet` precisely or replace with `--format`.

### F11 — P3 — Prose surfaces not task-selective
- type: design-issue
- evidence: observed (`--help`)
- impact: "Show stuff", "the friendly dependency manager!" banner, missing args/flags per command (`--json` absent).
- fix direction: rules-then-context summaries, e.g. `list  List installed packages (read-only; --format json)`; list per-command args, prerequisites, side effects.

### F12 — P3 — No evidence of contract tests
- type: schema-gap
- evidence: absence-of-evidence (no source supplied)
- fix direction: pin schema snapshots, JSON-clean stdout in non-TTY, error payloads and exits, non-TTY `sync` not prompting, dry-run behavior, concurrent cache/lockfile writes.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F10 |
| Machine Schema | F6 |
| Stdin Contract | not-checked — no stdin behavior shown or documented; also absence (F6) |
| Shell Safety | not-checked — `--` support and argument handling not visible |
| Agent-Safe Invocation | F1, F6, F9 |
| Output | F2 |
| Errors And Exit Codes | F4, F5 |
| Ambient State | F8 |
| Mutations And Long-Running Work | F1, F7 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F11 |
| Tests | F12 (no source to inspect) |

## Open questions / assumptions
- Does `sync` hang when stdin is not a TTY? Determines F1 at P0 vs P1. A safe probe: `depman sync < /dev/null` against a disposable project with a timeout.
- What reaches stderr? All captures dropped it; a rerun capturing stderr separately would show whether a structured error already exists there.
- Does `ls --json` stdout stay polluted when stdout is not a TTY (captures appear to be piped, so likely yes)?
- Where is "the log"?

## Release gating / remediation plan
F1–F5 are P0/P1 and block release. Suggested order:
1. Clean stdout: payload-only JSON, banners/progress to stderr, suppressed in non-TTY (F2).
2. Remove the default update check (F3).
3. Structured stderr errors + exit-code map (F4, F5).
4. Non-interactive `sync` failing fast without `--yes` (F1).
5. Then schema/fingerprint/`--machine`, dry runs, ambient-state docs, timeouts, naming, tests (F6–F12).
~~~~~~
