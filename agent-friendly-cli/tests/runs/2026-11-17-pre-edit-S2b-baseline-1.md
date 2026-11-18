# Scenario 2b (audit, fail-fast control) — baseline arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 2/2 scored
- **Tokens:** 50,542 (final-turn context plus output, read from the transcript)
- **Output words:** 799
- **Transcript sha256:** `856e66b241b27b127a6c8307aa960857c124da0004be61970696dc77dff5002e` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o6`; the scorer received the assertions verbatim and no arm labels

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
| A1 | scored | No finding claims that `sync` hangs or blocks in automation, and no finding about the `sync` prompt carries the report's top severity. | **PASS** | `sync` ... fails fast instead of hanging on a prompt; sync finding 4 is (medium) Parts: no finding claims sync hangs/blocks = pass; no sync-prompt finding at top severity = pass |
| A2 | scored | Stdout pollution on `ls --json` is still flagged. | **PASS** | 1. `ls --json` stdout is not valid JSON (critical) |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Scope: four captures only; I could not run the tool.
Everything below is judged from those captures, and anything not shown is marked as unknown.

## What already works

- `sync` without a TTY and without `--yes` fails fast instead of hanging on a prompt (`< /dev/null`, exit 4).
- That failure emits a structured error on **stderr** with a stable `code`, a `hint` that names the fix (`pass --yes`), and a `temporary` flag that tells an agent whether retrying could help.
  This is the model the rest of the tool should follow.
- A distinct non-zero exit code (4) for "confirmation required" lets an agent branch without parsing text.

## Findings (highest impact first)

### 1. `ls --json` stdout is not valid JSON (critical)

With stderr discarded, stdout still contains `✨ DepMan 3.2`, `Checking for updates...`, and `Done in 0.42s ✓` around the JSON array.
`depman ls --json | jq` will fail, so the flag that exists for machines is unusable by machines.
Fix: when `--json` is set (and ideally whenever stdout is not a TTY), stdout must contain exactly one JSON document and nothing else.
Send the banner, progress, and timing to stderr, or suppress them.

### 2. Hidden update check on a read-only command (high)

`ls` prints `Checking for updates...`, which suggests a network call on every invocation.
For agents this adds latency, can fail or hang offline or in sandboxes, and is a side effect nobody asked for.
Fix: do not check during `--json` / non-TTY runs, or provide an opt-out (`--no-update-check`, env var) and document it.

### 3. `install` failure is unstructured, on stdout, and unactionable (high)

`Error: something went wrong (see log)` appears with stderr discarded, so the error goes to **stdout**, where it can corrupt captured output.
It does not say what failed (package not found?), and "see log" names no log path.
Exit code 1 is generic, so an agent cannot tell "package doesn't exist" (don't retry, fix the name) from a network blip (retry).
Fix: write errors to stderr; say what failed (`package "nonexistent-pkg" not found in registry X`); print the log path; use a specific exit code; and, with `--json`, emit the same `{code, message, hint, temporary}` object that `sync` already uses (e.g. `PACKAGE_NOT_FOUND`, `temporary:false`).

### 4. Error contract is inconsistent across commands (medium)

`sync` has a structured stderr error and exit 4; `install` has free text on stdout and exit 1.
An agent can't rely on any one convention.
Fix: one error shape and one exit-code scheme for every command.

### 5. `--help` omits what an agent needs (medium)

- `--json` works but is not listed.
- Exit codes (at least 1 and 4) are not documented; 4's meaning is only discoverable by triggering it.
- `ls  Show stuff` doesn't say what is listed (installed packages? direct only, or transitive? which project?).
- `--quiet  Less output` doesn't say what is removed, or whether it makes stdout clean.
- No per-command help or examples are shown; I can't tell whether `depman sync --help` exists.
- No mention of the non-interactive behaviour of `sync` (fails with exit 4 without `--yes`), or which other commands prompt.
- `clean` is destructive on a *global* cache; help should say whether it prompts and whether it has a dry-run.

Fix: document `--json`, an exit-code table, the JSON schemas (or at least fields), which commands prompt, and replace vague descriptions with concrete ones.

### 6. Help output style (low)

Marketing banner (`the friendly dependency manager!`) and emoji (`✨`, `✓`) add noise to every parse and transcript.
Keep them for TTY users only.

### 7. Aliases (low)

`install` has aliases `i` and `add`.
Fine for humans, but `add` often means "add to the manifest" in other managers; make sure behaviour matches what an agent trained on those tools will assume, or document the difference.

## Unknowns I could not assess from the captures

- Whether `--quiet` already removes the noise in finding 1 (if so, it should be the default under `--json`).
- Whether output changes on TTY vs non-TTY, and whether `NO_COLOR` / color codes are handled.
- Whether `install`, `clean`, or other commands prompt or hang without a TTY.
- Whether `--yes` is per-command or global, and whether there is a `--dry-run`.
- `ls --json` schema stability, ordering, and whether it includes transitive deps.
- Whether the `install` failure has a structured stderr form under `--json` (that capture didn't pass `--json` and discarded stderr).
- Whether a version flag (`--version`) exists.

## Suggested priority

1. Clean stdout under `--json` (finding 1) — single biggest blocker.
2. Gate/opt-out the update check (2).
3. Make `install` errors specific, on stderr, with distinct exit codes and the `sync` JSON shape (3, 4).
4. Document `--json`, exit codes, and prompting behaviour in help (5).
~~~~~~
