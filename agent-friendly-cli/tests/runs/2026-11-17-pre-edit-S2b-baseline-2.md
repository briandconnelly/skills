# Scenario 2b (audit, fail-fast control) — baseline arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 50,247 (final-turn context plus output, read from the transcript)
- **Output words:** 670
- **Transcript sha256:** `cf000e0f72bace5710af16bb9aa662d8ef1207e28d085e3fcb6b9b17c78926b7` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o3`; the scorer received the assertions verbatim and no arm labels

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
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | `sync` without a TTY does not hang on its prompt Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | 1. High: `ls --json` stdout is not valid JSON |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Scope: findings are drawn only from the captured transcript; nothing was run.

## What already works (keep it)

- `sync` without a TTY does not hang on its prompt: it fails fast with stdin at `/dev/null`.
- `sync` failure uses a distinct exit code (4), not a generic 1.
- The `sync` error goes to stderr as structured JSON with a stable `code`, a `hint` naming the fix (`--yes`), and a `temporary` retry flag.
  This is the model the rest of the CLI should follow.
- `--yes` exists, so confirmation can be bypassed non-interactively.

## Findings, by severity

### 1. High: `ls --json` stdout is not valid JSON

With stderr discarded, stdout still contains `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` around the array.
`depman ls --json | jq` fails, so `--json` breaks its main promise.
Fix: when `--json` is set (or stdout is not a TTY), stdout must contain only the JSON document; send the banner, progress, and timing to stderr or drop them.

### 2. High: `install` errors go to stdout, are vague, and use a generic exit code

`Error: something went wrong (see log)` appears with stderr discarded, so it was written to stdout, where it can be mistaken for data.
It does not say what failed (the package was not found), which log, or where the log is.
Exit 1 does not separate "package not found" from network, permission, or internal errors.
Fix: write errors to stderr; name the cause and the package (`package 'nonexistent-pkg' not found in registry X`); print the log path; use distinct, documented exit codes; emit the same JSON error shape as `sync` when `--json` is given.

### 3. Medium: implicit network side effect on a read command

`ls` prints `Checking for updates...`, so a read-only listing appears to contact the network.
This adds latency, can fail offline or in sandboxes, and is a hidden side effect.
Fix: do not check for updates from non-interactive or `--json` runs, and provide an opt-out (flag or env var, for example `DEPMAN_NO_UPDATE_CHECK=1`).

### 4. Medium: `--help` is incomplete and imprecise

- `--json` is used by `ls` and `sync` but is not listed, so an agent cannot discover it.
- `ls` is described as "Show stuff"; say what it lists (installed packages? direct or transitive? local or global?).
- `clean` deletes from the global cache with no mention of confirmation, `--dry-run`, or scope; a destructive command needs these stated.
- `--quiet` says "Less output" without saying what is suppressed.
- No exit codes, environment variables, or `--version` are documented, and there is no sign of per-command help (`depman sync --help`).
- The help text includes a marketing tagline; it costs tokens and carries no information.

Fix: list every global and per-command flag, give each command a precise one-line description, document exit codes (0, 1, 4, ...) and the JSON error schema, and add `depman <command> --help`.

### 5. Low: decoration in output

Emoji and check marks (`✨`, `✓`) and the version banner appear on every run.
Fix: suppress them when stdout is not a TTY, and honor `NO_COLOR`-style conventions.

### 6. Low: inconsistent behavior across commands

`sync` has a structured stderr error and a specific exit code; `install` has neither.
An agent cannot rely on one error-handling path.
Fix: route all commands through one error reporter that produces the `sync` shape.

## Not determinable from the captures

- Whether `install` or `clean` prompt or hang without a TTY.
- Whether `--quiet` removes the stdout noise in finding 1.
- What other exit codes exist, and whether `clean` supports dry-run.
- What `install` writes to stderr (the capture discarded it).
  Capturing `depman install nonexistent-pkg 2>&1 >/dev/null` would show whether a more useful message already exists there.

## Suggested priority

1. Clean `--json` stdout (finding 1).
2. Stderr, specific messages, and distinct exit codes for all errors, reusing the `sync` JSON shape (findings 2 and 6).
3. Update-check opt-out (finding 3).
4. Help text and documented exit codes (finding 4).
~~~~~~
