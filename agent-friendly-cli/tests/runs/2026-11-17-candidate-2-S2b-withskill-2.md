# Scenario 2b (audit, fail-fast control) — with-skill arm 2 (candidate-2 wave)

- **Date:** 2026-11-17
- **Tree:** `3489640` on `fix/agent-friendly-cli-review-2026-11-17` (revised wording; the arms read the identical skill files at pre-split `832a583`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,557 (final-turn context plus output, read from the transcript)
- **Output words:** 1,273
- **Transcript sha256:** `1938f0a8502e44da8c2f7a7e8ec13db0231afbd6559d76c3277de0c0c9c2b8da` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o2`; the scorer received the assertions verbatim and no arm labels

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
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave3/out/S2b-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | F4 — P2 — `sync` reuses exit `4` ... `sync` failed fast instead of hanging Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity (P1) = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | Lines 1, 2 and 4 are `✨ DepMan 3.2`, `Checking for updates...` and `Done in 0.42s ✓`. |

## Verbatim final output

~~~~~~markdown
# depman 3.2 — agent-friendliness audit

Audience: the tool author, who can change anything.
Evidence comes only from the captures you supplied, which are verbatim. In them, stdout is shown with stderr discarded, except the last capture, which shows stderr only.
I did not run any probes.

## Findings (ordered by severity)

### F1 — P1 — `ls --json` stdout mixes a banner, progress text and a summary with the payload
- Type: `impl-bug` (`--json` promises JSON, but stdout is not valid JSON)
- Evidence: `observed` (verbatim capture supplied by the user)
- Location: `depman ls --json 2>/dev/null`. Lines 1, 2 and 4 are `✨ DepMan 3.2`, `Checking for updates...` and `Done in 0.42s ✓`.
- Impact: `json.loads(stdout)` fails. An agent has to guess which line holds the payload, and that guess breaks whenever the decoration changes.
- Fix direction: in JSON or machine mode, stdout carries only the array. Send the banner, progress and timing to stderr, or suppress them. Add a test that parses stdout as JSON.

### F2 — P1 — The `ls` read path runs an update check
- Type: `design-issue`
- Evidence: `observed` (the `Checking for updates...` line in the capture). That the check makes a network call is `inferred`.
- Location: `depman ls --json` output.
- Impact: a read command makes an undeclared network call. It adds latency, can fail offline or in a sandbox, and leaks usage. No evidence shows the check stays on the local machine, so the severity cannot drop to P2.
- Fix direction: make update checks opt-in, never run them in machine or non-TTY mode, and never write them to stdout. If you keep the check, declare it in the schema as a side effect.

### F3 — P1 — The `install` failure is prose on stdout with no symbolic code
- Type: `design-issue`
- Evidence: `observed`. `Error: something went wrong (see log)` appears with stderr discarded, so it went to stdout. The exit code is `1`.
- Location: `depman install nonexistent-pkg`.
- Impact: an agent cannot tell "package not found" from a network or permission failure. It cannot decide whether to retry. It also reads an error from the stream that should carry only the success payload. "see log" names no path. Exit `1` is the generic code, so it says nothing about the cause.
- Fix direction: emit a structured error on stderr and keep stdout empty, using the shape `sync` already uses. For example: `{"code":"PACKAGE_NOT_FOUND","message":"...","temporary":false,"resource_id":"nonexistent-pkg"}` with exit `3` (not found). If the log matters, give its location in a `path` field. Declare a fallback code such as `INTERNAL` (exit 1) for failures nothing else anticipates.

### F4 — P2 — `sync` reuses exit `4`, and neither the code nor its confirmation behavior is declared
- Type: `schema-gap`
- Evidence: `observed` (exit 4 with `CONFIRMATION_REQUIRED` on stderr). The undeclared status is `absence-of-evidence`: `--help` documents no exit codes.
- Location: `depman sync --json < /dev/null`.
- Positive: with stdin not a TTY, `sync` failed fast instead of hanging. It also wrote a well-formed error to stderr only, with `code`, `message`, `hint` and `temporary`. Keep that behavior and use it as the model for F3.
- Impact: under the usual convention, exit `4` means unauthenticated. An agent that branches on the exit code alone may start an auth flow.
- Fix direction: map `CONFIRMATION_REQUIRED` to exit `2` (usage or validation) or to a declared domain code in the 10–123 range. Declare it in a per-command error catalog. Keep the hint as a flag value (`--yes`) and do not embed a shell string in it.

### F5 — P2 — No machine-readable contract; `--json` is undocumented
- Type: `schema-gap`
- Evidence: `absence-of-evidence`. `--help` lists only `--quiet` and `--yes`, yet `--json` works. No `schema`, `version` or fingerprint command appears in the material.
- Impact: an agent cannot discover the machine flag, the output shapes, the exit-code map, which commands mutate, or what stdin each command reads. It has to learn all of that by trial and error.
- Fix direction: add `depman schema` with `--fingerprint`, and expose a single command's contract through `depman schema <command>`. Declare:
  - one machine profile (for example `--machine`, which implies `--json`, no prompts, no banners and no update check)
  - the output class of each command (`ls` is a `list`)
  - the exit codes and the error catalog
  - a read-only or mutating flag for each command
  - each command's latency class
  - the stdin contract

### F6 — P2 — Mutating commands lack `--dry-run`, and `clean`'s safety is undeclared
- Type: `schema-gap`
- Evidence: `absence-of-evidence` from `--help`. That `clean` deletes data without asking is `inferred` from its summary, "Remove unused packages from the global cache".
- Impact: an agent cannot preview `install`, `sync` or `clean`. `clean` affects global state shared across projects. Nothing documents whether it asks for confirmation, how it behaves on interrupt, or whether concurrent runs are safe.
- Fix direction: add `--dry-run` to the mutating commands; its output includes `dry_run: true`. Require `--yes` for `clean` the same way `sync` does. Declare that each lockfile or cache write is atomic or locked, and what an interrupt leaves behind.

### F7 — P3 — Help text is vague and leans on aliases
- Type: `design-issue`
- Evidence: `observed` (`--help` capture).
- Location: `ls  Show stuff`; `install` aliases `i, add`; the `--quiet  Less output` option; the `--help` banner line.
- Impact: "Show stuff" does not let an agent choose between commands, and "Less output" does not say what gets dropped. The aliases multiply the ways to spell the same call.
- Fix direction: write each summary binding-rules-first, for example "ls: List installed packages (read-only)". Mark aliases as migration-only in the schema and leave them out of canonical examples. State exactly what `--quiet` suppresses. Prefer `list` over `ls` as the canonical name.

## Checklist coverage

| Section | Status |
|---|---|
| Command Model | F7 |
| Machine Schema | F5 |
| Stdin Contract | F5 (undeclared). The one observed case is fine: `sync` with `/dev/null` stdin did not block. |
| Shell Safety | not-checked. No captures of `--` or of hostile argument values. The `sync` hint correctly names a flag rather than a shell string. |
| Agent-Safe Invocation | F1, F2. Partly OK: `sync` did not prompt in non-TTY mode. Isolation, timeouts and metadata-path latency are not-checked. |
| Output | F1, F3 |
| Errors And Exit Codes | F3, F4 |
| Ambient State | not-checked. The material shows no config, environment or credential behavior. A global cache exists (F6), but its location and override are undocumented. |
| Mutations And Long-Running Work | F6. `sync` requires `--yes`, which is good. |
| Side Effects And Telemetry | F2 |
| Prose Surfaces | F7 |
| Tests | not-checked. No source or tests were supplied. |

## Open questions and assumptions
- I assumed `Checking for updates...` means a network call. If the check reads a local file only, F2 drops to P2.
- Does `--quiet` remove the banner and the update check from `ls --json`? Even if it does, `--json` alone must yield clean stdout.
- Does `install --json` change the error shape? Only the plain-mode failure was captured.
- Is the exit `4` for `sync` deliberate? Which other numeric codes does depman use?

## Suggested remediation order
F1, F2 and F3 are P1 and block release. Fix them first: clean JSON on stdout, no update check on reads, and structured errors for `install`. Then publish the schema and exit-code map (F5, F4). Then add dry-run and confirmation for the mutating commands (F6). Leave the help-text polish (F7) for last.
~~~~~~
