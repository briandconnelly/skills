# Scenario 2 (audit) — with-skill arm 2 (candidate-3 wave)

- **Date:** 2026-11-17
- **Tree:** `3cccc7a` on `fix/agent-friendly-cli-review-2026-11-17` (final wording: hardening edits reverted, rule conflicts from the Codex branch review resolved)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 3/4 conformance
- **Tokens:** 64,584 (final-turn context plus output, read from the transcript)
- **Output words:** 1,389
- **Transcript sha256:** `c71254f8d76ff4a3f14609b919b25e8308c0fa8995b4173d3611d64bb2dfc2a6` (session-local copy; not committed)
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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave4/out/S2-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | Evidence: inferred — `--help` says sync "asks for confirmation first"; nothing documents that the prompt is suppressed Parts: blocking risk = pass; established vs not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | Does `sync` actually block when stdin is not a TTY ... (F1 is inferred.) |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | Evidence: observed (user-supplied verbatim capture, stderr discarded...) `json.loads(stdout)` fails Parts: flagged breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Error has no symbolic code; ... Exit code does not distinguish failure classes |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Read path performs an update check (undeclared network call) |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | Agents cannot preview destructive cleanup ... `clean` mutates a shared global cache |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | `ls Show stuff`; `install (aliases: i, add)` ... three names for one operation inflate the selection space Parts: aliases = pass; Show stuff = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | Tests \| not-checked — no source or test suite supplied |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **FAIL** | F7 has no Location; F10 has no Location or Impact; F11 has no Location or Impact |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | Evidence: inferred / observed / absence-of-evidence |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | Severity: P0 (F1); Severity: P1 (F2) Parts: hang P0 = pass; pollution >=P1 = pass |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **PASS** | \| Stdin Contract \| not-checked — no stdin behavior shown ... \| |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author (can change anything).
Task: review of an existing CLI from captured material only; no probes were run.
All captures discard stderr, so every line shown is stdout.

## Findings (ordered by severity)

### F1 — `sync` prompts for confirmation; likely hangs in automation
- Severity: P0 (blocking behavior in machine/non-TTY mode is fixed at P0)
- Type: design-issue
- Evidence: inferred — `--help` says sync "asks for confirmation first"; nothing documents that the prompt is suppressed when stdin is not a TTY, or that `--yes` applies to `sync`.
- Location: `depman --help`, `sync` line and `--yes` option.
- Impact: an agent or CI job running `depman sync` waits on terminal input forever, or reads EOF and does something undeclared.
- Fix direction: never prompt when stdin is not a TTY or in machine mode; fail fast with a structured error such as `CONFIRMATION_REQUIRED` (exit 2, `temporary: false`, `hint` naming `--yes`) instead. Document which commands honor `--yes`. Add `--dry-run` to `sync` so agents can preview the lockfile change.

### F2 — `ls --json` mixes banner, progress, and summary with the JSON payload on stdout
- Severity: P1 (fixed placement for mixed success stdout)
- Type: impl-bug (`--json` promises JSON; stdout is not parseable JSON)
- Evidence: observed (user-supplied verbatim capture, stderr discarded, so all four lines are stdout).
- Location: `depman ls --json` output: `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓` surround the array.
- Impact: `json.loads(stdout)` fails; agents must strip lines heuristically, which breaks whenever the banner text changes.
- Fix direction: stdout carries only the payload. Move banners, progress, and timings to stderr, and suppress them entirely in machine mode and when stderr is not a TTY. Add a test that `depman ls --json | jq .` succeeds.

### F3 — Read path performs an update check (undeclared network call)
- Severity: P1 (hidden side effect on a read path; no evidence it is local-only)
- Type: design-issue
- Evidence: observed — `Checking for updates...` printed during `ls`.
- Location: `depman ls --json` stdout line 2.
- Impact: unexpected network egress, extra latency and failure modes on a read, nondeterminism in sandboxed/offline agents.
- Fix direction: make update checks opt-in (or off by default), always off in machine mode and non-TTY, and never written to stdout. Declare `ls` latency class `local`.

### F4 — Error has no symbolic code; message is unactionable; failure written to stdout
- Severity: P1 (errors without a symbolic code are fixed at P1)
- Type: design-issue (plus impl-bug for the stream: the error appeared despite `2>/dev/null`, so it is on stdout)
- Evidence: observed.
- Location: `depman install nonexistent-pkg` → stdout `Error: something went wrong (see log)`, exit 1.
- Impact: agents cannot tell not-found from network, auth, or usage failures; cannot decide whether to retry; "see log" points to an undocumented location; a caller checking stdout for success payload gets an error string.
- Fix direction: on failure, stdout is empty; stderr carries a structured object, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"package 'nonexistent-pkg' not found in registry","temporary":false,"resource_id":"nonexistent-pkg","field":"<package>"}`. Declare the framing (`single-error-object`) in the schema. Name the log path if it matters (a `path` field), or drop the reference.

### F5 — Exit code does not distinguish failure classes
- Severity: P1
- Type: schema-gap
- Evidence: observed (exit 1 for not-found); absence-of-evidence for any declared exit-code map.
- Location: `echo $?` → `1`.
- Impact: shell-level callers cannot branch on not-found vs transient.
- Fix direction: declare an exit map (e.g., 2 usage, 3 not found, 4 unauthenticated, 6 rate limited, 7 timeout, 9 transient) with a symbolic code per command, plus one fallback `INTERNAL` → exit 1.

### F6 — No machine-readable schema or contract
- Severity: P1
- Type: schema-gap
- Evidence: absence-of-evidence — `--help` is the only discovery surface; no `schema`, `--help --json`, or fingerprint is shown.
- Location: `depman --help`.
- Impact: agents must parse prose to learn commands, flags, output shapes, exit codes, and which commands mutate.
- Fix direction: add `depman schema [command]` and `depman schema --fingerprint` declaring command tree, aliases, flags/types, read-only vs mutating, output class per command (`ls`: `list`; `install`/`clean`/`sync`: `bulk-result` or `record`), error catalog, latency class, schema version, and `fingerprint_scope`.

### F7 — No declared machine profile; `--json` is undocumented
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence — `--json` works on `ls` but is not in `--help`; only `--quiet` ("Less output") and `--yes` are listed.
- Impact: agents cannot know which commands support JSON or what flag guarantees clean, non-interactive output.
- Fix direction: add a single `--machine` flag implying JSON output, no prompts, no color/progress/banners, no update check; declare it in the schema. Give `--quiet` a precise definition or drop it.

### F8 — Mutations (`install`, `clean`, `sync`) lack `--dry-run` and retry semantics
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence.
- Location: `--help`. `clean` mutates a shared global cache.
- Impact: agents cannot preview destructive cleanup or know whether retrying an interrupted `install`/`sync` is safe; concurrent runs on the global cache/lockfile are undefined.
- Fix direction: add `--dry-run` (output includes `dry_run: true`) to each mutating command; declare idempotency (installing an already-present package is a no-op), interrupt behavior, and locking for the lockfile and global cache.

### F9 — Vague and alias-heavy command model
- Severity: P2
- Type: design-issue
- Evidence: observed (`--help`).
- Location: `ls  Show stuff`; `install (aliases: i, add)`.
- Impact: "Show stuff" does not tell an agent what `ls` lists (installed? declared? global cache?); three names for one operation inflate the selection space, and `add` usually means "add to manifest" in other managers, which may differ from install.
- Fix direction: rename or describe `ls` precisely (e.g., `list` — "List installed packages in the current project as name/version records"). Keep aliases only for migration, declare them in the schema, and use `install` in all canonical examples.

### F10 — Ambient state undocumented
- Severity: P2
- Type: schema-gap
- Evidence: absence-of-evidence — global cache, lockfile, registry, project directory selection, and credentials are implied but nothing documents sources, precedence, or how to disable them.
- Fix direction: document config/env/cache/cwd resolution and precedence; add `depman config show --resolved` and an `--isolated` flag; declare `--project-dir` (or similar) to override cwd selection.

### F11 — Prose surfaces are marketing-first
- Severity: P3
- Type: design-issue
- Evidence: observed — `--help` opens with "the friendly dependency manager!" and gives no defaults, prerequisites, or output info.
- Fix direction: rules-then-context help text: usage, binding constraints (e.g., "sync prompts unless --yes"), defaults, then background.

## Checklist Coverage

| Section | Status |
|---|---|
| Command Model | F9 |
| Machine Schema | F6, F7 |
| Stdin Contract | not-checked — no stdin behavior shown; absence of any declaration folds into F6 |
| Shell Safety | not-checked — `--` support and argument handling not visible; declare in schema (F6) |
| Agent-Safe Invocation | F1, F7; metadata-path latency not-checked |
| Output | F2, F4 |
| Errors And Exit Codes | F4, F5 |
| Ambient State | F10 |
| Mutations And Long-Running Work | F1, F8 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F9, F11 |
| Tests | not-checked — no source or test suite supplied; recommend tests for `ls --json` parseability, non-TTY `sync` not blocking, error payload/exit mapping, and no network on `ls` |

## Open Questions / Assumptions

- Does `sync` actually block when stdin is not a TTY, or does it auto-decline/accept? (F1 is inferred.) One safe probe: `depman sync < /dev/null` with a timeout, in a disposable project.
- Does `--json` exist on commands besides `ls`, and does `--quiet` suppress the banner/update check?
- Is anything written to stderr today? Captures discarded it, so stderr content is unknown.
- What and where is "the log"?
- Does the update check also write a cache/timestamp file (an implicit write on a read)?

## Remediation Plan

Release blockers (P0/P1): F1–F6.
1. Clean stdout: payload only; banners/progress/update notices to stderr and off in machine mode (F2, F3).
2. Non-interactive `sync` with structured `CONFIRMATION_REQUIRED` failure (F1).
3. Structured stderr errors with symbolic codes and a declared exit map (F4, F5).
4. Ship `depman schema` + fingerprint and a `--machine` profile (F6, F7).
Then schedule F8–F11 and the tests listed above.
~~~~~~
