# Scenario 2 (audit) — baseline arm 1 (pre-edit wave)

- **Date:** 2026-11-17
- **Tree:** `63c846b` on `test/agent-friendly-cli-instrument-2026-11-17` (skill files identical to `main` at `b6958e0`)
- **Mode:** baseline (fresh general-purpose subagent; one of three arms in this cell)
- **Model:** `claude-opus-5-5`
- **Score:** 4/8 scored; 0/4 conformance
- **Tokens:** 49,585 (final-turn context plus output, read from the transcript)
- **Output words:** 474
- **Transcript sha256:** `5bb878a78d7c9a6936045ab1f93b89efecfe6fea5534ddf9da5027027e94699e` (session-local copy; not committed)
- **Scoring:** blinded packet, output id `o1`; the scorer received the assertions verbatim and no arm labels

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
| A1 | scored | `sync` prompting for confirmation is identified as a risk of blocking in automation, and the report says what the capture establishes and what it does not (Invocation Safety, Evidence). Reworded 2026-11-17: the ranking is house severity policy and is recorded only by the conformance assertion below. | **FAIL** | 'will hang a non-interactive agent unless it knows to pass --yes' - no statement of what capture establishes vs not Parts: sync prompt flagged as blocking risk = pass; states what capture establishes and does not = fail |
| A2 | scored | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **FAIL** | Hang stated as fact; no shown-vs-deduced distinction Parts: shows documented prompt = pass; distinguishes deduced non-TTY hang = fail |
| A3 | scored | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | `depman ls --json \| jq` fails. Parts: pollution flagged as breaking parsing = pass; treated as established = pass |
| A4 | scored | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Exit 1 is indistinguishable from any other failure. |
| A5 | scored | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Implicit network update check on every run. |
| A6 | scored | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | `clean` is destructive (global cache) but has no `--dry-run` mentioned. |
| A7 | scored | Alias duplication (`i`, `add`) and the vague `ls Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **FAIL** | 'Aliases i/add are fine' - alias duplication not flagged Parts: alias duplication flagged = fail; vague ls description flagged = pass |
| A8 | scored | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **FAIL** | Only lists unknown behaviors (stderr, --quiet); no checklist areas like stdin/tests |
| C1 | conformance | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`: severity, type, evidence, location, impact, fix direction. | **FAIL** | Uses High/Medium/Low, no P0-P3 or template Parts: P0-P3 words = fail; template fields severity/type/evidence/location/impact/fix = fail |
| C2 | conformance | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | **FAIL** | No observed/inferred/absence-of-evidence labels |
| C3 | conformance | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | **FAIL** | No P0/P1 severities |
| C4 | conformance | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | **FAIL** | No checklist coverage table |

## Verbatim final output

~~~~~~markdown
# depman agent-friendliness audit

Evidence is limited to the three captures; stderr was discarded, so anything printed there is unseen.

## High severity

1. **`--json` output is not parseable.**
   `depman ls --json` writes a banner (`✨ DepMan 3.2`), an update-check line, and a `Done in 0.42s ✓` trailer to stdout around the JSON array.
   `depman ls --json | jq` fails.
   Fix: in `--json` mode, stdout must contain exactly one JSON document; send banners, progress, and timing to stderr (or suppress them).

2. **Implicit network update check on every run.**
   `Checking for updates...` appears even on a read-only `ls`.
   This adds latency, non-determinism, and network dependence in sandboxes/CI.
   Fix: disable by default when not a TTY or when `--json`/`CI` is set; provide `--no-update-check` / env var.

3. **Errors are unactionable.**
   `Error: something went wrong (see log)` names neither the cause (package not found), the package, nor the log path.
   It is also on stdout (it survived `2>/dev/null`), so it pollutes captured output.
   Fix: write errors to stderr; say what failed and why (`package 'nonexistent-pkg' not found in registry X`), give the log path, suggest a next step; offer a structured error under `--json` (e.g. `{"error":{"code":"PACKAGE_NOT_FOUND",...}}`).

4. **Single generic exit code.**
   Exit 1 is indistinguishable from any other failure.
   Fix: document distinct exit codes (e.g. usage error, not found, network, conflict) in `--help`.

## Medium severity

5. **Interactive confirmation in `sync`.**
   "asks for confirmation first" will hang a non-interactive agent unless it knows to pass `--yes`.
   Fix: when stdin is not a TTY, fail fast with a message naming `--yes` instead of blocking; consider `--dry-run` to preview.

6. **`--help` is too thin to plan from.**
   - `ls` is described as "Show stuff"; say what it lists (installed? direct vs transitive?).
   - `--json` is used but not documented; list which commands support it.
   - `--quiet` "Less output" is vague: what is suppressed?
   - `--yes` scope unclear: which commands prompt?
   - No per-command help, arguments, examples, or exit codes shown.
   - `clean` is destructive (global cache) but has no `--dry-run` mentioned.
   Fix: concrete descriptions, document all flags, add `depman <cmd> --help` with examples.

7. **Decorations in machine contexts.**
   Emoji/✓ and a marketing tagline add tokens and break naive parsing.
   Fix: disable when not a TTY or with `NO_COLOR`/`--plain`.

## Low severity / to verify

8. Version is only visible in the banner; add `--version` with plain output.
9. JSON records carry only `name` and `version`; consider fields agents commonly need (direct/dev, resolved source), and a stable, documented schema.
10. Aliases `i`/`add` are fine, but ensure `add` semantics match `install` exactly.
11. Unknown: what goes to stderr, whether `--quiet` fixes the stdout pollution, and how `install` behaves with `--json`.
    Re-capture with stderr kept separately to confirm.

## Suggested priority

Fix 1 and 3 first (clean JSON stdout, errors to stderr with specifics), then 4 and 5, then help text.
~~~~~~
