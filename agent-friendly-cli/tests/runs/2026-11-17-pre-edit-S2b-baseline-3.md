# Scenario 2b (audit, fail-fast control) — baseline arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 50,036 (final-turn context plus output, read from the transcript)
- **Output words:** 576
- **Transcript sha256:** `a6a91da4b4c7fa17856db1d127a2d567586750206cfe1dfa3ae6dd496d933fab` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o4`; the scorer received the assertions verbatim and no arm labels

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

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | It does not hang on a prompt when stdin is not a TTY; it fails fast. Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | 1. High: `ls --json` stdout is not valid JSON |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Scope: only the four captures provided; nothing was run.
Every capture except the last discards stderr, so all text in them is stdout.

## Findings, by severity

### 1. High: `ls --json` stdout is not valid JSON
Stdout contains a banner (`✨ DepMan 3.2`), `Checking for updates...`, the JSON array, and `Done in 0.42s ✓`.
`depman ls --json | jq` fails, so an agent has to guess which line is the payload.
Fix: when `--json` is set (or stdout is not a TTY), stdout holds exactly one JSON document.
Send the banner, progress, and timing to stderr, or drop them.

### 2. High: install failure is unactionable, and it goes to stdout
`Error: something went wrong (see log)` names no cause (unknown package? network?), no log path, and no next step.
It appears under `2>/dev/null`, so the error is on stdout, where it can be mistaken for data.
Exit 1 is the only signal, and nothing documents what 1 means.
Fix: write errors to stderr, using the same structured shape `sync` already uses, e.g. `{"code":"PACKAGE_NOT_FOUND","message":"no package named nonexistent-pkg","hint":"check the name with depman search","temporary":false}`.
Give each error class its own documented exit code.

### 3. Medium: implicit update check on every command
`Checking for updates...` suggests a network call on a read-only `ls`.
This adds latency, can fail or hang offline or in a sandbox, and makes output nondeterministic.
Fix: skip the check when non-interactive, and add an opt-out (`--no-update-check` or an env var).

### 4. Medium: `--help` is too thin for an agent to plan from
- `--json` works but is not listed.
- `ls` is described as "Show stuff". Say what it lists (installed packages? global cache?).
- `clean` deletes things, but help does not say whether it prompts, or whether there is a `--dry-run`.
- Exit codes are not documented, even though `sync` returns 4.
- `--quiet` ("Less output") does not say what it suppresses.
- There are no per-command help or examples, e.g. `depman install --help`, or the argument syntax for `install`.
Fix: list every flag, define each exit code, and add one example per command.
Mark which commands are destructive or need confirmation.

### 5. Low: decoration in machine paths
Emoji and check marks (`✨`, `✓`) show up in stdout that was captured from a non-TTY.
Turn them off when stdout is not a TTY, or when `NO_COLOR`/`--json` is set.

## What already works (keep it, and extend it)
`sync --json < /dev/null` is the model to copy:
- It does not hang on a prompt when stdin is not a TTY; it fails fast.
- Stdout is empty, so it is not polluted.
- Exit 4 is distinct from the generic 1.
- Stderr holds a structured error with a stable `code`, a `hint` the agent can act on (`pass --yes`), and a `temporary` retry flag.

Make every command behave this way: install, ls, and clean included.
Document code 4 (and the rest) in `--help`.

## Suggested priority
1. Clean JSON on stdout for `--json` (finding 1).
2. Structured stderr errors and distinct exit codes everywhere (finding 2).
3. Update check off when non-interactive (finding 3).
4. Help text completeness, especially `--json`, exit codes, and `clean` safety (finding 4).

## Unverified (needs a run to confirm)
- Whether `clean` prompts, or how it behaves without a TTY.
- Whether `--quiet` suppresses the banner and the update check.
- What `install` writes to stderr; that capture discarded it.
~~~~~~
