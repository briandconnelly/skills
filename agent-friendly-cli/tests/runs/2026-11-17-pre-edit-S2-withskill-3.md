# Scenario 2 (audit) — with-skill arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 8/8 scored; 4/4 conformance
- **Tokens:** 63,431 (final-turn context plus output, read from the transcript)
- **Output words:** 1,377
- **Transcript sha256:** `04dfd339f9a2a4238dc47659d3b264fb79e648e92800ef89edfb19fb4485e5c9` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o5`; the scorer received the assertions verbatim and no arm labels

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
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave1/out/S2-withskill-3.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | evidence: inferred (...; I did not observe how it behaves without a TTY) Parts: sync prompt flagged as blocking risk = pass; states what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | help says "asks for confirmation first"; I did not observe how it behaves without a TTY Parts: shows documented prompt = pass; distinguishes deduced non-TTY hang = pass |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | evidence: observed ... `depman ls --json \| jq` fails Parts: pollution flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | F4 — Errors have no symbolic code |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | F3 — Hidden update check on a read path |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` ... add `clean --dry-run` |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **PASS** | three names for one operation; `ls Show stuff` Parts: alias duplication flagged = pass; vague ls description flagged = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | \| Tests \| not-checked: no source or tests supplied |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **PASS** | severity: P0 / type / evidence / location / impact / fix direction Parts: P0-P3 words = pass; template fields severity/type/evidence/location/impact/fix = pass |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **PASS** | evidence: observed / inferred / absence-of-evidence |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **PASS** | F1 severity: P0; F2 severity: P1 |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **PASS** | \| Stdin Contract \| not-checked: there is no evidence about stdin |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — Agent-Friendliness Audit

Audience: the tool's author (who can change anything).
Task: audit of an existing CLI, done only from the captures you supplied; I did not run depman.
All `observed` labels below mean "you supplied a verbatim capture"; every captured line is stdout, because stderr went to `/dev/null`.
Release gating: P0 and P1 findings block a release.
This audit has one P0 and five P1s.

## Findings (ordered by severity)

### F1 — `sync` prompts for confirmation, with no declared non-interactive behavior
- severity: P0
- type: design-issue
- evidence: inferred (help says "asks for confirmation first"; I did not observe how it behaves without a TTY)
- location: `depman --help`, `sync` line
- impact: an agent or CI job that calls `depman sync` can hang waiting for terminal input. Nothing says whether `--yes` covers `sync`, or whether a non-TTY stdin suppresses the prompt or fails fast.
- fix direction: when stdin is not a TTY, or in machine mode, never prompt. Fail fast with a structured `confirmation_required` error (exit 2, `temporary: false`, `hint` naming `--yes`). Declare in the schema that `--yes` applies to `sync`. Add `sync --dry-run` that prints the planned lockfile diff with `dry_run: true`.

### F2 — `ls --json` stdout mixes a banner, progress text and a summary with the JSON payload
- severity: P1
- type: impl-bug
- evidence: observed (`depman ls --json 2>/dev/null`)
- location: stdout lines `✨ DepMan 3.2`, `Checking for updates...` and `Done in 0.42s ✓` surround the JSON array
- impact: `depman ls --json | jq` fails. Agents have to guess which line is the payload, and that costs tokens.
- fix direction: in JSON mode, stdout carries only the payload. Send the banner, progress and timing to stderr, and suppress them entirely when stderr is not a TTY or in machine mode. Add a test asserting that `ls --json` stdout parses as a single JSON document.

### F3 — Hidden update check on a read path, printed to stdout
- severity: P1
- type: design-issue
- evidence: observed (`Checking for updates...` on stdout during `ls`)
- location: `depman ls --json` output
- impact: a read command makes an undeclared network call. That adds latency and a failure mode, can break offline or sandboxed runs, and pollutes stdout. I have no evidence that the check stays on the local machine, so this does not drop to P2.
- fix direction: no update check by default. Make it opt-in, suppress it in machine mode, never write it to stdout, and declare it in the schema's side effects.

### F4 — Errors have no symbolic code and reference an undisclosed log
- severity: P1
- type: design-issue
- evidence: observed (`Error: something went wrong (see log)`, exit 1)
- location: `depman install nonexistent-pkg`
- impact: an agent cannot tell "package not found" apart from a network, auth or other failure. It cannot decide whether to retry, and it does not know where "the log" is. This is the common failure path for `install`.
- fix direction: emit a structured error such as `{"code":"package_not_found","message":"…","temporary":false,"resource_id":"nonexistent-pkg","hint":"…"}`. Use distinct exits (for example 3 for not found, declared in the schema). Expose the log path in a `path` or `details` field.

### F5 — The failure message goes to stdout, not stderr
- severity: P1
- type: impl-bug
- evidence: observed (the error line survived `2>/dev/null`, so it was written to stdout)
- location: `depman install nonexistent-pkg` output
- impact: a caller that reads stdout as the payload sees error text as if it were data. Stream separation cannot be relied on.
- fix direction: write failures to stderr only, using a declared framing (`single-error-object` or `ndjson-typed`). Keep stdout empty on failure.

### F6 — No machine mode or schema to discover
- severity: P1
- type: schema-gap
- evidence: absence-of-evidence (help lists no `schema` command, no `--json` or `--format` global, and no machine profile; `--json` appears only in the `ls` capture)
- location: `depman --help`
- impact: agents cannot learn which commands accept `--json`, what output shapes or exit codes to expect, or which commands mutate. That pushes them to parse prose.
- fix direction: add `depman schema` and `depman schema --fingerprint` covering the command tree, flags with types, output class per command (`ls` → `list`), read-only vs mutating, side effects, exit codes and the error catalog. Add one `--machine` flag that implies JSON output, no prompts, no color, no banners and no update check.

### F7 — Vague, non-selective help text
- severity: P2
- type: design-issue
- evidence: observed
- location: `ls  Show stuff`, `--quiet  Less output`, `--yes  Assume yes`, plus a marketing banner as the first line of help
- impact: agents cannot tell what `ls` lists (installed? direct or transitive? global?), what `--quiet` suppresses, or which commands `--yes` affects.
- fix direction: write summaries that put the rule first, for example "ls — list installed packages in the current project (read-only)". State the scope of each flag. Remove the slogan.

### F8 — Command naming, and aliases in the main help
- severity: P2
- type: design-issue
- evidence: observed
- location: `install (aliases: i, add)`, `ls`
- impact: three names for one operation, plus the abbreviation `ls` instead of `list`, give agents more ways to pick inconsistently. `add` also suggests different semantics (adding to the manifest rather than installing).
- fix direction: make `list` canonical and keep `ls` only as a declared alias. Declare aliases in the schema and keep them out of canonical examples. Decide whether `add` really means `install`.

### F9 — `clean` is a destructive mutation with no declared safeguards
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`, `clean`
- impact: an agent cannot preview what `clean` removes or know whether it is safe to run concurrently with an `install`.
- fix direction: add `clean --dry-run` with `dry_run: true` output listing the packages it would remove. Declare it as mutating, declare its locking or atomicity, and declare what an interrupt leaves behind.

### F10 — Undeclared ambient state, timeouts and retries
- severity: P2
- type: schema-gap
- evidence: absence-of-evidence
- location: `depman --help`
- impact: registry config, credentials, cache location and network timeouts are all invisible. Agents cannot isolate runs or inspect the resolved config.
- fix direction: document config, env and credential sources and their precedence. Add `config show --resolved`, `--no-config`/`--isolated` and `--timeout-ms` for networked commands, and declare retry behavior.

### F11 — Non-deterministic noise in stdout
- severity: P3
- type: impl-bug
- evidence: observed (`Done in 0.42s ✓`)
- location: `ls --json` output
- impact: run-to-run differences break caching and diffing, and the emoji wastes tokens. Removing this is covered by the F2 fix.
- fix direction: remove it as part of F2.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F8 |
| Machine Schema | F6 |
| Stdin Contract | not-checked: there is no evidence about stdin; the `sync` prompt is under F1 |
| Shell Safety | not-checked: no evidence of `--` support or of how arguments are handled |
| Agent-Safe Invocation | F1, F6, F10 |
| Output | F2, F5, F11 |
| Errors And Exit Codes | F4, F5 |
| Ambient State | F10 |
| Mutations And Long-Running Work | F1, F9 |
| Side Effects And Telemetry | F3 |
| Prose Surfaces | F7 |
| Tests | not-checked: no source or tests supplied (recommended: a test that stdout of `--json` parses, a non-TTY `sync` test, and exit-code map tests) |

## Open questions and assumptions

- Does `sync` prompt when stdin is not a TTY, and does `--yes` apply to it? (F1 is inferred.)
- Does `--quiet` suppress the banner and the update check?
- Is the update check a network call, and can it be disabled?
- Where is "the log", and what does `install` write to stderr (it was discarded)?
- Is `--json` supported on commands other than `ls`?

## Suggested remediation order

1. F1, F2, F3, F5: make it non-blocking and keep stdout clean (one `--machine` profile fixes most of this).
2. F4: structured errors and an exit-code map.
3. F6: `schema` and fingerprint.
4. F7–F10: help text, naming, dry-run and ambient state.
~~~~~~
