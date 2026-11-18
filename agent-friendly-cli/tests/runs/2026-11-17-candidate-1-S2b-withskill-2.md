# Scenario 2b (audit, fail-fast control) — with-skill arm 2 (candidate-1 wave)

- **Date:** 2026-11-17
- **Tree:** `df8fdcd` on `fix/agent-friendly-cli-review-2026-11-17` (first candidate wording; the arms read the identical skill files at pre-rebase `5ea7acf`)
- **Mode:** with-skill (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 64,450 (final-turn context plus output, read from the transcript)
- **Output words:** 1,288
- **Transcript sha256:** `e2c3a6c78a13fbd36990388d348a1d099cdc030aecc7498c0aa5eb9c0aac48f2` (session-local copy; not committed)
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
> 1. Read the skill at /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/SKILL.md and follow it, including the files under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/references/ that it routes you to.
> 2. Do not read, list, or search anything under /Users/bdc/projects/skills-afcli-fixes/agent-friendly-cli/tests/, any other file in that repository, or any other directory. Do not use the web or any other skill.
> 3. Your task is in /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/prompts/S2b.md. Read it and do exactly what it asks, as you would for a real user, applying the skill.
> 4. Write your complete answer as Markdown to /private/tmp/claude-501/-Users-bdc-projects-skills/9790e7f3-33cc-48b6-881c-58edafa6171a/scratchpad/wave2/out/S2b-withskill-2.md, then reply with only the word done.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | `sync` with stdin closed did **not** hang. ... F5 — P2: exit `4` for `CONFIRMATION_REQUIRED` (top severity is P1) Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding carries top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | F1 — P1: `ls --json` stdout mixes a banner, progress text, and a summary into the JSON payload |

## Verbatim final output

~~~~~~markdown
# depman 3.2: agent-friendliness audit

Audience: the tool's author, so this report lists contract gaps and the fixes that close them.
Evidence comes only from the four captures you supplied.
Each is labeled `observed (user-supplied capture)`.
I did not run anything.
Stream attribution follows your capture notes: every line is stdout, except the last capture, which is stderr only.

## Findings (by severity)

### F1 — P1: `ls --json` stdout mixes a banner, progress text, and a summary into the JSON payload
- type: `impl-bug` (`--json` promises JSON, and stdout is not valid JSON)
- evidence: observed (user-supplied capture)
- location: `depman ls --json 2>/dev/null`. stdout lines 1–2 (`✨ DepMan 3.2`, `Checking for updates...`) and line 4 (`Done in 0.42s ✓`) surround the array
- impact: `json.loads` / `jq` on stdout fails, so agents have to scrape out the line that looks like JSON. The non-ASCII glyphs also cost tokens.
- fix direction: in `--json` mode (and whenever stdout is not a TTY), stdout carries only the payload. Send the banner, progress, and timing to stderr, and suppress them entirely in machine mode. Add a single `--machine` profile that implies `--json`, no color, no progress, and no prompts.

### F2 — P1: the read path runs an update check
- type: `design-issue`
- evidence: observed (user-supplied capture). The text `Checking for updates...` appears in the `ls` output. A network call is `inferred`.
- location: `depman ls --json` stdout line 2
- impact: a read verb makes a call nobody asked for. That adds latency, fails offline or in sandboxes, and leaks usage. It is also the source of part of F1's stdout pollution.
- fix direction: no update check by default. Make it opt-in and always suppressed in machine mode. If it stays, declare it as a side effect in the schema and send its notice to stderr only. (I gave this P1 because nothing shows the effect stays on the local machine.)

### F3 — P1: install failure has no symbolic code, goes to stdout, and points at an unnamed log
- type: `design-issue`
- evidence: observed (user-supplied capture)
- location: `depman install nonexistent-pkg 2>/dev/null` prints `Error: something went wrong (see log)` on stdout and exits `1`
- impact: an agent cannot tell not-found from network, auth, or conflict failures, cannot decide whether to retry, and does not know where the log is. The error is on stdout, so a caller that treats stdout as payload misreads it. `sync` already emits a good structured error, so the tool is inconsistent with itself.
- fix direction: write the same structured error as `sync` to stderr, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"...","temporary":false,"resource_id":"nonexistent-pkg"}`, and exit with a declared not-found code (the skill convention is `3`). Keep stdout empty on failure. Name the log path in a `path` field, or drop the reference to it. Declare a fallback code such as `INTERNAL` (exit `1`) for unanticipated failures.

### F4 — P2: no machine-readable schema, and `--json` is not in the help
- type: `schema-gap`
- evidence: absence-of-evidence (`--help` lists no `schema` command, no `--json`, no exit codes, and no output shapes)
- location: `depman --help`
- impact: agents learn the contract by trial and error. The `--json` flag the captures use is undocumented, as are exit `4` and which commands mutate.
- fix direction: add `depman schema` (plus `schema <command>` and `schema --fingerprint`, with `schema_version` and `fingerprint_scope`). It should declare per command: whether it reads or mutates, the output class (`ls` → `list`), shapes, stdin, the per-command error catalog with exit mappings, side effects, latency class, and the machine profile.

### F5 — P2: exit `4` for `CONFIRMATION_REQUIRED` is undeclared and clashes with the common convention
- type: `schema-gap`
- evidence: observed (user-supplied capture), exit=4
- location: `depman sync --json < /dev/null`
- impact: shell-level callers that follow the usual convention read `4` as "unauthenticated". Nothing documents what `4` means here.
- fix direction: declare the exit map in the schema. Map confirmation-required to usage/validation `2` or to a declared domain code (`10`+), and list `CONFIRMATION_REQUIRED` in `sync`'s error catalog with `retryable: false`.

### F6 — P2: vague command summaries, an alias list, and vague flags
- type: `design-issue`
- evidence: observed (user-supplied capture)
- location: `--help`. `ls  Show stuff`, `install (aliases: i, add)`, `--quiet  Less output`, `--yes  Assume yes`
- impact: "Show stuff" does not say what is listed (installed deps? the lockfile? the global cache?), so an agent cannot choose between `ls` and the other commands. Two aliases for one operation multiply the invocation paths. `--quiet` gives no guarantee about what it suppresses, and it does not say which commands accept `--yes`.
- fix direction: rewrite each summary so it says what the command does and what it changes, e.g. `ls  List installed dependencies (read-only)`. Keep aliases only for migration, declare them in the schema, and leave them out of examples. Spell out each flag's effect and scope, or replace `--quiet` with the machine profile.

### F7 — P2: mutations have no declared dry-run or retry semantics
- type: `schema-gap`
- evidence: absence-of-evidence
- location: `--help` for `install`, `clean` (removes from the **global** cache, shared across projects), and `sync`
- impact: an agent cannot preview `clean` or `sync`. It also cannot know whether retrying `install` after a timeout is safe, or whether interrupting `sync` leaves a half-written lockfile.
- fix direction: add `--dry-run` (output includes `dry_run: true`). Declare which mutations are repeat-safe, the lockfile write is atomic, behavior under concurrent invocations against the global cache and the lockfile, and SIGINT behavior.

### F8 — P3: the help banner contains marketing text
- type: `design-issue`
- evidence: observed (user-supplied capture)
- location: `--help` line 1
- impact: minor token cost. The version would be better exposed through `depman version --json`.
- fix direction: lead the help with usage. Expose the version through a dedicated command.

## What already works (credit)
- `sync` with stdin closed did **not** hang. It failed fast with a structured error on stderr only: `code`, `message`, `hint`, and `temporary:false` are all present. That is the target shape for every error (see F3). Its confirmation behavior has to be declared (F5), and `hint` could carry the repair as structured `details` (e.g. `{"flag":"--yes"}`).
- `--yes` exists as an explicit trigger for non-interactive confirmation.

## Checklist coverage
- Command Model: F6
- Machine Schema: F4, F5
- Stdin Contract: absence covered by F4. Observed `sync` with `/dev/null` stdin fails fast and does not block.
- Shell Safety: `not-checked`. There is no evidence of `--` support or of how arguments are handled.
- Agent-Safe Invocation: F1 (no machine profile). Non-interactive behavior on closed stdin is OK for `sync` (observed). TTY detection of progress and the latency of metadata paths are `not-checked`.
- Output: F1, F3
- Errors And Exit Codes: F3, F5
- Ambient State: `not-checked`. There is no evidence about the config, registry credentials, or global cache location. Expect gaps: no `--isolated` or resolved-config inspection appears in the help.
- Mutations And Long-Running Work: F7
- Side Effects And Telemetry: F2
- Prose Surfaces: F6, F8
- Tests: `not-checked`. No source or tests were supplied.

## Open questions / assumptions
- Does the update check make a network call, and does it write anything (such as a timestamp cache)?
- Is the `install` error always on stdout, or only without `--json`? The capture did not use `--json`.
- Does `--quiet` remove the banner and progress from `ls --json` stdout?
- What does `sync` do with a TTY on stdin and no `--yes`? Is the prompt suppressed when only stdout is non-TTY?

## Remediation plan
Fix F1–F3 first; they are the P1 findings, and each one breaks parsing or branching for agents. Then publish the schema (F4), which resolves F5 and most of F7.
~~~~~~
