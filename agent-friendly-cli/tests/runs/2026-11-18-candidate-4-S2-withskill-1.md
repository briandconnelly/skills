# Scenario S2 — with-skill arm 1 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1258
- **Scoring:** blinded packet, output id `o91`; the scorer received the assertion block verbatim and no arm labels

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
> 1. Read the skill at /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/SKILL.md and follow it, including the files under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/tree/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/prompts/S2.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S2-withskill-1.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 — sync prompt blocking risk + what capture establishes/does not
- o91: PASS — part1 "likely hangs agents in non-TTY use" pass; part2 "inferred (help text...); no capture shows behavior without a TTY" pass.
### A2 — hang finding separates shown prompt from deduced hang
- o91: PASS — "inferred (help text: 'asks for confirmation first'); no capture shows behavior without a TTY".
### A3 — stdout pollution flagged as breaking parsing, established by capture
- o91: PASS — part1 "`json.loads(stdout)` fails" pass; part2 "evidence: observed" pass.
### A4 — unstructured error + generic exit 1, no symbolic code
- o91: PASS — "generic exit 1 for a not-found case"; "Errors have no symbolic code".
### A5 — update check on read path as hidden side effect
- o91: PASS — "F3 — Update check on a read path ... hidden side effect".
### A6 — `clean` without `--dry-run`
- o91: PASS — F6 "`clean` deletes from a shared global cache ... no preview"; fix "`--dry-run` on install/clean/sync".
### A7 — aliases `i`, `add` and `ls Show stuff`
- o91: PASS — part1 "`install` aliases `i, add`" pass; part2 "`ls  Show stuff`" pass.
### A8 — states areas captures cannot answer
- o91: PASS — "Stdin Contract ... not-checked — no capture uses stdin"; "Shell Safety | not-checked".
### C1 — P0–P3 + template fields (severity, type, evidence, location, impact, fix direction) on every finding
- o91: PASS — F1–F10 each list severity/type/evidence/location/impact/fix direction.
### C2 — literal evidence labels
- o91: PASS — "inferred", "observed", "absence-of-evidence".
### C3 — hang P0, pollution ≥P1
- o91: PASS — F1 P0, F2 P1.
### C4 — coverage table with not-checked reasons
- o91: PASS — table, "not-checked — no capture uses stdin".

## Verbatim final output

~~~~~~~~markdown
# depman 3.2 — agent-friendliness audit

Audience: tool author (can change anything).
Evidence base: three user-supplied captures, stdout only (stderr discarded); nothing was run.
`observed` below means "observed in the user-supplied verbatim capture".

Release gating: F1–F5 (P0/P1) block a release until fixed.

## Findings (by severity)

### F1 — `sync` prompts for confirmation; likely hangs agents in non-TTY use
- severity: P0
- type: design-issue
- evidence: inferred (help text: "asks for confirmation first"); no capture shows behavior without a TTY or whether `--yes` covers it
- location: `depman --help`, `sync` summary
- impact: an agent calling `depman sync` without `--yes` waits on terminal input in CI and hangs until killed.
- fix direction: never prompt when stdin is not a TTY or in machine mode; instead fail fast with a structured error (e.g. `CONFIRMATION_REQUIRED`, exit 2, `temporary: false`, `hint` naming `--yes`). Declare in the schema that `sync` is mutating, that `--yes` is its action trigger, and which global flags apply to it.

### F2 — `ls --json` stdout mixes banner, progress, and summary with the payload
- severity: P1 (fixed placement: mixed success stdout)
- type: impl-bug (`--json` promises JSON; stdout is not parseable JSON)
- evidence: observed
- location: `depman ls --json` capture, lines `✨ DepMan 3.2`, `Checking for updates...`, `Done in 0.42s ✓`
- impact: `json.loads(stdout)` fails; agents must strip lines heuristically and waste tokens on decoration.
- fix direction: in JSON/machine mode stdout carries only the payload array; banner, progress and timing go to stderr (as typed NDJSON `progress`/`warning` records if declared) or are suppressed. Suppress the banner and emoji whenever stdout is not a TTY.

### F3 — Update check on a read path
- severity: P1 (fixed placement: hidden side effect on a read path; no evidence it is local-only)
- type: design-issue
- evidence: observed (`Checking for updates...` printed by `ls`); the network call itself is inferred
- location: `depman ls --json` capture
- impact: undeclared network traffic, latency and possible failure on a read, also in CI/sandboxed agents; output depends on network state.
- fix direction: make update checks opt-in (or an explicit `depman self check-update` command), suppressed in machine mode, never written to stdout; declare `ls` latency class (`local`/`cached`).

### F4 — Errors have no symbolic code and are written to stdout
- severity: P1 (fixed placement: no symbolic code)
- type: design-issue
- evidence: observed (error text appears in a `2>/dev/null` capture, so it went to stdout; exit `1`)
- location: `depman install nonexistent-pkg` capture
- impact: agents cannot distinguish not-found from network, auth, or bug; "something went wrong" gives no repair; error text on stdout corrupts any payload parsing; generic exit 1 for a not-found case.
- fix direction: write failures to stderr as a structured object `{code, message, temporary, hint, details}` (e.g. `PACKAGE_NOT_FOUND`, exit 3, `temporary: false`, `details.name`); keep stdout empty on failure; declare a per-command error catalog including a fallback `INTERNAL` (exit 1) and a transport-failure code for networked commands; replace "see log" with the actual log `path` field.

### F5 — No machine-readable contract or machine profile
- severity: P1
- type: schema-gap
- evidence: absence-of-evidence (help lists no `schema` command, no `--json`/`--machine` global flag; `--json` works on `ls` but is undocumented)
- location: `depman --help`
- impact: agents cannot discover which commands accept `--json`, output shapes, exit codes, or which commands mutate; must guess from prose.
- fix direction: add `depman schema` (+ `--fingerprint`, per-command `schema <command>`) declaring command tree, aliases, flags/types/defaults, read-only vs mutating, output class per command (`ls`: `list`), error catalog, exit codes, side effects, latency class, schema version + fingerprint. Add one machine profile flag (e.g. `--machine`) implying JSON, no color/banner/progress/prompts, no update check.

### F6 — Mutating commands lack dry-run and retry semantics
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `install`, `clean`, `sync` in `--help`
- impact: `clean` deletes from a shared global cache and `sync` rewrites the lockfile with no preview; after a timeout/interrupt agents cannot know what changed; concurrent runs against the global cache/lockfile are undefined.
- fix direction: `--dry-run` on `install`/`clean`/`sync` returning `dry_run: true` plus planned effects; declare interrupt semantics, atomic lockfile writes and cache locking, and which mutations are safe to retry.

### F7 — Ambient state undocumented, no isolation
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (a global cache, a log file, and presumably registry config/credentials exist; none are documented)
- location: `--help`
- impact: results depend on hidden cwd/project, cache and config; agents cannot inspect or neutralize them.
- fix direction: document cwd/project selection and its override flag, config files, env vars, cache and log locations with precedence; add `config show --resolved` and `--isolated`/`--no-config`.

### F8 — Command naming and prose summaries are not task-selective
- severity: P2
- type: design-issue
- evidence: observed (help text)
- location: `--help`: `ls  Show stuff`; `install` aliases `i, add`; `--quiet  Less output`
- impact: "Show stuff" does not tell an agent what is listed (installed deps? cache?); `add` vs `install` suggests distinct operations; `--quiet` is undefined, so agents may rely on it to clean stdout and fail.
- fix direction: canonical full-word verbs (`list`), aliases declared as migration-only in the schema; rules-first summaries (e.g. "list: List installed dependencies of the current project. Read-only."); define precisely what `--quiet` suppresses, or replace it with the machine profile.

### F9 — No evidence of contract tests
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence (no source or tests supplied)
- location: n/a
- impact: F2/F4-style regressions (stdout pollution, exit-code drift) recur unnoticed.
- fix direction: add tests for schema snapshots, `--json` payload purity, failure payloads and exit codes, non-TTY no-prompt behavior, dry-run, interrupt and concurrency on the lockfile/cache.

### F10 — Help banner on `--help` stdout
- severity: P3
- type: design-issue
- evidence: observed
- location: `--help` first line
- impact: minor token waste; harmless for humans.
- fix direction: drop marketing text from help; expose version via `depman version` (structured with `--json`).

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F5 |
| Stdin Contract | F5 (undeclared); behavior not-checked — no capture uses stdin |
| Shell Safety | not-checked — no `--` support declared (part of F5); argument handling unknown without source |
| Agent-Safe Invocation | F1, F5 (no machine profile, no non-TTY suppression); metadata latency not-checked |
| Output | F2, F4 (error on stdout) |
| Errors And Exit Codes | F4 |
| Ambient State | F7 |
| Mutations And Long-Running Work | F1, F6 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F8, F10 |
| Tests | F9 |

## Open questions / assumptions

- Does `sync --yes` (or a non-TTY stdin) actually skip the prompt? F1 stays P0 until a non-TTY capture shows it does not block.
- Is `--json` supported on commands other than `ls`, and what does stderr contain? Captures with stderr kept would confirm stream attribution.
- Does the update check make a network call, and is its result cached? (Affects F3 only if proven local, which would downgrade it to P2.)
- What does `--quiet` suppress — does `ls --json --quiet` produce clean stdout?
- Exit codes beyond `1` were not observed; the full map is unknown.

## Suggested remediation order

1. Non-interactive `sync` (F1).
2. Clean `--json` stdout + stderr structured errors with symbolic codes (F2, F4).
3. Remove the update check from reads (F3).
4. `depman schema` + `--machine` profile (F5), then dry-run/ambient-state/naming (F6–F8) and contract tests (F9).
~~~~~~~~
