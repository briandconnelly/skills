# Scenario 2 (audit) — baseline arm 2 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 6/8 scored; 0/4 conformance
- **Tokens:** 50,150 (final-turn context plus output, read from the transcript)
- **Output words:** 806
- **Transcript sha256:** `d9f9f9cae2eb978021135aaa039835b09a83a26f452688ec1b744aa46f5f47fe` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o4`; the scorer received the assertions verbatim and no arm labels

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
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **PASS** | If it prompts when stdin is not a TTY...; could not check: What `sync` actually does without `--yes` Parts: sync prompt flagged as blocking risk = pass; states what capture establishes and does not = pass |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | `sync` "asks for confirmation first." If it prompts when stdin is not a TTY, an agent's call blocks Parts: shows documented prompt = pass; distinguishes deduced non-TTY hang = pass |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | `depman ls --json \| jq` fails, so any agent that reads it as JSON breaks. Parts: pollution flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | The only exit code seen is `1` ... without parsing text |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Hidden network side effect on a read-only command. |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` is destructive but has no dry run |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **FAIL** | 'Aliases (`i`, `add`) are fine' - duplication not flagged Parts: alias duplication flagged = fail; vague ls description flagged = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **FAIL** | 'What I could not check' lists stderr/TTY behaviors, not checklist areas (stdin, tests) |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **FAIL** | High/Medium/Low, no P0-P3 or template Parts: P0-P3 words = fail; template fields severity/type/evidence/location/impact/fix = fail |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **FAIL** | No evidence labels |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **FAIL** | No P0/P1; hang is High, pollution High |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **FAIL** | No coverage table |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Scope: only the three captures provided (stderr discarded, so every line shown is stdout).
I could not run the tool, so I cannot tell whether a problem is a bug or just undocumented behavior.

## Findings, by severity

### High

1. **`--json` output is not parseable JSON.**
   `depman ls --json` prints a banner (`✨ DepMan 3.2`), a progress line (`Checking for updates...`), and a footer (`Done in 0.42s ✓`) on stdout around the JSON array.
   `depman ls --json | jq` fails, so any agent that reads it as JSON breaks.
   Fix: with `--json`, stdout should hold the JSON document and nothing else.
   Send the banner, progress and timing to stderr, or leave them out.

2. **Hidden network side effect on a read-only command.**
   `ls` prints "Checking for updates..." to stdout, so it seems to reach the network, which costs time, can fail offline, and makes output non-deterministic.
   Fix: do not check for updates during normal commands, or move the check to stderr and let `--no-update-check` or an env var (for example `DEPMAN_NO_UPDATE_CHECK=1`) turn it off.
   Skip it automatically when not on a TTY or when `CI` is set.

3. **Error output gives no information to act on.**
   The install failure prints only `Error: something went wrong (see log)`.
   It does not say what failed (the package was not found), which log, or where the log is.
   It also goes to stdout, not stderr: we know this because it appears even though stderr was discarded.
   Fix: write errors to stderr, name the cause and the input (`package 'nonexistent-pkg' not found in registry <url>`), give the log's full path, and suggest a next step (for example, did you mean / search command).
   With `--json`, also give a structured error object such as `{"error":{"code":"PACKAGE_NOT_FOUND","package":"nonexistent-pkg"}}`.

4. **Interactive confirmation can hang an agent.**
   `sync` "asks for confirmation first."
   If it prompts when stdin is not a TTY, an agent's call blocks until it times out.
   Fix: never prompt when stdin is not a TTY.
   Fail fast with a clear message saying `--yes` is needed, and a distinct exit code.
   Document which commands prompt, and that `--yes` covers all of them.

### Medium

5. **Exit codes do not tell failures apart.**
   The only exit code seen is `1`, for "package not found."
   An agent cannot tell "not found" from a network error, a permission error or a usage error without parsing text.
   Fix: document an exit-code table (for example 0 ok, 2 usage, 3 not found, 4 network, 5 needs confirmation) and list it in `--help`.

6. **`clean` is destructive but has no dry run or confirmation in the docs.**
   It removes packages from the global cache, which affects other projects.
   Fix: add `--dry-run` (ideally with `--json`) that lists what would be removed, and document whether `clean` prompts.

7. **The help text is vague and incomplete.**
   - `ls  Show stuff` does not say what it lists (installed deps? the tree? global or local?).
   - `--json` is used in the capture but is not listed in `--help`, so an agent cannot find it.
   - `--quiet` ("Less output") does not say what it hides, or whether it makes stdout machine-clean.
   - It does not say which options are global and which belong to a command.
   - There are no examples, no `depman <command> --help` pointer, and no exit codes.
   Fix: describe every command precisely, list every flag (including `--json`), and add per-command help with examples.

8. **Branding and decoration in output.**
   The emoji/glyph banner (`✨`, `✓`) and the "friendly" tagline cost tokens and make parsing harder.
   Fix: print them only when stdout is a TTY, honor `NO_COLOR`, and leave them out entirely in `--json`/`--quiet` mode.

### Low

9. **No `--version` flag shown.** The version appears only in banners. Add `depman --version` that prints only the version.
10. **Aliases (`i`, `add`) are fine** but should also show in per-command help so an agent does not mistake them for separate commands.
11. **Unknown: what `--help` writes to stderr.** We cannot see it. Check that help goes to stdout and exits 0.

## What I could not check

- Whether any of this changes when stdout is not a TTY (all captures may come from a TTY or a pipe; the prompt does not say).
- What goes to stderr (discarded in every capture).
- What `sync` actually does without `--yes` in a non-interactive shell.
- Whether `--quiet` removes the banner or the update check.

## Suggested priority for the author

1. Make `--json` stdout pure JSON (finding 1). This alone makes `ls` usable by agents.
2. Send all diagnostics to stderr, and make errors specific and machine-readable (3).
3. Never prompt off a TTY, and fail fast instead (4).
4. Document `--json`, exit codes, and per-command help (5, 7).
5. Remove or gate the update check (2), and add `clean --dry-run` (6).
~~~~~~
