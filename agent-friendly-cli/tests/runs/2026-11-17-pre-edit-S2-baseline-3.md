# Scenario 2 (audit) — baseline arm 3 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 6/8 scored; 0/4 conformance
- **Tokens:** 49,991 (final-turn context plus output, read from the transcript)
- **Output words:** 680
- **Transcript sha256:** `71a20d7a925075b4c9254a9c371e0d170f26bcb8bcbf47512040340babae7de9` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o6`; the scorer received the assertions verbatim and no arm labels

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

> Agent prompt: read the prompt file and do exactly what it asks; that file is the only input; no other file, shell command, web access, or skill; write the answer to a per-arm output file.

## Assertions

| Id | Kind | Assertion | Result | Evidence |
| --- | --- | --- | --- | --- |
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | an agent with no TTY may hang; Not determinable: Behavior of ... `sync` Parts: sync prompt flagged as blocking risk = pass; states what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | `sync` "asks for confirmation first"; an agent with no TTY may hang ... help doesn't say ... what happens without a TTY Parts: shows documented prompt = pass; distinguishes deduced non-TTY hang = pass |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | `depman ls --json \| jq .` will fail Parts: pollution flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Exit status is `1`, which can't be told apart from any other failure. |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Hidden network side effect on a read command |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` removes packages from the global cache ... with no `--dry-run` shown |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **FAIL** | '`add` aliasing `install` is fine' - duplication not flagged Parts: alias duplication flagged = fail; vague ls description flagged = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **FAIL** | 'Not determinable' lists behaviors, not checklist areas like stdin/tests |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **FAIL** | High/Medium/Low; no template Parts: P0-P3 words = fail; template fields severity/type/evidence/location/impact/fix = fail |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **FAIL** | No evidence labels |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **FAIL** | No P0/P1 |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **FAIL** | No coverage table |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Scope: only the three captures provided (stderr discarded, so every line is stdout).
Nothing was executed; findings are limited to what the captures show.

## High severity

### 1. `--json` output is not parseable
`depman ls --json` puts a banner (`✨ DepMan 3.2`), a status line (`Checking for updates...`) and a footer (`Done in 0.42s ✓`) on stdout around the JSON array.
`depman ls --json | jq .` will fail, and an agent has to guess which line is data.
Fix: when `--json` is set, stdout contains exactly one JSON document and nothing else; send banners, progress and timing to stderr (or drop them).

### 2. Errors are unactionable
`depman install nonexistent-pkg` prints `Error: something went wrong (see log)`.
It does not name the package, the cause (not found in registry), or where "the log" is.
Fix: say what failed and why, e.g. `error: package 'nonexistent-pkg' not found in registry <url>`, plus a next step (`try: depman search nonexistent`) and the log path if one exists.
Offer a structured form under `--json` (e.g. `{"error":{"code":"PACKAGE_NOT_FOUND","package":"nonexistent-pkg","message":...}}`).

### 3. Errors go to stdout
That error line survived `2>/dev/null`, so it was written to stdout.
Error text on stdout contaminates piped/captured data.
Fix: write diagnostics to stderr; keep stdout for results.

### 4. One generic exit code
Exit status is `1`, which can't be told apart from any other failure.
An agent can't distinguish "package doesn't exist" (don't retry) from network/registry failure (retry) or usage error.
Fix: document distinct exit codes (e.g. 2 usage, 3 not found, 4 network/transient) in `--help`.

### 5. Hidden network side effect on a read command
`ls` performs `Checking for updates...`, a network call, on every run.
That adds latency, can hang or fail offline/sandboxed, and makes output nondeterministic.
Fix: no update check in non-interactive or `--json` runs; provide an opt-out (`--no-update-check` / env var) and document it.

## Medium severity

### 6. Interactive confirmation risk
`sync` "asks for confirmation first"; an agent with no TTY may hang.
`--yes` exists, but help doesn't say which commands prompt or what happens without a TTY.
Fix: never block on a prompt when stdin isn't a TTY — fail fast with a message naming `--yes`; list prompting commands in help.

### 7. Destructive commands lack a preview
`clean` removes packages from the global cache, and `sync` rewrites the lockfile, with no `--dry-run` shown.
Fix: add `--dry-run` that reports what would change (with JSON output).

### 8. `--json` is undocumented
`ls --json` works but `--help` doesn't list it, so an agent can't discover it.
Fix: list every option in help, ideally per-command (`depman ls --help`), and state which commands support `--json`.

### 9. Vague help text
`ls  Show stuff` and `--quiet  Less output` don't say what is shown or suppressed.
Fix: e.g. `ls  List installed packages (name, version)`; specify exactly what `--quiet` removes.

### 10. Help is decorated and unversioned in a stable way
The tagline/emoji/`✓` add noise; no `--version` flag is documented.
Fix: add `--version` printing a bare version string; keep decoration off in non-TTY output (honor `NO_COLOR`, detect non-TTY).

## Low severity

### 11. Aliases overlap with distinct semantics
`add` aliasing `install` is fine, but document whether `install` with no args installs from the lockfile versus adding a new dependency — agents commonly confuse these.

### 12. Help format
Help went to stdout (good). Consider adding usage examples per command and a machine-readable command listing.

## Not determinable from the captures
- What stderr contains (all captures discarded it), including whether the update check or the log path is reported there.
- Behavior of `--quiet`, `--yes`, `clean`, `sync` and exit codes for other failures.
- Whether output changes when stdout is not a TTY (these captures may already be non-TTY, which would make findings 1 and 10 worse).

## Priority order for the author
1. Clean stdout under `--json` (finding 1) and errors to stderr (3).
2. Specific errors plus distinct exit codes (2, 4).
3. Remove/disable the update check for non-interactive runs (5).
4. Non-TTY prompt safety and `--dry-run` (6, 7).
5. Help text fixes (8–10).
~~~~~~
