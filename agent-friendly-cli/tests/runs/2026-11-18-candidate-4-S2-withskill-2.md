# Scenario S2 — with-skill arm 2 (candidate-4 wave, issue #264)

- **Date:** 2026-11-18
- **Tree:** `4401ca2 (wording 80b72b2)` on `fix/agent-friendly-cli-hardening-264`, read from a detached worktree
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Output words (`wc -w`):** 1022
- **Scoring:** blinded packet, output id `o7`; the scorer received the assertion block verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/05ab3720-17ad-43fa-804f-f12616560daf/scratchpad/264/out/S2-withskill-2.md, then reply with only the word done.

## Scorer's verdicts for this output

### A1 — sync prompt blocking risk + what capture establishes/does not
- o7: PASS — part1 "may hang waiting for input" pass; part2 "inferred from its help text, not observed" pass.
### A2 — hang finding separates shown prompt from deduced hang
- o7: PASS — "Whether `sync` actually hangs without a TTY is inferred from its help text, not observed".
### A3 — stdout pollution flagged as breaking parsing, established by capture
- o7: PASS — part1 "make stdout non-parseable" pass; part2 "evidence: observed (capture, stdout only)" pass.
### A4 — unstructured error + generic exit 1, no symbolic code
- o7: PASS — "Errors carry no symbolic code"; "exit 1 ... map not-found to exit 3".
### A5 — update check on read path as hidden side effect
- o7: PASS — "undeclared network call on a read verb".
### A6 — `clean` without `--dry-run`
- o7: PASS — F7 "`clean` deletes from a shared global cache; agents can't preview"; add `--dry-run`.
### A7 — aliases `i`, `add` and `ls Show stuff`
- o7: PASS — part1 "Three names for install" pass; part2 "'Show stuff' does not say what is listed" pass.
### A8 — states areas captures cannot answer
- o7: PASS — "Shell Safety | not-checked: no `--` support or source shown"; stdin "not-checked at runtime".
### C1 — P0–P3 + template fields (severity, type, evidence, location, impact, fix direction) on every finding
- o7: FAIL — F8 has no location; F9 has no location/impact; F10 and F11 lack location/impact fields.
### C2 — literal evidence labels
- o7: PASS — same three words used.
### C3 — hang P0, pollution ≥P1
- o7: PASS — F1 P0, F2 P1.
### C4 — coverage table with not-checked reasons
- o7: PASS — table, "not-checked: no `--` support or source shown".

## Verbatim final output

~~~~~~~~markdown
# DepMan 3.2 — Agent-Friendliness Audit

Audience: tool author (can change anything). Evidence: user-supplied verbatim captures, stdout only (stderr discarded), so stderr behavior is not observed.

## Findings (by severity)

### F1 — P0 — `sync` prompts for confirmation; no declared non-interactive behavior
- type: schema-gap · evidence: inferred (help text: "asks for confirmation first")
- location: `depman --help`, `sync` line
- impact: an agent or CI job calling `sync` without a TTY may hang waiting for input. `--yes` exists globally, but nothing says non-TTY stdin suppresses the prompt or fails fast.
- fix: in machine/non-TTY mode, never prompt; without `--yes`, fail immediately with a structured error (e.g. `CONFIRMATION_REQUIRED`, exit 2, `temporary: false`, hint naming `--yes`). Declare this in the schema and add a non-TTY test.

### F2 — P1 — `ls --json` stdout mixes banner, progress, and summary with the payload
- type: impl-bug (`--json` promises JSON) · evidence: observed (capture, stdout only)
- location: `depman ls --json` output lines 1, 2, 4
- impact: `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` make stdout non-parseable; agents must strip lines heuristically.
- fix: in JSON/machine mode stdout carries only the payload. Move diagnostics to stderr (as typed NDJSON or suppressed) and drop banners entirely when non-TTY.

### F3 — P1 — Update check on a read path
- type: design-issue · evidence: observed ("Checking for updates..." on `ls`)
- location: `depman ls --json` line 2
- impact: undeclared network call on a read verb: latency, failure in offline/sandboxed agents, and nondeterminism. No evidence it stays local, so P1 stands.
- fix: make update checks opt-in, off in machine mode and non-TTY, and never on stdout.

### F4 — P1 — Errors carry no symbolic code, and errors go to stdout
- type: design-issue · evidence: observed
- location: `depman install nonexistent-pkg` → stdout `Error: something went wrong (see log)`, exit 1
- impact: an agent cannot tell not-found from network failure from bad input; it can only parse vague English. The error landed on stdout (stderr was discarded and it still showed), polluting the success channel. "see log" names no path.
- fix: emit a structured error on stderr `{"code":"PACKAGE_NOT_FOUND","message":"...","temporary":false,"resource_id":"nonexistent-pkg","hint":"..."}`, keep stdout empty on failure, and map not-found to exit 3. Declare a fallback `INTERNAL` code (exit 1). Give the log path in a `path` field.

### F5 — P2 — No machine schema or machine profile
- type: schema-gap · evidence: absence-of-evidence
- location: `--help` (no `schema` command, no `--machine`/`--format`)
- impact: agents can't discover flags, output shapes, exit codes, or side effects without trial and error. `--json` appears in use but isn't documented in help.
- fix: add `depman schema` (plus `schema <command>` and `schema --fingerprint` with `fingerprint_scope`), a single `--machine` profile, per-command output class (`ls` → `list`), error catalog, read-only vs mutating classification, latency class, and stdin contract.

### F6 — P2 — Ambiguous command model and aliases
- type: design-issue · evidence: observed
- location: help: `ls — Show stuff`; `install (aliases: i, add)`
- impact: "Show stuff" does not say what is listed (project deps? global cache?). Three names for install inflate the choice space; `add` usually means "add to manifest", which may differ from install.
- fix: rename to `list` with a selective summary ("List installed dependencies of the current project"); keep aliases only for migration, declared in schema as deprecated.

### F7 — P2 — Mutations lack `--dry-run`, idempotency, and side-effect declarations
- type: schema-gap · evidence: absence-of-evidence
- location: `install`, `clean`, `sync` in help
- impact: `clean` deletes from a shared global cache; agents can't preview the effect, and nothing says whether retries after an interrupt are safe or how concurrent runs touch the lockfile.
- fix: add `--dry-run` (output with `dry_run: true`) to all three; declare retry/reconcile semantics, signal behavior, and lockfile/cache locking.

### F8 — P2 — Ambient state undocumented
- type: schema-gap · evidence: absence-of-evidence
- impact: global cache location, registry config, credentials, and whether the cwd selects the project are all implicit.
- fix: document sources and precedence; add `--isolated`/`--no-config` and a `config show --resolved` command; add `--project <path>` to override the cwd.

### F9 — P2 — No timeout control for networked commands
- type: schema-gap · evidence: absence-of-evidence
- fix: add `--timeout-ms` and declare retry behavior for `install`, `sync`, and anything that hits the registry.

### F10 — P3 — Vague, human-oriented flags and output
- type: design-issue · evidence: observed
- `--quiet` ("Less output") doesn't define what is suppressed; emoji/checkmarks in output. Fix: define `--quiet` precisely or replace it with the machine profile; keep emoji out of non-TTY output.

### F11 — P2 — No evidence of contract tests
- type: schema-gap · evidence: absence-of-evidence (no source supplied)
- fix: add tests for JSON stdout purity, error payloads and exit codes, non-TTY no-prompt behavior on `sync`, and dry-run.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F6 |
| Machine Schema | F5 |
| Stdin Contract | F5 (undeclared); not-checked at runtime |
| Shell Safety | not-checked: no `--` support or source shown |
| Agent-Safe Invocation | F1, F2, F9 |
| Output | F2, F4 |
| Errors And Exit Codes | F4 |
| Ambient State | F8 |
| Mutations And Long-Running Work | F1, F7 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F6, F10 |
| Tests | F11 |

## Open questions / assumptions
- stderr was discarded, so I can't tell what (if anything) DepMan writes there; F4 assumes the error line went to stdout because it appeared despite `2>/dev/null`.
- Whether `sync` actually hangs without a TTY is inferred from its help text, not observed.
- Whether `--json` is a documented flag or an undocumented one is unclear.
- What "see log" refers to and where the log lives.

## Suggested remediation order
P0/P1 block release: F1 (no prompts in non-TTY), F2 + F3 (clean stdout, no update check), F4 (structured stderr errors with codes). Then add the schema and machine profile (F5), which gives a place to declare the rest (F6–F11).
~~~~~~~~
